from TAQCleaner import *
import unittest
import MyDirectories
from FileManager import FileManager
import BaseUtils
from matplotlib import pyplot as plt

class Test_TAQAdjust(unittest.TestCase):

    def test(self):

        fm1 = FileManager(MyDirectories.getAdjDir())
        fm2 = FileManager(MyDirectories.getCleanDir())
        # obj = TAQCleanTrades(k = 5, tau = 0.0005)
        # obj.cleanAllTrades(tickers = ['MTW'], dates = ['20070620','20070621'])
        # reader_before = fm1.getTradesFile( '20070620', 'MTW' )
        # reader_after = fm2.getTradesFile('20070620', 'MTW')
        # BaseUtils.plot_ba_price(reader_before, reader_after, "Trade cleaning for MTW")
        obj = TAQCleanQuotes(k = 60, tau = 0.0005)
        obj.cleanAllQuotes(tickers = ['GE'], dates = ['20070720','20070721'])
        reader_before = fm1.getQuotesFile( '20070720', 'GE' )
        reader_after = fm2.getQuotesFile('20070720', 'GE')
        print(reader_before.getN(), reader_after.getN())
        BaseUtils.plot_ba_bidp(reader_after, reader_before, "Bid cleaning for General Electric")
        BaseUtils.plot_ba_askp(reader_after, reader_before, "Ask cleaning for General Electric")
        plt.show()
        
if __name__ == "__main__":
    unittest.main()
