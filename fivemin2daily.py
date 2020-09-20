'''
Created on Mar 9, 2017

@author: joign
'''

from coins import CoinDB

def fiveMinToDailyAll():
    coins = CoinDB()
    for coin in coins.coins:
        
        lastPriceDate = coins.lastPriceDate(coin)
        if lastPriceDate:
            print coin,lastPriceDate,' ...'
            #updateSinceLastPrice(coin)
            count = coins.fiveMinToDaily(coin)
            print 'done! %d days.' % count
            
            
if __name__ == '__main__':
    
    print 'Filtering and copying 5min ticker data to daily data ..'
    fiveMinToDailyAll()
    
