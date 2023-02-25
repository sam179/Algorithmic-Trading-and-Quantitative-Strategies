import pandas as pd
import gzip
import struct
from matplotlib import pyplot as plt
import MyDirectories
from TAQTradesReader import TAQTradesReader
from TAQQuotesReader import TAQQuotesReader
from FileManager import FileManager
import numpy as np

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



def binToFrame(date,ticker,trade = True):

    '''
    Read data from bin to a dataframe
    date : list
    '''

    baseDir = MyDirectories.getTAQDir()
    fm = FileManager(baseDir)
    df_full = pd.DataFrame()
    for d in date:
        if trade:
            reader = fm.getTradesFile(d,ticker)
            
            data_dict = {

                'time':pd.to_numeric(reader._ts),
                'price':pd.to_numeric(reader._p),
                'size':pd.to_numeric(reader._s)
            }

        else:
            reader = fm.getQuotesFile(d,ticker)

            data_dict = {
                'time':pd.to_numeric(reader._ts),
                'askPrice':pd.to_numeric(reader._ap),
                'askSize':pd.to_numeric(reader._as),
                'bidPrice':pd.to_numeric(reader._bp),
                'bidSize':pd.to_numeric(reader._bs)
            }
        df = pd.DataFrame(data_dict)
        df['time'] = pd.to_datetime(
            df['time'],
            unit = 'ms',
            origin=pd.Timestamp(d)
            )
        if len(df_full)==0:
            df_full = df
        else:
            df_full = df_full.append(df)
    return df_full


def weighted_average_price(df,time_col = 'time',price_col = 'price',size_col = 'size'):
    return df.groupby(time_col).apply(
        lambda x: np.average(x[price_col], weights = x[size_col])
        )

def cal_return(df,freq='5T',return_type = 'change'):
    '''
    This function calculate the return (pure change or pct change)
    df : processed df from weighted_average_price(); index are datetime; 
        single column represents price
    freq : the frequency to calculate return; default 5T
    return_type : can be 'change' or 'pct_change'

    return : a series of change; index time
    '''
    if return_type == 'change':
        return df.resample(freq).apply(
            lambda x: x[-1]-x[0] if len(x)>0 else None
            ).dropna()
    if return_type == 'pct_change':
        return df.resample(freq).apply(
            lambda x: x[-1]/x[0]-1 if len(x)>0 else None
            ).dropna()

    