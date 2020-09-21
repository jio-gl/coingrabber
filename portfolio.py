'''
Created on Feb 22, 2017

@author: joigno
'''

import csv
from math import sqrt,exp,log

from coins import CoinDB
from stocks import get_returns
from dateconfig import DateRange
from datetime import datetime,timedelta

def calcReturns( vals, window=1 ):
    ret = []
    if len(vals) == 0:
        return ret
    for i in range(len(vals)/window - 1):
        ratio = ( vals[(i+1)*window] / float(vals[(i)*window]) ) - 1.0
        ret.append( ratio )
    return ret

def calcLogReturns( vals, window=1 ):
    ret = []
    if len(vals) == 0:
        return ret
    for i in range(len(vals)/window - 1):
        ratio = log( vals[(i+1)*window] / float(vals[(i)*window]) )
        ret.append( ratio )
    return ret

def median(lst):
    quotient, remainder = divmod(len(lst), 2)
    if remainder:
        return sorted(lst)[quotient]
    return sum(sorted(lst)[quotient - 1:quotient + 1]) / 2.

def ave(vals,minusOne=False):
    if len(vals)==0:
        return 0.0
    return sum(vals)/(minusOne and len(vals)-1 or len(vals))


class PortfolioAnalyzer(object):
    '''
    classdocs
    '''
    
    lastNPoints = 3650

    def __init__(self,):
        '''
        Constructor
        '''
        self.returns = {}
        self.medians = {}
        self.sigmas = {}
        self.sigmaChances = {}
        self.correlations = {}
    
        self.db = CoinDB()
        self.assets = self.db.coins #+ self.db.stocks
        
    
    def loadAndComputeStatistics(self):
        
        self.rets = {}
        self.computeReturns()
        self.computeSigmas()
        self.computeCorrelations()
        
    
    def computeReturns(self):
        
        # compute returns
        for a in self.assets:
            #vals = self.db.prices(a)
            #print vals
            #print '*'*80
            #vals = vals[-self.lastNPoints:]
            rvals = get_returns(a)
            #rvals = calcReturns(vals)
            #rvals = sorted(rvals)
            #print rvals
            #break
            self.rets[a] = rvals
            ret = self._computeReturns(rvals,a)
            self.returns[a] = ret

            
    def _computeReturns(self, rvals, name):
            
        ret = ave(rvals)

        # above average returns chance.
        #aboveavechance = sum([ 1. for r in rvals if r > ret])/len(rvals)
        #aboveAveRetAve = ave([ r for r in rvals if r > ret])
        #positiveChance = sum([ 1. for r in rvals if r > 0.0])/len(rvals)
        #positiveRetAve = ave([ r for r in rvals if r > 0.0])

        #print 'UPSIDE'                
        
        print 'Average Returns for ',name,' is %.4f percent'%(ret*100)
        
        #print 'Above-average returns chance =  %.2f percent' % (aboveavechance*100.0)
        #print 'Above-average returns average return =  %.2f percent' % (aboveAveRetAve*100.0)
        #print 'Positive returns chance =  %.2f percent' % (positiveChance*100.0)
        #print 'Positive returns average return =  %.2f percent' % (positiveRetAve*100.0)
        #print
        #print
        #print
        
        return ret
    
    

    def computeSigmas(self):
        
        #print 'sigmas (standard deviation) ...'
        # sigmas
        for a in self.assets:
            #print vals
            #print '*'*80
            rA = self.returns[a]
            rvals = self.rets[a]
            
            sigma = self._computeSigmas(rA,rvals,a)
            self.sigmas[a] = sigma
            
            
    def _computeSigmas(self, rA, rvals, name):
        
        variance = ave( [(rA-r)**2 for r in rvals] , minusOne=True)
        sigma = sqrt( abs(variance) )
        # Chances of average return between average minus sigma and average plus sigma
        #sigmaRangeChance = sum([ 1. for r in rvals if (r > rA+sigma or r < rA-sigma)])/len(rvals)
        #print 'RISK AS RETURNS DISPERSION.'
        
        #print 'Standard Deviation (sigma) ',name,'%.2f percent'%(sigma*100)
        
        #print 'Sigma = %.2f percent'%(sigma*100)
        low = rA-sigma
        high = rA+sigma
        #print 'Chances of return OUTSIDE [average-sigma,average+sigma] percent = [%.2f,%.2f] are ONLY %.2f percent' % (low*100,high*100,sigmaRangeChance*100)

        #print 'RISK AS SUB-AVERAGE RETURNS'
        # sub average returns chance.
        #subavechance = sum([ 1. for r in rvals if r < rA])/len(rvals)
        #subAveRetAve = ave([ r for r in rvals if r < rA])
        #print 'Sub-average returns chance =  %.2f percent' % (subavechance*100.0)
        #print 'Sub-average returns average return =  %.2f percent' % (subAveRetAve*100.0)
        
        #print 'RISK AS NEGATIVE RETURNS'
        # Negative returns chance.
        #negChance = sum([ 1. for r in rvals if r < 0.0])/len(rvals)
        #negRetAve = ave([ r for r in rvals if r < 0.0])
        #print 'Negative returns chance =  %.2f percent' % (negChance*100.0)
        #print 'Negative returns average return =  %.2f percent' % (negRetAve*100.0)
        #print ''
        return sigma
        
    def computeCorrelations(self):
        
        print
        print 'correlations...'
        corrList = []
        for a in self.assets:
            for b in self.assets:
                #print a,b
                if b == a:
                    self.correlations[(a,b)] = 1.0
                    continue
                retsA = self.rets[a]
                retsB = self.rets[b]
                rA = self.returns[a]
                rB = self.returns[b]
                # changes to calcula simultaneusly
                if len(retsA) > len(retsB):
                    retsA = retsA[-len(retsB):]
                else:
                    retsB = retsB[-len(retsA):]
                rAB = sum([ (rA-r)**2 for r in retsA ])
                rAB *= sum([ (rB-r)**2 for r in retsB ])
                if rAB == 0.0:
                    print a,b,'%.2f'%0.0
                    continue
                rAB = 1.0/sqrt(rAB)
                rAB *= sum( (rA-ra)*(rB-rb) for ra,rb in zip(retsA,retsB) )
                self.correlations[(a,b)] = rAB
                #print a,b,'%.4f'%rAB
                corrList.append( (rAB,a,b) )
        #for t in sorted(corrList):
        #    print t
                 
    def portfolioReturn(self, mypfolio):
        return sum([ w*self.returns[coin] for coin,w in mypfolio.iteritems() ])
        
    
    def portfolioStandardDev(self, mypfolio):
        variance = 0.0
        for coinA,wA in mypfolio.iteritems():
            for coinB,wB in mypfolio.iteritems():
                variance += wA * wB * self.correlations[(coinA,coinB)] * self.sigmas[coinA] * self.sigmas[coinB]
        return sqrt( abs(variance) )
                
    
    def portfolioAnalysis(self, mypfolio, minReturn, maxSigma, maxDaysTesting=None,testing=False):
        # Portfolio Returns
        pfolioRet = self.portfolioReturn(mypfolio)
        print 'Analyzing portfolio ...'
        print mypfolio
        print
        print 'Portfolio Returns = %.2f percent' % (pfolioRet*100.0)
        print 
        print 'Analyzing Portfolio Risk ..'
        pfolioRets = [ (coin,self.rets[coin]) for coin,w in mypfolio.iteritems() ]
        minLen = min([ len(rets) for coin,rets in pfolioRets ])
        if maxDaysTesting:
            minLen = min(minLen,maxDaysTesting)
        pfolioRets = [ (coin,rets[-minLen:]) for coin,rets in pfolioRets ]
        
        pfolioWRets = []
        finalRet = 1.0
        maxDrawdown = 1.0
        for i in range(minLen):
            dayRet = sum([ mypfolio[coin]*rets[i] for coin,rets in pfolioRets])
            pfolioWRets.append( dayRet )
            finalRet *= 1.0+dayRet
            if finalRet < maxDrawdown:
                maxDrawdown = finalRet
            #print finalRet
        finalRet = finalRet - 1.0
        maxDrawdown = maxDrawdown - 1.0
        finalAve = self._computeReturns(pfolioWRets, str(mypfolio))
        sigma = self._computeSigmas(pfolioRet, pfolioWRets, str(mypfolio) )
        print 'FINAL REPORT (for fixed Minimum Return of %.4f percent):' % (minReturn*100.0)
        start = datetime(year=DateRange.endYear,month=DateRange.endMonth,day=DateRange.endDay)
        start = start - timedelta(days=minLen)
        print 'Observations for %d Days (Year-Month-Day) Start = %d-%d-%d  and End = %d-%d-%d' % (minLen,start.year,start.month,start.day,DateRange.endYear,DateRange.endMonth,DateRange.endDay)
        #print 'Observed Average Return per Day = %.2f percent' % (finalAve*100.0)
        print 'Expected Average Return per Day = %.4f percent' % (minReturn*100.0)
        print 'Observed Average Return per Day = %.4f percent' % (finalAve*100.0)
        print 'Expected Standard Deviation per day = %.4f percent' % (maxSigma*100.0)
        print 'Observed Standard Deviation per day = %.4f percent' % (sigma*100.0)
        print 'Expected Return in %d Days = %.4f percent' % (minLen, (finalAve*minLen*100.0))
        print 'Observed Return in %d Days = %.4f percent' % (minLen,finalRet*100.0)
        try:
            print 'Expected SHARPE RATIO = %.4f' % ( finalAve*minLen / (maxSigma*sqrt(minLen)) )
            print 'Observed SHARPE RATIO = %.4f' % ( finalRet / (sigma*sqrt(minLen)) )
            print 'Observed SHARPE RATIO = %.4f' % ( finalRet / (sigma*sqrt(minLen)) )
        except:
            pass
        
        self.pfolioWRets = pfolioWRets
        self.pfolioRets = pfolioRets
        
        print '-'*80
        #return finalRet, sigma*sqrt(minLen)
        if not testing:
            return (finalAve+minReturn)/2.,(sigma+maxSigma)/2.,maxDrawdown,minLen             
        else:
            return finalRet,sigma*sqrt(minLen),maxDrawdown,minLen
    
            
if __name__ == '__main__':
    
    pfolio = PortfolioAnalyzer()
    pfolio.loadAndComputeStatistics()
    #p = {'nem': 0.06249055663832853, 'factom': 0.10389908862501246, 'bitcoin': 0.2030021970065782, 'dash': 0.317480548857279, 'ethereum': 0.0719461976790565, 'dogecoin': 0.03328743017533109, 'gamecredits': 0.2073376851097738}
    #pfolio.portfolioAnalysis(p)
