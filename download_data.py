#!/usr/bin/env python3
"""
Download cryptocurrency historical data
"""

import os
import time
import pandas as pd
import argparse
from datetime import datetime
from scraper2024 import get_coins, get_data, get_price, get_time, coin_to_coin_number

# Configure intervals - prioritize 1D data first
INTERVALS = [
    '1D',    # Daily data (most important)
    '1H',    # Hourly
    '4H',    # 4-hour
    '15m',   # 15-minute
    '1W'     # Weekly
]

def get_date(time): 
    """Convert timestamp to datetime"""
    date = datetime.fromtimestamp(time)
    return date

def download_all_data(intervals=None):
    """Download data for all coins and intervals"""
    if intervals is None:
        intervals = ['1D']  # Default to daily data only
    
    # Create data directory if it doesn't exist
    if not os.path.exists('data'):
        os.makedirs('data')
        print("Created data/ directory")
    
    # Get list of coins
    coins = get_coins()
    print(f"Found {len(coins)} coins")
    
    # Download data for each coin and interval
    for interval in intervals:
        print(f"\nDownloading {interval} data...")
        for coin in coins:
            try:
                print(f"  {coin}...", end='', flush=True)
                
                # Get coin number
                coin_number = coin_to_coin_number(coin)
                
                # Get data
                data = get_data(coin_number, interval)
                
                # Extract prices and times
                prices = get_price(data)
                times = get_time(data)
                
                # Save data with interval prefix
                df = pd.DataFrame({'times': times, 'prices': prices})
                df['times'] = df['times'].apply(get_date)
                df.to_csv(f'data/{interval}_price_{coin}.csv', index=False)
                
                print(" done")
                # Increased delay to avoid rate limiting
                time.sleep(1.0)  # 2 seconds between requests
            except Exception as e:
                print(f" error: {str(e)}")
                # Even longer delay after an error
                time.sleep(5.0)  # 5 seconds after an error
        
        # Add extra delay between intervals
        print(f"Completed {interval} data. Waiting 10 seconds before next interval...")
        time.sleep(10.0)  # 10 seconds between intervals
    
    print("\nData download completed!")
    print("Files saved in data/ directory with format: [interval]_price_[coin].csv")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Download cryptocurrency historical data')
    parser.add_argument('-i', '--interval', choices=INTERVALS, 
                      help='Download data for a specific interval (default: all intervals)')
    args = parser.parse_args()
    
    print("Starting data download...")
    if args.interval:
        print(f"Downloading data for interval: {args.interval}")
        download_all_data(intervals=[args.interval])
    else:
        print("Downloading data for all intervals")
        download_all_data(intervals=INTERVALS) 