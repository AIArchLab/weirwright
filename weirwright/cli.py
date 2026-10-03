import argparse, json, sys
from datetime import date
from .rules import evaluate, InputError


def load(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        raise InputError(f"{path}: {e}")


def run(policy_path, records_path, as_of):
    pol = load(policy_path)
    recs = load(records_path)
    if not isinstance(recs, list):
        raise InputError(f"{records_path}: expected a JSON array of records")
    return [evaluate(r, pol, as_of) for r in recs]


def main(argv=None):
    ap = argparse.ArgumentParser(prog="weirwright")
    ap.add_argument("--policy", default="data/policy.json")
    ap.add_argument("--records", default="data/changes.json")
    ap.add_argument("--as-of", default=date.today().isoformat())
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    try:
        out = run(a.policy, a.records, date.fromisoformat(a.as_of))
    except (InputError, ValueError) as e:
        print(f"input error: {e}", file=sys.stderr)
        return 2
    if a.json:
        print(json.dumps(out, indent=2, ensure_ascii=False))
    else:
        for r in out:
            failed = [k for k, v in r["rules"].items() if not v["ok"]]
            print(f"{r['id']:<10} {r['verdict']:<10} failed: {','.join(failed) or '-'}")
            for k in failed:
                print(f"    {k}: {r['rules'][k]['evidence']}")
            if r["bypass_note"]:
                print(f"    bypass: {r['bypass_note']}")
        c = {}
        for r in out:
            c[r["verdict"]] = c.get(r["verdict"], 0) + 1
        print("summary:", ", ".join(f"{k}={v}" for k, v in sorted(c.items())))
    return 1 if any(r["verdict"] == "FAIL" for r in out) else 0
