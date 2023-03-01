import MyDirectories
from FileManager import FileManager
import pandas as pd
from collections import deque
from statistics import mean, stdev
import os
import BaseUtils
import numpy as np

class TAQCleanTrades():
    """Self suffiecent class for cleaning data
    """
    def __init__(self, k = 5, tau = 0.0005):
       # get adjusted directory
       self._fm = FileManager( MyDirectories.getAdjDir())
       self._k = k
       self._tau = tau

    # cleans all trade data
    def cleanAllTrades(self, dates = None, tickers = None):
        
        if not dates : dates = BaseUtils.default_dates
        if not tickers : tickers = list(BaseUtils.snp_tickers)
        
        # get dates
        Dates = self._fm.getTradeDates(list(dates)[0], list(dates)[1])
        for ticker in tickers:
            
            for date in Dates:
                
                # getting trade file
                try:
                    tradeData = self._fm.getTradesFile( date, ticker )
                except:
                    print(ticker, date, "FILE NOT FOUND")
                    continue

                # setting local dataframe for the records    
                N = tradeData.getN()
                data = pd.DataFrame({
                'time':pd.to_numeric(tradeData._ts),
                'Price':pd.to_numeric(tradeData._p),
                'Size':pd.to_numeric(tradeData._s)
                })
                
                # rolling window mean and std calculation
                data["mean"] = data["Price"].rolling(self._k,center=True).mean()
                data["std"] = data["Price"].rolling(self._k,center=True).std()

                # fixing beginning and end values
                if len(data)<self._k:
                    continue
                data.loc[N - self._k // 2  : , "mean"] = data["mean"].iloc[N-self._k//2 - 1]
                data.loc[ : self._k // 2 , "mean" ] = data["mean"].iloc[self._k//2]
                data.loc[N - self._k // 2 : , "std"] = data["std"].iloc[N - self._k//2 - 1]
                data.loc[ : self._k // 2 , "std"] = data["std"].iloc[self._k//2]

                # filtering out outliers
                data = data[ (abs(data["Price"] - data["mean"]) < 2*data["std"] + self._tau*data["mean"])]

                # write updated records to clean data directory
                BaseUtils.mkDir(MyDirectories.getTradesClDir() / date)
                BaseUtils.writeToBinTrades(MyDirectories.getTradesClDir() / date / (ticker + '_trades.binRT'), \
                           [tradeData.getSecsFromEpocToMidn(), len(data)],\
                           [data["time"].values.tolist(), data["Size"].values.tolist(), data["Price"].values.tolist()])         


class TAQCleanQuotes():
    """Self suffiecent class for cleaning data
    """

    def __init__(self, k = 5, tau = 0.0005):
       # get adjusted directory
       self._fm = FileManager( MyDirectories.getAdjDir())
       self._k = k
       self._tau = tau

    # cleans all quote data
    def cleanAllQuotes(self, dates = None, tickers = None):
        
        if not dates : dates = BaseUtils.default_dates
        if not tickers : tickers = BaseUtils.snp_tickers
       
        # get dates
        Dates = self._fm.getQuoteDates(dates[0], dates[1])
        for ticker in tickers:
            for date in Dates:

                # getting quotes file
                try:
                    quoteData = self._fm.getQuotesFile( date, ticker )
                except:
                    print(ticker, date, "FILE NOT FOUND")
                    continue
                 
                # setting local dataframe for the records  
                data = pd.DataFrame({
                'time':pd.to_numeric(quoteData._ts),
                'askPrice':pd.to_numeric(quoteData._ap),
                'askSize':pd.to_numeric(quoteData._as),
                'bidPrice':pd.to_numeric(quoteData._bp),
                'bidSize':pd.to_numeric(quoteData._bs)
                })

                # rolling window mean and std calculation
                N = quoteData.getN()
                data["meanbid"] = data["bidPrice"].rolling(self._k,center=True).mean()
                data["meanask"] = data["askPrice"].rolling(self._k, center=True).mean()
                data["stdbid"] = data["bidPrice"].rolling(self._k,center=True).std()
                data["stdask"] = data["askPrice"].rolling(self._k,center=True).std()

                # fixing beginning and end values
                data.loc[N - self._k // 2 : , "meanbid"] = data["meanbid"].iloc[N-self._k//2 - 1]
                data.loc[N - self._k // 2 : ,"meanask"] = data["meanask"].iloc[N-self._k//2 - 1]
                data.loc[: self._k // 2 ,"meanbid"] = data["meanbid"].iloc[self._k//2]
                data.loc[: self._k // 2 ,"meanask"] = data["meanask"].iloc[self._k//2]
                data.loc[N - self._k // 2 : ,"stdbid"] = data["stdbid"].iloc[N-self._k//2 - 1]
                data.loc[N - self._k // 2 : ,"stdask"] = data["stdask"].iloc[N-self._k//2 - 1]
                data.loc[: self._k // 2 ,"stdbid"] = data["stdbid"].iloc[self._k//2]
                data.loc[: self._k // 2 ,"stdask"] = data["stdask"].iloc[self._k//2]
                # filtering out outliers
                data = data[ ((abs(data["bidPrice"] - data["meanbid"]) < 2*data["stdbid"] + self._tau*data["meanbid"]) & \
                              (abs(data["askPrice"] - data["meanask"]) < 2*data["stdask"] + self._tau*data["meanask"]))]

                # write updated records to clean data directory
                BaseUtils.mkDir(MyDirectories.getQuotesClDir() / date)
                BaseUtils.writeToBinQuotes(MyDirectories.getQuotesClDir() / date / (ticker + '_quotes.binRQ'), \
                           [quoteData.getSecsFromEpocToMidn(), len(data)],\
                           [data["time"].values.tolist(), data["bidSize"].values.tolist(),\
                            data["bidPrice"].values.tolist(), data["askSize"].values.tolist(), \
                            data["askPrice"].values.tolist()])
                
                






    