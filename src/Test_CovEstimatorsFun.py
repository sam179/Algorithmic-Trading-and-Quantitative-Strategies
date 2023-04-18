import unittest
import CovEstimatorsFun as covariance_estimators

class TestCovEstimators(unittest.TestCase):

    #def test_min_var_weight(self):

    def test_cov_cal(self):
        ce = covariance_estimators.CovEstimators('normalized_returns.csv')
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


        print(cov)



if __name__ == "__main__":
    unittest.main()