'''
Created on Feb 27, 2017

@author: joigno
'''

import csv,pickle
from collections import OrderedDict

from dateconfig import DateRange

DAILY = '1d'

class CoinDB(object):
    
    debug = False
    
    assets = {
        'golem-network-tokens',
        'augur',
        'maidsafecoin',
        'gnosis-gno',
        'digixdao',
        'singulardtv',
        'ardor',
        'tether',
        'iconomi',
    }

    coinSets = {

        'test' : ['clams'],

        'cap' : [
            'bitcoin',
            'ethereum',
            'ripple',
            'nem',
            'ethereum-classic',
            'litecoin',
            'dash',
            'monero',
            'stratis',
            #'bytecoin-bcn',
            # 10
            'golem-network-tokens',
            'stellar',
            'zcash',
            #'waves',
            'dogecoin',
            # on poloniex
            #'gnosis-gno',
            'augur',
            'steem',
            'siacoin',
            'maidsafecoin',
            # 20
            'bitshares',
            'gamecredits',
            #'digixdao',
            'digibyte',
            #'bitconnect',
            'lisk',
            'decred',
            'factom',
            #'tether',
            'singulardtv',
            # 30
            # on polonix
            'ardor',
            
            #'iconomi',
            #'byteball',
            #'round',
            #'pivx',
            #'aragon',
            #'firstblood',
            'syscoin',
            'nxt',
            #'antshares',
            # 40
            #'komodo',
            #'rlc',
            'peercoin',
            #'emercoin',
            #'ubiq',
            'omni',
            #'melon',
            #'lykke',
            'storjcoin-x',
            'counterparty',
        ],
        
        'margin' : [
            'ripple',
            'dash',
            'ethereum',
            'litecoin',
            'monero',
            'maidsafecoin',
            'dogecoin',
            'stellar',
            'factom',
            'bitshares',
            'clams',
            #'-ripple',
            #'-dash',
            #'-ethereum',
            #'-litecoin',
            #'-monero',
            #'-maidsafecoin',
            #'-dogecoin',
            #'-stellar',
            #'-factom',
            #'-bitshares',
            #'-clams',
            ],
        
        'vip' : [
            'steem',
            'bitcoin',
            'monero',
            'gamecredits',
            'decred',
            'augur',
            'dogecoin',
            'factom',
            'maidsafecoin',
            'litecoin',
            'dash',
            'iocoin',
            'bitcrystals',
            ],


        'allUSD' : [
            'bitcoin',
            'ethereum',
            'dash',
            'ripple',
            'litecoin',
            'monero',
            'ethereum-classic',
            'nem',
            'maidsafecoin',
            'augur',
            'tether',            
            'zcash',
            'iconomi',
            'factom',
            'dogecoin', 
            'waves',
            'steem',
            'digixdao',
            'golem-network-tokens',
            'ardor',
            'gamecredits',
            'lisk',
            'stellar',
            'decred',
            'shadowcoin',
            'peercoin',
            'bitcrystals',
            'bitshares',
            'bitconnect',
            'bytecoin-bcn',
            'komodo',
            'emercoin',
            'siacoin',
            'singulardtv',
            'stratis',
            'nxt',      
            'counterparty',
            'storjcoin-x',
            'iocoin', 
            'rubycoin',
            'bitcoindark',
            'nexus',
            'belacoin',
            'clams',
            
            
            'potcoin',
            'rubycoin/bitcoin',
            'shadowcoin',
            'syscoin',
             #'SPY', ccy2ticker('EUR'), ccy2ticker('JPY')
            ],
        'all' : [
            'bitcoin',
            'dash',
            #'factom',
            'litecoin',
            'nem/bitcoin', 
            'stellar',
            'bitshares',
            'dogecoin/bitcoin',
            'gamecredits/bitcoin',
            'monero',
            'ripple',     
            'dash/monero',       
            #'bytecoin-bcn',          
            'counterparty', 
            'ethereum',  
            'emercoin/bitcoin',
            'iocoin/bitcoin',
            'potcoin',
            'rubycoin/bitcoin',
            #'shadowcoin/bitcoin',
            #'solarcoin',
            #'syscoin',
            #'ybcoin',
             #'SPY', ccy2ticker('EUR'), ccy2ticker('JPY')
            ],
        'poloniex' : [
            'dash/bitcoin',
            'ethereum/bitcoin',
            'bitcoin',
            'monero/bitcoin',
            'ethereum',
            'litecoin/bitcoin',
            'dash',
            'ripple/bitcoin',
            #'ethereum-classic/bitcoin',
            #'zcash/bitcoin',
            #'factom/bitcoin',
            'monero',
            'nem/bitcoin',
            #'stratis/bitcoin',
            'stellar/bitcoin',
            'litecoin',
            #'ethereum-classic',
            #'ethereum-classic/ethereum',
            #'lisk/bitcoin',
            'shadowcoin/bitcoin',
            'gamecredits/bitcoin',
            'nxt/bitcoin',
            #'steem/bitcoin',
            'dash/monero',
            'ripple',
            'counterparty/bitcoin',
            'dogecoin/bitcoin',
            #'decred/bitcoin',
            'potcoin/bitcoin',
            'iocoin/bitcoin',
            'bitshares/bitcoin',
            'syscoin/bitcoin',
            'peercoin/bitcoin',
            'namecoin/bitcoin',
            ]  ,
        'kraken' : [
            'bitcoin',
            'ethereum',
            'ethereum/bitcoin',
            'monero',
            'monero/bitcoin',
            'ripple/bitcoin',
            'litecoin/bitcoin',
            'stellar/bitcoin',
            'stellar',
            ]   ,
        'bittrex' : [
            'dash/bitcoin',
            #'ethereum/bitcoin',
            'monero/bitcoin',
            #'stratis/bitcoin',
            'shadowcoin/bitcoin',
            'gulden/bitcoin',
            'nem/bitcoin',
            #'komodo/bitcoin',
            #'waves/bitcoin',
            'ripple/bitcoin',
            'litecoin/bitcoin',
            'bitcoin',
            'dogecoin/bitcoin',
            
            ]
                
            }

    allCoins = list(set(coinSets['kraken'] + coinSets['poloniex'] + coinSets['bittrex']))
    coins = coinSets['cap'] # list(set( coinSets['margin'] + coinSets['vip'] ))


    stocks = [
            'SPY',
            'JPY%3DX',
            'EUR%3DX',
        ]
    
    periods = [
            DAILY,
        ]
    
    periodSearch = {
            DAILY : [' 00:00:',' 00:01:',' 00:02:',' 00:03:',' 00:04:',' 00:05:',],
        }
    
    fname = 'data/5min_%s.csv'
    fnameDaily = 'data/1d_%s.csv'
    cacheFName = "coincache.p"
    csvOrderedFieldnames = OrderedDict([('Date',None),('Timestamp',None),('PriceBTC',None),('PriceUSD',None),('MarketCap',None),('Volume',None)])
    
    def __init__(self, period=DAILY):
        assert( period in self.periods )
        self.period = period
        try:
            self.__cache = pickle.load( open( self.cacheFName, "rb" ) )
        except:
            self.__cache = {}
    
    
    def __del__(self):
        pickle.dump( self.__cache, open( self.cacheFName, "wb" ) )
    
    def formatEndDate(self):
        ret = '%d-' % ( DateRange.endYear )
        if DateRange.endMonth>=10:
            ret += '%d-' % ( DateRange.endMonth )
        else:
            ret += '0%d-' % ( DateRange.endMonth )
        if DateRange.endDay>=10:
            ret += '%d' % ( DateRange.endDay )
        else:
            ret += '0%d' % ( DateRange.endDay )
        return ret

    def lastPriceDate(self, coin):
        '''
        Assuming the first line in DB is the last price.
        '''
        fname = self.fname % coin.lower()
        lastRow = None
        try:
            with open(fname, 'rb') as csvfile:
                reader = csv.DictReader(csvfile)
                for r in reader:
                    lastRow = r
                    break  
        except:
            pass
        if not lastRow:
            return None
        return lastRow['Date']
    
    
    def fiveMinToDaily(self, coin, timeIncreasing=True):
        fname = self.fname % coin.lower()
        fnameDaily = self.fnameDaily % coin.lower()
        rows = []
        dailyCSV = open(fnameDaily, 'wb')
        writer = csv.DictWriter(dailyCSV, delimiter=',', fieldnames=self.csvOrderedFieldnames) 
        writer.writeheader()
        count = 0
        with open(fname, 'rb') as csvfile:
            reader = csv.DictReader(csvfile)
            priceFilter = lambda r : any([ (p in r['Date']) for p in self.periodSearch[self.period]])
            # Filter last point (now in reverse order) until we get to the static end of date range.
            for r in reader:
                if priceFilter(r):
                    writer.writerow( r )
                    count += 1
        return count
        
        
    def loadPriceList(self, coin, timeIncreasing=True, useFilter=False, field='PriceUSD'):
        
        endDate = self.formatEndDate()
#         if (coin,endDate,self.period) in self.__cache:
#             if self.debug:
#                 print 'hit CACHE HIT!!! %s' %(str((coin,endDate,self.period)))
#             return self.__cache[(coin,endDate,self.period)]
#         else:
#             if self.debug:
#                 print 'MISS CACHE MISS!!! %s' %(str((coin,endDate,self.period)))
            
    
        fname = self.fnameDaily % coin.lower()
        rows = []
        with open(fname, 'rb') as csvfile:
            reader = csv.DictReader(csvfile)
            priceFilter = lambda r : any([ (p in r['Date']) for p in self.periodSearch[self.period]])
            vals = []
            # Filter last point (now in reverse order) until we get to the static end of date range.
            
            filterHeadCompleted = False
            for r in reader:
                if not filterHeadCompleted:
                    if endDate in r['Date']:
                        filterHeadCompleted = True
                    continue
                if not useFilter or priceFilter(r):
                    vals.append( float(r[field]) ) 
            #vals = [ r['Date'] for r in reader ]
            if timeIncreasing:
                vals.reverse()
        #self.__cache[(coin,endDate,self.period)] = vals
        return vals
    
    def isCurrencyPair(self,coin):
        return '/' in coin
    
    def prices(self, coin):
        
        assert( coin in self.coins)

        
        if self.isCurrencyPair(coin):
            if self.debug:
                print 'isCurrencyPair ...',coin
            coin1 = coin.split('/')[0]
            vals1 = self.loadPriceList(coin1)
            coin2 = coin.split('/')[1]
            vals2 = self.loadPriceList(coin2)
            if self.debug:
                print coin1,len(vals1),coin2,len(vals2)
            minLen = min( len(vals1), len(vals2) )
            vals1 = vals1[-minLen:]
            vals2 = vals2[-minLen:]
            vals = [ p1/p2 for p1,p2 in zip(vals1,vals2) ]
        else:
            if self.debug:
                print 'Not Currency Pair ...',coin
            vals = self.loadPriceList(coin)

        return vals

    def returns(self, coin):
        prices = self.prices(coin)
        return map(lambda (x, y): (y/x)-1, zip(prices[0:-1], prices[1:]))


if __name__ == '__main__':
    c = CoinDB()
    print c.prices('komodo')
