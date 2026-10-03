from datetime import date

REQUIRED_FIELDS = ["id", "author", "target_branch", "via_pull_request", "merged_sha"]


class InputError(Exception):
    pass


def validate(record):
    for f in REQUIRED_FIELDS:
        if f not in record:
            raise InputError(f"record {record.get('id', '?')}: missing field '{f}'")


def r1(rec, pol):
    ok = rec["target_branch"] != pol["protected_branch"] or rec["via_pull_request"] is True
    return ok, f"target_branch={rec['target_branch']}, via_pull_request={rec['via_pull_request']}"


def r2(rec, pol):
    author = rec["author"]
    others = [a for a in rec.get("approvals", []) if a != author]
    if not others:
        return False, f"approvals={rec.get('approvals', [])}, author={author}: no independent approval"
    sensitive = [f for f in rec.get("files", [])
                 if any(f.startswith(p) for p in pol["sensitive_paths"])]
    if sensitive and not any(a in pol["code_owners"] for a in others):
        return False, f"sensitive files {sensitive} need code-owner approval; approvals={others}"
    return True, f"independent approvals={others}, sensitive_files={sensitive}"


def r3(rec, pol):
    sha = rec["merged_sha"]
    by_name = {}
    for c in rec.get("checks", []):
        by_name.setdefault(c["name"], []).append(c)
    problems = []
    for name in pol["required_checks"]:
        hit = [c for c in by_name.get(name, []) if c.get("sha") == sha]
        if not hit:
            seen = [c.get("sha") for c in by_name.get(name, [])]
            problems.append(f"{name}: no result on {sha} (seen on {seen})")
        elif not all(c["status"] == "passed" for c in hit):
            problems.append(f"{name}: status {[c['status'] for c in hit]}")
    if problems:
        return False, "; ".join(problems)
    return True, f"required checks {pol['required_checks']} passed on {sha}"


def r4(rec, pol):
    s = rec.get("secret_scan")
    if not s:
        return False, "no secret_scan record"
    if s.get("sha") != rec["merged_sha"]:
        return False, f"scan on {s.get('sha')}, merged {rec['merged_sha']}"
    return s.get("status") == "clean", f"secret_scan.status={s.get('status')}"


def r5(rec, pol):
    t = rec.get("ticket_id")
    return bool(t), f"ticket_id={t}"


def r6(rec, pol):
    d = rec.get("deploy")
    if not d:
        return False, "no deploy record"
    problems = []
    if d.get("sha") != rec["merged_sha"]:
        problems.append(f"deploy.sha={d.get('sha')} != merged {rec['merged_sha']}")
    if d.get("health_check") != "passed":
        problems.append(f"health_check={d.get('health_check')}")
    if not rec.get("rollback_plan"):
        problems.append("no rollback_plan")
    if problems:
        return False, "; ".join(problems)
    return True, f"deploy.sha={d['sha']}, health_check=passed, rollback_plan present"


RULES = [("R1", r1), ("R2", r2), ("R3", r3), ("R4", r4), ("R5", r5), ("R6", r6)]


def check_bypass(rec, as_of):
    b = rec.get("bypass")
    if not b:
        return None
    problems = []
    if not b.get("approver") or b.get("approver") == rec["author"]:
        problems.append("approver missing or same as author")
    if not b.get("reason"):
        problems.append("reason empty")
    due = b.get("post_review_due")
    if not due:
        problems.append("post_review_due missing")
    elif not b.get("post_review_done") and date.fromisoformat(due) < as_of:
        problems.append(f"post-review overdue since {due}")
    return (not problems), ("; ".join(problems) or "approver, reason and post-review plan recorded")


def evaluate(rec, pol, as_of):
    validate(rec)
    results = {}
    for rid, fn in RULES:
        ok, ev = fn(rec, pol)
        results[rid] = {"ok": bool(ok), "evidence": ev}
    all_ok = all(r["ok"] for r in results.values())
    bypass = check_bypass(rec, as_of)
    if bypass is None:
        verdict = "PASS" if all_ok else "FAIL"
        bnote = None
    else:
        bok, bnote = bypass
        verdict = "PASS" if all_ok and bok else ("EXCEPTION" if bok else "FAIL")
        if all_ok and bok:
            verdict = "PASS"
    return {"id": rec["id"], "verdict": verdict, "rules": results, "bypass_note": bnote}
