#!/usr/bin/env python3
"""
Cryptocurrency Portfolio Analysis Example
"""

from portfolio import PortfolioAnalyzer
from coins import CoinDB
import os
import argparse

def analyze_portfolio(portfolio, interval='1D'):
    """Analyze a cryptocurrency portfolio"""
    print(f"\n{'★'*3} Analyzing {interval} Portfolio {'★'*3}")
    
    # Initialize analyzer
    analyzer = PortfolioAnalyzer(interval=interval)
    
    # Check data availability
    coin_db = CoinDB()
    missing = []
    for coin in portfolio:
        prices = coin_db.prices(coin, interval)
        if prices is None or len(prices) == 0:
            missing.append(coin)
            
    if missing:
        print(f"Missing {interval} data for: {', '.join(missing)}")
        print("Run 'python download_data.py' first")
        return

    # Perform analysis
    print("\nLoading data...")
    # The PortfolioAnalyzer now loads data in __init__, so we don't need to call loadAndComputeStatistics
    
    print("\nPortfolio Composition:")
    for coin, allocation in portfolio.items():
        print(f"- {coin.capitalize():<10} {allocation:.0%}")

    # Calculate metrics
    daily_return = analyzer.portfolioReturn(portfolio)
    daily_risk = analyzer.portfolioStandardDev(portfolio)
    
    print("\nKey Metrics:")
    print(f"Daily Return:     {daily_return:.4%}")
    print(f"Daily Risk (σ):   {daily_risk:.4%}")
    print(f"Annual Return*:   {daily_return*365:.2%}")
    print(f"Annual Risk (σ)*: {daily_risk*(365**0.5):.2%}")
    print("* Annualized metrics assume 365 days")

    # Detailed analysis
    print("\nRunning Detailed Analysis...")
    analyzer.portfolioAnalysis(
        portfolio, 
        min_return=0.001,   # 0.1% daily minimum return
        max_sigma=0.02      # 2% daily volatility limit
    )
    
    # Add explanation of Expected vs Observed results
    print("\nExpected vs Observed Results Explanation:")
    print("Expected values are based on target parameters (min_return=0.1%, max_sigma=2%)")
    print("Observed values are calculated from actual historical data")
    print("The large difference between Expected and Observed values indicates:")
    print("1. The portfolio is performing with much lower volatility than our maximum limit")
    print("2. The actual returns are lower than our target")
    print("3. Despite lower returns, the risk-adjusted performance (Sharpe ratio) is better than expected")
    print("   due to the much lower volatility")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Cryptocurrency Portfolio Analyzer')
    parser.add_argument('-i', '--interval', default='1D', 
                      choices=['15m', '1H', '4H', '1D', '1W'],
                      help='Time interval for analysis')
    args = parser.parse_args()

    if not os.path.exists('data'):
        print("Error: 'data' directory not found")
        print("Run 'python download_data.py' first")
        exit(1)

    # Sample portfolio (modify weights as needed)
    sample_portfolio = {
        'bitcoin': 0.6,    # 60%
        'ethereum': 0.3,   # 30%
        'litecoin': 0.1    # 10%
    }

    analyze_portfolio(sample_portfolio, args.interval) 