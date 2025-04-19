### Stocks
### Sean Welleck | 2014
# Updated for Python 3 compatibility and integration with scraper2024.py
#
# A module for retrieving stock information using the
# yahoo finance API (https://code.google.com/p/yahoo-finance-managed/wiki/CSVAPI)

from math import log
import csv
import requests
from collections import defaultdict
import numpy
try:
	from statsmodels.stats.covariance import cov_nearest
except ImportError:
	print('!!!!!!!!!!!!!!!!!!!!!!!! WARNING ERROR IMPORTING from statsmodels.stats.covariance import cov_nearest')
from datetime import datetime, timedelta

from coins import CoinDB
from dateconfig import DateRange

# Retrieves the stock quote for the given symbol
# from Yahoo Finance as a float.
# Input:  symbol - stock symbol as a string
# Output: price  - latest trade price from yahoo finance
def get_stock_quote(symbol):
	BASE_URL = 'http://download.finance.yahoo.com/d/quotes.csv?s='
	ID = symbol
	close_prop = '&f=l1'
	SUFFIX = '&e=.csv'
	url = "%s%s%s%s" % (BASE_URL, ID, close_prop, SUFFIX)
	try:
		response = requests.get(url)
		price = float(response.text.strip())
		return price
	except Exception as e:
		print(f"Error getting stock quote for {symbol}: {e}")
		return None

# Downloads the stock history for the given symbol,
# for the given date range, as a csv file.
# Input: symbol   - stock symbol as a string
#        start    - start date in the form 'mm/dd/yyyy'
#        end      - end date in the form 'mm/dd/yyyy'
#        outfile  - output filename, e.g. 'out.csv'
#        interval - trading interval; either d, w, m (daily, weekly, monthl7)
def csv_quote_history(symbol, start, end, outfile, interval='d'):
	response = _quote_history(symbol, start, end, interval)
	with open(outfile, 'w', newline='') as f:
		csv_reader = csv.reader(response.text.splitlines())
		csv_writer = csv.writer(f)
		for row in csv_reader:
			csv_writer.writerow(row)

# Gives the stock history for the given symbol,
# for the given date range, as a dictionary.
# Output: keys: ['High', 'Adj Close', 'Volume', 'Low', 'Date', 'Close', 'Open']
#         values: list
def quote_history_dict(symbol, start, end, interval='d'):#interval='m'):
	history = defaultdict(lambda: [])
	response = _quote_history(symbol, start, end, interval)
	if response is None:
		return {}  # Return empty dict instead of defaultdict
	try:
		dreader = csv.DictReader(response.text.splitlines())
		for row in dreader:
			for key in row.keys():
				history[key].insert(0, row[key])
		return history
	except Exception as e:
		print(f"Error processing history for {symbol}: {e}")
		return {}

def _quote_history(symbol, start, end, interval):
	BASE_URL = 'http://ichart.yahoo.com/table.csv?s='
	ID = symbol
	sm, sd, sy = start.split('/')
	em, ed, ey = end.split('/')
	url = "%s%s&a=%d&b=%d&c=%d&d=%d&e=%d&f=%d&g=%s" % (BASE_URL, ID, (int(sm)-1), int(sd), int(sy), (int(em)-1), int(ed), int(ey), interval)
	try:
		response = requests.get(url)
		return response
	except Exception as e:
		print(f"Error getting quote history for {symbol}: {e}")
		return None

def get_prices(symbol, start, end, interval='d'):#interval='m'):
	history = quote_history_dict(symbol, start, end, interval)
	if not history:
		return []
	prices = [round(float(x), 2) for x in history['Close']]
	if prices:
		prices[0] = round(float(history['Open'][0]), 2)
	return prices

def threeYearRange():
	end = datetime(DateRange.endYear, DateRange.endMonth, DateRange.endDay) #datetime.now()
	start = end - timedelta(days=365*3)
	printDate = lambda d: '%d/%d/%d' % (d.month, d.day, d.year)
	return printDate(start), printDate(end)

def get_returns(symbol, start=None, end=None, interval='d', maxDays=None):#interval='m'):
	if not start or not end:
		start, end = threeYearRange()

	coinDb = CoinDB()
	isShort = symbol[0] == '-'
	symbol = symbol.replace('-', '')
	
	prices = []
	try:
		if interval == 'd' and symbol in coinDb.coins:
			prices = coinDb.prices(symbol)
			prices = maxDays and prices[-maxDays:] or prices
		else:
			history = quote_history_dict(symbol, start, end, interval)
			if not history or 'Close' not in history:
				return []
			prices = [round(float(x), 2) for x in history['Close']]
			if prices:
				prices[0] = round(float(history['Open'][0]), 2)
	except Exception as e:
		print(f"Error getting returns for {symbol}: {e}")
		return []

	if len(prices) < 2:
		return []

	# Convert all prices to floats first
	prices = [float(p) for p in prices if isinstance(p, (int, float, str)) and str(p).replace('.','',1).isdigit()]
	
	return [(isShort and -1.0 or 1.0) * ((float(y)/float(x)) - 1) 
			for x, y in zip(prices[0:-1], prices[1:])]

def get_log_returns(symbol, start=None, end=None, interval='d'):#interval='m'):

	if not start or not end:
		start, end = threeYearRange()

	coinDb = CoinDB()
	isShort = symbol[0] == '-'
	symbol = symbol.replace('-', '')
	if interval=='d' and symbol in coinDb.coins:
		prices = coinDb.prices(symbol)
	else:
		history = quote_history_dict(symbol, start, end, interval)
		if not history:
			return []
		prices = [round(float(x), 2) for x in history['Close']]
		if prices:
			prices[0] = round(float(history['Open'][0]), 2)
	
	if len(prices) < 2:
		return []
	
	log_returns = [(isShort and -1.0 or 1.0)*log(y/x) for x, y in zip(prices[0:-1], prices[1:])]
	return log_returns

def get_yr_returns(symbol, start, end):
	history = quote_history_dict(symbol, start, end, 'd')
	if not history:
		return []
	prices = [round(float(x), 2) for x in history['Close']]
	if prices:
		prices[0] = round(float(history['Open'][0]), 2)
		prices.insert(0, prices[0])
	if len(prices) < 13:
		return []
	returns = [(y/x)-1 for x, y in zip(prices[0::12][:-1], prices[12::12])]
	return returns

def avg_return(symbol, start, end, interval='d', maxDays=None):
	if interval=='y':
		return numpy.mean(get_yr_returns(symbol, start, end))
	else:
		return numpy.mean(get_returns(symbol, start, end, interval, maxDays))

def cov_matrix(symbols, start, end, interval='d', maxDays=None):
	minLen = maxDays and maxDays or 1000000000
	data = []
	for s in symbols:
		if interval=='y':
			rets = get_yr_returns(s, start, end)
		else:
			rets = get_returns(s, start, end, interval)
		print(s, len(rets))
		minLen = min(minLen, len(rets))	
		data.append(numpy.array(rets))	
	data = [d[-minLen:] for d in data]
	print('INFO: NUMBER OF DAYS USED FOR PORTFOLIO OPTIMIZATION = ', minLen)
	x = numpy.array(data)
	return cov_nearest(numpy.cov(x))
