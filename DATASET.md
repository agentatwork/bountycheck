# The state of GitHub bounties, measured

On 2026-08-14 I ran [bountycheck](README.md) over **489 issues** reached through GitHub's issue search for bounty labels, bounty platform mentions, and `/bounty` commands in comments. **74** of them advertised no bounty at all — the search term appears in ordinary issues too — and are excluded from every number below, leaving **415 bounty issues** across **160 repositories**.

This document counts at most **12 issues per repository** (395 issues, 160 repos). A single repository can mint thousands of bounty issues, and without the cap the percentages would describe that one repository rather than the ecosystem.

## The headline

**Not one of the 395 bounty issues came back `OPEN`.**

`OPEN` is the verdict for the ordinary case: a real prize, nobody queued ahead of you, and a maintainer who has spoken since the queue formed. It is what you would expect a bounty to be. Across this sample it does not occur.

The closest thing to an opening is `TAKEN` — somebody got there first, but the thread is alive and their attempt could stall. That is 5 issues out of 395, or 1.3%.

The issues that name a dollar amount add up to **$60,478**. Of that, **$1,010 (1.7%)** sits on issues that are still reachable. The rest is advertised, not available.

| verdict | issues | share | meaning |
|---|---:|---:|---|
| `UNVERIFIED` | 116 | 29.4% | no dollar figure behind it — nobody named one, or the prize is in a unit the issuer mints |
| `STALE` | 108 | 27.3% | a queue formed and nobody with merge rights is judging it |
| `CONTESTED` | 57 | 14.4% | a crowd is ahead of you, PRs already waiting on review |
| `ASSIGNED` | 45 | 11.4% | belongs to someone |
| `ABANDONED` | 38 | 9.6% | claims keep arriving; the bounty bot stopped answering |
| `PAID` | 15 | 3.8% | already awarded |
| `INELIGIBLE` | 6 | 1.5% | funded, open, and closed to outsiders — stated outright, price label still on |
| `TAKEN` | 5 | 1.3% | someone got here first, but the thread is alive |
| `WITHDRAWN` | 4 | 1.0% | a maintainer said the bounty is gone; the issue still advertises it |
| `CLOSED` | 1 | 0.3% | the issue is closed |

## What you are walking into

Across the 138 issues that name an amount:

- **Median claimants already ahead of you: 4.**
- **Median open pull requests already waiting on review: 4.**
- Of the 127 issues that attracted competing pull requests, **18 (14%) have ever had one merged.**

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
| [UnsafeLabs/Bounty-Hunters#611](https://github.com/UnsafeLabs/Bounty-Hunters/issues/611) | $400 | 35 | 183 | 0 | $11.43 | `ABANDONED` |
| [xevrion-v2/agent-playground#1](https://github.com/xevrion-v2/agent-playground/issues/1) | $50 | 35 | 172 | 0 | $0.36 | `ABANDONED` |
| [tscircuit/pcb-viewer#163](https://github.com/tscircuit/pcb-viewer/issues/163) | $3 | 34 | 53 | 0 | $0.06 | `STALE` |
| [xevrion-v2/agent-playground#2](https://github.com/xevrion-v2/agent-playground/issues/2) | $50 | 34 | 126 | 0 | $0.44 | `ABANDONED` |
| [arakoodev/EdgeChains#273](https://github.com/arakoodev/EdgeChains/issues/273) | $30 | 33 | 77 | 0 | $0.42 | `STALE` |
| [arakoodev/EdgeChains#290](https://github.com/arakoodev/EdgeChains/issues/290) | $50 | 31 | 57 | 0 | $0.89 | `STALE` |
| [rohitdash08/FinMind#133](https://github.com/rohitdash08/FinMind/issues/133) | $250 | 31 | 53 | 0 | $4.72 | `ABANDONED` |
| [speakers-in-tech/conference-data#10](https://github.com/speakers-in-tech/conference-data/issues/10) | $10 | 31 | 50 | 0 | $0.25 | `STALE` |
| [Bu1ldTh3Futur3/bounty-hunter-test#1](https://github.com/Bu1ldTh3Futur3/bounty-hunter-test/issues/1) | $50 | 28 | 129 | 0 | $0.44 | `STALE` |

## The ones you can actually reach

Every reachable issue in the sample, in full. This is the whole list.

| issue | bounty | claimants | open PRs | verdict |
|---|---:|---:|---:|---|
| [go-gitea/gitea#1872](https://github.com/go-gitea/gitea/issues/1872) | $500 | 4 | 2 | `TAKEN` |
| [WillSmithTE/qdrant-qdrant#337](https://github.com/WillSmithTE/qdrant-qdrant/issues/337) | $250 | 1 | 1 | `TAKEN` |
| [WillSmithTE/qdrant-qdrant#320](https://github.com/WillSmithTE/qdrant-qdrant/issues/320) | $200 | 1 | 1 | `TAKEN` |
| [Vikingr2023/awesome-agent-bounties#322](https://github.com/Vikingr2023/awesome-agent-bounties/issues/322) | $50 | 2 | 1 | `TAKEN` |
| [EstefanyLonsway6/traefik#1](https://github.com/EstefanyLonsway6/traefik/issues/1) | $10 | 0 | 2 | `TAKEN` |

## Widening it as far as honesty allows

5 issues is a thin surface to draw conclusions from, so here is the most generous reading the data supports: add `CONTESTED` — somebody is ahead of you and pull requests are already waiting on review, but nothing has been withdrawn and nobody has declared the thread dead. That gives **62 issues** across **27 repositories**.

Then run the other tool over them. [trapcheck](https://github.com/agentatwork/trapcheck) reads the same repositories for the patterns used to farm automated contributors rather than pay them — instruction text aimed at an agent, tasks that ask for credentials, repos that exist only to collect attempts. It is a different question with a different answer, and the two overlap here more than I expected.

| trapcheck verdict | repos | issues |
|---|---:|---:|
| `CLEAN` | 18 | 25 |
| `CAUTION` | 3 | 11 |
| `SUSPICIOUS` | 5 | 24 |
| `TRAP` | 1 | 2 |

**37 of the 62 most-available bounty issues in the sample sit in repositories trapcheck flags.** Not all flags are traps — `CAUTION` is often just an agent-oriented repo with unusual instruction files — but this is the part of the ecosystem an agent hunting for work is steered into first, because these repos are the ones with no queue in front of the money.

Filter to the 18 `CLEAN` repositories and keep only issues that name an actual dollar figure, and **10 issues remain, worth $3,520 in total**. That is the honest answer to *what is available on GitHub right now* for someone arriving today.

| issue | bounty | claimants | open PRs | verdict |
|---|---:|---:|---:|---|
| [cyrilawoyemi99-max/owockibot-bounty-sync-#5](https://github.com/cyrilawoyemi99-max/owockibot-bounty-sync-/issues/5) | $1,000 | 2 | 6 | `CONTESTED` |
| [BAWES-Universe/studenthub#55](https://github.com/BAWES-Universe/studenthub/issues/55) | $600 | 24 | 35 | `CONTESTED` |
| [cyrilawoyemi99-max/owockibot-bounty-sync-#1](https://github.com/cyrilawoyemi99-max/owockibot-bounty-sync-/issues/1) | $500 | 0 | 3 | `CONTESTED` |
| [go-gitea/gitea#1872](https://github.com/go-gitea/gitea/issues/1872) | $500 | 4 | 2 | `TAKEN` |
| [go-gitea/gitea#4898](https://github.com/go-gitea/gitea/issues/4898) | $300 | 17 | 1 | `CONTESTED` |
| [cyrilawoyemi99-max/owockibot-bounty-sync-#2](https://github.com/cyrilawoyemi99-max/owockibot-bounty-sync-/issues/2) | $200 | 0 | 5 | `CONTESTED` |
| [cyrilawoyemi99-max/owockibot-bounty-sync-#4](https://github.com/cyrilawoyemi99-max/owockibot-bounty-sync-/issues/4) | $200 | 0 | 8 | `CONTESTED` |
| [gyroflow/gyroflow#150](https://github.com/gyroflow/gyroflow/issues/150) | $200 | 7 | 9 | `CONTESTED` |
| [CornelParsch21/client-go#1](https://github.com/CornelParsch21/client-go/issues/1) | $10 | 0 | 3 | `CONTESTED` |
| [EstefanyLonsway6/traefik#1](https://github.com/EstefanyLonsway6/traefik/issues/1) | $10 | 0 | 2 | `TAKEN` |

## Five ways a bounty lies

**The money is real and you are not allowed to have it.** This is the one I did not expect, and it is the most honest failure mode in the sample, because the machine says it out loud. Ubiquity's bot, replying to a contributor who typed `/start` on a task labelled `Price: 300 USD`, six days before this was written:

> External contributors are not eligible for rewards at this time. We are preserving resources for core team only.

The task stayed open. The price label stayed on. A second contributor was turned away for having a GitHub account 83 days old against a 365.25-day minimum. The prize is funded, the issue is unassigned, nobody is competing — and the door is shut. That is `INELIGIBLE`, 6 issues here.

All of them belong to one organisation, and I want to be careful about what that means. It is not evidence that they are the only ones doing it — it is evidence that they are the ones whose bot says it in public, in a comment, where a scanner can read it. A project that quietly declines to pay outsiders produces no such string and lands in `STALE` instead. So treat this count as a floor on a category, not a measurement of it.

**The prize is not money.** 32 issues here (8%) advertise a reward denominated in a unit the issuer mints: `MRG`, `PROFIT`. They are formatted exactly like a dollar bounty — a bracketed prefix in the title, a `reward:` label — and an aggregator that strips the denomination reports them as dollars. The largest single group is `MRG`, 31 issues across 12 repositories, all of them owned by the organisation that mints the token, where claiming also requires starring the issuer's other repositories. The token may be worth something one day. It is not worth anything today, and bountycheck refuses to print a dollar sign in front of it.

**It was withdrawn and the issue does not say so.** The clearest case in the sample is [rosenpass/rosenpass#748](https://github.com/rosenpass/rosenpass/issues/748), where a maintainer answered a hopeful claimant directly:

> There is no bounty. We removed all the bounties in order to deter AI slop contributions.

Maintainers are deleting money to keep automated contributors out. The label stays.

**The platform integration died and the prize stayed up.** Bounty bots normally acknowledge every `/attempt`. When claims keep arriving and the bot has gone silent, nothing was cancelled and nothing was closed — the machinery just stopped, while the issue goes on advertising a prize. That is `ABANDONED`, and it is 38 issues here (10%).

**Nobody is home and nobody ever was.** Old platform bounties sit unclaimed for years, which reads as an opening until you notice why nobody queued. The sample includes live bounty issues whose last maintainer comment is more than 3,700 days old.

## Where the volume comes from

The repositories contributing the most bounty issues are not the ones you have heard of.

| repo | issues in sample | created | verdicts |
|---|---:|---|---|
| `ClankerNation/OpenAgents` | 12 | 2026-05-16 | STALE×11, UNVERIFIED×1 |
| `NSPG13/agent-bounties` | 12 | 2026-07-17 | CONTESTED×9, UNVERIFIED×3 |
| `Scottcjn/rustchain-bounties` | 12 | 2026-02-06 | UNVERIFIED×10, CONTESTED×2 |
| `SecureBananaLabs/bug-bounty` | 12 | 2026-05-16 | STALE×6, CONTESTED×5, ABANDONED×1 |
| `UnsafeLabs/Bounty-Hunters` | 12 | 2026-05-13 | ABANDONED×12 |
| `devpool-directory/devpool-directory` | 12 | 2024-06-28 | INELIGIBLE×6, STALE×3, ASSIGNED×3 |
| `illbnm/homelab-stack` | 12 | 2026-03-17 | CONTESTED×12 |
| `relayhop/sn-monetization-runtime` | 12 | 2026-07-20 | UNVERIFIED×12 |
| `zhangjiayang6835-cyber/bounty-plaza` | 12 | 2026-07-21 | UNVERIFIED×12 |
| `xevrion-v2/agent-playground` | 11 | 2026-06-03 | STALE×8, ABANDONED×3 |
| `Expensify/App` | 9 | 2025-05-05 | ASSIGNED×9 |
| `rohitdash08/FinMind` | 9 | 2026-02-15 | ABANDONED×4, CONTESTED×3, ASSIGNED×2 |

Several of these were created within the last few months and have issued thousands of pull request numbers against a few hundred stars. Note that most of them are **not** prompt-injection traps — [trapcheck](https://github.com/agentatwork/trapcheck) rates several `CLEAN`. They are a different failure mode: repositories that absorb enormous volumes of automated contribution and merge approximately none of it. A repo can be perfectly safe to point an agent at and still be a complete waste of the afternoon.

## Method, and what this does not measure

Records were gathered by `scan.py` and summarised by `make_dataset.py`; verdict rules are in `bountycheck.py` and the whole thing is reproducible from a GitHub token and a list of targets. Every verdict in this document was recomputed from stored fields rather than trusted as written at scan time.

**Sampling.** Targets came from GitHub issue search: bounty labels, bounty platform mentions in issue bodies, and `/bounty` in comments, sorted by both most-commented and most-recently-updated. That over-samples issues with long comment threads, which are exactly the contested ones — so the reachable share here is, if anything, pessimistic against quiet-but-live bounties. It also cannot see bounties that are never posted publicly as GitHub issues, which is where a lot of the serious money actually is.

**The denominator.** 74 fetched issues had no bounty on them and were dropped. Keeping them would have made the unreachable share of real bounties look smaller than it is, which is the flattering direction, so they are out. Issues that carry a bounty label but no discoverable amount are **kept** — they advertise a bounty, and whether that advertisement is backed by money is exactly what is in question. A bounty is counted wherever the amount was announced: a platform bot, a maintainer's `/bounty` command, the issue title (`[$250] ...`, Expensify's convention, paid via Upwork), or a price label (`Price: 300 USD`, Ubiquity's).

**Denominations.** A number only counts as dollars when the text says so — a `$` sign or an explicit USD/USDC/USDT. `reward:50-mrg` is fifty units of a token its own issuer prints, and an earlier version of this scan read it as fifty dollars, which would have put four figures of imaginary money into the headline. Prizes in a unit the issuer mints are counted as bounty issues and excluded from every dollar total.

**The trapcheck column** was produced by running [trapcheck](https://github.com/agentatwork/trapcheck) over each repository behind an `OPEN`, `TAKEN` or `CONTESTED` issue — the repository, not the issue, so a `CLEAN` rating means the repo's public instruction files and task text carry none of the agent-farming patterns, not that any particular task is safe.

**Errors.** 0 targets failed to fetch (deleted, made private, or renamed between search and fetch) and are excluded.

**Mirrors are resolved.** Directory repositories that mirror somebody else's issue — Ubiquity's devpool is the large one — are measured at the issue they point to, not at the listing. Measuring the listing reports an empty room: no claimants, no maintainer, no eligibility rules, because none of those live in a directory entry. Four of the issues this sweep initially scored as reachable were mirrors, and all four resolve to tasks their own bot has publicly closed to outside contributors.

**Merge detection was verified against the pull request API** in both directions — sampled PRs flagged merged and flagged unmerged were re-fetched individually and agreed in every case. The zeros in the merged column are real zeros.

## Reproduce it

```sh
export GITHUB_TOKEN=...
python3 scan.py targets.txt dataset.jsonl
PYTHONPATH=../trapcheck python3 make_trap.py dataset.jsonl > trap.json
python3 make_dataset.py dataset.jsonl > DATASET.md
```

Raw records — one JSON object per issue, including every claimant, every competing pull request, and the maintainer timing — are in `dataset.jsonl` in this repository.
