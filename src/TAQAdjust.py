import MyDirectories
from FileManager import FileManager
import pandas as pd
import BaseUtils
import shutil
from collections import deque
import os
cfap = 'Cumulative Factor to Adjust Prices'
cfas = 'Cumulative Factor to Adjust Shares/Vol' 

class TAQAdjust():

    def __init__(self, isquote = False):
       self._isquote = isquote
       self._fm = FileManager( MyDirectories.getTAQDir())

    def adjustData(self, dates = None, tickers = None):
        if self._isquote:
           return self.adjustAllQuotes(dates,tickers) 
        else:
           return self.adjustAllTrades(dates,tickers)

    def adjustAllTrades(self, dates = None, tickers = None):

        if not dates : dates = BaseUtils.default_dates
        if not tickers : tickers = BaseUtils.snp_tickers

        Dates = self._fm.getTradeDates(dates[0], dates[1])
        for ticker in tickers:
               
            priceFactors = BaseUtils.snp.loc[BaseUtils.snp['Ticker Symbol'] == ticker, ['Names Date', cfap]].set_index("Names Date")
            shareFactors = BaseUtils.snp.loc[BaseUtils.snp['Ticker Symbol'] == ticker, ['Names Date', cfas]].set_index("Names Date")
            pricechange = priceFactors.iloc[0, 0] != priceFactors.iloc[-1, 0]
            sharechange = shareFactors.iloc[0, 0] != shareFactors.iloc[-1, 0]

            for date in Dates:
               BaseUtils.mkDir(MyDirectories.getTradesAdjDir() / date)
               try:
                  if (not pricechange) and (not sharechange):
                        shutil.copy(MyDirectories.getTradesDir() / date / (ticker + '_trades.BinRT'), \
                                    MyDirectories.getTradesAdjDir() / date /"")
                        continue
                  else:
                     tradeData = self._fm.getTradesFile( date, ticker )

               except:
                  print(ticker, date, "FILE NOT FOUND")
                  continue

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

               BaseUtils.writeToBinTrades(MyDirectories.getTradesAdjDir() / date / (ticker + '_trades.BinRT'), \
                           [tradeData.getSecsFromEpocToMidn(), tradeData.getN()],\
                           [ts, shares, prices])  


    def adjustAllQuotes(self, dates = None, tickers = None):

        if not dates : dates = BaseUtils.default_dates
        if not tickers : tickers = BaseUtils.snp_tickers
           
        Dates = self._fm.getQuoteDates(dates[0], dates[1])

        for ticker in tickers:
            priceFactors = BaseUtils.snp.loc[BaseUtils.snp['Ticker Symbol'] == ticker, ['Names Date', cfap]].set_index("Names Date")
            shareFactors = BaseUtils.snp.loc[BaseUtils.snp['Ticker Symbol'] == ticker, ['Names Date', cfas]].set_index("Names Date")
            pricechange = priceFactors.iloc[0, 0] != priceFactors.iloc[-1, 0]
            sharechange = shareFactors.iloc[0, 0] != shareFactors.iloc[-1, 0]

            for date in Dates:
               BaseUtils.mkDir(MyDirectories.getQuotesAdjDir() / date)
               try:
                  if (not pricechange) and (not sharechange):
                     shutil.copy(MyDirectories.getQuotesDir() / date / (ticker + '_quotes.BinRQ'), MyDirectories.getQuotesAdjDir() / date /"")
                     continue
                  else:
                     quoteData = self._fm.getQuotesFile( date, ticker )
               except:
                  print(ticker, date, "FILE NOT FOUND")
                  continue

               bidprices = []
               bidsize = []
               askprices = []
               asksize = []
               ts = []      

               for index in range(quoteData.getN()):
                  ts.append(quoteData.getMillisFromMidn(index))
                  bidprices.append(quoteData.getBidPrice(index))
                  bidsize.append(quoteData.getBidSize(index))
                  askprices.append(quoteData.getAskPrice(index))
                  asksize.append(quoteData.getAskSize(index))

                  if pricechange:
                     bidprices[-1] = bidprices[-1] / priceFactors.loc[date,cfap]
                     askprices[-1] = askprices[-1] / priceFactors.loc[date,cfap]

                  if sharechange:
                     bidsize[-1] = int(bidsize[-1] * shareFactors.loc[date, cfas])
                     asksize[-1] = int(asksize[-1] * shareFactors.loc[date, cfas])

               BaseUtils.writeToBinQuotes(MyDirectories.getQuotesAdjDir() / date / (ticker + '_quotes.BinRQ'), \
                             [quoteData.getSecsFromEpocToMidn(), quoteData.getN()],\
                             [ts, bidsize, bidprices, asksize, askprices])            
            
         
   






    
