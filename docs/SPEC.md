# Weirwright - Specification v0.3

Publisher: AIArchLab
Tagline: executable change-control gates; evidence in, verdict out
Status: candidate, not published
Scenario: fully self-authored. All data is synthetic. No client, case or company information is used.

## 1. Problem

A small engineering team (up to 5 people) has written change-control rules in a document. Nobody can show, for a given change, whether the rules were actually followed. The rule says "every change is reviewed"; the evidence is spread across the repository host, the CI system and the deploy log.

This tool turns six written rules into six executable checks over change records, and reports for each change: pass, fail, or exception (a bypass that was recorded and approved).

## 2. Audience

- Engineering lead or architect who owns the change policy.
- Risk or audit reader who needs evidence per change, not a policy document.

## 3. Principle

Policy = written rule + executable check. The check reads the actual recorded state of a change, not the declared state.

## 4. Rules and control points

| ID | Rule (plain language) | Control point | Evidence field in record |
|----|----------------------|---------------|--------------------------|
| R1 | Changes reach the protected branch only through a pull request. | Branch protection | `target_branch`, `via_pull_request` |
| R2 | At least one approval from someone other than the author. Changes touching sensitive paths need an approval from a listed code owner. | Review gate | `author`, `approvals[]`, `files[]` |
| R3 | Required checks passed on the exact commit that was merged. | CI gate | `merged_sha`, `checks[]` (`name`, `status`, `sha`) |
| R4 | No secret detected in the change. | Secret scan | `secret_scan.status`, `secret_scan.sha` |
| R5 | The change links to a ticket. | Traceability | `ticket_id` |
| R6 | The deploy record names the merged commit, the post-deploy health check passed, and a rollback plan exists. | Deploy verification | `deploy.sha`, `deploy.health_check`, `rollback_plan` |

## 5. Bypass handling

A record with `bypass` set (emergency change) is not a pass. It is reported as EXCEPTION when all of the following hold, otherwise FAIL:

- `bypass.approver` is set and differs from the author;
- `bypass.reason` is not empty;
- `bypass.post_review_due` is set, and either `bypass.post_review_done` is true or the due date is not yet past the report date.

A bypass never hides a rule result: the per-rule results are still listed.

## 6. Inputs and outputs

- Policy: JSON (`policy.json`): protected branch, required check names, sensitive path prefixes, code owners.
- Records: JSON array of change records (see section 4 for fields).
- Report date: `--as-of YYYY-MM-DD` (default: today).
- Output: text table, or `--json` machine-readable report. Exit code 0 if no FAIL, 1 if any FAIL, 2 on invalid input.

## 7. Out of scope

- Connecting to any real repository host, CI or cloud account. This version reads files only.
- Judging code quality or security of the change itself.
- Legal or compliance conclusions.

## 8. Limits to state publicly

- The checker is only as good as the records fed to it. Records must come from system logs, not typed by hand.
- A pass means the recorded evidence matches the rule, not that the change is safe.
- Synthetic sample data demonstrates the logic; it is not a benchmark.
