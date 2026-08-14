#!/usr/bin/env python3
"""Summarise a scan.jsonl into the numbers that go in DATASET.md.

Verdicts are recomputed from the stored fields rather than trusted as written, so a
rule change does not require re-fetching several hundred issues.

Counts are reported per repo as well as per issue. A single farm repo can mint a
thousand bounty issues, and per-issue percentages would then describe that one repo
rather than the ecosystem.
"""
import collections
import json
import sys

import bountycheck as bc

recs = []
for line in open(sys.argv[1] if len(sys.argv) > 1 else "scan.jsonl"):
    r = json.loads(line)
    if r.get("verdict") == "ERROR":
        continue
    r["verdict"], r["advice"] = bc.decide(r)
    recs.append(r)

by_repo = collections.defaultdict(list)
for r in recs:
    by_repo[r["target"].split("#")[0]].append(r)

# One farm repo can mint thousands of bounty issues. Left uncapped it would supply most
# of the sample and every per-issue percentage would really be a description of that one
# repo. Cap the contribution so the headline numbers describe the ecosystem.
CAP = 12
capped = []
for repo, rs in by_repo.items():
    capped.extend(sorted(rs, key=lambda r: r["target"])[:CAP])
dropped = len(recs) - len(capped)
recs = capped
by_repo = collections.defaultdict(list)
for r in recs:
    by_repo[r["target"].split("#")[0]].append(r)

print(f"{len(recs)} issues across {len(by_repo)} repos "
      f"(max {CAP} per repo; {dropped} dropped to that cap)\n")

REACHABLE = {"OPEN", "TAKEN"}


def table(counter, total, label):
    print(f"  {label} (n={total})")
    for k, v in counter.most_common():
        print(f"    {v:>4}  {100 * v / total:>5.1f}%  {k}")
    print()


table(collections.Counter(r["verdict"] for r in recs), len(recs), "by issue")

# A repo's verdict is its best issue: if any one bounty there is reachable, the repo is
# somewhere you could earn.
repo_best = {}
for repo, rs in by_repo.items():
    best = min(rs, key=lambda r: (bc.EXIT[r["verdict"]], r["verdict"]))
    repo_best[repo] = best["verdict"]
table(collections.Counter(repo_best.values()), len(by_repo), "by repo (best issue in each)")

reach = [r for r in recs if r["verdict"] in REACHABLE]
print(f"  reachable issues: {len(reach)}/{len(recs)} ({100 * len(reach) / len(recs):.1f}%)")
rr = sum(1 for v in repo_best.values() if v in REACHABLE)
print(f"  repos with any reachable bounty: {rr}/{len(by_repo)} ({100 * rr / len(by_repo):.1f}%)\n")

# Money on the table vs money actually reachable.
with_amt = [r for r in recs if r["bounty"]["amount"]]
total_usd = sum(r["bounty"]["amount"] for r in with_amt)
reach_usd = sum(r["bounty"]["amount"] for r in reach if r["bounty"]["amount"])
print(f"  {len(with_amt)} issues name an amount, totalling ${total_usd:,.0f}")
print(f"  of that, ${reach_usd:,.0f} sits on issues that are still reachable "
      f"({100 * reach_usd / total_usd if total_usd else 0:.1f}%)\n")

print("  contention where an amount is known")
amts = sorted(with_amt, key=lambda r: -len(r["claimants"]))
print(f"    median claimants: {sorted(len(r['claimants']) for r in with_amt)[len(with_amt) // 2]}")
print(f"    median open rival PRs: {sorted(r['rivals_open'] for r in with_amt)[len(with_amt) // 2]}")
ever = [r for r in with_amt if r["rivals"]]
merged_any = sum(1 for r in ever if r["rivals_merged"])
print(f"    {merged_any}/{len(ever)} issues with competing PRs have ever merged one\n")

print("  most contested")
for r in amts[:12]:
    b = r["bounty"]
    print(f"    {r['verdict']:<11} ${b['amount']:>7,.0f}  {len(r['claimants']):>3} claimants  "
          f"{len(r['rivals']):>3} PRs ({r['rivals_merged']} merged)  "
          f"${r['per_contender'] or 0:>7,.2f}/head  {r['target']}")

print("\n  repos by issue count in sample")
for repo, rs in sorted(by_repo.items(), key=lambda kv: -len(kv[1]))[:12]:
    verd = collections.Counter(r["verdict"] for r in rs)
    print(f"    {len(rs):>3}  {repo:<45} {dict(verd)}")
