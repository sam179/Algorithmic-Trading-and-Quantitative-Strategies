import unittest
from NormalizeReturns import NormalizeReturns

class TestNormalizeReturns(unittest.TestCase):
    def test_get_returns(self):
        normalize_returns = NormalizeReturns()
        returns = normalize_returns.get_returns(start_date='20070620', end_date='20070621')

        self.assertEqual(returns.shape, (78, 499))
        self.assertAlmostEqual(returns['JAVA'][0], 0.035729954, places=6)


if __name__ == "__main__":
    unittest.main()