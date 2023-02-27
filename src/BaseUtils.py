import pandas as pd
import gzip
import struct
from matplotlib import pyplot as plt
import MyDirectories
import os

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

def plot_ba_price( dataB, dataA, title, filename=None):
    fig, (ax1,ax2) = plt.subplots(2,figsize=(15,10))
    fig.suptitle(title)
    plot_data(ax1,dataB.getN(),dataB.getMillisFromMidn, dataB.getPrice,"Price Before")
    ax1.legend()
    plot_data(ax2,dataA.getN(),dataA.getMillisFromMidn, dataA.getPrice,"Price After")
    ax2.legend()
    if filename : fig.savefig(filename)

def plot_ba_bidp( dataB, dataA, title, filename=None):
    fig, (ax1,ax2) = plt.subplots(2,figsize=(15,10))
    fig.suptitle(title)
    plot_data(ax1,dataB.getN(),dataB.getMillisFromMidn, dataB.getBidPrice,"Price Before")
    ax1.legend()
    plot_data(ax2,dataA.getN(),dataA.getMillisFromMidn, dataA.getBidPrice,"Price After")
    ax2.legend()
    if filename : fig.savefig(filename)

def plot_ba_askp( dataB, dataA, title, filename=None):
    fig, (ax1,ax2) = plt.subplots(2,figsize=(15,10))
    fig.suptitle(title)
    plot_data(ax1,dataB.getN(),dataB.getMillisFromMidn, dataB.getAskPrice,"Price Before")
    ax1.legend()
    plot_data(ax2,dataA.getN(),dataA.getMillisFromMidn, dataA.getAskPrice,"Price After")
    ax2.legend()
    if filename : fig.savefig(filename)

def plot_data(ax,N,data_x,data_y,label):
    x = []
    y = []
    for index in range(N):
        x.append(data_x(index))
        y.append(data_y(index))
    ax.plot(x,y,label = label)


def plot_ba_trade(dataB,dataA,title,filename=None):
    fig, (ax1,ax2) = plt.subplots(2,figsize=(15,10))
    fig.suptitle(title)
    plot_data(ax1,dataB.getN(),dataB.getMillisFromMidn, dataB.getPrice,"Price Before")
    plot_data(ax1,dataA.getN(),dataA.getMillisFromMidn, dataA.getPrice,"Price After")
    ax1.legend()
    plot_data(ax2,dataB.getN(),dataB.getMillisFromMidn, dataB.getSize,"Size Before")
    plot_data(ax2,dataA.getN(),dataA.getMillisFromMidn, dataA.getSize,"Size After")
    ax2.legend()
    if filename : fig.savefig(filename)


def plot_ba_bid(dataB,dataA,title,filename=None):
    fig, (ax1,ax2) = plt.subplots(2,figsize=(15,10))
    fig.suptitle(title)
    plot_data(ax1,dataB.getN(),dataB.getMillisFromMidn, dataB.getBidPrice,"Price Before")
    plot_data(ax1,dataA.getN(),dataA.getMillisFromMidn, dataA.getBidPrice,"Price After")
    ax1.legend()
    plot_data(ax2,dataB.getN(),dataB.getMillisFromMidn, dataB.getBidSize,"Size Before")
    plot_data(ax2,dataA.getN(),dataA.getMillisFromMidn, dataA.getBidSize,"Size After")
    ax2.legend()
    if filename : fig.savefig(filename)

def plot_ba_ask(dataB,dataA,title,filename=None):
    fig, (ax1,ax2) = plt.subplots(2,figsize=(15,10))
    fig.suptitle(title)
    plot_data(ax1,dataB.getN(),dataB.getMillisFromMidn, dataB.getAskPrice,"Price Before")
    plot_data(ax1,dataA.getN(),dataA.getMillisFromMidn, dataA.getAskPrice,"Price After")
    ax1.legend()
    plot_data(ax2,dataB.getN(),dataB.getMillisFromMidn, dataB.getAskSize,"Size Before")
    plot_data(ax2,dataA.getN(),dataA.getMillisFromMidn, dataA.getAskSize,"Size After")
    ax2.legend()
    if filename : fig.savefig(filename)

def mkDir(folderName):
    if not os.path.isdir(folderName):
       os.makedirs(folderName)

snp = readExcel(MyDirectories.getTAQDir() / "s&p500.csv")
snp["Names Date"] = snp["Names Date"].apply(lambda x: str(x)[:-2])
snp_tickers = set(snp['Ticker Symbol'].dropna().to_list())
default_dates = ["20070620", "20070921"]


def binToFrame(date,ticker,trade = True):

    '''
    Read data from bin to a dataframe
    date : list
    '''

    
    df_full = pd.DataFrame()
    for d in date:
        if trade:
            baseDir = MyDirectories.getAdjDir()
            fm = FileManager(baseDir)
            reader = fm.getTradesFile(d,ticker)
            
            data_dict = {

                'time':pd.to_numeric(reader._ts),
                'price':pd.to_numeric(reader._p),
                'size':pd.to_numeric(reader._s)
            }

        else:
            baseDir = MyDirectories.getAdjDir()
            fm = FileManager(baseDir)
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

def cal_return(df,freq='5T',return_type = 'change',
                startdate = '20070919',enddate = '20070920'):
    '''
    This function calculate the return (pure change or pct change)
    df : processed df from weighted_average_price(); index are datetime; 
        single column represents price
    freq : the frequency to calculate return; default 5T
    return_type : can be 'change' or 'pct_change'

    return : a series of change; index time
    '''
    drop_index = pd.date_range(startdate+'160000',enddate+'093059',freq=freq)
    if return_type == 'change':
        return df.resample(freq).apply(
            lambda x: x[-1]-x[0] if len(x)>0 else None
            ).drop(drop_index)
    if return_type == 'pct_change':
        return df.resample(freq).apply(
            lambda x: x[-1]/x[0]-1 if len(x)>0 else None
            ).drop(drop_index)

