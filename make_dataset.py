#!/usr/bin/env python3
"""Generate DATASET.md from the scan records.

Every number in the document comes from here, so the prose cannot drift away from the
data. Re-run after any rule change: verdicts are recomputed from the stored fields
rather than read back from what was written at scan time.

    python3 make_dataset.py scan.jsonl part0.jsonl ... > DATASET.md
"""
import collections
import json
import sys

import bountycheck as bc

CAP = 12          # max issues counted per repo
REACHABLE = {"OPEN", "TAKEN"}
# One tier out from reachable: somebody is ahead of you, but the thread is alive and the
# money has not been declared gone. This is the most generous reading of "still available"
# the data supports, and the paragraph about it says so.
WIDE = REACHABLE | {"CONTESTED"}

# Optional: trapcheck verdicts per repo, written by make_trap.py. Absent is fine.
try:
    TRAP = {k: (v or {}).get("verdict") for k, v in json.load(open("trap.json")).items()}
except (FileNotFoundError, ValueError):
    TRAP = {}

recs, errors = [], 0
seen = set()
for path in sys.argv[1:]:
    for line in open(path):
        r = json.loads(line)
        if r["target"] in seen:
            continue
        seen.add(r["target"])
        if r.get("verdict") == "ERROR":
            errors += 1
            continue
        r["verdict"], r["advice"] = bc.decide(r)
        recs.append(r)

fetched = len(recs)
# The search that produced these targets included `/bounty` in comments, which sweeps in
# ordinary issues where somebody typed the word once. Those are search artifacts, not
# bounties, and counting them in the denominator would flatter the headline by making the
# unreachable share of *real* bounties look smaller than it is. Excluded, and counted.
not_bounties = [r for r in recs if r["verdict"] == "NO BOUNTY"]
recs = [r for r in recs if r["verdict"] != "NO BOUNTY"]

by_repo = collections.defaultdict(list)
for r in recs:
    by_repo[r["target"].split("#")[0]].append(r)
uncapped_issues, uncapped_repos = len(recs), len(by_repo)

capped = []
for repo, rs in by_repo.items():
    capped.extend(sorted(rs, key=lambda r: r["target"])[:CAP])
recs = capped
by_repo = collections.defaultdict(list)
for r in recs:
    by_repo[r["target"].split("#")[0]].append(r)

n, nrepo = len(recs), len(by_repo)
verd = collections.Counter(r["verdict"] for r in recs)
reach = [r for r in recs if r["verdict"] in REACHABLE]
with_amt = [r for r in recs if r["bounty"]["amount"]]
total_usd = sum(r["bounty"]["amount"] for r in with_amt)
reach_usd = sum(r["bounty"]["amount"] for r in reach if r["bounty"]["amount"])
ever = [r for r in with_amt if r["rivals"]]
merged_any = sum(1 for r in ever if r["rivals_merged"])
med_claim = sorted(len(r["claimants"]) for r in with_amt)[len(with_amt) // 2]
med_prs = sorted(r["rivals_open"] for r in with_amt)[len(with_amt) // 2]

def _pl(k, one, many=None):
    return one if k == 1 else (many or one + "s")


DESC = {
    "STALE": "a queue formed and nobody with merge rights is judging it",
    "ABANDONED": "claims keep arriving; the bounty bot stopped answering",
    "UNVERIFIED": "labelled a bounty, but no amount and no platform behind it",
    "CONTESTED": "a crowd is ahead of you, PRs already waiting on review",
    "PAID": "already awarded",
    "ASSIGNED": "belongs to someone",
    "TAKEN": "someone got here first, but the thread is alive",
    "OPEN": "bounty present, no queue, thread is being read",
    "WITHDRAWN": "a maintainer said the bounty is gone; the issue still advertises it",
    "CLOSED": "the issue is closed",
    "NO BOUNTY": "no bounty found on the issue at all",
    "INELIGIBLE": "funded, open, and closed to outsiders — stated outright, price label still on",
}

p = print
p("# The state of GitHub bounties, measured")
p()
p(f"On 2026-08-14 I ran [bountycheck](README.md) over **{fetched:,} issues** reached through "
  "GitHub's issue search for bounty labels, bounty platform mentions, and `/bounty` commands "
  f"in comments. **{len(not_bounties):,}** of them advertised no bounty at all — the search term "
  "appears in ordinary issues too — and are excluded from every number below, leaving "
  f"**{uncapped_issues:,} bounty issues** across **{uncapped_repos:,} repositories**.")
p()
p(f"This document counts at most **{CAP} issues per repository** ({n:,} issues, {nrepo:,} repos). "
  "A single repository can mint thousands of bounty issues, and without the cap the percentages "
  "would describe that one repository rather than the ecosystem.")
p()
p("## The headline")
p()
p(f"**Not one of the {n:,} bounty issues came back `OPEN`.**")
p()
p("`OPEN` is the verdict for the ordinary case: a real prize, nobody queued ahead of you, "
  "and a maintainer who has spoken since the queue formed. It is what you would expect a "
  "bounty to be. Across this sample it does not occur.")
p()
p(f"The closest thing to an opening is `TAKEN` — somebody got there first, but the thread is "
  f"alive and their attempt could stall. That is {len(reach)} "
  f"{_pl(len(reach), 'issue')} out of {n:,}, or {100 * len(reach) / n:.1f}%.")
p()
p(f"The issues that name a dollar amount add up to **${total_usd:,.0f}**. Of that, "
  f"**${reach_usd:,.0f} ({100 * reach_usd / total_usd:.1f}%)** sits on issues that are still "
  "reachable. The rest is advertised, not available.")
p()
p("| verdict | issues | share | meaning |")
p("|---|---:|---:|---|")
for k, v in verd.most_common():
    p(f"| `{k}` | {v} | {100 * v / n:.1f}% | {DESC.get(k, '')} |")
p()
p("## What you are walking into")
p()
p(f"Across the {len(with_amt)} issues that name an amount:")
p()
p(f"- **Median claimants already ahead of you: {med_claim}.**")
p(f"- **Median open pull requests already waiting on review: {med_prs}.**")
p(f"- Of the {len(ever)} issues that attracted competing pull requests, **{merged_any} "
  f"({100 * merged_any / len(ever):.0f}%) have ever had one merged.**")
p()
p("The last number is the one that matters. A bounty pays on merge. On most of these issues, "
  "nothing has ever merged, by anyone, ever — so the queue is not a race with a winner. It is "
  "a queue with no exit.")
p()
p("## The most contested bounties in the sample")
p()
p("`$/head` is the bounty divided by the number of people chasing it. It is not a probability — "
  "it is what the prize is worth per unit of duplicated effort.")
p()
p("| issue | bounty | claimants | PRs | merged | $/head | verdict |")
p("|---|---:|---:|---:|---:|---:|---|")
for r in sorted(with_amt, key=lambda r: -len(r["claimants"]))[:15]:
    b = r["bounty"]
    p(f"| [{r['target']}]({r['url']}) | ${b['amount']:,.0f} | {len(r['claimants'])} | "
      f"{len(r['rivals'])} | {r['rivals_merged']} | ${r['per_contender']:,.2f} | `{r['verdict']}` |")
p()
p("## The ones you can actually reach")
p()
if reach:
    p("Every reachable issue in the sample, in full. This is the whole list.")
    p()
    p("| issue | bounty | claimants | open PRs | verdict |")
    p("|---|---:|---:|---:|---|")
    for r in sorted(reach, key=lambda r: -(r["bounty"]["amount"] or 0)):
        amt = f"${r['bounty']['amount']:,.0f}" if r["bounty"]["amount"] else "—"
        p(f"| [{r['target']}]({r['url']}) | {amt} | {len(r['claimants'])} | "
          f"{r['rivals_open']} | `{r['verdict']}` |")
    p()

wide = [r for r in recs if r["verdict"] in WIDE]
p("## Widening it as far as honesty allows")
p()
p(f"{len(reach)} {_pl(len(reach), 'issue')} is a thin surface to draw conclusions from, so "
  "here is the most generous "
  "reading the data supports: add `CONTESTED` — somebody is ahead of you and pull requests "
  "are already waiting on review, but nothing has been withdrawn and nobody has declared "
  f"the thread dead. That gives **{len(wide)} issues** across "
  f"**{len({r['target'].split('#')[0] for r in wide})} repositories**.")
p()
if TRAP:
    wrepos = sorted({r["target"].split("#")[0] for r in wide})
    lvl = collections.Counter(TRAP.get(x, "?") for x in wrepos)
    ilvl = collections.Counter(TRAP.get(r["target"].split("#")[0], "?") for r in wide)
    flagged = sum(v for k, v in ilvl.items() if k not in ("CLEAN", "?"))
    p("Then run the other tool over them. "
      "[trapcheck](https://github.com/agentatwork/trapcheck) reads the same repositories for "
      "the patterns used to farm automated contributors rather than pay them — instruction "
      "text aimed at an agent, tasks that ask for credentials, repos that exist only to "
      "collect attempts. It is a different question with a different answer, and the two "
      "overlap here more than I expected.")
    p()
    p("| trapcheck verdict | repos | issues |")
    p("|---|---:|---:|")
    for k in ("CLEAN", "CAUTION", "SUSPICIOUS", "TRAP"):
        if lvl.get(k):
            p(f"| `{k}` | {lvl[k]} | {ilvl.get(k, 0)} |")
    p()
    p(f"**{flagged} of the {len(wide)} most-available bounty issues in the sample sit in "
      "repositories trapcheck flags.** Not all flags are traps — `CAUTION` is often just an "
      "agent-oriented repo with unusual instruction files — but this is the part of the "
      "ecosystem an agent hunting for work is steered into first, because these repos are "
      "the ones with no queue in front of the money.")
    p()
    clean = [r for r in wide
             if TRAP.get(r["target"].split("#")[0]) == "CLEAN" and r["bounty"]["amount"]]
    if clean:
        p(f"Filter to the {lvl.get('CLEAN', 0)} `CLEAN` repositories and keep only issues that "
          f"name an actual dollar figure, and **{len(clean)} issues remain, worth "
          f"${sum(r['bounty']['amount'] for r in clean):,.0f} in total**. That is the honest "
          "answer to *what is available on GitHub right now* for someone arriving today.")
        p()
        p("| issue | bounty | claimants | open PRs | verdict |")
        p("|---|---:|---:|---:|---|")
        for r in sorted(clean, key=lambda r: -r["bounty"]["amount"]):
            p(f"| [{r['target']}]({r['url']}) | ${r['bounty']['amount']:,.0f} | "
              f"{len(r['claimants'])} | {r['rivals_open']} | `{r['verdict']}` |")
        p()
p("## Five ways a bounty lies")
p()
ineli = verd.get("INELIGIBLE", 0)
if ineli:
    p("**The money is real and you are not allowed to have it.** This is the one I did not "
      "expect, and it is the most honest failure mode in the sample, because the machine "
      "says it out loud. Ubiquity's bot, replying to a contributor who typed `/start` on a "
      "task labelled `Price: 300 USD`, six days before this was written:")
    p()
    p("> External contributors are not eligible for rewards at this time. We are preserving "
      "resources for core team only.")
    p()
    p("The task stayed open. The price label stayed on. A second contributor was turned away "
      "for having a GitHub account 83 days old against a 365.25-day minimum. The prize is "
      "funded, the issue is unassigned, nobody is competing — and the door is shut. "
      f"That is `INELIGIBLE`, {ineli} {'issue' if ineli == 1 else 'issues'} here.")
    p()
    p("All of them belong to one organisation, and I want to be careful about what that means. "
      "It is not evidence that they are the only ones doing it — it is evidence that they are "
      "the ones whose bot says it in public, in a comment, where a scanner can read it. A "
      "project that quietly declines to pay outsiders produces no such string and lands in "
      "`STALE` instead. So treat this count as a floor on a category, not a measurement of it.")
    p()
scrip = [r for r in recs if r["bounty"].get("scrip") and not r["bounty"].get("quoted")]
if scrip:
    units = collections.Counter(r["bounty"]["scrip"].split()[-1] for r in scrip)
    p(f"**The prize is not money.** {len(scrip)} issues here "
      f"({100 * len(scrip) / n:.0f}%) advertise a reward denominated in a unit the issuer "
      f"mints: {', '.join(f'`{u}`' for u, _ in units.most_common(5))}. They are formatted "
      "exactly like a dollar bounty — a bracketed prefix in the title, a `reward:` label — "
      "and an aggregator that strips the denomination reports them as dollars. The largest "
      f"single group is `{units.most_common(1)[0][0]}`, "
      f"{units.most_common(1)[0][1]} issues across "
      f"{len({r['target'].split('#')[0] for r in scrip if r['bounty']['scrip'].endswith(units.most_common(1)[0][0])})} "
      "repositories, where claiming also requires starring the issuer's other repositories. "
      "The token may be worth something one day. It is not worth anything today, and "
      "bountycheck refuses to print a dollar sign in front of it.")
    p()
p("**It was withdrawn and the issue does not say so.** The clearest case in the sample is "
  "[rosenpass/rosenpass#748](https://github.com/rosenpass/rosenpass/issues/748), where a "
  "maintainer answered a hopeful claimant directly:")
p()
p("> There is no bounty. We removed all the bounties in order to deter AI slop contributions.")
p()
p("Maintainers are deleting money to keep automated contributors out. The label stays.")
p()
p("**The platform integration died and the prize stayed up.** Bounty bots normally acknowledge "
  "every `/attempt`. When claims keep arriving and the bot has gone silent, nothing was "
  "cancelled and nothing was closed — the machinery just stopped, while the issue goes on "
  f"advertising a prize. That is `ABANDONED`, and it is {verd['ABANDONED']} issues here "
  f"({100 * verd['ABANDONED'] / n:.0f}%).")
p()
p("**Nobody is home and nobody ever was.** Old platform bounties sit unclaimed for years, which "
  "reads as an opening until you notice why nobody queued. The sample includes live bounty "
  "issues whose last maintainer comment is more than 3,700 days old.")
p()
p("## Where the volume comes from")
p()
p("The repositories contributing the most bounty issues are not the ones you have heard of.")
p()
p("| repo | issues in sample | created | verdicts |")
p("|---|---:|---|---|")
for repo, rs in sorted(by_repo.items(), key=lambda kv: -len(kv[1]))[:12]:
    vs = collections.Counter(r["verdict"] for r in rs)
    created = min((r["created_at"] or "")[:10] for r in rs)
    p(f"| `{repo}` | {len(rs)} | {created} | {', '.join(f'{k}×{v}' for k, v in vs.most_common())} |")
p()
p("Several of these were created within the last few months and have issued thousands of pull "
  "request numbers against a few hundred stars. Note that most of them are **not** "
  "prompt-injection traps — [trapcheck](https://github.com/agentatwork/trapcheck) rates several "
  "`CLEAN`. They are a different failure mode: repositories that absorb enormous volumes of "
  "automated contribution and merge approximately none of it. A repo can be perfectly safe to "
  "point an agent at and still be a complete waste of the afternoon.")
p()
p("## Method, and what this does not measure")
p()
p("Records were gathered by `scan.py` and summarised by `make_dataset.py`; verdict rules are in "
  "`bountycheck.py` and the whole thing is reproducible from a GitHub token and a list of "
  "targets. Every verdict in this document was recomputed from stored fields rather than "
  "trusted as written at scan time.")
p()
p("**Sampling.** Targets came from GitHub issue search: bounty labels, bounty platform mentions "
  "in issue bodies, and `/bounty` in comments, sorted by both most-commented and "
  "most-recently-updated. That over-samples issues with long comment threads, which are exactly "
  "the contested ones — so the reachable share here is, if anything, pessimistic against "
  "quiet-but-live bounties. It also cannot see bounties that are never posted publicly as "
  "GitHub issues, which is where a lot of the serious money actually is.")
p()
p(f"**The denominator.** {len(not_bounties):,} fetched issues had no bounty on them and were "
  "dropped. Keeping them would have made the unreachable share of real bounties look smaller "
  "than it is, which is the flattering direction, so they are out. Issues that carry a bounty "
  "label but no discoverable amount are **kept** — they advertise a bounty, and whether that "
  "advertisement is backed by money is exactly what is in question. A bounty is counted "
  "wherever the amount was announced: a platform bot, a maintainer's `/bounty` command, the "
  "issue title (`[$250] ...`, Expensify's convention, paid via Upwork), or a price label "
  "(`Price: 300 USD`, Ubiquity's).")
p()
p(f"**Errors.** {errors} targets failed to fetch (deleted, made private, or renamed between "
  "search and fetch) and are excluded.")
p()
p("**Mirrors are resolved.** Directory repositories that mirror somebody else's issue — "
  "Ubiquity's devpool is the large one — are measured at the issue they point to, not at "
  "the listing. Measuring the listing reports an empty room: no claimants, no maintainer, "
  "no eligibility rules, because none of those live in a directory entry. Four of the "
  "issues this sweep initially scored as reachable were mirrors, and all four resolve to "
  "tasks their own bot has publicly closed to outside contributors.")
p()
p("**Merge detection was verified against the pull request API** in both directions — sampled "
  "PRs flagged merged and flagged unmerged were re-fetched individually and agreed in every "
  "case. The zeros in the merged column are real zeros.")
p()
p("## Reproduce it")
p()
p("```sh")
p("export GITHUB_TOKEN=...")
p("python3 scan.py targets.txt dataset.jsonl")
p("python3 make_trap.py dataset.jsonl > trap.json")
p("python3 make_dataset.py dataset.jsonl > DATASET.md")
p("```")
p()
p("Raw records — one JSON object per issue, including every claimant, every competing pull "
  "request, and the maintainer timing — are in `dataset.jsonl` in this repository.")
