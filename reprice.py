#!/usr/bin/env python3
"""Re-derive the prize block on existing scan records without re-walking every thread.

A full scan costs about ten API calls per issue - most of them paging comments and
timelines - which is an hour of rate limit for five hundred issues. When only the
amount-parsing rules change, the comment walk is wasted work: the rules that read a
title or a label need the issue and nothing else.

So: keep every record whose amount came from a bot or a maintainer command exactly as
scanned, and for the rest re-fetch one issue each and re-run the title/label rules. One
call per record instead of ten, and the result is the same as a full re-scan under the
new rules.

    python3 reprice.py in.jsonl [in2.jsonl ...] > out.jsonl
"""
import json
import sys

import bountycheck as bc

gh = bc.GH()
done = 0
for path in sys.argv[1:]:
    for line in open(path):
        r = json.loads(line)
        b = r.get("bounty") or {}
        # An amount that came out of a comment is unaffected by these rules; leave it.
        if r.get("verdict") == "ERROR" or b.get("amount") is not None:
            print(json.dumps(r), flush=True)
            continue
        # Mirrors are measured at the issue they point to, so that is the issue to re-read.
        target = r.get("mirror_of") or r["target"]
        owner, name, num = bc.parse_target(target)
        try:
            issue = gh.issue(owner, name, num)
        except SystemExit as e:
            print(f"stopping at {target}: {e}", file=sys.stderr)
            print(json.dumps(r), flush=True)
            continue
        if issue:
            fresh = bc.find_bounty(issue, [])
            # find_bounty with no comments cannot see a platform bot, and by construction
            # there was no amount to lose. Everything else is re-derived.
            fresh["platform"] = fresh["platform"] or b.get("platform")
            r["bounty"] = fresh
            r["verdict"], r["advice"] = bc.decide(r)
        print(json.dumps(r), flush=True)
        done += 1
print(f"repriced {done}", file=sys.stderr)
