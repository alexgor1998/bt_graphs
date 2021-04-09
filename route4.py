# -*- coding: utf-8 -*-
"""
Created on Tue Mar 23 18:04:41 2021
@author: Alex
"""

import json
import numpy as np
import pandas as pd
import geopy.distance as gd
from math import radians, cos, sin, atan2, pi

def in_dict(key, dict):
    return key in dict

def azimuth(point1,point2):
    lat1 = point1[0]
    lon1 = point1[1]
    lat2 = point2[0]
    lon2 = point2[1]
# convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    az = atan2(sin(lon2-lon1)*cos(lat2),
                    cos(lat1)*sin(lat2)-sin(lat1)*cos(lat2)*cos(lon2-lon1))
    #azd = degrees(az)
    #if azd < 0:
    #    azd += 360
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
route0 = []
f1 = open('routes.geojson', 'r', encoding='utf-8')
data = json.load(f1)
for feature in data['features']:
    if ((in_dict('ref', feature['properties']) == True)
    and (feature['properties']['ref'] == '5')
    and (feature['properties']['route'] == 'tram')):
        route0.append(feature['geometry']['coordinates'][0])
route = [[],[]]        
route[0] = np.array(route0[0])
route[1] = np.array(route0[1])
#swapping (lon,lat) to (lat,lon)
route[0][:,[0,1]] = route[0][:,[1,0]]
route[1][:,[0,1]] = route[1][:,[1,0]]
#print('\n')
#print(route)

pts_fwd = len(route[0])
pts_bwd = len(route[1])
#onroute distance in forward direction (increases along the track)
dist_fwd = [gd.distance(route[0][i-1],route[0][i]).km
            for i in range(pts_fwd)]
dist_fwd[0] = 0 #distance from point #0 to point #0 is 0
s_fwd = np.cumsum(dist_fwd) #distance from point #0 to point #i
len_fwd = s_fwd[-1]
#onroute distance in backward direction (decreases along the track)
dist_bwd = [gd.distance(route[1][i-1],route[1][i]).km
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

rt_table = day_table[day_table['bus_id'] == bid]

ts_list = pd.unique(rt_table['bus_name'])
print(ts_list)
print('\n')
sample_ts = ts_list[0]
ts_table = rt_table.loc[rt_table['bus_name'] == sample_ts]
#print(ts_table)
direction = -1  #initial direction unknown
s = 0.0
pathgraph = []

for ind,ts_point in ts_table.iterrows():
    coords = [ts_point['lat'],ts_point['lon']]
    #proxtable = list of proximities from the point to the route segments
    if (direction == 0):
        proxtable = [proximity(coords,route[0][i],route[0][i+1])
                     for i in range(pts_fwd-1)]
        #calculating distance from terminus 0
        iprox = np.argmin(proxtable)
        s = s_fwd[iprox] + gd.distance(coords,route[0][iprox]).km
    if (direction == 1):
        proxtable = [proximity(coords,route[1][i],route[1][i+1])
                     for i in range(pts_fwd-1)]
        iprox = np.argmin(proxtable)
        s = s_bwd[iprox+1] + gd.distance(coords,route[1][iprox+1]).km    
    if  (gd.distance(route[0][0],coords).km < 0.02):
        #we are close to terminus 0
        direction = 0
        s = 0
    if  (gd.distance(route[1][0],coords).km < 0.02):
        #we are close to terminus 1
        direction = 1
        s = len_bwd
    pathgraph.append([ts_point['timestamp'][11:19],s])
    
print(*pathgraph,sep = '\n')