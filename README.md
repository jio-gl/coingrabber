# CoinGrabber

A Python tool for analyzing cryptocurrency portfolios and tracking cryptocurrency prices.

<img width="1149" alt="image" src="https://github.com/user-attachments/assets/b43e0098-16e6-4a98-b0ae-c6f575c0e31c" />

## TLDR;

```bash
python download_data.py -i 1D # download data from CMC
python portfolio_example.py   # analyze an example portfolio
python optimization.py        # GUI choose coins  and optimize efficieny frontier
```

## Overview

CoinGrabber is a Python-based tool that allows users to:
- Fetch and analyze cryptocurrency price data
- Calculate portfolio returns and risk metrics
- Track historical cryptocurrency performance
- Generate reports on portfolio performance
- Optimize cryptocurrency portfolios

## Requirements

- Python 3.6+
- Required Python packages:
  - requests
  - pandas
  - numpy
  - matplotlib (for visualization)
  - cvxopt (for portfolio optimization)
  - tkinter (for GUI)

## Installation

1. Clone the repository:
```
git clone https://github.com/yourusername/coingrabber.git
cd coingrabber
```

2. Install the required packages:
```
pip install -r requirements.txt
```

## Main Scripts

### 1. Downloading Cryptocurrency Data

To download daily cryptocurrency data for all available coins:

```
python download_data.py
```

This will download 1-day interval data for all cryptocurrencies and save it to the `data` directory.

To download data for a specific interval:

```
python download_data.py -i 1D  # For daily data
python download_data.py -i 1H  # For hourly data
python download_data.py -i 4H  # For 4-hour data
python download_data.py -i 15m # For 15-minute data
```

### 2. Portfolio Analysis Example

To run a simple portfolio analysis with default settings:

```
python portfolio_example.py
```

This will analyze a sample portfolio containing Bitcoin (60%), Ethereum (30%), and Litecoin (10%) using daily data.

### 3. Portfolio Optimization GUI

To launch the portfolio optimization GUI:

```
python optimization.py
```

The GUI allows you to:
- Select cryptocurrencies to include in your portfolio
- Choose optimization objective (Best Return, Best Risk, or Best Sharpe Ratio)
- Set optimization parameters (generations, population size, mutation rate)
- Visualize the efficient frontier
- View the optimal portfolio composition

### 4. Uncorrelated Portfolio Builder

To build a portfolio of uncorrelated cryptocurrencies using Ray Dalio's "Holy Grail" strategy:

```
python uncorrelated.py
```

This script:
- Finds cryptocurrencies with low correlation to each other
- Filters assets based on minimum annualized return
- Calculates portfolio metrics (returns, volatility, Sharpe ratio)
- Generates visualizations (correlation heatmap, portfolio performance)
- Saves the portfolio details to an output file

You can customize the analysis with these parameters:
```
python uncorrelated.py -i 1D -n 7 -c 0.2 -r 0.1
```
Where:
- `-i` or `--interval`: Time interval (15m, 1H, 4H, 1D, 1W)
- `-n` or `--num-assets`: Number of assets to include (default: 5)
- `-c` or `--max-correlation`: Maximum allowed correlation (default: 0.3)
- `-r` or `--min-return`: Minimum annualized return required (default: 0.0)

## Project Structure

- `download_data.py`: Downloads cryptocurrency data for different time intervals
- `portfolio_example.py`: Demonstrates portfolio analysis with a sample portfolio
- `optimization.py`: Provides a GUI for portfolio optimization
- `uncorrelated.py`: Implements Ray Dalio's strategy for building uncorrelated portfolios
- `scraper2024.py`: Contains functions for fetching cryptocurrency data
- `coins.py`: Defines the `CoinDB` class for managing cryptocurrency data
- `portfolio.py`: Contains the `PortfolioAnalyzer` class for portfolio analysis
- `dateconfig.py`: Defines date ranges for data analysis
- `stocks.py`: Provides functions for fetching stock data (for comparison)

## License

This project is licensed under the MIT License - see the LICENSE file for details.
