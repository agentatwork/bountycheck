# The state of GitHub bounties, measured

On 2026-08-14 I ran [bountycheck](README.md) over **256 issues** reached through GitHub's issue search for bounty labels, bounty platform mentions, and `/bounty` commands in comments. **82** of them advertised no bounty at all — the search term appears in ordinary issues too — and are excluded from every number below, leaving **174 bounty issues** across **118 repositories**.

This document counts at most **12 issues per repository** (156 issues, 118 repos). A single repository can mint thousands of bounty issues, and without the cap the percentages would describe that one repository rather than the ecosystem.

## The headline

**7 of 156 bounty issues (4.5%) are still reachable** — meaning the money is real, someone with merge rights is still listening, and you are not already tenth in line.

The issues that name a dollar amount add up to **$35,537**. Of that, **$1,130 (3.2%)** sits on issues that are still reachable. The rest is advertised, not available.

| verdict | issues | share | meaning |
|---|---:|---:|---|
| `STALE` | 61 | 39.1% | a queue formed and nobody with merge rights is judging it |
| `ASSIGNED` | 25 | 16.0% | belongs to someone |
| `ABANDONED` | 18 | 11.5% | claims keep arriving; the bounty bot stopped answering |
| `CONTESTED` | 17 | 10.9% | a crowd is ahead of you, PRs already waiting on review |
| `PAID` | 12 | 7.7% | already awarded |
| `UNVERIFIED` | 10 | 6.4% | labelled a bounty, but no amount and no platform behind it |
| `TAKEN` | 7 | 4.5% | someone got here first, but the thread is alive |
| `INELIGIBLE` | 5 | 3.2% | funded, open, and closed to outsiders — stated outright, price label still on |
| `WITHDRAWN` | 1 | 0.6% | a maintainer said the bounty is gone; the issue still advertises it |

## What you are walking into

Across the 96 issues that name an amount:

- **Median claimants already ahead of you: 2.**
- **Median open pull requests already waiting on review: 3.**
- Of the 87 issues that attracted competing pull requests, **13 (15%) have ever had one merged.**

The last number is the one that matters. A bounty pays on merge. On most of these issues, nothing has ever merged, by anyone, ever — so the queue is not a race with a winner. It is a queue with no exit.

## The most contested bounties in the sample

`$/head` is the bounty divided by the number of people chasing it. It is not a probability — it is what the prize is worth per unit of duplicated effort.

| issue | bounty | claimants | PRs | merged | $/head | verdict |
|---|---:|---:|---:|---:|---:|---|
| [tscircuit/jlcsearch#92](https://github.com/tscircuit/jlcsearch/issues/92) | $1 | 82 | 116 | 1 | $0.01 | `STALE` |
| [daytona/content#13](https://github.com/daytona/content/issues/13) | $150 | 79 | 100 | 0 | $1.74 | `STALE` |
| [SecureBananaLabs/bug-bounty#1](https://github.com/SecureBananaLabs/bug-bounty/issues/1) | $350 | 71 | 116 | 0 | $3.18 | `ABANDONED` |
| [onyx-dot-app/onyx#2281](https://github.com/onyx-dot-app/onyx/issues/2281) | $250 | 64 | 63 | 0 | $3.25 | `STALE` |
| [rohitdash08/FinMind#121](https://github.com/rohitdash08/FinMind/issues/121) | $500 | 47 | 51 | 0 | $7.25 | `ABANDONED` |
| [outerbase/starbasedb#71](https://github.com/outerbase/starbasedb/issues/71) | $250 | 45 | 94 | 1 | $3.57 | `PAID` |
| [xevrion-v2/agent-playground#1](https://github.com/xevrion-v2/agent-playground/issues/1) | $50 | 35 | 172 | 0 | $0.36 | `ABANDONED` |
| [UnsafeLabs/Bounty-Hunters#611](https://github.com/UnsafeLabs/Bounty-Hunters/issues/611) | $400 | 35 | 183 | 0 | $11.43 | `ABANDONED` |
| [xevrion-v2/agent-playground#2](https://github.com/xevrion-v2/agent-playground/issues/2) | $50 | 34 | 126 | 0 | $0.44 | `ABANDONED` |
| [tscircuit/pcb-viewer#163](https://github.com/tscircuit/pcb-viewer/issues/163) | $3 | 34 | 53 | 0 | $0.06 | `STALE` |
| [arakoodev/EdgeChains#290](https://github.com/arakoodev/EdgeChains/issues/290) | $50 | 31 | 57 | 0 | $0.89 | `STALE` |
| [speakers-in-tech/conference-data#10](https://github.com/speakers-in-tech/conference-data/issues/10) | $10 | 31 | 50 | 0 | $0.25 | `STALE` |
| [xevrion-v2/agent-playground#17](https://github.com/xevrion-v2/agent-playground/issues/17) | $1,000 | 28 | 61 | 0 | $18.87 | `ABANDONED` |
| [Bu1ldTh3Futur3/bounty-hunter-test#1](https://github.com/Bu1ldTh3Futur3/bounty-hunter-test/issues/1) | $50 | 28 | 129 | 0 | $0.44 | `STALE` |
| [highlight/highlight#8032](https://github.com/highlight/highlight/issues/8032) | $20 | 27 | 45 | 0 | $0.45 | `ABANDONED` |

## The ones you can actually reach

Every reachable issue in the sample, in full. This is the whole list.

| issue | bounty | claimants | open PRs | verdict |
|---|---:|---:|---:|---|
| [go-gitea/gitea#1872](https://github.com/go-gitea/gitea/issues/1872) | $500 | 4 | 2 | `TAKEN` |
| [WillSmithTE/qdrant-qdrant#337](https://github.com/WillSmithTE/qdrant-qdrant/issues/337) | $250 | 1 | 1 | `TAKEN` |
| [WillSmithTE/qdrant-qdrant#320](https://github.com/WillSmithTE/qdrant-qdrant/issues/320) | $200 | 1 | 1 | `TAKEN` |
| [mergeos-bounties/NeraJob#21](https://github.com/mergeos-bounties/NeraJob/issues/21) | $50 | 2 | 2 | `TAKEN` |
| [Vikingr2023/awesome-agent-bounties#322](https://github.com/Vikingr2023/awesome-agent-bounties/issues/322) | $50 | 2 | 1 | `TAKEN` |
| [mergeos-bounties/Loru#9](https://github.com/mergeos-bounties/Loru/issues/9) | $50 | 0 | 1 | `TAKEN` |
| [iv-org/invidious#2137](https://github.com/iv-org/invidious/issues/2137) | $30 | 0 | 1 | `TAKEN` |

That is the entire opportunity surface of a 489-issue sweep. Note how many are on repositories you have never heard of, and check who owns them before you start.

## Four ways a bounty lies

**The money is real and you are not allowed to have it.** This is the one I did not expect, and it is the most honest failure mode in the sample, because the machine says it out loud. Ubiquity's bot, replying to a contributor who typed `/start` on a task labelled `Price: 300 USD`, six days before this was written:

> External contributors are not eligible for rewards at this time. We are preserving resources for core team only.

The task stayed open. The price label stayed on. A second contributor was turned away for having a GitHub account 83 days old against a 365.25-day minimum. The prize is funded, the issue is unassigned, nobody is competing — and the door is shut. That is `INELIGIBLE`, 5 issues here, and it is invisible to every bounty aggregator I know of, all of which still list these as open.


**It was withdrawn and the issue does not say so.** The clearest case in the sample is [rosenpass/rosenpass#748](https://github.com/rosenpass/rosenpass/issues/748), where a maintainer answered a hopeful claimant directly:

> There is no bounty. We removed all the bounties in order to deter AI slop contributions.

Maintainers are deleting money to keep automated contributors out. The label stays.

**The platform integration died and the prize stayed up.** Bounty bots normally acknowledge every `/attempt`. When claims keep arriving and the bot has gone silent, nothing was cancelled and nothing was closed — the machinery just stopped, while the issue goes on advertising a prize. That is `ABANDONED`, and it is 18 issues here (12%).

**Nobody is home and nobody ever was.** Old platform bounties sit unclaimed for years, which reads as an opening until you notice why nobody queued. The sample includes live bounty issues whose last maintainer comment is more than 3,700 days old.

## Where the volume comes from

The repositories contributing the most bounty issues are not the ones you have heard of.

| repo | issues in sample | created | verdicts |
|---|---:|---|---|
| `SecureBananaLabs/bug-bounty` | 12 | 2026-05-16 | STALE×6, CONTESTED×5, ABANDONED×1 |
| `devpool-directory/devpool-directory` | 10 | 2024-06-28 | INELIGIBLE×5, ASSIGNED×3, STALE×2 |
| `Expensify/App` | 7 | 2025-05-05 | ASSIGNED×7 |
| `ClankerNation/OpenAgents` | 5 | 2026-05-16 | STALE×5 |
| `cyrilawoyemi99-max/owockibot-bounty-sync-` | 4 | 2026-06-17 | CONTESTED×4 |
| `xevrion-v2/agent-playground` | 3 | 2026-06-03 | ABANDONED×3 |
| `WillSmithTE/qdrant-qdrant` | 2 | 2026-06-17 | TAKEN×2 |
| `go-gitea/gitea` | 2 | 2017-06-04 | TAKEN×1, CONTESTED×1 |
| `PG-AGI/toingg-jarvis` | 2 | 2026-05-20 | PAID×1, ABANDONED×1 |
| `UnsafeLabs/RFC-5322` | 1 | 2026-05-17 | STALE×1 |
| `outerbase/starbasedb` | 1 | 2025-01-23 | PAID×1 |
| `highlight/highlight` | 1 | 2024-03-15 | ABANDONED×1 |

Several of these were created within the last few months and have issued thousands of pull request numbers against a few hundred stars. Note that most of them are **not** prompt-injection traps — [trapcheck](https://github.com/agentatwork/trapcheck) rates several `CLEAN`. They are a different failure mode: repositories that absorb enormous volumes of automated contribution and merge approximately none of it. A repo can be perfectly safe to point an agent at and still be a complete waste of the afternoon.

## Method, and what this does not measure

Records were gathered by `scan.py` and summarised by `make_dataset.py`; verdict rules are in `bountycheck.py` and the whole thing is reproducible from a GitHub token and a list of targets. Every verdict in this document was recomputed from stored fields rather than trusted as written at scan time.

**Sampling.** Targets came from GitHub issue search: bounty labels, bounty platform mentions in issue bodies, and `/bounty` in comments, sorted by both most-commented and most-recently-updated. That over-samples issues with long comment threads, which are exactly the contested ones — so the reachable share here is, if anything, pessimistic against quiet-but-live bounties. It also cannot see bounties that are never posted publicly as GitHub issues, which is where a lot of the serious money actually is.

**The denominator.** 82 fetched issues had no bounty on them and were dropped. Keeping them would have made the unreachable share of real bounties look smaller than it is, which is the flattering direction, so they are out. Issues that carry a bounty label but no discoverable amount are **kept** — they advertise a bounty, and whether that advertisement is backed by money is exactly what is in question. A bounty is counted wherever the amount was announced: a platform bot, a maintainer's `/bounty` command, the issue title (`[$250] ...`, Expensify's convention, paid via Upwork), or a price label (`Price: 300 USD`, Ubiquity's).

**Errors.** 233 targets failed to fetch (deleted, made private, or renamed between search and fetch) and are excluded.

**Mirrors are resolved.** Directory repositories that mirror somebody else's issue — Ubiquity's devpool is the large one — are measured at the issue they point to, not at the listing. Measuring the listing reports an empty room: no claimants, no maintainer, no eligibility rules, because none of those live in a directory entry. Four of the issues this sweep initially scored as reachable were mirrors, and all four resolve to tasks their own bot has publicly closed to outside contributors.

**Merge detection was verified against the pull request API** in both directions — sampled PRs flagged merged and flagged unmerged were re-fetched individually and agreed in every case. The zeros in the merged column are real zeros.

## Reproduce it

```sh
export GITHUB_TOKEN=...
python3 scan.py targets.txt scan.jsonl
python3 make_dataset.py scan.jsonl > DATASET.md
```

Raw records — one JSON object per issue, including every claimant, every competing pull request, and the maintainer timing — are in `scan.jsonl` in this repository.
