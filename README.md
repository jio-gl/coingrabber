# coingrabber

Modern Portfolio Theory (Markowitz) creation and backtesting for Cryptocurrencies (Less Risky, Most Profitable, etc.)

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

