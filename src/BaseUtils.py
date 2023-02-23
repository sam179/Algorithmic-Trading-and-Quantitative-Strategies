import pandas as pd
import gzip
import struct
from matplotlib import pyplot as plt

startDate = "20070919"
endDate = "20070921"

def readExcel(filename, index = None):
    if ".csv" == filename.suffix:
        return pd.read_csv(filename, index_col = index)
    else:
        return pd.read_excel(filename, index_col = index)
    

def writeToBinQuotes(filename,header,data):
    with gzip.open(filename, "wb") as f:
        d = struct.pack('>2i',*header)
        f.write(d)
        d = struct.pack( ( ">%di" % header[ 1 ]), *data[0] )
        f.write(d)
        d = struct.pack( ( ">%di" % header[ 1 ]), *data[1] )
        f.write(d)
        d = struct.pack( ( ">%df" % header[ 1 ]), *data[2] )
        f.write(d)
        d = struct.pack( ( ">%di" % header[ 1 ]), *data[3] )
        f.write(d)
        d = struct.pack( ( ">%df" % header[ 1 ]), *data[4] )
        f.write(d)
            
def writeToBinTrades(filename,header,data):
    with gzip.open(filename, "wb") as f:
        d = struct.pack('>2i',*header)
        f.write(d)
        d = struct.pack( ( ">%di" % header[ 1 ]), *data[0] )
        f.write(d)
        d = struct.pack( ( ">%di" % header[ 1 ]), *data[1] )
        f.write(d)
        d = struct.pack( ( ">%df" % header[ 1 ]), *data[2] )
        f.write(d)


def plotTrades(dataO, dataM, tickers, title, filename=None):
    ts = []
    prices1 = []
    prices2 = []
    size1 = []
    size2 = []

    if(dataO.getN() != dataM.getN()):
       raise("Data sizes are different.")

    for index in range(dataO.getN()):
        ts.append(dataO.getMillisFromMidn(index))
        prices1.append(dataO.getPrice(index))
        prices2.append(dataM.getPrice(index))
        size1.append(dataO.getSize(index))
        size2.append(dataM.getSize(index))

    fig, (ax1,ax2) = plt.subplot(2)
    ax1.plot(ts, prices1)
    ax1.plot(ts, prices2)
    ax1.set_title("Prices : " + title)
    ax1.legend(tickers)
    ax2.plot(ts, size1)
    ax2.plot(ts, size2)
    ax2.set_title("Shares : " + title)
    ax2.legend(tickers)
    plt.show()
    if filename: fig.savefig(filename)

    