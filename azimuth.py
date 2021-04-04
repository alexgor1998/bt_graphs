# -*- coding: utf-8 -*-
"""
Created on Sat Apr  3 20:12:16 2021

@author: Alex
"""
from math import radians, cos, sin, atan2, pi
import geopy.distance as gd

def azimuth(point1,point2):
    # convert decimal degrees to radians
    lat1 = point1[0]
    lon1 = point1[1]
    lat2 = point2[0]
    lon2 = point2[1]
    
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    az = atan2(sin(lon2-lon1)*cos(lat2),
                    cos(lat1)*sin(lat2)-sin(lat1)*cos(lat2)*cos(lon2-lon1))
    if az < 0:
        az += 2*pi
    return az

def proximity(point0,startpoint,endpoint):
    angle1 = azimuth(startpoint,point0) - azimuth(startpoint,endpoint)
    angle2 = azimuth(endpoint,startpoint) - azimuth(endpoint, point0)    
    sdist = gd.distance(startpoint, point0).km
    edist = gd.distance(endpoint, point0).km
    project = abs(sdist*sin(angle1))
    if (abs(angle1) < pi/2) and (abs(angle2) < pi/2):
        #min distance is transvelsal
        return project
        #min distance is point to point
    else:
        return min(sdist, edist)
p1 = [56.308633,43.983249]
p2 = [56.304022,43.989174]
p3 = [56.29015,43.995673]
print(azimuth(p1,p2))
print(proximity(p2,p1,p3))