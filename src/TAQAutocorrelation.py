import MyDirectories
from FileManager import FileManager
import pandas as pd
import BaseUtils as bu
import statsmodels.api as sm
import matplotlib.pyplot as plt
import os
from pathlib import Path

class TAQAutocorrelation():
    '''
    class to perform serial correlations of trade prices on a single stock
    '''

    def __init__(self,date,ticker):
        '''
        date : [list] a list of dates to get data
        ticker : [str] name of the ticker
        '''
        # get data and get weighted average price
        self.ticker = ticker
        self.date = date
        self.date.sort()
        self.data = bu.binToFrame(self.date,ticker,baseDir=MyDirectories.getCleanDir()) # bin_to_frame to be written later
        self.data = bu.weighted_average_price(self.data)


    def autocorrelation(self,freq,lags=1,plot=False):
        # loop over a list of frequency to find optimal parameter
        for f in freq:
            #calculate change in price in a given period
            self.return_freq = bu.cal_return(self.data,freq = f).dropna()
            # perform Ljung test
            lb_p = sm.stats.acorr_ljungbox(self.return_freq,lags=lags)['lb_pvalue']
            # make plots
            if plot:
                self.plot_autocorr(
                    f'{self.ticker} {self.date[-1]} {self.date[0]} {f} return [p:{lb_p[1]}]',
                    f'{self.ticker}_{f}_autocorr.jpg'
                    )
            # loop through different lag values and if p-value is bigger than 0.05 return
            for i in range(1,len(lb_p)+1):
                if lb_p[i]>0.05:
                    return f,i
                
        print('No frequency in the list satisfies')
        return None 

    def plot_autocorr(self,title,filename=None):

        # make plots and save
        fig,ax = plt.subplots()
        ax.plot(self.return_freq)
        ax.set_title(title)
        
        if filename: 
            filepath = MyDirectories.getTestPlotDir()
            fig.savefig(filepath/filename)





    
        
class AutoCorrAll():
    """
    Calculate autocorrelation for all 
    """
    BASE_DIR = MyDirectories.getCleanDir()
    fm = FileManager(BASE_DIR)

    def __init__(self,tickers,startdate,enddate,
        freq_list = ['10S','20S','30S','1T','3T','5T','10T','20T'],lags=1):
        '''
        tickers : [list] a list of symbols for analysis
        startdate : [String] if None then 20070621
        enddate : [String] if None thwn 20070921
        '''
        self.tickers = tickers
        self.date = self.fm.getTradeDates(startdate,enddate)
        self.freq_list = freq_list
        self.lags = lags

    def get_all_optimal_freq(self,record = True,record_file = 'noCorrFreq.txt'):
        for ticker in self.tickers:
            try:
                # find optimal frequency for each ticker
                autoCorr = TAQAutocorrelation(self.date,ticker)
                optimal_f,optimal_l = autoCorr.autocorrelation(freq = self.freq_list,lags=self.lags)
                # write results to a text file
                if record:
                    path = MyDirectories.getRecordDir()
                    
                    with open(path/record_file,mode = 'a') as f:
                        f.write(f'{ticker}, {optimal_l}, {optimal_f}')
                        f.write('\n')
                        f.close()
                print(f'{ticker}, {optimal_l}, {optimal_f}')
                    
            except Exception as e:
                print(e)
            
            
                






    
