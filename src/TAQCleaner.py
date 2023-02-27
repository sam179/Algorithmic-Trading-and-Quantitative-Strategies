import MyDirectories
from FileManager import FileManager
import pandas as pd
from collections import deque
from statistics import mean, stdev
import os
import BaseUtils

class TAQCleanTrades():
    """Self suffiecent class for cleaning data
    """
    
    def __init__(self, k = 5, tau = 0.0005):
       # get adjusted directory
       self._fm = FileManager( MyDirectories.getAdjDir())
       self._k = k
       self._tau = tau
       
       #deque for tracking window of size k
       self._price = deque([],maxlen=self._k)

    # updates parameters on update
    def setParams(self):
        self._mean = mean(self._price)
        self._std = stdev(self._price) 
        
    # outlier check rule
    def checkNotOutlier(self,price):
        return abs(price - self._mean) < 2*self._std + self._tau*self._mean

    # cleans all trade data
    def cleanAllTrades(self, dates = None, tickers = None):
        
        if not dates : dates = BaseUtils.default_dates
        if not tickers : tickers = BaseUtils.snp_tickers
       
        # get dates
        Dates = self._fm.getTradeDates(dates[0], dates[1])
        for ticker in tickers:
            
            for date in Dates:
                
                # get trades file
                prices = []
                shares = []
                ts = []
                try:
                    tradeData = self._fm.getTradesFile( date, ticker )
                except:
                    print(ticker, date, "FILE NOT FOUND")
                    continue
                
                # initialize tracker pointer to check correct records
                tracker = 0
                for index in range(tradeData.getN()):

                    # keep appending price till queue is full
                    if len(self._price) < self._k-1:
                       self._price.append(tradeData.getPrice(index))
                       continue
                    
                    # append data and set parameters
                    self._price.append(tradeData.getPrice(index))
                    self.setParams()

                    # if tracker is 0, check first k/2 records
                    if tracker == 0:
                       while(tracker <= (self._k // 2)):
                           if self.checkNotOutlier(tradeData.getPrice(tracker)): 
                              prices.append(tradeData.getPrice(tracker))
                              shares.append(tradeData.getSize(tracker))
                              ts.append(tradeData.getMillisFromMidn(tracker))
                           tracker += 1 
                       continue 
                    
                    # updates outliers with moving window
                    if self.checkNotOutlier(tradeData.getPrice(tracker)):
                        prices.append(tradeData.getPrice(tracker))
                        shares.append(tradeData.getSize(tracker))
                        ts.append(tradeData.getMillisFromMidn(tracker)) 

                    tracker += 1

                # checking end of file records
                while(tracker < tradeData.getN()):
                  if self.checkNotOutlier(tradeData.getPrice(tracker)): 
                     prices.append(tradeData.getPrice(tracker))
                     shares.append(tradeData.getSize(tracker))
                     ts.append(tradeData.getMillisFromMidn(tracker))
                  tracker += 1 

                # write updated records to clean data directory
                BaseUtils.mkDir(MyDirectories.getTradesClDir() / date)
                BaseUtils.writeToBinTrades(MyDirectories.getTradesClDir() / date / (ticker + '_trades.binRT'), \
                           [tradeData.getSecsFromEpocToMidn(), len(prices)],\
                           [ts, shares, prices])
                
                # clear the queue after the file is processed
                self._price.clear()                

class TAQCleanQuotes():
    """Self suffiecent class for cleaning data
    """
    
    def __init__(self, k = 5, tau = 0.0005):
       # get adjusted directory
       self._fm = FileManager( MyDirectories.getAdjDir())
       self._k = k
       self._tau = tau

       #deque for tracking window of size k for bid and ask
       self._price1 = deque([],maxlen=self._k)
       self._price2 = deque([],maxlen=self._k)

    # updates parameters on update
    def setParams(self):
        self._mean1 = mean(self._price1)
        self._std1 = stdev(self._price1)
        self._mean2 = mean(self._price2)
        self._std2 = stdev(self._price2) 

    # outlier check rule
    def checkNotOutlier(self,price,m,std):
        return abs(price - m) <= 2*std + self._tau*m

    # cleans all quote data
    def cleanAllQuotes(self, dates = None, tickers = None):
        
        if not dates : dates = BaseUtils.default_dates
        if not tickers : tickers = BaseUtils.snp_tickers
       
        # get dates
        Dates = self._fm.getQuoteDates(dates[0], dates[1])
        for ticker in tickers:
            for date in Dates:
                bidprices = []
                bidsize = []
                askprices = []
                asksize = []
                ts = []

                try:
                    quoteData = self._fm.getQuotesFile( date, ticker )
                except:
                    print(ticker, date, "FILE NOT FOUND")
                    continue

                tracker = 0
                # initialize tracker pointer to check correct records
                for index in range(quoteData.getN()):

                    # keep appending price till queue is full
                    if len(self._price1) < self._k-1:
                       self._price1.append(quoteData.getBidPrice(index))
                       self._price2.append(quoteData.getAskPrice(index))
                       continue

                    # append data and set parameters   
                    self._price1.append(quoteData.getBidPrice(index))
                    self._price2.append(quoteData.getAskPrice(index))
                    self.setParams()

                    # if tracker is 0, check first k/2 records and update bid ans ask
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
                    
                    # updates outliers with moving window
                    if self.checkNotOutlier(quoteData.getBidPrice(tracker), self._mean1,self._std1) and \
                        self.checkNotOutlier(quoteData.getAskPrice(tracker), self._mean2,self._std2): 
                        bidprices.append(quoteData.getBidPrice(tracker))
                        bidsize.append(quoteData.getBidSize(tracker))
                        ts.append(quoteData.getMillisFromMidn(tracker))
                        askprices.append(quoteData.getAskPrice(tracker))
                        asksize.append(quoteData.getAskSize(tracker))

                    tracker += 1

                # checking end of file records
                while(tracker < quoteData.getN()):
                    if self.checkNotOutlier(quoteData.getBidPrice(tracker), self._mean1,self._std1) and \
                        self.checkNotOutlier(quoteData.getAskPrice(tracker), self._mean2,self._std2): 
                        bidprices.append(quoteData.getBidPrice(tracker))
                        bidsize.append(quoteData.getBidSize(tracker))
                        ts.append(quoteData.getMillisFromMidn(tracker))
                        askprices.append(quoteData.getAskPrice(tracker))
                        asksize.append(quoteData.getAskSize(tracker))
                    tracker += 1 

                # write updated records to clean data directory
                BaseUtils.mkDir(MyDirectories.getQuotesClDir() / date)
                BaseUtils.writeToBinQuotes(MyDirectories.getQuotesClDir() / date / (ticker + '_quotes.binRQ'), \
                           [quoteData.getSecsFromEpocToMidn(), len(bidprices)],\
                           [ts, bidsize, bidprices, asksize, askprices])
                
                # clear the queue after the file is processed
                self._price1.clear()
                self._price2.clear()
                






    