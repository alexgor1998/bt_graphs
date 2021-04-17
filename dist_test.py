# -*- coding: utf-8 -*-
"""
Created on Sat Apr 10 11:22:49 2021

@author: Alex
"""

import geopy.distance as gd
import numpy as np
from tqdm import tqdm
from math import dist,sin,cos
def azimuth(points1,points2):
    # note: angles are computed clockwise from vertical axis, like real azimuths 
    points1 = np.reshape(points1,(-1,2))
    points2 = np.reshape(points2,(-1,2))
    deltas = points2 - points1
    return np.arctan2(deltas[:,0], deltas[:,1])
def proximity(point0,startpoint,endpoint):
    angle1 = azimuth(startpoint,point0) - azimuth(startpoint,endpoint)
    angle2 = azimuth(endpoint,startpoint) - azimuth(endpoint, point0)    
    sdist = np.sqrt(np.sum((startpoint - point0) ** 2,axis = 1))
    edist = np.sqrt(np.sum((endpoint - point0) ** 2,axis = 1))
    is_transversal = ((np.cos(angle1) > 0) & (np.cos(angle2) > 0))
    # if projection goes onto the segment
    project = np.abs(sdist*np.sin(angle1))
    # if projection goes beyond the segment => doesn't represent distance
    dist_ptp = np.fmin(sdist, edist)
    res = np.where(is_transversal,project,dist_ptp)
    return res

def azimuth_old(point1,point2):
    x1 = point1[0]
    y1 = point1[1]
    x2 = point2[0]
    y2 = point2[1]
    az = np.arctan2(x2-x1,y2-y1)
    return az
def proximity_old(point0,startpoint,endpoint):
    angle1 = azimuth_old(startpoint,point0) - azimuth_old(startpoint,endpoint)
    angle2 = azimuth_old(endpoint,startpoint) - azimuth_old(endpoint, point0)
    sdist = dist(startpoint, point0)
    edist = dist(endpoint, point0)
    project = abs(sdist*sin(angle1))
    if (cos(angle1) > 0) and (cos(angle2) > 0):
        #min distance is transversal
        return project
    else:
        #min distance is point to point
        return min(sdist, edist)
    
city_lat = 56.32694
city_lon = 44.00750
par_n = gd.distance([city_lat+0.5,city_lon-0.5],[city_lat+0.5,city_lon+0.5]).km
par_s = gd.distance([city_lat-0.5,city_lon-0.5],[city_lat-0.5,city_lon+0.5]).km
merid = gd.distance([city_lat-0.5,city_lon],[city_lat+0.5,city_lon]).km
#print(par_n,par_s,merid)

lat = 0
lon = 0
flaty = (lat - city_lat)*merid
flatx = (lon - city_lon)*((lat - city_lat + 0.5)*par_n + (lat - city_lat - 0.5)*par_s)

a = np.array([[0,1],[0,2],[0,3],[0,4]])
b = np.array([[10,0],[10,0],[10,0],[10,0]])
c = np.array([0,0])
d = np.array([1,0])
points1 = np.array([[1,1],[3,4],[3,0],[0,4],[-2,2]])
points2 = np.array([[1,-1],[3,5],[0,4],[3,0],[-3,3]])
#print(azimuth(a,c),'\n',azimuth2(a,c))
print(azimuth(c,d))
#print(azimuth(a,d))
#print(proximity(c,points1,points2))
#print(np.sqrt(np.sum((points1 - points2) ** 2,axis = 1)))  
def proxcycle(coords,p1,p2):
    res =  [proximity_old(coords,p1[i],p2[i]) for i in range(len(p1))]
    return res
#for _ in tqdm(range(20_000)):
#    proximity(c,points1,points2)
#for _ in tqdm(range(20_000)):
#    proxcycle(c,points1,points2)

#p1 = [56.308633,43.983249]
#p2 = [56.304022,43.989174]
#p3 = [56.29015,43.995673]
#print(azimuth(p1,p2))
#print(proximity(p2,p1,p3))
