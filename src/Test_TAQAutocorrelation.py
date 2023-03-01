from TAQAutocorrelation import TAQAutocorrelation
from TAQAutocorrelation import AutoCorrAll
import unittest
import os
import MyDirectories
from pathlib import Path

class Test_TAQAutocorrelation(unittest.TestCase):
    
    def test_autocorrelation(self):

        cor_obj = TAQAutocorrelation(['20070622'],'JBL')
        f1,l1 = cor_obj.autocorrelation(['10S','20S'],plot=True)
        
        plot_path = MyDirectories.getTestPlotDir()
        # to check if plots are plotted
        self.assertTrue('JBL_10S_autocorr.jpg' in os.listdir(plot_path))
        self.assertTrue('JBL_20S_autocorr.jpg' in os.listdir(plot_path))
        # to see if it detect freuency correctly
        self.assertEqual(f1,'20S')
        

    def test_get_all_optimal_freq(self):
        all = AutoCorrAll(['JBL','TMO'],'20070621','20070622')
        all.get_all_optimal_freq()
        record_path = Path(Path(os.getcwd()+'/record'))
        # to check if the record file is created
        self.assertTrue('noCorrFreq.txt' in os.listdir(record_path))
        # to see correct data is written in
        with open(record_path/'noCorrFreq.txt',mode = 'r+') as f:
            lastLine = str(f.readlines()[-1]).split(',')
            f.close()
        self.assertTrue(lastLine[0],'TMO')

if __name__ == "__main__":
    unittest.main()