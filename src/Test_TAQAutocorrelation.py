from TAQAutocorrelation import TAQAutocorrelation
from TAQAutocorrelation import AutoCorrAll
import unittest
import os

class Test_TAQAutocorrelation(unittest.TestCase):
    
    def test_autocorrelation(self):
        cor_obj = TAQAutocorrelation(['20070622'],'JBL')
        f1,l1 = cor_obj.autocorrelation(['10S','20S'],plot=True)
        f2,l2 = cor_obj.autocorrelation(['3T'],plot=True)

       

        self.assertEqual(f1,'20S')
        self.assertEqual(f2,'3T')

    def test_get_all_optimal_freq(self):
        all = AutoCorrAll(['JBL','TMO'],'20070621','20070622')
        all.get_all_optimal_freq()
        self.assertTrue('noCorrFreq.txt' in os.listdir(os.getcwd()+'/record'))

if __name__ == "__main__":
    unittest.main()