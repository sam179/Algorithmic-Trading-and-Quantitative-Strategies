from unittest import TestCase
import unittest
import pandas as pd
from TAQCleaner import *
import numpy as np
import scipy.stats as scp
import MyDirectories
from FileManager import FileManager
from TAQQuotesReader import TAQQuotesReader
from TAQTradesReader import TAQTradesReader
import matplotlib.pyplot as plt
from pathlib import Path
import warnings
import MyDirectories
from TAQQuotesReader import TAQQuotesReader
from TAQTradesReader import TAQTradesReader
import TAQStats

class Test_TAQStats(unittest.TestCase):

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
        self.assertLessEqual(trading_timestamp[1] - trading_timestamp[0], X * 60000)

        # Testing the timestamp duration to be less than or equal to X minutes for quotes
        quote_timestamp = quote_data["MillisFromMidn"]
        self.assertLessEqual(quote_timestamp[1] - quote_timestamp[0], X * 60000)

        # Checking the size of the stock list returned in both datasets
        self.assertEqual(len(stocks), len(trading_tickers.index))
        self.assertEqual(len(stocks), len(quote_tickers.index))

        stocks = None
        X = 10
        """
            Testing the simple case where we are calculating 10-minute returns for 
            when no stocks are passed, so we take the full S&P500 list and run
        """
        spx_data = pd.read_excel('s&p500.xlsx', sheet_name=['WRDS'])
        spx_tickers = spx_data['WRDS']['Ticker Symbol']
        spx_tickers = spx_tickers.unique()
        stocks = spx_tickers

        trading_data, quote_data = TAQStats.x_minute_stats(X=X, stocks=stocks)
        trading_tickers = trading_data["Ticker"].unique()
        quote_tickers = quote_data["Ticker"].unique()

        # Testing the timestamp duration to be less than or equal to X minutes for trades
        trading_timestamp = trading_data["MillisFromMidn"]
        self.assertLessEqual(trading_timestamp[1] - trading_timestamp[0], X * 60000)

        # Testing the timestamp duration to be less than or equal to X minutes for quotes
        quote_timestamp = quote_data["MillisFromMidn"]
        self.assertLessEqual(quote_timestamp[1] - quote_timestamp[0], X * 60000)

        # Checking the size of the stock list returned in both datasets
        self.assertEqual(len(stocks), len(trading_tickers.index))
        self.assertEqual(len(stocks), len(quote_tickers.index))


        stocks = ["SUNW"]
        X = None
        """
            Testing the simple case where we are calculating daily returns
            for only one stock.
        """
        spx_data = pd.read_excel('s&p500.xlsx', sheet_name=['WRDS'])
        spx_tickers = spx_data['WRDS']['Ticker Symbol']
        spx_tickers = spx_tickers.unique()
        stocks = spx_tickers

        trading_data, quote_data = TAQStats.x_minute_stats(X=X, stocks=stocks)
        trading_tickers = trading_data["Ticker"].unique()
        quote_tickers = quote_data["Ticker"].unique()

        # Testing the timestamp duration to be less than or equal to X minutes for trades
        trading_timestamp = trading_data["MillisFromMidn"]
        self.assertLessEqual(trading_timestamp[0], )

        # Testing the timestamp duration to be less than or equal to X minutes for quotes
        quote_timestamp = quote_data["MillisFromMidn"]
        self.assertLessEqual(quote_timestamp[1] - quote_timestamp[0], X * 60000)

        # Checking the size of the stock list returned in both datasets
        self.assertEqual(len(stocks), len(trading_tickers.index))
        self.assertEqual(len(stocks), len(quote_tickers.index))

    def test_stock_stats(self):
        stocks = ["SUNW", "ADP"]
        X = 10
        """
        Testing the simple case where we are calculating 10-minute returns for 
        a given sample of stocks
        """
        trading_data, quote_data = TAQStats.stock_stats(X=X, stocks=stocks)
        trading_tickers = trading_data["Ticker"].unique()
        quote_tickers = quote_data["Ticker"].unique()

        # Testing the timestamp duration to be less than or equal to X minutes for trades
        trading_timestamp = trading_data["MillisFromMidn"]
        self.assertLessEqual(trading_timestamp[1] - trading_timestamp[0], X * 60000)

        # Testing the timestamp duration to be less than or equal to X minutes for quotes
        quote_timestamp = quote_data["MillisFromMidn"]
        self.assertLessEqual(quote_timestamp[1] - quote_timestamp[0], X * 60000)

        # Checking the size of the stock list returned in both datasets
        self.assertEqual(len(stocks), len(trading_tickers.index))
        self.assertEqual(len(stocks), len(quote_tickers.index))

        stocks = None
        X = 10
        """
            Testing the simple case where we are calculating 10-minute returns for 
            when no stocks are passed, so we take the full S&P500 list and run
        """
        spx_data = pd.read_excel('s&p500.xlsx', sheet_name=['WRDS'])
        spx_tickers = spx_data['WRDS']['Ticker Symbol']
        spx_tickers = spx_tickers.unique()
        stocks = spx_tickers

        trading_data, quote_data = TAQStats.stock_stats(X=X, stocks=stocks)
        trading_tickers = trading_data["Ticker"].unique()
        quote_tickers = quote_data["Ticker"].unique()

        # Testing the timestamp duration to be less than or equal to X minutes for trades
        trading_timestamp = trading_data["MillisFromMidn"]
        self.assertLessEqual(trading_timestamp[1] - trading_timestamp[0], X * 60000)

        # Testing the timestamp duration to be less than or equal to X minutes for quotes
        quote_timestamp = quote_data["MillisFromMidn"]
        self.assertLessEqual(quote_timestamp[1] - quote_timestamp[0], X * 60000)

        # Checking the size of the stock list returned in both datasets
        self.assertEqual(len(stocks), len(trading_tickers.index))
        self.assertEqual(len(stocks), len(quote_tickers.index))

        stocks = ["SUNW"]
        X = None
        """
            Testing the simple case where we are calculating returns for all available ticks
            for only one stock.
        """
        spx_data = pd.read_excel('s&p500.xlsx', sheet_name=['WRDS'])
        spx_tickers = spx_data['WRDS']['Ticker Symbol']
        spx_tickers = spx_tickers.unique()
        stocks = spx_tickers

        trading_data, quote_data = TAQStats.stock_stats(X=X, stocks=stocks)
        trading_tickers = trading_data["Ticker"].unique()
        quote_tickers = quote_data["Ticker"].unique()

        # Testing the timestamp duration to be less than or equal to X minutes for trades
        trading_timestamp = trading_data["MillisFromMidn"]
        self.assertLessEqual(trading_timestamp[0], )

        # Testing the timestamp duration to be less than or equal to X minutes for quotes
        quote_timestamp = quote_data["MillisFromMidn"]
        self.assertLessEqual(quote_timestamp[1] - quote_timestamp[0], X * 60000)

        # Checking the size of the stock list returned in both datasets
        self.assertEqual(len(stocks), len(trading_tickers.index))
        self.assertEqual(len(stocks), len(quote_tickers.index))

if __name__ == "__main__":
    unittest.main()
