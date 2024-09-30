
'''
{
    "data": {
        "points": {
            "1727302500": {
                "v": [
                    26.804457831247564,
                    455485.93,
                    0E-15,
                    0.00042311470742515495,
                    0
                ],
                "c": [
                    26.804457831247564,
                    455485.93,
                    0E-15
                ]
            },
'''

# https://api.coinmarketcap.com/data-api/v3/cryptocurrency/detail/chart?id=31656&range=1D

import requests 
import json 
import pandas as pd
from datetime import datetime
import time
import os

def get_data(coin_number=31656, range='1D'):
    url = "https://api.coinmarketcap.com/data-api/v3/cryptocurrency/detail/chart?id=%d&range=%s" % (coin_number,range)
    response = requests.get(url)
    data = json.loads(response.text)
    return data

def get_price(data):
    points = data['data']['points']
    prices = []
    for point in points:
        price = points[point]['v'][0]
        prices.append(price)
    return prices

def get_time(data):
    points = data['data']['points']
    times = []
    for point in points:
        #time = points[point]['v'][0]
        times.append(int(point))
    return times    

def get_date(time): 
    date = datetime.fromtimestamp(time)
    return date

def save_data(prices, times, name):  
    df = pd.DataFrame({'times': times, 'prices': prices})
    df['times'] = df['times'].apply(get_date)
    df.to_csv('data/price_%s.csv' % name, index=False)

def main():
    coin = 'ethereum'
    coinnumber = coin_to_coin_number(coin)
    data = get_data(coinnumber, '1M')
    prices = get_price(data)
    times = get_time(data)
    save_data(prices, times, coin)

# coins/200x200/31656.png
# view-source:https://coinmarketcap.com/es/currencies/morpheus/
def coin_to_coin_number(coinname='morpheus'):
    url = "https://coinmarketcap.com/es/currencies/%s/" % coinname
    response = requests.get(url)
    data = response.text
    coin_number = data.split('coins/200x200/')[1].split('.png')[0]
    return int(coin_number)

def get_coins():
    coins = [
        'bitcoin',
        'ethereum',
        'solana',
        'dogecoin',
        'ripple',
        'sui',
        'celestia',
        'chainlink',
        'dogwifhat',
        'aave',
        'avalanche',
        'arbitrum',
        'uniswap',
        'near-protocol',
        'dydx',
        'sei',
        'aptos',
        'toncoin',
        'bnb',
        'cardano',
        'filecoin',
        'cosmos',
        'injective',
        'bitcoin-cash',
        'polkadot-new',
        'litecoin',
        'stellar',
        'ethereum-classic',
        'thorchain',
        'internet-computer',
        'algorand',
        'eos',
        'chiliz',
        'gala',
        'helium',
        'kaspa',
        'monero',
        'multiversx-egld',
        'theta-network',
        'tezos',
        ]
    return coins

def get_all_data():
    coins = get_coins()
    for coin in coins:
        coinnumber = coin_to_coin_number(coin)
        data = get_data(coinnumber, '7D')
        prices = get_price(data)
        times = get_time(data)
        save_data(prices, times, coin)
        time.sleep(0.25)


if __name__ == '__main__':
    get_all_data()