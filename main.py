
from optimization import OptimalPortfolio
from coins import CoinDB
from portfolio import PortfolioAnalyzer
from dateconfig import DateRange
from datetime import datetime,timedelta
from math import sqrt,exp

if __name__ == '__main__':

    COMPLETE_BACKTESTING = False
    #r_min = 0.0125
    #periodDaysTest = 30
    leverage = 2.5
    # TODO: test trainingDaysTest on, 32,64,128,256,512,1024,2048
    #trainingDaysTest = None #240
    log = open('log.txt','w')
    logp = open('logpfolio.txt','w')
    initialMonth = 1
    numberOfMonths = 14
    movingWindowTesting = 15
    startDateObj = datetime(year=2016,month=initialMonth,day=1)
    bestParamsDays = None
    bestAveGlobalSharpe = 0.0
    for periodDaysTest in [60]:#range(60,121,10):#range(1,181):#[60]:#[2**i for i in range(0,7)]:
        #if periodDaysTest > 60:
        #    periodDaysTest = 60
        for empiricTraining in [True]:
            for trainingDaysTest in [215]:#range(200,221,5):#range(2,1024):#[16]:#[2**i for i in range(1,11)]:
                totalReturn = 1.0
                aveGlobalSharpe = 0.0
                count = 0
                for i in range(30*numberOfMonths/(COMPLETE_BACKTESTING and movingWindowTesting or periodDaysTest)):#periodDaysTest):
            
                    endDateObj = startDateObj + timedelta(days= i*(COMPLETE_BACKTESTING and movingWindowTesting or periodDaysTest) )
                    
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
                    for mil in range(1,1000):
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
                            #log.write('TheoreticalSearchingBestSharpe %.4f %.4f %.4f %.4f\n' % (r_min,ret,sigma,ret/sigma))
                            log.flush()
                            if ret/sigma > maxSharpeRatio and len(p) > 2 :
                                maxSharpeRatio,bestRet,bestSigma,bestPfolio = ret/sigma,ret,sigma,p
                            # new best portfolio with enoughs different coin, more than 2.
                            
                    if ret:
                        print 'Optimal Sharpe portfolio ret/sigma/sharpe = %.4f/%.4f/%.4f' % (bestRet,bestSigma,bestRet/bestSigma)
                        print 'Optimal Sharpe pfolio = %s' % (str(bestPfolio))
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
                        totalReturn *= retCost + 1.0
                        #log.write('-----------------------------------------------------------\n')
                        #log.write('Portfolio = %s\n' % str(bestPfolio))
                        try:
                            aveGlobalSharpe += retCost / sigma
                            count += 1
                            log.write('Tdays=%d EmpiricTrain=%s start%s end%s EstRet=%.2f EstSigma=%.2f EstSharpe=%.2f Ret=%.2f Sigma=%.2f Sharpe=%.2f MaxDD=%.2f AccumRet=%.2f AcumRetLeve=%.2f\n' % 
                                (trainingDaysTest, empiricTraining,str(endDateObj).split()[0],str(endDateObjTest).split()[0],
                                 bestRet*periodDaysTest*100,bestSigma*sqrt(periodDaysTest)*100,bestRet*periodDaysTest/(bestSigma*sqrt(periodDaysTest)),
                                 retCost*100,sigma*100,retCost/sigma,
                                 maxDrawdown*100.0,
                                 (totalReturn-1.0)*100, (totalReturn-1.0)*100 * leverage) )
                        except:
                            pass 
                        dumpFolio = sorted(list(bestPfolio.iteritems()),key=lambda x:-x[1])
                        dumpFolio = [ (c,'%.3f'%w) for c,w in dumpFolio ]
                        logp.write('%s\n\n' % str(dumpFolio) )
                    else:
                        log.write('OutOfSampleTestingOneMonth No Portfolio Found!\n')        
                    log.flush()
                    logp.flush()
                aveGlobalSharpe /= count
                if aveGlobalSharpe > bestAveGlobalSharpe:
                    bestAveGlobalSharpe = aveGlobalSharpe
                    bestParamsDays = periodDaysTest,trainingDaysTest
                log.write('Total Final return (period of %d days, training days %d) discounting Costs = %.4f percent  AverageSharpe = %.4f \n' % (periodDaysTest,trainingDaysTest,(totalReturn-1)*100.0,aveGlobalSharpe))
                
                log.write('------------------------------------------------\n' )
                logp.write('------------------------------------------------\n' )
                log.flush()
                logp.flush()
    log.write('BEST GLOBAL AVERAGE SHARPE = %.4f  PeriodDaysTest = %d  TrainingDaysTest = %d  \n' % (bestAveGlobalSharpe,bestParamsDays[0],bestParamsDays[1]) )
