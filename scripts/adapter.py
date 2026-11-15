#!/usr/bin/env python3
"""Optional TypeSafe HTTP adapter. Offline by default; Python 3.11+ standard library.

This adapter has one closed synthetic policy bundle. The Lean kernel rechecks
normalized integer gates. Nothing in a neural response can set reviewedFact.
"""
import argparse
from decimal import Decimal, InvalidOperation, ROUND_FLOOR
import json
import os
from pathlib import Path
import sys
import urllib.error
import urllib.request

MODEL = "jev-1.14.0"
LINE = "TX42 was charged twice; the duplicate amount is USD 25.00."
CHOICES = ("refund", "review", "none")


def request_body():
    return {
        "model": MODEL,
        "state": {"source_id": "synthetic-ledger-TX42-v1", "text": LINE,
                  "policy": "A reviewed duplicate charge of USD 25 is eligible for a refund recommendation."},
        "questions": {
            "action": {"type": "choice", "instructions": "Which recommendation fits this synthetic record?",
                       "criteria": {"refund": "A duplicate charge eligible under the supplied policy",
                                    "review": "Human review is required", "none": "None of these fits"}},
            "support": {"type": "noul", "instructions": "Does the text explicitly state there was a duplicate charge?"},
            "risk": {"type": "score", "instructions": "How much does this record conflict with the policy?",
                     "criteria": ["No conflict is evident", "Some ambiguity", "Clear conflict"]},
        },
    }


def unique_object(pairs):
    out = {}
    for key, value in pairs:
        if key in out:
            raise ValueError(f"duplicate JSON key: {key}")
        out[key] = value
    return out


def loads(raw):
    return json.loads(raw, parse_float=Decimal, parse_int=Decimal,
                      parse_constant=lambda x: (_ for _ in ()).throw(ValueError(f"invalid number: {x}")),
                      object_pairs_hook=unique_object)


def probability(value):
    if isinstance(value, bool) or not isinstance(value, (Decimal, int)):
        raise ValueError("probability must be a JSON number")
    number = Decimal(value)
    if not number.is_finite() or not 0 <= number <= 1:
        raise ValueError("probability outside [0,1]")
    return number


def distribution(value, keys):
    if not isinstance(value, dict) or set(value) != set(keys):
        raise ValueError("unexpected probability options")
    values = {k: probability(value[k]) for k in keys}
    total = sum(values.values())
    if abs(total - 1) > Decimal("0.000001"):
        raise ValueError("probability mass does not sum to 1 within tolerance")
    return {k: v / total for k, v in values.items()}


def floor_bps(value):
    return int((value * 10000).to_integral_value(rounding=ROUND_FLOOR))


def normalize(response):
    if not isinstance(response, dict):
        raise ValueError("response must be a JSON object")
    if response.get("model") != MODEL:
        raise ValueError("response must name the pinned model version")
    answers = response.get("answers")
    if not isinstance(answers, dict) or set(answers) != {"action", "support", "risk"}:
        raise ValueError("unexpected or missing question ids")
    action, support, risk = (answers[k] for k in ("action", "support", "risk"))
    if not all(isinstance(answer, dict) for answer in (action, support, risk)):
        raise ValueError("each answer must be a JSON object")
    if action.get("type") != "choice" or support.get("type") != "noul" or risk.get("type") != "score":
        raise ValueError("answer/question type mismatch")
    choices = distribution(action.get("probabilities"), CHOICES)
    choice = action.get("choice")
    if choice not in CHOICES or choices[choice] != max(choices.values()):
        raise ValueError("selected choice is not a highest-probability declared option")
    probability(action.get("confidence"))  # Validate type/range; not independent evidence.
    probability(risk.get("confidence"))
    risk_probs = distribution(risk.get("probabilities"), ("0", "1", "2"))
    expected = risk_probs["1"] + 2 * risk_probs["2"]
    supplied_score = risk.get("score")
    if isinstance(supplied_score, bool) or not isinstance(supplied_score, (Decimal, int)):
        raise ValueError("score must be a JSON number")
    if not Decimal(supplied_score).is_finite() or abs(Decimal(supplied_score) - expected) > Decimal("0.00001"):
        raise ValueError("score disagrees with probability-weighted rubric")
    expected_legend = {str(i): description for i, description in enumerate(
        request_body()["questions"]["risk"]["criteria"])}
    if risk.get("legend") != expected_legend:
        raise ValueError("rubric legend differs from the code-owned request")
    refund, review = floor_bps(choices["refund"]), floor_bps(choices["review"])
    risk0, risk1 = floor_bps(risk_probs["0"]), floor_bps(risk_probs["1"])
    # Allocate quantization remainder to abstention and highest risk.
    return {"model": MODEL, "policyId": "synthetic-refund-v1",
            "sourceId": "synthetic-ledger-TX42-v1", "quote": LINE,
            "factId": "duplicate-charge-25-reviewed", "choice": choice,
            "refundBps": refund, "reviewBps": review, "noneBps": 10000 - refund - review,
            "supportNoulBps": floor_bps(probability(support.get("noul"))),
            "risk0Bps": risk0, "risk1Bps": risk1, "risk2Bps": 10000 - risk0 - risk1}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--request", action="store_true", help="print request; no network")
    group.add_argument("--response", type=Path, help="normalize a saved response; no network")
    group.add_argument("--live", action="store_true", help="explicitly call TypeSafe; billable")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        if args.request:
            result = request_body()
        elif args.response:
            result = normalize(loads(args.response.read_text()))
        else:
            key = os.environ.get("TYPESAFE_API_KEY")
            if not key:
                raise ValueError("TYPESAFE_API_KEY is required for --live")
            request = urllib.request.Request("https://api.typesafe.ai/v1/systemone",
                data=json.dumps(request_body()).encode(),
                headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"}, method="POST")
            with urllib.request.urlopen(request, timeout=30) as response:
                result = normalize(loads(response.read().decode()))
        raw = json.dumps(result, indent=2) + "\n"
        if args.output:
            args.output.write_text(raw)
        else:
            sys.stdout.write(raw)
        return 0
    except (ValueError, TypeError, KeyError, InvalidOperation, OSError, urllib.error.URLError) as error:
        print(f"Adapter rejected input: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
