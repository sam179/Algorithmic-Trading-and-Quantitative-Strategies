import unittest
from MyDirectories import *
import pandas as pd
from TrainTestSplit import TrainTestSplit
import numpy as np

class Test_TrainTestSplit(unittest.TestCase):
    tts = TrainTestSplit('normalized_returns.csv',q=0.5)
    
    def testConstructor(self):
        '''test for constructors'''
        d = pd.read_csv(MyDirectories.BASE_DIR/'normalized_returns.csv',index_col=[0])
        self.assertEqual(str(self.tts.data.columns),str(d.columns))


    def testSplit(self):
        '''test that train and test sets have the same length'''
        self.tts.split()
        self.assertEqual(len(self.tts.train),len(self.tts.test))
        # test for corner cases
        corner_case = TrainTestSplit('normalized_returns.csv',q=0.5)
        corner_case.data = np.random.rand(300,200)
        corner_case.split()
        self.assertEqual(len(corner_case.train),0)

    def testGetTrainTest(self):
        '''test to see if they can get train test data correctly'''
        # if fold is too large
        with self.assertRaises(Exception):self.tts.get_train_set(70)
        # when the fold is within range
        self.tts.split()
        t = self.tts.get_test_set(2)
        self.assertEqual(len(t),self.tts.test_size)


if __name__ == "__main__":
    unittest.main()
    

