import copy, json, os, subprocess, sys, tempfile, unittest
from datetime import date
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from weirwright.rules import evaluate
from weirwright.cli import main

POL = json.load(open(os.path.join(ROOT, "data/policy.json")))
GOOD = {"id": "T", "author": "kai", "target_branch": "main", "via_pull_request": True,
        "files": ["app/a.py"], "approvals": ["mia"], "merged_sha": "s1",
        "checks": [{"name": "unit-tests", "status": "passed", "sha": "s1"},
                   {"name": "static-analysis", "status": "passed", "sha": "s1"}],
        "secret_scan": {"status": "clean", "sha": "s1"}, "ticket_id": "TKT-1",
        "deploy": {"sha": "s1", "health_check": "passed"}, "rollback_plan": "rollback"}
AS_OF = date(2026, 10, 3)

def ev(**kw):
    r = copy.deepcopy(GOOD); r.update(kw); return evaluate(r, POL, AS_OF)

class T(unittest.TestCase):
    def test_ac01(self): self.assertEqual(ev()["verdict"], "PASS")
    def test_ac02(self): self.assertFalse(ev(via_pull_request=False)["rules"]["R1"]["ok"])
    def test_ac03(self): self.assertFalse(ev(approvals=["kai"])["rules"]["R2"]["ok"])
    def test_ac04(self):
        self.assertFalse(ev(files=["infra/x.tf"])["rules"]["R2"]["ok"])
        self.assertTrue(ev(files=["infra/x.tf"], approvals=["omar"])["rules"]["R2"]["ok"])
    def test_ac05(self):
        c = copy.deepcopy(GOOD["checks"]); c[0]["sha"] = "old"
        self.assertFalse(ev(checks=c)["rules"]["R3"]["ok"])
    def test_ac06(self): self.assertFalse(ev(checks=GOOD["checks"][:1])["rules"]["R3"]["ok"])
    def test_ac07(self):
        self.assertFalse(ev(secret_scan={"status": "found", "sha": "s1"})["rules"]["R4"]["ok"])
        self.assertFalse(ev(secret_scan={"status": "clean", "sha": "old"})["rules"]["R4"]["ok"])
    def test_ac08(self): self.assertFalse(ev(ticket_id="")["rules"]["R5"]["ok"])
    def test_ac09(self):
        self.assertFalse(ev(deploy={"sha": "x", "health_check": "passed"})["rules"]["R6"]["ok"])
        self.assertFalse(ev(deploy={"sha": "s1", "health_check": "failed"})["rules"]["R6"]["ok"])
        self.assertFalse(ev(rollback_plan="")["rules"]["R6"]["ok"])
    def test_ac10(self):
        r = ev(approvals=[], bypass={"approver": "lin", "reason": "outage", "post_review_due": "2026-10-10"})
        self.assertEqual(r["verdict"], "EXCEPTION")
        self.assertFalse(r["rules"]["R2"]["ok"])
    def test_ac11(self):
        self.assertEqual(ev(approvals=[], bypass={"approver": "kai", "reason": "x", "post_review_due": "2026-10-10"})["verdict"], "FAIL")
        self.assertEqual(ev(approvals=[], bypass={"approver": "lin", "reason": "x", "post_review_due": "2026-09-01"})["verdict"], "FAIL")
    def test_ac12(self):
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
            f.write("{bad")
        self.assertEqual(main(["--records", f.name, "--policy", os.path.join(ROOT, "data/policy.json")]), 2)
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
            json.dump([{"id": "Z"}], f)
        self.assertEqual(main(["--records", f.name, "--policy", os.path.join(ROOT, "data/policy.json")]), 2)
    def test_ac13(self):
        exp = json.load(open(os.path.join(ROOT, "data/expected.json")))
        recs = json.load(open(os.path.join(ROOT, "data/changes.json")))
        self.assertEqual(len(recs), len(exp["expected"]))
        for r in recs:
            got = evaluate(r, POL, date.fromisoformat(exp["as_of"]))["verdict"]
            self.assertEqual(got, exp["expected"][r["id"]], r["id"])
    def test_ac14(self):
        o = subprocess.run([sys.executable, "verify_sample.py", "--n", "3", "--seed", "7"], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(o.returncode, 0)
        self.assertEqual(o.stdout.count("== CHG-"), 3)
        o2 = subprocess.run([sys.executable, "verify_sample.py", "--n", "3", "--seed", "7"], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(o.stdout, o2.stdout)

if __name__ == "__main__":
    unittest.main()
