import glob
from collections import deque

from src import MyDirectories


class FileNames(object):

    # The following are convenience methods for working with trade
    # files and dates. You don't need to use them. They're just
    # here ars examples.

    @staticmethod
    def getListOfBinRTFiles( dateDir ):
        # dateDir is the full path name of a particular sub-directory
        # containing *.binRT files - one per ticker - for one day of
        # data, e.g. "/Users/lee/TAQ/trades/20070620"
        return deque( glob.glob( "%s/*_trades.binRT" % dateDir ) )
    
    @staticmethod
    def getListOfBinRTDates( binRTTradesDir ):
        return deque( glob.glob( "%s/2007*" % binRTTradesDir ) )
    
    # The following are convenience methods for working with a merged
    # file format - all tickers and all dates in one giant file - 
    # that is used for running backtests. We won't be using these
    # until the very end of the semester.

    @staticmethod
    def getMergedDayOfTradesFile( dateDir ):
        # dateDir is the full path name of a particular sub-directory
        # containing one gzipped binary file with all trades for all
        # tickers for that day, e.g. BaseGZDir + "/trades/20070620/f1.gz9"
        return ( FileNames.getListOfGZTradeFiles( dateDir ) )[ 0 ]
    
    @staticmethod
    def getListOfGZTradeFiles( dateDir ):
        # dateDir is the full path name of a particular sub-directory
        # containing one gzipped binary file with all trades for all
        # tickers for that day, e.g. BaseGZDir + "/trades/20070620/f1.gz9"
        return deque( glob.glob( "%s/*.gz*" % dateDir ) )
    
    @staticmethod
    def getListOfGZTradeDates():
        return deque( glob.glob( "%s/2007*" % MyDirectories.getTradesDir() ) )
        
        
