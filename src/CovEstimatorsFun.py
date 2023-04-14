import pandas as pd
import numpy as np
from sklearn.covariance import empirical_covariance
import pyRMT
from sklearn.model_selection import TimeSeriesSplit
import numpy as np
from TrainTestSplit import TrainTestSplit
import MyDirectories 

def min_var_weight(cov,test_set,n_stocks = 499,type = 'min_variance'):
    '''
    return weight of min variance portfolio
    cov: estimated covariance matrix
    test_set: already standarized test_set; df with time being index and tickers as column; return should be 5min returns
    n_stocks: number of stocks
    type: which type of g; choice of "min_variance","omniscient", and "random"
    '''
    cov = np.array(cov)
    cov_inv = np.linalg.inv(cov)
    test_set = np.array(test_set)
    if type == 'min_variance':
        g = np.ones(n_stocks)
    elif type == 'omniscient':
        g = (np.cumprod(1+test_set,axis = 1)[-1]-1) * np.sqrt(n_stocks)
    else:
        g = np.random.rand(n_stocks)
        g = (g/np.linalg.norm(g))* np.sqrt(n_stocks)

    return np.dot(cov_inv,g)/(g.T@cov_inv@g)



def cov_cal(data,type = 'empirical'):
    '''
    return covaraince calcuated by given type
    data : dataframe or array; index = time, column = tickers
    type : string; choose from 'empirical','clipped','optimalShrinkage'
    '''
    data = np.array(data)
    if type == 'empirical':
        return empirical_covariance(data)

    elif type== "clipped":
        return pyRMT.clipped(data,return_covariance=True)

    else:
        return pyRMT.optimalShrinkage(data,return_covariance=True)

class CovEstimators():

    def __init__(self,filename,q=0.5):
        
        self.splitObj = TrainTestSplit(filename,q)
        self.splitObj.split()
        self.sample_n = self.splitObj.get_n()
        

    def avg_variance(self,cov_type,g_type):
        vol = []
        for i in range(self.sample_n):
            train_data = self.splitObj.get_train_set(i)
            test_data = self.splitObj.get_test_set(i)
            cov = cov_cal(train_data,type = cov_type)
            w = min_var_weight(cov,test_data,type = g_type)
            vol.append(np.sqrt(w.T@cov@w*252*78))
        return np.mean(vol),np.std(vol)



if __name__=="__main__":
    ce = CovEstimators('normalized_returns.csv')
    with open(MyDirectories.getRecordDir()/'covEstimatorResult.txt',mode='a') as f:
        for cov_type in ['empirical','clipped','optimalShrinkage']:
            for g_type in ["min_variance","omniscient","random"]:
                avg_vol,std_vol = ce.avg_variance(cov_type,g_type)
                f.write(f'{cov_type} {g_type} {avg_vol} {std_vol}')
                f.write('\n')
                print(f'{cov_type} {g_type} {avg_vol} {std_vol}')
    f.close()