import numpy as np
import pandas as pd
import math as m
import matplotlib.pyplot as plt
import cvxopt
import os
from scipy.stats import multivariate_normal
from sklearn.utils import resample
from cvxopt import matrix
from cvxopt import solvers

# cd D:\\OneDrive\\文档\\cityu\\MachineLearning\\MLAssignment\\

NAME_MAP = {'LS':'Least Square Regression',
            'RLS':'Regularized LS',
            'LASSO':'L1-Regularized LS',
            'RR':'Robust Regression',
            'BR':'Bayesian Regression'}

# define the polynomial function
def poly_function(x,order = 1):
    return np.array([m.pow(x,i) for i in range(0,order+1) ])

# load file from txt
def load_file(filename = 'polydata_data_polyx.txt'):
    return np.genfromtxt(filename,dtype='double')

def load_dataset():
    polyx = load_file(filename = os.path.join('PA-1','PA-1-data-text','polydata_data_polyx.txt'))
    polyy = load_file(filename = os.path.join('PA-1','PA-1-data-text','polydata_data_polyy.txt'))
    sampx = load_file(filename = os.path.join('PA-1','PA-1-data-text','polydata_data_sampx.txt'))
    sampy = load_file(filename = os.path.join('PA-1','PA-1-data-text','polydata_data_sampy.txt'))

    return polyx,polyy,sampx,sampy

# transpose 
def T(x):
    if(len(x.shape)>1):
        return np.transpose(x)
    else:
        return x.reshape(1,x.shape[0])

# x is a set of column vectors, get the transpose form of Φ matrix
def PHIx(x,order=5,function='poly'):
    if(function == 'poly'):
        mat = [poly_function(item,order) for item in x ]
        #return np.transpose(np.array(mat))
        return T(np.array(mat))

# return objective function according to different methods.
def obj_function(y,PHI,theta,Lambda=0,method='LS'):
    if method == 'LS':
        return np.linalg.norm(y-np.dot(T(PHI),theta),ord=2)
    if method == 'RLS':
        return np.linalg.norm(y-np.dot(T(PHI),theta),ord=2) + Lambda * np.linalg.norm(theta,ord=2)
    if method == 'LASSO':
        return np.linalg.norm(y-np.dot(T(PHI),theta),ord=2) + Lambda * np.linalg.norm(theta,ord=1)
    if method == 'RR':
        return np.linalg.norm(y-np.dot(T(PHI),theta),ord=1)

# Generate prediction according to the theta
def predict(x,theta,function='poly'):
    if(function=='poly'):
        PHIX=PHIx(x,order=theta.shape[0]-1,function=function)
        predections = np.dot(T(PHIX),theta)
        return predections

# parameter estimate , all input vectors are column vectors
def para_estimate(y,PHI,Lambda=0.1,method='LS'):
    if method == 'LS':
        return np.dot(np.dot(np.linalg.inv(np.dot(PHI,T(PHI))),PHI),y)
    if method == 'RLS':
        return np.dot(np.dot(np.linalg.inv(np.dot(PHI,T(PHI))+Lambda*np.eye(PHI.shape[0])),PHI),y)
    if method == 'LASSO':
        PHIPHIT = np.dot(PHI,T(PHI))
        PHIy = np.dot(PHI,y)

        H = np.vstack((np.hstack((PHIPHIT,-1*PHIPHIT)),
                       np.hstack((-1*PHIPHIT,PHIPHIT))))
        
        f = np.hstack((PHIy,-1*PHIy))
        f = Lambda * np.ones(f.shape) - f

        P = matrix(H)
        q = matrix(f)
        G = matrix(np.eye(len(f))*-1)
        h = matrix(np.zeros(len(f)))
        
        sol = solvers.qp(P,q,G,h)
        x = sol['x']
        theta = x[:int(len(x)/2)]- x[int(len(x)/2):]

        return np.array(theta)
    if method == 'RR':

        A = np.vstack((np.hstack((-1*T(PHI),-1*np.eye(T(PHI).shape[0]))),
                       np.hstack((T(PHI),-1*np.eye(T(PHI).shape[0])))))
        b = np.hstack((-1*y,
                       y))

        f = np.hstack((np.zeros(T(PHI).shape[1]),
                       np.ones(T(PHI).shape[0])))

        c = matrix(f)
        A = matrix(A)
        b = matrix(b)

        sol = solvers.lp(c,A,b)

        theta = np.array(sol['x'][:T(PHI).shape[1]])
        return theta

# define mean square error
def mse(y,prediction):

    if(len(y)!=len(prediction)):
        return m.inf

    ry =  y.reshape(len(y),1)
    rp = prediction.reshape(len(prediction),1)
    e = ry - rp
    return (np.dot(T(e),e)/len(e))[0,0]

# define posterior of Bayesian Regression
def posterior_BR(x,y,PHI,alpha=0.1,sigma=0.1):
    SIGMA_theta = np.linalg.inv(1/alpha*np.eye(PHI.shape[0])+1/(sigma*sigma)*np.dot(PHI,T(PHI)))
    miu_theta = 1/(sigma*sigma)*np.dot(np.dot(SIGMA_theta,PHI),y) 
    #posterior = multivariate_normal(x,miu_theta,SIGMA_theta)
    return miu_theta,SIGMA_theta

# define predictive model of Bayesan Regression
def predict_BR(x,miu_theta,SIGMA_theta,function='poly'):

    if(function=='poly'):
        PHIX = PHIx(x,order=miu_theta.shape[0]-1,function=function)
        miu_star = np.dot(T(PHIX),miu_theta)
        sigma_theta_sqr = np.dot(np.dot(T(PHIX),SIGMA_theta),PHIX)
        return miu_star,sigma_theta_sqr

# Generate Plots 
def plot_f_s(x,y,pred,sampx,sampy,label):
    plt.plot(x, y, label='True Function',c='k')
    plt.legend()
    plt.plot(x, pred, label=label,c='b')
    plt.legend()
    plt.plot(sampx, sampy,'ro',label='data')
    plt.legend()
    plt.savefig(os.path.join('PA-1','plots',label+'.jpg'))
    plt.show()
    return 

def plot_f_s_std(x,y,pred,sampx,sampy,deviation,label):
    plt.plot(x, y, label='True Function',c='k')
    plt.legend()
    plt.plot(x, pred, label=label,c='b')  
    plt.legend()  
    plt.plot(sampx, sampy,'ro',label='data')
    plt.legend()
    plt.errorbar(x, pred,yerr = deviation)
    plt.savefig(os.path.join('PA-1','plots',label+'.jpg'))
    plt.show()    
    return

# model selection to search the best parameter 
def model_selection(polyx,polyy,sampx,sampy,param_dict,estimator='RLS'):
    para_err_map={}
    best_para={}

    if (estimator == 'RLS' or estimator == 'LASSO'):
        Lambdas = param_dict['Lambda']
        functions = param_dict['function']
        orders = param_dict['order']

        for order in orders:
            for function in functions:
                PHIX = PHIx(sampx,order=order,function=function)
                for Lambda in Lambdas:
                    theta = para_estimate(sampy,PHIX,Lambda=Lambda,method=estimator)
                    prediction = predict(polyx,theta,function=function)
                    err = mse(prediction,polyy)
                    paraset = {'function':function,'order':order,'Lambda':Lambda}
                    para_err_map[str(paraset)] = err
    
    if (estimator == 'BR'):
        alphas = param_dict['alpha']
        sigmas = param_dict['sigma']
        functions = param_dict['function']
        orders = param_dict['order']

        for order in orders:
            for function in functions:
                PHIX = PHIx(sampx,order=order,function=function)
                for alpha in alphas:
                    for sigma in sigmas:
                        theta,SIGMA_theta = posterior_BR(sampx,sampy,PHIX,alpha=alpha,sigma=sigma)
                        prediction,cov = predict_BR(polyx,theta,SIGMA_theta,function=function)
                        err = mse(prediction,polyy)
                        paraset = {'function':function,'order':order,'alpha':alpha,'sigma':sigma}
                        para_err_map[str(paraset)] = err        
    
    best = min(para_err_map, key=para_err_map.get)
    best_para = eval(best)
    return para_err_map,best_para

# Plot learning curve with different data size
def learning_curve(polyx,polyy,sampx,sampy,paradict={},subset=[1],repeat=1,method='LS',plot_title='Learning Curve LS'):
    err = []
    for size in subset:
        nsamp = int(size*len(sampy))
        err_perround = 0
        for i in range(0,repeat):
            resampx, resampy = resample(sampx, sampy,n_samples=nsamp,replace=False, random_state=i*17)
            round_err = experiment(polyx,polyy,resampx,resampy,paradict,method=method,plot_title=NAME_MAP[method]+' subset '+str(round(size,1)),show_plot=not i)
            # if parameter dictionnary is not empty
            #if method == 'BR':
                #theta,SIGMA_theta, prediction,cov = experiment(polyx,polyy,resampx,resampy,paradict,method=method,plot_title=method+' '+str(size))
            #else :
                #theta, prediction = experiment(polyx,polyy,resampx,resampy,paradict,method=method,plot_title=method+' '+str(size))
            err_perround += round_err
                
        err.append(err_perround/repeat)

    plt.plot(subset, err, label=plot_title,c='b')
    plt.legend()
    plt.savefig(os.path.join('PA-1','plots',plot_title+'.jpg'))
    plt.show()

    return err

# Define experiment with certain method and data
def experiment(polyx,polyy,sampx,sampy,paradict={},method='LS',plot_title='Least-squares Regression',show_plot=True):
    
    prediction= np.array([])
    theta = np.array([])

    # parameter is not empty
    if paradict:

        try:
            if (method == 'BR'):
                PHIX = PHIx(sampx,order=paradict['order'],function=paradict['function'])
                theta,SIGMA_theta = posterior_BR(sampx,sampy,PHIX,alpha=paradict['alpha'],sigma=paradict['sigma'])
                prediction,cov = predict_BR(polyx,theta,SIGMA_theta,function=paradict['function'])
                if(show_plot==True):
                    plot_f_s_std(polyx,polyy,prediction,sampx,sampy,np.sqrt(np.sqrt(cov.diagonal())),label=plot_title)
                #return theta,SIGMA_theta, prediction,cov
                return mse(prediction,polyy)


            else:
                PHIX = PHIx(sampx,order=paradict['order'],function=paradict['function'])
                theta = para_estimate(sampy,PHIX,Lambda=paradict['Lambda'],method=method)
                prediction = predict(polyx,theta,function=paradict['function'])
                if(show_plot==True):
                    plot_f_s(polyx,polyy,prediction,sampx,sampy,label=plot_title) 
                #return theta, prediction
                return mse(prediction,polyy)
            
        except Exception as e:
            print ('missing parameter: ')
            print (e)
            return 

    # parameter is empty
    if (method == 'BR'):
            PHIX = PHIx(sampx)
            theta,SIGMA_theta = posterior_BR(sampx,sampy,PHIX)
            prediction,cov = predict_BR(polyx,theta,SIGMA_theta)
            if(show_plot==True):
                plot_f_s_std(polyx,polyy,prediction,sampx,sampy,np.sqrt(np.sqrt(cov.diagonal())),label=plot_title)
            #return theta,SIGMA_theta, prediction,cov
            return mse(prediction,polyy)

    PHIX = PHIx(sampx)
    theta = para_estimate(sampy,PHIX,method=method)
    prediction = predict(polyx,theta)
    if(show_plot==True):
        plot_f_s(polyx,polyy,prediction,sampx,sampy,label=plot_title)

    #return theta, prediction
    return mse(prediction,polyy)

# Set experiments with outliers
def outliers_experiments(polyx,polyy,sampx,sampy,olx,oly,paradict={},method='LS',plot_title='Least-squares Regression'):

    addedx = np.hstack((sampx,olx))
    addedy = np.hstack((sampy,oly))

    return experiment(polyx,polyy,addedx,addedy,paradict=paradict,method=method,plot_title=plot_title)

def mseMap_toCSV(msedict,fname='mse.csv'):
    keys = list(msedict.keys())
    values = list(msedict.values())
    mseDf = pd.DataFrame({'mse':values},index=keys)
    mseDf.sort(columns='mse',inplace=True)
    mseDf.to_csv(os.path.join('PA-1','plots',fname))
    return

def main():

    polyx,polyy,sampx,sampy = load_dataset()
    
    # methods without hyper parameters
    mse_LS = experiment(polyx,polyy,sampx,sampy,method='LS',plot_title=NAME_MAP['LS'])
    mseMap_toCSV({'nohparam':mse_LS},'mse_LS.csv')

    mse_RR = experiment(polyx,polyy,sampx,sampy,method='RR',plot_title=NAME_MAP['RR'])
    mseMap_toCSV({'nohparam':mse_RR},'mse_RR.csv')


    # methods with hyper parameters
    para_RLS = {'Lambda':[0.1,0.25,0.5,1,2,5],'function':['poly'],'order':[5]}
    para_err_RLS,opt_para_RLS = model_selection(polyx,polyy,sampx,sampy,para_RLS,estimator='RLS')
    mseMap_toCSV(para_err_RLS,'mse_RLS.csv')
    mse_RLS = experiment(polyx,polyy,sampx,sampy,paradict=opt_para_RLS,method='RLS',plot_title=NAME_MAP['RLS'])

    para_LASSO = {'Lambda':[0.1,0.25,0.5,1,2,5],'function':['poly'],'order':[5]}
    para_err_LASSO,opt_para_LASSO = model_selection(polyx,polyy,sampx,sampy,para_LASSO,estimator='LASSO')
    mseMap_toCSV(para_err_LASSO,'mse_LASSO.csv')
    mse_LASSO = experiment(polyx,polyy,sampx,sampy,paradict=opt_para_LASSO,method='LASSO',plot_title=NAME_MAP['LASSO'])

    para_BR = {'alpha':[0.1,0.5,1,5],'sigma':[0.1,0.5,1,5],'function':['poly'],'order':[5]}
    para_err_BR,opt_para_BR = model_selection(polyx,polyy,sampx,sampy,para_BR,estimator='BR')
    mseMap_toCSV(para_err_BR,'mse_BR.csv')
    mse_BR = experiment(polyx,polyy,sampx,sampy,paradict=opt_para_BR,method='BR',plot_title=NAME_MAP['BR'])

    # learning curve experiments
    subset = np.linspace(0.2,1,5)
    err_LS = learning_curve(polyx,polyy,sampx,sampy,subset=subset,repeat=10,method='LS',plot_title='Learning Curve '+NAME_MAP['LS'])
    err_RLS = learning_curve(polyx,polyy,sampx,sampy,subset=subset,repeat=10,method='RLS',plot_title='Learning Curve '+NAME_MAP['RLS'])
    err_LASSO = learning_curve(polyx,polyy,sampx,sampy,subset=subset,repeat=10,method='LASSO',plot_title='Learning Curve '+NAME_MAP['LASSO'])
    err_RR = learning_curve(polyx,polyy,sampx,sampy,subset=subset,repeat=10,method='RR',plot_title='Learning Curve '+NAME_MAP['RR'])
    err_BR = learning_curve(polyx,polyy,sampx,sampy,subset=subset,repeat=10,method='BR',plot_title='Learning Curve '+NAME_MAP['BR'])

    # outliers experiments
    outliers_x = [-1.3,0.5,0.7,1]
    outliers_y = [80,30,50,-30]

    mseol_LS = outliers_experiments(polyx,polyy,sampx,sampy,outliers_x,outliers_y,method='LS',plot_title=NAME_MAP['LS']+' with Outliers')
    mseol_RR = outliers_experiments(polyx,polyy,sampx,sampy,outliers_x,outliers_y,method='RR',plot_title=NAME_MAP['RR']+' with Outliers')
    mseol_RLS = outliers_experiments(polyx,polyy,sampx,sampy,outliers_x,outliers_y,paradict=opt_para_RLS,method='RLS',plot_title=NAME_MAP['RLS']+' with Outliers')
    mseol_LASSO = outliers_experiments(polyx,polyy,sampx,sampy,outliers_x,outliers_y,paradict=opt_para_LASSO,method='LASSO',plot_title=NAME_MAP['LASSO']+' with Outliers')
    mseol_BR = outliers_experiments(polyx,polyy,sampx,sampy,outliers_x,outliers_y,paradict=opt_para_BR,method='BR',plot_title=NAME_MAP['BR']+' with Outliers')

    # higer order experiments
    para_Lambda_o10 = {'Lambda':[0.1,0.25,0.5,1,2,5],'function':['poly'],'order':[10]}
    para_BR_o10 = {'alpha':[0.1,0.5,1,5],'sigma':[0.1,0.5,1,5],'function':['poly'],'order':[10]}

    mse_LS_o10 = experiment(polyx,polyy,sampx,sampy,paradict={'function':'poly','order':10,'Lambda':0},method='LS',plot_title=NAME_MAP['LS']+' order 10')
    mseMap_toCSV({'nohparam':mse_LS_o10},'mse_LS_o10.csv')

    mse_RR_o10 = experiment(polyx,polyy,sampx,sampy,paradict={'function':'poly','order':10,'Lambda':0},method='RR',plot_title=NAME_MAP['RR']+' order 10')
    mseMap_toCSV({'nohparam':mse_RR_o10},'mse_RR_o10.csv')

    # methods with hyper parameters
    para_err_RLS_o10,opt_para_RLS_o10 = model_selection(polyx,polyy,sampx,sampy,para_Lambda_o10,estimator='RLS')
    mseMap_toCSV(para_err_RLS_o10,'mse_RLS_o10.csv')
    mse_RLS_o10 = experiment(polyx,polyy,sampx,sampy,paradict=opt_para_RLS_o10,method='RLS',plot_title=NAME_MAP['RLS']+' order 10')

    para_err_LASSO_o10,opt_para_LASSO_o10 = model_selection(polyx,polyy,sampx,sampy,para_Lambda_o10,estimator='LASSO')
    mseMap_toCSV(para_err_LASSO_o10,'mse_LASSO_o10.csv')
    mse_LASSO_o10 = experiment(polyx,polyy,sampx,sampy,paradict=opt_para_LASSO_o10,method='LASSO',plot_title=NAME_MAP['LASSO']+' order 10')

    para_err_BR_o10,opt_para_BR_o10 = model_selection(polyx,polyy,sampx,sampy,para_BR_o10,estimator='BR')
    mseMap_toCSV(para_err_BR_o10,'mse_BR_o10.csv')
    mse_BR_o10 = experiment(polyx,polyy,sampx,sampy,paradict=opt_para_BR_o10,method='BR',plot_title=NAME_MAP['BR']+' order 10')

if __name__ == "__main__":
    main()