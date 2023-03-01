from TAQCleaner import *
import unittest
import MyDirectories
from FileManager import FileManager
import BaseUtils
from matplotlib import pyplot as plt

class Test_TAQAdjust(unittest.TestCase):

    # test to check correct implementatin of trades filtering
    def test1(self):

        # setting up fake trade file
        fm2 = FileManager(MyDirectories.getCleanDir())
        BaseUtils.writeToBinTrades(MyDirectories.getAdjDir()/ "trades" / '20070620' / ('test' + '_trades.binRT'), \
                           [2020, 7],\
                           [[1,2,3,4,5,6,7],\
                            [1,2,3,4,5,6,7], \
                            [1,1,1,14,1,1,2]]) 
        
        # cleaning trade data
        obj = TAQCleanTrades(k=6,tau=0.0005)
        obj.cleanAllTrades(tickers = ["test"], dates = ['20070620','20070621'])

        # getting cleaned data
        reader = fm2.getTradesFile('20070620', 'test')

        # assertions on cleaned data

        self.assertListEqual(list(reader._p), [1,1,1,1,1,2])
        self.assertListEqual(list(reader._s),[1,2,3,5,6,7])
        self.assertListEqual(list(reader._ts), [1,2,3,5,6,7])
        self.assertEqual(reader.getN(),6)

        # setting up fake trade file
        BaseUtils.writeToBinQuotes(MyDirectories.getAdjDir() / 'quotes' / '20070620' / ('test' + '_quotes.binRQ'), \
                           [2020, 7],\
                           [[1,2,3,4,5,6,7],\
                            [1,2,3,4,5,6,7], \
                            [1,1,1,14,1,1,2],\
                            [1,2,3,4,5,6,7],\
                            [1,1,1,1,14,1,2]]) 
                
        # cleaning quote data
        obj = TAQCleanQuotes(k=6,tau=0.0005)
        obj.cleanAllQuotes(tickers = ["test"], dates = ['20070620','20070621'])

        # getting cleaned data
        reader = fm2.getQuotesFile('20070620', 'test')

        # assertions on cleaned data
        self.assertListEqual(list(reader._bp), [1,1,1,1,2])
        self.assertListEqual(list(reader._bs),[1,2,3,6,7])
        self.assertListEqual(list(reader._ap), [1,1,1,1,2])
        self.assertListEqual(list(reader._as),[1,2,3,6,7])
        self.assertListEqual(list(reader._ts), [1,2,3,6,7])
        self.assertEqual(reader.getN(),5)

    def test2(self):
        # filemanger setup
        fm1 = FileManager(MyDirectories.getAdjDir())
        fm2 = FileManager(MyDirectories.getCleanDir())

        # cleaning trades
        obj = TAQCleanTrades(k = 60, tau = 0.0005)
        obj.cleanAllTrades(tickers = ['GE'], dates = ['20070720','20070721'])

        # getting before and after data
        reader_before = fm1.getTradesFile( '20070720', 'GE' )
        reader_after = fm2.getTradesFile('20070720', 'GE')

        # saving plots to test_plot
        BaseUtils.plot_ba_price(reader_before, reader_after, "Trade cleaning for MTW",\
                                filename = MyDirectories.getTestPlotDir()/"test_trade_clean.png")
        
        # cleaning quotes data
        obj = TAQCleanQuotes(k = 60, tau = 0.0005)
        obj.cleanAllQuotes(tickers = ['GE'], dates = ['20070720','20070721'])

        # getting before and after data
        reader_before = fm1.getQuotesFile( '20070720', 'GE' )
        reader_after = fm2.getQuotesFile('20070720', 'GE')

        # saving plots to test_plot
        BaseUtils.plot_ba_bidp(reader_after, reader_before, "Bid cleaning for General Electric",\
                               filename = MyDirectories.getTestPlotDir()/"test_bid_clean.png")
        BaseUtils.plot_ba_askp(reader_after, reader_before, "Ask cleaning for General Electric",\
                               filename = MyDirectories.getTestPlotDir()/"test_ask_clean.png")
  
        
if __name__ == "__main__":
    unittest.main()
