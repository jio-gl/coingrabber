'''
Created on May 1, 2017

@author: joign
'''

import time

from poloniex import Poloniex


def sign(x):
    if x == 0.0:
        return 0.0
    return x/abs(x)

def log(line):
    line = str(line)
    line = time.ctime() + ' ' + line + '\n'
    try:
        open('poloniex.log','a').write(line)
    except:
        open('poloniex.log','w').write(line)


class PoloniexBot(object):
    '''
    classdocs
    '''

    FRACTION_ERROR_TOTAL = 0.05
    LEVERAGE = 2.5
    
    coin2ticker = {
            'bitcoin' : 'BTC',
            
        }
    

    def __init__(self):
        '''
        Constructor
        '''
        self.polo = Poloniex(Key='KEY', Secret='SECRET')
        
        
    def totalBTC(self):
        return
    
    
    def buyMargin(self, pair, rate, amount, lendingRate=0.02):
        prevBalance = self.returnMarginAccountSummary()
        resp = self.polo.marginBuy( pair=pair, rate=rate, amount=amount, lendingRate=lendingRate)
        log(resp)
        time.sleep( 2.0 )
        if prevBalance != self.returnMarginAccountSummary():
            log('Warning: Margin Buy Order not executed!! Sleeping 3 seconds and retrying...')
            time.sleep( 3.0 )
            resp = self.polo.marginBuy( pair=pair, rate=rate, amount=amount, lendingRate=lendingRate)
            time.sleep( 2.0 )
            if prevBalance != self.returnMarginAccountSummary():
                log('Warning: Margin Buy Order not executed after Retry!!')
                return False
        return True
    
    
    def sellMargin(self, pair, rate, amount, lendingRate=0.02):
        prevBalance = self.returnMarginAccountSummary()
        resp = self.polo.marginSell( pair=pair, rate=rate, amount=amount, lendingRate=lendingRate)
        log(resp)
        time.sleep( 2.0 )
        if prevBalance != self.returnMarginAccountSummary():
            log('Warning: Margin Buy Order not executed!! Sleeping 3 seconds and retrying...')
            time.sleep( 3.0 )
            resp = self.polo.marginSell( pair=pair, rate=rate, amount=amount, lendingRate=lendingRate)
            time.sleep( 2.0 )
            if prevBalance != self.returnMarginAccountSummary():
                log('Warning: Margin Buy Order not executed after Retry!!')
                return False
        return True
    
    def returnMarginAccountSummary(self):
        return self.polo.returnMarginAccountSummary()
    
    
    def totalValue(self):
        return float(self.returnMarginAccountSummary()['totalValue'])

    def totalValueLeveraged(self):
        return float(self.returnMarginAccountSummary()['totalValue'])*self.LEVERAGE
    
    def midprice(self, coin):
        return (float(self.polo.returnOrderBook( pair='BTC_%s'%coin , depth=1)['asks'][0][0]) + float(self.polo.returnOrderBook( pair='BTC_%s'%coin , depth=1)['bids'][0][0]))/2.0 
    
    def bestAsk(self, coin, amount=None):
        if not amount:
            return float(self.polo.returnOrderBook( pair='BTC_%s'%coin , depth=1)['asks'][0][0])
        else:
            asks = self.polo.returnOrderBook( pair='BTC_%s'%coin , depth=50)['asks']
            acum = 0.0
            for t in asks:
                acum += float(t[1])
                if acum >= amount:
                    return float(t[0])
            return float(asks[-1][0])


    def bestBid(self, coin, amount=None):
        if not amount:
            return float(self.polo.returnOrderBook( pair='BTC_%s'%coin , depth=1)['bids'][0][0])
        else:
            bids = self.polo.returnOrderBook( pair='BTC_%s'%coin , depth=50)['bids']
            acum = 0.0
            for t in bids:
                acum += float(t[1])
                if acum >= amount:
                    return float(t[0])
            return float(bids[-1][0])

    
    def marginBuyWeight(self, w , coin ):
        print 
        print 'marginBuyWeight'
        amountBTC = self.totalValue()*(1.0-self.FRACTION_ERROR_TOTAL) * w
        print 'amountBTC=',amountBTC
        amount = amountBTC / self.bestAsk(coin)
        print 'amount=',amount
        bestRate = self.bestAsk(coin, amount)
        print 'bestRate=',bestRate
        return self.buyMargin(pair='BTC_%s'%coin, rate=bestRate, amount=amount)
        
    def marginSellWeight(self, w , coin ):
        print
        print 'marginSellWeight'
        amountBTC = self.totalValue()*(1.0-self.FRACTION_ERROR_TOTAL) * w
        print 'amountBTC=',amountBTC
        amount = amountBTC / self.bestBid(coin)
        print 'amount=',amount
        bestRate = self.bestBid(coin, amount)
        print 'bestRate=',bestRate
        return self.sellMargin(pair='BTC_%s'%coin, rate=bestRate, amount=amount)
    
    
    def marginPositionWeight(self, w, coin):
        print
        print 'marginSellWeight'
        print 'w=',w
        amountBTC = self.totalValueLeveraged()*(1.0-self.FRACTION_ERROR_TOTAL) * w
        print 'amountBTC=',amountBTC
        midprice = self.midprice(coin)
        amount = amountBTC / midprice
        print 'amount=',amount
        currentPos = self.currentMarginPosition(coin)
        if sign(amount) != sign(currentPos):
            print 'Different sign in new position!'
            self.closeMarginPosition(coin)
            if w > 0.0:
                self.marginBuyWeight(w, coin)
            elif w < 0.0:
                self.marginSellWeight(abs(w), coin)
        else:
            print 'Same sign in new position!'
            diffPos = (amount - currentPos)
            print 'diffPos=',diffPos
            bestRate = w > 0.0 and self.bestAsk(coin, abs(diffPos)) or self.bestBid(coin, abs(diffPos))
            diffW = (amount - currentPos) * bestRate / self.totalValueLeveraged()
            print 'diffW=',diffW 
            if diffW > 0.0:
                self.marginBuyWeight(diffW, coin)
            elif diffW < 0.0:
                self.marginSellWeight(abs(diffW), coin)
            
    
    def closeMarginPosition( self, coin):
        return self.polo.closeMarginPosition('BTC_%s' % coin)
    
    
    def currentMarginPosition(self, cointicker):
        return float(self.polo.getMarginPosition('BTC_%s'%cointicker)['amount'])
    
    def updateMarginPosition(self, cointicker, w):
        pos = self.polo.getMarginPosition('BTC_%s'%cointicker)
        if sign(w) == sign( self.currentMarginPosition(cointicker) ):
            if abs(w) > abs( self.currentMarginPosition(cointicker) ):
                pass
    
    def openPortolio(self, pfolio):        
        for coin,w in pfolio.iteritems():
            if coin == 'bitcoin':
                continue 
            cointicker = self.coin2ticker[coin]
            self.closeMarginPosition(cointicker)
            if w > 0.0:
                self.marginBuyWeight(w, cointicker)
            elif w < 0.0:
                self.marginSellWeight(w, cointicker)
    
    
if __name__ == '__main__':
    
    #polobot = PoloniexBot()
    #polobot.marginBuyWeight(0.5, coin='CLAM')
    #polobot.marginSellWeight(0.5, coin='ETH')
    #polobot.marginPositionWeight(w=-0.75, coin='ETH')
 
    pass
