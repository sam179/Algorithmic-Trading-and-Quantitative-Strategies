from TAQAutocorrelation import TAQAutocorrelation
import unittest

class Test_TAQAutocorrelation(unittest.TestCase):
    
    def test_autocorrelation(self):
        cor_obj = TAQAutocorrelation(['20070919','20070920'],'IBM')
        optimal_f = cor_obj.autocorrelation(['20S','30S','1T','3T','5T'],lags=1)
        self.assertEqual(optimal_f,'30S')

if __name__ == "__main__":
    unittest.main()