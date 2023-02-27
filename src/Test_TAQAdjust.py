from TAQAdjust import *
import unittest
import MyDirectories
from FileManager import FileManager
import BaseUtils
from matplotlib import pyplot as plt

class Test_TAQAdjust(unittest.TestCase):

    # test to check correct update logic
    def test(self):

        deltaForFloatComp = 0.001

        # initializing file manager for raw and adjusted data
        fm1 = FileManager(MyDirectories.getTAQDir())
        fm2 = FileManager(MyDirectories.getAdjDir())

        # object creation for trade adjustment
        obj = TAQAdjust(isquote=False)

        # need to initiallize tickers for all dates, else update would not be correct
        obj.adjustData(tickers = ['NVDA'])

        # get raw data
        reader_before = fm1.getTradesFile( '20070620', 'NVDA' )

        # get post adjustment data 
        reader_after = fm2.getTradesFile('20070620', 'NVDA')

        # price comparison before after adjustment
        self.assertAlmostEqual(
            reader_before.getPrice(0),
            reader_after.getPrice(0)*1.5,
            None, "Price adjustment failed",
            deltaForFloatComp
        )

        # size comparison before after adjustment
        self.assertEqual(
            int(reader_before.getSize(0) * 1.5),
            reader_after.getSize(0),
            "Volume adjustment failed"
        )

        # plot the two trades. Can check file in test_plot
        BaseUtils.plot_ba_trade(reader_before, reader_after, "Trade adjustment for NVIDIA", \
                                filename = MyDirectories.getTestPlotDir()/"test_trade_adjust.png")

        # check quote adjustment
        obj = TAQAdjust(isquote=True)

        # adjust data
        obj.adjustData(tickers = ['NVDA'])

        #get raw quotes file
        reader_before = fm1.getQuotesFile( '20070620', 'NVDA' )

        # get adjusted quotes file
        reader_after = fm2.getQuotesFile('20070620', 'NVDA')

        # bid comparison before after adjustment
        self.assertAlmostEqual(
            reader_before.getBidPrice(0),
            reader_after.getBidPrice(0)*1.5,
            None, "Bid Price adjustment failed",
            deltaForFloatComp
        )

        # bid size comparison before after adjustment
        self.assertEqual(
            int(reader_before.getBidSize(0)*1.5),
            reader_after.getBidSize(0),
            "Bid volume adjustment failed"
        )

        # ask comparison before after adjustment
        self.assertAlmostEqual(
            reader_before.getAskPrice(0),
            reader_after.getAskPrice(0)*1.5,
            None, "Ask Price adjustment failed",
            deltaForFloatComp
        )

        # ask size comparison before after adjustment
        self.assertEqual(
            int(reader_before.getAskSize(0)*1.5),
            reader_after.getAskSize(0),
            "Ask volume adjustment failed"
        )

        # plot bid and ask separately. Can check file in test_plot
        BaseUtils.plot_ba_bid(reader_before, reader_after, "Bid adjustment for NVIDIA",\
                              filename = MyDirectories.getTestPlotDir()/"test_bid_adjust.png")
        BaseUtils.plot_ba_ask(reader_before, reader_after, "Ask adjustment for NVIDIA",\
                              filename = MyDirectories.getTestPlotDir()/"test_ask_adjust.png")

        # show plot
        plt.show()
        
if __name__ == "__main__":
    unittest.main()
