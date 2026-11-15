# Primary sources

Reviewed November 15, 2026. Model behavior and interface details can change; the adapter requests the versioned ID `jev-1.14.0` and rejects aliases in returned records.

1. TypeSafe AI, [Introducing System One Models & Jev](https://typesafe.ai/blog/introducing-system-one-models-and-jev), September 15, 2026. Public disclosure of parallel structured outputs and RLCD; this is vendor reporting, not an independently reproduced training method.
2. TypeSafe AI, [Introduction](https://docs.typesafe.ai/introduction). Atomic independent questions over common state, typed decision interface.
3. TypeSafe AI, [System One](https://docs.typesafe.ai/concepts/system-one). Calibration is a group property, not a correctness guarantee for one case.
4. TypeSafe AI, [AI primer](https://docs.typesafe.ai/introduction/machine-learning-primer). The vendor's conceptual post-training account.
5. TypeSafe AI, [Confidence](https://docs.typesafe.ai/confidence). Distribution concentration differs from probability of correctness; no independent evidence from a redundant threshold.
6. TypeSafe AI, [Models](https://docs.typesafe.ai/models). Versioned model names, aliases, supported primitives, and account-independent weights.
7. TypeSafe AI, [System One HTTP API](https://docs.typesafe.ai/api/system-one). Request and response schema, endpoint, Choice and Score distributions, Noul scalar.
8. TypeSafe AI, [Noul](https://docs.typesafe.ai/primitives/noul). Probability of a yes answer; no separate confidence field.
9. TypeSafe AI, [Score](https://docs.typesafe.ai/primitives/score). Ordered rubric and probability-weighted expected score.
10. TypeSafe AI, [Pre-parsed value extraction](https://docs.typesafe.ai/cookbooks/pre_parsed_value_extraction_cookbook). Selecting from code-owned source spans rather than generating new values.
11. TypeSafe AI, [Self-consistency: choices](https://docs.typesafe.ai/cookbooks/consistency_choice_cookbook). Vendor repeatability experiment showing remaining variation, distinct from accuracy.
12. Lexifina, [Formalizing all US case law in Lean](https://lexifina.com/blog/formalizing-all-us-case-law-in-lean), November 13, 2026. Inspiration for the evidence-certificate and rule-authority boundary. This repository does not reproduce its reported corpus or measurements.
13. Lean, [Theorem proving in Lean 4](https://lean-lang.org/theorem_proving_in_lean4/). The role of propositions, proofs, and trusted assumptions.

No exact parameter count, layer layout, pretrained base, complete RLCD loss, training corpus, or released Jev weights was established by these public sources. The bridge does not claim to reproduce Jev's training or inference engine.
