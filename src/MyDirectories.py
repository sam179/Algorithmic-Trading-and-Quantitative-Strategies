import os
from datetime import datetime
from pathlib import Path
cwd = Path(os.getcwd())

class MyDirectories(object):

    TEMP_DIR = cwd / "tmp"
    DATA_PATH = cwd / "data"
    BASE_DIR = cwd
    SRC_DIR = cwd / "src"
    TIMESTAMP = lambda : datetime.now().strftime("%Y%m%d")
    BinRTTradesDir = DATA_PATH
    BinRQQuotesDir = DATA_PATH

def getTempDir():
    return MyDirectories.TEMP_DIR


def getTradesDir():
    return MyDirectories.BinRTTradesDir


def getQuotesDir():
    return MyDirectories.BinRQQuotesDir


def getTAQDir():
    return MyDirectories.DATA_PATH