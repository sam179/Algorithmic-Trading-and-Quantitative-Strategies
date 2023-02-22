from TAQAdjust import *
import unittest

obj = TAQAdjust(isquote=False)
changedTrades = obj.adjustData(tickers = ['IBM','MSFT'])
