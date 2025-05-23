from optimization import OptimalPortfolio
from coins import CoinDB
from portfolio import PortfolioAnalyzer
from dateconfig import DateRange
from datetime import datetime,timedelta
from math import sqrt,exp


import sys
import io


if __name__ == '__main__':

    ### # if False Minimize Risk.
    MAXIMIZE_SHARPE = True # if False minimize Risk.
    # or desired return
    TARGET_RETURN = None #0.02 #0.021
    ###
    
    
    print 'INFO: CONFIGURED TO MINIMIZE RISK, NOT MAXIMIZE SHARPE RATIO.'
    COMPLETE_BACKTESTING = True
    CURRENT_PORTFOLIO = True
    #r_min = 0.0125
    #periodDaysTest = 30
    leverage = 2.5
    # TODO: test trainingDaysTest on, 32,64,128,256,512,1024,2048
    #trainingDaysTest = None #240
    log = open('log.txt','w')
    logp = open('logpfolio.txt','w')
    initialMonth = 5
    numberOfMonths = 1
    movingWindowTesting = 1
    startDateObj = CURRENT_PORTFOLIO and (datetime.today()-timedelta(days=1)) or datetime(year=2017,month=initialMonth,day=3)
    bestParamsDays = None
    bestAveGlobalSharpe = 0.0
    for periodDaysTest in [1]:#range(75,76,1):#range(1,181):#[60]:#[2**i for i in range(0,7)]:
        #if periodDaysTest > 60:
        #    periodDaysTest = 60
        for empiricTraining in [True]:
            for trainingDaysTest in [7]:#range(240,241,1):#range(2,1024):#[16]:#[2**i for i in range(1,11)]:
                totalReturn = 1.0
                aveGlobalSharpe = 0.0
                count = 0
                daysDeltaPerTest = (COMPLETE_BACKTESTING and movingWindowTesting or periodDaysTest)
                numberOfTests = 30*numberOfMonths/daysDeltaPerTest
                totalDaysPerTestSet = numberOfTests * periodDaysTest
                sumReturns = 0.0
                for i in range(numberOfTests):#periodDaysTest):
            
                    endDateObj = startDateObj + timedelta(days= i*daysDeltaPerTest )
                    
                    DateRange.endYear = endDateObj.year
                    DateRange.endMonth = endDateObj.month
                    DateRange.endDay = endDateObj.day
                    endDate = '%d/%d/%d' % (endDateObj.month,endDateObj.day,endDateObj.year)
                    opt = OptimalPortfolio(CoinDB.coins,end=endDate,maxDays=trainingDaysTest)
                    if opt.bad:
                        continue
                    pfolio = PortfolioAnalyzer()
                    pfolio.loadAndComputeStatistics()
                    maxSharpeRatio,bestRet,bestSigma,bestPfolio = -100000.0, None, None, None
                    minStdDev = 1000000000.0
                    return_range = not TARGET_RETURN and range(1,1000) or [TARGET_RETURN*1000]
                    save_stdout = sys.stdout
                    sys.stdout = io.BytesIO()
                    ret = None
                    for mil in return_range:#1000):
                        r_min = 0.001 * mil
                        p = opt.findOptimalPortfolio(minReturn=r_min)
                        if not p:
                            break
                        else:
                            if empiricTraining:
                                pfolioSigma = pfolio.portfolioStandardDev(p)
                                ret,sigma,maxDrawdown,days = pfolio.portfolioAnalysis(p,r_min,pfolioSigma,maxDaysTesting=trainingDaysTest,testing=False)
                                #ret = exp(ret*days)
                                #sigma = sigma*sqrt(days)
                            else:
                                ret,sigma = pfolio.portfolioReturn(p), pfolio.portfolioStandardDev(p)                            

                            dumpFolio = sorted(list(p.iteritems()),key=lambda x:-x[1])
                            dumpFolio = [ (c,'%.6f'%w) for c,w in dumpFolio ]
                            logp.write('%s\n' % str(dumpFolio) )
                            logp.write('Portofolio Metrics MinRet=%.4f Ret=%.4f Risk=%.4f DailySharpe=%.4f\n\n' % (r_min,ret,sigma,ret/sigma))
                            log.flush()
                            if MAXIMIZE_SHARPE and ret/sigma > maxSharpeRatio and len(p) > 2 :
                                maxSharpeRatio,bestRet,bestSigma,bestPfolio = ret/sigma,ret,sigma,p
                            # new best portfolio with enoughs different coin, more than 2.
                            if not MAXIMIZE_SHARPE and sigma <= minStdDev:
                                maxSharpeRatio,bestRet,bestSigma,bestPfolio = ret/sigma,ret,sigma,p
                                minStdDev = sigma
                    sys.stdout = save_stdout       
                    if ret:
                        dumpFolio = sorted(list(bestPfolio.iteritems()),key=lambda x:-x[1])
                        dumpFolio = [ (c,'%.6f'%w) for c,w in dumpFolio ]
                        logp.write('PortfolioStartDate=%s %s\n\n' % (str(endDateObj).split()[0],str(dumpFolio) ) )
                        if CURRENT_PORTFOLIO:
                            count += 1
                            break

                        if MAXIMIZE_SHARPE:
                            print 'Optimal Sharpe portfolio ret/sigma/sharpe = %.4f/%.4f/%.4f' % (bestRet,bestSigma,bestRet/bestSigma)
                            print 'Optimal Sharpe pfolio = %s' % (str(bestPfolio))
                        else:
                            print 'Optimal Min Risk portfolio ret/sigma/sharpe = %.4f/%.4f/%.4f' % (bestRet,bestSigma,bestRet/bestSigma)
                            print 'Optimal Min Risk pfolio = %s' % (str(bestPfolio))
                        endDateObjTest = startDateObj + timedelta(days=(COMPLETE_BACKTESTING and (i*movingWindowTesting+periodDaysTest) or ((i+1)*periodDaysTest)))        
                        DateRange.endYear = endDateObjTest.year
                        DateRange.endMonth = endDateObjTest.month
                        DateRange.endDay = endDateObjTest.day
                        pfolio = PortfolioAnalyzer()
                        pfolio.loadAndComputeStatistics()
                        pfolioLen = len(bestPfolio)
                        ret,sigma,maxDrawdown,days = pfolio.portfolioAnalysis(bestPfolio,bestRet,bestSigma,maxDaysTesting=periodDaysTest,testing=True)
                        #ret = exp(ret*days)
                        #sigma = sigma*sqrt(days)
                        takerFee = 0.0025
                        retCost = ((ret+1.0) * (1.0 - takerFee*2)) - 1.0
                        sumReturns += retCost
                        totalReturn *= retCost + 1.0
                        #log.write('-----------------------------------------------------------\n')
                        #log.write('Portfolio = %s\n' % str(bestPfolio))
                        try:
                            count += 1
                            if MAXIMIZE_SHARPE:
                                aveGlobalSharpe += retCost / sigma
                            else:
                                aveGlobalSharpe += sigma
                            log.write('Tdays=%d EmpiricTrain=%s start%s end%s EstRet=%.2f EstSigma=%.2f EstSharpe=%.2f Ret=%.2f Sigma=%.2f Sharpe=%.2f MaxDD=%.2f AccumRet=%.2f AcumRetLeve=%.2f\n' % 
                                (trainingDaysTest, empiricTraining,str(endDateObj).split()[0],str(endDateObjTest).split()[0],
                                 bestRet*periodDaysTest*100,bestSigma*sqrt(periodDaysTest)*100,bestRet*periodDaysTest/(bestSigma*sqrt(periodDaysTest)),
                                 retCost*100,sigma*100,retCost/sigma,
                                 maxDrawdown*100.0,
                                 (totalReturn-1.0)*100, (totalReturn-1.0)*100 * leverage) )
                        except:
                            pass 
                    else:
                        log.write('OutOfSampleTestingOneMonth No Portfolio Found!\n')        
                    log.flush()
                    logp.flush()
                aveGlobalSharpe /= count
                if MAXIMIZE_SHARPE and aveGlobalSharpe > bestAveGlobalSharpe:
                    bestAveGlobalSharpe = aveGlobalSharpe
                    bestParamsDays = periodDaysTest,trainingDaysTest
                if not MAXIMIZE_SHARPE and aveGlobalSharpe < bestAveGlobalSharpe:
                    bestAveGlobalSharpe = aveGlobalSharpe
                    bestParamsDays = periodDaysTest,trainingDaysTest
                returnPerDay = (COMPLETE_BACKTESTING and (sumReturns) or (totalReturn-1))*100/totalDaysPerTestSet
                log.write('Total Final return (period of %d days, training days %d) discounting Costs = %.4f percent  AverageSharpe = %.4f  RetPerDay = %.4f percent \n' 
                          % (periodDaysTest,trainingDaysTest,(totalReturn-1)*100.0,aveGlobalSharpe,returnPerDay))
                
                log.write('------------------------------------------------\n' )
                logp.write('------------------------------------------------\n' )
                log.flush()
                logp.flush()
    #if MAXIMIZE_SHARPE:
    #    log.write('BEST GLOBAL AVERAGE MAX SHARPE = %.4f  PeriodDaysTest = %d  TrainingDaysTest = %d  \n' % (bestAveGlobalSharpe,bestParamsDays[0],bestParamsDays[1]) )
    #else:
    #    log.write('BEST GLOBAL AVERAGE MIN RISK = %.4f  PeriodDaysTest = %d  TrainingDaysTest = %d  \n' % (bestAveGlobalSharpe,bestParamsDays[0],bestParamsDays[1]) )
    print '*'*80
    print 'RESULTS ' + (MAXIMIZE_SHARPE and 'MAXIMIZING SHARPE RATIO' or 'MINIMIZING RISK')
    
    print '*'*80
    print open('logpfolio.txt').read()   
    print '*'*80
    print 'END OF RESULTS ' + (MAXIMIZE_SHARPE and 'MAXIMIZING SHARPE RATIO' or 'MINIMIZING RISK')
    print '*'*80
