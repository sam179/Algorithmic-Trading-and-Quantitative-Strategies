import BaseUtils
import MyDirectories
import pandas as pd
from TAQQuotesReader import TAQQuotesReader
from TAQTradesReader import TAQTradesReader
from FileManager import FileManager
import numpy as np
from ReturnBuckets import ReturnBuckets
from VWAP import VWAP
from TickTest import TickTest
import multiprocessing as mp
import itertools
import scipy.optimize as opt
from scipy import stats
import matplotlib.pyplot as plt
import os

class ImpactModel():
    def __init__(self, stocks = None, dates = None, window = 10, num_stocks=None):

        # Set default values for stocks and dates
        self._dates = BaseUtils.snp_dates
        self._stocks = set(BaseUtils.snp_tickers)

        # Set the default number of returns
        self.returns = 195

        # Override default values if user provides them
        if dates: self._dates = dates
        if num_stocks is not None:

            # Get the top num_stocks stocks based on file size
            tickers = []
            sizes = []
            dt = self._dates[0]
            fm = FileManager(MyDirectories.getTAQDir())
            for tic in fm.getTradeTickers(dt):
                tickers.append(tic)
                sizes.append(os.path.getsize(MyDirectories.getTradesDir()/ dt / (tic + '_trades.binRT')))

            sizes = np.array(sizes)
            tickers = np.array(tickers)
            idx = np.argsort(sizes)[-num_stocks:]
            tickers = tickers[idx]

            # Add these stocks to the set of stocks to be processed
            for e in tickers: self._stocks.add(e)

        # Convert the set of stocks to a list
        self._stocks = list(self._stocks)

        # Override default value if user provides it
        if stocks: self._stocks = stocks

        # Set the sliding window size for rolling calculations
        self.wd = window

    def processAllData(self):

        # Create empty dataframes to store the results
        mq = pd.DataFrame(index = self._dates,columns=self._stocks)
        mq2 = mq.copy()
        tvd = mq.copy()
        ap = mq.copy()
        imb = mq.copy()
        vwap330 = mq.copy()
        vwap400 = mq.copy()
        tp = mq.copy()

        # Create a multiprocessing pool to process the data for each stock and date in parallel
        pool = mp.Pool(processes=mp.cpu_count() - 2)
        results = [pool.apply_async(self.processData, args=(dt, st)) for dt in self._dates for st in self._stocks]
        pool.close()
        pool.join()

        # Retrieve the results from the pool and store them in the dataframes
        for res, (dt, st) in zip(results, itertools.product(self._dates,self._stocks)):
            mq.loc[dt, st], mq2.loc[dt, st], tvd.loc[dt, st], ap.loc[dt, st], \
            imb.loc[dt, st], vwap330.loc[dt, st], vwap400.loc[dt, st], tp.loc[dt, st] = res.get()

        # Clean the data by dropping dates and stocks with too many missing values
        d_dates, d_tickers = self.cleanData(mq,mq2,tvd,ap,imb,vwap330,vwap400,tp)

        # Calculate the volatility, x_v, h, average_daily_value, and daily_imbalance
        vol = -(mq.rolling(window=self.wd).sum().dropna()/self.returns/self.wd)**2 + mq2.rolling(window=self.wd).sum().dropna()/self.returns/self.wd
        vol = np.sqrt(vol*195)
        average_daily_value = 6*(tvd*vwap400).rolling(window=self.wd).sum().dropna()/self.wd/6.5
        daily_imbalance = (imb*vwap330).loc[vol.index]
        x_v = daily_imbalance/average_daily_value
        h =  ((vwap330 - ap) - (tp - ap)/2).loc[vol.index]

        # save the data to csv files for later use
        self.saveData(vol,x_v,h,average_daily_value,daily_imbalance,vwap400) 

        # return dropped dates and stocks
        return d_dates, d_tickers


    def cleanData(self,mq,mq2,tvd,ap,imb,vwap330,vwap400,tp):
        # clean output data
        count = mq.isnull().sum(axis=1)
        half_count = count > len(mq.columns)/2
        num_cols = len(mq.columns)

        # determine dropped dates nased on 1/2 threshold
        dropped_dates = mq.index[half_count]

        # drop same dates and stocks for all matrices
        mq.dropna(thresh=num_cols/2, inplace=True)
        dropped_stocks = mq.columns[mq.isnull().any()]
        mq.dropna(axis=1, how = 'any', inplace = True)

        mq2.dropna(thresh=num_cols/2, inplace=True)
        mq2.dropna(axis=1, how = 'any', inplace = True)

        tvd.dropna(thresh=num_cols/2, inplace = True)
        tvd.dropna(axis=1, how = 'any', inplace = True)

        ap.dropna(thresh=num_cols/2, inplace = True)
        ap.dropna(axis=1, how = 'any', inplace = True)

        imb.dropna(thresh=num_cols/2, inplace = True)
        imb.dropna(axis=1, how = 'any', inplace = True)

        vwap330.dropna(thresh=num_cols/2, inplace = True)
        vwap330.dropna(axis=1, how = 'any', inplace = True)

        vwap400.dropna(thresh=num_cols/2, inplace = True)
        vwap400.dropna(axis=1, how = 'any', inplace = True)

        tp.dropna(thresh=num_cols/2, inplace = True)
        tp.dropna(axis=1, how = 'any', inplace = True)

        return dropped_dates, dropped_stocks

    def processData(self, dt, st):

        try:
            # try loading the files
            quotes = TAQQuotesReader(MyDirectories.getQuotesDir()/ dt / (st + '_quotes.binRQ'))
            trades = TAQTradesReader(MyDirectories.getTradesDir()/ dt / (st + '_trades.binRT'))
        except:
            # return null values if files don't exist
            return pd.NA,pd.NA,pd.NA,pd.NA,pd.NA,pd.NA,pd.NA,pd.NA

        # 9:30, 3:30, 4:00 timestamps
        start930 = 19 * 60 * 60 * 1000 / 2
        end400 = 16 * 60 * 60 * 1000
        end330 = end400 - 1800000

        try:
            # try estimating all output
            vwap400 = VWAP(trades, start930, end400).getVWAP()
            vwap330 = VWAP(trades, start930, end330).getVWAP()
            tvd = 0

            # wrapper class for return buckets
            class midq:
                def __init__(self,quotes):
                    self._q = quotes

                def getTimestamp(self, i):
                    return self._q.getMillisFromMidn(i)
            
                def getPrice(self, i):
                    return (self._q.getBidPrice(i) + self._q.getAskPrice(i))/2
                
                def getN(self):
                    return self._q.getN()
                
            # return buckets for mid quotes
            mq = midq(quotes)
            returnBuckets = ReturnBuckets(mq, None, None, self.returns)

            # calculate x, xx series for vol estimation
            mqr = np.sum(np.array(returnBuckets._returns))
            mqrr = np.sum(np.array(returnBuckets._returns)**2)
            
            # get terminal and arrival prices
            ap = (mq.getPrice(0) + mq.getPrice(1) + mq.getPrice(2) + mq.getPrice(3) + mq.getPrice(4))/5
            tp = (mq.getPrice(mq.getN() - 1) + mq.getPrice(mq.getN() - 2) + mq.getPrice(mq.getN() - 3)\
                + mq.getPrice(mq.getN() - 4) + mq.getPrice(mq.getN() - 5))/5

            # estimate trade imbalance    
            tickTest = TickTest()
            classifications = tickTest.classifyAll(trades, start930, end400)
            imb = 0
            for i in range(0, trades.getN()):
                if trades.getTimestamp(i) < start930:
                    continue
                if trades.getTimestamp(i) >= end400:
                    break
                imb += trades.getSize(i) * classifications[i][2]
                tvd += trades.getSize(i)

            if vwap330 is None: raise("")

        except:
            # if fails then return null values
            print(f'This failed for stock : {st}, date : {dt}')
            return pd.NA,pd.NA,pd.NA,pd.NA,pd.NA,pd.NA,pd.NA,pd.NA

        return mqr, mqrr, tvd, ap, imb, vwap330, vwap400, tp
    
    def saveData(self,vol, x_v, h, adv,dimb,vwap):
        # save relevant data for reuse
        vol.to_csv(MyDirectories.getRecordDir() / 'vol.csv')
        x_v.to_csv(MyDirectories.getRecordDir() / 'x_v.csv')
        h.to_csv(MyDirectories.getRecordDir() / 'h.csv')
        adv.to_csv(MyDirectories.getRecordDir() / 'adv.csv')
        dimb.to_csv(MyDirectories.getRecordDir() / 'dimb.csv')
        vwap.to_csv(MyDirectories.getRecordDir() / 'vwap.csv')

    def getData(self):
        # get relevant data for regression analysis
        vol = pd.read_csv(MyDirectories.getRecordDir() / 'vol.csv', index_col=0)
        x_v = pd.read_csv(MyDirectories.getRecordDir() / 'x_v.csv', index_col=0)
        h = pd.read_csv(MyDirectories.getRecordDir() / 'h.csv', index_col=0)
        vwap = pd.read_csv(MyDirectories.getRecordDir() / 'vwap.csv', index_col=0)
        adv = pd.read_csv(MyDirectories.getRecordDir() / 'adv.csv', index_col=0)
        vwap = vwap.loc[h.index]
        adv = adv.loc[h.index]
        return vol,x_v,h,vwap,adv
    
    def nls(self, vol, x_v, h):
        # non-linear least squares
        # objective function
        def func(params,x_v,vol,h):
            return np.mean((np.sign(x_v)*params[0]*vol*(np.abs(x_v)**params[1]) - h)**2)

        # return fit result
        result = opt.minimize(func,[0.14,0.6],args=(x_v,vol,h),options={'maxiter' : 10000},tol = 1e-8)
        return result
    
    def getResid(self, params, x_v, vol, h):
        # get residual with given parameters
        return h - np.sign(x_v)*params[0]*vol*(np.abs(x_v)**params[1])

    # def robust_statisitcs(self, params, x_v, vol, h):
    #     resid = self.getResid(params,x_v,vol,h)
    #     e = params[0]
    #     b = params[1]
    #     mask = x_v != 0
    #     x_v = x_v[mask]
    #     resid = resid[mask]
    #     vol = vol[mask]
    #     resid = stats.zscore(resid)
    #     df = np.sign(x_v)*vol*np.array([e*(np.abs(x_v)**b)*np.log(np.abs(x_v)), (np.abs(x_v)**b)])
    #     dfsum = np.mean(np.array([[val[0]**2,val[1]**2] for val in df.T]), axis=0)
    #     dfe = resid*df
    #     dfesum = np.mean(np.array([[val[0]**2,val[1]**2] for val in dfe.T]), axis=0)
    #     vparams = np.sqrt(dfesum/(dfsum**2))
    #     return self.getTStats(vparams[1],vparams[0], e, b, len(resid) - 2)
        
    def getTStats(self,vare, varb, e, b, df):
        # get t-stats and p-values
        t_eta = e/vare
        t_beta = b/varb
        p_eta = stats.t.sf(abs(t_eta), df)
        p_beta = stats.t.sf(abs(t_beta), df)
        return t_eta, t_beta, p_eta, p_beta
    
    def generatePairs(self, combined):
        # sample from pairs and fit the model
        resampled_pairs = combined[np.random.randint(len(combined), size=len(combined)), :]
        return self.nls(resampled_pairs[:,0], resampled_pairs[:,1], resampled_pairs[:,2])
    
    def paired(self, vol, x_v, h, num_iter):
        # run paired bootstrap for robust error estimates
        combined = np.column_stack((vol,x_v,h))
        pool = mp.Pool(processes=mp.cpu_count()-2)
        results = [pool.apply_async(self.generatePairs, args=(combined,)) for _ in range(num_iter)]
        pool.close()
        pool.join()
        es = []
        bs = []
        for res in results:
           try:
                params = res.get()
           except:
               continue
           es.append(params.x[0])
           bs.append(params.x[1]) 

        es = np.array(es)
        bs = np.array(bs)
        t_e, t_b, p_e, p_b = self.getTStats(np.std(es), np.std(bs), np.mean(es), np.mean(bs), len(combined) - 2)
        return np.mean(es), np.mean(bs), t_e, t_b, p_e, p_b
        
    def generateResiduals(self, resid,vol,x_v, params):
        # sample from residual and fit the model
        resampled_resid = resid[np.random.randint(len(resid), size=len(resid))]
        h_rs = np.sign(x_v)*params[0]*vol*(np.abs(x_v)**params[1]) + resampled_resid
        return self.nls(vol,x_v,h_rs)
    
    def residual(self, vol, x_v, h, num_iter):
        # run paired bootstrap for robust error estimates
        params = self.nls(vol,x_v,h).x
        resid = self.getResid(params,x_v,vol,h)
        pool = mp.Pool(processes=mp.cpu_count()-2)
        results = [pool.apply_async(self.generateResiduals, args=(resid,vol,x_v,params,)) for _ in range(num_iter)]
        pool.close()
        pool.join()
        es = []
        bs = []
        for res in results:
            result = res.get()
            es.append(result.x[0])
            bs.append(result.x[1])

        es = np.array(es)
        bs = np.array(bs)
        t_e, t_b, p_e, p_b = self.getTStats(np.std(es), np.std(bs), np.mean(es), np.mean(bs), len(resid) - 2)
        return np.mean(es), np.mean(bs), t_e, t_b, p_e, p_b

    def qplot(self, resid, filename):
        # plot quantile-quantile plots of the residual
        fig,ax = plt.subplots(1)
        stats.probplot(resid, dist="norm", plot=ax)
        ax.set_title('Q-Q plot of the regression residuals')
        ax.set_xlabel('Theoretical quantiles')
        ax.set_ylabel('Sample quantiles')
        fig.savefig(filename)
    
    def residHist(self,resid,filename):
        # plot histogram of residuals
        fig,ax = plt.subplots(1)
        ax.hist(resid,bins=1000, range=(-3,3))
        ax.set_title('Residual Histogram')
        ax.set_xlabel('Frequency')
        ax.set_ylabel('Residual')
        fig.savefig(filename)

    def homoskedasticTest(self,resid,x_v,vol):
        # white's heteroskedacity test
        k = 2
        n = len(resid)
        X = np.column_stack((np.ones(n), x_v,vol))
        XX = np.dot(X.T, X)
        residuals_squared = resid**2
        UX = np.dot(residuals_squared, X)
        UX2 = np.dot(UX.T, UX)
        test_statistic = n * np.dot(UX.T, np.dot(np.linalg.inv(XX), UX)) / (residuals_squared.sum()**2)
        from scipy.stats import chi2
        p_value = 1 - chi2.cdf(test_statistic, k)
        return p_value

    def generalNLS(self, status='all', num_iter=1000):
        # fit regression for subset of data
        vol, x_v, h, _, adv = self.getData()
        row_sums = adv.sum()
        median = row_sums.median()

        if status == 'active':
           cols = adv.columns[row_sums > median] 
           vol = vol.loc[:,cols]
           x_v = x_v.loc[:,cols]
           h = h.loc[:,cols]

        elif status == 'inactive':
            cols = adv.columns[row_sums < median] 
            vol = vol.loc[:,cols]
            x_v = x_v.loc[:,cols]
            h = h.loc[:,cols]

        vol = vol.stack().values
        x_v = x_v.stack().values
        h = h.stack().values
        m1 = abs(stats.zscore(x_v)) < 30000
        m2 = abs(stats.zscore(h/vol)) < 10
        m3 = abs(stats.zscore(vol)) < 30000
        m4 = x_v != 0
        mask = m1&m2&m3&m4
        vol = vol[mask]
        x_v = x_v[mask]
        h = h[mask]
        self.runNLS(x_v,vol,h, status + '_',num_iter = num_iter)
        
    def runNLS(self,x_v,vol,h,title, num_iter = 1000):
        # combined run with bootstrap methods
        resNLS = self.nls(vol,x_v,h).x
        resid = self.getResid(resNLS,x_v,vol,h)
        p_value = self.homoskedasticTest(resid,x_v,vol)
        print(f"        NLS beta : {resNLS[1]}, eta : {resNLS[0]}, p_value from white's test : {p_value}")
        self.qplot(resid, MyDirectories.getRecordDir() / (title + 'qplot' + '.png'))
        self.residHist(resid, MyDirectories.getRecordDir()/ (title + 'hist' + '.png'))
        eta,beta,t_eta,t_beta, p_eta, p_beta = self.paired(vol, x_v, h, num_iter)
        print(f"    Paired bootstrap results for {num_iter} iterations : ")
        print(f"        NLS beta : {beta}, eta : {eta}, t_eta : {t_eta}, t_beta : {t_beta}, p_eta : {p_eta}, p_beta : {p_beta}")
        eta,beta,t_eta,t_beta, p_eta, p_beta = self.residual(vol, x_v, h, num_iter)
        print(f"    Residual bootstrap results for {num_iter} iterations : ")
        print(f"        NLS beta : {beta}, eta : {eta}, t_eta : {t_eta}, t_beta : {t_beta}, p_eta : {p_eta}, p_beta : {p_beta}")


        
        