import unittest
from MyDirectories import *
import pandas as pd
from TrainTestSplit import TrainTestSplit

class Test_TrainTestSplit(unittest.TestCase):
    tts = TrainTestSplit('normalized_returns.csv',q=0.5)
    def testConstructor(self):
        
        self.assertEqual(len(self.tts.data.columns),509) #need to change with full data set


    def testSplit(self):

        self.tts.split()
        self.tts.get_test_set(2)
        self.assertFalse(self.tts.train,None)



if __name__ == "__main__":
    unittest.main()
    

