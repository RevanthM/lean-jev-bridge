import copy
from decimal import Decimal
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

from adapter import loads, normalize, request_body

ROOT = Path(__file__).resolve().parents[1]


class AdapterTests(unittest.TestCase):
    def setUp(self):
        self.response = loads((ROOT / "fixtures/synthetic-response.json").read_text())

    def replay(self, packet):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "packet.json"
            path.write_text(json.dumps(packet))
            process = subprocess.run([str(ROOT / ".lake/build/bin/bridge"), str(path)],
                                     capture_output=True, text=True)
            return process.returncode, json.loads(process.stdout)["decision"]

    def test_offline_bridge_accepts(self):
        packet = normalize(self.response)
        process = subprocess.run([str(ROOT / ".lake/build/bin/bridge"), str(ROOT / "fixtures/normalized-packet.json")],
                                 capture_output=True, text=True, check=True)
        self.assertEqual(json.loads(process.stdout)["decision"], "accepted")
        self.assertEqual(packet, json.loads((ROOT / "fixtures/normalized-packet.json").read_text()))

    def test_low_probability_routes_to_review(self):
        self.response["answers"]["action"]["probabilities"] = {
            "refund": Decimal("0.97"), "review": Decimal("0.02"), "none": Decimal("0.01")}
        self.assertEqual(normalize(self.response)["refundBps"], 9700)
        self.assertEqual(self.replay(normalize(self.response)), (0, "review"))

    def test_wrong_source_quote_routes_to_review(self):
        packet = normalize(self.response)
        packet["quote"] = "Fabricated sentence."
        self.assertEqual(self.replay(packet), (0, "review"))

    def test_invalid_normalized_distribution_rejected_by_lean(self):
        packet = normalize(self.response)
        packet["refundBps"] = 10001
        self.assertEqual(self.replay(packet), (2, "invalid"))

    def test_probability_overshoot_rejected(self):
        self.response["answers"]["support"]["noul"] = Decimal("1.1")
        with self.assertRaises(ValueError):
            normalize(self.response)

    def test_wrong_model_rejected(self):
        self.response["model"] = "jev-latest"
        with self.assertRaises(ValueError):
            normalize(self.response)

    def test_unrecognized_option_rejected(self):
        self.response["answers"]["action"]["choice"] = "send-money"
        with self.assertRaises(ValueError):
            normalize(self.response)

    def test_wrong_question_type_rejected(self):
        self.response["answers"]["support"]["type"] = "choice"
        with self.assertRaises(ValueError):
            normalize(self.response)

    def test_reversed_rubric_rejected(self):
        self.response["answers"]["risk"]["legend"] = {
            "0": "Clear conflict", "1": "Some ambiguity", "2": "No conflict is evident"}
        with self.assertRaises(ValueError):
            normalize(self.response)

    def test_non_object_response_rejected(self):
        with self.assertRaises(ValueError):
            normalize([])

    def test_non_object_answer_rejected(self):
        self.response["answers"]["action"] = None
        with self.assertRaises(ValueError):
            normalize(self.response)

    def test_mass_error_rejected(self):
        self.response["answers"]["action"]["probabilities"]["refund"] = Decimal("0.9")
        with self.assertRaises(ValueError):
            normalize(self.response)

    def test_duplicate_keys_rejected(self):
        with self.assertRaises(ValueError):
            loads('{"model":"a","model":"b"}')

    def test_nan_rejected(self):
        with self.assertRaises(ValueError):
            loads('{"probability":NaN}')

    def test_boolean_is_not_probability(self):
        self.response["answers"]["support"]["noul"] = True
        with self.assertRaises(ValueError):
            normalize(self.response)

    def test_score_must_match_distribution(self):
        self.response["answers"]["risk"]["score"] = Decimal("1.5")
        with self.assertRaises(ValueError):
            normalize(self.response)

    def test_conservative_quantization(self):
        self.response["answers"]["action"]["probabilities"] = {
            "refund": Decimal("0.980099"), "review": Decimal("0.019899"), "none": Decimal("0.000002")}
        packet = normalize(self.response)
        self.assertEqual(packet["refundBps"], 9800)
        self.assertEqual(packet["noneBps"], 2)

    def test_request_is_versioned_and_three_typed_questions(self):
        request = request_body()
        self.assertEqual(request["model"], "jev-1.14.0")
        self.assertEqual({q["type"] for q in request["questions"].values()}, {"choice", "score", "noul"})


if __name__ == "__main__":
    unittest.main()
