#!/usr/bin/env python3
"""Run trapcheck over the repositories behind the still-available issues in a scan.

bountycheck answers "will this repo pay me?". trapcheck answers "will this repo attack
my agent?". The interesting number is the overlap, and the only honest way to get it is
to run the second tool over the output of the first rather than eyeball the repo names.

    PYTHONPATH=../trapcheck python3 make_trap.py dataset.jsonl > trap.json

Writes {repo: trapcheck record} for every repo with at least one OPEN, TAKEN or
CONTESTED issue. Repos that fail to fetch get an {"error": ...} entry and are counted
as unknown rather than silently dropped.
"""
import json
import sys

import bountycheck as bc
import trapcheck as tc

WIDE = {"OPEN", "TAKEN", "CONTESTED"}

recs, seen = [], set()
for path in sys.argv[1:]:
    for line in open(path):
        r = json.loads(line)
        if r["target"] in seen or r.get("verdict") == "ERROR":
            continue
        seen.add(r["target"])
        r["verdict"], _ = bc.decide(r)
        recs.append(r)

repos = sorted({r["target"].split("#")[0] for r in recs if r["verdict"] in WIDE})
out = {}
for repo in repos:
    owner, name = repo.split("/")
    try:
        out[repo] = tc.analyse(owner, name, None, tc.GH())
    except SystemExit as e:
        out[repo] = {"error": str(e)}
    except Exception as e:
        out[repo] = {"error": f"{type(e).__name__}: {e}"}
    print(f"{repo:56} {out[repo].get('verdict') or out[repo].get('error')}", file=sys.stderr)

json.dump(out, sys.stdout, indent=1)
