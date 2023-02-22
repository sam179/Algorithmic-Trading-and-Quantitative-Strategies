import MyDirectories
from FileManager import FileManager
import pandas as pd
import BaseUtils as bu
from collections import deque

class TAQAdjust():

    def __init__(self, isquote = False, k = 5, tau = 0.0005):
       self._isquote = isquote
       self._fm = FileManager( MyDirectories.getAdjDir())
       self._snp = bu.readExcel(MyDirectories.getTAQDir() / "s&p500.xlsx").dropna()
       self._k = k
       self._tau = tau
       self._price = deque([],maxlen=self._k)
 
    def cleanData(self, dates = None, tickers = None):
        if self._isquote:
           return self.cleanAllQuotes(dates,tickers) 
        else:
           return self.cleanAllTrades(dates,tickers)

    def cleanAllTrades(self, dates = None, tickers = None):
        
        if dates == None:
           dates = [bu.startDate, bu.endDate]

        if tickers == None:
           tickers =  set(self._snp['Ticker Symbol'].to_list())
       
        # Dates = self._fm.getTradeDates(dates[0], dates[1])

        for ticker in tickers:
            for date in dates:
                tradeData = self._fm.getTradesFile( date, ticker )
                tradeData.rewrite(MyDirectories.BinRTTradesClDir / date / (ticker + '_trades.binRT'), ticker)
                for index in range(tradeData.getN()):

                    if len(self._price) != self.k:
                       self._price.append(tradeData.getPrice(index))
                       continue

                    




    