import unittest
import BaseUtils as bu

class Test_BaseUtils(unittest.TestCase):

    def test_bintooframe(self):
        df = bu.binToFrame(['20070919','20070920'],'IBM')
        df_col = list(df.columns)
        
        self.assertEqual(len(df),62280)
        self.assertEqual(
            str(df_col),
            '[\'time\', \'price\', \'size\']'
            )
        self.assertAlmostEqual(float(df['price'].iloc[0]),116.9000015258789)

    def test_weighted_average_price(self):
        df = bu.binToFrame(['20070920'],'IBM')
        df_weighted = bu.weighted_average_price(df)

        self.assertEqual(len(df_weighted),len(set(df['time'])))

    def test_cal_return(self):
        df = bu.binToFrame(['20070919','20070920'],'IBM')
        df_weighted = bu.weighted_average_price(df)
        df_return = bu.cal_return(df_weighted)
        self.assertEqual(float(df_return.iloc[0]),-0.548636002974078)

if __name__ == "__main__":
    unittest.main()