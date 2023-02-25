import MyDirectories
from FileManager import FileManager
import pandas as pd
import BaseUtils as bu
import statsmodels.api as sm

class TAQAutocorrelation():

    def __init__(self,date,ticker):
        self.data = bu.binToFrame(date,ticker) # bin_to_frame to be written later
        self.data = bu.weighted_average_price(self.data)


    def autocorrelation(self,freq,lags=1):
        for f in freq:
            return_freq = bu.cal_return(self.data,freq = f)
            lb_p = float(sm.stats.acorr_ljungbox(return_freq,lags=lags)['lb_pvalue'])
            if lb_p>0.05:
                
                return f
        print('No frequency in the list satisfies')
        return None 


    
        
class AutoCorrAll():
    BASE_DIR = MyDirectories.getAdjDir()
    fm = FileManager(BASE_DIR)

    def __init__(self,tickers,startdate,enddate,
        freq_list = ['20S','30S','1T','3T','5T','10T','20T'],lag_list=[1,2]):
        self.tickers = tickers
        self.date = self.fm.getTradeDates(startdate,enddate)
        self.freq_list = freq_list
        self.lag_list = lag_list

    def get_all_optimal_freq(self,record = True,record_file = 'noCorrFreq.txt'):
        for ticker in self.tickers:
            try:
                autoCorr = TAQAutocorrelation(self.date,ticker)
            except Exception as e:
                print(e)
            for lag in self.lag_list:
                optimal_f = autoCorr.autocorrelation(freq = self.freq_list,lags=lag)
                if record:
                    with open(record_file,mode = 'w') as f:
                        f.write(f'{ticker}, {lag}, {optimal_f}')
                        f.write('\n')
                        f.close()
                print(f'{ticker}, {lag}, {optimal_f}')
                






    
