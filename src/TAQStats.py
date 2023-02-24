import pandas as pd
from taq import MyDirectories
from taq.FileManager import FileManager
from taq.TAQQuotesReader import TAQQuotesReader
from taq.TAQTradesReader import TAQTradesReader
from pathlib import Path

start_date = "20070620"
end_date = "20070624"
time_increment = 60000


def X_minute_stats(X):
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
    #spx_tickers = ['SUNW']

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

        trade_data["Returns"] = trade_data["Price"].pct_change(1).round(decimals = 5)
        trade_data_table = trade_data_table.append(trade_data)


    quote_data_table = pd.DataFrame(columns=["Ticker", "Date", "N", "MillisFromMidn", "AskSize", "AskPrice", "BidSize", "BidPrice", "MidQuote", "Returns"])

    for ticker in spx_tickers:
        quote_data = pd.DataFrame(
            columns=["Ticker", "Date", "N", "MillisFromMidn", "AskSize", "AskPrice", "BidSize", "BidPrice", "MidQuote"])
        for date in trade_dates:

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
                     "MidQuote": (quote_reader.getAskPrice(0) + quote_reader.getBidPrice(0))/2}
            quote_data = quote_data.append(value, ignore_index=True)
            N = quote_reader.getN()

            for index in range(N):
                if quote_reader.getMillisFromMidn(index) > current_time:
                    value = {"Ticker": ticker, "Date": date, "N": index - 1, "MillisFromMidn": current_time,
                             "AskSize": quote_reader.getAskSize(index - 1), "AskPrice": quote_reader.getAskPrice(index - 1),
                             "BidSize": quote_reader.getBidSize(index - 1), "BidPrice": quote_reader.getBidPrice(index - 1),
                             "MidQuote": (quote_reader.getAskPrice(index - 1) + quote_reader.getBidPrice(index - 1))/2}
                    print(value)
                    current_time = current_time + X * time_increment
                    # trade_data_table = pd.concat( [trade_data_table, value], ignore_index=True)
                    quote_data = quote_data.append(value, ignore_index=True)

        quote_data["Returns"] = quote_data["MidQuote"].pct_change(1).round(decimals=5)
        quote_data_table = quote_data_table.append(quote_data)

    trade_data_table.to_csv(tradefilepath)
    quote_data_table.to_csv(quotefilepath)

if __name__ == "__main__":
    X_minute_stats(100)
