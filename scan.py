#!/usr/bin/env python3
"""Run bountycheck over a list of targets and write one JSON record per line.

Resumable: targets already present in the output file are skipped, so a rate-limit
stall or a restart costs nothing already paid for.
"""
import json
import sys
import time

from bountycheck import GH, analyse, parse_target

targets = [ln.strip() for ln in open(sys.argv[1]) if ln.strip() and not ln.startswith("#")]
out_path = sys.argv[2]

done = set()
try:
    with open(out_path) as fh:
        for line in fh:
            try:
                done.add(json.loads(line)["target"])
            except Exception:
                pass
except FileNotFoundError:
    pass

gh = GH()
with open(out_path, "a") as fh:
    for i, t in enumerate(targets, 1):
        if t in done:
            continue
        try:
            rec = analyse(*parse_target(t), gh)
        except SystemExit as e:
            rec = {"target": t, "verdict": "ERROR", "error": str(e)}
        except Exception as e:  # a single bad issue must not end a 499-issue run
            rec = {"target": t, "verdict": "ERROR", "error": f"{type(e).__name__}: {e}"}
        fh.write(json.dumps(rec) + "\n")
        fh.flush()
        print(f"[{i}/{len(targets)}] {rec['verdict']:<10} {t}", flush=True)
        time.sleep(0.4)
