import unittest
from VWAP import VWAP
from TAQTradesReader import TAQTradesReader
from MyDirectories import *


class Test_VWAP(unittest.TestCase):

    def testVWAP(self):
        filePathName = MyDirectories.BinRTTradesDir / "20070919" / "IBM_trades.binRT"
        start930 = 19 * 60 * 60 * 1000 / 2
        end4 = 16 * 60 * 60 * 1000
        vwap = VWAP(TAQTradesReader(filePathName), start930, end4)
        self.assertEqual(
            "There were 36913 trades and a VWAP price of 116.468791",
            "There were %d trades and a VWAP price of %f" % (vwap.getN(), vwap.getVWAP())
        )


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testVWAP']
    unittest.main()
