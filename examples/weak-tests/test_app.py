import unittest
from unittest.mock import patch

from app import apply_discount, transfer


class DiscountTests(unittest.TestCase):
    def test_returns_a_number(self):
        result = apply_discount(100, 10)
        self.assertIsInstance(result, (int, float))

    def test_does_not_crash_on_valid_input(self):
        apply_discount(100, 10)

    @unittest.skip("boundaries later")
    def test_rejects_over_100_percent(self):
        with self.assertRaises(ValueError):
            apply_discount(100, 101)


class TransferTests(unittest.TestCase):
    @patch("app._check_balance", return_value=True)
    def test_successful_transfer(self, _check_balance):
        self.assertEqual(transfer(100, 10), 90)

    def test_rejects_negative_amount(self):
        with self.assertRaises(ValueError):
            transfer(100, -1)


if __name__ == "__main__":
    unittest.main()
