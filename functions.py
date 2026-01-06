import numpy as n
import time


# Determine the numerical derivative of the dataset
def D(xlist, ylist):
    yprime = n.diff(ylist)/n.diff(xlist)
    xprime =[]
    for p in range(len(yprime)):
        xtemp = (xlist[p+1]+xlist[p])/2
        xprime = n.append(xprime,xtemp)
    return xprime, yprime