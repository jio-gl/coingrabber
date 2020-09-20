'''
Created on Dec 30, 2017

@author: joign
'''

import json,time
from math import sqrt

# 1) Poner la lista de coins en un objeto


class VirtualBot(object):
    
    TAKER_FEE = 0.1 + 0.15
    
    coin2ticker = {
        'ETH' : 'ethereum',
        'XMR' : 'monero',
        'LTC' : 'litecoin',
        'DASH' : 'dash',
        'ZEC' : 'zcash',
            
        }
    
    def __init__(self, coins,size,debug=False):
        self.prices = {}
        self.index = 0
        self.size = size
        self.available = {}
        self.debug = debug
        
        self.dates = []
        
        for coin in coins:
            self.available[coin] = 0.0
            first = True
            prices = []
            for l in open('data/5min_%s.csv'%self.coin2ticker[coin]):
                if first:
                    first = False
                    continue
                
                newPrice = float(l.split(',')[3])
                prices.append( newPrice )
                
                if len(self.dates) < size:
                    self.dates.append( l.split(',')[0] )
                
                if len(prices) >= size:
                    break
                
            prices.reverse()
            self.dates.reverse()
            self.prices[coin] = prices
            
        self.prices['USD'] = [1.0]*self.size

    def updateAvailable(self,coin,val):
        self.available[coin] = val
        
    def getAvailable(self,coin):
        return self.available[coin]
    
    def balanceBase(self):
        return self.available['USD']
    
    def currentDate(self):
        if self.index < len(self.dates):
            return self.dates[self.index]
        else:
            return ''
    
    def ticker(self,coin=None, baseCoin=None):
        if baseCoin != 'USD':
            raise Exception('Base coin %s not supported yet!' % coin)
        return {'bid': self.prices[coin][self.index], 'ask': self.prices[coin][self.index]}
        
    def placeOrder(self, coin, amount=None, type=None, orderType=None):
        if orderType != 'market':
            raise Exception('VirtualBot only supports market orders!')
        
        if type == 'buy':
            self.available[coin] += amount * (100.0-self.TAKER_FEE)/100.0
            self.available['USD'] -= amount * self.prices[coin][self.index]
            if self.available['USD'] < 0.0:
                #print self.available['USD']
                raise Exception('Error on VirtualBot available USD negative, bought to much coin! %s' % coin)
        else:
            self.available[coin] -= amount
            self.available['USD'] += amount * self.prices[coin][self.index] * (100.0-self.TAKER_FEE)/100.0
            if self.available[coin] < 0.0:
                raise Exception('Error on VirtualBot available %s negative, sold to much coin!' % (coin))
        
        
    def sleep(self, seconds):
        self.index += 1
    
    def stop(self):
        return self.index >= self.size



class StampedeStrategy(object):
    
    fname = 'data/stampede.json'
    obj = {'USD' : {'available':0.0,'bid':1.0,'ask':1.0}}

    BASE_COIN = 'USD'
    MAX_EXPOSURE = 0.98
    TAKER_FEE_PERCENT = 0.1
    WINDOWS_SECONDS = 60*5
    
    # STRATEGY PARAMETERS
    MOVING_WINDOWS_SIZE = 8 # 12*4
    SELL_LOSS_BELOW_MAX_PERCENT = 1.28 #4.0
    BUY_PROFIT_BELOW_MAX_PERCENT = 0.08 #4.0 + TAKER_FEE_PERCENT*2
    BUY_PROFIT_ABOVE_MIN_PERCENT = 100.0
    
    def __init__(self, bot,debug=False):
        self.debug = debug
        try:
            self.obj = json.load(open(self.fname))
        except:
            self.obj = {}
        self.bot = bot
    
    def __del__(self):
        #json.dump(open(self.fname,'w'), self.obj)
        pass
    
    def coins(self):
        ret = list(self.obj.keys())
        ret.remove(self.BASE_COIN)
        return ret
    
    def addCoin(self, coin, available):
        if not coin in self.obj:
            self.obj[coin] = {}
        self.obj[coin]['available'] = available

    def isBought(self,coin):
        return self.obj[coin]['available']*self.obj[coin]['ask'] > 10.0
    
    def boughtCoins(self):
        return [ coin for coin in self.coins() if self.isBought(coin)]
    
    def boughtCount(self):
        return len(self.boughtCoins())
    
    def soldCoins(self):
        return [ coin for coin in self.coins() if not self.isBought(coin)]

    def soldCount(self):
        return len(self.soldCoins())
    
    def updateAvailable(self, coin, available):
        if not coin in self.obj:
            self.obj[coin] = {}
        self.obj[coin]['available'] = available

    def coinWeight(self,coin):
        return self.obj[coin]['weight']
    
    def setEqualWeights(self):
        numcoins = len(self.coins())
        for coin in self.coins():
            self.obj[coin]['weight'] = 1./numcoins

    def setWeights(self, weights):
        for coin in self.coins():
            self.obj[coin]['weight'] = weights[coin]

    def soldWeight(self):
        ret = 0.0
        for coin in self.soldCoins():
            ret += self.obj[coin]['weight']
        return ret

    def updateTicker(self, coin, ticker):
        self.obj[coin]['bid'] = ticker['bid']
        self.obj[coin]['ask'] = ticker['ask']
        
    def balanceBase(self):
        sumUSD = 0.0
        for coin in self.coins():
            sumUSD += self.obj[coin]['bid'] * self.obj[coin]['available']
        return sumUSD + self.obj[self.BASE_COIN]['available']
    
    def availableBase(self):
        return self.obj[self.BASE_COIN]['available']
    
    def updateMovingAverage(self,coin,ticker):

        self.movingAverageTickers[coin]['ask'] *= float(self.MOVING_WINDOWS_SIZE-1) / self.MOVING_WINDOWS_SIZE
        self.movingAverageTickers[coin]['ask'] += ticker['ask'] * 1.0/self.MOVING_WINDOWS_SIZE

        self.movingAverageTickers[coin]['bid'] *= float(self.MOVING_WINDOWS_SIZE-1) / self.MOVING_WINDOWS_SIZE
        self.movingAverageTickers[coin]['bid'] += ticker['bid'] * 1.0/self.MOVING_WINDOWS_SIZE
    
    
    def checkTriggers(self,coin):
        if not 'maxPrice' in self.obj[coin]:
            self.obj[coin]['maxPrice'] = self.movingAverageTickers[coin]['ask']
        if not 'minPrice' in self.obj[coin]:
            self.obj[coin]['minPrice'] = self.movingAverageTickers[coin]['bid']
        
        #print 'MA price %s = %f  STOP = %f' % (coin,self.movingAverageTickers[coin]['bid'],self.obj[coin]['maxPrice'] * (100.0-self.SELL_LOSS_BELOW_MAX_PERCENT)/100) 
        # Check sell trigger
        if self.isBought(coin) and self.movingAverageTickers[coin]['bid'] < self.obj[coin]['maxPrice'] * (100.0-self.SELL_LOSS_BELOW_MAX_PERCENT)/100 :
            avail = self.obj[coin]['available']
            self.bot.placeOrder(coin=coin, amount=avail, type='sell', orderType='market')
            self.obj[coin]['maxPrice'] = self.movingAverageTickers[coin]['bid']
            self.obj[coin]['minPrice'] = self.movingAverageTickers[coin]['ask']
            
            if self.debug:
                print 'STOP LOSS!! %s  Price = %f'%(coin,self.movingAverageTickers[coin]['bid'])
            self.recordReturns(updateSharpe=False)

            
        # check update max
        elif self.isBought(coin) and self.movingAverageTickers[coin]['bid'] > self.obj[coin]['maxPrice']:
            self.obj[coin]['maxPrice'] = self.movingAverageTickers[coin]['bid']
            
        # check update min
        elif not self.isBought(coin) and self.movingAverageTickers[coin]['ask'] < self.obj[coin]['minPrice']:
            self.obj[coin]['minPrice'] = self.movingAverageTickers[coin]['ask']
            
        # Check buy trigger from Rebound after Local Min
        elif not self.isBought(coin) and self.movingAverageTickers[coin]['ask'] > self.obj[coin]['minPrice'] * (100.0+self.BUY_PROFIT_ABOVE_MIN_PERCENT)/100 :
            avail = self.obj[coin]['available']
            availableUSD = self.availableBase()
            soldW = self.soldWeight()
            desired = (self.obj[coin]['weight']/soldW) * (availableUSD / self.obj[coin]['ask'])
            # cap with exposure
            desired *= self.MAX_EXPOSURE
            avail = self.obj[coin]['available']
            toBuy = desired - avail
            self.bot.placeOrder(coin,amount=toBuy, type='buy', orderType='market') 
            
            self.obj[coin]['maxPrice'] = self.movingAverageTickers[coin]['ask']
            self.obj[coin]['minPrice'] = self.movingAverageTickers[coin]['ask']

            if self.debug:
                print 'BUY AGAIN AFTER REBOUND ON MINIMUM!! %s  Price = %f'%(coin,self.movingAverageTickers[coin]['ask'])
            self.recordReturns(updateSharpe=False)
            
            
        # Check buy trigger from Rebound to near previous Bought Price
        elif not self.isBought(coin) and self.movingAverageTickers[coin]['ask'] > self.obj[coin]['maxPrice'] * (100.0-self.BUY_PROFIT_BELOW_MAX_PERCENT)/100 :
            avail = self.obj[coin]['available']
            availableUSD = self.availableBase()
            desired = self.obj[coin]['weight']/self.soldWeight() * (availableUSD / self.obj[coin]['bid'])
            # cap with exposure
            desired *= self.MAX_EXPOSURE
            avail = self.obj[coin]['available']
            toBuy = desired - avail
            self.bot.placeOrder(coin,amount=toBuy, type='buy', orderType='market') 
            
            self.obj[coin]['maxPrice'] = self.movingAverageTickers[coin]['ask']
            self.obj[coin]['minPrice'] = self.movingAverageTickers[coin]['ask']

            if self.debug:
                print 'BUY AGAIN NEAR PREVIOUS SELL!! %s  Price = %f'%(coin,self.movingAverageTickers[coin]['ask'])
            self.recordReturns(updateSharpe=False)
    
    
    def runStrategy(self, coins, availables, weights=None):
        # init
        for coin,avail in availables.iteritems():
            self.addCoin(coin, avail)
        if not weights:
            self.setEqualWeights()
        else:
            self.setWeights(weights)
        
        # bought to desired weights
        for coin in self.coins():
            ticker = self.bot.ticker(coin=coin, baseCoin=self.BASE_COIN)
            self.updateTicker(coin, ticker)
        self.buyWeights()
        
        if self.debug:
            print 'BALANCE USD =',self.balanceBase()
        self.prevBal = self.balanceBase()
        self.initBal = self.prevBal
        
        self.rets = []
        
        # loop
        while not self.bot.stop():
            
            initTime = time.time()
            
            for coin in self.coins():
                # update prices
                if coin != self.BASE_COIN:
                    # update ticker
                    ticker = self.bot.ticker(coin=coin, baseCoin=self.BASE_COIN)
                    self.updateMovingAverage(coin,ticker)
                    self.updateTicker(coin, ticker)
                    self.checkTriggers(coin)
                    # update available
                    balance = self.bot.getAvailable(coin)
                    self.obj[coin]['available'] = balance
                    self.obj[self.BASE_COIN]['available'] = self.bot.balanceBase()
                    
            self.recordReturns(printMsg=False)
            self.prevBal = self.balanceBase()
            
            endTime = time.time()
            diffTime = endTime - initTime
            self.bot.sleep(self.WINDOWS_SECONDS - diffTime)
            
        retTot = self.recordReturns(printMsg=True, updateSharpe=False)
        print 'Return Total = ',retTot
        
        return self.sharpeRatio(),retTot
    
        
    def sharpeRatio(self):
        aveRet = sum(self.rets) / len(self.rets)
        if self.debug:
            print '-'*80
            print 'Average Return Percent = ',aveRet
        stdDev = sqrt( 1./len(self.rets) * sum([ (r-aveRet)**2 for r in self.rets]) )
        if self.debug:
            print 'Std Dev Returns Percent = ',stdDev
        sharpe = aveRet / stdDev
        if self.debug:
            print 'Sharpe Ratio = ',sharpe
        return sharpe
        

    def recordReturns(self,printMsg=True, updateSharpe=True):
        returnStep = (self.balanceBase() / self.prevBal - 1.0) * 100.0
        returnTotal = (self.balanceBase() / self.initBal - 1.0) * 100.0
        if printMsg:
            if self.debug:
                print '%s BALANCE USD = %.4f   RETURN PERCENT STEP = %.4f  ACCUMULATED RETURN = %.4f' % (self.bot.currentDate(),self.balanceBase(),returnStep,returnTotal)
            #print self.obj       
        if updateSharpe:
            self.rets.append( returnStep ) 
        return returnTotal    
        

            
    def buyWeights(self):
        self.movingAverageTickers = {}
        totalUSD = self.balanceBase()
        for coin in self.coins():
            d = self.obj[coin]
            desired = d['weight'] * totalUSD / d['ask']
            self.movingAverageTickers[coin] = {}
            self.movingAverageTickers[coin]['ask'] = d['ask'] 
            self.movingAverageTickers[coin]['bid'] = d['bid'] 
            # cap with exposure
            desired *= self.MAX_EXPOSURE
            avail = d['available']
            toBuy = desired - avail
            self.bot.placeOrder(coin, amount=toBuy, type='buy', orderType='market') 
            self.obj[coin]['available'] = self.bot.getAvailable(coin) 
            self.obj[self.BASE_COIN]['available'] = self.bot.getAvailable(self.BASE_COIN) 
                       

if __name__ == '__main__':

    initUSD = 100.0
    coins = [
                'ETH',
                'XMR',
                'LTC',
                'DASH',
                'ZEC',
            ]
    availables = {
                'ETH' : 0.0,
                'XMR' : 0.0,
                'LTC' : 0.0, 
                'DASH' : 0.0, 
                'ZEC' : 0.0, 
                'USD' : initUSD,
            }
    
    windows = 12 * 24 * 360 # 30 days, 5 minutes windows
    
    bot = VirtualBot(coins, size=windows) 
    bot.updateAvailable('USD', initUSD)

     # New Max Sharpe! sharpe = 0.020800  Params = 16.000000, 20.480000, 0.640000  Total Return Percent = 105.3059
    # New Max Sharpe! sharpe = 0.019561  Params = 32.000000, 5.120000, -163.840000, 2.560000  Total Return Percent = 3117.5240
          
    strat = StampedeStrategy(bot,debug=True)
    strat.MOVING_WINDOWS_SIZE = 32.0
    strat.SELL_LOSS_BELOW_MAX_PERCENT = 5.12
    strat.BUY_PROFIT_BELOW_MAX_PERCENT = -100.0
    strat.BUY_PROFIT_ABOVE_MIN_PERCENT = 2.56
    print strat.runStrategy(coins, availables)
    
#     params = []
#     for i in [5]:#range(0,10,2):
#         p1 = 2**i
#         for j in range(8,12): # [7]:
#             p2 = 2**j / 100.0
#             for k in [14]:#range(5,14,2):
#                 p3 = -(2**k) / 100.0
#                 #params.append((p1,p2,p3,100.0))
#                 for l in range(8,12):#range(0,14):
#                     p4 = 2**l / 100.0
#                     params.append((p1,p2,p3,p4))
#                              
#     maxSharpe = 0.0
#     for p1,p2,p3,p4 in params:
#         bot = VirtualBot(coins, size=windows) 
#         bot.updateAvailable('USD', initUSD)
#         strat = StampedeStrategy(bot)
#         strat.MOVING_WINDOWS_SIZE = p1
#         strat.SELL_LOSS_BELOW_MAX_PERCENT = p2
#         strat.BUY_PROFIT_BELOW_MAX_PERCENT = p3
#         strat.BUY_PROFIT_ABOVE_MIN_PERCENT = p4
#         try:
#             sharpe,retTot = strat.runStrategy(coins, availables)
#         except:
#             sharpe,reTot = 0.0, 0.0
#         if sharpe > 0:
#             print p1,p2,p3,p4
#         if sharpe > maxSharpe:
#             #print p1,p2,p3,p4
#             maxSharpe = sharpe
#             print 'New Max Sharpe! sharpe = %f  Params = %f, %f, %f, %f  Total Return Percent = %.4f' % (maxSharpe,p1,p2,p3,p4,retTot)