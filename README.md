# Lean Jev Bridge

A runnable research prototype for placing a deterministic Lean decision kernel after TypeSafe AI's probabilistic Jev model. It demonstrates a typed proposal, conservative numeric normalization, reviewed evidence, an effective-date policy, and explicit acceptance, review, or invalid results.

**Status: synthetic prototype, November 15, 2026.** This repository contains no trained neural model, Jev weights, real customer records, measured Jev outputs, medical adjudicator, or permitting authority. The single executable policy is a reviewed fictional duplicate-charge example. The other Matha Labs research repos explore the healthcare and permitting domains.

The question motivating this work is useful: can a Jev-shaped interface produce deterministic business decisions through Lean? Yes, given fixed structured facts, policy, and model response. A repeat model call can still change the response. Checking a source quote is not proof that its semantic interpretation is correct.

## Run offline

Install Lean through [the official instructions](https://lean-lang.org/install/). The `lean-toolchain` file pins Lean 4.35.0. There are no third-party Lean dependencies. Python 3.11+ uses only its standard library.

```sh
lake build
lake exe bridge
python3 scripts/adapter.py --response fixtures/synthetic-response.json --output /tmp/bridge-packet.json
lake exe bridge /tmp/bridge-packet.json
python3 -m unittest discover -s scripts -p 'test_*.py'
python3 scripts/check_proofs.py
```

The packet replay prints `{"decision":"accepted",...}` for the accepted fixture. Alter the quote or lower the success probability and it prints `review`. Invalid model versions, probability totals, and unsupported choices produce `invalid` with exit code 2. Missing or malformed JSON fields also exit 2.

Every fixture response is manually authored. No API calls are needed to build, test, or run CI.

## Optional real TypeSafe request

Preview the request without network access:

```sh
python3 scripts/adapter.py --request
```

An explicit `--live` call uses the official endpoint and can incur API charges. It reads `TYPESAFE_API_KEY` from the environment. Do not put credentials in source files or command arguments. This operation is provided for later evaluation; it was not used to produce this research release.

```sh
python3 scripts/adapter.py --live --output /tmp/bridge-live-packet.json
lake exe bridge /tmp/bridge-live-packet.json
```

## What the core proves

`Bridge/Kernel.lean` has these 12 named theorems:

- `accepted_iff`
- `accepted_requires_reviewed_fact`
- `accepted_requires_certificate`
- `accepted_requires_pinned_model`
- `accepted_requires_current_policy`
- `accepted_requires_choice_threshold`
- `accepted_requires_noul_threshold`
- `accepted_requires_risk_bound`
- `no_probability_can_bypass_false_fact`
- `no_probability_can_bypass_bad_certificate`
- `unrecognized_model_is_invalid`
- `replay_is_deterministic`

The certificate requirement includes exact source-quote equality. The replay theorem states that equal policy and packet inputs imply equal outputs; it makes no claim that repeated neural calls produce equal packets. `Bridge/Tests.lean` contains 24 kernel-checked regression examples. There are 18 Python adapter and end-to-end tests.

The risk rubric has levels 0, 1, and 2. The kernel recomputes the risk numerator from integer probability mass and allows at most 500/10000 = 0.05. Choice success and Noul support each require at least 9800/10000 = 0.98. These are illustrative policy constants, not calibrated operating thresholds for any real domain. The adapter assigns rounding remainder to abstention and highest risk. It treats Choice/Score confidence as metadata, not extra independent evidence.

Lean proves consistency with the encoded rules and reviewed-fact inputs. The external semantic review that made a fact eligible, source authenticity, translation correctness, completeness of policy coverage, and model calibration remain outside those theorems. The fixed local policy bundle deliberately cannot be modified by the model response.

## Documentation

- [Whitepaper](docs/whitepaper.md): model research, architecture, relation to Lexifina, trust boundaries, and next steps.
- [Sources](docs/sources.md): first-party references checked November 15, 2026.
- [Evaluation](docs/evaluation.md): exact tests and scope.

This is independent Matha Labs work. Jev and TypeSafe AI are referenced for interoperability and research; no affiliation or endorsement is implied.

## Publication

Read the [Matha Labs research article](https://www.mathalabs.com/blog/jev-meets-lean/), [download the whitepaper PDF](docs/whitepaper.pdf), or inspect its [editable source](docs/whitepaper.md). The published evaluation uses synthetic fixtures only.
