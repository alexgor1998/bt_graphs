# -*- coding: utf-8 -*-
"""
Created on Tue Mar 23 18:04:41 2021
@author: Alex
"""

import json
import numpy as np
import pandas as pd
import geopy.distance as gd
from math import atan2, dist, sin, cos, pi
import matplotlib.pyplot as plt
def in_dict(key, dict):
    return key in dict

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
    if (cos(angle1) > 0) and (cos(angle2) > 0):
        #min distance is transvelsal
        return project
        #min dictance is point to point
    else:
        return min(sdist, edist)
def flatten(lat,lon):
    #flattening coordinates assuming 1x1 degree being a trapezoid
    flaty = (lat - city_lat)*merid
    flatx = (lon - city_lon)*((lat - city_lat + 0.5)*par_n + (city_lat - lat + 0.5)*par_s)
    flatxy = np.zeros((2,len(lat)))
    flatxy[0] = flatx
    flatxy[1] = flaty
    return flatxy

#main    
city_lat = 56.32694
city_lon = 44.00750
par_n = gd.distance([city_lat+0.5,city_lon-0.5],[city_lat+0.5,city_lon+0.5]).km
par_s = gd.distance([city_lat-0.5,city_lon-0.5],[city_lat-0.5,city_lon+0.5]).km
merid = gd.distance([city_lat-0.5,city_lon],[city_lat+0.5,city_lon]).km

route0 = []
f1 = open('routes.geojson', 'r', encoding='utf-8')
data = json.load(f1)
for feature in data['features']:
    if ((in_dict('ref', feature['properties']) == True)
    and (feature['properties']['ref'] == '5')
    and (feature['properties']['route'] == 'tram')):
        route0.append(feature['geometry']['coordinates'][0])
georoute = [[],[]]        
georoute[0] = np.array(route0[0])
georoute[1] = np.array(route0[1])
#print('\n')
#print(georoute[0])
route = [[],[]]
route[0] = np.swapaxes(flatten(georoute[0][:,1],georoute[0][:,0]),0,1)        
route[1] = np.swapaxes(flatten(georoute[1][:,1],georoute[1][:,0]),0,1)
#swapping axes to represent as a set of points [[x1,y1],[x2,y2],...]     
#print(route[0])

#plt.plot(route[0][:,0],route[0][:,1])
#plt.plot(route[1][:,0],route[1][:,1])
#plt.axis('equal') #also may try 'scaled'

pts_fwd = len(route[0])
pts_bwd = len(route[1])

#onroute distance in forward direction (increases along the track)
dist_fwd = [dist(route[0][i-1],route[0][i])
            for i in range(pts_fwd)]
dist_fwd[0] = 0 #distance from point #0 to point #0 is 0
s_fwd = np.cumsum(dist_fwd) #distance from point #0 to point #i
len_fwd = s_fwd[-1]
#onroute distance in backward direction (decreases along the track)
dist_bwd = [dist(route[1][i-1],route[1][i])
            for i in range(pts_bwd)]
dist_bwd[0] = 0 
s_bwd = np.cumsum(dist_bwd)
len_bwd = s_bwd[-1]
s_bwd = len_bwd - s_bwd

#print(len_fwd)
#print(len_bwd)
#print(abs(len_fwd-len_bwd)/(len_fwd+len_bwd)*2)

f2 = open('bus_track_2021-03-27.csv', 'r', encoding='utf-8')
day_table = pd.read_csv(f2)
bid = 7995 #for tram #5 -> bus_id = 7995

rt_table = day_table[day_table['bus_id'] == bid].copy()
rt_table['x'],rt_table['y'] = flatten(rt_table['lat'],rt_table['lon'])

ts_list = pd.unique(rt_table['bus_name'])
print(ts_list)

sample_ts = ts_list[1]
ts_table = rt_table.loc[rt_table['bus_name'] == sample_ts]
#print(ts_table)
direction = None  #initial direction unknown

s = 0.0
pathgraph = [[],[]]
print('Path calculation started!')
for ind,ts_point in ts_table.iterrows():
    coords = [ts_point['x'],ts_point['y']]
    #proxtable = list of proximities from the point to the route segments
    if (direction == 0):
        proxtable = [proximity(coords,route[0][i],route[0][i+1])
                     for i in range(pts_fwd-1)]
        #calculating distance from terminus 0
        iprox = np.argmin(proxtable)
        s = s_fwd[iprox] + dist(coords,route[0][iprox])
    if (direction == 1):
        proxtable = [proximity(coords,route[1][i],route[1][i+1])
                     for i in range(pts_bwd-1)]
        iprox = np.argmin(proxtable)
        s = s_bwd[iprox+1] + dist(coords,route[1][iprox+1])    
    if  (dist(route[0][0],coords) < 0.05):
        #we are close to terminus 0
        direction = 0
        s = 0
    if  (dist(route[1][0],coords) < 0.05):
        #we are close to terminus 1
        direction = 1
        s = len_bwd
    pathgraph[0].append(ts_point['timestamp'][11:19])
    pathgraph[1].append(s)
print('Path calculation complete!')
#print(*pathgraph,sep = '\n')
plt.plot(pathgraph[0],pathgraph[1])