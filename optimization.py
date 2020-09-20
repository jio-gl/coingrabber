import numpy

from cvxopt import matrix,solvers

import stocks

# https://wellecks.wordpress.com/2014/03/23/portfolio-optimization-with-python/


#symbols = ['GOOG', 'AIMC', 'GS', 'BH', 'TM', 
#           'F', 'HLS', 'DIS', 'LUV', 'MSFT']

def ccy2ticker(ccy):
    return ccy.upper() + '=X'#'%3DX'

class OptimalPortfolio(object):

    symbols = [
    #        'bitcoin',  'dash',              'factom',       'litecoin',  'nem',   'stellar',]
    #        'bitshares',     'dogecoin',          'gamecredits',  'monero',    'ripple',            
    #        'bytecoin-bcn',  'nem',       'shadowcoin',          
    #        'counterparty',  'ethereum',          'lisk',         'nem',   'ethereum',  
             'SPY', ccy2ticker('EUR'), ccy2ticker('JPY')
            ]

    def __init__(self, symbols,start=None,end=None,maxDays=None):

        if symbols:
            self.symbols = symbols

        self.n = len(symbols)
        print symbols,self.n

        self.start = start
        #start = '2/26/2014'
        self.end = end
        #end = '2/26/2017'
        self.maxDays = maxDays

        # average yearly return for each stock
        r_avg = map(lambda s: stocks.avg_return(s, start, end, 'd', maxDays), symbols)
        print r_avg
        # covariance of asset returns
        try:
            sigma = numpy.array(stocks.cov_matrix(symbols, start, end, 'd',maxDays))
            self.bad = False
        except:
            self.bad = True
            return 
        self.r_avg = matrix(r_avg)
        sigma = matrix(sigma)
        # that was easy
        self.P = sigma
        self.q = matrix(numpy.zeros((self.n, 1)))


    def findOptimalPortfolio(self, minReturn):
        
        print 'Minimum Return Desired, r_min = %.2f percent' % (minReturn*100.)
        r_min = minReturn

        print 'Searching optimal portfolio ...'
        
        # inequality constraints Gx <= h
        # captures the constraints (avg_ret'x >= r_min) and (x >= 0)
        G = matrix(numpy.concatenate((
                     -numpy.transpose(numpy.array(self.r_avg)), 
                     -numpy.identity(self.n)), 0))
        h = matrix(numpy.concatenate((
                     -numpy.ones((1,1))*r_min, 
                      numpy.zeros((self.n,1))), 0))
        
        # equality constraint Ax = b; captures the constraint sum(x) == 1
        A = matrix(1.0, (1,self.n))
        b = matrix(1.0)
        
        #Optimal solution found.
        #[0.0, 0.0, 0.0, 0.7, 0.16, 0.0, 0.0, 0.0, 0.0, 0.13]
        try:
            sol = solvers.qp(self.P, self.q, G, h, A, b)
        except ValueError:
            print 'Warning: couldnt find optimal portfolio, probably minimum return is to big!'
            return None
        
        print
        pfolio = {}
        #print 'x =',sol['x']
        total = 0.0
        for s,w in zip(self.symbols,list(sol['x'])):
            if w < 0.0001 or round(w*10000.0,1) == 0.0:
                continue
            total += w
            pfolio[s] = w
            #print s,' = ','%.2f'%(w*100.0),' percent'
        for k in pfolio:
            pfolio[k] = pfolio[k]/total
            print k,' = ','%.2f'%(pfolio[k]*100.0),' percent'
        return pfolio


if __name__ == '__main__':
    
    opt = OptimalPortfolio(OptimalPortfolio.symbols)
    r_min = 0.01
    p = opt.findOptimalPortfolio(minReturn=r_min)
    if not p:
        print 'ERROR: couldnt find optimal portfolio por Minimal Return %f percent !' % (r_min*100.0)
    else:
        print p
