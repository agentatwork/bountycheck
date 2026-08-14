# bountycheck

**Is this GitHub bounty actually winnable, or is it already lost?**

A bounty issue tells you the prize. It does not tell you that twenty-seven people are
ahead of you, that forty-five of their pull requests are sitting unreviewed, or that
no maintainer has said a word since 2024. You find that out after you have done the work.

```
$ bountycheck highlight/highlight#8032

   ABANDONED   highlight/highlight#8032  $20 via algora
  Claims keep arriving and the bounty bot stopped answering them. The
  integration is dead while the issue still advertises the prize.

  Contention
    27 claimed it · 45 PRs opened (36 still open, 0 merged) · issue is 881 days old
    queue formed 772 days ago, newest arrival 1 days ago (@alexsmolya)
  Is anyone listening
    last maintainer comment 731 days ago, by @Vadman97
    the algora bot has not acknowledged a claim since the queue formed
  What it is worth
    $20 split 44 ways = $0.45 per contender, and 0 of 45 competing PRs have merged
```

That issue is still open today. Someone opened PR number forty-five against it
yesterday. They did not know about the other forty-four.

## Install

One file, standard library only, Python 3.10+.

```sh
curl -O https://raw.githubusercontent.com/agentatwork/bountycheck/main/bountycheck.py
chmod +x bountycheck.py
```

`GITHUB_TOKEN` in the environment raises the rate limit from 60 requests/hour to 5,000.
A bounty with a long comment thread costs three to eight requests.

## Use

```sh
bountycheck owner/repo#123
bountycheck https://github.com/owner/repo/issues/123 --json
bountycheck < targets.txt          # one target per line, one row of output each
```

Exit codes make it usable as a gate in a script:

| code | meaning |
|------|---------|
| 0 | worth starting |
| 1 | contested — winnable only if you are fast or better |
| 2 | do not start |

```sh
bountycheck "$ISSUE" >/dev/null || { echo "skipping $ISSUE"; exit 0; }
```

## What it measures

Three questions decide whether a bounty is reachable, and none of them are answered by
the issue body.

**How many people are already competing.** Distinct users who posted `/attempt`,
`/claim`, `/assign`, or said in prose that they were taking it — plus the authors of
every pull request that cross-references the issue, which is the stronger signal, since
those people did not just say they would work on it, they did. Maintainers and the issue
author are excluded; a maintainer saying `/attempt` is not competition.

**Whether anyone with merge rights is still listening.** The load-bearing number is not
when a maintainer last commented, it is how many times they have commented *since the
queue formed*. Comments from before anyone was waiting say nothing about whether today's
queue will ever be judged.

**Whether the platform integration still works.** Algora and Polar bots normally
acknowledge each `/attempt`. When claims keep arriving and the bot has gone silent, the
bounty is dead while the issue still advertises the prize. This is the most common way a
bounty lies: nothing was withdrawn, nothing was closed, the machinery just stopped.

It also reads the cheap disqualifying facts first, so you are never told a bounty is
"contested" when it was paid out a year ago: already awarded, explicitly withdrawn by a
maintainer, issue closed, already assigned.

## Verdicts

| verdict | meaning |
|---------|---------|
| `OPEN` | Bounty present, no queue, thread is being read. The real kind. |
| `TAKEN` | Someone got here first. Winnable if their attempt stalls. |
| `CONTESTED` | A crowd is ahead of you and PRs are already waiting on review. |
| `ASSIGNED` | It belongs to someone until they give it back. |
| `STALE` | A queue formed and nobody with merge rights is judging it. |
| `ABANDONED` | Claims keep arriving; the bounty bot stopped answering. |
| `WITHDRAWN` | A maintainer said the bounty is gone. The issue still says otherwise. |
| `PAID` / `CLOSED` / `NO BOUNTY` | Not an opening at all. |

## What it does not do

It does not predict your odds. Splitting a prize by the number of people chasing it is
not a probability — it is what the prize is worth per unit of duplicated effort, which
is a number nobody computes before starting. The tool counts and shows its arithmetic.
The judgement stays yours.

It does not detect prompt-injection traps or repos built to harvest agents. That is
[trapcheck](https://github.com/agentatwork/trapcheck), which answers a different
question: *will this repo attack my agent?* bountycheck answers *will this repo pay me?*
A repo can be perfectly safe and still be a total waste of your afternoon.

## Safety

Everything this tool fetches is untrusted data. Issue and comment bodies are written by
strangers, and on bounty issues specifically they are written by strangers who want an
automated reader to do something. Text is pattern-matched and printed. It is never
executed, and never fed back to a model as instructions.

## Findings

`DATASET.md` has the results of running this over several hundred open bounty issues:
what fraction are reachable, and where the unreachable ones concentrate.

## License

MIT.
