from taq import MyDirectories
from taq.FileManager import FileManager
import pandas as pd


def spx_filter(start_date_string, end_date_string):

    base_dir = MyDirectories.getTAQDir()
    fm = FileManager(base_dir)
    trades = {}
    quotes = {}
    spx_data = pd.read_excel('s&p500.xlsx')
    spx_tickers = spx_data['Trading Symbol']
    spx_tickers = spx_tickers['Trading Symbol'].unique()

    trade_dates = fm.getTradeDates(start_date_string, end_date_string)

    for date in trade_dates:
        tickers = fm.getTradeTickers(date)
        for ticker in tickers:
            if ticker in spx_tickers:
                trades[date].append(ticker)

    quotes = {}
    quote_dates = fm.getQuoteDates(start_date_string, end_date_string)

    for date in quote_dates:
        tickers = fm.getQuoteTickers(date)
        for ticker in tickers:
            if ticker in spx_tickers:
                quotes[date].append(ticker)

    return trades, quotes
