from TAQAdjust import *
from TAQCleaner import *
import unittest
import MyDirectories
from FileManager import FileManager

obj = TAQCleanTrades(k = 101, tau = 0)
fm = FileManager(MyDirectories.getAdjDir())
reader = fm.getTradesFile( '20070920', 'MSFT' )
out = list([
            reader.getN(),
            reader.getSecsFromEpocToMidn(),
            reader.getMillisFromMidn( 0 ),
            reader.getSize( 0 ),
            reader.getPrice( 0 )
        ])
print(out)

reader = fm.getTradesFile( '20070920', 'IBM' )
out = list([
            reader.getN(),
            reader.getSecsFromEpocToMidn(),
            reader.getMillisFromMidn( 0 ),
            reader.getSize( 0 ),
            reader.getPrice( 0 )
        ])
print(out)

obj.cleanAllTrades(tickers = ['IBM','MSFT'])
fm = FileManager( MyDirectories.getCleanDir())

reader = fm.getTradesFile( '20070920', 'IBM' )
out = list([
            reader.getN(),
            reader.getSecsFromEpocToMidn(),
            reader.getMillisFromMidn( 0 ),
            reader.getSize( 0 ),
            reader.getPrice( 0 )
        ])
print(out)

reader = fm.getTradesFile( '20070920', 'MSFT' )
out = list([
            reader.getN(),
            reader.getSecsFromEpocToMidn(),
            reader.getMillisFromMidn( 0 ),
            reader.getSize( 0 ),
            reader.getPrice( 0 )
        ])
print(out)