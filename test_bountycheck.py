#!/usr/bin/env python3
"""Tests for bountycheck. No network: every fixture is a hand-built API response,
with shapes copied from real ones I read off the GitHub API first.

    python3 test_bountycheck.py
"""
import sys
from datetime import datetime, timedelta, timezone

import bountycheck as bc

PASS = FAIL = 0


def check(name, got, want):
    global PASS, FAIL
    if got == want:
        PASS += 1
    else:
        FAIL += 1
        print(f"  FAIL {name}\n       got  {got!r}\n       want {want!r}")


def ago(days):
    return (datetime.now(timezone.utc) - timedelta(days=days)).isoformat().replace("+00:00", "Z")


def comment(user, body, days, assoc="NONE"):
    return {"user": {"login": user}, "body": body, "author_association": assoc,
            "created_at": ago(days)}


def issue(**kw):
    base = {"title": "t", "body": "", "state": "open", "created_at": ago(400),
            "html_url": "https://github.com/o/r/issues/1", "user": {"login": "reporter"},
            "assignee": None, "labels": []}
    base.update(kw)
    return base


def xref(number, author, state="open", merged=False, days=10, repo="o/r"):
    return {"event": "cross-referenced", "source": {"issue": {
        "number": number, "html_url": f"https://github.com/{repo}/pull/{number}",
        "user": {"login": author}, "state": state,
        "pull_request": {"merged_at": ago(days) if merged else None},
        "created_at": ago(days)}}}


def run(iss, comments, timeline=()):
    """analyse() without the network - same assembly, fixtures instead of HTTP."""
    class FakeGH(bc.GH):
        def __init__(self):
            self.calls = 0
        def issue(self, o, n, num): return iss
        def comments(self, o, n, num): return list(comments)
        def timeline(self, o, n, num): return list(timeline)
    return bc.analyse("o", "r", 1, FakeGH())


# --------------------------------------------------------------------------------------
print("bounty detection")
# The exact header algora-pbc[bot] posts, trimmed.
ALGORA = ("## 💎 $20 bounty [• Highlight (YC W23)](https://algora.io/highlight)\n\n"
          "**Payment will be awarded to the first person to successfully merge a PR.**\n"
          "1. **Start working**: Comment `/attempt #8032` with your implementation plan")

f = run(issue(), [comment("algora-pbc[bot]", ALGORA, 300)])
check("algora bot amount", f["bounty"]["amount"], 20.0)
check("algora bot platform", f["bounty"]["platform"], "algora")

f = run(issue(), [comment("Vadman97", "/bounty $2,500", 300, "MEMBER")])
check("maintainer command amount", f["bounty"]["amount"], 2500.0)

f = run(issue(), [comment("randomguy", "/bounty $9000", 300, "NONE")])
check("outsider cannot post a bounty", f["bounty"]["amount"], None)

f = run(issue(labels=[{"name": "💎 Bounty"}]), [])
check("label alone is weak evidence", f["bounty"]["platform"], "label only")
check("label alone has no amount", f["bounty"]["amount"], None)

f = run(issue(), [])
check("no bounty at all", f["verdict"], "NO BOUNTY")

# --------------------------------------------------------------------------------------
print("claimant counting")
cs = [comment("algora-pbc[bot]", ALGORA, 300),
      comment("alice", "/attempt #1", 200),
      comment("alice", "/attempt #1", 190),          # same person twice
      comment("bob", "/claim #1", 100),
      comment("maint", "/attempt #1", 90, "MEMBER"),  # maintainers are not rivals
      comment("algora-pbc[bot]", "@bob is attempting", 99),
      comment("carol", "I'd like to work on this", 50),
      comment("dave", "great issue, thanks for filing", 40)]
f = run(issue(), cs)
check("distinct claimants", sorted(c["user"] for c in f["claimants"]), ["alice", "bob", "carol"])
check("repeat claims collapse", next(c["n"] for c in f["claimants"] if c["user"] == "alice"), 2)
check("prose claim recognised", next(c["explicit"] for c in f["claimants"] if c["user"] == "carol"), False)

f = run(issue(user={"login": "alice"}), [comment("algora-pbc[bot]", ALGORA, 300),
                                         comment("alice", "/attempt #1", 200)])
check("author is not racing themselves", len(f["claimants"]), 0)

# --------------------------------------------------------------------------------------
print("rival PRs")
tl = [xref(10, "alice"), xref(11, "bob", state="closed"), xref(12, "carol", merged=True, state="closed"),
      xref(13, "eve", repo="someone/else"),          # PR on another repo cannot claim this
      xref(10, "alice"),                              # deduped
      {"event": "commented"}]
f = run(issue(), [comment("algora-pbc[bot]", ALGORA, 300)], tl)
check("rivals deduped and repo-scoped", len(f["rivals"]), 3)
check("open rivals", f["rivals_open"], 1)
check("merged rivals", f["rivals_merged"], 1)

# --------------------------------------------------------------------------------------
print("maintainer liveness")
cs = [comment("algora-pbc[bot]", ALGORA, 300),
      comment("maint", "good first issue", 250, "MEMBER"),   # before the queue
      comment("alice", "/attempt #1", 200),
      comment("bob", "/attempt #1", 150)]
f = run(issue(), cs)
check("comments before the queue do not count", f["maintainer"]["replied_since_first_claim"], 0)

cs.append(comment("maint", "go ahead", 100, "MEMBER"))
f = run(issue(), cs)
check("comments after the queue do count", f["maintainer"]["replied_since_first_claim"], 1)

# --------------------------------------------------------------------------------------
print("bot liveness")
f = run(issue(), [comment("algora-pbc[bot]", ALGORA, 300), comment("alice", "/attempt #1", 200)])
check("bot silent since queue", f["bot_alive"], False)
check("silent bot means abandoned", f["verdict"], "ABANDONED")

f = run(issue(), [comment("algora-pbc[bot]", ALGORA, 300), comment("alice", "/attempt #1", 200),
                  comment("algora-pbc[bot]", "@alice is attempting", 199)])
check("bot answered the queue", f["bot_alive"], True)

f = run(issue(), [comment("maint", "/bounty $50", 300, "MEMBER"), comment("alice", "/attempt", 10)])
check("no bot, no bot verdict", f["bot_alive"], None)

# --------------------------------------------------------------------------------------
print("withdrawal and payout")
f = run(issue(), [comment("algora-pbc[bot]", ALGORA, 300),
                  comment("ilka-schulz",
                          "@mitre88 There is no bounty. We removed all the bounties in order to "
                          "deter AI slop contributions.", 1, "MEMBER")])
check("maintainer withdrawal wins", f["verdict"], "WITHDRAWN")

f = run(issue(), [comment("algora-pbc[bot]", ALGORA, 300),
                  comment("randomguy", "there is no bounty lol", 1, "NONE")])
check("outsider cannot withdraw a bounty", f["verdict"] == "WITHDRAWN", False)

f = run(issue(), [comment("algora-pbc[bot]", ALGORA, 300),
                  comment("alice", "/attempt #1", 200),
                  comment("algora-pbc[bot]", "🎉 @alice has been awarded $20", 100)])
check("payout outranks contention", f["verdict"], "PAID")

# --------------------------------------------------------------------------------------
print("verdicts")
f = run(issue(state="closed"), [comment("algora-pbc[bot]", ALGORA, 300)])
check("closed issue", f["verdict"], "CLOSED")

f = run(issue(assignee={"login": "alice"}), [comment("algora-pbc[bot]", ALGORA, 300)])
check("assigned issue", f["verdict"], "ASSIGNED")

# A bare label with no amount and no bot is not an opportunity, it is an absence of
# evidence. Reporting an empty queue there as OPEN is the mistake this tool exists to
# prevent, so it gets its own verdict.
f = run(issue(created_at=ago(10), labels=[{"name": "bounty"}]), [])
check("label only, no queue", f["verdict"], "UNVERIFIED")
check("unverified is not a green light", bc.EXIT[f["verdict"]], 1)
f = run(issue(created_at=ago(10), labels=[{"name": "bounty"}]), [comment("alice", "/attempt", 5)])
check("label only, one claimant", f["verdict"], "UNVERIFIED")

live = [comment("algora-pbc[bot]", ALGORA, 30)]
f = run(issue(created_at=ago(30)), live)
check("fresh, unclaimed, bot present", f["verdict"], "OPEN")
check("open bounty exits 0", bc.EXIT[f["verdict"]], 0)

f = run(issue(created_at=ago(30)), live + [comment("alice", "/attempt #1", 20),
                                           comment("algora-pbc[bot]", "@alice is attempting", 19)])
check("one rival", f["verdict"], "TAKEN")

many = live + [comment("algora-pbc[bot]", "ack", 5)]
many += [comment(f"u{i}", "/attempt #1", 10 - i) for i in range(6)]
f = run(issue(created_at=ago(30)), many)
check("six rivals, young queue", f["verdict"], "CONTESTED")

# Same queue, aged. A dashboard-posted bounty nobody ever spoke on is fine at ten days
# and damning at two hundred.
old = live + [comment("algora-pbc[bot]", "ack", 100)]
old += [comment(f"u{i}", "/attempt #1", 200 - i) for i in range(6)]
f = run(issue(created_at=ago(400)), old)
check("six rivals, aged queue", f["verdict"], "STALE")

stale = [comment("algora-pbc[bot]", ALGORA, 900), comment("maint", "here you go", 800, "MEMBER")]
stale += [comment(f"u{i}", "/attempt #1", 700 - i * 100) for i in range(4)]
stale += [comment("algora-pbc[bot]", "ack", 300)]   # bot alive, humans gone
f = run(issue(created_at=ago(900)), stale)
check("live bot but silent maintainers", f["verdict"], "STALE")

# --------------------------------------------------------------------------------------
print("arithmetic")
cs = [comment("algora-pbc[bot]", ALGORA, 300)] + \
     [comment(f"u{i}", "/attempt #1", 200 - i) for i in range(4)]
tl = [xref(20, "u0"), xref(21, "outsider")]   # u0 already counted; outsider is extra
f = run(issue(), cs, tl)
check("contenders = claimants + PR authors not already counted", f["contenders"], 5)
check("per contender", f["per_contender"], 4.0)

f = run(issue(labels=[{"name": "bounty"}]), [comment("alice", "/attempt", 5)])
check("no amount, no arithmetic", f["per_contender"], None)

# --------------------------------------------------------------------------------------
print("target parsing")
check("shorthand", bc.parse_target("owner/repo#123"), ("owner", "repo", 123))
check("url", bc.parse_target("https://github.com/owner/repo/issues/123"), ("owner", "repo", 123))
check("url with trailing slash", bc.parse_target("https://github.com/o/r/issues/9/"), ("o", "r", 9))
try:
    bc.parse_target("owner/repo")
    check("repo without issue rejected", True, False)
except SystemExit:
    check("repo without issue rejected", True, True)

print(f"\n{PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
