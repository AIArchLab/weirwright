"""Generates the synthetic sample set and expected verdicts. All names and ids are invented."""
import json, copy

base = {
    "id": "CHG-001", "author": "kai", "target_branch": "main", "via_pull_request": True,
    "files": ["app/service.py"], "approvals": ["mia"], "merged_sha": "a1b2c3",
    "checks": [{"name": "unit-tests", "status": "passed", "sha": "a1b2c3"},
               {"name": "static-analysis", "status": "passed", "sha": "a1b2c3"}],
    "secret_scan": {"status": "clean", "sha": "a1b2c3"}, "ticket_id": "TKT-101",
    "deploy": {"sha": "a1b2c3", "health_check": "passed"}, "rollback_plan": "redeploy previous tag"}

recs, exp = [], {}
def add(n, verdict, fn=None):
    r = copy.deepcopy(base)
    r["id"] = f"CHG-{n:03d}"
    r["merged_sha"] = r["secret_scan"]["sha"] = r["deploy"]["sha"] = f"sha{n:03d}"
    for c in r["checks"]: c["sha"] = f"sha{n:03d}"
    r["ticket_id"] = f"TKT-{100+n}"
    if fn: fn(r)
    recs.append(r); exp[r["id"]] = verdict

add(1, "PASS")
add(2, "FAIL", lambda r: r.update(via_pull_request=False))
add(3, "FAIL", lambda r: r.update(approvals=["kai"]))
add(4, "FAIL", lambda r: r.update(files=["infra/network.tf"], approvals=["mia"]))
add(5, "PASS", lambda r: r.update(files=["infra/network.tf"], approvals=["lin"]))
def stale(r): r["checks"][0]["sha"] = "old000"
add(6, "FAIL", stale)
add(7, "FAIL", lambda r: r.update(checks=r["checks"][:1]))
add(8, "FAIL", lambda r: r["secret_scan"].update(status="found"))
add(9, "FAIL", lambda r: r.update(ticket_id=""))
add(10, "FAIL", lambda r: r["deploy"].update(health_check="failed"))
add(11, "FAIL", lambda r: r.update(rollback_plan=""))
def emerg(r):
    r.update(approvals=[], ticket_id="")
    r["bypass"] = {"approver": "lin", "reason": "production outage", "post_review_due": "2026-10-10", "post_review_done": False}
add(12, "EXCEPTION", emerg)
def emerg_overdue(r):
    emerg(r); r["bypass"]["post_review_due"] = "2026-09-20"
add(13, "FAIL", emerg_overdue)
def emerg_self(r):
    emerg(r); r["bypass"]["approver"] = "kai"
add(14, "FAIL", emerg_self)
add(15, "FAIL", lambda r: r["deploy"].update(sha="other99"))
json.dump(recs, open("data/changes.json", "w"), indent=2)
json.dump({"as_of": "2026-10-03", "expected": exp}, open("data/expected.json", "w"), indent=2)
