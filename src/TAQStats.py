import pandas as pd
import numpy as np
import scipy.stats as scp
import os
import MyDirectories
from TAQCleaner import *
from FileManager import FileManager
from TAQQuotesReader import TAQQuotesReader
from TAQTradesReader import TAQTradesReader
import matplotlib.pyplot as plt
from pathlib import Path
import warnings
from TickTest import TickTest
import openpyxl
import BaseUtils

warnings.simplefilter('ignore')

start_date = "20070620"
end_date = "20070921"
time_increment = 60000

"""
x_minute_stats function takes as input five parameters:
--> X :  represents the x minute variable for which returns are computed. 
         In case, no values is passed the default behaviour of the function is to 
         iterate every single price in the TAQ dataset
--> stocks: represents the list of stock. In case, no value is passed, the default 
         behaviour is to get the list of stocks from S&P500 excel file in the directory. 
--> start_date_string: start date
--> end_date_string: end date
--> clean_data: indicates whether the data has been cleaned or not. 
------------------------------------------------------------------------------------------
The function lists out the returns in every x minute starting from the first tick of every 
day. This data is stored in relevant files. 

"""


def x_minute_stats(X=None, stocks=None, start_date_string=start_date, end_date_string=end_date, clean_data=0):
    baseDir = MyDirectories.getTAQDir()
    fm = FileManager(baseDir)
    tradefilepath = str(MyDirectories.getTAQDir()) + "/tradeReturns.csv"
    quotefilepath = str(MyDirectories.getTAQDir()) + "/quoteReturns.csv"
    start_date = start_date_string
    end_date = end_date_string
    trade_dates = sorted(fm.getTradeDates(start_date, end_date))
    quote_dates = sorted(fm.getQuoteDates(start_date, end_date))

    # Creating a tables for trading data
    trade_data_table = pd.DataFrame(columns=["Ticker", "Date", "N", "MillisFromMidn", "Size", "Price", "Returns"])

    spx_tickers = stocks

    # Fetching SPX tickers from the file
    if spx_tickers == None:
        spx_data = pd.read_excel(os.getcwd() + '/data_orig/s&p500.xlsx', sheet_name=['WRDS'])
        spx_tickers = spx_data['WRDS']['Ticker Symbol']
        spx_tickers = spx_tickers.unique()

    for ticker in spx_tickers:
        trade_data = pd.DataFrame(columns=["Ticker", "Date", "N", "MillisFromMidn", "Size", "Price"])
        for date in trade_dates:
            try:
                if (not clean_data):
                    trade_reader = TAQTradesReader(
                        str(MyDirectories.getTradesDir()) + '/' + date + '/' + ticker + '_trades.binRT')
                else:
                    trade_reader = TAQTradesReader(
                        str(MyDirectories.getTradesClDir()) + '/' + date + '/' + ticker + '_trades.binRT')
            except:
                continue

            N = trade_reader.getN()

            # Default behaviour in case no X is specified
            if X == None:
                for index in range(N):
                    # print('Data Entry ' + str(index) + ' of ' + str(N))
                    value = {"Ticker": ticker, "Date": date, "N": index,
                             "MillisFromMidn": trade_reader.getMillisFromMidn(index),
                             "Size": trade_reader.getSize(index), "Price": trade_reader.getPrice(index)}
                    trade_data = trade_data.append(value, ignore_index=True)
            else:
                init_time = trade_reader.getMillisFromMidn(0)
                current_time = init_time + X * time_increment
                value = {"Ticker": ticker, "Date": date, "N": 0, "MillisFromMidn": init_time,
                         "Size": trade_reader.getSize(0), "Price": trade_reader.getPrice(0)}
                trade_data = trade_data.append(value, ignore_index=True)

                for index in range(N):
                    if trade_reader.getMillisFromMidn(index) > current_time:
                        value = {"Ticker": ticker, "Date": date, "N": index - 1, "MillisFromMidn": current_time,
                                 "Size": trade_reader.getSize(index - 1), "Price": trade_reader.getPrice(index - 1)}
                        # print(value)
                        current_time = current_time + X * time_increment
                        # trade_data_table = pd.concat( [trade_data_table, value], ignore_index=True)
                        trade_data = trade_data.append(value, ignore_index=True)

        trade_data["Returns"] = trade_data["Price"].pct_change(1).round(decimals=5)
        trade_data_table = trade_data_table.append(trade_data)

    quote_data_table = pd.DataFrame(
        columns=["Ticker", "Date", "N", "MillisFromMidn", "AskSize", "AskPrice", "BidSize", "BidPrice", "MidQuote",
                 "Returns"])

    for ticker in spx_tickers:
        quote_data = pd.DataFrame(
            columns=["Ticker", "Date", "N", "MillisFromMidn", "AskSize", "AskPrice", "BidSize", "BidPrice", "MidQuote"])
        for date in quote_dates:
            try:
                if not clean_data:
                    quote_reader = TAQQuotesReader(
                        str(MyDirectories.getQuotesDir()) + '/' + date + '/' + ticker + '_quotes.binRQ')
                else:
                    quote_reader = TAQQuotesReader(
                        str(MyDirectories.getQuotesClDir()) + '/' + date + '/' + ticker + '_quotes.binRQ')
            except:
                continue

            N = quote_reader.getN()
            if X == None:
                for index in range(N):
                    # print('Data Entry ' + str(index) + ' of ' + str(N))
                    value = {"Ticker": ticker, "Date": date, "N": index,
                             "MillisFromMidn": quote_reader.getMillisFromMidn(index),
                             "AskSize": quote_reader.getAskSize(index), "AskPrice": quote_reader.getAskPrice(index),
                             "BidSize": quote_reader.getBidSize(index), "BidPrice": quote_reader.getBidPrice(index),
                             "MidQuote": (quote_reader.getAskPrice(index) + quote_reader.getBidPrice(index)) / 2}
                    quote_data = quote_data.append(value, ignore_index=True)
            else:
                init_time = quote_reader.getMillisFromMidn(0)
                current_time = init_time + X * time_increment
                value = {"Ticker": ticker, "Date": date, "N": 0, "MillisFromMidn": init_time,
                         "AskSize": quote_reader.getAskSize(0), "AskPrice": quote_reader.getAskPrice(0),
                         "BidSize": quote_reader.getBidSize(0), "BidPrice": quote_reader.getBidPrice(0),
                         "MidQuote": (quote_reader.getAskPrice(0) + quote_reader.getBidPrice(0)) / 2}
                quote_data = quote_data.append(value, ignore_index=True)

                for index in range(N):
                    if quote_reader.getMillisFromMidn(index) > current_time:
                        value = {"Ticker": ticker, "Date": date, "N": index - 1, "MillisFromMidn": current_time,
                                 "AskSize": quote_reader.getAskSize(index - 1),
                                 "AskPrice": quote_reader.getAskPrice(index - 1),
                                 "BidSize": quote_reader.getBidSize(index - 1),
                                 "BidPrice": quote_reader.getBidPrice(index - 1),
                                 "MidQuote": (quote_reader.getAskPrice(index - 1) + quote_reader.getBidPrice(
                                     index - 1)) / 2}
                        # print(value)
                        current_time = current_time + X * time_increment
                        # trade_data_table = pd.concat( [trade_data_table, value], ignore_index=True)
                        quote_data = quote_data.append(value, ignore_index=True)

        quote_data["Returns"] = quote_data["MidQuote"].pct_change(1).round(decimals=5)
        quote_data_table = quote_data_table.append(quote_data)

    trade_data_table.to_csv(tradefilepath)
    quote_data_table.to_csv(quotefilepath)
    #print(quote_data_table)

    return trade_data_table, quote_data_table


"""
stock_stats function takes in as arguments five parameters:
--> X: x minutes for which returns will be calculated by calling function  x_minute_stats
--> stocks: which represents the list of stocks for which calculation needs to be done
--> start_date_string: start date
--> end_date_string: end date
--> clean_data: indicates whether the data has been cleaned or not. 
---------------------------------------------------------------------------------------------------------
This function calculates basic stats for the given stocks. These stats are computed for a trading day and 
on the basis of X minute return calculations. These stats include means, standard deviations etc across 
various metrics.  
"""


def stock_stats(X=None, stocks=None, start_date_string=start_date, end_date_string=end_date, clean_data=0):
    baseDir = MyDirectories.getTAQDir()
    fm = FileManager(baseDir)
    trade_dates = sorted(fm.getTradeDates(start_date_string, end_date_string))
    quote_dates = sorted(fm.getQuoteDates(start_date_string, end_date_string))

    # The default duration for returns is to get daily returns
    if X == None:
        X = 600

    trade_data, quote_data = x_minute_stats(X, stocks, clean_data=clean_data)
    trade_data = trade_data.fillna(trade_data.mean())
    quote_data = quote_data.fillna(quote_data.mean())
    spx_tickers = stocks

    if spx_tickers == None:
        spx_data = pd.read_excel('/data_orig/s&p500.xlsx', sheet_name=['WRDS'])
        spx_tickers = spx_data['WRDS']['Ticker Symbol']
        spx_tickers = spx_tickers.unique()

    columns = ["Ticker", "Date", "Length(days)", "Total Trades", "Total Quotes", "Mean Returns(Trades)",
               "Mean Returns(Quotes)", "Trade Quote Ratio", "Median Returns(Trades)", "Median Returns(Quote)",
               "Standard Deviation(Trades)", "Standard Deviation(Quotes)", "Mean Absolute Deviation(Trades)",
               "Mean Absolute Deviation(Quotes)", "Skew(Trades)", "Skew(Quotes)", "Kurtosis(Trades)",
               "Kurtosis(Quotes)", "10 Largest Returns(Trades)", "10 Largest Returns(Quotes)",
               "10 Smallest Returns(Trades)", "10 Smallest Returns(Quotes)", "Maximum Drawdown(Trades)",
               "Maximum Drawdown(Quotes)"]

    stock_data_table = pd.DataFrame(columns=columns)

    for ticker in spx_tickers:

        length = 0
        total_trades = 0
        total_quotes = 0
        ticker_trade_data = trade_data[trade_data["Ticker"] == ticker]
        ticker_quote_data = quote_data[quote_data["Ticker"] == ticker]

        for date in trade_dates:
            try:
                if (not clean_data):
                    trade_reader = TAQTradesReader(
                        str(MyDirectories.getTradesDir()) + '/' + date + '/' + ticker + '_trades.binRT')
                else:
                    trade_reader = TAQTradesReader(
                        str(MyDirectories.getTradesClDir()) + '/' + date + '/' + ticker + '_trades.binRT')
            except:
                continue
            N = trade_reader.getN()
            if N > 0:
                length = length + 1
            total_trades = total_trades + N

            trade_date_filter = ticker_trade_data[ticker_trade_data["Date"] == date]
            trade_returns = np.array(trade_date_filter["Returns"]) * 252
            trade_returns_mean = trade_returns.mean()
            trade_returns_median = np.median(trade_returns)
            trade_returns_std = trade_returns.std()
            trade_mad = np.abs(trade_returns - trade_returns_median)
            trade_returns_mad = np.median(trade_mad)
            trade_returns_skew = scp.skew(trade_returns)
            trade_returns_kurtosis = scp.kurtosis(trade_returns)
            trade_returns_sorted = np.argsort(trade_returns)
            trade_returns_10_largest = trade_returns[trade_returns_sorted[-10:]]
            trade_returns_10_smallest = trade_returns[trade_returns_sorted[: 10]]

            cum_returns = np.cumprod(1 + trade_returns)
            running_max = np.maximum.accumulate(cum_returns)
            drawdowns = (cum_returns - running_max) / running_max
            max_trade_drawdown = np.min(drawdowns)

            try:
                if not clean_data:
                    quote_reader = TAQQuotesReader(
                        str(MyDirectories.getQuotesDir()) + '/' + date + '/' + ticker + '_quotes.binRQ')
                else:
                    quote_reader = TAQQuotesReader(
                        str(MyDirectories.getQuotesClDir()) + '/' + date + '/' + ticker + '_quotes.binRQ')
            except:
                continue
            N = quote_reader.getN()
            total_quotes = total_quotes + N
            trade_quote_ratio = total_trades / total_quotes
            quote_date_filter = ticker_quote_data[ticker_quote_data["Date"] == date]
            quote_returns = np.array(quote_date_filter["Returns"]) * 252
            quote_returns_mean = quote_returns.mean()
            quote_returns_median = np.median(quote_returns)
            quote_returns_std = quote_returns.std()
            quote_mad = np.abs(quote_returns - quote_returns_median)
            quote_returns_mad = np.median(quote_mad)
            quote_returns_skew = scp.skew(quote_returns)
            quote_returns_kurtosis = scp.kurtosis(quote_returns)

            quote_returns_sorted = np.argsort(quote_returns)
            quote_returns_10_largest = quote_returns[quote_returns_sorted[-10:]]
            quote_returns_10_smallest = quote_returns[quote_returns_sorted[: 10]]

            cum_returns = np.cumprod(1 + quote_returns)
            running_max = np.maximum.accumulate(cum_returns)
            drawdowns = (cum_returns - running_max) / running_max
            max_quote_drawdown = np.min(drawdowns)

            value = {"Ticker": ticker, "Date": date, 'Length(days)': length, "Total Trades": total_trades,
                     "Total Quotes": total_quotes, "Mean Returns(Trades)": trade_returns_mean,
                     "Mean Returns(Quotes)": quote_returns_mean, "Trade Quote Ratio": trade_quote_ratio,
                     "Median Returns(Trades)": trade_returns_median,
                     "Median Returns(Quote)": quote_returns_median, "Standard Deviation(Trades)": trade_returns_std,
                     "Standard Deviation(Quotes)": quote_returns_std,
                     "Mean Absolute Deviation(Trades)": trade_returns_mad,
                     "Mean Absolute Deviation(Quotes)": quote_returns_mad, "Skew(Trades)": trade_returns_skew,
                     "Skew(Quotes)": quote_returns_skew, "Kurtosis(Trades)": trade_returns_kurtosis,
                     "Kurtosis(Quotes)": quote_returns_kurtosis, "10 Largest Returns(Trades)": trade_returns_10_largest,
                     "10 Largest Returns(Quotes)": quote_returns_10_largest,
                     "10 Smallest Returns(Trades)": trade_returns_10_smallest,
                     "10 Smallest Returns(Quotes)": quote_returns_10_smallest,
                     "Maximum Drawdown(Trades)": max_trade_drawdown,
                     "Maximum Drawdown(Quotes)": max_quote_drawdown}
            stock_data_table = stock_data_table.append(value, ignore_index=True)

    stock_data_table = stock_data_table.round(decimals=5)
    if (X == None):
        filename = str(MyDirectories.getTAQDir()) + "stock_stats_" + str(
            stocks) + "_" + "Full_" + start_date_string + "_" + end_date_string + ".csv"
    else:
        filename = str(MyDirectories.getTAQDir()) + "stock_stats_" + str(stocks) + "_" + str(
            X) + "_min_" + start_date_string + "_" + end_date_string + ".csv"
    stock_data_table.to_csv(Path(filename))
    # columns = ["Ticker", "Date", "Length(days)", "Total Trades", "Mean Returns(Trades)"]

    plot_stats(stock_data_table, spx_tickers, trade_dates)

    return stock_data_table

"""
basic_daily_stats function calculates daily statistics of a stock as asked in question 2b
Returns are calculated based on the changes in daily returns of the stock. 
-----------------------------------------------------------------------------------------------------------------
Parameters to input are:
---> X: Which is supposed to be 600 to calculate daily returns. Since 600 mins equate to 10 hrs
---> stocks: List of stocks. In the question we run this over the entire S&P book
---> start_date_string: start_date
---> end_date_string: end_date 
---> clean_data: indicates whether we ran a clean version of the data
"""


def basic_daily_stats(X=None, stocks=None, start_date_string=start_date, end_date_string=end_date, clean_data=0):
    baseDir = MyDirectories.getTAQDir()
    fm = FileManager(baseDir)
    trade_dates = sorted(fm.getTradeDates(start_date_string, end_date_string))
    quote_dates = sorted(fm.getQuoteDates(start_date_string, end_date_string))

    # The default duration for returns is to get daily returns
    if X == None:
        X = 600

    trade_data, quote_data = x_minute_stats(X, stocks, clean_data=clean_data)
    trade_data = trade_data.fillna(trade_data.mean())
    quote_data = quote_data.fillna(trade_data.mean())
    spx_tickers = stocks

    if spx_tickers == None:
        spx_data = pd.read_excel('/data_orig/s&p500.xlsx', sheet_name=['WRDS'])
        spx_tickers = spx_data['WRDS']['Ticker Symbol']
        spx_tickers = spx_tickers.unique()

    columns = ["Ticker", "Sample Length(days)", "Total Trades", "Total Quotes", "Mean Returns(Trades)",
               "Mean Returns(Quotes)", "Trade Quote Ratio", "Median Returns(Trades)", "Median Returns(Quote)",
               "Standard Deviation(Trades)", "Standard Deviation(Quotes)", "Mean Absolute Deviation(Trades)",
               "Mean Absolute Deviation(Quotes)", "Skew(Trades)", "Skew(Quotes)", "Kurtosis(Trades)",
               "Kurtosis(Quotes)", "10 Largest Returns(Trades)", "10 Largest Returns(Quotes)",
               "10 Smallest Returns(Trades)", "10 Smallest Returns(Quotes)", "Maximum Drawdown(Trades)",
               "Maximum Drawdown(Quotes)"]

    stock_data_table = pd.DataFrame(columns=columns)

    for ticker in spx_tickers:

        length = 0
        total_trades = 0
        total_quotes = 0
        ticker_trade_data = trade_data[trade_data["Ticker"] == ticker]
        ticker_quote_data = quote_data[quote_data["Ticker"] == ticker]

        # trade_date_filter = ticker_trade_data[ticker_trade_data["Date"] == date]
        trade_returns = np.array(ticker_trade_data["Returns"]) * 252
        trade_returns_mean = trade_returns.mean()
        trade_returns_median = np.median(trade_returns)
        trade_returns_std = trade_returns.std()
        trade_mad = np.abs(trade_returns - trade_returns_median)
        trade_returns_mad = np.median(trade_mad)
        trade_returns_skew = scp.skew(trade_returns)
        trade_returns_kurtosis = scp.kurtosis(trade_returns)

        trade_returns_sorted = np.argsort(trade_returns)
        trade_returns_10_largest = trade_returns[trade_returns_sorted[-10:]]
        trade_returns_10_smallest = trade_returns[trade_returns_sorted[: 10]]

        cum_returns = np.cumprod(1 + trade_returns)
        running_max = np.maximum.accumulate(cum_returns)
        drawdowns = (cum_returns - running_max) / running_max
        try:
            max_trade_drawdown = np.min(drawdowns)
        except:
            max_trade_drawdown = 0

        # quote_date_filter = ticker_quote_data[ticker_quote_data["Date"] == date]
        quote_returns = np.array(ticker_quote_data["Returns"]) * 252
        quote_returns_mean = quote_returns.mean()
        quote_returns_median = np.median(quote_returns)
        quote_returns_std = quote_returns.std()
        quote_mad = np.abs(quote_returns - quote_returns_median)
        quote_returns_mad = np.median(quote_mad)
        quote_returns_skew = scp.skew(quote_returns)
        quote_returns_kurtosis = scp.kurtosis(quote_returns)

        quote_returns_sorted = np.argsort(quote_returns)
        quote_returns_10_largest = quote_returns[quote_returns_sorted[-10:]]
        quote_returns_10_smallest = quote_returns[quote_returns_sorted[: 10]]

        cum_returns = np.cumprod(1 + quote_returns)
        running_max = np.maximum.accumulate(cum_returns)
        drawdowns = (cum_returns - running_max) / running_max
        try:
            max_quote_drawdown = np.min(drawdowns)
        except:
            max_quote_drawdown = 0

        for date in trade_dates:
            try:
                trade_reader = TAQTradesReader(
                    str(MyDirectories.getTradesDir()) + '/' + date + '/' + ticker + '_trades.binRT')
            except:
                continue
            N = trade_reader.getN()
            if N > 0:
                length = length + 1
            total_trades = total_trades + N

            try:
                quote_reader = TAQQuotesReader(
                    str(MyDirectories.getQuotesDir()) + '/' + date + '/' + ticker + '_quotes.binRQ')
            except:
                continue
            N = quote_reader.getN()
            total_quotes = total_quotes + N
            trade_quote_ratio = total_trades / total_quotes

        value = {"Ticker": ticker, "Sample Length(days)": length, "Total Trades": total_trades,
                 "Total Quotes": total_quotes, "Mean Returns(Trades)": trade_returns_mean,
                 "Mean Returns(Quotes)": quote_returns_mean, "Trade Quote Ratio": trade_quote_ratio,
                 "Median Returns(Trades)": trade_returns_median,
                 "Median Returns(Quote)": quote_returns_median, "Standard Deviation(Trades)": trade_returns_std,
                 "Standard Deviation(Quotes)": quote_returns_std,
                 "Mean Absolute Deviation(Trades)": trade_returns_mad,
                 "Mean Absolute Deviation(Quotes)": quote_returns_mad, "Skew(Trades)": trade_returns_skew,
                 "Skew(Quotes)": quote_returns_skew, "Kurtosis(Trades)": trade_returns_kurtosis,
                 "Kurtosis(Quotes)": quote_returns_kurtosis, "10 Largest Returns(Trades)": trade_returns_10_largest,
                 "10 Largest Returns(Quotes)": quote_returns_10_largest,
                 "10 Smallest Returns(Trades)": trade_returns_10_smallest,
                 "10 Smallest Returns(Quotes)": quote_returns_10_smallest,
                 "Maximum Drawdown(Trades)": max_trade_drawdown,
                 "Maximum Drawdown(Quotes)": max_quote_drawdown}
        stock_data_table = stock_data_table.append(value, ignore_index=True)

    stock_data_table = stock_data_table.round(decimals=5)
    if (X == 600):
        filename = str(
            MyDirectories.getTAQDir()) + "basic_daily_stats_" + "Full_" + start_date_string + "_" + end_date_string + ".csv"
    else:
        filename = str(MyDirectories.getTAQDir()) + "stock_stats_" + str(stocks) + "_" + str(
            X) + "_min_" + start_date_string + "_" + end_date_string + ".csv"
    stock_data_table.to_csv(Path(filename))
    # columns = ["Ticker", "Date", "Length(days)", "Total Trades", "Mean Returns(Trades)"]

    # plot_stats(stock_data_table, spx_tickers, trade_dates)


def plot_stats(stock_data_table, tickers, dates):
    columns = ["Ticker", "Date", "Length(days)", "Total Trades", "Total Quotes", "Mean Returns(Trades)",
               "Mean Returns(Quotes)", "Trade Quote Ratio", "Median Returns(Trades)", "Median Returns(Quote)",
               "Standard Deviation(Trades)", "Standard Deviation(Quotes)", "Mean Absolute Deviation(Trades)",
               "Mean Absolute Deviation(Quotes)", "Skew(Trades)", "Skew(Quotes)", "Kurtosis(Trades)",
               "Kurtosis(Quotes)", "10 Largest Returns(Trades)", "10 Largest Returns(Quotes)",
               "10 Smallest Returns(Trades)", "10 Smallest Returns(Quotes)", "Maximum Drawdown(Trades)",
               "Maximum Drawdown(Quotes)"]

    for column in columns:

        if column in ["Ticker", "Date", "Length(days)", "10 Largest Returns(Trades)", "10 Largest Returns(Quotes)",
                      "10 Smallest Returns(Trades)", "10 Smallest Returns(Quotes)"]:
            continue

        plt.figure(figsize=(14, 6))
        plt.title(column + ' with Dates')
        plt.xlabel('Dates')
        plt.ylabel(column)
        ax = plt.gca()
        plt.grid()
        for ticker in tickers:
            ticker_data = stock_data_table[stock_data_table["Ticker"] == ticker]
            plt.plot(dates, ticker_data[column], label=column + " : " + ticker)
        plt.legend(labelspacing=1, title='Stocks', fontsize='large')
        ax.set_xticklabels([])


def get_vwap(reader, startTS, endTS):
    v = 0
    s = 0
    counter = 0
    for i in range(0, reader.getN()):
        if reader.getMillisFromMidn(i) < startTS:
            continue
        if reader.getMillisFromMidn(i) >= endTS:
            break
        counter = counter + 1
        v = v + (reader.getSize(i) * reader.getPrice(i))
        s = s + reader.getSize(i)
    if counter == 0:
        counter = 0
        vwap = None
    else:
        counter = counter
        vwap = v / s

    return vwap, counter


def impact_model_stats(stocks=None, start_date=start_date, end_date=end_date):
    baseDir = MyDirectories.getTAQDir()
    fm = FileManager(baseDir)
    tradefilepath = MyDirectories.getTAQDir() / "tradeReturns.csv"
    quotefilepath = MyDirectories.getTAQDir() / "quoteReturns.csv"
    trade_dates = sorted(fm.getTradeDates(start_date, end_date))
    quote_dates = sorted(fm.getQuoteDates(start_date, end_date))
    X = 2
    startTS = 34200000
    endTS = 57600000
    endTS_330 = endTS - 1800000
    # Creating a tables for trading data

    spx_tickers = stocks

    # Fetching SPX tickers from the file
    if spx_tickers is None:
        spx_data = pd.read_excel(os.getcwd() + '/data_orig/s&p500.xlsx', sheet_name=['WRDS'])
        spx_tickers = spx_data['WRDS']['Ticker Symbol']
        spx_tickers = spx_tickers.unique()

    # We compute various matrices
    mid_quote_matrix = pd.DataFrame(columns=quote_dates)
    total_daily_volume_matrix = pd.DataFrame(columns=quote_dates)
    arrival_price_matrix = pd.DataFrame(columns=quote_dates)
    imbalance_matrix = pd.DataFrame(columns=quote_dates)
    vwap_330_matrix = pd.DataFrame(columns=quote_dates)
    vwap_400_matrix = pd.DataFrame(columns=quote_dates)
    terminal_price_matrix = pd.DataFrame(columns=quote_dates)

    for ticker in spx_tickers:

        # Generating 2-minute mid-quotes matrix
        _, quotes = x_minute_stats(X, [ticker], start_date_string=start_date, end_date_string=end_date)
        quotes_trimmed = quotes[["Ticker", "Date", "Returns"]]
        quotes_grouped = quotes_trimmed.groupby(['Ticker', 'Date']).mean()
        quotes_pivoted = quotes_grouped.pivot_table("Returns", ["Ticker"], "Date")
        mid_quote_matrix = mid_quote_matrix.append(quotes_pivoted)

        # Generating total daily volume matrix
        # Daily Volume is Volume Weighted Average Price times the total volume
        # Generating VWAP 400 and VWAP 330 matrix as well
        # Generating imbalance matrix
        tdv_vals = pd.DataFrame(columns=["Ticker", "Date", "Trade Volume"])
        vwap_400_vals = pd.DataFrame(columns=["Ticker", "Date", "VWAP"])
        vwap_330_vals = pd.DataFrame(columns=["Ticker", "Date", "VWAP"])
        imbalance_vals = pd.DataFrame(columns=["Ticker", "Date", "Imbalance"])
        for date in quote_dates:
            try:
                trade_reader = TAQTradesReader(MyDirectories.getTradesDir()  /  date / (ticker + '_trades.binRT'))
            except:
                continue
            N = trade_reader.getN()
            vwap_400, _ = get_vwap(trade_reader, startTS, endTS)
            vwap_330, _ = get_vwap(trade_reader, startTS, endTS_330)

            if vwap_330 is None:
                continue
            volume = 0

            for index in range(N):
                volume += trade_reader.getSize(index)

            volume_value = {"Ticker": ticker, "Date": date, "Trade Volume": volume * vwap_400}
            tdv_vals = tdv_vals.append(volume_value, ignore_index=True)
            vwap_val = {"Ticker": ticker, "Date": date, "VWAP": vwap_400}
            vwap_400_vals = vwap_400_vals.append(vwap_val, ignore_index=True)
            vwap_val = {"Ticker": ticker, "Date": date, "VWAP": vwap_330}
            vwap_330_vals = vwap_330_vals.append(vwap_val, ignore_index=True)

            tick_test = TickTest()
            classifications = tick_test.classifyAll(trade_reader, startTS, endTS_330)
            imbalance = 0
            for i in range(0, N):
                if trade_reader.getMillisFromMidn(i) < startTS:
                    continue
                if trade_reader.getMillisFromMidn(i) >= endTS_330:
                    break
                imbalance += trade_reader.getSize(i) * classifications[i][2]
            imbalance_val = {"Ticker": ticker, "Date": date, "Imbalance": imbalance * vwap_330}
            imbalance_vals = imbalance_vals.append(imbalance_val, ignore_index=True)
        tdv_pivoted = tdv_vals.pivot_table("Trade Volume", ["Ticker"], "Date")
        total_daily_volume_matrix = total_daily_volume_matrix.append(tdv_pivoted)
        vwap_400_pivoted = vwap_400_vals.pivot_table("VWAP", ["Ticker"], "Date")
        vwap_400_matrix = vwap_400_matrix.append(vwap_400_pivoted)
        vwap_330_pivoted = vwap_330_vals.pivot_table("VWAP", ["Ticker"], "Date")
        vwap_330_matrix = vwap_330_matrix.append(vwap_330_pivoted)
        imbalance_pivoted = imbalance_vals.pivot_table("Imbalance", ["Ticker"], "Date")
        imbalance_matrix = imbalance_matrix.append(imbalance_pivoted)

        # Generating arrival price matrix and terminal price matrix
        arrival_price = pd.DataFrame(columns=["Ticker", "Date", "Average Price"])
        terminal_price = pd.DataFrame(columns=["Ticker", "Date", "Average Price"])
        for date in quote_dates:
            try:
                quote_reader = TAQQuotesReader(MyDirectories.getQuotesDir() / date / (ticker + '_quotes.binRQ'))
            except:
                continue

            N = quote_reader.getN()
            price = 0
            for index in range(0, min(N, 5) - 1):
                price += (quote_reader.getAskPrice(index) + quote_reader.getBidPrice(index)) / 2
            price_value = {"Ticker": ticker, "Date": date, "Average Price": price / min(N, 5)}
            arrival_price = arrival_price.append(price_value, ignore_index=True)

            price = 0
            for index in range(max(N - 5, 0), N - 1):
                price += (quote_reader.getAskPrice(index) + quote_reader.getBidPrice(index)) / 2
            price_value = {"Ticker": ticker, "Date": date, "Average Price": price / min(N, 5)}
            terminal_price = terminal_price.append(price_value, ignore_index=True)

        arrival_price_pivoted = arrival_price.pivot_table("Average Price", ["Ticker"], "Date")
        arrival_price_matrix = arrival_price_matrix.append(arrival_price_pivoted)

        terminal_price_pivoted = terminal_price.pivot_table("Average Price", ["Ticker"], "Date")
        terminal_price_matrix = terminal_price_matrix.append(terminal_price_pivoted)

    print(mid_quote_matrix)

    return mid_quote_matrix, total_daily_volume_matrix, arrival_price_matrix, imbalance_matrix, vwap_330_matrix, vwap_400_matrix, terminal_price_matrix



def stock_analysis(X=None, stocks=None, start_date_string=start_date, end_date_string=end_date):
    stocks = ['MSFT', 'GE']
    # a = stock_stats(X=3, stocks=stocks)

    # a, b = x_minute_stats(X = 600, stocks = stocks)
    # basic_daily_stats()
    quotes_cleaner = TAQCleanQuotes(k=100, tau=0.00025)

    quotes_cleaner.cleanAllQuotes(tickers=stocks)

    trades_cleaner = TAQCleanTrades(k=100, tau=0.00025)

    trades_cleaner.cleanAllTrades(tickers=stocks)

    # stock_stats(X = 1/6, stocks=stocks, clean_data=0)

    # filename = "basic_daily_stats_Full20070620_20070921.csv"
    # stats_table = pd.read_csv(filename)
    #
    # test_data = stats_table.iloc[0]

if __name__ == "__main__":
    # x_minute_stats(10, ['MSFT', 'AAPL'], start_date_string = '20070620', end_date_string = '20070622')
    # stock_stats(X=None, stocks=['SUNW', 'ADP'])
    impact_model_stats(start_date='20070620', end_date='20070623')
