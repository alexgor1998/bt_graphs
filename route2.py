# -*- coding: utf-8 -*-
"""
Created on Tue Mar 23 18:04:41 2021
@author: Alex
"""

import json
import numpy as np
import matplotlib.pyplot as plt
import geopy.distance as gd

def in_dict(key, dict):
    return key in dict
def flatten(lat,lon):
    # flattening coordinates assuming 1x1 degree being a trapezoid
    flaty = (lat - city_lat)*merid
    flatx = (lon - city_lon)*((lat - city_lat + 0.5)*par_n + (city_lat - lat + 0.5)*par_s)
    flatxy = np.zeros((2,len(lat)))
    flatxy[0] = flatx
    flatxy[1] = flaty
    return flatxy

city_lat = 56.32694
city_lon = 44.00750
par_n = gd.distance([city_lat+0.5,city_lon-0.5],[city_lat+0.5,city_lon+0.5]).km
par_s = gd.distance([city_lat-0.5,city_lon-0.5],[city_lat-0.5,city_lon+0.5]).km
merid = gd.distance([city_lat-0.5,city_lon],[city_lat+0.5,city_lon]).km
route_name = 'А-40'
print('Route extracion started!')
route0 = []
f1 = open('routes.geojson', 'r', encoding='utf-8')
data = json.load(f1)
f1.close()
for feature in data['features']:
    if ((in_dict('ref:official', feature['properties']) == True)
        and (feature['properties']['ref:official'] == route_name)):
        route0.append(feature['geometry']['coordinates'][0])
georoute = [[],[]]        
georoute[0] = np.array(route0[0])
georoute[1] = np.array(route0[1])
route = [[],[]]
route[0] = np.swapaxes(flatten(georoute[0][:,1],georoute[0][:,0]),0,1)
route[1] = np.swapaxes(flatten(georoute[1][:,1],georoute[1][:,0]),0,1)
print('Route extracted and flattened!')

plt.plot(route[0][:,0],route[0][:,1])
plt.plot(route[1][:,0],route[1][:,1])
plt.axis('equal') #also may try 'scaled'
plt.savefig(route_name+'_map.png', bbox_inches = 'tight', dpi = 500)
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
#print(s_bwd)

print(len_fwd)
print(len_bwd)
print(abs(len_fwd-len_bwd)/(len_fwd+len_bwd)*2)


