import math as m
import os

import numpy as np
import pandas as pd
import pylab as pl
import scipy.io as sio
from PIL import Image  # python3

import pa2
import PA2_IMP as im
import scipy.cluster.vq as vq


IMGPATH = os.path.join('PA-2', 'data', 'images')
OUTPATH = os.path.join('PA-2', 'data', 'processed')

DATA = os.listdir(IMGPATH)

METHODS = ['KM', 'EMGMM', 'WKM', 'GMS', 'WGMS']
K = [2, 5, 10, 50]
Lambda = [0.1, 0.5, 2, 5, 10]


def main():
    exp_dict = {}

    for data in DATA:

        img = Image.open(os.path.join(IMGPATH, data))
        pl.subplot(1, 3, 1)
        pl.imshow(img)

        X_raw, L = pa2.getfeatures(img, 7)
        X = vq.whiten(X_raw.T)

        for method in METHODS[:2]:
            for k in K:
                if(method == 'KM'):
                    clf = im.Kmeans(k=k)
                if(method == 'EMGMM'):
                    clf = im.EMGMM(k=k)
                clf.fit_x(X)
                clf.cluster()

                Y = clf.get_result() + 1
                segm = pa2.labels2seg(Y, L)
                pl.subplot(1, 3, 2)
                pl.imshow(segm)
                csegm = pa2.colorsegms(segm, img)
                pl.subplot(1, 3, 3)
                pl.imshow(csegm)
                pl.savefig(os.path.join(OUTPATH, data + '_' +
                                        method + '_' + str(k) + '_processed.jpg'))
                pl.show()

    for data2 in DATA:

        img = Image.open(os.path.join(IMGPATH, data2))
        pl.subplot(1, 3, 1)
        pl.imshow(img)

        X_raw, L = pa2.getfeatures(img, 7)
        X = vq.whiten(X_raw.T)
        
        for l in Lambda:
            for k in K:
                WKM = im.WeightedKmeans4D(k=k, Lambda=l)
                WKM.fit_x(X)
                WKM.cluster()
                Y = WKM.get_result() + 1
                segm = pa2.labels2seg(Y, L)
                pl.subplot(1, 3, 2)
                pl.imshow(segm)
                csegm = pa2.colorsegms(segm, img)
                pl.subplot(1, 3, 3)
                pl.imshow(csegm)
                pl.savefig(os.path.join(OUTPATH, data2 + '_WKM_' + str(k) + '_' + str(l) + '_processed.jpg'))
                pl.show()

    return


if __name__ == "__main__":
    pl.switch_backend('agg')
    main()
