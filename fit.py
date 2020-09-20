

from sklearn import linear_model
from sklearn import svm
from sklearn import neural_network
import numpy as np


from sklearn.linear_model import *
from sklearn.cross_validation import KFold

def predFunc( X, Y, generator=None):
    #X = [[0., 0.], [1., 1.], [2., 2.], [3., 3.]]
    #Y = [0., 1., 2., 3.]
    if not generator:
        reg = linear_model.ARDRegression()  #BayesianRidge() #LogisticRegression()#LinearRegression() #BayesianRidge()
    else:
        reg = generator()
    
    reg.fit(X, Y)
    return reg.predict
    #print reg.predict ([[1, 0.]])
    
def predFuncSVM(X, Y):
    #X = [[0., 0.], [1., 1.], [2., 2.], [3., 3.]]
    #Y = [0., 1., 2., 3.]
    reg = svm.SVC()  #BayesianRidge() #LogisticRegression()#LinearRegression() #BayesianRidge()
    reg.fit(X, Y)
    return reg.predict

def predFuncDeep(X, Y):
    #X = [[0., 0.], [1., 1.], [2., 2.], [3., 3.]]
    #Y = [0., 1., 2., 3.]
    reg = neural_network.BernoulliRBM(n_components=2)
    reg.fit(X, Y)
    return reg.predict

def predFuncLogisticCV(X,Y):
    fold = KFold(len(Y), n_folds=5, shuffle=True, random_state=777)
    searchCV = LogisticRegressionCV(
        Cs=list(np.power(10.0, np.arange(-10, 10)))
        ,penalty='l2'
        ,scoring='roc_auc'
        ,cv=fold
        ,max_iter=10000
        ,fit_intercept=True
        ,solver='newton-cg'
        ,tol=10
    )
    searchCV.fit(X, Y)
    return searchCV.predict

    #print ('Max auc_roc:', searchCV.scores_[1].max())
