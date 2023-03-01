from unittest import TestCase
import unittest
import pandas as pd
from TAQCleaner import *

import TAQStats

class Test_TAQStats(TestCase):

    def test_x_minute_stats(self):

        stocks = ["SUNW", "ADP"]
        X = 10

        """
        Testing the simple case where we are calculating 10-minute returns for
        a given sample of stocks
        """
        trading_data, quote_data = TAQStats.x_minute_stats(X = X, stocks = stocks)
        trading_tickers = trading_data["Ticker"].unique()
        quote_tickers = quote_data["Ticker"].unique()

        # Testing the timestamp duration to be less than or equal to X minutes for trades
        trading_timestamp = trading_data["MillisFromMidn"]
        self.assertLessEqual(trading_timestamp.iloc[1] - trading_timestamp.iloc[0], X * 60000)

        # Testing the timestamp duration to be less than or equal to X minutes for quotes
        quote_timestamp = quote_data["MillisFromMidn"]
        self.assertLessEqual(quote_timestamp.iloc[1] - quote_timestamp.iloc[0], X * 60000)

        # Checking the size of the stock list returned in both datasets
        self.assertEqual(len(stocks), len(trading_tickers.index))
        self.assertEqual(len(stocks), len(quote_tickers.index))

        testing_set = trading_data.iloc[1]

        self.assertEqual(testing_set[0], "SUNW")
        self.assertEqual(str(testing_set[1]), "20070621")
        self.assertEqual(str(testing_set[2]), "0")
        self.assertEqual(str(testing_set[3]), "34200000")
        self.assertEqual(str(testing_set[4]), "305535")
        self.assertEqual(str(testing_set[5]), "5.07")
        self.assertEqual(str(testing_set[6]), "-0.01362")

    def test_stock_stats(self):
        stocks = ["SUNW", "ADP"]
        X = 300

        """
        Testing the simple case where we are calculating 10-minute returns for
        a given sample of stocks
        """
        data = TAQStats.stock_stats(X=X, stocks=stocks)

        test_data = data.iloc[0]

        self.assertEqual(test_data[0], "SUNW")
        self.assertEqual(str(test_data[1]), "20070620")
        self.assertEqual(str(test_data[2]), "1")
        self.assertEqual(str(test_data[3]), "25645")
        self.assertEqual(str(test_data[4]), "35006")
        self.assertEqual(str(test_data[5]), "-1.00863")
        self.assertEqual(str(test_data[6]), "-0.863352")
        self.assertEqual(str(test_data[7]), "0.732589")
        self.assertEqual(str(test_data[8]), "-1.00863")
        self.assertEqual(str(test_data[9]), "-0.863352")
        self.assertEqual(str(test_data[10]), "0.70749")
        self.assertEqual(str(test_data[11]), "0.608328")
        self.assertEqual(str(test_data[12]), "0.70749")
        self.assertEqual(str(test_data[13]), "0.608328")
        self.assertEqual(str(test_data[14]), "0.0")
        self.assertEqual(str(test_data[15]), "0.0")
        self.assertEqual(str(test_data[16]), "-2.0")
        self.assertEqual(str(test_data[17]), "-2.0")


    def test_basic_daily_stats(self):

        TAQStats.basic_daily_stats()

        filename = MyDirectories.getTAQDir() / "Files/basic_daily_stats_Full_20070620_20070921.csv"
        stats_table = pd.read_csv(filename)

        test_data = stats_table.iloc[0]

        self.assertEqual(test_data[1], "SUNW")
        self.assertEqual(str(test_data[2]), "2304483")
        self.assertEqual(str(test_data[3]), "4138394")
        self.assertEqual(str(test_data[4]), "-0.098893")
        self.assertEqual(str(test_data[5]), "-0.089395")
        self.assertEqual(str(test_data[6]), "0.556854")
        self.assertEqual(str(test_data[7]), "0.0")
        self.assertEqual(str(test_data[8]), "0.0")
        self.assertEqual(str(test_data[9]), "5.003718")
        self.assertEqual(str(test_data[10]), "5.094801")
        self.assertEqual(str(test_data[11]), "2.03112")
        self.assertEqual(str(test_data[12]), "2.03364")
        self.assertEqual(str(test_data[13]), "0.788423")
        self.assertEqual(str(test_data[14]), "0.768249")
        self.assertEqual(str(test_data[15]), "6.10916")
        self.assertEqual(str(test_data[16]), "5.920463")



if __name__ == "__main__":
    unittest.main()
