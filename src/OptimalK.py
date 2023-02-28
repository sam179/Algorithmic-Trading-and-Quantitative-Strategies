import MyDirectories
from FileManager import FileManager
import pandas as pd
import BaseUtils as bu
import statsmodels.api as sm
import scipy.stats as scps
import os

def search_optimalK(df,k_list = [20,30,40,60,80],stationary_thres = 0.80):
    '''
    df : [Series] must be a series with satetime index and price column
    k_list : [list] a list of k values to try with
    stationary_thres : [float] less than one; what percent of windows need to pass normal test
    '''
    for k in k_list:
        if len(df)<k:
            break
        # get rolling windows and perform normal test on each
        p = (df - df.rolling(k).mean()).rolling(k).apply(
            lambda x: scps.normaltest(x,nan_policy = 'omit')[1]
        )
        # return optimal k and ratio of satisfied window over total windpw
        if len(p[p>0.05])>=len(p)*stationary_thres:
            return k,len(p[p>0.05])/len(p)

    print('None in the list satisfies.')
    return None,None

class OptimalKAll():
    '''
    to find optimal k for a list of tickers
    '''
    BASE_DIR = MyDirectories.getCleanDir()
    fm = FileManager(BASE_DIR)

    def __init__(self,tickers,startdate,enddate):
        '''
        tickers:[list] a list of ticker symbols
        startdate:[string] startdate to get data
        enddate: [string] end date to get date; if None than 20070921
        '''
        self.tickers = tickers
        self.date = self.fm.getTradeDates(startdate,enddate)
        self.date.sort()
    
    def get_all_optimal_k(self,record=True,record_file = 'optimalK.txt',thres=0.8):
        filepath = os.getcwd()+'/record/'
        for ticker in self.tickers:
            
            try:
                df = bu.weighted_average_price(bu.binToFrame(self.date,
                ticker,baseDir=MyDirectories.getCleanDir()))
                optimalK,r = search_optimalK(df,stationary_thres=thres)
                if record:
                    with open(filepath+record_file,mode = 'a') as f:
                        f.write(f'{ticker}, {optimalK},{r}')
                        f.write('\n')
                        f.close()
                print(f'{ticker}, {optimalK},{r}')
            except Exception as e:
                print(e)



            
