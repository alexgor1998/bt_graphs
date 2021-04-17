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
import matplotlib.cm as cm
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
def getdistance(point0,route_track):
    prox_table = proximity(point0, route_track[:-1], route_track[1:])
    prox_value =  np.min(prox_table)
    prox_index = np.argmin(prox_table)
    return prox_value,prox_index

# Main start here    
# latitude and longitude for Nizhniy Novgorod
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
# swapping axes to represent as a set of points [[x1,y1],[x2,y2],...]
#print(route[0])

#plt.plot(route[0][:,0],route[0][:,1])
#plt.plot(route[1][:,0],route[1][:,1])
#plt.axis('equal') #also may try 'scaled'

pts_fwd = len(route[0])
pts_bwd = len(route[1])

# onroute distance in forward direction (increases along the route)
dist_fwd = [dist(route[0][i-1],route[0][i])
            for i in range(pts_fwd)]
#may try dist_fwd = np.sqrt(np.sum((route[0][:-1], route[0][1:]) ** 2,axis = 1))
dist_fwd[0] = 0 # distance from point #0 to point #0 is 0
s_fwd = np.cumsum(dist_fwd) # distance from point #0 to point #i
len_fwd = s_fwd[-1]
# onroute distance in backward direction (decreases along the route to 0 at terminus 0)
dist_bwd = [dist(route[1][i-1],route[1][i])
            for i in range(pts_bwd)]
dist_bwd[0] = 0 
s_bwd = np.cumsum(dist_bwd)
len_bwd = s_bwd[-1]
s_bwd = len_bwd - s_bwd
#print(len_fwd)
#print(len_bwd)
#print(abs(len_fwd-len_bwd)/(len_fwd+len_bwd)*2)
f2 = open('bus_index.csv', 'r', encoding='utf-8')
bus_list = pd.read_csv(f2)
bus_id = bus_list.loc[bus_list['bus_name'] == route_name,'bus_id'].iloc[0] # for tram #5 -> bus_id = 7995
#print(bus_id)

f3 = open('bus_track_nizhniy-novgorod_2021-04-15.csv', 'r', encoding='utf-8')
day_table = pd.read_csv(f3)
f3.close()
date = day_table['timestamp'][0][0:10]
rt_table = day_table[day_table['bus_id'] == bus_id].copy()
rt_table['x'],rt_table['y'] = flatten(rt_table['lat'],rt_table['lon'])
rt_table['heading_rad'] = rt_table['heading']*2*pi/360.0
rt_table.loc[rt_table['heading_rad'] > pi,'heading_rad'] -= 2*pi 

ts_list = pd.unique(rt_table['bus_name'])
print('These vehicles were on route ',route_name,'on ',date,':')
print(ts_list)

fig = plt.figure(figsize = (20,6))
ax = fig.add_subplot(1, 1, 1)
ax.set_prop_cycle(color= cm.plasma(np.linspace(0, 1, len(ts_list))))
for sample_ts in ts_list:
    ts_table = rt_table.loc[rt_table['bus_name'] == sample_ts]
    
    direction = None  # initial direction unknown
    s = None
    pathgraph = [[],[]]
    
    print('Path calculation for ',sample_ts,' started!')
    for ind,ts_point in ts_table.iterrows():
        coords = np.array([ts_point['x'],ts_point['y']])
        # proxtable = list of proximities from the point to the route segments
        if ((direction == 0) or (direction == None)):
            prox,iprox = getdistance(coords,route[0])
            s = s_fwd[iprox] + dist(coords,route[0][iprox])                                
            if (((ts_point['speed'] > 5.0) or (direction == None))
            and (np.cos(ts_point['heading_rad'] - azimuth(route[0][iprox],route[0][iprox+1])) < 0)):
                # probably opposite direction
                prox,iprox = getdistance(coords,route[1])
                if (np.cos(ts_point['heading_rad'] - azimuth(route[1][iprox],route[1][iprox+1])) > 0):
                    direction = 1
                    s = s_bwd[iprox+1] + dist(coords,route[1][iprox+1])    
        elif (direction == 1):
            prox,iprox = getdistance(coords,route[1])
            s = s_bwd[iprox+1] + dist(coords,route[1][iprox+1])                                
            if ((ts_point['speed'] > 5.0)
            and (np.cos(ts_point['heading_rad'] - azimuth(route[1][iprox],route[1][iprox+1])) < 0)):
                # probably opposite direction
                prox,iprox = getdistance(coords,route[0])
                if (np.cos(ts_point['heading_rad'] - azimuth(route[0][iprox],route[0][iprox+1])) > 0):
                    direction = 0
                    s = s_fwd[iprox] + dist(coords,route[0][iprox])    
        else:
            print('Invalid direction = ', direction,', check the code')
        if  (dist(route[0][0],coords) < 0.05): # we are close to terminus 0
            direction = 0
            s = 0
        if  (dist(route[1][0],coords) < 0.05): # we are close to terminus 1
            direction = 1
            s = len_bwd
        if (prox > 0.25): # vehicle is far away from route
            directon = None
            s = None
        pathgraph[0].append(pd.to_datetime(ts_point['timestamp']))#[11:19])
        pathgraph[1].append(s)
    print('Path calculation finished!')
    #print(*pathgraph,sep = '\n') 
    ax.plot(pathgraph[0],pathgraph[1],'-',linewidth = 1, label = sample_ts)
print('Overall path calculation complete!')
import matplotlib.dates as mdates
#major ticks every hour
ax.xaxis.set_major_locator(mdates.HourLocator())
#minor ticks every 1/4 hour
ax.xaxis.set_minor_locator(mdates.MinuteLocator(byminute=(0,10,20,30,40,50)))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
ax.set_aspect(aspect = 0.01) #temporary
fig.autofmt_xdate()
ax.set_title(route_name+', '+date)
plt.legend(loc='upper left', bbox_to_anchor=(1.05, 1))
plt.show()
fig.savefig(route_name+' '+date+'.png', bbox_inches = 'tight', dpi = 500)