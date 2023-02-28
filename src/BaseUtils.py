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

# default dates
startDate = "20070919"
endDate = "20070921"

def readExcel(filename, index = None):
    '''
    read excel file or csv to dataframe
    filename : [String]the path of file 
    '''
    if ".csv" == filename.suffix:
        return pd.read_csv(filename, index_col = index)
    else:
        return pd.read_excel(filename, index_col = index)
    

def writeToBinQuotes(filename,header,data):
    '''
    write quote data to binary 
    filename : [String] file name the data should write into
    header : [list] header corresponding to seconds from epoch and number of records
    data : [list] data to write to binary files
    '''
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
    '''
    write trade data to binary 
    filename : [String] file name the data should write into
    header : [list] header corresponding to seconds from epoch and number of records
    data : [list] data to write to binary files
    '''
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
    '''
    Making before-after price comparison
    dataB : [Binreader] before data
    dataA : [Binreader] after data
    title : [String] title of the graph
    filename : [String] the name of the graph
    '''
    fig, (ax1,ax2) = plt.subplots(2,figsize=(15,10))
    fig.suptitle(title)
    plot_data(ax1,dataB.getN(),dataB.getMillisFromMidn, dataB.getPrice,"Price Before")
    ax1.legend()
    plot_data(ax2,dataA.getN(),dataA.getMillisFromMidn, dataA.getPrice,"Price After")
    ax2.legend()
    if filename : fig.savefig(filename)

def plot_ba_bidp( dataB, dataA, title, filename=None):
    '''
    Making before-after bid price comparison
    dataB : [Binreader] before data
    dataA : [Binreader] after data
    title : [String] title of the graph
    filename : [String] the name of the graph
    '''
    fig, (ax1,ax2) = plt.subplots(2,figsize=(15,10))
    fig.suptitle(title)
    plot_data(ax1,dataB.getN(),dataB.getMillisFromMidn, dataB.getBidPrice,"Price Before")
    ax1.legend()
    plot_data(ax2,dataA.getN(),dataA.getMillisFromMidn, dataA.getBidPrice,"Price After")
    ax2.legend()
    if filename : fig.savefig(filename)

def plot_ba_askp( dataB, dataA, title, filename=None):
    '''
    Making before-after ask price comparison
    dataB : [Binreader] before data
    dataA : [Binreader] after data
    title : [String] title of the graph
    filename : [String] the name of the graph
    '''
    fig, (ax1,ax2) = plt.subplots(2,figsize=(15,10))
    fig.suptitle(title)
    plot_data(ax1,dataB.getN(),dataB.getMillisFromMidn, dataB.getAskPrice,"Price Before")
    ax1.legend()
    plot_data(ax2,dataA.getN(),dataA.getMillisFromMidn, dataA.getAskPrice,"Price After")
    ax2.legend()
    if filename : fig.savefig(filename)

def plot_data(ax,N,data_x,data_y,label):
    '''
    Function to plot data
    ax : [matplotlib.axes.Axes] the axes to draw graph
    N : [int] length of the data
    data_x, data_y : [Function] a binreader function
    label : [String] label for lines   
    '''
    x = []
    y = []
    for index in range(N):
        x.append(data_x(index))
        y.append(data_y(index))
    ax.plot(x,y,label = label)


def plot_ba_trade(dataB,dataA,title,filename=None):
    '''
    Making before-after ask trade price and size comparison
    dataB : [Binreader] before data
    dataA : [Binreader] after data
    title : [String] title of the graph
    filename : [String] the name of the graph
    '''
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
    '''
    Making before-after ask bid price and size comparison
    dataB : [Binreader] before data
    dataA : [Binreader] after data
    title : [String] title of the graph
    filename : [String] the name of the graph
    '''
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
    '''
    Making before-after ask ask price and size comparison
    dataB : [Binreader] before data
    dataA : [Binreader] after data
    title : [String] title of the graph
    filename : [String] the name of the graph
    '''
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

# set some default values to be used throughout the project
snp = readExcel(MyDirectories.getTAQDir() / "s&p500.xlsx")
snp["Names Date"] = snp["Names Date"].apply(lambda x: str(x)[:-2])
snp_tickers = set(snp['Ticker Symbol'].dropna().to_list())
default_dates = ["20070620", "20070921"]


def binToFrame(date,ticker,trade = True,baseDir = MyDirectories.getAdjDir()):

    '''
    Read data from bin to a dataframe
    date : [list] a list of date
    ticker : [String] symbol of the ticker
    trade : [Boolean] True means it's trade data
    baseDir : [Path] the base path binary files locate

    return : a dataframe
    '''

    
    df_full = pd.DataFrame()
    # loop over days
    for d in date:
        if trade:
            baseDir = baseDir
            fm = FileManager(baseDir)
            try:
                reader = fm.getTradesFile(d,ticker)
                # build dictionary for dataframe
                data_dict = {

                'time':pd.to_numeric(reader._ts),
                'price':pd.to_numeric(reader._p),
                'size':pd.to_numeric(reader._s)
            }

            except Exception as e:
                print(e)
                continue
            
           
        else:
            baseDir = MyDirectories.getAdjDir()
            fm = FileManager(baseDir)
            try:
                reader = fm.getQuotesFile(d,ticker)

                data_dict = {
                    'time':pd.to_numeric(reader._ts),
                    'askPrice':pd.to_numeric(reader._ap),
                    'askSize':pd.to_numeric(reader._as),
                    'bidPrice':pd.to_numeric(reader._bp),
                    'bidSize':pd.to_numeric(reader._bs)
                }
            except Exception as e:
                print(e)
        df = pd.DataFrame(data_dict)
        # change millseconds to normal time format
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
    '''
    Calculate weighted average price
    df : [Dataframe]
    time_col : [String] the name of time column
    price_col : [String] the name of price column
    size_col : [String] the name of size column

    return : a series of weighted price; time is the index
    '''
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
    #drop_index = pd.date_range(startdate+'160000',enddate+'093059',freq=freq)
    if return_type == 'change':
        return df.resample(freq).apply(
            lambda x: x[-1]-x[0] if len(x)>0 else None
            ).dropna()
    if return_type == 'pct_change':
        return df.resample(freq).apply(
            lambda x: x[-1]/x[0]-1 if len(x)>0 else None
            ).dropna()

