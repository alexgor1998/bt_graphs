# -*- coding: utf-8 -*-
"""
Created on Tue Mar 23 18:04:41 2021
@author: Alex
"""

import json
import numpy as np
from geopy import distance

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
"""
for i in range(n):
    print(route[i])
    print('\n')
"""
pts_fwd = len(route[0])
pts_bwd = len(route[1])

dist_fwd = [distance.distance(distance.lonlat(*route[0][i-1]),
                              distance.lonlat(*route[0][i])).km
            for i in range(pts_fwd)]
dist_fwd[0] = 0 #distance from point #0 to point #0 is 0
s_fwd = np.cumsum(dist_fwd)
len_fwd = s_fwd[-1]

dist_bwd = [distance.distance(distance.lonlat(*route[1][i-1]),
                              distance.lonlat(*route[1][i])).km
            for i in range(pts_bwd)]
dist_bwd[0] = 0 
s_bwd = np.cumsum(dist_bwd)

len_bwd = s_bwd[-1]
s_bwd = len_bwd - s_bwd
print(s_bwd)

print('\n')
print(len_fwd)
print(len_bwd)
print(abs(len_fwd-len_bwd)/(len_fwd+len_bwd)*2)

