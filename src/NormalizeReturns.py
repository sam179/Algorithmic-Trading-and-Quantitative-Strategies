import numpy as np
import pandas as pd
from TAQQuotesReader import TAQQuotesReader
from TAQTradesReader import TAQTradesReader
import MyDirectories
from FileManager import FileManager
from ReturnBuckets import ReturnBuckets
import os


class NormalizeReturns(object):

    def cross_sectional_normalization(self, return_buckets, num_buckets):

        n = len(return_buckets)
        returns = np.empty((0, num_buckets))

        for bucket in return_buckets:
            asset_returns = np.array([[]])
            n = bucket.getN()

            for i in range(n):
                asset_returns = np.append(asset_returns, bucket.getReturn(i))

            demeaned_returns = asset_returns - np.mean(asset_returns)
            returns = np.append(returns, demeaned_returns.reshape(1, n), axis=0)

        returns_t = returns.T

        for i in range(len(returns_t)):
            row_norm = np.sqrt(returns_t[i].T @ returns_t[i])
            returns_t[i] = returns_t[i] / row_norm

        return returns_t

    def get_returns(self, start_date='20070620', end_date='20070919'):
        baseDir = MyDirectories.getTAQDir()
        fm = FileManager(baseDir)
        quote_dates = sorted(fm.getQuoteDates(start_date, end_date))
        spx_data = pd.read_excel(os.getcwd() + '/data_orig/s&p500.xlsx', sheet_name=['WRDS'])
        spx_tickers = spx_data['WRDS']['Ticker Symbol']
        spx_tickers = spx_tickers.unique()
        spx_tickers = self.filter_stocks(spx_tickers)
        print(len(spx_tickers))
        startTS = 18 * 60 * 60 * 1000 / 2  # 930AM
        endTS = 16 * 60 * 60 * 1000  # 4PM
        numBuckets = 78

        returns = np.empty((0, len(spx_tickers)))

        for date in quote_dates:

            intraday_returns = np.array([])
            for ticker in spx_tickers:

                try:
                    quote_reader = TAQQuotesReader(
                        str(MyDirectories.getQuotesDir()) + '/' + date + '/' + ticker + '_quotes.binRQ')
                except:
                    continue
                print('Retrieved data for ', ticker, ' for date', date)
                returnBuckets = ReturnBuckets(quote_reader, startTS, endTS, numBuckets)
                intraday_returns = np.append(intraday_returns, returnBuckets)

            normalized_returns = self.cross_sectional_normalization(intraday_returns, numBuckets)

            returns = np.append(returns, normalized_returns, axis=0)
            # print(normalized_returns.shape)
            # print(normalized_returns)
        # print(returns.shape)
        # print(returns)
        returns_data = pd.DataFrame(returns, columns=spx_tickers)
        filepath = str(MyDirectories.getTAQDir()) + "/normalized_returns.csv"
        returns_data.to_csv(filepath)

        return returns_data

    def filter_stocks(self, spx_tickers, start_date='20070620', end_date='20070921'):

        baseDir = MyDirectories.getTAQDir()
        fm = FileManager(baseDir)
        quote_dates = sorted(fm.getQuoteDates(start_date, end_date))
        good_tickers = []

        for ticker in spx_tickers:

            ticker_count = 0
            for date in quote_dates:

                try:
                    quote_reader = TAQQuotesReader(
                        str(MyDirectories.getQuotesDir()) + '/' + date + '/' + ticker + '_quotes.binRQ')

                except:
                    continue
                ticker_count += 1
                # if quote_reader.getN() > 0:
                #     ticker_count += 1
            if ticker_count == 63:
                good_tickers.append(ticker)

        return good_tickers
        # print(normalized_returns.shape)
        # print(normalized_returns)


if __name__ == "__main__":
    returns = pd.read_csv(os.getcwd() + '/data_orig/quoteReturns.csv')
    norm = NormalizeReturns()
    # data = norm.cross_sectional_normalization(returns)
    data = norm.get_returns()
