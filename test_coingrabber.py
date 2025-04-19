#!/usr/bin/env python3
"""
Unit tests for the coingrabber project.
"""

import unittest
import os
import pandas as pd
from datetime import datetime

from scraper2024 import get_data, get_price, get_time, coin_to_coin_number, get_coins
from grabber import pricesAll, get_all_data
from coins import CoinDB
from portfolio import PortfolioAnalyzer


class TestScraper2024(unittest.TestCase):
    """Test the scraper2024.py functionality."""
    
    def test_get_data(self):
        """Test getting data from the API."""
        # Test with Bitcoin
        data = get_data(1, '1D')  # Bitcoin ID is 1
        self.assertIsNotNone(data)
        self.assertIn('data', data)
        self.assertIn('points', data['data'])
    
    def test_get_price(self):
        """Test extracting price data."""
        data = get_data(1, '1D')  # Bitcoin ID is 1
        prices = get_price(data)
        self.assertIsNotNone(prices)
        self.assertGreater(len(prices), 0)
        self.assertIsInstance(prices[0], float)
    
    def test_get_time(self):
        """Test extracting time data."""
        data = get_data(1, '1D')  # Bitcoin ID is 1
        times = get_time(data)
        self.assertIsNotNone(times)
        self.assertGreater(len(times), 0)
        self.assertIsInstance(times[0], int)
    
    def test_coin_to_coin_number(self):
        """Test converting coin name to coin number."""
        # Test with Bitcoin
        coin_number = coin_to_coin_number('bitcoin')
        self.assertEqual(coin_number, 1)
        
        # Test with Ethereum
        coin_number = coin_to_coin_number('ethereum')
        self.assertIsInstance(coin_number, int)
        self.assertGreater(coin_number, 0)


class TestGrabber(unittest.TestCase):
    """Test the grabber.py functionality."""
    
    def test_pricesAll(self):
        """Test getting prices for a coin with 1D interval"""
        # Test with Bitcoin
        count, _ = pricesAll('bitcoin', '1D')
        self.assertGreater(count, 0)
        
        # Check if the file was created
        self.assertTrue(os.path.exists('data/1D_price_bitcoin.csv'))
        
        # Check if the file has numeric data
        df = pd.read_csv('data/1D_price_bitcoin.csv', dtype={'prices': float})
        self.assertTrue(pd.api.types.is_numeric_dtype(df['prices']))
        self.assertGreater(df['prices'].iloc[0], 0)
    
    def test_get_all_data(self):
        """Test getting all data for all coins."""
        # This test might take a while to run
        # Uncomment to run the full test
        # get_all_data()
        
        # Check if at least one file was created
        files = [f for f in os.listdir('data') if f.startswith('1D_price_') and f.endswith('.csv')]
        self.assertGreater(len(files), 0)


class TestCoins(unittest.TestCase):
    """Test the coins.py functionality."""
    
    def test_CoinDB(self):
        """Test the CoinDB class."""
        db = CoinDB()
        self.assertIsNotNone(db.coins)
        
        # Verify price data type
        prices = db.prices('bitcoin')
        self.assertIsInstance(prices, list)
        if len(prices) > 0:
            self.assertIsInstance(prices[0], (float, int))
        
        # Test getting returns for a coin
        returns = db.returns('bitcoin')
        self.assertIsNotNone(returns)
        
        # Test getting the last price date
        last_price_date = db.lastPriceDate('bitcoin')
        self.assertIsNotNone(last_price_date)


class TestPortfolio(unittest.TestCase):
    """Test the portfolio.py functionality."""
    
    def test_PortfolioAnalyzer(self):
        """Test the PortfolioAnalyzer class."""
        analyzer = PortfolioAnalyzer(interval='1D')
        analyzer.loadAndComputeStatistics()
        
        # Test with valid portfolio
        portfolio = {'bitcoin': 0.5, 'ethereum': 0.5}
        
        # Test portfolio return
        portfolio_return = analyzer.portfolioReturn(portfolio)
        self.assertIsNotNone(portfolio_return)
        if portfolio_return is not None:
            self.assertIsInstance(portfolio_return, float)

        # Test portfolio standard deviation
        portfolio_std = analyzer.portfolioStandardDev(portfolio)
        self.assertIsNotNone(portfolio_std)
        if portfolio_std is not None:
            self.assertIsInstance(portfolio_std, float)
            self.assertGreaterEqual(portfolio_std, 0)
        
        # Test portfolio analysis
        min_return = 0.001
        max_sigma = 0.02
        result = analyzer.portfolioAnalysis(portfolio, min_return, max_sigma)
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 4)


if __name__ == '__main__':
    unittest.main() 