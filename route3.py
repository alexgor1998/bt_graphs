# -*- coding: utf-8 -*-
"""
Created on Tue Mar 23 18:04:41 2021
@author: Alex
"""

import json
import numpy as np
import pandas as pd
import geopy.distance as gd
from math import radians, cos, sin, atan2, degrees

def azimuth(lat1, lon1, lat2, lon2):
    # convert decimal degrees to radians 
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    az = atan2(sin(lon2-lon1)*cos(lat2),
                    cos(lat1)*sin(lat2)-sin(lat1)*cos(lat2)*cos(lon2-lon1))
    azd = degrees(az)
    if azd < 0:
        azd += 360
    return azd
def in_dict(key, dict):
    return key in dict

route0 = []
f1 = open('routes.geojson', 'r', encoding='utf-8')
data = json.load(f1)
for feature in data['features']:
    if ((in_dict('ref', feature['properties']) == True)
    and (feature['properties']['ref'] == '5')
    and (feature['properties']['route'] == 'tram')):
        route0.append(feature['geometry']['coordinates'][0])
route = np.array(route0)
n = len(route)

pts_fwd = len(route[0])
pts_bwd = len(route[1])

dist_fwd = [gd.distance(gd.lonlat(*route[0][i-1]),
                     gd.lonlat(*route[0][i])).km
            for i in range(pts_fwd)]
dist_fwd[0] = 0 #distance from point #0 to point #0 is 0
s_fwd = np.cumsum(dist_fwd)
len_fwd = s_fwd[-1]

dist_bwd = [gd.distance(gd.lonlat(*route[1][i-1]),
                     gd.lonlat(*route[1][i])).km
            for i in range(pts_bwd)]
dist_bwd[0] = 0 
s_bwd = np.cumsum(dist_bwd)

len_bwd = s_bwd[-1]
s_bwd = len_bwd - s_bwd

print(len_fwd)
print(len_bwd)
print(abs(len_fwd-len_bwd)/(len_fwd+len_bwd)*2)

f2 = open('bus_track_2021-03-27.csv', 'r', encoding='utf-8')
day_table = pd.read_csv(f2)
bid = 7995 #for tram #5 -> bus_id = 7995
rt_table = day_table[day_table['bus_id'] == bid]
ts_list = pd.unique(rt_table['bus_name'])
print(ts_list)
print('\n')
sample_ts = ts_list[0]
ts_table = rt_table[rt_table['bus_name'] == sample_ts]
#print(ts_table)
direction = -1
coords_prev = [ts_table.iloc[0]['lat'],ts_table.iloc[0]['lon']]
#print(coords_prev)
s = 0.0
pathgraph = []
for ind,ts_point in ts_table.iterrows():
    coords = [ts_point['lat'],ts_point['lon']]
    if (direction == 0):
        s = s + gd.distance(coords,coords_prev).km
    if (direction == 1):
        s = s - gd.distance(coords,coords_prev).km
    coords_prev = coords
    if  (gd.distance(gd.lonlat(*route[0][0]),coords).km < 0.05):
        direction = 0
        s = 0
#        print('at ',ts_point['timestamp'],' we are starting at terminal 0!')
    if  (gd.distance(gd.lonlat(*route[1][0]),coords).km < 0.05):
        direction = 1
        s = len_bwd
#        print('at ',ts_point['timestamp'],' we are starting at terminal 1!')
    pathgraph.append([ts_point['timestamp'][11:19],s])
    
print(*pathgraph,sep = '\n')