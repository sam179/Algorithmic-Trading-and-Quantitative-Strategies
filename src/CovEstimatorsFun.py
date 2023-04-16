import pandas as pd
import numpy as np
from sklearn.covariance import empirical_covariance
import pyRMT
from sklearn.model_selection import TimeSeriesSplit
import numpy as np
from TrainTestSplit import TrainTestSplit
import MyDirectories 
import matplotlib.pyplot as plt

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
        #g = (np.cumprod(1+test_set,axis = 1)[-1]-1) * np.sqrt(n_stocks)
        g = np.array(np.mean(test_set,axis=0))
        #g = ((g)/np.std(g))
        g = (g/np.linalg.norm(g))* np.sqrt(n_stocks)
    else:
        g = np.random.rand(n_stocks)
        g = (g/np.linalg.norm(g))* np.sqrt(n_stocks)

    return np.dot(cov_inv, g)/(g.T @ cov_inv @ g)



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
        

    def avg_variance(self,cov_type,g_type,inSample=False):
        vol = []
        inSample_vol = []
        for i in range(self.sample_n):
            train_data = self.splitObj.get_train_set(i)
            test_data = self.splitObj.get_test_set(i)
            cov = cov_cal(train_data,type = cov_type)
            w = min_var_weight(cov,test_data,type = g_type)
            #cov_test = cov_cal(test_data,type = cov_type)
            #vol.append(np.sqrt((w.T @ cov_test @ w)*252*78))
            vol.append(np.sqrt(np.var(test_data@w)*252*78))
            if inSample:
                inSample_vol.append(np.sqrt(np.var(train_data@w)*252*78))
        if inSample:
            return np.mean(vol),np.std(vol),np.mean(inSample_vol),np.std(inSample_vol)
        return np.mean(vol),np.std(vol)


    def induced_turnover(self,cov_type,g_type):
        vol = []
        for i in range(self.sample_n):
            train_data = self.splitObj.get_train_set(i)
            test_data = self.splitObj.get_test_set(i)
            cov = cov_cal(train_data,type = cov_type)
            w = min_var_weight(cov,test_data,type = g_type)
            
            vol.append(np.sqrt(np.var(test_data@w)*252*78))
        vol = np.array(vol)
        vol_change = np.abs(vol[1:]-vol[:-1])/vol[:-1]
        return np.mean(vol_change)*6


    def visual_compare(self,cov_type,g_type,saveFile = True):
        vol = []
        real_vol = []
        
        for i in range(self.sample_n):
            train_data = self.splitObj.get_train_set(i)
            test_data = self.splitObj.get_test_set(i)
            train_cov = cov_cal(train_data,type = cov_type)
            test_cov = cov_cal(test_data,type = cov_type)
            train_w = min_var_weight(train_cov,test_data,type = g_type)
            test_w = min_var_weight(test_cov,test_data,type = g_type)
            #cov_test = cov_cal(test_data,type = cov_type)
            #vol.append(np.sqrt((w.T @ cov_test @ w)*252*78))
            vol.append(np.sqrt(np.var(test_data@train_w)*252*78))
            real_vol.append(np.sqrt(np.var(test_data@test_w)*252*78))
        e = np.mean((np.array(vol)-np.array(real_vol))**2)
        
        plt.plot(vol,label = 'estimated_vol',color = 'orange')
        plt.plot(real_vol,label = 'real_vol',color = 'blue')
        plt.legend()
        plt.suptitle(f'volatility comparison mse : {e} {cov_type} {g_type}')
        if saveFile:plt.savefig(MyDirectories.getRecordDir()/f'{cov_type}_{g_type}.jpg')

        return e
        





if __name__=="__main__":
    ce = CovEstimators('normalized_returns.csv')
    #ce.visual_compare('optimalShrinkage','omniscent')
    with open(MyDirectories.getRecordDir()/'covEstimatorResult.txt',mode='a') as f:
        f.write('induced turnovers')
        f.write('\n')
        for g_type in ['min_variance',"omniscient",'random']:
            for cov_type in ['empirical','clipped','optimalShrinkage']:
                # if cov_type == 'empirical':
                #     avg_vol,std_vol,inSample_vol,inSample_std = ce.avg_variance(cov_type,g_type,inSample=True)
                #     f.write(f'{cov_type} {g_type} {avg_vol} {std_vol}')
                #     f.write('\n')
                #     f.write(f'{cov_type} {g_type} inSample {inSample_vol} {inSample_std}')
                #     f.write('\n')
                #     print(f'{cov_type} {g_type} {avg_vol} {std_vol}')
                #     print(f'{cov_type} {g_type} inSample {inSample_vol} {inSample_std}')
                # else:
                #     avg_vol,std_vol = ce.avg_variance(cov_type,g_type)
                #     f.write(f'{cov_type} {g_type} {avg_vol} {std_vol}')
                #     f.write('\n')
                #     print(f'{cov_type} {g_type} {avg_vol} {std_vol}')
                it = ce.induced_turnover(cov_type,g_type)
                f.write(f'{cov_type} {g_type} {it}')
                f.write('\n')
                print(f'{cov_type} {g_type} {it}')

                
    f.close()