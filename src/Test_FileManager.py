import unittest

import MyDirectories
from FileManager import FileManager


# Version 1802181651 
class Test_FileManager(unittest.TestCase):

    def test(self):

        # Instantiate a file manager
        baseDir = MyDirectories.getTestDataDir()
        fm = FileManager( baseDir )

        # Make sure we can get a full list of trade dates between
        # a start date and an end date (exclusive).
        # Define a range of date for which we will be retrieving
        # actual trading days available in the TAQ database
        startDateString = "20070919"
        endDateString = "20070921"
        # Retrieve list of trading days for trades files
        tradeDates = fm.getTradeDates(startDateString, endDateString) # 20070620, 20070621, ...
        # Make sure we got what we expected.
        self.assertEqual( "['20070919', '20070920']", str( tradeDates ) )

        # Now, do the same thing for quotes.
        # Define a range of dates for quotes
        startDateString = "20070920"
        endDateString = "20070925"
        # Retrieve list of trading days for quotes files
        quoteDates = fm.getQuoteDates(startDateString, endDateString )
        # Make sure we got what we expected.
        self.assertEqual( "['20070920']", str( quoteDates ) )

        # Now, make sure we can retrieve a list of tickers for a
        # given trade date.
        # Retrieve list of tickers for trade files for that date
        tradeTickers = fm.getTradeTickers( tradeDates[ 0 ] )
        # Make sure we got what we expected.
        self.assertEqual("['IBM', 'MSFT', 'PFE']", str(tradeTickers))

        # Do the same thing for quotes.
        # Retrieve list of tickers for trade files for that date
        quoteTickers = fm.getQuoteTickers( quoteDates[ 0 ] )
        # Make sure we got what we expected.
        self.assertEqual("['GE', 'IBM', 'MSFT']", str( quoteTickers ) )

        # Retrieve one IBM quotes file.
        ibmQuotes20070920 = fm.getQuotesFile( "20070920", "IBM" )
        # Confirm that we have access to one of the fields, the
        # one that tells us how many records are in the file.
        self.assertEqual( 70166, ibmQuotes20070920.getN() )
        # Make sure the midquote for the last record is what we
        # expected.
        decimalPlacesForFloatPriceComparison = 3
        self.assertAlmostEqual(
            116.79499816894531,
            ( ibmQuotes20070920.getAskPrice( 70165 ) + ibmQuotes20070920.getBidPrice( 70165 ) ) / 2.0,
            decimalPlacesForFloatPriceComparison
        )

        # Retrieve one IBM trades file for the trade date
        ibmTrades20070919 = fm.getTradesFile( "20070919", "IBM" )
        # Confirm that we have access to one of the fields, the
        # one that tells us how many records are in the file.
        self.assertEqual( 36913, ibmTrades20070919.getN() )
        # Make sure the last trade of the day has the value we
        # expect.
        self.assertEqual(
            116.66999816894531,
            ibmTrades20070919.getPrice( 36912 ),
            decimalPlacesForFloatPriceComparison
        )

if __name__ == "__main__":
    unittest.main()

