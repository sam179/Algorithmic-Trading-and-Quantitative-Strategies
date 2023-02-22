import MyDirectories
from FileManager import FileManager
import pandas as pd
import BaseUtils as bu
import shutil
from collections import deque
import os
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
            pricechange = priceFactors.loc[Dates[0], cfap] != priceFactors.loc[Dates[-1], cfap]
            sharechange = shareFactors.loc[Dates[0], cfas] != shareFactors.loc[Dates[-1], cfas]

            for date in Dates:
               if not os.path.isdir(MyDirectories.getTradesAdjDir() / date):
                     os.makedirs(MyDirectories.getTradesAdjDir() / date)

               if (not pricechange) and (not sharechange):
                  shutil.copy(MyDirectories.getTradesDir() / date / (ticker + '_trades.BinRT'), MyDirectories.getTradesAdjDir() / date /"")
                  continue

               tradeData = self._fm.getTradesFile( date, ticker )
               prices = []
               shares = []
               ts = []      

               for index in range(tradeData.getN()):
                  ts.append(tradeData.getMillisFromMidn(index))
                  prices.append(tradeData.getPrice(index))
                  shares.append(tradeData.getSize(index))

                  if pricechange:
                     prices[-1] = prices[-1] / priceFactors.loc[date,cfap]

                  if sharechange:
                     shares[-1] = int(shares[-1] * shareFactors.loc[date, cfas])

               bu.writeToBinTrades(MyDirectories.getTradesAdjDir() / date / (ticker + '_trades.BinRT'), \
                             [tradeData.getSecsFromEpocToMidn(), tradeData.getN()],\
                             [ts, shares, prices])            
            
            
            if pricechange or sharechange:
               updatedTicker.append(ticker)    

        return updatedTicker 


    def adjustAllQuotes(self, dates = None, tickers = None):

        if dates == None:
           dates = [bu.startDate, bu.endDate]

        if tickers == None:
           tickers =  set(self._snp['Ticker Symbol'].to_list())
       
        Dates = self._fm.getQuoteDates(dates[0], dates[1])
        updatedTicker = []
        for ticker in tickers:
            priceFactors = self._snp.loc[self._snp['Ticker Symbol'] == ticker, ['Names Date', cfap]].set_index("Names Date")
            shareFactors = self._snp.loc[self._snp['Ticker Symbol'] == ticker, ['Names Date', cfas]].set_index("Names Date")
            pricechange = priceFactors.loc[Dates[0], cfap] != priceFactors.loc[Dates[-1], cfap]
            sharechange = shareFactors.loc[Dates[0], cfas] != shareFactors.loc[Dates[-1], cfas]

            for date in Dates:
               if not os.path.isdir(MyDirectories.getQuotesAdjDir() / date):
                     os.makedirs(MyDirectories.getQuotesAdjDir() / date)

               if (not pricechange) and (not sharechange):
                  shutil.copy(MyDirectories.getQuotesDir() / date / (ticker + '_quotes.BinRQ'), MyDirectories.getQuotesAdjDir() / date /"")
                  continue

               tradeData = self._fm.getQuotesFile( date, ticker )
               bidprices = []
               bidsize = []
               askprices = []
               asksize = []
               ts = []      

               for index in range(tradeData.getN()):
                  ts.append(tradeData.getMillisFromMidn(index))
                  bidprices.append(tradeData.getBidPrice(index))
                  bidsize.append(tradeData.getBidSize(index))
                  askprices.append(tradeData.getAskPrice(index))
                  asksize.append(tradeData.getAskSize(index))

                  if pricechange:
                     bidprices[-1] = bidprices[-1] / priceFactors.loc[date,cfap]
                     askprices[-1] = askprices[-1] / priceFactors.loc[date,cfap]

                  if sharechange:
                     bidsize[-1] = int(bidsize[-1] * shareFactors.loc[date, cfas])
                     asksize[-1] = int(asksize[-1] * shareFactors.loc[date, cfas])

               bu.writeToBinQuotes(MyDirectories.getQuotesAdjDir() / date / (ticker + '_quotes.BinRQ'), \
                             [tradeData.getSecsFromEpocToMidn(), tradeData.getN()],\
                             [ts, asksize, askprices, bidsize, bidprices])            
            
            
            if pricechange or sharechange:
               updatedTicker.append(ticker)    

        return updatedTicker             






    
