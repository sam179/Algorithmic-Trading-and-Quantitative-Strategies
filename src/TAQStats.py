import pandas as pd
import numpy as np
import scipy.stats as scp
from taq import MyDirectories
from taq.FileManager import FileManager
from taq.TAQQuotesReader import TAQQuotesReader
from taq.TAQTradesReader import TAQTradesReader
from pathlib import Path

start_date = "20070620"
end_date = "20070624"
time_increment = 60000


def x_minute_stats(X):
    baseDir = MyDirectories.getTAQDir()
    fm = FileManager(baseDir)
    tradefilepath = Path('tradeReturns.csv')
    quotefilepath = Path('quoteReturns.csv')
    trade_dates = sorted(fm.getTradeDates(start_date, end_date))
    quote_dates = sorted(fm.getQuoteDates(start_date, end_date))

    trade_data_table = pd.DataFrame(columns=["Ticker", "Date", "N", "MillisFromMidn", "Size", "Price", "Returns"])
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
            init_time = trade_reader.getMillisFromMidn(0)
            current_time = init_time + X * time_increment
            value = {"Ticker": ticker, "Date": date, "N": 0, "MillisFromMidn": init_time,
                     "Size": trade_reader.getSize(0), "Price": trade_reader.getPrice(0)}
            trade_data = trade_data.append(value, ignore_index=True)
            N = trade_reader.getN()

            # for index in range(N):
            #     if trade_reader.getMillisFromMidn(index) == current_time:
            #         value = {"ticker": ticker, "date": date, "N": index, "MillisFromMidn": current_time,
            #                  "Size": trade_reader.getSize(index), "Price": trade_reader.getPrice(index)}
            #         print(value)
            #         current_time = current_time + X * time_increment
            #         # trade_data_table = pd.concat( [trade_data_table, value], ignore_index=True)
            #         trade_data_table = trade_data_table.append(value, ignore_index=True)

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
            init_time = quote_reader.getMillisFromMidn(0)
            current_time = init_time + X * time_increment
            value = {"Ticker": ticker, "Date": date, "N": 0, "MillisFromMidn": init_time,
                     "AskSize": quote_reader.getAskSize(0), "AskPrice": quote_reader.getAskPrice(0),
                     "BidSize": quote_reader.getBidSize(0), "BidPrice": quote_reader.getBidPrice(0),
                     "MidQuote": (quote_reader.getAskPrice(0) + quote_reader.getBidPrice(0)) / 2}
            quote_data = quote_data.append(value, ignore_index=True)
            N = quote_reader.getN()

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


def stock_stats(X=None, start_date_string=start_date, end_date_string=end_date):
    baseDir = MyDirectories.getTAQDir()
    fm = FileManager(baseDir)
    trade_dates = sorted(fm.getTradeDates(start_date_string, end_date_string))
    quote_dates = sorted(fm.getQuoteDates(start_date_string, end_date_string))

    # The default duration for returns is to get daily returns
    if X == None:
        X = 600

    trade_data, quote_data = x_minute_stats(X)

    spx_data = pd.read_excel('s&p500.xlsx', sheet_name=['WRDS'])
    spx_tickers = spx_data['WRDS']['Ticker Symbol']
    spx_tickers = spx_tickers.unique()
    stock_data_table = pd.DataFrame(
        columns=["Ticker", "Length(days)", "Total Trades", "Total Quotes", "Mean Returns(Trades)",
                 "Mean Returns(Quotes)", "Trade Quote Ratio", "Median Returns(Trades)", "Median Returns(Quote)",
                 "Standard Deviation(Trades)", "Standard Deviation(Quotes)", "Mean Absolute Deviation(Trades)",
                 "Mean Absolute Deviation(Quotes)", "Skew(Trades)", "Skew(Quotes)", "Kurtosis(Trades)",
                 "Kurtosis(Quotes)", "10 Largest Returns(Trades)", "10 Largest Returns(Quotes)",
                 "10 Smallest Returns(Trades)", "10 Smallest Returns(Quotes)"])

    for ticker in spx_tickers:

        length = 0
        total_trades = 0
        total_quotes = 0
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
            total_quotes = total_quotes + N

        trade_quote_ratio = total_trades / total_quotes

        ticker_trade_data = trade_data[trade_data["Ticker"] == ticker]
        trade_returns = np.array(ticker_trade_data["Returns"]) * 252
        trade_returns_mean = trade_returns.mean()
        trade_returns_median = trade_returns.median()
        trade_returns_std = trade_returns.std()
        trade_mad = np.abs(trade_returns - trade_returns_median)
        trade_returns_mad = trade_mad.median()
        trade_returns_skew = scp.skew(trade_returns)
        trade_returns_kurtosis = scp.kurtosis(trade_returns)

        ticker_quote_data = quote_data[quote_data["Ticker"] == ticker]
        quote_returns = np.array(ticker_quote_data["Returns"]) * 252
        quote_returns_mean = quote_returns.mean()
        quote_returns_median = quote_returns.median()
        quote_returns_std = quote_returns.std()
        quote_mad = np.abs(quote_returns - quote_returns_median)
        quote_returns_mad = quote_mad.median()
        quote_returns_skew = scp.skew(quote_returns)
        quote_returns_kurtosis = scp.kurtosis(quote_returns)

        value = {"Ticker": ticker, 'Length(days)': length, "Total Trades": total_trades, "Total Quotes":total_quotes, "Mean Returns(Trades)": trade_returns_mean,
                 "Mean Returns(Quotes)": quote_returns_mean, "Trade Quote Ratio": trade_quote_ratio, "Median Returns(Trades)": trade_returns_median,
                 "Median Returns(Quote)": quote_returns_median, "Standard Deviation(Trades)": trade_returns_std,
                 "Standard Deviation(Quotes)": quote_returns_std, "Mean Absolute Deviation(Trades)": trade_returns_mad,
                 "Mean Absolute Deviation(Quotes)": quote_returns_mad, "Skew(Trades)": trade_returns_skew,
                 "Skew(Quotes)": quote_returns_skew, "Kurtosis(Trades)": trade_returns_kurtosis, "Kurtosis(Quotes)": quote_returns_kurtosis}

        stock_data_table.append(value, ignore_index=True)

if __name__ == "__main__":
    x_minute_stats(100)
