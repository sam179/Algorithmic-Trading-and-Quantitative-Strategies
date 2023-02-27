from OptimalK import OptimalKAll
import unittest
import os

class Test_OptimalK(unittest.TestCase):
    
    # def test_autocorrelation(self):
    #     cor_obj = TAQAutocorrelation(['20070919','20070920'],'IBM')
    #     optimal_f = cor_obj.autocorrelation(['20S','30S','1T','3T','5T','10T','20T'],lags=1)

    #     cor_obj2 = TAQAutocorrelation(['20070919','20070920'],'MSFT')
    #     optimal_f2 = cor_obj2.autocorrelation(['20S','30S','1T','3T','5T','10T','20T'],lags=1)

    #     self.assertEqual(optimal_f,'30S')

    def test_get_all_optimal_k(self):
        all = OptimalKAll(['IBM','MSFT'],None,None)
        all.get_all_optimal_k()
        self.assertTrue('optimalK.txt' in os.listdir(os.getcwd()))

if __name__ == "__main__":
    unittest.main()