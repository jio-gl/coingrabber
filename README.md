# coingrabber

## Introduction

Modern Portfolio Theory (Markowitz) creation and backtesting for Cryptocurrencies (Less Risky, Most Profitable, etc.)

## Usage

* Download currency data:
  * choose list of coins in `coins.py`, select coin set where it says
        `coins = coinSets ['cap'] # for example`.
  * run `grabber.py`
  * Options: `updateLastDays = True` (update currencies that already have a db file in data / `5min_[coin-name].txt`),
              `downloadMissing = True` (download complete coin if the db file data / `5min_[coin-name].txt` does not exist)
  * to generate daily data (data / `1d_[coin-name].txt`) you need to run also:
        `python fivemin2daily.py`

* Build Portfolio of Minimum Risk or Maximum Sharpe for the Current Day
  * run `current.py`
  * options, inside the file change flag `MAXIMIZE_SHARPE = True` (or `False` for a Minimum Risk portfolio)
                (result also in `logpfolio.txt`)

* Build Portfolio of Minimum Risk or Maximum Sharpe in Several periods for backtesting
  * run `strategy.py`
  * options, inside the file change flag `MAXIMIZE_SHARPE = True` (or `False` for a Minimum Risk portfolio)
                (result also in `logpfolio.txt`)
  * also if `TARGET_RETURN` is not `None`, then try to minimize the risk for that return.

## Example output

Each day a different portfolio is proposed:

```
PortfolioStartDate=2017-06-11 [('factom', '0.238'), ('-dogecoin', '0.236'), ('maidsafecoin', '0.218'), ('bitshares', '0.177'), ('stellar', '0.131')]

PortfolioStartDate=2017-06-12 [('bitshares', '0.267'), ('ethereum', '0.258'), ('-dogecoin', '0.230'), ('maidsafecoin', '0.134'), ('factom', '0.111')]

PortfolioStartDate=2017-06-13 [('bitshares', '0.477'), ('dash', '0.313'), ('-dogecoin', '0.211')]

PortfolioStartDate=2017-06-14 [('ethereum', '0.448'), ('dash', '0.200'), ('bitshares', '0.192'), ('-dogecoin', '0.160')]

PortfolioStartDate=2017-06-15 [('ethereum', '0.610'), ('factom', '0.196'), ('dash', '0.110'), ('bitshares', '0.084')]

PortfolioStartDate=2017-06-16 [('-monero', '0.357'), ('ethereum', '0.323'), ('dash', '0.312'), ('bitshares', '0.008')]

PortfolioStartDate=2017-06-17 [('-maidsafecoin', '0.235'), ('-monero', '0.214'), ('dash', '0.160'), ('litecoin', '0.142'), ('factom', '0.135'), ('-stellar', '0.114')]

PortfolioStartDate=2017-06-18 [('-maidsafecoin', '0.265'), ('-stellar', '0.218'), ('factom', '0.207'), ('litecoin', '0.160'), ('-bitshares', '0.149')]

PortfolioStartDate=2017-06-19 [('litecoin', '0.340'), ('-bitshares', '0.285'), ('-stellar', '0.222'), ('factom', '0.082'), ('-monero', '0.070')]

PortfolioStartDate=2017-06-20 [('litecoin', '0.475'), ('-bitshares', '0.387'), ('-stellar', '0.137')]

PortfolioStartDate=2017-06-21 [('litecoin', '0.697'), ('-dogecoin', '0.275'), ('dash', '0.028')]

PortfolioStartDate=2017-06-22 [('ripple', '0.436'), ('-stellar', '0.268'), ('litecoin', '0.200'), ('dash', '0.079'), ('-dogecoin', '0.016')]

PortfolioStartDate=2017-06-23 [('litecoin', '0.352'), ('ripple', '0.338'), ('-ethereum', '0.311')]

PortfolioStartDate=2017-06-24 [('-bitshares', '0.072'), ('-ethereum', '0.071'), ('litecoin', '0.060'), ('ripple', '0.059'), ('-dash', '0.057'), ('factom', '0.055'), ('-stellar', '0.052'), ('-dogecoin', '0.051'), ('-monero', '0.049'), ('maidsafecoin', '0.048'), ('-maidsaf\
ecoin', '0.047'), ('monero', '0.045'), ('dogecoin', '0.044'), ('-factom', '0.044'), ('stellar', '0.044'), ('-litecoin', '0.043'), ('dash', '0.042'), ('-ripple', '0.040'), ('bitshares', '0.039'), ('ethereum', '0.038')]

PortfolioStartDate=2017-06-25 [('-ethereum', '0.456'), ('maidsafecoin', '0.273'), ('ripple', '0.270')]
...
...
```
