# Evaluation scope

All inputs are synthetic. The published release performs no model calls and makes no clinical, legal, financial, throughput, cost, or calibration benchmark claim.

## Lean

`lake build` compiles 12 named theorems in `Bridge/Kernel.lean` and 24 examples in `Bridge/Tests.lean`. The examples cover:

- An accepted reviewed record; rejection of a false reviewed fact despite maximal neural confidence.
- Wrong source quote, source identifier, reviewed fact identifier, and policy identifier.
- Policy date before and after its valid interval.
- Choice and Noul thresholds on each side of the boundary.
- Score risk bound on each side of the boundary.
- Bad Choice mass, bad risk mass, and out-of-range Noul.
- Explicit abstention, review, unknown action, moving alias, and wrong pinned model.
- Empty evidence.

`scripts/check_proofs.py` rejects proof holes and explicit axioms in project Lean source. Its text scan supplements compilation; it does not establish that formal statements express all intended real-world requirements.

## Python adapter and executable boundary

`python3 -m unittest discover -s scripts -p 'test_*.py'` runs 18 tests. They exercise accepted offline replay, low-probability review, forged quote review, invalid distribution rejected by Lean, invalid probability range, wrong model, unknown option, wrong primitive, bad mass, duplicate keys, NaN, boolean-as-number rejection, inconsistent Score, conservative quantization, and versioned request construction.

The adapter consumes the public TypeSafe response shape, validates question and option keys, checks the selected Choice against its distribution, and recomputes the Score expectation. It normalizes probability totals only within 0.000001 of 1. Rounding sends remainder toward abstention or risk. The executable evaluates normalized integer JSON against its fixed local reviewed policy bundle.

## Evidence limits

The fixtures do not establish Jev accuracy, robustness to prompt injection, or real domain usefulness. Passing tests establish the stated behavior for these examples and kernel proofs establish their quantified formal statements. Policy/source authenticity, semantic fact review, and any future adapter implementation require their own validation. The current source quote check is exact equality with a bundled line; it is not an entailment checker over arbitrary prose.
