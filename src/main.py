import warnings
warnings.filterwarnings("ignore")
import MyDirectories
import BaseUtils
from TAQAdjust import TAQAdjust
from TAQCleaner import TAQCleanTrades, TAQCleanQuotes
from FileManager import FileManager
# from TAQAutocorrelation import AutoCorrAll
from TAQCAPM import *
from ImpactModel import ImpactModel
import time
from CovEstimatorsFun import CovEstimators
import CovEstimatorsFun as cf
import matplotlib.pyplot as plt
from scipy import stats


if __name__ == "__main__":

    # # Set up file managers for input and output directories
    # fm1 = FileManager(MyDirectories.getTAQDir())
    # fm2 = FileManager(MyDirectories.getAdjDir())
    # fm3 = FileManager(MyDirectories.getCleanDir())

    # # Adjust the TAQ data for the NVDA stock
    # adjuster = TAQAdjust()
    # adjuster.adjustData()
    # adjuster = TAQAdjust(isquote=True)
    # adjuster.adjustData()

    # # Clean the trade and quote data for the JBL and TMO stocks on the specified dates
    # cleaner = TAQCleanTrades(k=50, tau=0.001)
    # cleaner.cleanAllTrades()
    # cleaner = TAQCleanQuotes(k=50, tau=0.001)
    # cleaner.cleanAllQuotes()

    # # Set up the tickers for which to compute the optimal frequency for autocorrelation adjustment
    # tickers_dirty = BaseUtils.snp_tickers
    # tickers_corr = fm2.getTradeTickers('20070622')
    # tickers_corr.remove('JBL')
    # tickers_corr.remove('TMO')

    # # # Compute the optimal frequency for autocorrelation adjustment for all tickers
    # # all = AutoCorrAll(tickers_corr, None, None)
    # # all.get_all_optimal_freq()

    # # Run the example optimization problem and print the gap tolerance for one of the lambdas
    # results = runExample()
    # print(f"The optimization tolerance for one of the lambdas is: {results[0]['gap']}")

    # # Compute the market portfolio turnover for the specified date range
    # obj = TAQCAPM()
    # turnover = obj.turnOver("20070620", "20070920")
    # print(f"The market portfolio turnover is {turnover*100}%")

    # tic = time.time()
    # imm = ImpactModel(window=10)
    # # d_dates, d_stocks = imm.processAllData()
    # # print(d_dates, d_stocks)
    # print("Regression run for all stocks")
    # imm.generalNLS(status='all', num_iter=1000)
    # print("Regression run for active stocks")
    # imm.generalNLS(status='active', num_iter=1000)
    # print("Regression run for inactive stocks")
    # imm.generalNLS(status='inactive', num_iter=1000)
    # print(f"Time taken = {(time.time() - tic)/60} minutes")

    ce = CovEstimators('returns.csv')

    for g_type in ["min_variance", "omniscient", "random"]:
        for cov_type in ['ewrm','empirical','clipped','optimalShrinkage']:
            if cov_type == 'empirical':
                avg_vol,std_vol,inSample_vol,inSample_std = ce.avg_variance(cov_type,g_type,inSample=True)
                print(f'{cov_type} {g_type} {avg_vol} {std_vol}')
                print(f'{cov_type} {g_type} inSample {inSample_vol} {inSample_std}')
            else:
                avg_vol,std_vol = ce.avg_variance(cov_type,g_type)
                print(f'{cov_type} {g_type} {avg_vol} {std_vol}')

            it = ce.induced_turnover(cov_type,g_type)
            print(f'{cov_type} {g_type} {it}')

            ce.visual_compare(cov_type,g_type)




