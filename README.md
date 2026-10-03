# Weirwright

**Executable change-control gates. Evidence in, verdict out.**

Published by AIArchLab. Principle: governance = policy + executable checks.

## Problem

A team has a written change policy: "every change is reviewed, tested, traceable and verified after deploy." When someone asks "did change X follow the policy?", the evidence is spread across the repository host, the CI system and the deploy log, and nobody checks it per change.

## Who it is for

Engineering leads and architects who own a change policy, and risk or audit readers who need evidence per change.

## What it does

Reads change records and a small policy file. Applies six checks (protected branch, independent review, checks on the exact merged commit, secret scan, ticket link, deploy verification with rollback plan). Reports PASS, FAIL or EXCEPTION (a recorded, approved emergency bypass) for each change, with the evidence behind every result. An EXCEPTION still lists every failed rule.

## Run it in 5 minutes

Requires Python 3.10 or later (tested on 3.10). No other packages.

```
python3 -m weirwright --as-of 2026-10-03          # check the synthetic sample set
python3 -m unittest discover -s tests -v          # 14 tests, one per acceptance criterion
python3 verify_sample.py --n 5 --seed 7           # print evidence for 5 sampled records
```

Exit code: 0 no FAIL, 1 any FAIL, 2 invalid input. Add `--json` for a machine-readable report.

## Documents

- `docs/SPEC.md` - rules, control points, evidence fields, limits.
- `docs/ACCEPTANCE.md` - acceptance criteria, written before the code, each mapped to a test.

## Limits

- All sample data is synthetic. It shows the logic; it is not a benchmark.
- The checker reads files only. It does not connect to any repository host, CI or cloud account.
- A PASS means the recorded evidence matches the rule. It does not mean the change is safe.
- Results are only as reliable as the records fed in; use system logs, not hand-typed data.
- This is an engineering tool, not legal, audit or compliance advice.

## Licence

MIT. See `LICENSE`.
