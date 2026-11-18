
import unittest

from experiments.evaluate_natural_language import evaluate_question


class TestNaturalLanguageEvaluation(unittest.TestCase):

    def setUp(self):

        self.correct_result = {
            "question_id": 2,
            "columns": ["customer_name"],
            "rows": [
                ["Aditya Verma"],
                ["Kabir Shah"],
                ["Omkar Pawar"]
            ],
            "final_answer": (
                "1. Aditya Verma\n"
                "2. Kabir Shah\n"
                "3. Omkar Pawar"
            )
        }

    def test_correct_answer(self):

        result = evaluate_question(self.correct_result)

        self.assertTrue(result["factual_accuracy"])
        self.assertTrue(result["completeness"])
        self.assertTrue(result["ordering"])
        self.assertTrue(result["clarity"])

    def test_incorrect_name(self):

        test_data = self.correct_result.copy()

        test_data["final_answer"] = (
            "1. Aditya Verma\n"
            "2. Kabir Shah\n"
            "3. Rahul Sharma"
        )

        result = evaluate_question(test_data)

        self.assertFalse(result["factual_accuracy"])
        self.assertFalse(result["completeness"])
        self.assertFalse(result["ordering"])

    def test_missing_record(self):

        test_data = self.correct_result.copy()

        test_data["final_answer"] = (
            "1. Aditya Verma\n"
            "2. Kabir Shah"
        )

        result = evaluate_question(test_data)

        self.assertTrue(result["factual_accuracy"])
        self.assertFalse(result["completeness"])
        self.assertFalse(result["ordering"])

    def test_incorrect_order(self):

        test_data = self.correct_result.copy()

        test_data["final_answer"] = (
            "1. Kabir Shah\n"
            "2. Aditya Verma\n"
            "3. Omkar Pawar"
        )

        result = evaluate_question(test_data)

        self.assertTrue(result["factual_accuracy"])
        self.assertTrue(result["completeness"])
        self.assertFalse(result["ordering"])

    def test_incorrect_formatting(self):
        test_data = self.correct_result.copy()

        test_data["final_answer"] = (
            "1. Aditya Verma\n"
            "3. Kabir Shah\n"
            "4. Omkar Pawar"
        )

        result = evaluate_question(test_data)

        self.assertTrue(result["factual_accuracy"])
        self.assertTrue(result["completeness"])
        self.assertTrue(result["ordering"])
        self.assertFalse(result["clarity"])

    def test_duplicate_record(self):
        test_data = self.correct_result.copy()

        test_data["final_answer"] = (
            "1. Aditya Verma\n"
            "2. Aditya Verma\n"
            "3. Omkar Pawar"
        )

        result = evaluate_question(test_data)

        self.assertTrue(result["factual_accuracy"])
        self.assertFalse(result["completeness"])
        self.assertFalse(result["ordering"])
        self.assertTrue(result["clarity"])

    def test_empty_answer(self):
        test_data = self.correct_result.copy()
        test_data["final_answer"] = ""

        result = evaluate_question(test_data)

        self.assertFalse(result["factual_accuracy"])
        self.assertFalse(result["completeness"])
        self.assertFalse(result["ordering"])
        self.assertFalse(result["clarity"])

    def test_incorrect_numeric_answer(self):
        test_data = {
            "question_id": 6,
            "columns": ["COUNT(*)"],
            "rows": [[5]],
            "final_answer": "7"
        }

        result = evaluate_question(test_data)

        self.assertFalse(result["factual_accuracy"])
        self.assertFalse(result["completeness"])
        self.assertFalse(result["ordering"])
        self.assertTrue(result["clarity"])


if __name__ == "__main__":
    unittest.main()
