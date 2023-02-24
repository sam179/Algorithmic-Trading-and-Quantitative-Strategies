import os
from datetime import datetime
from pathlib import Path
cwd = Path(os.getcwd())

class MyDirectories(object):

    TEMP_DIR = cwd / "tmp"
    DATA_PATH = cwd / "data_orig"
    DATA_PATH_ADJ = cwd / "data_adj"
    DATA_PATH_CLEAN = cwd / "data_clean"
    BASE_DIR = cwd
    SRC_DIR = cwd / "src"
    TIMESTAMP = lambda : datetime.now().strftime("%Y%m%d")
    BinRTTradesDir = DATA_PATH / "trades"
    BinRQQuotesDir = DATA_PATH / "quotes"
    BinRTTradesAdjDir = DATA_PATH_ADJ / "trades"
    BinRQQuotesAdjDir = DATA_PATH_ADJ / "quotes"
    BinRTTradesClDir = DATA_PATH_CLEAN / "trades"
    BinRQQuotesClDir = DATA_PATH_CLEAN / "quotes"

def getAdjDir():
    return MyDirectories.DATA_PATH_ADJ

def getCleanDir():
    return MyDirectories.DATA_PATH_CLEAN

def getTempDir():
    return MyDirectories.TEMP_DIR

def getTradesDir():
    return MyDirectories.BinRTTradesDir

def getQuotesDir():
    return MyDirectories.BinRQQuotesDir

def getTAQDir():
    return MyDirectories.DATA_PATH

def getTradesAdjDir():
    return MyDirectories.BinRTTradesAdjDir

def getQuotesAdjDir():
    return MyDirectories.BinRQQuotesAdjDir

def getTradesClDir():
    return MyDirectories.BinRTTradesClDir

def getQuotesClDir():
    return MyDirectories.BinRQQuotesClDir