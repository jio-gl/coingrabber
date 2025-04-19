#!/usr/bin/env python3
"""
Uncorrelated Portfolio Builder - Ray Dalio's "Holy Grail" Strategy

This script implements Ray Dalio's strategy of finding uncorrelated assets
to build a portfolio that reduces risk without sacrificing returns.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import argparse
from portfolio import PortfolioAnalyzer
from coins import CoinDB
import os
import itertools
from datetime import datetime

def load_data(interval='1D'):
    """Load price data for all available coins"""
    coin_db = CoinDB()
    coins = coin_db.coins
    
    data = {}
    for coin in coins:
        try:
            df = pd.read_csv(f'data/{interval}_price_{coin}.csv')
            # Calculate returns as percentage change
            df['returns'] = df['prices'].pct_change().dropna()
            data[coin] = df['returns']
            print(f"Loaded data for {coin}")
        except Exception as e:
            print(f"Error loading {coin} data: {str(e)}")
    
    return data

def calculate_correlation_matrix(returns_data):
    """Calculate correlation matrix for all coins"""
    # Create a DataFrame with all returns
    returns_df = pd.DataFrame(returns_data)
    
    # Calculate correlation matrix
    corr_matrix = returns_df.corr()
    
    return corr_matrix

def calculate_annualized_return(returns_series):
    """
    Calculate the annualized return from a series of daily returns
    
    Args:
        returns_series: Series of daily returns
        
    Returns:
        Annualized return as a decimal
    """
    # Calculate the average daily return
    avg_daily_return = returns_series.mean()
    
    # Annualize by multiplying by 252 trading days
    annualized_return = avg_daily_return * 252
    
    return annualized_return

def find_uncorrelated_assets(corr_matrix, returns_data, num_assets=5, max_correlation=0.3, min_return=0.0):
    """
    Find a set of uncorrelated assets
    
    Args:
        corr_matrix: Correlation matrix
        returns_data: Dictionary of returns data for each asset
        num_assets: Number of assets to select
        max_correlation: Maximum allowed correlation between selected assets
        min_return: Minimum annualized return required for an asset
        
    Returns:
        List of selected assets
    """
    assets = corr_matrix.index.tolist()
    
    # Filter assets by minimum return if specified
    if min_return > 0:
        filtered_assets = []
        for asset in assets:
            # Calculate annualized return using the proper method
            annual_return = calculate_annualized_return(returns_data[asset])
            if annual_return >= min_return:
                filtered_assets.append(asset)
        
        if filtered_assets:
            assets = filtered_assets
            print(f"Filtered to {len(assets)} assets with minimum annualized return of {min_return:.2%}")
        else:
            print(f"Warning: No assets meet the minimum annualized return of {min_return:.2%}. Using all assets.")
    
    # If we have fewer assets than requested, return all of them
    if len(assets) <= num_assets:
        return assets
    
    # Start with the first asset
    selected = [assets[0]]
    
    # For each remaining asset, check correlation with already selected assets
    for asset in assets[1:]:
        # Check if adding this asset would exceed max correlation with any selected asset
        can_add = True
        for selected_asset in selected:
            correlation = abs(corr_matrix.loc[asset, selected_asset])
            if correlation > max_correlation:
                can_add = False
                break
        
        if can_add:
            selected.append(asset)
            if len(selected) >= num_assets:
                break
    
    # If we couldn't find enough uncorrelated assets, add the least correlated ones
    if len(selected) < num_assets:
        remaining = [a for a in assets if a not in selected]
        
        # Calculate average correlation with selected assets for each remaining asset
        avg_correlations = {}
        for asset in remaining:
            correlations = [abs(corr_matrix.loc[asset, s]) for s in selected]
            avg_correlations[asset] = sum(correlations) / len(correlations)
        
        # Sort by average correlation and add the least correlated ones
        sorted_remaining = sorted(avg_correlations.items(), key=lambda x: x[1])
        for asset, _ in sorted_remaining:
            if len(selected) >= num_assets:
                break
            selected.append(asset)
    
    return selected

def calculate_portfolio_metrics(returns_data, portfolio):
    """Calculate return and risk metrics for the portfolio"""
    # Create a DataFrame with returns for selected assets
    portfolio_returns = pd.DataFrame({coin: returns_data[coin] for coin in portfolio})
    
    # Calculate portfolio returns (equal weight)
    weights = {coin: 1.0/len(portfolio) for coin in portfolio}
    portfolio_returns['portfolio'] = sum(portfolio_returns[coin] * weights[coin] for coin in portfolio)
    
    # Calculate metrics
    # Calculate daily metrics
    daily_return = portfolio_returns['portfolio'].mean()
    daily_volatility = portfolio_returns['portfolio'].std()
    
    # Calculate annualized metrics using the proper method
    annual_return = calculate_annualized_return(portfolio_returns['portfolio'])
    annual_volatility = daily_volatility * np.sqrt(252)  # Annualized volatility
    
    # Calculate Sharpe ratio
    sharpe_ratio = annual_return / annual_volatility if annual_volatility > 0 else 0
    
    return {
        'daily_return': daily_return,
        'annual_return': annual_return,
        'daily_volatility': daily_volatility,
        'annual_volatility': annual_volatility,
        'sharpe_ratio': sharpe_ratio,
        'weights': weights
    }

def plot_correlation_heatmap(corr_matrix, selected_assets=None):
    """Plot correlation heatmap for selected assets"""
    if selected_assets:
        corr_matrix = corr_matrix.loc[selected_assets, selected_assets]
    
    plt.figure(figsize=(10, 8))
    plt.imshow(corr_matrix, cmap='coolwarm', vmin=-1, vmax=1)
    plt.colorbar(label='Correlation')
    plt.xticks(range(len(corr_matrix.columns)), corr_matrix.columns, rotation=45, ha='right')
    plt.yticks(range(len(corr_matrix.index)), corr_matrix.index)
    plt.title('Correlation Matrix')
    plt.tight_layout()
    
    # Save the plot
    os.makedirs('output', exist_ok=True)
    plt.savefig('output/correlation_heatmap.png')
    print("Correlation heatmap saved to output/correlation_heatmap.png")

def plot_portfolio_performance(returns_data, portfolio, weights):
    """Plot portfolio performance over time"""
    # Create a DataFrame with returns for selected assets
    portfolio_returns = pd.DataFrame({coin: returns_data[coin] for coin in portfolio})
    
    # Calculate portfolio returns
    portfolio_returns['portfolio'] = sum(portfolio_returns[coin] * weights[coin] for coin in portfolio)
    
    # Calculate cumulative returns
    cumulative_returns = (1 + portfolio_returns).cumprod()
    
    plt.figure(figsize=(12, 6))
    for coin in portfolio:
        plt.plot(cumulative_returns.index, cumulative_returns[coin], label=coin, alpha=0.7)
    plt.plot(cumulative_returns.index, cumulative_returns['portfolio'], label='Portfolio', linewidth=2)
    plt.xlabel('Time')
    plt.ylabel('Cumulative Return')
    plt.title('Portfolio Performance')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    
    # Save the plot
    os.makedirs('output', exist_ok=True)
    plt.savefig('output/portfolio_performance.png')
    print("Portfolio performance plot saved to output/portfolio_performance.png")

def main():
    parser = argparse.ArgumentParser(description='Build an uncorrelated portfolio using Ray Dalio\'s strategy')
    parser.add_argument('-i', '--interval', default='1D', choices=['15m', '1H', '4H', '1D', '1W'],
                      help='Time interval for analysis')
    parser.add_argument('-n', '--num-assets', type=int, default=5,
                      help='Number of assets to include in the portfolio')
    parser.add_argument('-c', '--max-correlation', type=float, default=0.3,
                      help='Maximum allowed correlation between selected assets')
    parser.add_argument('-r', '--min-return', type=float, default=0.0,
                      help='Minimum annualized return required for an asset (as decimal, e.g., 0.1 for 10%)')
    args = parser.parse_args()
    
    print("\n" + "="*80)
    print("RAY DALIO'S 'HOLY GRAIL' PORTFOLIO BUILDER".center(80))
    print("="*80)
    print("\nPARAMETERS:")
    print(f"  Time Interval: {args.interval} (Available: 15m, 1H, 4H, 1D, 1W)")
    print(f"  Number of Assets: {args.num_assets} (Default: 5)")
    print(f"  Maximum Correlation: {args.max_correlation} (Default: 0.3)")
    print(f"  Minimum Annualized Return: {args.min_return:.2%} (Default: 0.0%)")
    print("\n" + "-"*80)
    
    print(f"Loading {args.interval} data for all available coins...")
    returns_data = load_data(args.interval)
    
    if not returns_data:
        print("No data available. Please run download_data.py first.")
        return
    
    print(f"Calculating correlation matrix for {len(returns_data)} coins...")
    corr_matrix = calculate_correlation_matrix(returns_data)
    
    print(f"Finding {args.num_assets} uncorrelated assets (max correlation: {args.max_correlation})...")
    selected_assets = find_uncorrelated_assets(corr_matrix, returns_data, args.num_assets, args.max_correlation, args.min_return)
    
    print("\nSELECTED UNCORRELATED ASSETS:")
    for i, asset in enumerate(selected_assets, 1):
        # Calculate and display both daily and annualized returns for each selected asset
        daily_return = returns_data[asset].mean()
        annual_return = calculate_annualized_return(returns_data[asset])
        print(f"  {i}. {asset} (Daily Return: {daily_return*100:.4f}%, Annualized Return: {annual_return*100:.2f}%)")
    
    print("\nCalculating portfolio metrics...")
    metrics = calculate_portfolio_metrics(returns_data, selected_assets)
    
    print("\nPORTFOLIO METRICS:")
    print(f"  Daily Return: {metrics['daily_return']*100:.4f}%")
    print(f"  Annualized Return: {metrics['annual_return']*100:.2f}%")
    print(f"  Daily Volatility: {metrics['daily_volatility']*100:.4f}%")
    print(f"  Annualized Volatility: {metrics['annual_volatility']*100:.2f}%")
    print(f"  Sharpe Ratio: {metrics['sharpe_ratio']:.2f}")
    
    print("\nPORTFOLIO WEIGHTS:")
    for asset, weight in metrics['weights'].items():
        print(f"  {asset}: {weight:.2%}")
    
    print("\nGenerating visualizations...")
    plot_correlation_heatmap(corr_matrix, selected_assets)
    plot_portfolio_performance(returns_data, selected_assets, metrics['weights'])
    
    print("\nRAY DALIO'S 'HOLY GRAIL' STRATEGY SUMMARY:")
    print("------------------------------------------")
    print("1. We've selected assets with low correlation to each other")
    print("2. This portfolio should reduce risk without sacrificing returns")
    print("3. The strategy works by finding assets that move independently")
    print("4. This creates natural diversification that protects against market downturns")
    print("5. The portfolio should be rebalanced periodically to maintain low correlations")
    
    # Save the portfolio to a file
    os.makedirs('output', exist_ok=True)
    with open('output/uncorrelated_portfolio.txt', 'w') as f:
        f.write(f"Uncorrelated Portfolio ({datetime.now().strftime('%Y-%m-%d')})\n")
        f.write(f"Interval: {args.interval}\n")
        f.write(f"Number of assets: {args.num_assets}\n")
        f.write(f"Max correlation: {args.max_correlation}\n")
        f.write(f"Min annualized return: {args.min_return:.2%}\n\n")
        f.write("Selected Assets:\n")
        for i, asset in enumerate(selected_assets, 1):
            daily_return = returns_data[asset].mean()
            annual_return = calculate_annualized_return(returns_data[asset])
            f.write(f"{i}. {asset} (Daily Return: {daily_return*100:.4f}%, Annualized Return: {annual_return*100:.2f}%)\n")
        f.write("\nPortfolio Weights:\n")
        for asset, weight in metrics['weights'].items():
            f.write(f"{asset}: {weight:.2%}\n")
        f.write("\nPortfolio Metrics:\n")
        f.write(f"Daily Return: {metrics['daily_return']*100:.4f}%\n")
        f.write(f"Annualized Return: {metrics['annual_return']*100:.2f}%\n")
        f.write(f"Daily Volatility: {metrics['daily_volatility']*100:.4f}%\n")
        f.write(f"Annualized Volatility: {metrics['annual_volatility']*100:.2f}%\n")
        f.write(f"Sharpe Ratio: {metrics['sharpe_ratio']:.2f}\n")
    
    print("\nPortfolio details saved to output/uncorrelated_portfolio.txt")
    print("\n" + "="*80)
    print("To run with different parameters:")
    print("  python uncorrelated.py -i [interval] -n [num_assets] -c [max_correlation] -r [min_return]")
    print("  Example: python uncorrelated.py -i 1D -n 7 -c 0.2 -r 0.1")
    print("="*80)

if __name__ == "__main__":
    main() 