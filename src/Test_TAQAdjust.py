from TAQAdjust import *
import unittest
import MyDirectories
from FileManager import FileManager
import BaseUtils
from matplotlib import pyplot as plt

class Test_TAQAdjust(unittest.TestCase):

    def test(self):

        fm1 = FileManager(MyDirectories.getTAQDir())
        fm2 = FileManager(MyDirectories.getAdjDir())
        # obj = TAQAdjust(isquote=False)
        # obj.adjustData(tickers = ['NVDA'])
        reader_before = fm1.getTradesFile( '20070620', 'NVDA' )
        reader_after = fm2.getTradesFile('20070620', 'NVDA')
        BaseUtils.plot_ba_trade(reader_before, reader_after, "Trade adjustment for NVIDIA")
        # obj = TAQAdjust(isquote=True)
        # obj.adjustData(tickers = ['NVDA'])
        reader_before = fm1.getQuotesFile( '20070620', 'NVDA' )
        reader_after = fm2.getQuotesFile('20070620', 'NVDA')
        BaseUtils.plot_ba_bid(reader_before, reader_after, "Bid adjustment for NVIDIA")
        BaseUtils.plot_ba_ask(reader_before, reader_after, "Ask adjustment for NVIDIA")
        plt.show()
        
if __name__ == "__main__":
    unittest.main()
