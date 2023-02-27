from OptimalK import OptimalKAll
import unittest
import os

class Test_OptimalK(unittest.TestCase):
    
    
    def test_get_all_optimal_k(self):
        all = OptimalKAll(['JBL','TMO'],'20070621','20070622')
        all.get_all_optimal_k()
        self.assertTrue('optimalK.txt' in os.listdir(os.getcwd()+'/record'))
        with open(os.getcwd()+'/record/optimalK.txt',mode = 'r+') as f:
            lastLine = str(f.readlines()[-1]).split(',')
            f.close()
        self.assertTrue(lastLine[0],'TMO')

if __name__ == "__main__":
    unittest.main()