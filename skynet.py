'''
Created on Jul 16, 2017

@author: joigno
'''
from portfolio import PortfolioAnalyzer
from coins import CoinDB
from operator import pos
import technical_indicators.technical_indicators as tai
import numpy as np
from math import log,exp,sqrt
import copy

try:
    from fit import predFunc
except:
    pass

def sigmoid(x):
    try:
        ret = 1 / (1 + exp(-x))
    except:
        ret = 0.0
    return ret

def expShape(x):
    try:
        ret = exp(x)
    except:
        ret = 0.0
    return ret

def logShape(x):
    try:
        ret = log(x)
    except:
        ret = 0.0
    return ret


def mean(data):
    """Return the sample arithmetic mean of data."""
    n = len(data)
    if n < 1:
        raise ValueError('mean requires at least one data point')
    return sum(data)/n # in Python 2 use sum(data)/float(n)

def _ss(data):
    """Return sum of square deviations of sequence data."""
    c = mean(data)
    ss = sum((x-c)**2 for x in data)
    return ss

def pstdev(data):
    """Calculates the population standard deviation."""
    n = len(data)
    if n < 2:
        raise ValueError('variance requires at least two data points')
    ss = _ss(data)
    pvar = ss/n # the population variance
    return pvar**0.5


def sign(x): 
    if x == 0.0:
        return 0.0
    return abs(x)/x

def convexity(a,b,c): return -1*sign(b-a)*sign(b-c)
def convexityW(a,b,c):
    a,b,c = float(a),float(b),float(c)
    #ret = (c-b)/(b-a)
    #if sign(c-b) == sign(b-a):
    ret = (c-b)-(b-a)
    #else:
    #    ret = (c-b)/abs(b-a)
    return ret


class SkynetStrategies(object):
    '''
    classdocs
    '''
    
    def financePredFunc(self, prices):
        merged = [ [] for p in prices ]
        for ti in self.tiFuncs:
            inds = ti(np.array(prices))
            #print inds
            #print prices
            inds = [0.0]*(len(prices)-len(inds)) + list(inds)
            merged = [ (t+[i]+[ shape(i) for shape in self.shapeFuncs]) for i,t in zip(inds,merged) ]
        return merged

    def __init__(self):
        '''
        Constructor
        '''
        self.analyzer = PortfolioAnalyzer()
        self.analyzer.loadAndComputeStatistics()
        self.PERIOD = 14
        
    def equalMargin(self):        
        coins = CoinDB.coinSets['margin']   
        pfolio = dict([ (coin,1./len(coins)) for coin in coins ])
        self.analyzer.portfolioAnalysis(pfolio, minReturn=0.0, maxSigma=0.0, testing=True)

    def altMarginByCap(self):     
        pfolio = self.cap
        self.analyzer.portfolioAnalysis(pfolio, minReturn=0.0, maxSigma=0.0, testing=True)

    def minRiskStrategy(self):     
        pfolio = self.minRisk
        self.analyzer.portfolioAnalysis(pfolio, minReturn=0.0, maxSigma=0.0, testing=True)


    def addTechnicalIndicators(self, pfolioRets):
        newDict = {}
        for coin,rets in pfolioRets:
            X,Y = self.addTechnicalIndicatorsRets( rets )
            # see one step into the future
            Y = Y[1:]
            X = X[:-1]
            newDict[coin] = rets
        return newDict
    

    def smartIndicator( self, rets ):

        prices = []
        cap = 1.0
        for ret in rets:
            cap *= 1.0+ret
            prices.append( cap )        
        
        merged = self.financePredFunc( prices )
        #for p,t in zip(prices,merged):
        #    print p,t
        #print
        # do the machine learning
        X,Y = merged[self.PERIOD:], rets[self.PERIOD:]
        #print X
        #print Y
        #print 
        Y = Y[1:]
        lastX = X[-1]
        X = X[:-1]
        nextValueFunc = predFunc(X, Y)
        return nextValueFunc( lastX ) #- 0.5
            
    def estimateNextReturn(self, coin,d,rets ):
        raise Exception("Not Implemented!")
            
    def longShortML(self, top=1, onlyNeutral=True, leverage=1.0, roundTripFee=0.0, minimumConvexity=0.0, riskControl = 0.01):
        coins = CoinDB.coinSets['margin']    
        pfolio = dict([ (coin,1./len(coins)) for coin in coins ])
        self.analyzer.portfolioAnalysis(pfolio, minReturn=0.0, maxSigma=0.0, testing=True)
        
        pfolioRets = self.analyzer.pfolioRets
        lenDays = len(pfolioRets[0][1])
        print 'lenDays = ',lenDays
        
        capital = 1.0
        capitalWithControl = 1.0
        prevCapital = 1.0
        prevCapitalWithControl = 1.0
        pfolio = {}
        longShortRetsWithControl = []
        longShortRets = []
        active = True
        maxCapital = capital
        samePfolio = False
        for d in range(2,lenDays):
            
            dailyDict = {}
            
            for coin,rets in pfolioRets:

                # close position
                if coin in pfolio:
                    capital += sign(pfolio[coin])*pfolio[coin] * (1.0+(rets[d]*leverage-roundTripFee))
                    if active:
                        capitalWithControl += sign(pfolio[coin])*pfolio[coin] * (1.0+(rets[d]*leverage-roundTripFee))
                    del pfolio[coin]

                
                # Calculate Estimated Returns for next Period
                self.estimateNextReturn(coin,d,rets)
                x0,x1,x2 = rets[d-2],rets[d-1],rets[d]
                cconvex = convexityW(x0, x1, x2)
                dailyDict[coin] = cconvex
                
            #print '-'*80
            #print capital/prevCapital - 1.0, capital
            #print 'EFFECTIVE=',capitalWithControl
            print 'CAPITAL=%f  RETURN=%f'%(capitalWithControl,capitalWithControl/prevCapitalWithControl - 1.0)
            #print 'MARGINBENCH=',capital
            #print 'MAXCAPITAL=',maxCapital
            #print 'ACTIVE=',active
            
            if capitalWithControl > maxCapital:
                maxCapital = capitalWithControl
            
            if active and capitalWithControl < maxCapital*(1.0-riskControl):
                active = False
            
            if not active and capital >= maxCapital:
                active = True

            if prevCapitalWithControl == 0:
                capital = 0.0
                capitalWithControl = 0.0
                continue
            longShortRets.append( capital/prevCapital - 1.0 )
            longShortRetsWithControl.append( capitalWithControl/prevCapitalWithControl - 1.0 )
            #print capital
            #print 'Step = %d  Capital = %.2f' % (d,capital)
                
            cx = list( dailyDict.iteritems() )
            cx.sort(key=lambda x:x[1],reverse=True)
            #for t in cx:
                #if t[1] < 0.0:
            #    print t
            #print '-'*80
            
            pos = [ c for c,convex in cx[:top] if convex > 0 and convex>minimumConvexity]
            neg = [ c for c,convex in list(reversed(cx))[:top] if convex < 0 and convex < -minimumConvexity ]
            #print 'Top %d positive convexity and top %d negative convexity:' % (top,top)
            #print 'pos=',pos
            #print 'neg=',neg

            # check neutrality
            if onlyNeutral and not (len(pos)>=top and len(neg)>=top):
                # dont invest this period, because there is symmetric investment long/short
                continue
            #    active = False
            
            # open positions, positive for long, negative for short
            n = len(pos) + len(neg)
            pfolio = dict([ (c,capital/n) for c in pos] + [ (c,-capital/n) for c in neg])
            #print pfolio
            prevCapitalWithControl = capitalWithControl
            prevCapital = capital
            if prevCapital <= 0.0:
                print 'ERROR: Capital has gone Negative or Zero (bankrupt!).'
                print 'Capital = %f' % prevCapital
            capital = 0.0
            if active:
                capitalWithControl = 0.0
            #print pfolio
           
           
        rho,sigma = mean(longShortRetsWithControl), pstdev(longShortRetsWithControl) 
        if sigma==0 or sigma==0.0:
            sigma = 100000.0
        return {'capitalMultiplication':prevCapitalWithControl, 'dailyReturn':rho, 'dailySigma':sigma, 'dailySharpe':rho/sigma} 


if __name__ == '__main__':
    
    skynet = SkynetStrategies()
    
    # HYPER IA
    print skynet.longShortML(top=10,leverage=2.5,roundTripFee=0.005, onlyNeutral=False, minimumConvexity=0.01, riskControl=0.001)
