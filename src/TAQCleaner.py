import MyDirectories
from FileManager import FileManager
import pandas as pd
import BaseUtils as bu
from collections import deque
from statistics import mean, stdev
import os

class TAQCleanTrades():
    
    def __init__(self, k = 5, tau = 0.0005):
       self._fm = FileManager( MyDirectories.getAdjDir())
       self._snp = bu.readExcel(MyDirectories.getTAQDir() / "s&p500.csv").dropna()
       self._k = k
       self._tau = tau
       self._price = deque([],maxlen=self._k)

    def setParams(self):
        self._mean = mean(self._price)
        self._std = stdev(self._price) 
        
    def checkNotOutlier(self,price):
        return abs(price - self._mean) < 2*self._std + self._tau*self._mean

    def cleanAllTrades(self, dates = None, tickers = None):
        
        if dates == None:
           dates = [bu.startDate, bu.endDate]

        if tickers == None:
           tickers =  set(self._snp['Ticker Symbol'].dropna().to_list())
       
        Dates = self._fm.getTradeDates(dates[0], dates[1])
        for ticker in tickers:
            
            for date in Dates:
                prices = []
                shares = []
                ts = []

                if not os.path.isdir(MyDirectories.getTradesClDir() / date):
                     os.makedirs(MyDirectories.getTradesClDir() / date)

                tradeData = self._fm.getTradesFile( date, ticker )
                tracker = 0
                for index in range(tradeData.getN()):

                    if len(self._price) < self._k-1:
                       self._price.append(tradeData.getPrice(index))
                       continue
                    
                    self._price.append(tradeData.getPrice(index))
                    self.setParams()

                    if tracker == 0:
                       while(tracker <= (self._k // 2)):
                           if self.checkNotOutlier(tradeData.getPrice(tracker)): 
                              prices.append(tradeData.getPrice(tracker))
                              shares.append(tradeData.getSize(tracker))
                              ts.append(tradeData.getMillisFromMidn(tracker))
                           tracker += 1 
                       continue 
                    
                    if self.checkNotOutlier(tradeData.getPrice(tracker)):
                        prices.append(tradeData.getPrice(tracker))
                        shares.append(tradeData.getSize(tracker))
                        ts.append(tradeData.getMillisFromMidn(tracker)) 

                    tracker += 1

                while(tracker < tradeData.getN()):
                  if self.checkNotOutlier(tradeData.getPrice(tracker)): 
                     prices.append(tradeData.getPrice(tracker))
                     shares.append(tradeData.getSize(tracker))
                     ts.append(tradeData.getMillisFromMidn(tracker))
                  tracker += 1 
               
                bu.writeToBinTrades(MyDirectories.getTradesClDir() / date / (ticker + '_trades.BinRT'), \
                           [tradeData.getSecsFromEpocToMidn(), len(prices)],\
                           [ts, shares, prices])
                
                self._price.clear()                

class TAQCleanQuotes():

    def __init__(self, k = 5, tau = 0.0005):
       self._fm = FileManager( MyDirectories.getAdjDir())
       self._snp = bu.readExcel(MyDirectories.getTAQDir() / "s&p500.csv").dropna()
       self._k = k
       self._tau = tau
       self._price1 = deque([],maxlen=self._k)
       self._price2 = deque([],maxlen=self._k)

    def setParams(self):
        self._mean1 = mean(self._price1)
        self._std1 = stdev(self._price1)

        self._mean2 = mean(self._price2)
        self._std2 = stdev(self._price2) 

    def checkNotOutlier(self,price,m,std):
        return abs(price - m) <= 2*std + self._tau*m

    def cleanAllQuotes(self, dates = None, tickers = None):
        
        if dates == None:
           dates = [bu.startDate, bu.endDate]

        if tickers == None:
           tickers =  set(self._snp['Ticker Symbol'].dropna().to_list())
       
        Dates = self._fm.getQuoteDates(dates[0], dates[1])
        for ticker in tickers:
            
            for date in Dates:
                bidprices = []
                bidsize = []
                askprices = []
                asksize = []
                ts = []

                if not os.path.isdir(MyDirectories.getQuotesClDir() / date):
                     os.makedirs(MyDirectories.getQuotesClDir() / date)

                quoteData = self._fm.getQuotesFile( date, ticker )
                tracker = 0
                for index in range(quoteData.getN()):

                    if len(self._price1) < self._k-1:
                       self._price1.append(quoteData.getBidPrice(index))
                       self._price2.append(quoteData.getAskPrice(index))
                       continue

                    self._price1.append(quoteData.getBidPrice(index))
                    self._price2.append(quoteData.getAskPrice(index))
                    self.setParams()

                    if tracker == 0:
                       while(tracker < (self._k // 2)):
                           if self.checkNotOutlier(quoteData.getBidPrice(tracker), self._mean1,self._std1) and \
                              self.checkNotOutlier(quoteData.getAskPrice(tracker), self._mean2,self._std2): 
                              bidprices.append(quoteData.getBidPrice(tracker))
                              bidsize.append(quoteData.getBidSize(tracker))
                              ts.append(quoteData.getMillisFromMidn(tracker))
                              askprices.append(quoteData.getAskPrice(tracker))
                              asksize.append(quoteData.getAskSize(tracker))
                           tracker += 1 
                    
                    if self.checkNotOutlier(quoteData.getBidPrice(tracker), self._mean1,self._std1) and \
                        self.checkNotOutlier(quoteData.getAskPrice(tracker), self._mean2,self._std2): 
                        bidprices.append(quoteData.getBidPrice(tracker))
                        bidsize.append(quoteData.getBidSize(tracker))
                        ts.append(quoteData.getMillisFromMidn(tracker))
                        askprices.append(quoteData.getAskPrice(tracker))
                        asksize.append(quoteData.getAskSize(tracker))

                    tracker += 1

                while(tracker < quoteData.getN()):
                  if self.checkNotOutlier(quoteData.getBidPrice(tracker), self._mean1,self._std1) and \
                     self.checkNotOutlier(quoteData.getAskPrice(tracker), self._mean2,self._std2): 
                     bidprices.append(quoteData.getBidPrice(tracker))
                     bidsize.append(quoteData.getBidSize(tracker))
                     ts.append(quoteData.getMillisFromMidn(tracker))
                     askprices.append(quoteData.getAskPrice(tracker))
                     asksize.append(quoteData.getAskSize(tracker))
                  tracker += 1 
               
                bu.writeToBinQuotes(MyDirectories.getQuotesClDir() / date / (ticker + '_quotes.BinRQ'), \
                           [quoteData.getSecsFromEpocToMidn(), len(bidprices)],\
                           [ts, bidsize, bidprices, asksize, askprices])
                
                self._price1.clear()
                self._price2.clear()
                






    