# Acceptance criteria (written before the build)

Fixed before code was written. Each criterion maps to at least one test in `tests/test_weirwright.py`.

| ID | Criterion | Test |
|----|-----------|------|
| AC-01 | A record meeting all six rules is reported PASS. | test_ac01 |
| AC-02 | Direct push to the protected branch fails R1. | test_ac02 |
| AC-03 | Self-approval alone fails R2. | test_ac03 |
| AC-04 | A change touching a sensitive path without a code-owner approval fails R2. | test_ac04 |
| AC-05 | A passing check recorded on an older commit than the merged one fails R3 (stale evidence). | test_ac05 |
| AC-06 | A missing required check fails R3. | test_ac06 |
| AC-07 | A failed or stale secret scan fails R4. | test_ac07 |
| AC-08 | A missing ticket fails R5. | test_ac08 |
| AC-09 | Deploy of a different commit than merged, a failed health check, or no rollback plan fails R6. | test_ac09 |
| AC-10 | A complete bypass is EXCEPTION, not PASS; per-rule results stay visible. | test_ac10 |
| AC-11 | A bypass without a different approver, or with an overdue post-review, is FAIL. | test_ac11 |
| AC-12 | Malformed input exits with code 2 and names the problem. | test_ac12 |
| AC-13 | The sample set has an expected result per record (`data/expected.json`) and the checker matches all of them. | test_ac13 |
| AC-14 | Sampled verification: `verify_sample.py` draws N records with a fixed seed and prints, per rule, the source field values used, so a reviewer can compare to the raw record. | test_ac14 |

## Verification method

1. Run the test suite: all tests pass.
2. Run `python verify_sample.py --n 5 --seed 7`. For each sampled record, a reviewer opens `data/changes.json`, finds the record by id and confirms the printed field values match.
3. Any mismatch is a defect in the checker, not in the data.
