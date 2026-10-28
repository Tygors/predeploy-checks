import unittest

from app import apply_discount, fee, transfer


class DiscountTests(unittest.TestCase):
    def test_rejects_over_100(self):
        with self.assertRaises(ValueError):
            apply_discount(100, 101)

    def test_discount(self):
        self.assertEqual(apply_discount(100, 10), 90.0)


class TransferTests(unittest.TestCase):
    def test_transfer(self):
        self.assertEqual(transfer(100, 10), 90)


class FeeTests(unittest.TestCase):
    def test_fee(self):
        self.assertEqual(fee(100), 3.0)


if __name__ == "__main__":
    unittest.main()
