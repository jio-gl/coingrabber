'''
Created on Feb 8, 2017

@author: joign
'''

import datetime
import csv
import json
import urllib2
import time
import re
import os
import random

# mecha
import sys
import os
import re
from urllib2 import HTTPError
#import mechanize
#assert mechanize.__version__ >= (0, 0, 6, "a")
# end mecha

from coins import CoinDB


def timestamp2datestr(t):
    t = t / 1000
    #print t
    return datetime.datetime.fromtimestamp(
        int(t)
    ).strftime('%Y-%m-%d %H:%M:%S')


def mergeLists( listOfLists):
    ret = []
    for i in range(len(listOfLists[0])):
        t = []
        for l in range(len(listOfLists)):
            t.append( listOfLists[l][i] )
        ret.append( t )
    return ret

def json2csv(obj, ofname, daysBack, lastPriceDate=None, reverse=True):
    
    # ALL BTC https://api.coinmarketcap.com/v1/datapoints/bitcoin/1367174841000/1486583341000/
    
    cap = obj['market_cap_by_available_supply']
    ts = [e[0] for e in cap]
    dates = [ timestamp2datestr(t) for t in ts]
    if reverse:
        dates.reverse()
    
    cap = [e[1] for e in cap]
    cap.reverse()
    
    price_btc = obj['price_btc']
    price_btc = [e[1] for e in price_btc]
    price_btc.reverse()
    
    volume_usd = obj['volume_usd']
    volume_usd = [e[1] for e in volume_usd]
    volume_usd.reverse()
    
    price_usd = obj['price_usd']
    price_usd = [e[1] for e in price_usd]
    price_usd.reverse()
    
    # Filter by last date
    if lastPriceDate:
        #print '-'*80
        #print dates
        dates = [ d for d in dates if d > lastPriceDate]
        #print '-'*80
        #print dates
        foundLastPrice = len(dates) < len(ts)
        ts = ts[:len(dates)]
        price_btc = price_btc[:len(dates)]
        price_usd = price_usd[:len(dates)]
        cap = cap[:len(cap)]
        volume_usd = volume_usd[:len(dates)]
    else:
        foundLastPrice = False
    
    try:
        csvfile = open(ofname, 'a')
    except:
        csvfile = open(ofname, 'w')
    spamwriter = csv.writer(csvfile, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_MINIMAL,lineterminator='\n')
    
    if daysBack == 0:
        spamwriter.writerow(['Date','Timestamp','PriceBTC','PriceUSD','MarketCap','Volume'])
    else:
        #spamwriter.writerow(['-----------------------------------------------------------------------------Date','Timestamp','PriceBTC','PriceUSD','MarketCap','Volume'])
        pass
    for t in mergeLists([dates,ts,price_btc,price_usd,cap,volume_usd]):
        #print t
        spamwriter.writerow( t )
    
    return len(price_usd), foundLastPrice

    
def topCurrencies(n=100):
    txt = open('top.html').read()
    c = 0
    ret = []
    for f in re.findall('/assets/[a-z-]+/',txt):
        #print f
        if 'assets/volume' in f:
            continue
        if 'assets/search' in f:
            continue
        if 'assets/views' in f:
            continue
        ccy = f.split('/')[-2]
        if ccy in set(ret):
            continue
        #print ccy
        ret.append( f.split('/')[-2] )
        #print f
        c += 1
        if c >= n:
            break
    for f in re.findall('/currencies/[a-z-]+/',txt):
        #print f
        if 'currencies/volume' in f:
            continue
        if 'currencies/search' in f:
            continue
        if 'currencies/views' in f:
            continue
        if 'bitcoin' in f:
            continue
        ccy = f.split('/')[-2]
        if ccy in set(ret):
            continue
        #print ccy
        ret.append( f.split('/')[-2] )
        #print f
        c += 1
        if c >= n:
            break
    return ret


def json2prices(obj):
    price_usd = obj['price_usd']
    for e in price_usd:
        print e
    price_usd = [e[1] for e in price_usd]
    print len(price_usd)
    return price_usd



def pricesAll5minutes(coin, browser=None, lastPriceDate=None, isTemp=False):  
    coins = [coin]#,'ripple','monero','dash']
    ranges_name = ['5min']#,'7d','1m','3m','1y','YTD','ALL']
    
    count = 1
    daysBack = 0
    foundLastPrice = False
    while count > 0 and not foundLastPrice:
        print 'daysBack',coins[0],daysBack
        r = (int(time.time()) + 60*60*24*(daysBack-1) + 60)*1000, (int(time.time()) + 60*60*24*daysBack + 60)*1000 
        #url = 'https://graphs.coinmarketcap.com/v1/datapoints/%s/%d/%d/' % (coins[0],r[0],r[1])
        url = 'https://graphs.coinmarketcap.com/currencies/%s/%d/%d/' % (coins[0],r[0],r[1])
        print 'INFO: grabbing all prices (5 min periods) for %s ...' % coins[0]
        print url
        #respStr = browser.open(url).read()
        #print respStr
        
        try:
            opener = urllib2.build_opener()
            opener.addheaders = [
                    ('user-agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36'),
                    ('accept', 'application/json, text/javascript, */*; q=0.01'),
                    ('origin','https://coinmarketcap.com'),
                    ('referer','https://coinmarketcap.com/currencies/%s/'%coin),
                    #(':authority','graphs.coinmarketcap.com'),
                    #(':method','GET'),
                    #(':path','/currencies/litecoin/1486650841000/1494336841000/'),
                    ]
               
            resp = opener.open( url )
            respStr = resp.read()
            #print respStr
            #print '-'*80
            #print url
            #print respStr
        except HTTPError, e:
            sys.exit("%d: %s" % (e.code, e.msg))
        
        #except:
        #    print 'Error while retrieving url for %s sleeping 60 seconds ..' % coins[0]
        #    time.sleep(60.0)
        #    continue
        
        fname = not isTemp and 'data/%s_%s.csv' or 'data/temp_%s_%s.csv'
        count,foundLastPrice = json2csv( json.loads( respStr ), ofname=fname%(ranges_name[0],coins[0]), daysBack=daysBack, lastPriceDate=lastPriceDate )
        time.sleep( 1.0 + 1.0 * random.random() )
        daysBack -= 1
        
        #if daysBack == -2:
        #    break
        #return json2prices( json.load( urfllib2.urlopen(url) ) )


def combineLastPrices(coin):
    tfname = 'data/temp_5min_%s.csv' % coin
    fname = 'data/5min_%s.csv' % coin
    prev = open(fname).read()
    prev = prev.split('\n')
    prev = prev[1:]
    prev = '\n'.join( prev )
    new = open(tfname).read()
    os.remove( tfname )
    combined = open(fname,'w')
    combined.write( new + prev )
    

def updateSinceLastPrice(coin,browser):
    coins = CoinDB()
    # get last price date
    lastPriceDate = coins.lastPriceDate(coin)
    # get last new prices until we found the last price already stored
    pricesAll5minutes(coin, browser, lastPriceDate, isTemp=True)
    combineLastPrices(coin)


def updateLastTickers(updateLastDays=True,downloadMissing=True):
    coins = CoinDB()
    
    # browser
    browser = None
    #browser = mechanize.Browser()
    #browser.set_handle_robots(False)
    # mech.set_debug_http(True)

    # Get the starting page
    try:
        pass
        #browser.open("https://coinmarketcap.com/")
    except HTTPError, e:
        sys.exit("%d: %s" % (e.code, e.msg))
    
    missingCoins = []
    for coin in coins.coins:
        print coin
        lastPriceDate = coins.lastPriceDate(coin)
        if lastPriceDate:
            if updateLastDays:
                print coin,lastPriceDate
                updateSinceLastPrice(coin,browser)
        else:
            missingCoins.append( coin )
            
    # Download missing coins completely.
    if downloadMissing:
        print 'Download missing coins completely.'
        for coin in missingCoins:
            pricesAll5minutes(coin)
            


if __name__ == '__main__':

    print '    updateLastTickers(updateLastDays=True,downloadMissing=True)'
    updateLastTickers(updateLastDays=True,downloadMissing=True)

    #pricesAll5minutes('bitcoin')
            
    #for c in topCurrencies(n)[:5]:#['maidsafecoin','augur','iconomi']:#topCurrencies():
        
        #print c, coins.lastPriceDate(c)
        
        #pricesAll5minutes(c)
        #updateSinceLastPrice(c)
        
#         coins = [c]
#         r = (1067174841000,1486583341000)
#         url = 'https://api.coinmarketcap.com/v1/datapoints/%s/%d/%d/' % (coins[0],r[0],r[1])
#         print 'INFO: grabbing all prices (5 min periods) for %s ...' % coins[0]
#         print url
#         try:
#             resp = urllib2.urlopen(url)
#         except:
#             print 'Error while retrieving url for %s sleeping 60 seconds ..' % coins[0]
#             time.sleep(60.0)
#             continue
#         count = json2csv( json.load( resp ), ofname='data/%s_%s.csv'%('ALL',coins[0]), daysBack=0 )
#         time.sleep(7.0)
