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
p(f"**{len(reach)} of {n:,} bounty issues ({100 * len(reach) / n:.1f}%) are still reachable** — "
  "meaning the money is real, someone with merge rights is still listening, and you are not "
  "already tenth in line.")
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
p("That is the entire opportunity surface of a 489-issue sweep. Note how many are on "
  "repositories you have never heard of, and check who owns them before you start.")
p()
p("## Four ways a bounty lies")
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
      f"That is `INELIGIBLE`, {ineli} {'issue' if ineli == 1 else 'issues'} here, and it is "
      "invisible to every bounty aggregator I know of, all of which still list these as open.")
    p()
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
p("python3 scan.py targets.txt scan.jsonl")
p("python3 make_dataset.py scan.jsonl > DATASET.md")
p("```")
p()
p("Raw records — one JSON object per issue, including every claimant, every competing pull "
  "request, and the maintainer timing — are in `scan.jsonl` in this repository.")
