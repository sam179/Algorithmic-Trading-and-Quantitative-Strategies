from math import sqrt
from cvxopt import matrix
from cvxopt.blas import dot
from cvxopt.solvers import qp, options
import pylab
import numpy as np
import BaseUtils
from datetime import datetime, timedelta
import MyDirectories
import pandas as pd

def runExample():
    n = 4
    S = matrix( [[ 4e-2,  6e-3, -4e-3,   0.0 ],
                [ 6e-3,  1e-2,  0.0,    0.0 ],
                [-4e-3,  0.0,   2.5e-3, 0.0 ],
                [ 0.0,   0.0,   0.0,    0.0 ]] )
    pbar = matrix([.12, .10, .07, .03])

    G = matrix(0.0, (n,n))
    G[::n+1] = -1.0
    h = matrix(0.0, (n,1))
    A = matrix(1.0, (1,n))
    b = matrix(1.0)

    N = 100
    mus = [ 10**(5.0*t/N-1.0) for t in range(N) ]
    options['show_progress'] = False
    options['abstol'] = 1e-14
    options['reltol'] = 1e-12
    results = [ qp(mu*S, -pbar, G, h, A, b, options=options) for mu in mus ]
    xs = [ qp(mu*S, -pbar, G, h, A, b)['x'] for mu in mus ]
    returns = [ dot(pbar,x) for x in xs ]
    risks = [ sqrt(dot(x, S*x)) for x in xs ]
   
    pylab.figure(1, facecolor='w')
    pylab.plot(risks, returns)
    pylab.xlabel('standard deviation')
    pylab.ylabel('expected return')
    pylab.axis([0, 0.2, 0, 0.15])
    pylab.title('Risk-return trade-off curve (fig 4.12)')
    pylab.yticks([0.00, 0.05, 0.10, 0.15])

    pylab.figure(2, facecolor='w')
    c1 = [ x[0] for x in xs ]
    c2 = [ x[0] + x[1] for x in xs ]
    c3 = [ x[0] + x[1] + x[2] for x in xs ]
    c4 = [ x[0] + x[1] + x[2] + x[3] for x in xs ]
    pylab.fill(risks + [.20], c1 + [0.0], facecolor = '#F0F0F0')
    pylab.fill(risks[-1::-1] + risks, c2[-1::-1] + c1,
        facecolor = '#D0D0D0')
    pylab.fill(risks[-1::-1] + risks, c3[-1::-1] + c2,
        facecolor = '#F0F0F0')
    pylab.fill(risks[-1::-1] + risks, c4[-1::-1] + c3,
        facecolor = '#D0D0D0')
    pylab.axis([0.0, 0.2, 0.0, 1.0])
    pylab.xlabel('standard deviation')
    pylab.ylabel('allocation')
    pylab.text(.15,.5,'x1')
    pylab.text(.10,.7,'x2')
    pylab.text(.05,.7,'x3')
    pylab.text(.01,.7,'x4')
    pylab.title('Optimal allocations (fig 4.12)')
    pylab.savefig(MyDirectories.getResultPlotDir()/ "cvxopt_example.png")
    return results


class TAQCAPM():
    def __init__(self, dates = None, filename=None):
        # Initialize the class with optional arguments for dates and filename
        self._dates = dates
        # Define columns of interest
        self._cols = [r"Names Date", r"Trading Symbol", r"Price or Bid/Ask Average", r"Shares Outstanding"]
        if filename:
            # If a filename is provided, read in the excel file and select only the columns of interest
            self._snp = BaseUtils.readExcel(filename)[self._cols]
        else: 
            # If no filename is provided, read in the default s&p500.csv file and select only the columns of interest
            self._snp = BaseUtils.readExcel(MyDirectories.getTAQDir() / "s&p500.csv")[self._cols]

    def getWeights(self, date):
        # Calculate weights for a given date
        # Select rows where "Names Date" equals the given date, and make a copy of the resulting dataframe
        current = self._snp.loc[self._snp["Names Date"] == float(date)].copy()
        # Calculate market cap for each row
        current["Market Cap"] = current[r"Price or Bid/Ask Average"]*current["Shares Outstanding"]
        # Calculate weight as market cap divided by the sum of all market caps
        current["weight"] = current["Market Cap"]/(current["Market Cap"].sum())
        # Return the resulting dataframe
        return current

    def turnOver(self, date1, date2):
        # Calculate turnover ratio between two dates
        # Get weights for the current date
        current = self.getWeights(date2)
        # Get weights for the previous date
        prev = self.getWeights(date1)
        # Merge the two dataframes on "Trading Symbol" using an outer join and fill any missing values with 0
        combined = pd.merge(current[["weight","Trading Symbol"]], prev[["weight","Trading Symbol"]], on="Trading Symbol", how='outer', suffixes=('_current', '_prev')).fillna(0)
        # Calculate turnover as the sum of absolute differences between current and previous weights
        return (combined["weight_current"] - combined["weight_prev"]).abs().sum()



