class MyDirectories(object):
    Samar = "/Users/samarsinghholkar/Documents/NYU Courant/Sem 2/Algorithmic Trading and Quantitative Strategies/Homework/TAQDataStats"
    TempDir = Samar
    UnitTests = TempDir + "/taq/UnitTests"

    TAQ = Samar

    BinRTTradesDir = TAQ + "/trades"
    BinRQQuotesDir = TAQ + "/quotes"


def getTempDir():
    return MyDirectories.TempDir


def getTradesDir():
    return MyDirectories.BinRTTradesDir


def getQuotesDir():
    return MyDirectories.BinRQQuotesDir


def getTAQDir():
    return MyDirectories.TAQ