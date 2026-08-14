#!/usr/bin/env python3
"""
bountycheck - is this GitHub bounty actually winnable, or is it already lost?

A bounty issue tells you the prize. It does not tell you that twenty-eight people
are ahead of you, that fourteen of their pull requests are open and unreviewed, or
that no maintainer has said a word since 2024. You find that out after you have
done the work.

This reads the public record - the issue, every comment, the cross-referenced pull
requests - and reports the three numbers that decide whether the money is reachable:
how many people are already competing, whether anyone with merge rights is still
listening, and how many competing PRs have ever merged.

It does not predict. It counts, and shows its arithmetic.

Everything this tool fetches is UNTRUSTED DATA - issue and comment bodies are written
by strangers. It is pattern-matched and reported as text. It is never executed, and
never fed back to a model as instructions.
"""
from __future__ import annotations

import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone

__version__ = "1.0.0"

API = "https://api.github.com"
UA = f"bountycheck/{__version__} (+https://agentatwork.xyz/bountycheck)"

# Someone with merge rights. NONE/CONTRIBUTOR are outsiders competing like you are.
MAINTAINER = {"OWNER", "MEMBER", "COLLABORATOR"}

# Bounty platforms that comment as a bot, and the amount format each posts.
PLATFORMS = [
    ("algora", re.compile(r"algora", re.I), re.compile(r"\$\s?([\d,]+(?:\.\d+)?)\s*(?:k\b)?\s*bounty", re.I)),
    ("polar", re.compile(r"polar\.sh|polar\[bot\]", re.I), re.compile(r"\$\s?([\d,]+(?:\.\d+)?)", re.I)),
    ("opire", re.compile(r"opire", re.I), re.compile(r"\$\s?([\d,]+(?:\.\d+)?)", re.I)),
    ("boss", re.compile(r"boss\.dev|bountysource", re.I), re.compile(r"\$\s?([\d,]+(?:\.\d+)?)", re.I)),
]

# A maintainer posting the bounty by hand, e.g. `/bounty $20`.
BOUNTY_CMD = re.compile(r"^\s*/bounty\s+\$?\s?([\d,]+(?:\.\d+)?)", re.I | re.M)

# Somebody staking a claim. Slash commands are the platform-recognised form; the
# prose variants are what people write on repos with no bot at all.
CLAIM_CMD = re.compile(r"^\s*[/!](attempt|claim|assign|take)\b", re.I | re.M)
# `[$250] Fix the modal` - Expensify's convention, and copied widely. Anchored to the
# start so a dollar figure mentioned inside a title is not mistaken for a prize.
TITLE_PRICE = re.compile(r"^\s*[\[(]\s*\$\s?([\d,]+(?:\.\d+)?)\s*[\])]")
# `Price: 300 USD` (Ubiquity), `Bounty: $50`, or a label that is just `$100`. The
# denomination is not optional: `reward:50-mrg` is fifty units of a token the issuer mints
# for itself, and reporting that as fifty dollars would be the worst mistake this tool
# could make. If it does not say dollars, it does not count as dollars.
LABEL_PRICE = re.compile(
    r"(?:price|bounty|reward|prize)\W{0,4}\$\s?([\d,]+(?:\.\d+)?)"
    r"|(?:price|bounty|reward|prize)\W{0,4}([\d,]+(?:\.\d+)?)\s*(?:usdc?|usdt|dollars?)\b"
    r"|^\$\s?([\d,]+(?:\.\d+)?)$", re.I)

# A prize denominated in something the issuer prints. Points, credits, or a ticker nobody
# quotes. It may be worth something one day; it is not money today.
SCRIP = re.compile(r"\b(\d[\d,]*)\s*[-\s]?((?!USD|USDC|USDT|EUR|GBP)[A-Z]{2,6})\b"
                   r"|\b(\d[\d,]*)\s*(points?|credits?|tokens?|stars?)\b", re.I)
# A directory entry whose entire body is a link to the issue it mirrors.
MIRROR = re.compile(r"^https://github\.com/([\w.-]+)/([\w.-]+)/issues/(\d+)/?$")

CLAIM_PROSE = re.compile(
    r"\b(?:i(?:'|’)?d?\s+(?:like|want|will|can)\s+to\s+(?:work\s+on|take|try|tackle|solve)"
    r"|i(?:'|’)?m\s+(?:working|going\s+to\s+work)\s+on"
    r"|can\s+i\s+(?:work\s+on|take|be\s+assigned)"
    r"|please\s+assign\s+(?:this\s+)?(?:to\s+)?me"
    r"|working\s+on\s+(?:this|it)\s+(?:now|already))\b", re.I)

# The bounty is gone but the issue still reads as if it is not.
CANCELLED = re.compile(
    r"\b(?:no\s+(?:longer\s+a\s+|more\s+)?bount(?:y|ies)"
    r"|there\s+is\s+no\s+bounty"
    r"|bount(?:y|ies)\s+(?:has\s+been\s+|have\s+been\s+|is\s+|are\s+|was\s+|were\s+)?"
    r"(?:removed|cancelled|canceled|revoked|withdrawn|expired|closed)"
    r"|(?:removed|cancelling|canceling|dropping)\s+(?:all\s+)?(?:the\s+)?bount(?:y|ies)"
    r"|rewarded\s+to\s+@)", re.I)

# A different thing entirely from a bounty being cancelled: the bounty is real, funded and
# open, and *you* specifically cannot be paid for it. Ubiquity's bot says this outright
# while the `Price: 300 USD` label stays on the issue, and account-age gates do the same
# job more quietly. This is not a race you might lose - it is a door, and it is shut.
INELIGIBLE = re.compile(
    r"\b(?:external\s+contributors?\s+are\s+not\s+eligible"
    r"|not\s+eligible\s+for\s+(?:the\s+)?rewards?"
    r"|preserving\s+resources\s+for\s+(?:the\s+)?core\s+team"
    r"|needs?\s+an\s+account\s+at\s+least\s+[\d.]+\s+days?\s+old"
    r"|only\s+(?:members|maintainers|core\s+team|employees)\s+(?:can|may|are)\s+"
    r"(?:eligible|claim|be\s+(?:paid|rewarded)))", re.I)

# The bounty was paid out. Algora and Polar both announce this.
AWARDED = re.compile(r"\b(?:has\s+been\s+awarded|bounty\s+(?:has\s+been\s+)?paid"
                     r"|reward(?:ed)?\s+(?:of\s+)?\$[\d,]+\s+(?:has\s+been\s+)?(?:rewarded|awarded|sent))\b", re.I)

NOW = datetime.now(timezone.utc)


def _days(iso: str | None) -> int | None:
    if not iso:
        return None
    try:
        return (NOW - datetime.fromisoformat(iso.replace("Z", "+00:00"))).days
    except ValueError:
        return None


def _plural(n: int, one: str, many: str | None = None) -> str:
    return one if n == 1 else (many or one + "s")


class GH:
    def __init__(self, token: str | None = None):
        self.token = token or os.environ.get("GITHUB_TOKEN") or ""
        self.calls = 0

    def _get(self, url: str):
        headers = {"user-agent": UA, "accept": "application/vnd.github+json"}
        if self.token:
            headers["authorization"] = f"token {self.token}"
        req = urllib.request.Request(url, headers=headers)
        for attempt in range(3):
            try:
                self.calls += 1
                with urllib.request.urlopen(req, timeout=30) as r:
                    return json.loads(r.read())
            except urllib.error.HTTPError as e:
                if e.code in (403, 429) and attempt < 2:
                    time.sleep(2 + attempt * 3)
                    continue
                if e.code == 404:
                    return None
                raise
            except (urllib.error.URLError, TimeoutError):
                if attempt < 2:
                    time.sleep(2)
                    continue
                raise
        return None

    def _paged(self, url: str, cap: int = 400) -> list:
        """Follow pages until exhausted. A two-year-old bounty easily exceeds one page,
        and truncating it would undercount exactly the contention we are here to measure."""
        out: list = []
        page = 1
        sep = "&" if "?" in url else "?"
        while len(out) < cap:
            d = self._get(f"{url}{sep}per_page=100&page={page}")
            if not d:
                break
            out.extend(d)
            if len(d) < 100:
                break
            page += 1
        return out

    def issue(self, owner: str, name: str, num: int):
        return self._get(f"{API}/repos/{owner}/{name}/issues/{num}")

    def comments(self, owner: str, name: str, num: int) -> list:
        return self._paged(f"{API}/repos/{owner}/{name}/issues/{num}/comments")

    def timeline(self, owner: str, name: str, num: int) -> list:
        return self._paged(f"{API}/repos/{owner}/{name}/issues/{num}/timeline")


# --------------------------------------------------------------------------------------
# Extraction
# --------------------------------------------------------------------------------------
def find_bounty(issue: dict, comments: list) -> dict:
    """Amount and platform, from whichever of the three places announced it."""
    out = {"amount": None, "platform": None, "posted_at": None, "source": None, "scrip": None}

    body = issue.get("body") or ""
    for name, who, amt in PLATFORMS:
        m = amt.search(body)
        if m and who.search(body):
            out.update(amount=_money(m.group(1)), platform=name,
                       posted_at=issue.get("created_at"), source="issue body")
            break

    for c in comments:
        author = c["user"]["login"]
        text = c.get("body") or ""

        m = BOUNTY_CMD.search(text)
        if m and c.get("author_association") in MAINTAINER:
            out.update(amount=_money(m.group(1)), platform=out["platform"] or "manual",
                       posted_at=c["created_at"], source=f"@{author} command")
            continue

        for name, who, amt in PLATFORMS:
            if not who.search(author):
                continue
            m = amt.search(text)
            if m:
                out.update(amount=_money(m.group(1)), platform=name,
                           posted_at=c["created_at"], source=f"{author} comment")
            break

    # The two programs in this ecosystem that most reliably pay put the number where a
    # comment scan will never look: Expensify writes it into the title (`[$250] ...`) and
    # pays out on Upwork, and Ubiquity writes it into a label (`Price: 300 USD`). Missing
    # these reports the most dependable payers on GitHub as having no bounty at all.
    if out["amount"] is None:
        m = TITLE_PRICE.search(issue.get("title") or "")
        if m:
            out.update(amount=_money(m.group(1)), platform=out["platform"] or "title",
                       posted_at=issue.get("created_at"), source="issue title")

    if out["amount"] is None:
        for lbl in issue.get("labels", []):
            name = lbl.get("name") or ""
            m = LABEL_PRICE.search(name)
            if m:
                out.update(amount=_money(m.group(1) or m.group(2) or m.group(3)),
                           platform=out["platform"] or "price label",
                           posted_at=issue.get("created_at"), source=f"label {name!r}")
                break

    if out["amount"] is None:
        for text in [issue.get("title") or ""] + [l.get("name") or "" for l in issue.get("labels", [])]:
            m = SCRIP.search(text)
            if m:
                unit = m.group(2) or m.group(4)
                out.update(platform=out["platform"] or "scrip",
                           scrip=f"{m.group(1) or m.group(3)} {unit.upper()}",
                           source=f"{text.strip()!r}")
                break

    # A `💎 Bounty`-style label is weak evidence, but it is evidence when nothing else spoke.
    if out["amount"] is None:
        for lbl in issue.get("labels", []):
            if "bounty" in (lbl.get("name") or "").lower():
                out.update(platform=out["platform"] or "label only", source=f"label {lbl['name']!r}")
                break
    return out


def _money(s: str) -> float:
    try:
        return float(s.replace(",", ""))
    except ValueError:
        return 0.0


def find_claimants(comments: list, author: str | None) -> tuple[dict, list]:
    """Distinct outsiders who staked a claim, and when each first did.

    Maintainers and bots are excluded: a maintainer saying `/attempt` is not
    competition, and the issue author is presumed not to be racing themselves.
    """
    claims: dict[str, dict] = {}
    for c in comments:
        user = c["user"]["login"]
        if user.endswith("[bot]") or c.get("author_association") in MAINTAINER or user == author:
            continue
        text = c.get("body") or ""
        cmd = CLAIM_CMD.search(text)
        prose = None if cmd else CLAIM_PROSE.search(text)
        if not cmd and not prose:
            continue
        rec = claims.setdefault(user, {"user": user, "first": c["created_at"], "last": c["created_at"],
                                       "n": 0, "explicit": bool(cmd)})
        rec["n"] += 1
        rec["last"] = c["created_at"]
        rec["explicit"] = rec["explicit"] or bool(cmd)
    ordered = sorted(claims.values(), key=lambda r: r["first"])
    return claims, ordered


def find_rival_prs(timeline: list, owner: str, name: str, num: int) -> list:
    """Pull requests that reference this issue. These are the people who did not just
    say they would work on it - they did the work. Each one is a rival for the money."""
    prs: dict[str, dict] = {}
    for e in timeline:
        if e.get("event") not in ("cross-referenced", "connected", "referenced"):
            continue
        src = (e.get("source") or {}).get("issue") or {}
        if not src.get("pull_request"):
            continue
        url = src.get("html_url")
        if not url or f"/{owner}/{name}/" not in url:
            continue  # a PR on some other repo cannot claim this bounty
        prs[url] = {
            "url": url,
            "number": src.get("number"),
            "author": (src.get("user") or {}).get("login"),
            "state": src.get("state"),
            "merged": bool((src.get("pull_request") or {}).get("merged_at")),
            "created_at": src.get("created_at"),
        }
    return sorted(prs.values(), key=lambda p: p["created_at"] or "")


def maintainer_activity(comments: list, since: str | None) -> dict:
    """Is anyone with merge rights still reading this thread?

    `replied_since` is the load-bearing one: maintainer comments from before the
    queue formed say nothing about whether today's queue will ever be judged.
    """
    mine = [c for c in comments
            if c.get("author_association") in MAINTAINER and not c["user"]["login"].endswith("[bot]")]
    after = [c for c in mine if since and c["created_at"] > since]
    return {
        "comments": len(mine),
        "last_at": mine[-1]["created_at"] if mine else None,
        "last_by": mine[-1]["user"]["login"] if mine else None,
        "replied_since_first_claim": len(after),
        "last_since_text": (after[-1].get("body") or "")[:200] if after else None,
    }


def bot_alive(comments: list, platform: str | None, first_claim: str | None) -> bool | None:
    """A bounty platform's bot normally acknowledges each `/attempt`. If claims keep
    arriving and the bot has gone quiet, the integration is dead even though the
    issue still advertises a prize. Returns None when there was never a bot."""
    if not platform or platform in ("manual", "label only"):
        return None
    bots = [c for c in comments if c["user"]["login"].endswith("[bot]")
            and any(p.search(c["user"]["login"]) for _, p, _ in PLATFORMS)]
    if not bots:
        return None
    if not first_claim:
        return True
    return any(c["created_at"] > first_claim for c in bots)


def scan_ineligible(comments: list) -> dict | None:
    """Somebody with standing said outsiders cannot be paid here.

    Unlike a withdrawal, this is usually said by the bot rather than a human, so bots
    count - they are the ones enforcing it. Outsiders speculating do not.
    """
    for c in reversed(comments):
        by = c["user"]["login"]
        if not by.endswith("[bot]") and c.get("author_association") not in MAINTAINER:
            continue
        text = c.get("body") or ""
        m = INELIGIBLE.search(text)
        if m:
            return {"at": c["created_at"], "by": by,
                    "text": " ".join(text[max(0, m.start() - 40):m.end() + 100].split())}
    return None


def scan_cancelled(issue: dict, comments: list) -> dict | None:
    """A maintainer saying the bounty is gone outranks every other signal."""
    for c in comments:
        if c.get("author_association") not in MAINTAINER or c["user"]["login"].endswith("[bot]"):
            continue
        text = c.get("body") or ""
        m = CANCELLED.search(text)
        if m:
            return {"at": c["created_at"], "by": c["user"]["login"],
                    "text": " ".join(text[max(0, m.start() - 60):m.end() + 120].split())}
    return None


def scan_awarded(comments: list) -> dict | None:
    for c in comments:
        text = c.get("body") or ""
        if c["user"]["login"].endswith("[bot]") and AWARDED.search(text):
            return {"at": c["created_at"], "text": " ".join(text[:180].split())}
    return None


# --------------------------------------------------------------------------------------
# Verdict
# --------------------------------------------------------------------------------------
def decide(f: dict) -> tuple[str, str]:
    """Order matters: the cheapest disqualifying fact wins, so we never tell someone
    a bounty is 'contested' when it was actually paid out a year ago."""
    live_rivals = f["rivals_open"]
    claimants = len(f["claimants"])
    silent = f["maintainer"]["last_at"]
    silent_days = _days(silent)

    if f["awarded"]:
        return "PAID", "This bounty was already awarded. The thread is history, not an opening."
    if f["cancelled"]:
        return "WITHDRAWN", ("A maintainer said the bounty is gone. The issue still advertises it; "
                             "that is the trap. Do not start.")
    if f.get("ineligible"):
        return "INELIGIBLE", (f"@{f['ineligible']['by']} stated that contributors like you cannot "
                              "be paid here. The prize is real, funded, and closed to you. The "
                              "price label is still on the issue.")
    if f["issue_state"] == "closed":
        return "CLOSED", "The issue is closed. Whatever it once paid, it is not paying now."
    if f["bounty"]["amount"] is None and f["bounty"]["platform"] is None:
        return "NO BOUNTY", "No bounty found on this issue. Whatever sent you here was not the issue itself."
    if f["bounty"].get("scrip"):
        return "UNVERIFIED", (f"The prize is {f['bounty']['scrip']} - a unit the issuer mints, not "
                              "money. It may be worth something one day. Price it yourself before "
                              "you spend an afternoon on it.")
    if f["assignee"]:
        return "ASSIGNED", f"Assigned to @{f['assignee']}. It is theirs until they give it back."
    if f["bot_alive"] is False:
        return "ABANDONED", ("Claims keep arriving and the bounty bot stopped answering them. The "
                             "integration is dead while the issue still advertises the prize.")
    # An empty queue is not evidence of opportunity when the thread has been silent for
    # years. Old platform bounties in particular sit there unclaimed and unreachable -
    # nobody queued because there is nobody home, which is the opposite of an opening.
    if silent_days is not None and silent_days > 365:
        return "STALE", (f"No maintainer has spoken here in {silent_days} days"
                         + (f", with {claimants} already queued." if claimants else
                            ". Nobody queued because there is nobody home."))
    if silent_days is not None and silent_days > 180 and claimants >= 3:
        return "STALE", (f"A queue of {claimants} formed and no maintainer has spoken in "
                         f"{silent_days} days. Nobody is judging this.")
    # Nobody with merge rights ever spoke, and the issue has had years to attract one.
    if f["maintainer"]["comments"] == 0 and (_days(f["created_at"]) or 0) > 365:
        return "STALE", ("Nobody with merge rights has ever commented, and the issue is "
                         f"{_days(f['created_at'])} days old.")
    # Plenty of bounties are posted from a platform dashboard, so the maintainer never
    # comments and never needs to. That is only damning once the queue has aged without
    # anyone showing up to judge it.
    queue_age = _days(f["claimants"][0]["first"]) if f["claimants"] else None
    if f["maintainer"]["comments"] == 0 and claimants >= 2 and (queue_age or 0) > 60:
        return "STALE", (f"Nobody with merge rights has ever commented here, and the queue has been "
                         f"waiting {queue_age} days.")
    if live_rivals >= 3 or claimants >= 5:
        return "CONTESTED", (f"{claimants} {_plural(claimants, 'person', 'people')} ahead of you and "
                             f"{live_rivals} open {_plural(live_rivals, 'PR')} already waiting on review.")

    # No amount named by anyone, no platform bot - just a label somebody applied. An
    # empty queue on an issue like this is not an opportunity, it is an absence of
    # evidence, and reporting it as OPEN would be the exact mistake this tool exists to
    # prevent. Repos that mint hundreds of these are the ones worth being slowest about.
    if f["bounty"]["amount"] is None and f["bounty"]["platform"] in ("label only", "scrip"):
        return "UNVERIFIED", ("Labelled as a bounty, but nobody has named an amount and no bounty "
                              "platform is involved. There may be no money here at all.")

    if claimants >= 1 or live_rivals >= 1:
        return "TAKEN", "Someone got here first. Winnable only if their attempt stalls."
    return "OPEN", "No queue, bounty present, and the thread is being read. This is the real kind."


def analyse(owner: str, name: str, num: int, gh: GH, _via: str | None = None) -> dict:
    issue = gh.issue(owner, name, num)
    if not issue:
        raise SystemExit(f"bountycheck: {owner}/{name}#{num} not found (or not public)")
    if issue.get("pull_request"):
        raise SystemExit(f"bountycheck: {owner}/{name}#{num} is a pull request, not an issue")

    # Bounty directories (Ubiquity's devpool is the big one) mirror somebody else's issue
    # and the whole body is a link to it. The mirror has no claimants and no maintainer,
    # so measuring it reports an empty room while the real queue - and the real
    # eligibility rules - are one hop away. Follow the link once and measure that.
    if _via is None:
        m = MIRROR.match((issue.get("body") or "").strip())
        if m:
            up = analyse(m.group(1), m.group(2), int(m.group(3)), gh,
                         _via=f"{owner}/{name}#{num}")
            up["mirror_of"] = up["target"]              # where the work actually happens
            up["target"] = f"{owner}/{name}#{num}"      # what you asked about
            return up

    comments = gh.comments(owner, name, num)
    timeline = gh.timeline(owner, name, num)

    author = (issue.get("user") or {}).get("login")
    bounty = find_bounty(issue, comments)
    claims, claimants = find_claimants(comments, author)
    rivals = find_rival_prs(timeline, owner, name, num)
    first_claim = claimants[0]["first"] if claimants else None
    maint = maintainer_activity(comments, first_claim)

    f = {
        "target": f"{owner}/{name}#{num}",
        "url": issue.get("html_url"),
        "title": issue.get("title"),
        "issue_state": issue.get("state"),
        "created_at": issue.get("created_at"),
        "assignee": (issue.get("assignee") or {}).get("login"),
        "labels": [lbl["name"] for lbl in issue.get("labels", [])],
        "bounty": bounty,
        "claimants": claimants,
        "rivals": rivals,
        "rivals_open": sum(1 for p in rivals if p["state"] == "open"),
        "rivals_merged": sum(1 for p in rivals if p["merged"]),
        "maintainer": maint,
        "bot_alive": bot_alive(comments, bounty["platform"], first_claim),
        "cancelled": scan_cancelled(issue, comments),
        "ineligible": scan_ineligible(comments),
        "awarded": scan_awarded(comments),
        "comment_count": len(comments),
        "api_calls": gh.calls,
    }
    f["verdict"], f["advice"] = decide(f)

    # The arithmetic, spelled out. Splitting a prize by the number of people chasing it
    # is not a probability - it is what the prize is worth per unit of duplicated effort,
    # which is the number nobody computes before starting.
    amt = bounty["amount"]
    contenders = max(1, len(claimants) + sum(1 for p in rivals
                                             if p["state"] == "open" and p["author"] not in claims))
    f["per_contender"] = round(amt / contenders, 2) if amt else None
    f["contenders"] = contenders
    return f


# --------------------------------------------------------------------------------------
# Output
# --------------------------------------------------------------------------------------
COLOR = {"WITHDRAWN": "\033[1;97;41m", "ABANDONED": "\033[1;97;41m", "PAID": "\033[1;90m",
         "CLOSED": "\033[1;90m", "NO BOUNTY": "\033[1;90m", "STALE": "\033[1;30;43m",
         "CONTESTED": "\033[1;33m", "ASSIGNED": "\033[1;33m", "TAKEN": "\033[1;33m",
         "OPEN": "\033[1;32m", "UNVERIFIED": "\033[1;36m"}
RESET = "\033[0m"

# Exit codes, so this can gate a script: 0 go, 1 think hard, 2 do not start.
EXIT = {"OPEN": 0, "TAKEN": 1, "CONTESTED": 1, "ASSIGNED": 1, "STALE": 2, "ABANDONED": 2,
        "WITHDRAWN": 2, "PAID": 2, "CLOSED": 2, "NO BOUNTY": 2, "UNVERIFIED": 1, "INELIGIBLE": 2}


def render(f: dict, use_color: bool = True) -> str:
    c = COLOR.get(f["verdict"], "") if use_color else ""
    r = RESET if use_color else ""
    b = f["bounty"]
    amount = f"${b['amount']:,.0f}" if b["amount"] else "unknown amount"
    plat = f" via {b['platform']}" if b["platform"] else ""

    out = ["", f"  {c} {f['verdict']} {r}  {f['target']}  {amount}{plat}",
           f"  {f['advice']}", ""]

    age = _days(f["created_at"])
    out.append("  Contention")
    out.append(f"    {len(f['claimants'])} claimed it · {len(f['rivals'])} "
               f"{_plural(len(f['rivals']), 'PR')} opened ({f['rivals_open']} still open, "
               f"{f['rivals_merged']} merged) · issue is {age} days old")
    if f["claimants"]:
        first, last = f["claimants"][0], f["claimants"][-1]
        out.append(f"    queue formed {_days(first['first'])} days ago, newest arrival "
                   f"{_days(last['first'])} days ago (@{last['user']})")

    m = f["maintainer"]
    out.append("  Is anyone listening")
    if m["last_at"]:
        out.append(f"    last maintainer comment {_days(m['last_at'])} days ago, by @{m['last_by']}")
    else:
        out.append("    no maintainer has ever commented on this issue")
    if f["claimants"]:
        n = m["replied_since_first_claim"]
        out.append(f"    {n} maintainer {_plural(n, 'comment')} since the first claim"
                   + ("  <- nobody is judging the queue" if n == 0 else ""))
    if f["bot_alive"] is False:
        out.append(f"    the {b['platform']} bot has not acknowledged a claim since the queue formed")

    if f["per_contender"] is not None:
        out.append("  What it is worth")
        out.append(f"    ${b['amount']:,.0f} split {f['contenders']} "
                   f"{_plural(f['contenders'], 'way')} = "
                   f"${f['per_contender']:,.2f} per contender"
                   + (f", and {f['rivals_merged']} of {len(f['rivals'])} competing PRs have merged"
                      if f["rivals"] else ""))

    if f.get("mirror_of"):
        out.append("  Mirror")
        out.append(f"    This is a directory entry. Measured the issue it points at, "
                   f"{f['mirror_of']}.")
    for key, label in (("cancelled", "Withdrawn"), ("awarded", "Awarded"),
                       ("ineligible", "Ineligible")):
        if f[key]:
            out.append(f"  {label}")
            out.append(f"    {f[key]['at'][:10]}: \"{f[key]['text'][:160]}\"")

    out.append("")
    out.append(f"  {f['url']}")
    out.append("")
    return "\n".join(out)


def render_row(f: dict) -> str:
    b = f["bounty"]
    amt = f"${b['amount']:,.0f}" if b["amount"] else "?"
    return (f"{f['verdict']:<10} {amt:>8}  {len(f['claimants']):>3} claim "
            f"{f['rivals_open']:>3} open PR  {f['target']}")


def parse_target(s: str) -> tuple[str, str, int]:
    s = s.strip().rstrip("/")
    m = re.search(r"github\.com/([^/]+)/([^/]+?)/issues/(\d+)", s)
    if not m:
        m = re.match(r"^([^/#\s]+)/([^/#\s]+?)#(\d+)$", s)
    if not m:
        raise SystemExit(f"bountycheck: cannot parse target {s!r}\n"
                         "  try:  bountycheck owner/repo#123   |   a github issue URL")
    return m.group(1), m.group(2), int(m.group(3))


def main(argv: list[str]) -> int:
    args = [a for a in argv[1:] if not a.startswith("-")]
    flags = {a for a in argv[1:] if a.startswith("-")}
    if "-h" in flags or "--help" in flags or (not args and sys.stdin.isatty()):
        print(__doc__)
        print("usage: bountycheck <owner/repo#issue | github issue url> [--json] [--no-color]")
        print("       bountycheck < list-of-targets.txt        one per line, one row of output each")
        print("       GITHUB_TOKEN in the environment raises the rate limit.")
        print("\nexit: 0 = worth starting, 1 = contested, 2 = do not start\n")
        return 0

    gh = GH()
    if not args:  # batch mode: targets on stdin
        worst = 0
        for line in sys.stdin:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            try:
                f = analyse(*parse_target(line), gh)
            except SystemExit as e:
                print(f"{'ERROR':<10} {'':>8}  {e}")
                continue
            print(render_row(f), flush=True)
            worst = max(worst, EXIT[f["verdict"]])
        return worst

    f = analyse(*parse_target(args[0]), gh)
    if "--json" in flags:
        print(json.dumps(f, indent=2))
    else:
        print(render(f, use_color="--no-color" not in flags and sys.stdout.isatty()))
    return EXIT[f["verdict"]]


if __name__ == "__main__":
    sys.exit(main(sys.argv))
