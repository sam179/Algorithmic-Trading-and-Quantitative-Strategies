from CovEstimatorsFun import CovEstimators
import CovEstimatorsFun as cf
import unittest
import numpy as np
import pandas as pd
import MyDirectories
import os

class Test_CovEstimator(unittest.TestCase):
    ce = CovEstimators('returns.csv')

    def test_min_var_weight(self):
        'Test to see if min_var_weight functions'
        # normal case
        cov = np.cov(self.ce.splitObj.get_train_set(0))
        w = cf.min_var_weight(cov,
                              self.ce.splitObj.get_test_set(0),
                              n_stocks=len(cov))
        self.assertEqual(len(w),len(cov))

        # corner case cov and test_set don't have compatible size
        with self.assertRaises(Exception):
            cf.min_var_weight([[1,2,3],[12,3,5],[3,8,3]],
                              self.ce.splitObj.get_test_set(0),
                              n_stocks=len(cov)
                              )
            
    def test_cov_cal(self):
        'Test for cov cal function'
        # normal case
        cov = np.cov(self.ce.splitObj.get_train_set(0))
        cov2 = cf.cov_cal(self.ce.splitObj.get_train_set(0))
        self.assertAlmostEqual(cov[0][0],cov2[0][0],5)
        train_data = self.ce.splitObj.get_train_set(0)

        cov_type = 'optimalShrinkage'
        cov = cf.cov_cal(train_data, type=cov_type)
        self.assertAlmostEqual(cov[0][0], 1.37067947e-06, places=5)

        cov_type = 'clipped'
        cov = cf.cov_cal(train_data, type=cov_type)
        self.assertAlmostEqual(cov[0][0], 1.37067947e-06, places=5)

        cov_type = 'empirical'
        cov = cf.cov_cal(train_data, type=cov_type)
        self.assertAlmostEqual(cov[0][0], 1.36996291e-06, places=5)

        cov_type = 'ewrm'
        cov = cf.cov_cal(train_data, type=cov_type)
        self.assertAlmostEqual(cov[0][0], 9.70936348e-07, places=5)

        # corner cases:data is empty
        cov3 = cf.cov_cal(data=pd.DataFrame())
        self.assertIsNone(cov3)
        # corner cases:input type doesn't belong to any 
        cov4 = cf.cov_cal(self.ce.splitObj.get_train_set(0),'real')
        self.assertIsNone(cov4)

    def test_induced_turover(self):
        "Test if induced turnover works"
        
        for g_type in ["min_variance"]:
            for cov_type in ['empirical']:
                it = self.ce.induced_turnover(cov_type,g_type)
                self.assertAlmostEqual(it,1.89,1)

    def test_visual_compare(self):
        'Test if visual compare function works'
        cov_type = ['optimalShrinkage','empirical','clipped']
        g_type = 'min_variance'
        for c in cov_type:
            self.ce.visual_compare(c,g_type)
            record_path = MyDirectories.getRecordDir()
            # to check if the record file is created
            self.assertTrue(f'{c}_{g_type}.jpg' in os.listdir(record_path))
            





if __name__ == "__main__":
    unittest.main()