from TAQAdjust import *
import unittest
import MyDirectories
from FileManager import FileManager

obj = TAQAdjust(isquote=True)
changedTrades = obj.adjustData(tickers = ['IBM','MSFT'])
print(changedTrades)
fm = FileManager( MyDirectories.getAdjDir())
reader = fm.getQuotesFile( '20070920', 'MSFT' )
out = list([
            reader.getN(),
            reader.getSecsFromEpocToMidn(),
            reader.getMillisFromMidn( 0 ),
            reader.getBidSize( 0 ),
            reader.getBidPrice( 0 ),
            reader.getAskSize( 0 ),
            reader.getAskPrice( 0 )
        ])
print(out)