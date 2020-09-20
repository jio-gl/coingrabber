'''
Created on Mar 16, 2017

@author: joign
'''

from cdf import phi as cdf
from cdf import normpdf as pdf
class Norm: pass 
norm = Norm()
N = norm.cdf = cdf
n = norm.pdf = pdf

#from scipy.stats import norm
#N = norm.cdf

from math import sqrt

class KellyCriteria(object):
    '''
    classdocs
    '''


    def __init__(self, meanRet, sigmaRet, leverage):
        '''
        Constructor
        '''
        self.mean,self.sigma = meanRet,sigmaRet
        self.winAmount = self.mean
        
        margin = 1.0 / leverage
        self.chanceLoosingAll = N( (-margin-self.mean)/self.sigma ) 
        print 'Chance of Liquidation = %.4f percent ' % (self.chanceLoosingAll*100.0)
        
    def kellyBetFraction(self):
        return (self.mean*(1.0-self.chanceLoosingAll) - self.chanceLoosingAll ) / self.winAmount
    
    
if __name__ == '__main__':
    
    dailyRet = 0.4843/100 #0.5255/100 #0.4008/100 #0.9211/100 #1.0564/100 #0.4787/100 #0.2067 / 100 #0.7883/100 #2.3137 / 100 #0.7009 / 100.0
    dailyDev = 2.9258/100 #8.16/100 #9.92/100 #15.13/100 #13.32/100 #7.22/100 #7.17/100 #10.71/100 #21.47 / 100 #2.3428 / 100.0
    days = 30
    leverage = 2.5
    
    
    
    kelly = KellyCriteria( meanRet=dailyRet*days, sigmaRet=dailyDev*sqrt(days), leverage=leverage )
    
    kellyBetFraction = kelly.kellyBetFraction()
    print 'kellyBetFractionYouMustBet = ', kellyBetFraction