import csv
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import numpy
from math import log,exp,sqrt
from functools import reduce
import operator

import numpy as np

ifname = 'bitcoin_1d.csv' #'TSLA.csv' #'btc2.csv'
business_days = True

vals = []
with open(ifname, 'rb') as csvfile:
     spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
     has_header = csv.Sniffer().has_header(csvfile.read(1024))
     spamreader = csv.reader( open(ifname, 'rb'), delimiter=',', quotechar='|')
     for row in spamreader:
          if has_header:
               has_header = False
               continue
          vals.append( float(row[3]) )

if business_days:
     years = 1.0 # len(vals) / 251.
     year_days = 251.
else:
     years = 1.0 # len(vals) / 365.
     year_days = 365.

def quad(vals):
     return map( lambda x:x**2, vals)

def delta(vals):
     ret = []
     for i in range(1,len(vals)):
          prev = vals[i-1]
          curr = vals[i]
          diff = curr - prev
          ret.append( diff )
     return [0.0]+ret

def ratio(vals):
     ret = []
     for i in range(1,len(vals)):
          prev = vals[i-1]
          curr = vals[i]
          diff = curr / prev
          ret.append( diff )
     return [1.0]+ret

def ratio_change(vals):
     ret = []
     for i in range(1,len(vals)):
          prev = vals[i-1]
          curr = vals[i]
          diff = (curr / prev) - 1.0
          ret.append( diff )
     return [1.0]+ret

def U(t,dvals):
     return dvals[t] > 0 and 1 or 0

def Uw(t,rvals):
     return rvals[t] > 1.0 and rvals[t]-1.0 or 0

def Uws(t,rvals):
     return rvals[t-1] * rvals[t] > 1.0 and 1 or 0

def Uwseq(t,rvals):
     return (rvals[t-1] > 1.0 and rvals[t] > 1.0) and 1 or 0

def Uwseq2(t,rvals):
     return (rvals[t-1] > 1.0 and rvals[t] > 1.0) and rvals[t]-1.0 or 0

def Uwsw(t,rvals):
     return rvals[t-1] * rvals[t] > 1.0 and (rvals[t-1] * rvals[t])-1.0 or 0

def D(t,dvals):
     return dvals[t] < 0 and 1 or 0

def Dw(t,rvals):
     return rvals[t] < 1.0 and (1.0/rvals[t])-1.0 or 0

def Dws(t,rvals):
     return rvals[t] * rvals[t-1] < 1.0 and 1 or 0

def Dwseq(t,rvals):
     return (rvals[t-1] < 1.0 and rvals[t] < 1.0) and 1 or 0

def Dwseq2(t,rvals):
     return (rvals[t-1] < 1.0 and rvals[t] < 1.0) and (1.0/rvals[t])-1.0 or 0

def Dwsw(t,rvals):
     return rvals[t] * rvals[t-1] < 1.0 and (1./(rvals[t] * rvals[t-1]))-1.0 or 0

def RSI(vals, window_size=31, sampleSize=5000, startPoint=0, ob=58, os=42, years=None,year_days=None, use_weighted=False):

     fee = 0.00 #0.26
     vals = vals[startPoint:startPoint+sampleSize]

     if business_days:
          years = 1.0 # len(vals) / 251.
          year_days = 251.
     else:
          years = 1.0 # len(vals) / 365.
          year_days = 365.

     ret = [] # [0.0]*window_size
     dvals = delta(vals)
     rcvals = ratio_change(vals)
     stdev = numpy.std( rcvals )
     
     # http://www.investopedia.com/university/optionvolatility/volatility2.asp
     volatility = stdev * 15.937
     #print 'VOLATILITY=',volatility

     beta = 1.0/window_size
     overbought,oversold = ob,os
     n_up,n_down = 0,0
     round_trips = 0
     bought = False
     usd = 1.0
     stock = 0.0
     wins = 0
     trades = 0
     prev_price = -1
     max_loss = 1.0
     the_ret = sum( [ abs(log(abs(d))) for d in dvals if d != 0.0 ] ) / (float(sampleSize)/year_days)

     rvals = ratio(vals)
     the_ret2 = ((reduce( operator.mul, [ ( d>1.0 and d or 1/d ) for d in rvals if d != 0.0] , 1)-1.0)*100) / (float(sampleSize)/year_days)

     ddlist = [] # drawdown as tuples (localmax1,localmin1)
     localmax = 0
     localmaxdd = 0
     RSIs = []
     for (r,d),t in zip(zip(rvals,dvals),range(len(vals))):

          if t < window_size:
               if d > 0.0:
                    n_up += 1
               if d < 0.0:
                    n_down += 1
               continue
          
          if stock > 0:
               pfolio = stock * vals[t]
          else:
               pfolio = usd
          if pfolio > localmax:
               localmax = pfolio
          elif localmax - pfolio > localmaxdd:
               ddlist.append( localmax - pfolio )
               localmaxdd = localmax - pfolio
               

          if not use_weighted:
               n_up = (1-beta)*n_up + beta * U(t,dvals)
               n_down = (1-beta)*n_down + beta * D(t,dvals)
          else:
               n_up = (1-beta)*n_up + beta * Uwsw(t,rvals)
               n_down = (1-beta)*n_down + beta * Dwsw(t,rvals)

          RS = (n_up) / (n_down)
          RSI = 100.0*RS/(1.0+RS)
          #print 'RSI',RSI
          RSIs.append( RSI )
          if RSI > overbought:
               msg = 'OVERBOUGHT'
               if bought:
                    msg += ' - SELL'
                    bought = False
                    round_trips += 1
                    usd = stock * vals[t] * (100.-fee)/100.

                    max_loss = min(max_loss,usd)
                    stock = 0.0
                    trades += 1
                    if prev_price >= 0 and prev_price < vals[t]:
                         wins += 1
                    prev_price = vals[t]
                    
          elif RSI < oversold:
               msg = 'OVERSOLD'
               if not bought:
                    msg += ' - BUY'
                    bought = True
                    max_loss = min(max_loss,usd)
                    stock = usd / vals[t] * (100.-fee)/100.
                    usd = 0.0
                    trades += 1
                    if prev_price >= 0 and prev_price > vals[t]:
                         wins += 1
                    prev_price = vals[t]
          else:
               msg = ''
          ret.append(RSI)

     #print 'Average RSI',sum(ret)/len(ret)
     #print 'Median RSI',np.median(ret)

     if stock > 0.0:
          usd = stock * vals[-1]
     retrn = (usd-1.0)*100.0

     if trades > 0:
          winning = (100.0*float(wins)/trades)
     else:
          winning = 0.0

     if ddlist != []:
          dd = (100.0*max(ddlist))
     else: 
          dd = 0.0

     sharpe = (volatility!= 0 and years!=0) and (retrn / years) / volatility or retrn
     norm_return = the_ret2!=0.0 and retrn / the_ret2 or retrn
     return [round_trips/years,retrn/years, winning, dd, sharpe, norm_return]


def list_sum(l1,l2):
     return [ a+b for a,b in zip(l1,l2) ]

def list_div(l,f):
     return [ v/f for v in l ]

def min_list( l1,l2 ):
     return [ min(a,b) for a,b in zip(l1,l2) ]

def max_list( l1,l2 ):
     return [ max(a,b) for a,b in zip(l1,l2) ]

if __name__ == '__main__':

     h = open('hist.csv','w')
     maxret,maxrettrips,maxsharpe,maxnret,maxtripdown,maxrtd = 0.0, 0.0, 0.0, 0.0, 0.0, 0.0
     mob,mos,mob_rt,mos_rt,mob_sr,mos_sr,mob_nr,mos_nr,mob_td,mos_td,mos_rtd,mob_rtd = -1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1
     samples = 1
     max_params, max_params_rt, max_params_sr, max_params_nr, max_params_td, max_params_rtd = None, None, None, None, None, None
     for ob in np.arange(66.56,76.00,0.05):#(51.56,53.0,0.01):#range(67,90,1): #(62,63)
          for os in np.arange(56.00,66.55,0.05):#range(40,66,1): # (44,45)

               logperw = open('log_per_window.txt','w')

               init = [0.0]*6
               initmin,initmax = None,None
               for i in range(samples):
                    
                    rsi = RSI(vals,sampleSize=290,startPoint=-i-290-1,ob=ob,os=os,years=years,year_days=year_days)
                    h.write('%s\n'% ('Bootstrap %d,'%i + ','.join( map(lambda f: '%.2f'%f,list(rsi[:-1])) ) +','+  ','.join( map(lambda f: '%.5f'%f,list(rsi[-1:])))  )  )
                    init = list_sum( init, rsi )
                    if not initmin:
                         initmin = rsi
                         initmax = rsi
                    else:
                         initmin = min_list( initmin, rsi )
                         initmax = max_list( initmax, rsi )
                    
                    logperw.write( '%f\n' % rsi[1] )
                    
               print '='*80
               print 'Testing overbough rsi %f and oversold rsi %f ...' % (ob,os)
               print 'Current max return in average (ob=%f os=%f) = %.2f'%(mob,mos,maxret)
               avel = list_div( init, samples  )
               print 'AVE ',avel
               print 'MIN ',initmin
               print 'MAX ',initmax
               print 'MAX Params [round_trips,retrn, win_percent, drawdown, sharpe, normalized_return] = ',max_params
               if avel[1] > maxret and avel[0]>0:
                    maxret = avel[1]
                    mob,mos = ob,os
                    max_params = avel
               if avel[1]*sqrt(avel[0]) > maxrettrips and avel[0]>0:
                    maxrettrips = avel[1]*sqrt(avel[0])
                    mob_rt,mos_rt = ob,os
                    max_params_rt = avel
               if avel[4] > maxsharpe and avel[0]>0:
                    maxsharpe = avel[4]
                    mob_sr,mos_sr = ob,os
                    max_params_sr = avel
               if avel[5] > maxnret and avel[0]>0:
                    maxnret = avel[5]
                    mob_nr,mos_nr = ob,os
                    max_params_nr = avel
               if avel[3]>0 and avel[0]/avel[3] > maxtripdown and avel[0]>0:
                    maxtripdown = avel[0]/avel[3]
                    mob_td,mos_td = ob,os
                    max_params_td = avel
               if avel[3]>0 and sqrt(avel[0])*avel[1]/avel[3] > maxrtd and avel[0]>0:
                    maxrtd = sqrt(avel[0])*avel[1]/avel[3]
                    mob_rtd,mos_rtd = ob,os
                    max_params_rtd = avel



     print '*'*80
     print 'PARAMETER SEARCH:'
     print 'Max Ave Annualized Return = ',maxret
     print 'OverBought RSI Limit =',mob
     print 'OverSold RSI limit =',mos
     print 'Params [round_trips,retrn, win_percent, drawdown, sharpe, normalized_return] = ',max_params

     print
     print 'PARAMETER SEARCH:'
     print 'Max (Ave Annualized Return * Sqrt(Ave Number of RoundTrips))  = ',maxrettrips
     print 'OverBought RSI Limit =',mob_rt
     print 'OverSold RSI limit =',mos_rt
     print 'Params [round_trips,retrn, win_percent, drawdown, sharpe, normalized_return] = ',max_params_rt

     print
     print 'PARAMETER SEARCH:'
     print 'Max Ave Sharpe Ratio  = ',maxsharpe
     print 'OverBought RSI Limit =',mob_sr
     print 'OverSold RSI limit =',mos_sr
     print 'Params [round_trips,retrn, win_percent, drawdown, sharpe, normalized_return] = ',max_params_sr

     print
     print 'PARAMETER SEARCH:'
     print 'Max Ave Normalized Return  = ',maxnret
     print 'OverBought RSI Limit =',mob_nr
     print 'OverSold RSI limit =',mos_nr
     print 'Params [round_trips,retrn, win_percent, drawdown, sharpe, normalized_return] = ',max_params_nr

     print
     print 'PARAMETER SEARCH:'
     print 'Max (Ave Round Trips / Ave Drawdown )   = ',maxtripdown
     print 'OverBought RSI Limit =',mob_td
     print 'OverSold RSI limit =',mos_td
     print 'Params [round_trips,retrn, win_percent, drawdown, sharpe, normalized_return] = ',max_params_td

     print
     print 'PARAMETER SEARCH:'
     print 'Max (Sqrt(Ave Round Trips) * Ave Return / Ave Drawdown )   = ',maxrtd
     print 'OverBought RSI Limit =',mob_rtd
     print 'OverSold RSI limit =',mos_rtd
     print 'Params [round_trips,retrn, win_percent, drawdown, sharpe, normalized_return] = ',max_params_rtd


