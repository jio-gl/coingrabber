import unittest
from unittest.mock import patch
from datetime import datetime, timedelta
from stocks import get_stock_quote, quote_history_dict, get_returns
import pandas as pd

class TestStocks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.valid_symbol = "AAPL"
        cls.invalid_symbol = "INVALID123"
        cls.end_date = datetime.now().strftime('%Y-%m-%d')
        cls.start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
        
        # Mock historical data
        cls.mock_history = pd.DataFrame({
            'Open': [150.0, 151.0],
            'High': [152.0, 153.0],
            'Low': [149.0, 150.5],
            'Close': [151.5, 152.5],
            'Volume': [1000000, 1200000]
        }, index=pd.date_range(start='2023-01-01', periods=2))

    @patch('yfinance.Ticker')
    def test_get_stock_quote_valid(self, mock_ticker):
        mock_instance = mock_ticker.return_value
        mock_instance.history.return_value = pd.DataFrame({
            'Close': [175.0]
        }, index=pd.date_range(end='2023-12-31', periods=1))
        
        price = get_stock_quote(self.valid_symbol)
        self.assertEqual(price, 175.0)

    @patch('yfinance.Ticker')
    def test_get_stock_quote_invalid(self, mock_ticker):
        mock_instance = mock_ticker.return_value
        mock_instance.history.return_value = pd.DataFrame()
        
        price = get_stock_quote(self.invalid_symbol)
        self.assertIsNone(price)

    @patch('yfinance.Ticker')
    def test_quote_history_dict_valid(self, mock_ticker):
        mock_instance = mock_ticker.return_value
        mock_instance.history.return_value = self.mock_history
        
        history = quote_history_dict(self.valid_symbol, self.start_date, self.end_date)
        self.assertEqual(history['Close'], [151.5, 152.5])
        self.assertEqual(history['Date'], ['2023-01-01', '2023-01-02'])

    @patch('yfinance.Ticker')
    def test_quote_history_dict_invalid(self, mock_ticker):
        mock_instance = mock_ticker.return_value
        mock_instance.history.return_value = pd.DataFrame()
        
        history = quote_history_dict(self.invalid_symbol, self.start_date, self.end_date)
        self.assertEqual(history, {})

    def test_get_returns_valid(self):
        """Test calculating returns for valid symbol"""
        returns = get_returns("MSFT", self.start_date, self.end_date)
        
        self.assertGreater(len(returns), 50)  # Should have ~252 daily returns
        self.assertIsInstance(returns[0], float)
        
        # Verify returns are within reasonable bounds
        for r in returns:
            self.assertGreater(r, -1.0)  # No -100% daily drops
            self.assertLess(r, 2.0)      # No 200% daily gains

    def test_get_returns_invalid(self):
        """Test handling invalid symbol in returns calculation"""
        returns = get_returns(self.invalid_symbol, self.start_date, self.end_date)
        self.assertEqual(len(returns), 0)

if __name__ == '__main__':
    unittest.main(verbosity=2) 