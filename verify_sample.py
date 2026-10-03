"""Sampled verification: draw N records (fixed seed) and print the source fields behind each rule result."""
import argparse, json, random
from datetime import date
from weirwright.rules import evaluate

ap = argparse.ArgumentParser()
ap.add_argument("--n", type=int, default=5)
ap.add_argument("--seed", type=int, default=7)
ap.add_argument("--records", default="data/changes.json")
ap.add_argument("--policy", default="data/policy.json")
ap.add_argument("--as-of", default="2026-10-03")
a = ap.parse_args()
recs = json.load(open(a.records)); pol = json.load(open(a.policy))
for rec in random.Random(a.seed).sample(recs, min(a.n, len(recs))):
    res = evaluate(rec, pol, date.fromisoformat(a.as_of))
    print(f"== {rec['id']} verdict={res['verdict']}  (compare with {a.records}, id={rec['id']})")
    for k, v in res["rules"].items():
        print(f"   {k} {'ok  ' if v['ok'] else 'FAIL'} {v['evidence']}")
