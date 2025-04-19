'''
Created on Feb 22, 2017
Updated for Python 3 compatibility

@author: joigno
'''

import csv
from math import sqrt, exp, log
import pandas as pd

from coins import CoinDB
from stocks import get_returns
from scraper2024 import get_coins
from dateconfig import DateRange
from datetime import datetime, timedelta

def calcReturns(vals, window=1):
    ret = []
    if len(vals) == 0:
        return ret
    for i in range(len(vals)//window - 1):
        ratio = (vals[(i+1)*window] / float(vals[(i)*window])) - 1.0
        ret.append(ratio)
    return ret

def calcLogReturns(vals, window=1):
    ret = []
    if len(vals) == 0:
        return ret
    for i in range(len(vals)//window - 1):
        ratio = log(vals[(i+1)*window] / float(vals[(i)*window]))
        ret.append(ratio)
    return ret

def median(lst):
    quotient, remainder = divmod(len(lst), 2)
    if remainder:
        return sorted(lst)[quotient]
    return sum(sorted(lst)[quotient - 1:quotient + 1]) / 2.

def ave(vals, minusOne=False):
    if len(vals) == 0:
        return 0.0
    return sum(vals)/(minusOne and len(vals)-1 or len(vals))


class PortfolioAnalyzer(object):
    '''
    classdocs
    '''
    
    lastNPoints = 3650

    def __init__(self, interval='1D'):
        '''
        Constructor
        '''
        self.interval = interval
        self.data = {}
        self.returns = {}  # Stores lists of returns
        self.average_returns = {}  # Stores calculated averages
        self.medians = {}
        self.sigmas = {}
        self.sigmaChances = {}
        self.correlations = {}
    
        self.coin_db = CoinDB()
        self.assets = get_coins() #+ self.coin_db.stocks
        
        self._load_data()
        
    def _load_data(self):
        """Load price data for all coins"""
        for coin in get_coins():
            try:
                df = pd.read_csv(f'data/{self.interval}_price_{coin}.csv')
                df['returns'] = df['prices'].pct_change().dropna()
                self.returns[coin] = df['returns']
            except Exception as e:
                print(f"Error loading {coin} data: {str(e)}")
        
        self.rets = {}
        self.computeReturns()
        self.computeSigmas()
        self.computeCorrelations()
        
    def computeReturns(self):
        """Compute and store returns for all assets"""
        for a in self.assets:
            rvals = get_returns(a)
            self.rets[a] = rvals
            self.returns[a] = rvals  # Store raw returns
            self.average_returns[a] = ave(rvals)  # Store average
            print(f'Average Returns for {a}: {self.average_returns[a]*100:.4f}%')

    def computeSigmas(self):
        """Compute standard deviations for all assets"""
        for a in self.assets:
            if a in self.returns:
                returns = self.returns[a]
                avg = self.average_returns[a]
                sigma = self._computeSigmas(returns, avg, a)
                self.sigmas[a] = sigma
            
    def _computeSigmas(self, returns, avg, name):
        """Compute standard deviation for a list of returns"""
        variance = ave([(r - avg)**2 for r in returns], minusOne=True)
        sigma = sqrt(abs(variance))
        
        low = avg - sigma
        high = avg + sigma
        
        return sigma
        
    def computeCorrelations(self):
        """Compute correlations between all assets"""
        print()
        print('Computing correlations...')
        corrList = []
        
        for a in self.assets:
            for b in self.assets:
                if b == a:
                    self.correlations[(a,b)] = 1.0
                    continue
                    
                if a not in self.returns or b not in self.returns:
                    continue
                    
                retsA = self.returns[a]
                retsB = self.returns[b]
                avgA = self.average_returns[a]
                avgB = self.average_returns[b]
                
                # Ensure we have the same number of data points
                minLen = min(len(retsA), len(retsB))
                if minLen == 0:
                    continue
                    
                retsA = retsA[-minLen:]
                retsB = retsB[-minLen:]
                
                # Calculate correlation
                numerator = sum((rA - avgA) * (rB - avgB) for rA, rB in zip(retsA, retsB))
                denomA = sum((rA - avgA)**2 for rA in retsA)
                denomB = sum((rB - avgB)**2 for rB in retsB)
                
                if denomA == 0 or denomB == 0:
                    continue
                    
                correlation = numerator / sqrt(denomA * denomB)
                self.correlations[(a,b)] = correlation
                corrList.append((correlation, a, b))
                
        # Sort correlations for display
        corrList.sort(reverse=True)
        for corr, a, b in corrList[:10]:  # Show top 10 correlations
            print(f"{a}-{b}: {corr:.4f}")

    def portfolioReturn(self, portfolio):
        """Calculate annualized portfolio return"""
        total = 0.0
        for coin, weight in portfolio.items():
            if coin in self.average_returns:
                total += weight * (self.average_returns[coin] * 252)
        return total
        
    
    def portfolioStandardDev(self, portfolio):
        """Calculate annualized portfolio volatility"""
        variances = 0.0
        for coin, weight in portfolio.items():
            if coin in self.returns:
                returns = self.returns[coin]
                avg = self.average_returns[coin]
                variance = ave([(r - avg)**2 for r in returns], minusOne=True)
                variances += (weight ** 2) * variance * 252
        
        # Add covariance terms (simplified for example)
        # In reality should calculate full covariance matrix
        return sqrt(variances)
                
    
    def portfolioAnalysis(self, mypfolio, min_return, max_sigma, maxDaysTesting=None, testing=False):
        # Portfolio Returns
        pfolioRet = self.portfolioReturn(mypfolio)
        print('Analyzing portfolio ...')
        print(mypfolio)
        print()
        print('Portfolio Returns = %.2f percent' % (pfolioRet*100.0))
        print()
        print('Analyzing Portfolio Risk ..')
        pfolioRets = [(coin, self.returns[coin]) for coin, w in mypfolio.items()]
        minLen = min([len(rets) for coin, rets in pfolioRets])
        if maxDaysTesting:
            minLen = min(minLen, maxDaysTesting)
        pfolioRets = [(coin, rets[-minLen:]) for coin, rets in pfolioRets]
        
        pfolioWRets = []
        finalRet = 1.0
        maxDrawdown = 1.0
        for i in range(minLen):
            dayRet = sum([mypfolio[coin]*rets[i] for coin, rets in pfolioRets])
            pfolioWRets.append(dayRet)
            finalRet *= 1.0+dayRet
            if finalRet < maxDrawdown:
                maxDrawdown = finalRet
        finalRet = finalRet - 1.0
        maxDrawdown = maxDrawdown - 1.0
        finalAve = ave(pfolioWRets)
        sigma = sqrt(ave([(finalAve-r)**2 for r in pfolioWRets], minusOne=True))
        print('FINAL REPORT (for fixed Minimum Return of %.4f percent):' % (min_return*100.0))
        start = datetime(year=DateRange.endYear, month=DateRange.endMonth, day=DateRange.endDay)
        start = start - timedelta(days=minLen)
        print('Observations for %d Days (Year-Month-Day) Start = %d-%d-%d  and End = %d-%d-%d' % (minLen, start.year, start.month, start.day, DateRange.endYear, DateRange.endMonth, DateRange.endDay))
        print('Expected Average Return per Day = %.4f percent' % (min_return*100.0))
        print('Observed Average Return per Day = %.4f percent' % (finalAve*100.0))
        print('Expected Standard Deviation per day = %.4f percent' % (max_sigma*100.0))
        print('Observed Standard Deviation per day = %.4f percent' % (sigma*100.0))
        print('Expected Return in %d Days = %.4f percent' % (minLen, (finalAve*minLen*100.0)))
        print('Observed Return in %d Days = %.4f percent' % (minLen, finalRet*100.0))
        try:
            print('Expected SHARPE RATIO = %.4f' % (finalAve*minLen / (max_sigma*sqrt(minLen))))
            print('Observed SHARPE RATIO = %.4f' % (finalRet / (sigma*sqrt(minLen))))
        except:
            pass
        
        self.pfolioWRets = pfolioWRets
        self.pfolioRets = pfolioRets
        
        print('-'*80)
        if not testing:
            return (finalAve+min_return)/2., (sigma+max_sigma)/2., maxDrawdown, minLen             
        else:
            return finalRet, sigma*sqrt(minLen), maxDrawdown, minLen
    
            
if __name__ == '__main__':
    
    pfolio = PortfolioAnalyzer()
    # The data is now loaded in the constructor, so we don't need to call loadAndComputeStatistics
    # pfolio.loadAndComputeStatistics()
    
    # Example portfolio for testing
    p = {'bitcoin': 0.4, 'ethereum': 0.3, 'litecoin': 0.3}
    pfolio.portfolioAnalysis(p, min_return=0.001, max_sigma=0.02)
