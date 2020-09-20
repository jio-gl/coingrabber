'''
Created on Apr 18, 2017

@author: joign
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


class BasicStrategies(object):
    '''
    classdocs
    '''

    cap = {
            'ethereum': 0.626751939039325,
            'ripple': 0.16886651245067355,
            'dash': 0.07130221798884202,
            'litecoin': 0.07062185331337598,
            'monero':0.040957953463056196,
            'maidsafecoin':0.013199074704041367,
            'factom':0.008300449040685807, 
        }
    
    # 2017-04-24 Minimum Risk
    minRisk = {
                'bitcoin' : 0.544,
                'bitshares' : 0.081,
                'ethereum' : 0.075,
                'gamecredits' : 0.056,
                'decred' : 0.046,
                'syscoin' : 0.035,
                'ethereum-classic' :0.033,
                'monero' : 0.029,
                'storjcoin-x' : 0.021,
                'maidsafecoin' : 0.019,
                'rubycoin' : 0.016,
                'stellar' : 0.012,
                }
    
    # PortfolioStartDate=2017-07-05
    maxSharpe =  dict([('bitcoin', float('0.218634')),
                       ('dash', float('0.129257')), 
                       ('decred', float('0.107269')), 
                       ('factom', float('0.106231')), 
                       ('steem', float('0.094044')), 
                       ('maidsafecoin', float('0.088666')), 
                       ('litecoin', float('0.085239')), 
                       ('dogecoin', float('0.077091')), 
                       ('gamecredits', float('0.072112')), 
                       ('iocoin', float('0.018290')), 
                       ('monero', float('0.003168')),

                       ])

    PERIOD = 7
    tiFuncs = [
                    #lambda prices : tai.rsi(prices)/100.0 ,
                    #lambda prices : tai.rsi(prices)/100.0-1.0,
                    #lambda prices : tai.sma(prices,period=14),
                    #lambda prices : tai.wma(prices,period=14),
                    #lambda prices : tai.ema(prices,period=14),
                    #lambda prices : tai.ma_env(prices,14, 0.1, 4)[4],
                    #lambda prices : tai.bb(prices,period=14)[3],
                ]
    shapeFuncs = [
                #logShape,
                #expShape,
                #sigmoid,
            ]
    
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
            
            
    def longShortMomentum(self, top=1, onlyNeutral=True, leverage=1.0, roundTripFee=0.0, minimumConvexity=0.0, riskControl = 0.01):
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

        
    def perCapitalization(self, top=20, onlyNeutral=True, leverage=1.0, roundTripFee=0.0, riskControl = 0.01, equallyDistributed=False):

        coins = CoinDB.coinSets['cap'][:top]
        coindb = CoinDB()
        coinCaps = {}
        print coins
        
        pfolioCaps = [ (coin,coindb.loadPriceList(coin, timeIncreasing=True, useFilter=False, field='MarketCap')) for coin in coins ]
        minLen = min([ len(caps) for coin,caps in pfolioCaps ])
        minLen = 180
        print minLen
        pfolioCaps = [ (coin,caps[-minLen:]) for coin,caps in pfolioCaps ]
        totalCaps = []
        for coin,caps in pfolioCaps:
            print coin
            print caps
        for day in range(minLen):
            totalCaps.append( sum([caps[day] for coin,caps in pfolioCaps ]) )
            for coin,caps in pfolioCaps:
                caps[day] = float(caps[day]) / totalCaps[-1]
        print 'TOTAL:'
        print totalCaps
        for coin,caps in pfolioCaps:
            print coin
            print caps
        
        pfolioCaps = dict(pfolioCaps)
#        return    
        
        pfolio = dict([ (coin,1./len(coins)) for coin in coins ])
        self.analyzer.portfolioAnalysis(pfolio, minReturn=0.0, maxSigma=0.0, testing=True, maxDaysTesting=minLen)
        
        pfolioRets = self.analyzer.pfolioRets
        pfolioRets = [ (coin,rets[-minLen:]) for coin,rets in pfolioRets ]
        lenDays = len(pfolioRets[0][1])
        print 'lenDays = ',lenDays
        
        #print 'Prices =',coindb.loadPriceList(coin)[-minLen:]
        
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
        for d in range(2,minLen):
            
            dailyDict = {}
            
            for coin,rets in pfolioRets:

                # close position
                if coin in pfolio:
                    
                    rets = rets[-minLen:]
                    
                    # diff fee
                    diffCap = abs(pfolioCaps[coin][d] - pfolioCaps[coin][d-1])
                    diffFee = diffCap * roundTripFee
                    print 'DiffWeight = %f  DiffFee = %f' % (diffCap,diffFee)
                    #print 'Price = ',coindb.loadPriceList(coin)[-minLen:][d]
                    capital += sign(pfolio[coin])*pfolio[coin] * (1.0+(rets[d]*leverage-diffFee))
                    if active:
                        capitalWithControl += sign(pfolio[coin])*pfolio[coin] * (1.0+(rets[d]*leverage-roundTripFee))
                    del pfolio[coin]

                
                
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
              
            if not equallyDistributed:  
                pfolio = dict([ (c,capital*pfolioCaps[c][d]) for c in coins])
            else:
                pfolio = dict([ (c,capital/top) for c in coins])
            print pfolio
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
        totalSharpe = minLen*rho / (sqrt(minLen)*sigma)
        return {'capitalMultiplication':prevCapitalWithControl, 'dailyReturn':rho, 'dailySigma':sigma, 'dailySharpe':rho/sigma, 'totalSharpe':totalSharpe} 
        
    def portfolioDailyRebalance(self, weights=None, leverage=1.0, roundTripFee=0.0, equallyDistributed=False):

        coins = CoinDB.coinSets['vip']
        coindb = CoinDB()
        coinCaps = {}
        print coins
        
        pfolioCaps = [ (coin,coindb.loadPriceList(coin, timeIncreasing=True, useFilter=False, field='MarketCap')) for coin in coins ]
        minLen = min([ len(caps) for coin,caps in pfolioCaps ])
        minLen = 90
        print minLen
        pfolioCaps = [ (coin,caps[-minLen:]) for coin,caps in pfolioCaps ]
        
        pfolioCaps = dict(pfolioCaps)

        
        pfolioCaps = [ (coin,coindb.loadPriceList(coin, timeIncreasing=True, useFilter=False, field='MarketCap')) for coin in coins ]
        minLen = min([ len(caps) for coin,caps in pfolioCaps ])
        minLen = 90
        print minLen
        
        pfolio = dict([ (coin,1./len(coins)) for coin in coins ])
        self.analyzer.portfolioAnalysis(pfolio, minReturn=0.0, maxSigma=0.0, testing=True, maxDaysTesting=minLen)
        
        pfolioRets = self.analyzer.pfolioRets
        pfolioRets = [ (coin,rets[-minLen:]) for coin,rets in pfolioRets ]
        lenDays = len(pfolioRets[0][1])
        print 'lenDays = ',lenDays
        pfolioRetsDic = dict(pfolioRets)
        
        #print 'Prices =',coindb.loadPriceList(coin)[-minLen:]
        
        capital = 0.0
        capitalWithControl = 0.0
        prevCapital = 1.0
        import copy
        if not equallyDistributed:  
            print 'W = ',weights
            pfolio = copy.deepcopy(weights)
        else:
            pfolio = dict([ (c,1.0/len(coins)) for c in coins])
        print 'W = ',weights
        print 'P = ',pfolio
        longShortRets = []
        maxCapital = capital
        samePfolio = False
        for d in range(2,minLen-1):
            
            dailyDict = {}
            
            for coin,rets in pfolioRets:

                # close position
                if coin in pfolio:
                    
                    rets = rets[-minLen:]
                    
                    # diff fee
                    simpleReturn = abs(rets[d])
                    diffFee = simpleReturn * roundTripFee
                    #print 'Coin = %s  simpleReturns = %f  DiffFee = %f' % (coin, rets[d],diffFee)
                    #print 'Price = ',coindb.loadPriceList(coin)[-minLen:][d]
                    capital += prevCapital * sign(pfolio[coin])*pfolio[coin] * (1.0+(rets[d]*leverage-diffFee))
                    del pfolio[coin]

                
                
            #print '-'*80
            #print capital/prevCapital - 1.0, capital
            #print 'EFFECTIVE=',capitalWithControl
            print 'CAPITAL=%f  RETURN=%f'%(capital,capital/prevCapital - 1.0)
            #print 'MARGINBENCH=',capital
            #print 'MAXCAPITAL=',maxCapital
            #print 'ACTIVE=',active
            
            if capitalWithControl > maxCapital:
                maxCapital = capitalWithControl
            
            longShortRets.append( capital/prevCapital - 1.0 )
            
            if not equallyDistributed:  
                print 'W = ',weights
                pfolio = copy.deepcopy(weights)
            else:
                pfolio = dict([ (c,1.0/len(coins)) for c in coins])
            print pfolio
            prevCapital = capital
            if prevCapital < 0.0:
                print 'ERROR: Capital has gone Negative or Zero (bankrupt!).'
                print 'Capital = %f' % prevCapital
            capital = 0.0
           
           
        rho,sigma = mean(longShortRets), pstdev(longShortRets) 
        if sigma==0 or sigma==0.0:
            sigma = 100000.0
        totalSharpe = minLen*rho / (sqrt(minLen)*sigma)
        return {'capitalMultiplication':prevCapital, 'dailyReturn':rho, 'dailySigma':sigma, 'dailySharpe':rho/sigma, 'totalSharpe':totalSharpe} 
        


if __name__ == '__main__':
    
    basic = BasicStrategies()
    
#     rets = [
#             -0.01,
#             -0.01,
#             -0.01,
#             -0.01,
#             -0.01,
#             -0.01,
#             -0.01,
#             -0.01,
#             -0.01,
#             -0.01,
#             -0.01,
#             -0.01,
#             -0.01,
#             -0.01,
#             -0.01,
#             -0.01,
#             -0.01,
#             -0.01,
#             -0.01,
#             -0.01,
#             -0.01,
#             -0.01,
#             -0.01,
#             -0.01,
#         ]
#     print basic.smartIndicator(rets)
    #for t in  basic.addTechnicalIndicatorsRets(rets):
    #    print t
    
    #basic.minRiskStrategy() #equalMargin()#altMarginByCap()#equalMargin()
    #for ret in basic.analyzer.pfolioWRets:
    #    print ret

    # topN= 2 minConv 0.016  BEST Return
    # topN=9  minConv 0.027 Best Sharpe
    #print basic.longShortMomentum(top=9,leverage=2.5,roundTripFee=0.005, onlyNeutral=False, minimumConvexity=0.027, riskControl=0.001)
    
    #print basic.longShortMomentum(top=2,leverage=2.5,roundTripFee=0.0025, onlyNeutral=True, minimumConvexity=0.001, riskControl=0.001)
    #print basic.perCapitalization(top=10,leverage=2.5,roundTripFee=0.0025, riskControl=1.0, equallyDistributed=True)
   
    #print basic.portfolioDailyRebalance(weights=basic.maxSharpe, leverage=1.0, roundTripFee=0.0025, equallyDistributed=True)

    
    # HYPER smartIndicator
    print basic.longShortMomentum(top=10,leverage=2.5,roundTripFee=0.005, onlyNeutral=False, minimumConvexity=0.01, riskControl=0.001)
    
    
    
    # search for better minimum convexity parameter
#     res = []
#     maxSharpe = 0.0
#     maxTopN = None
#     maxMinConv = None
#     maxRet = None
#     for topN in range(1,10):
#         for i in range(1,200):
#             r = basic.longShortMomentum(top=topN,leverage=2.5,roundTripFee=0.005, onlyNeutral=False, minimumConvexity=0.001*i)
#             if r[3] > maxSharpe and r[1]>0.0 and r[0]>100.0:
#                 maxSharpe = r[3]
#                 maxTopN = topN
#                 maxMinConv = 0.001*i
#                 maxRet = r[0]
#                 'NEW!!!!!!!!!!!!!!!!!!!!!!!!!!!! SHARPE MAX = ',maxSharpe
#             res.append( (r,0.001*i ) )
#     for r,mC in res:
#         if r[3] == maxSharpe:
#             print 'MAXSharpe = %f   MINIMUMCONVEXITY = %f' % (maxSharpe,mC)
#             print r
#     print 'besRet = %f   maxTopN = %d  bestMinConvexity = %f' % (maxRet, maxTopN,maxMinConv)

    
    
    
    
#     print convexityW(1, 2, 3)
#     print convexityW(3,2,1)
# 
#     print convexityW(1, 2, 4)
#     print convexityW(4, 2, 1)
# 
#     print convexityW(1, 2, 1)
#     print convexityW(2, 1, 2)
#     
#     print convexityW(1, 0, -1)
#     print convexityW(-1, 0, 1)
# 
#     print convexityW(1, 0, -2)
#     print convexityW(-2, 0, 1)
#     
#     print convexityW(-1, -2, -4)
#     print convexityW(10, 9, 5)

