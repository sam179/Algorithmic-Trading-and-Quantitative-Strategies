import unittest
import BaseUtils as bu

class Test_BaseUtils(unittest.TestCase):

    def test_bintooframe(self):
        df = bu.binToFrame('20070920','IBM')
        df_col = list(df.columns)
        
        self.assertEqual(len(df),25367)
        self.assertEqual(
            str(df_col),
            '[\'time\', \'price\', \'size\']'
            )
        self.assertAlmostEqual(df['price'][0],116.2699966430664)

if __name__ == "__main__":
    unittest.main()