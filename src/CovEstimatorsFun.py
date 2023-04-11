import pandas as pd
import numpy as np
from sklearn.covariance import empirical_covariance
import pyRMT
from sklearn.model_selection import TimeSeriesSplit
import numpy as np

def min_var_weight(cov,test_set,n_stocks = 500,type = 'min_variance'):
    '''
    return weight of min variance portfolio
    cov: estimated covariance matrix
    test_set: already standarized test_set; df with time being index and tickers as column; return should be 5min returns
    n_stocks: number of stocks
    type: which type of g; choice of "min_variance","omniscient", and "random"
    '''
    cov = np.array(cov)
    test_set = np.array(test_set)
    if type == 'min_variance':
        g = np.ones(n_stocks)
    elif type == 'omniscient':
        g = (np.cumprod(1+test_set,axis = 1)[-1]-1) * np.sqrt(n_stocks)
    else:
        g = np.random.rand(n_stocks)
        g = (g/np.linalg.norm(g))* np.sqrt(n_stocks)

    return np.dot(cov,g)/(g@cov@g)



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


if __name__=="__main__":
    cov = np.random.rand(500,500)
    test_set = pd.DataFrame(np.random.rand(600,500))
    print(cov_cal(test_set,'optimalShrinkage'))
    print(min_var_weight(cov,test_set,500,type='random'))