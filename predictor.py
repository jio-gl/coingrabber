'''
Created on Jul 13, 2017

@author: joigno
'''

import csv,copy
import numpy as np
from math import log,exp

from sklearn.metrics import precision_score, recall_score
from sklearn import preprocessing

from fit import predFunc,predFuncSVM,predFuncDeep,predFuncLogisticCV
from technical_indicators import *
from technical_indicators import technical_indicators
from grid import runGridSearch

from sklearn import linear_model


def sign(x):
    if x==0.0:
        return 0
    else:
        return int(abs(x)/x)

def signBinary(x):
    if x==0.0:
        return 0
    else:
        if int(abs(x)/x)==-1:
            return 0
        else:
            return 1

    
    
def logreturns(prices):
    initLen = len(prices)
    prices = [ p==0.0 and 1.0 or p for p in prices]
    logrets = map(log,prices)
    final = []
    prevVal = logrets[0]
    for l in logrets[1:]:
        final.append( l-prevVal )
        #print l-prevVal
        prevVal = l
    final2 = final
    assert( initLen == len(final2)+1 )
    return final2

def simplereturns(prices):
    prices = [ p==0.0 and 1.0 or p for p in prices]
    final = []
    prevVal = prices[0]
    for l in prices[1:]:
        final.append( l/prevVal - 1.0 )
        prevVal = l
    final2 = final
    return final2


class LinearPredictor(object):
    '''
    classdocs
    '''


    def __init__(self, csvFnames):
        '''
        Constructor
        '''
        self.csvFnames = csvFnames
        
        
    def loadData(self, lastNPeriods=30):
        self.rows = []
        for csvFname in self.csvFnames:
            
            with open(csvFname) as csvfile:
                reader = csv.DictReader(csvfile)
                count = 0
                for row,index in zip(reader,range(lastNPeriods)):
                    #print index
                    newRow = []
                    #print row
                    if 'PriceBTC' in row and row['PriceBTC'] == 'PriceBTC':
                        continue
                    newRow.append( float(row['PriceBTC']) )
                    newRow.append( float(row['MarketCap']) )
                    newRow.append( float(row['Volume']) )
                    if len(self.rows) <= index:
                        self.rows.append(newRow)
                    else:
                        self.rows[index] += newRow
                    count += 1
                print 'Added %d data points for file %s.' % (count,csvFname)
                    #print self.rows[index]
        self.rows.reverse()
        self.lastNPeriods = lastNPeriods
        #for r in self.rows:
        #    print r
        
        
    def computeLogReturns(self, days=1):
        
        richRows = [ [] ]*self.lastNPeriods
        mainCoinPrices = np.array([ r[0] for r in self.rows]) 
        mainCoinPricesReturns = logreturns(mainCoinPrices)   
        for fname,index in zip(self.csvFnames,range(len(self.csvFnames))):
            print 'Computing log returns and technical indicators for %s ...' % fname
            
            print len(self.rows)
            prices = np.array([ r[index*3+0] for r in self.rows]) 
            final0 = logreturns(prices)        
    
#            marketCap = np.array([ r[index*3+1] for r in self.rows]) 
#            final1 = logreturns(marketCap)        
#     
            volume = np.array([ r[index*3+2] for r in self.rows]) 
            final2 = logreturns(volume)        
            
            
    
            richRows = [ row+[lg] for row,lg in zip(richRows,final0) ]
#            richRows = [ row+[lg] for row,lg in zip(richRows,final1) ]
            richRows = [ row+[lg] for row,lg in zip(richRows,final2) ]

            prices = [ r[index*3+0] for r in self.rows]
            period = 21
            roc = [1.0]*period + list(technical_indicators.roc( prices, period ))
            assert( len(roc) == len(self.rows) )
            period = 14        
            rsi = [50.0]*period + list(technical_indicators.rsi( np.array(prices), period=period ))
            assert( len(rsi) == len(self.rows) )
            period = 12        
            ema12 = [1.0]*(period-1) + list(technical_indicators.ema( np.array(prices), period=period ))
            assert( len(ema12) == len(self.rows) )
            period = 26
            ema26 = [1.0]*(period-1) + list(technical_indicators.ema( np.array(prices), period=period ))
            assert( len(ema26) == len(self.rows) )
              
            richRows = [ list(row)+[lg] for row,lg in zip(richRows,roc[1:]) ]
            richRows = [ list(row)+[lg] for row,lg in zip(richRows,rsi[1:]) ]
            richRows = [ list(row)+[e12-e26] for (row,e12),e26 in zip(zip(richRows,ema12[1:]),ema26[1:]) ]
    
        richRows = preprocessing.scale(richRows)
            
            #self.rows = preprocessing.scale(self.rows)
    
        self.X = richRows[:-1] #[ r[1:] for r in self.rows[:-1] ]
        self.Y = mainCoinPricesReturns[1:] #[ r[0] for r in self.rows[1:] ]
        
        print 'X =', len(self.X)
        print 'Y =', len(self.Y)
        print 'Y = ', self.Y
            
            #self.X = preprocessing.scale(self.X)
            #self.Y = preprocessing.scale(self.Y)
            
            #min_max_scaler = preprocessing.MinMaxScaler()
            #self.X = min_max_scaler.fit_transform(self.X)
            #self.Y = min_max_scaler.fit_transform(self.Y)
            
            #for x,y in zip(self.X,self.Y):
            #    print x,y

    
    def generatePredictor(self, X,Y, generator=None):
        print 'Generating predictor ...'
        self.predictor = predFunc(X, Y, generator=generator) #predFunc(X, Y)
        return self.predictor

    def split(self, fraction=0.75):
        l = int(round(len(self.X) * fraction))
        return self.X[:l], self.Y[:l], self.X[l:], self.Y[l:]


    def testPredictor(self, predictor, X, Y, threshold=0.0):
        y_true, y_pred = [], []
        sameDirection = 0
        for x,y in zip(X,Y):
            py = predictor(x)
            if abs(py) < threshold:
                continue
            print'------------------'
            print 'Observed X = ',x
            print 'Observed Val = ',y
            y_true.append( sign(y) )
            y_pred.append( sign(py) )
            print 'Predictd Val = ',py
            print 'Same Direction    = ',round(py)==round(y)
            if sign(py)==sign(y):
                sameDirection += 1
            print 'Abs Diff     = ',abs(py-y) 
            
        print '-'*80
        print 'Active predictions = ',len(y_true)
        print 'Total points = ',len(Y)
        print 'PRECISION = ',precision_score(y_true, y_pred, average='micro')
        print 'RECALL = ',precision_score(y_true, y_pred, average='micro')
        print 'HIT RATIO = ',float(sameDirection)/len(y_true)

    def completeTestPredictor(self, generator=None):
        X_train, Y_train, X_test, Y_test = self.split()
        predictor = self.generatePredictor(X_train,Y_train,generator=generator)
        assert( len(X_test)+len(X_train) == len(Y_test)+len(Y_train) )
        print len(X_test)+len(X_train) 
        self.testPredictor(predictor,X_test,Y_test)

if __name__ == '__main__':
    
    #pred = LinearPredictor('./data/6Hour_buyOrSell_aggregated_.bitfinexUSD.csv')#5min_ardor.csv')
    pred = LinearPredictor([
        './data/1d_dogecoin.csv', # 57.0% dash stellar ripple clams
         #'./data/1d_maidsafecoin.csv', # 60.2 % factom
         #'./data/1d_factom.csv', # 56.5 % ethereum dash
         #'./data/1d_ethereum.csv', # 61.5 % dash
         './data/1d_dash.csv', # 57.7 % ethereum dogecoin
         #'./data/1d_litecoin.csv', # 59.7 % stellar monero clams dash
        './data/1d_stellar.csv', # 62.2 % dash
        #'./data/1d_bitshares.csv', # 59.0 % ripple clams stellar dogecoin
        './data/1d_ripple.csv', # 57.1 % clams stellar maidsafecoin dogecoin
        #'./data/1d_monero.csv', # 55.9 % clams bitshares ripple dogecoin
        './data/1d_clams.csv', # 55.9 % stellar litecoin ripple dogecoin
        ])
    pred.loadData(lastNPeriods=1000)
    pred.computeLogReturns(days=1)
    print 'X ', len(pred.X)
    print 'Y ', len(pred.Y)
    
    #runGridSearch(pred.X,pred.Y)
    #searchLogistic(pred.X,pred.Y)
    
    gens = [
#         'linear_model.ARDRegression',
#         'linear_model.BayesianRidge',
#         'linear_model.ElasticNet',
#         'linear_model.ElasticNetCV',
#         'linear_model.Lars',
#         'linear_model.LarsCV',
#         'linear_model.Lasso',
#         'linear_model.LassoCV',
#         'linear_model.LassoLars',
#         'linear_model.LassoLarsCV',
#         'linear_model.LassoLarsIC',
        'linear_model.LinearRegression',
#         'linear_model.LogisticRegression',
#         'linear_model.OrthogonalMatchingPursuit',
#         'linear_model.PassiveAggressiveRegressor',
        #'linear_model.Perceptron',
#         'linear_model.Ridge',
#         'linear_model.RidgeCV',
#         'linear_model.SGDRegressor',
#         'linear_model.TheilSenRegressor',
        ]
    
    for method in gens:    
        gen = eval(method)
        pred.completeTestPredictor(generator=gen)
        print method
