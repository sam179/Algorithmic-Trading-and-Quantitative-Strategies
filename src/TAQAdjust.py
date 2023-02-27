import MyDirectories
from FileManager import FileManager
import pandas as pd
import BaseUtils
import shutil
from collections import deque
import os
cfap = 'Cumulative Factor to Adjust Prices'
cfas = 'Cumulative Factor to Adjust Shares/Vol' 
import numpy as np

class TAQAdjust():
   """Class to manage trade adjustment for corporate actions, the class is self contained
   """

   def __init__(self, isquote = False):
      """Initializer set isquote to true for quotes adjustment and false for trade adjustment
      """
      self._isquote = isquote
      # file manager to get raw data
      self._fm = FileManager( MyDirectories.getTAQDir())

   def adjustData(self, dates = None, tickers = None):
      """wraper function to call appropriate funtion

      Args:
          dates (string list, optional): A list with start and end dates, 
                                         if none all the dates will be taken for adjustment. Defaults to None.
          tickers (string list, optional): A list of tickers for adjustment, 
                                         if none all the tickers in S&P500 will be taken. Defaults to None.

      Returns:
          _type_: _description_
      """

      # delegation to appropriate function
      if self._isquote:
         return self.adjustAllQuotes(dates,tickers) 
      else:
         return self.adjustAllTrades(dates,tickers)

   def adjustAllTrades(self, dates = None, tickers = None):
      """Adjusts all trades as per the inputs

      Args:
          dates (string list, optional): A list with start and end dates, 
                                         if none all the dates will be taken for adjustment. Defaults to None.
          tickers (string list, optional): A list of tickers for adjustment, 
                                         if none all the tickers in S&P500 will be taken. Defaults to None.
      """
      # sets appropriate parameters
      if not dates : dates = BaseUtils.default_dates
      if not tickers : tickers = BaseUtils.snp_tickers

      # get trade dates 
      Dates = self._fm.getTradeDates(dates[0], dates[1])


      for ticker in tickers:

         # Extracting information about adjustment factors form S&P500 file   
         priceFactors = BaseUtils.snp.loc[BaseUtils.snp['Ticker Symbol'] == ticker, ['Names Date', cfap]].set_index("Names Date")
         shareFactors = BaseUtils.snp.loc[BaseUtils.snp['Ticker Symbol'] == ticker, ['Names Date', cfas]].set_index("Names Date")

         # checks if last dates' and first dates' factors are same as no adjustment is required in that case
         pricechange = priceFactors.iloc[0, 0] != priceFactors.iloc[-1, 0]
         sharechange = shareFactors.iloc[0, 0] != shareFactors.iloc[-1, 0]

         # getting trade files for each date
         for date in Dates:

            # creates directory for storing adjusted files
            BaseUtils.mkDir(MyDirectories.getTradesAdjDir() / date)


            try:
               # case were there is no change and files are copied form raw directory to the new one
               if (not pricechange) and (not sharechange):
                     shutil.copy(MyDirectories.getTradesDir() / date / (ticker + '_trades.BinRT'), \
                                 MyDirectories.getTradesAdjDir() / date /"")
                     continue
               else:
                  #elose gets trade file from raw directory
                  tradeData = self._fm.getTradesFile( date, ticker )

            except:
               # file not found
               print(ticker, date, "FILE NOT FOUND")
               continue

            # storing data in loacal variable
            ts = tradeData._ts
            prices = np.array(tradeData._p)
            shares = np.array(tradeData._s)

            # updating data with adjustments
            if pricechange: prices /= priceFactors.loc[date,cfap]
            if sharechange: shares = (shares * shareFactors.loc[date, cfas]).astype(int)

            # writes the updated data to the new directory
            BaseUtils.writeToBinTrades(MyDirectories.getTradesAdjDir() / date / (ticker + '_trades.BinRT'), \
                        [tradeData.getSecsFromEpocToMidn(), tradeData.getN()],\
                        [ts, shares.tolist(), prices.tolist()])  


   def adjustAllQuotes(self, dates = None, tickers = None):
      """Adjusts all quotes as per the inputs

      Args:
          dates (string list, optional): A list with start and end dates, 
                                         if none all the dates will be taken for adjustment. Defaults to None.
          tickers (string list, optional): A list of tickers for adjustment, 
                                         if none all the tickers in S&P500 will be taken. Defaults to None.
      """

      # sets appropriate parameters
      if not dates : dates = BaseUtils.default_dates
      if not tickers : tickers = BaseUtils.snp_tickers
         
      # get trade dates 
      Dates = self._fm.getQuoteDates(dates[0], dates[1])

      for ticker in tickers:
         # Extracting information about adjustment factors form S&P500 file  
         priceFactors = BaseUtils.snp.loc[BaseUtils.snp['Ticker Symbol'] == ticker, ['Names Date', cfap]].set_index("Names Date")
         shareFactors = BaseUtils.snp.loc[BaseUtils.snp['Ticker Symbol'] == ticker, ['Names Date', cfas]].set_index("Names Date")

         # checks if last dates' and first dates' factors are same as no adjustment is required in that case
         pricechange = priceFactors.iloc[0, 0] != priceFactors.iloc[-1, 0]
         sharechange = shareFactors.iloc[0, 0] != shareFactors.iloc[-1, 0]

         for date in Dates:
            # creates directory for storing adjusted files
            BaseUtils.mkDir(MyDirectories.getQuotesAdjDir() / date)
            try:
               #  case were there is no change and files are copied form raw directory to the new one
               if (not pricechange) and (not sharechange):
                  shutil.copy(MyDirectories.getQuotesDir() / date / (ticker + '_quotes.BinRQ'), MyDirectories.getQuotesAdjDir() / date /"")
                  continue
               else:
                  #else gets quote file from raw directory
                  quoteData = self._fm.getQuotesFile( date, ticker )
            except:
               # file not found
               print(ticker, date, "FILE NOT FOUND")
               continue

            # storing data in loacal variable   
            ts = quoteData._ts
            bidprices = np.array(quoteData._bp)
            bidsize = np.array(quoteData._bs)
            askprices = np.array(quoteData._ap)
            asksize = np.array(quoteData._as)

            # updating data with adjustments
            if pricechange: 
               bidprices /= priceFactors.loc[date,cfap]
               askprices /= priceFactors.loc[date,cfap]
            if sharechange: 
               bidsize = (bidsize * shareFactors.loc[date, cfas]).astype(int)
               asksize = (asksize * shareFactors.loc[date, cfas]).astype(int)

            # writes the updated data to the new directory
            BaseUtils.writeToBinQuotes(MyDirectories.getQuotesAdjDir() / date / (ticker + '_quotes.BinRQ'), \
                           [quoteData.getSecsFromEpocToMidn(), quoteData.getN()],\
                           [ts, bidsize.tolist(), bidprices.tolist(), asksize.tolist(), askprices.tolist()])            
         
      
   






    
