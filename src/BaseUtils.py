import pandas as pd
import gzip
import struct
from matplotlib import pyplot as plt
import MyDirectories
import os

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