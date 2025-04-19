'''
Created on Feb 27, 2017
Updated for Python 3 compatibility and integration with scraper2024.py

@author: joigno
'''

import csv
import os
import pandas as pd
from scraper2024 import get_coins

class CoinDB(object):
    """
    CoinDB class for accessing cryptocurrency data
    Updated to use scraper2024.py for coin data
    """
    
    def __init__(self):
        """Initialize the CoinDB"""
        # Get coins from scraper2024
        self.coins = get_coins()
        
        # Create data directory if it doesn't exist
        if not os.path.exists('data'):
            os.makedirs('data')
    
    def prices(self, coin, interval='1D'):
        """
        Get price data for a coin and interval
        
        Args:
            coin (str): Coin symbol
            interval (str): Time interval ('15m', '1H', '4H', '1D', '1W')
            
        Returns:
            pandas.Series: Price data or None if not available
        """
        try:
            file_path = f'data/{interval}_price_{coin}.csv'
            if not os.path.exists(file_path):
                return None
                
            df = pd.read_csv(file_path)
            return df['prices']
        except Exception as e:
            print(f"Error loading prices for {coin} ({interval}): {str(e)}")
            return None
    
    def returns(self, coin, interval='1D'):
        """
        Calculate returns for a coin and interval
        
        Args:
            coin (str): Coin symbol
            interval (str): Time interval ('15m', '1H', '4H', '1D', '1W')
            
        Returns:
            list: Returns or empty list if not available
        """
        prices = self.prices(coin, interval)
        if prices is None or len(prices) < 2:
            return []
            
        # Calculate returns
        returns = []
        for i in range(1, len(prices)):
            if prices[i-1] > 0:  # Avoid division by zero
                ret = (prices[i] / prices[i-1]) - 1.0
                returns.append(ret)
            else:
                returns.append(0.0)
                
        return returns

if __name__ == '__main__':
    c = CoinDB()
    print(c.prices('komodo'))
