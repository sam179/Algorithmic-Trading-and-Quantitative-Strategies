import pandas as pd
import numpy as np
import scipy.stats as scp
from taq import MyDirectories
from taq.FileManager import FileManager
from taq.TAQQuotesReader import TAQQuotesReader
from taq.TAQTradesReader import TAQTradesReader
import matplotlib.pyplot as plt
from pathlib import Path
import warnings
import openpyxl

warnings.simplefilter('ignore')

start_date = "20070620"
end_date = "20070920"
time_increment = 60000

"""
x_minute_stats function takes as input two parameters:
--> X :  represents the x minute variable for which returns are computed. 
         In case, no values is passed the default behaviour of the function is to 
         iterate every single price in the TAQ dataset
--> stocks: represents the list of stock. In case, no value is passed, the default 
         behaviour is to get the list of stocks from S&P500 excel file in the directory. 
------------------------------------------------------------------------------------------
The function lists out the returns in every x minute starting from the first tick of every 
day. This data is stored in relevant files. 

"""
def x_minute_stats(X=None, stocks=None):

    baseDir = MyDirectories.getTAQDir()
    fm = FileManager(baseDir)
    tradefilepath = Path('tradeReturns.csv')
    quotefilepath = Path('quoteReturns.csv')
    trade_dates = sorted(fm.getTradeDates(start_date, end_date))
    quote_dates = sorted(fm.getQuoteDates(start_date, end_date))

    # Creating a tables for trading data
    trade_data_table = pd.DataFrame(columns=["Ticker", "Date", "N", "MillisFromMidn", "Size", "Price", "Returns"])

    spx_tickers = stocks

    # Fetching SPX tickers from the file
    if spx_tickers == None:
        spx_data = pd.read_excel('s&p500.xlsx', sheet_name=['WRDS'])
        spx_tickers = spx_data['WRDS']['Ticker Symbol']
        spx_tickers = spx_tickers.unique()
    # spx_tickers = ['SUNW']

    for ticker in spx_tickers:
        trade_data = pd.DataFrame(columns=["Ticker", "Date", "N", "MillisFromMidn", "Size", "Price"])
        for date in trade_dates:
            try:
                print('Getting Trade data for ' + ticker + ', date: ' + str(date))
            except:
                print(ticker)
                continue
            try:
                trade_reader = TAQTradesReader(
                    MyDirectories.getTradesDir() + '/' + date + '/' + ticker + '_trades.binRT')
            except:
                pass

            N = trade_reader.getN()

            # Default behaviour in case no X is specified
            if X == None:
                for index in range(N):
                    print('Data Entry ' + str(index) + ' of ' + str(N))
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
                        print(value)
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
                print('Getting Quote data for ' + ticker + ', date: ' + str(date))
            except:
                print(ticker)
                continue
            try:
                quote_reader = TAQQuotesReader(
                    MyDirectories.getQuotesDir() + '/' + date + '/' + ticker + '_quotes.binRQ')
            except:
                pass

            N = quote_reader.getN()
            if X == None:
                for index in range(N):
                    print('Data Entry ' + str(index) + ' of ' + str(N))
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
                        print(value)
                        current_time = current_time + X * time_increment
                        # trade_data_table = pd.concat( [trade_data_table, value], ignore_index=True)
                        quote_data = quote_data.append(value, ignore_index=True)

        quote_data["Returns"] = quote_data["MidQuote"].pct_change(1).round(decimals=5)
        quote_data_table = quote_data_table.append(quote_data)

    trade_data_table.to_csv(tradefilepath)
    quote_data_table.to_csv(quotefilepath)

    return trade_data_table, quote_data_table

"""
stock_stats function takes in as arguments 4 parameters:
--> X: x minutes for which returns will be calculated by calling function  x_minute_stats
--> stocks: which represents the list of stocks for which calculation needs to be done
--> start_date_string: start date
--> end_date_string: end date
---------------------------------------------------------------------------------------------------------
This function calculates basic stats for the given stocks. These stats are computed for a trading day and 
on the basis of X minute return calculations. These stats include means, standard deviations etc across 
various metrics.  
"""
def stock_stats(X=100, stocks=None, start_date_string=start_date, end_date_string=end_date):
    baseDir = MyDirectories.getTAQDir()
    fm = FileManager(baseDir)
    trade_dates = sorted(fm.getTradeDates(start_date_string, end_date_string))
    quote_dates = sorted(fm.getQuoteDates(start_date_string, end_date_string))

    # The default duration for returns is to get daily returns
    if X == None:
        X = 600

    trade_data, quote_data = x_minute_stats(X, stocks)
    trade_data = trade_data.fillna(trade_data.mean())
    quote_data = quote_data.fillna(trade_data.mean())
    spx_tickers = stocks

    if spx_tickers == None:
        spx_data = pd.read_excel('s&p500.xlsx', sheet_name=['WRDS'])
        spx_tickers = spx_data['WRDS']['Ticker Symbol']
        spx_tickers = spx_tickers.unique()

    columns = ["Ticker", "Date", "Length(days)", "Total Trades", "Total Quotes", "Mean Returns(Trades)",
               "Mean Returns(Quotes)", "Trade Quote Ratio", "Median Returns(Trades)", "Median Returns(Quote)",
               "Standard Deviation(Trades)", "Standard Deviation(Quotes)", "Mean Absolute Deviation(Trades)",
               "Mean Absolute Deviation(Quotes)", "Skew(Trades)", "Skew(Quotes)", "Kurtosis(Trades)",
               "Kurtosis(Quotes)", "10 Largest Returns(Trades)", "10 Largest Returns(Quotes)",
               "10 Smallest Returns(Trades)", "10 Smallest Returns(Quotes)", "Maximum Drawdown(Trades)", "Maximum Drawdown(Quotes)"]

    stock_data_table = pd.DataFrame(columns=columns)

    for ticker in spx_tickers:

        length = 0
        total_trades = 0
        total_quotes = 0
        ticker_trade_data = trade_data[trade_data["Ticker"] == ticker]
        ticker_quote_data = quote_data[quote_data["Ticker"] == ticker]

        for date in trade_dates:
            try:
                print('Getting Trade data for ' + ticker + ', date: ' + str(date))
            except:
                print(ticker)
                continue
            try:
                trade_reader = TAQTradesReader(
                    MyDirectories.getTradesDir() + '/' + date + '/' + ticker + '_trades.binRT')
            except:
                pass
            N = trade_reader.getN()
            if N > 0:
                length = length + 1
            total_trades = total_trades + N

            trade_date_filter = ticker_trade_data[ticker_trade_data["Date"] == date]
            trade_returns = np.array(trade_date_filter["Returns"]) * 252
            print(trade_returns)
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
            drawdowns = (cum_returns - running_max)/running_max
            max_trade_drawdown = np.min(drawdowns)

            try:
                print('Getting Quote data for ' + ticker + ', date: ' + str(date))
            except:
                print(ticker)
                continue
            try:
                quote_reader = TAQQuotesReader(
                    MyDirectories.getQuotesDir() + '/' + date + '/' + ticker + '_quotes.binRQ')
            except:
                pass
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
                     "10 Smallest Returns(Quotes)": quote_returns_10_smallest, "Maximum Drawdown(Trades)": max_trade_drawdown,
                     "Maximum Drawdown(Quotes)": max_quote_drawdown}
            stock_data_table = stock_data_table.append(value, ignore_index=True)

    stock_data_table = stock_data_table.round(decimals=5)
    #print(stock_data_table)
    if (X == None):
        filename = "stock_stats_" + str(stocks) + "_" + "Full" + "_min_" + start_date_string + "_" + end_date_string + ".csv"
    else:
        filename = "stock_stats_" + str(stocks) + "_" + str(X) + "_min_" + start_date_string + "_" + end_date_string + ".csv"
    stock_data_table.to_csv(Path(filename))
    #columns = ["Ticker", "Date", "Length(days)", "Total Trades", "Mean Returns(Trades)"]
    for column in columns:

        if column in ["Ticker", "Date", "Length(days)", "10 Largest Returns(Trades)", "10 Largest Returns(Quotes)",
                      "10 Smallest Returns(Trades)", "10 Smallest Returns(Quotes)"]:
            continue

        plt.figure(figsize=(14, 6))
        plt.title(column + ' with Dates')
        plt.xlabel('Dates')
        plt.ylabel(column)
        plt.grid()
        for ticker in spx_tickers:
            ticker_data = stock_data_table[stock_data_table["Ticker"] == ticker]
            plt.plot(trade_dates, ticker_data[column], label=column + " : " + ticker)
        plt.legend(labelspacing=1, title='Stocks', fontsize='large')
        plt.show()


def stock_analysis(X=None, stocks=None, start_date_string=start_date, end_date_string=end_date):

    stock_stats(X=X, stocks=stocks)



if __name__ == "__main__":
    # x_minute_stats(100)
    stock_stats(X=10, stocks=['SUNW', 'ADP'])
