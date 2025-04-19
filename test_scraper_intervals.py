#!/usr/bin/env python3
"""
Unit tests for scraper2024 time intervals
"""

import unittest
from scraper2024 import get_data, coin_to_coin_number

class TestScraperIntervals(unittest.TestCase):
    """Test supported time intervals for scraper2024"""
    
    def setUp(self):
        """Get Bitcoin ID before each test"""
        self.bitcoin_id = coin_to_coin_number('bitcoin')
        self.assertIsNotNone(self.bitcoin_id, "Failed to get Bitcoin ID")
        self.assertIsInstance(self.bitcoin_id, int, "Bitcoin ID should be integer")
        self.working_intervals = []

    def test_interval_coverage(self):
        """Test all potential intervals and report working ones"""
        test_intervals = [
            '15m', '30m', '1H', '4H', 
            '1D', '7D', '1M', '3M', '1Y'
        ]
        
        for interval in test_intervals:
            with self.subTest(interval=interval):
                try:
                    data = get_data(self.bitcoin_id, interval)
                    if self._is_valid_response(data):
                        self.working_intervals.append(interval)
                        print(f"✅ {interval} works")
                    else:
                        print(f"❌ {interval} returned invalid data")
                except Exception as e:
                    print(f"🚫 {interval} failed: {str(e)}")

    def _is_valid_response(self, data):
        """Check if response contains valid data"""
        return (
            data is not None and
            'data' in data and
            'points' in data['data'] and
            len(data['data']['points']) > 0
        )

    def tearDown(self):
        """Report working intervals after all tests"""
        if self.working_intervals:
            print("\nWorking intervals without API key:")
            for interval in sorted(self.working_intervals):
                print(f"- {interval}")
        else:
            print("\nNo intervals worked without API key")

if __name__ == '__main__':
    unittest.main() 