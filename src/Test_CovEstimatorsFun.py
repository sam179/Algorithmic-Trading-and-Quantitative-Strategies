from CovEstimatorsFun import CovEstimators
import CovEstimatorsFun as cf
import unittest
import numpy as np
import pandas as pd

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
        train_data = ce.splitObj.get_train_set(0)

        cov_type = 'optimalShrinkage'
        cov = covariance_estimators.cov_cal(train_data, type=cov_type)
        self.assertAlmostEqual(cov[0][0], 3.17694534e-03, places=6)

        cov_type = 'clipped'
        cov = covariance_estimators.cov_cal(train_data, type=cov_type)
        self.assertAlmostEqual(cov[0][0], 0.00317695, places=6)

        cov_type = 'empirical'
        cov = covariance_estimators.cov_cal(train_data, type=cov_type)
        self.assertAlmostEqual(cov[0][0], 3.17682995e-03, places=6)

        cov_type = 'ewrm'
        cov = covariance_estimators.cov_cal(train_data, type=cov_type)
        self.assertAlmostEqual(cov[0][0], 8.49027983e-03, places=6)

        # corner cases:data is empty
        cov3 = cf.cov_cal(data=pd.DataFrame())
        self.assertIsNone(cov3)
        # corner cases:input type doesn't belong to any 
        cov4 = cf.cov_cal(self.ce.splitObj.get_train_set(0),'real')
        self.assertIsNone(cov4)





if __name__ == "__main__":
    unittest.main()