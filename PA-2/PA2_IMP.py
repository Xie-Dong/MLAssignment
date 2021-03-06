import math as m
import os

import numpy as np
import pandas as pd
from numpy.random import shuffle
from scipy.spatial.distance import euclidean
from scipy.stats import multivariate_normal
from sklearn.utils import resample
from sklearn import preprocessing


def gaussian(x, miu, SIGMA):
    miu = np.nan_to_num(miu)
    SIGMA = np.nan_to_num(SIGMA)
    return multivariate_normal.pdf(x, miu, SIGMA, allow_singular=True)

    # return the probabilty of each x, dim = N * K
    # col = probabilty each x.
    # row = each mixture modelxxx


def get_mixture_Gaussian_pdf(x, miu, SIGMA):
    result = np.array([])
    n = x.shape[0]

    for j in range(0, miu.shape[0]):
        result = np.append(result, gaussian(x, miu[j], SIGMA[j]))
        # if j == 0 : n = len(result)

    return result.reshape(-1, n).T

# transpose


def T(x):
    if(hasattr(x, 'shape') == False):
        x = np.array(x)
    if(len(x.shape) > 1):
        return np.transpose(x)
    else:
        return x.reshape(-1, 1)


def load_file(filename='data.txt'):
    return np.genfromtxt(filename, dtype='double')

# In our experiment, input of x is row wise
# shape of x is N * D while N is the number of data point, D is dimension of each data


class ClusterAlgorithm:
    """Base class of of clustering algorithms"""
    K = 1
    itera = 1
    z = np.array([])
    x = np.array([])
    threshold = 0
    N = 0
    d = 1

    def __init__(self, k=1, itera=100, threshold=0.005):
        self.K = k
        self.itera = itera
        self.threshold = threshold

    def fit_x(self, x):
        """Fit input value of x, input of x is row wise"""
        if(hasattr(x, 'shape') == False):
            x = np.array(x)
        self.d = x.shape[1]
        self.x = x
        self.N = len(x)
        self.z = np.zeros((self.N, self.K))
        return


class Kmeans(ClusterAlgorithm):
    """K-means clustering heritage cluster algorithm"""

    miu = np.array([])

    def initial_miu(self, pick_index=[]):
        if (len(pick_index) == self.K):
            self.miu = self.x[pick_index]
            return
        else:
            self.miu = resample(self.x, n_samples=self.K,
                                replace=False, random_state=self.K
                                )
            return

    def fit_x(self, x, pick=[]):
        """Fit input value of x, input of x is row wise"""
        ClusterAlgorithm.fit_x(self, x)
        self.initial_miu(pick)
        return

    def get_result(self):
        """get cluster result (sigal value)"""
        return np.argmax(self.z, axis=1)

    def cluster(self):
        """start the clustering procedure"""
        if(len(self.x) < 1):
            print('no data')
            return

        count = 0

        while(count < self.itera):

            # Cluster Assignment
            z = np.array([])
            count += 1
            distance = np.array(
                [np.linalg.norm(self.x - item, axis=1) for item in self.miu]).T

            for item in distance:
                midx = np.argmin(item)
                item = 0 * item
                item[midx] = 1
                z = np.append(z, item)

            self.z = z.reshape(distance.shape)

            # Estimate center
            tmiu = (np.dot(self.z.T, self.x)) / np.sum(self.z, axis=0)[:, None]

            # Termination of iteration
            if(np.linalg.norm(self.miu - tmiu) < self.threshold):
                self.miu = tmiu
                return

            else:
                self.miu = tmiu
        return


class WeightedKmeans4D(Kmeans):
    """Weighted Kmeans allow weighting between feature typs"""
    Lambda = 0

    def __init__(self, k=1, itera=100, threshold=0.005, Lambda=0.1):
        ClusterAlgorithm.__init__(self, k, itera, threshold)
        self.Lambda = Lambda

    def weighted_distance_4d(self, a, b):
        """
        - compute weighted distance
        - a is a metrix n * 4
        - b is a vector 1 * 4
        - retutn a distance vector 1 * 4
        """
        if(self.d != 4):
            print('it is not a 4 - dimensional data clustering')
            return

        chdim = int((self.d) / 2)

        minus = a - b

        left = np.square(np.linalg.norm(minus[:, :chdim], axis=1))
        right = np.square(np.linalg.norm(minus[:, chdim:], axis=1))

        return left + self.Lambda * right

    def cluster(self):
        """start the clustering procedure"""
        if(len(self.x) < 1):
            print('no data')
            return

        if(self.d != 4):
            print('it is not a 4 - dimensional data clustering')
            return

        count = 0

        while(count < self.itera):

            # Cluster Assignment
            z = np.array([])
            count += 1
            distance = np.array(
                [self.weighted_distance_4d(self.x, item) for item in self.miu]).T

            for item in distance:
                midx = np.argmin(item)
                item = 0 * item
                item[midx] = 1
                z = np.append(z, item)

            self.z = z.reshape(distance.shape)

            # Estimate center
            tmiu = (np.dot(self.z.T, self.x)) / np.sum(self.z, axis=0)[:, None]

            # Termination of iteration
            if(np.linalg.norm(self.miu - tmiu) < self.threshold):
                self.miu = tmiu
                return

            else:
                self.miu = tmiu
        return


class EMMM(ClusterAlgorithm):
    """Base class for all EM clustering mixture model"""
    pi = np.array([])

    def fit_x(self, x, pi=[]):
        """Fit input value of x, input of x is row wise"""
        ClusterAlgorithm.fit_x(self, x)
        self.initial_pi(pi)
        return

    def initial_pi(self, pi_init=[]):
        if(len(pi_init) == self.K):
            self.pi = np.array(pi_init)
            return
        else:
            self.pi = np.ones(self.K) / self.K
            return

    def get_result(self):
        """get cluster result (sigal value)"""
        return np.argmax(self.z, axis=1)


class EMGMM(EMMM):
    """EM Mixture Gaussian Model"""
    miu = np.array([])
    SIGMA = np.array([])

    def __init__(self, k=1, itera=10, threshold=0.005):
        EMMM.__init__(self, k, itera, threshold)

    def fit_x(self, x, miu=[], SIGMA=np.array([])):
        """Fit input value of x, input of x is row wise"""
        EMMM.fit_x(self, x)
        self.initial_miu(miu_init=miu)
        self.initial_SIGMA(SIGMA_init=SIGMA)

        return

    def initial_miu(self, miu_init=[], sample=True):
        """Set initial of miu, you can set value you want, sampling dataset, or average value"""
        if(len(miu_init) == self.d):
            self.miu = np.array(miu_init)

        elif(sample is True):
            self.miu = resample(self.x, n_samples=self.K,
                                replace=False, random_state=self.d)
        else:
            avg = np.average(self.x)
            inivalues = np.linspace(avg, self.K, num=(self.K) * self.d)
            self.miu = inivalues.reshape(self.K, self.d)
        return

    def initial_SIGMA(self, SIGMA_init=np.array([])):

        # you can assign any values to the initial sigma or just use eye matrix
        if(SIGMA_init.shape == (self.K, self.d, self.d)):
            self.SIGMA = SIGMA_init
        else:
            eyed = np.eye(self.d)
            self.SIGMA = np.array([eyed for i in range(0, self.K)])

        return

    def cluster(self):
        if(len(self.x) < 1):
            print('no data')
            return

        count = 0
        N = self.x.shape[0]

        while(count < self.itera):
            count += 1
            z = self.z
            miu = self.miu
            pi = self.pi
            SIGMA = self.SIGMA

            # return the probabilty of each x, dim = N * K
            # sample gaussian outputs a martix of probability of each components of all samples dim =  N (samples) * K (components)
            sample_gaussians = get_mixture_Gaussian_pdf(
                self.x, self.miu, self.SIGMA)
            # dpi = np.diag(self.pi)

            # E step z_ij = pi_j * Gaussian(x_i,theta_j)/ sum_over_k(pi_k * Gaussian(x_i,theta_k))
            # z_numerator = np.dot(sample_gaussians, dpi)
            z_numerator = sample_gaussians * pi
            z_denominator = np.sum(z_numerator, axis=1)
            z = (z_numerator.T / z_denominator).T

            # M step
            N_j = np.sum(z, axis=0)
            pi = N_j / N

            miu = ((np.dot(z.T, self.x).T) / N_j).T

            # SIMGA = 1/N[j] * sum_over_i(z[i][j]*(x[i]-miu[j])(x[i]-miu[j]).T)
            SIGMA = np.array([np.dot(((self.x - miu[j]).T * z[:, j]), self.x - miu[j])
                              for j in range(0, self.K)])
            SIGMA = (SIGMA.T / N_j).T

            # Temination of iteration
            if((np.linalg.norm(self.miu - miu) < self.threshold) and (np.linalg.norm(self.SIGMA - SIGMA) < self.threshold)):
                self.z = z
                self.miu = miu
                self.SIGMA = SIGMA
                self.pi = pi
                print(count)
                return

            self.z = z
            self.miu = miu
            self.SIGMA = SIGMA
            self.pi = pi
        return


class GaussianMeanShift(ClusterAlgorithm):
    """MeanShift clustering algorithm"""
    h = 0
    # Bandiwith of the kernel

    x_ = np.array([])
    kernel = ''
    tolarance = 0
    # tolarance of result outputing, it is the decemal

    def __init__(self, itera=10, threshold=0.005, bandwidth=5, kernel='gaussian', tolarance=5):
        ClusterAlgorithm.__init__(self, itera=itera, threshold=threshold)
        self.kernel = kernel
        self.h = bandwidth
        self.tolarance = tolarance

    def fit_x(self, x):
        ClusterAlgorithm.fit_x(self, x)
        self.x_ = x
        return

    def update(self):
        if(self.kernel == 'gaussian'):
            dia_sqrh = np.eye(self.d) * (self.h) * (self.h)
            covs = np.array([dia_sqrh for i in range(0, self.N)])

            # return the probabilty of each x, dim = N * N
            # sample gaussian outputs a martix of probability of each components of all samples dim =  N (samples) * N (components)
            sample_gaussians = get_mixture_Gaussian_pdf(
                self.x, self.x_, covs)

            x_numerator = np.dot(sample_gaussians.T, self.x)
            x_denominator = np.sum(sample_gaussians, axis=0)
            x = (x_numerator.T / x_denominator).T

            return x

    def cluster(self):
        if(len(self.x) < 1):
            print('no data')
            return
        count = 0
        while (count < self.itera):
            count += 1
            x_ = self.update()
            if((np.linalg.norm(self.x_ - x_) < self.threshold)):
                print(count)
                self.x_ = x_
                return
            self.x_ = x_
        return

    def get_result(self):
        """
         round the x_ value using a specific decimal value
         encode different rounding results to 0 - n classes
         n is not fixed
        """
        x_ = self.x_
        roundx = np.around(x_, decimals=self.tolarance)
        strx = roundx.astype(str)
        strxj = [",".join(item) for item in strx]
        le = preprocessing.LabelEncoder()
        result = le.fit_transform(strxj)
        return result


class WeightGMeanshift(GaussianMeanShift):
    hc = 0

    def __init__(self, chrominance_bandwidth=5, location_bandwidth=5, itera=10, threshold=0.005, kernel='weighted_gaussian', tolarance=5):
        GaussianMeanShift.__init__(self, itera=itera, bandwidth=chrominance_bandwidth,
                                   threshold=threshold, kernel=kernel, tolarance=tolarance)
        self.hc = location_bandwidth

    def fit_x(self, x):
        GaussianMeanShift.fit_x(self, x)
        if (self.d != 4):
            print('not 4 -dmiensional ')

    def update(self):
        """
            weighted gaussian is 
            put first d/2 diemnsion in to Gaussian_hp with covariance hp**2 
            put last d/2 diemnsion in to Gaussian_hc with covariance hc**2 
            weighted gaussian return pdf_hp * pdf_hc
        """
        if(self.kernel == 'weighted_gaussian'):

            chdim = int((self.d) / 2)
            # this method change the covariance to a non isotropic one 
            # by modifieng the cov matrix
            # 2 times faster than multiping two gaussians.
            dia_sqrhp = np.ones(chdim) * ((self.h) ** 2)
            dia_sqrhc = np.ones(chdim) * ((self.hc) ** 2)

            dia_cov = np.concatenate((dia_sqrhp,dia_sqrhc))

            cov =  np.diag(dia_cov)

            covh = np.array([cov for i in range(0, self.N)])

            # return the probabilty of each x, dim = N * N
            # sample gaussian outputs a martix of probability of each components of all samples dim =  N (samples) * N (components)
            # compare with multipying two gaussian , denominator need to multipied sqrt(2 * pi)

            sample_gaussians = get_mixture_Gaussian_pdf(
                self.x, self.x_, covh)

            sample_gaussians = sample_gaussians / (m.sqrt(2*m.pi))

            x_numerator = np.dot(sample_gaussians.T, self.x)
            x_denominator = np.sum(sample_gaussians, axis=0)
            x = (x_numerator.T / x_denominator).T

            return x

def main():

    KM = WeightedKmeans4D(k=2, itera=100)
    x = np.array([[1, 1, 2, 2], [9, 7, 15, 15], [1, 2, 3, 4]])
    KM.fit_x(x)
    KM.cluster()
    print(KM.get_result())

    # GMM = EMGMM(k=3, itera=100)
    #x = np.array([[1, 1], [2, 2], [9, 7], [15, 15], [105, 5]])
    # GMM.fit_x(x)
    # GMM.cluster()

    # print(GMM.z)
    # print(GMM.miu)
    # print(GMM.SIGMA)

    MS = WeightGMeanshift(chrominance_bandwidth=3,
                          location_bandwidth=5, itera=1, tolarance=1)
    MS.fit_x(x)
    MS.cluster()
    print(MS.x_)
    print(MS.get_result())
    return


if __name__ == "__main__":
    main()
