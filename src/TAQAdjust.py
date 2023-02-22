import MyDirectories
from FileManager import FileManager
import pandas as pd
import BaseUtils as bu
cfap = 'Cumulative Factor to Adjust Prices'
cfas = 'Cumulative Factor to Adjust Shares/Vol' 

class TAQAdjust():

    def __init__(self, isquote = False):
       self._isquote = isquote
       self._fm = FileManager( MyDirectories.getTAQDir())
       self._snp = bu.readExcel(MyDirectories.getTAQDir() / "s&p500.csv")
       self._snp["Names Date"] = self._snp["Names Date"].apply(lambda x: str(x)[:-2])
       
    def adjustData(self, dates = None, tickers = None):
        if self._isquote:
           return self.adjustAllQuotes(dates,tickers) 
        else:
           return self.adjustAllTrades(dates,tickers)

    def adjustAllTrades(self, dates = None, tickers = None):

        if dates == None:
           dates = [bu.startDate, bu.endDate]

        if tickers == None:
           tickers =  set(self._snp['Ticker Symbol'].to_list())
       
        Dates = self._fm.getTradeDates(dates[0], dates[1])
        updatedTicker = []
        for ticker in tickers:
            priceFactors = self._snp.loc[self._snp['Ticker Symbol'] == ticker, ['Names Date', cfap]].set_index("Names Date")
            shareFactors = self._snp.loc[self._snp['Ticker Symbol'] == ticker, ['Names Date', cfas]].set_index("Names Date")
            pricechange = priceFactors.loc[Dates[0], cfap] == priceFactors.loc[Dates[-1], cfap]
            sharechange = shareFactors.loc[Dates[0], cfas] == shareFactors.loc[ Dates[-1], cfas]

            if pricechange or sharechange:
               updatedTicker.append(ticker)

            for date in dates:
                tradeData = self._fm.getTradesFile( date, ticker )
                if pricechange:
                   for index in range(tradeData.getN()):
                       tradeData.setPrice(index, tradeData.getPrice(index) / priceFactors.loc[date,cfap])

                if sharechange:
                   for index in range(tradeData.getN()):
                       tradeData.setSize(index, tradeData.getSize(index) * shareFactors.loc[date, cfas])

                tradeData.rewrite(MyDirectories.BinRTTradesAdjDir / date / (ticker + '_trades.binRT'))

        return updatedTicker 


    def adjustAllQuotes(self, dates = None, tickers = None):

        if dates == None:
           dates = [bu.startDate, bu.endDate]

        if tickers == None:
           tickers =  set(self._snp['Ticker Symbol'].to_list())
       
        Dates = self._fm.getQuoteDates(dates[0], dates[1])
        updatedTicker = []
        for ticker in tickers:
            priceFactors = self._snp.loc[self._snp['Ticker Symbol'] == ticker, ['Names Date', cfap]].set_index('Names Date')
            shareFactors = self._snp.loc[self._snp['Ticker Symbol'] == ticker, ['Names Date', cfas]].set_index('Names Date')
            pricechange = priceFactors.loc[Dates[0]] == priceFactors[Dates[-1]]
            sharechange = shareFactors.loc[Dates[0]] == shareFactors[Dates[-1]]
            
            if pricechange or sharechange:
               updatedTicker.append(ticker)

            for date in dates:
                quoteData = self._fm.getQuotesFile( date, ticker )
                if pricechange:
                   for index in range(quoteData.getN()):
                       quoteData.setBidPrice(index, quoteData.getBidPrice(index) / pricechange.loc[date])
                       quoteData.setAskPrice(index, quoteData.getAskPrice(index) / pricechange.loc[date])

                if sharechange:
                   for index in range(quoteData.getN()):
                       quoteData.setBidSize(index, quoteData.getBidSize(index) * sharechange.loc[date])
                       quoteData.setAskSize(index, quoteData.getAskSize(index) * sharechange.loc[date])

                quoteData.rewrite(MyDirectories.BinRQQuotesAdjDir / date / (ticker + '_quotes.binRQ'))

        return updatedTicker            






    
