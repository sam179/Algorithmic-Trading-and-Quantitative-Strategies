import MyDirectories
import BaseUtils
from TAQAdjust import TAQAdjust
from OptimalK import OptimalKAll
from TAQCleaner import TAQCleanTrades, TAQCleanQuotes
from FileManager import FileManager
from TAQAutocorrelation import AutoCorrAll
from TAQCAPM import *


if __name__ == "__main__":

    # Set up file managers for input and output directories
    fm1 = FileManager(MyDirectories.getTAQDir())
    fm2 = FileManager(MyDirectories.getAdjDir())
    fm3 = FileManager(MyDirectories.getCleanDir())

    # Adjust the TAQ data for the NVDA stock
    adjuster = TAQAdjust()
    adjuster.adjustData(tickers = ['NVDA'])
    adjuster = TAQAdjust(isquote=True)
    adjuster.adjustData(tickers = ['NVDA'])

    # Clean the trade and quote data for the JBL and TMO stocks on the specified dates
    cleaner = TAQCleanTrades(k=50, tau=0.001)
    cleaner.cleanAllTrades(dates=['20070622', '20070623'], tickers=['JBL', 'TMO'])
    cleaner = TAQCleanQuotes(k=50, tau=0.001)
    cleaner.cleanAllQuotes(dates=['20070622', '20070623'], tickers=['JBL', 'TMO'])

    # Set up the tickers for which to compute the optimal frequency for autocorrelation adjustment
    tickers_dirty = BaseUtils.snp_tickers
    tickers_corr = fm2.getTradeTickers('20070622')
    tickers_corr.remove('JBL')
    tickers_corr.remove('TMO')

    # Compute the optimal frequency for autocorrelation adjustment for all tickers
    all = AutoCorrAll(tickers_corr, None, None)
    all.get_all_optimal_freq()

    # Run the example optimization problem and print the gap tolerance for one of the lambdas
    results = runExample()
    print(f"The optimization tolerance for one of the lambdas is: {results[0]['gap']}")

    # Compute the market portfolio turnover for the specified date range
    obj = TAQCAPM()
    turnover = obj.turnOver("20070620", "20070920")
    print(f"The market portfolio turnover is {turnover*100}%")





