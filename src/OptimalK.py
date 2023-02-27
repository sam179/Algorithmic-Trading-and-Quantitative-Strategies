import MyDirectories
from FileManager import FileManager
import pandas as pd
import BaseUtils as bu
import statsmodels.api as sm
import scipy.stats as scps

def search_optimalK(df,k_list = [5,10,20,30,40,60,80],stationary_thres = 0.05):
    '''
    df must be a series coming from weight_average_price
    '''
    for k in k_list:
        standard = (df - df.rolling(k).mean())/df.rolling(k).std()
        p = scps.normaltest(standard,nan_policy = 'omit')[1]
        
        if p>stationary_thres:
            return k,p

        # p = (df - df.rolling(k).mean()).rolling(k).apply(
        #     lambda x:scps.normaltest(x,nan_policy = 'omit')[1]
        # )

        # if len(p[p>0.05])>=len(p)*stationary_thres:
        #     return k,len(p[p>0.05])/len(p)

    print('None in the list satisfies.')
    return None,None

class OptimalKAll():
    BASE_DIR = MyDirectories.getAdjDir()
    fm = FileManager(BASE_DIR)

    def __init__(self,tickers,startdate,enddate):
        self.tickers = tickers
        self.date = self.fm.getTradeDates(startdate,enddate)
        self.date.sort()
    
    def get_all_optimal_k(self,record=True,record_file = 'optimalK.txt'):
        for ticker in self.tickers:
            
            try:
                df = bu.weighted_average_price(bu.binToFrame(self.date,ticker))
                optimalK,r = search_optimalK(df)
                if record:
                    with open(record_file,mode = 'a') as f:
                        f.write(f'{ticker}, {optimalK},{r}')
                        f.write('\n')
                        f.close()
                print(f'{ticker}, {optimalK},{r}')
            except Exception as e:
                print(e)



            
