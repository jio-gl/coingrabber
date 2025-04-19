'''
Created on Feb 8, 2017
Updated for Python 3 compatibility and integration with scraper2024.py

@author: joign
'''

import datetime
import csv
import json
import time
import re
import os
import random
import sys
import requests
from urllib.error import HTTPError
import pandas as pd

from coins import CoinDB
from scraper2024 import get_data, get_price, get_time, coin_to_coin_number, get_coins


def timestamp2datestr(t):
    t = t / 1000
    return datetime.datetime.fromtimestamp(
        int(t)
    ).strftime('%Y-%m-%d %H:%M:%S')


def mergeLists(listOfLists):
    ret = []
    for i in range(len(listOfLists[0])):
        t = []
        for l in range(len(listOfLists)):
            t.append(listOfLists[l][i])
        ret.append(t)
    return ret


def json2csv(obj, ofname, daysBack, lastPriceDate=None, reverse=True):
    
    # ALL BTC https://api.coinmarketcap.com/v1/datapoints/bitcoin/1367174841000/1486583341000/
    
    cap = obj['market_cap_by_available_supply']
    ts = [e[0] for e in cap]
    dates = [timestamp2datestr(t) for t in ts]
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
        dates = [d for d in dates if d > lastPriceDate]
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
                            quotechar='"', quoting=csv.QUOTE_MINIMAL, lineterminator='\n')
    
    if daysBack == 0:
        spamwriter.writerow(['Date','Timestamp','PriceBTC','PriceUSD','MarketCap','Volume'])
    else:
        pass
    for t in mergeLists([dates,ts,price_btc,price_usd,cap,volume_usd]):
        spamwriter.writerow(t)
    
    return len(price_usd), foundLastPrice


def topCurrencies(n=100):
    txt = open('top.html').read()
    c = 0
    ret = []
    for f in re.findall('/assets/[a-z-]+/',txt):
        if 'assets/volume' in f:
            continue
        if 'assets/search' in f:
            continue
        if 'assets/views' in f:
            continue
        ccy = f.split('/')[-2]
        if ccy in set(ret):
            continue
        ret.append(f.split('/')[-2])
        c += 1
        if c >= n:
            break
    for f in re.findall('/currencies/[a-z-]+/',txt):
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
        ret.append(f.split('/')[-2])
        c += 1
        if c >= n:
            break
    return ret


def json2prices(obj):
    price_usd = obj['price_usd']
    price_usd = [e[1] for e in price_usd]
    return price_usd


def pricesAll(coin, interval='1D'):
    """Get prices for a coin with specified interval"""
    coin_number = coin_to_coin_number(coin)
    data = get_data(coin_number, interval)
    
    # Save data with interval prefix
    filename = f"data/{interval}_price_{coin}.csv"
    df = pd.DataFrame({
        'times': get_time(data),
        'prices': get_price(data)
    })
    df.to_csv(filename, index=False)
    return len(df), df['prices'].iloc[-1] if len(df) > 0 else None


def get_all_data(intervals=['1D', '1H', '4H', '1W']):
    """Get data for all coins at specified intervals"""
    coins = get_coins()
    for coin in coins:
        for interval in intervals:
            try:
                pricesAll(coin, interval)
                print(".", end="", flush=True)  # Simple progress indicator
            except Exception as e:
                print(f"\nError fetching {coin}: {str(e)}")
    print("\nData collection complete")


def combineLastPrices(coin):
    tfname = 'data/temp_5min_%s.csv' % coin
    fname = 'data/5min_%s.csv' % coin
    prev = open(fname).read()
    prev = prev.split('\n')
    prev = prev[1:]
    prev = '\n'.join(prev)
    new = open(tfname).read()
    os.remove(tfname)
    combined = open(fname,'w')
    combined.write(new + prev)


def updateSinceLastPrice(coin, browser):
    coins = CoinDB()
    # get last price date
    lastPriceDate = coins.lastPriceDate(coin)
    # get last new prices until we found the last price already stored
    pricesAll(coin)
    combineLastPrices(coin)


def updateLastTickers(updateLastDays=True, downloadMissing=True):
    coins = CoinDB()
    
    missingCoins = []
    for coin in coins.coins:
        print(coin)
        lastPriceDate = coins.lastPriceDate(coin)
        if lastPriceDate:
            if updateLastDays:
                print(coin, lastPriceDate)
                updateSinceLastPrice(coin, None)
        else:
            missingCoins.append(coin)
            
    # Download missing coins completely.
    if downloadMissing:
        print('Download missing coins completely.')
        for coin in missingCoins:
            pricesAll(coin)


class CoinGrabber:
    def __init__(self):
        self.coin_list = get_coins()  # Use dynamic list from scraper
        self.data_dir = "data"
        os.makedirs(self.data_dir, exist_ok=True)

    def get_all_prices(self, interval='1D'):
        """Download prices for all coins in the scraper list"""
        for coin in self.coin_list:
            self.get_coin_prices(coin, interval)


if __name__ == '__main__':
    get_all_data()
