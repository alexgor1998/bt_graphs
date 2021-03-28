# -*- coding: utf-8 -*-
"""
Created on Tue Mar 23 18:04:41 2021
@author: Alex
"""

import json

def in_dict(key, dict):
    return key in dict
result = []
i = 0
f1 = open('routes.geojson', 'r', encoding='utf-8')
data = json.load(f1)
for feature in data['features']:
    if ((in_dict('ref', feature['properties']) == True)
        and (feature['properties']['ref'] == '5')
        and (feature['properties']['route'] == 'tram')):
        result.append(feature['properties'])
        
print(result)
