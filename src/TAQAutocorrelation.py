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
        return None 
