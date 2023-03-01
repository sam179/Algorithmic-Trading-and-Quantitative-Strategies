import pandas as pd
import unittest
import pandas as pd
from unittest.mock import MagicMock

# Import the class to be tested
from TAQCAPM import TAQCAPM


class Test_TAQCAPM(unittest.TestCase):
    
    def setUp(self):
        # Create a sample dataframe for testing
        self.test_df = pd.DataFrame({
            "Names Date": [20210101, 20210101, 20210102, 20210102],
            "Trading Symbol": ["AAPL", "GOOG", "AAPL", "GOOG"],
            "Price or Bid/Ask Average": [100.0, 200.0, 105.0, 190.0],
            "Shares Outstanding": [1000000, 500000, 2000000, 1000000]
        })
        # Create an instance of the class to be tested using stub data
        self.taq_capm = TAQCAPM(filename=None)
        self.taq_capm._snp = self.test_df
    
    def test_getWeights(self):
        # Test the getWeights method for a valid date
        expected_output = pd.DataFrame({
            "Names Date": [20210101, 20210101],
            "Trading Symbol": ["AAPL", "GOOG"],
            "Price or Bid/Ask Average": [100.0, 200.0],
            "Shares Outstanding": [1000000, 500000],
            "Market Cap": [100000000.0, 100000000.0],
            "weight": [0.5, 0.5]
        })
        output = self.taq_capm.getWeights(20210101)
        pd.testing.assert_frame_equal(output, expected_output)
    
    def test_turnOver(self):
        # Set up stub data for the getWeights method
        self.taq_capm.getWeights = MagicMock()
        self.taq_capm.getWeights.side_effect = [
            pd.DataFrame({
                "Trading Symbol": ["AAPL", "GOOG"],
                "weight": [0.5, 0.5]
            }),
            pd.DataFrame({
                "Trading Symbol": ["AAPL", "GOOG"],
                "weight": [0.6, 0.4]
            })
        ]
        
        # Test the turnOver method
        output = self.taq_capm.turnOver(20210101, 20210102)
        self.assertAlmostEqual(output, 0.2)

        
if __name__ == "__main__":
    unittest.main()
