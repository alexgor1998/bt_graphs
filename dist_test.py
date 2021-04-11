# -*- coding: utf-8 -*-
"""
Created on Sat Apr 10 11:22:49 2021

@author: Alex
"""
from math import atan2, dist, sin, pi
import geopy.distance as gd
from tqdm import tqdm

def azimuth(point1,point2):
    x1 = point1[0]
    y1 = point1[1]
    x2 = point2[0]
    y2 = point2[1]

    az = atan2(x2-x1,y2-y1)
    if az < 0:
        az += 2*pi
    return az

def proximity(point0,startpoint,endpoint):
    angle1 = azimuth(startpoint,point0) - azimuth(startpoint,endpoint)
    angle2 = azimuth(endpoint,startpoint) - azimuth(endpoint, point0)    
    sdist = dist(startpoint, point0)
    edist = dist(endpoint, point0)
    project = abs(sdist*sin(angle1))
    if (abs(angle1) < pi/2) and (abs(angle2) < pi/2):
        #min distance is transvelsal
        return project
        #min dictance is point to point
    else:
        return min(sdist, edist)
city_lat = 56.32694
city_lon = 44.00750
par_n = gd.distance([city_lat+0.5,city_lon-0.5],[city_lat+0.5,city_lon+0.5]).km
par_s = gd.distance([city_lat-0.5,city_lon-0.5],[city_lat-0.5,city_lon+0.5]).km
merid = gd.distance([city_lat-0.5,city_lon],[city_lat+0.5,city_lon]).km
print(par_n,par_s,merid)

lat = 0
lon = 0
flaty = (lat - city_lat)*merid
flatx = (lon - city_lon)*((lat - city_lat + 0.5)*par_n + (lat - city_lat - 0.5)*par_s)


#for _ in tqdm(range(20_000)):
#    proximity((0,0),(2,2),(1,0))

#p1 = [56.308633,43.983249]
#p2 = [56.304022,43.989174]
#p3 = [56.29015,43.995673]
#print(azimuth(p1,p2))
#print(proximity(p2,p1,p3))
