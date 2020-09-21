# coingrabber

## Introduction

Modern Portfolio Theory (Markowitz) creation and backtesting for Cryptocurrencies (Minimum Risk portfolio, Most Profitable portfolio, etc.)

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

## Example outputs

### Portfolios

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

### Backtesting

```
...
...
Tdays=7 Empiric=True start2017-04-21 end2017-05-21 EstRet=83.77 EstSigma=22.71 EstSharpe=3.69 Ret=219.77 Sigma=47.45 Sharpe=4.63 MaxDD=-3.69 AccumRet=7336375140391.67 AcumRetLeve=18340937850979.18
Tdays=7 Empiric=True start2017-04-24 end2017-05-24 EstRet=81.67 EstSigma=18.62 EstSharpe=4.39 Ret=253.93 Sigma=44.67 Sharpe=5.68 MaxDD=0.00 AccumRet=25965776353137.44 AcumRetLeve=64914440882843.59
Tdays=7 Empiric=True start2017-04-27 end2017-05-27 EstRet=79.82 EstSigma=19.48 EstSharpe=4.10 Ret=130.50 Sigma=46.67 Sharpe=2.80 MaxDD=0.00 AccumRet=59850299226145.38 AcumRetLeve=149625748065363.47
Tdays=7 Empiric=True start2017-04-30 end2017-05-30 EstRet=100.76 EstSigma=20.18 EstSharpe=4.99 Ret=147.17 Sigma=43.50 Sharpe=3.38 MaxDD=0.00 AccumRet=147933060607548.81 AcumRetLeve=369832651518872.00
Tdays=7 Empiric=True start2017-05-03 end2017-06-02 EstRet=98.05 EstSigma=22.52 EstSharpe=4.35 Ret=290.79 Sigma=55.56 Sharpe=5.23 MaxDD=-3.24 AccumRet=578110608042233.75 AcumRetLeve=1445276520105584.50
Tdays=7 Empiric=True start2017-05-06 end2017-06-05 EstRet=79.82 EstSigma=17.24 EstSharpe=4.63 Ret=205.76 Sigma=45.79 Sharpe=4.49 MaxDD=0.00 AccumRet=1767635837434288.00 AcumRetLeve=4419089593585720.00
Tdays=7 Empiric=True start2017-05-09 end2017-06-08 EstRet=83.31 EstSigma=17.30 EstSharpe=4.81 Ret=88.42 Sigma=29.48 Sharpe=3.00 MaxDD=0.00 AccumRet=3330641586665126.00 AcumRetLeve=8326603966662815.00
Tdays=7 Empiric=True start2017-05-12 end2017-06-11 EstRet=92.72 EstSigma=18.78 EstSharpe=4.94 Ret=70.43 Sigma=31.18 Sharpe=2.26 MaxDD=-8.17 AccumRet=5676517966795571.00 AcumRetLeve=14191294916988928.00
Tdays=7 Empiric=True start2017-05-15 end2017-06-14 EstRet=83.49 EstSigma=26.23 EstSharpe=3.18 Ret=64.37 Sigma=47.26 Sharpe=1.36 MaxDD=-6.64 AccumRet=9330655262574820.00 AcumRetLeve=23326638156437048.00
Tdays=7 Empiric=True start2017-05-18 end2017-06-17 EstRet=83.38 EstSigma=16.97 EstSharpe=4.91 Ret=135.79 Sigma=44.13 Sharpe=3.08 MaxDD=0.00 AccumRet=22000687195687104.00 AcumRetLeve=55001717989217760.00
Tdays=7 Empiric=True start2017-05-21 end2017-06-20 EstRet=110.99 EstSigma=26.09 EstSharpe=4.25 Ret=80.45 Sigma=38.79 Sharpe=2.07 MaxDD=-8.24 AccumRet=39699187695376824.00 AcumRetLeve=99247969238442064.00
Tdays=7 Empiric=True start2017-05-24 end2017-06-23 EstRet=173.21 EstSigma=36.01 EstSharpe=4.81 Ret=90.69 Sigma=36.08 Sharpe=2.51 MaxDD=-5.24 AccumRet=75702265319846384.00 AcumRetLeve=189255663299615968.00
Tdays=7 Empiric=True start2017-05-27 end2017-06-26 EstRet=105.50 EstSigma=26.46 EstSharpe=3.99 Ret=24.29 Sigma=28.01 Sharpe=0.87 MaxDD=-13.53 AccumRet=94094107668622528.00 AcumRetLeve=235235269171556320.00
Tdays=7 Empiric=True start2017-05-30 end2017-06-29 EstRet=80.37 EstSigma=36.07 EstSharpe=2.23 Ret=41.32 Sigma=38.00 Sharpe=1.09 MaxDD=0.00 AccumRet=132975862660852128.00 AcumRetLeve=332439656652130304.00
Tdays=7 Empiric=True start2017-06-02 end2017-07-02 EstRet=61.32 EstSigma=35.79 EstSharpe=1.71 Ret=12.09 Sigma=62.49 Sharpe=0.19 MaxDD=0.00 AccumRet=149047202637578336.00 AcumRetLeve=372618006593945856.00
Total Final return (period of 30 days, training days 7) discounting Costs = 143188610738300000.0000 percent  AverageSharpe = 2.3596  RetPerDay = 2.3632 percent
------------------------------------------------
BEST GLOBAL AVERAGE SHARPE = 2.3596  PeriodDaysTest = 30  TrainingDaysTest = 7
```
