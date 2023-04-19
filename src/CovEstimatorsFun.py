import pandas as pd
import numpy as np
from sklearn.covariance import empirical_covariance
import pyRMT
from sklearn.model_selection import TimeSeriesSplit
import numpy as np
from TrainTestSplit import TrainTestSplit
import MyDirectories 
import matplotlib.pyplot as plt
from FileManager import FileManager
import BaseUtils


def test_period_return(test_set):
    fm = FileManager(MyDirectories.getCleanDir())
    def indexToDate(index):
        dates = fm.getTradeDates('20070620','20070930')
        dates.sort()
        millisToMidn = [16 * 60 * 60 * 1000]+list(range(int(18 * 60 * 60 * 1000 / 2),
                                                        int(16 * 60 * 60 * 1000) ,78))
        day = dates[3] #dates[index//(78)]
        millis = millisToMidn[index%78]
        return day,millis
    
    def getPrice(day,millis,ticker):
        qReader = fm.getTradesFile(day,ticker)    # change later
        for i in range(qReader.getN()):
            if qReader.getMillisFromMidn(i)>=millis:
                price = qReader.getPrice(i)
                return price
            else:
                return 0
    
    tickers = test_set.columns
    startD,startM = indexToDate(test_set.index[0])
    endD,endM = indexToDate(test_set.index[-1])
    r = []
    #startP,endP = []
    for ticker in tickers:
        # startP.append(getPrice(startD,startM,ticker))
        # endP.append(getPrice(endD,endM,ticker))
        if getPrice(startD,startM,ticker)!=0:
            r.append(getPrice(endD,endM,ticker)/getPrice(startD,startM,ticker) -1)
    return r
        

def min_var_weight(cov,test_set,n_stocks = 502,type = 'min_variance'):
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
        r = (np.cumprod(1+test_set,axis = 1)[-1]-1) 
        g = r* np.sqrt(n_stocks)
        #g = np.array(np.mean(test_set,axis=0))
        #g = ((g)/np.std(g))
        #g = g*np.sqrt(n_stocks)#(g/np.linalg.norm(g))* np.sqrt(n_stocks)
        # r = test_period_return(test_set)
        # g = r/np.std(r) *np.sqrt(n_stocks)
    else:
        g = np.random.rand(n_stocks)
        g = (g/np.linalg.norm(g))* np.sqrt(n_stocks)

    return np.dot(cov_inv, g)/(g.T @ cov_inv @ g)

def ewrm_estimator(data, alpha=0.94):
    """
    Computes the Exponentially Weighted Random Matrices estimator for a given set of data.
    """
    
    # Loop through the data and compute the EWRM estimator
    for i in range(len(data)):
        if i == 0:
            cov_matrix = 1/len(data)*alpha * np.outer(data[i], data[i])
        else:
            # Update the covariance matrix with the new data point
            cov_matrix = (1-alpha) * np.outer(data[i], data[i]) + (alpha) * cov_matrix


    return cov_matrix 

def cov_cal(data,type = 'empirical'):
    '''
    return covaraince calcuated by given type
    data : dataframe or array; index = time, column = tickers
    type : string; choose from 'empirical','clipped','optimalShrinkage'
    '''
    data = np.array(data)
    if len(data)>0:
        if type == 'empirical':
            return empirical_covariance(data)

        elif type== "clipped":
            return pyRMT.clipped(data,return_covariance=True)

        elif type=='optimalShrinkage':
            return pyRMT.optimalShrinkage(data,return_covariance=True)
        
        elif type=='ewrm':
            return ewrm_estimator(data)
        else:
            print('type is not valid.')
    else:
        return None

class CovEstimators():

    def __init__(self,filename,q=0.5):
        
        self.splitObj = TrainTestSplit(filename,q)
        self.splitObj.split()
        self.sample_n = self.splitObj.get_n()

    def avg_variance(self,cov_type,g_type,inSample=False):
        'Calculate the average volatility across the folds'
        vol = []
        inSample_vol = []
        for i in range(self.sample_n):
            train_data = self.splitObj.get_train_set(i)
            test_data = self.splitObj.get_test_set(i)
            cov = cov_cal(train_data,type = cov_type)
            w = min_var_weight(cov,test_data,type = g_type,n_stocks=len(test_data.columns))
            #cov_test = cov_cal(test_data,type = cov_type)
            #vol.append(np.sqrt((w.T @ cov_test @ w)*252*78))
            vol.append(np.sqrt(np.var(test_data@w)*252*78))
            if inSample:
                inSample_vol.append(np.sqrt(np.var(train_data@w)*252*78))
        if inSample:
            return np.mean(vol),np.std(vol),np.mean(inSample_vol),np.std(inSample_vol)
        return np.mean(vol),np.std(vol)


    def induced_turnover(self,cov_type,g_type):
        "calculate the induced turnover"
        vol = []
        # only using the first group as test
        train_data = self.splitObj.get_train_set(0)
        test_data = self.splitObj.get_test_set(0)
        cov = cov_cal(train_data,type = cov_type)
        w = min_var_weight(cov,test_data,type = g_type,n_stocks=len(test_data.columns))
        for i in range(self.sample_n):
            test_data = self.splitObj.get_test_set(i)
            vol.append(np.sqrt(np.var(test_data@w)*252*78))
        vol = np.array(vol)
        vol_change = np.abs(vol[1:]-vol[:-1])/vol[:-1]
        return np.mean(vol_change)*6


    def visual_compare(self,cov_type,g_type,saveFile = True):
        'generate visual compare'
        vol = []
        real_vol = []
        train_data = self.splitObj.get_train_set(0)
        full_data = self.splitObj.data
        train_cov = cov_cal(train_data,type = cov_type)
        test_cov = cov_cal(full_data,type = cov_type)
        for i in range(self.sample_n):
            
            test_data = self.splitObj.get_test_set(i)
            
            train_w = min_var_weight(train_cov,test_data,type = g_type)
            test_w = min_var_weight(test_cov,test_data,type = g_type)
            #cov_test = cov_cal(test_data,type = cov_type)
            #vol.append(np.sqrt((w.T @ cov_test @ w)*252*78))
            vol.append(np.sqrt(np.var(test_data@train_w)*252*78))
            real_vol.append(np.sqrt(np.var(test_data@test_w)*252*78))
        e = np.mean((np.array(vol)-np.array(real_vol))**2)
        plt.cla()
        plt.plot(vol,label = 'estimated_vol',color = 'orange')
        plt.plot(real_vol,label = 'real_vol',color = 'blue')
        plt.ylim(0,0.38)
        plt.legend()
        
        plt.suptitle(f'volatility comparison mse : {e} {cov_type} {g_type}')
        if saveFile:plt.savefig(MyDirectories.getRecordDir()/f'{cov_type}_{g_type}.jpg')

        return e
        





# if __name__=="__main__":
    # ce = CovEstimators('returns.csv')
    # #ce.visual_compare('optimalShrinkage','omniscent')
    # with open(MyDirectories.getRecordDir()/'covEstimatorResult.txt',mode='a') as f:
    #     # f.write('induced turnovers')
    #     # f.write('\n')
    #     for g_type in ["min_variance"]:#,"omniscient","random"]:
    #         for cov_type in ['ewrm','empirical','clipped','optimalShrinkage']:
    #             # if cov_type == 'empirical':
    #             #     avg_vol,std_vol,inSample_vol,inSample_std = ce.avg_variance(cov_type,g_type,inSample=True)
    #             #     f.write(f'{cov_type} {g_type} {avg_vol} {std_vol}')
    #             #     f.write('\n')
    #             #     f.write(f'{cov_type} {g_type} inSample {inSample_vol} {inSample_std}')
    #             #     f.write('\n')
    #             #     print(f'{cov_type} {g_type} {avg_vol} {std_vol}')
    #             #     print(f'{cov_type} {g_type} inSample {inSample_vol} {inSample_std}')
    #             # else:
    #             #     avg_vol,std_vol = ce.avg_variance(cov_type,g_type)
    #             #     f.write(f'{cov_type} {g_type} {avg_vol} {std_vol}')
    #             #     f.write('\n')
    #             #     print(f'{cov_type} {g_type} {avg_vol} {std_vol}')
            
    #             # it = ce.induced_turnover(cov_type,g_type)
    #             # f.write(f'{cov_type} {g_type} {it}')
    #             # f.write('\n')
    #             # print(f'{cov_type} {g_type} {it}')

    #             ce.visual_compare(cov_type,g_type)

                
    # f.close()