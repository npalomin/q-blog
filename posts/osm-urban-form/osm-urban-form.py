################
# import modules
################
#| label: import (in terminal) `python3 -m pip install <package> --user 

import osmnx as ox
import os
import matplotlib.pyplot as plt
import geopandas as gpd
import pandas as pd
import random
from ast import literal_eval
#from pyrosm import get_data

from IPython.display import Image

ox.config(log_console=False, use_cache=True)

####################
# read Google sheets
####################

# publish to web csv `https://docs.google.com/spreadsheets/d/1wzU-HD3poWfd7jDTK3w_88r5zHASDIrVTg5wGxEwESo/edit#gid=0a`
path = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vRywtZWBYrE0mtCEjsanD_IswTid2v8AoOT0D7RerV8G7tyNMxx0GvbVM6E8zH9tYkFzxaRRSczkIPv/pub?gid=0&single=true&output=csv'
cgsh = pd.read_csv(path)

# convert latlng to tuple
cgsh['latlng'] = [literal_eval(x) for x in cgsh['latlng']]

# capitalize names
cgsh['name'] = cgsh['name'].str.title()

# create list
listgsh = cgsh[['name','latlng']].values.tolist()
listgsh

# select cities
cities = []
cities = listgsh[0:3] + listgsh[15:16] + listgsh[23:28]

cities

#############
# definitions
#############

dist = 5000
tagsb = {'building': True}
tagss = {'footway': 'sidewalk'}
highways = {'highway':True}
bus = {'route':'bus'} # doesn't work with OSMnx

green = {'amenity':'grave_yard',
'landuse':['allotments', 'cemetery', 'farmland', 'forest', 'grass', 'greenfield', 'meadow', 'orchard', 'recreation_ground', 'village_green', 'vineyard'],
'leisure':['garden', 'golf_course', 'nature_reserve', 'park', 'pitch', 'stadium'],
'natural':['wood', 'scrub', 'health', 'grassland', 'wetland'],
'tourism':['camp_site']}

blue = {'water':True,'natural':['water','bay'], 'waterway':'canal'}

# https://taginfo.openstreetmap.org/keys/amenity#values
poi = {'amenity': True}

# colors
# https://matplotlib.org/3.5.0/_images/sphx_glr_named_colors_003.png
ecol1 = 'grey'
ecol2 = 'tomato'
ecol3 = 'yellowgreen'
ecol4 = 'chocolate'
ecol5 = 'lightsteelblue'

######
# test
######

# lima
mycity = cities[-1]
point = mycity[1]
name = mycity[0]

# Highways
Gp = ox.geometries_from_point(center_point = point, tags = highways, dist = 5000)
# select only 'linestring' features
Gp = Gp.loc[Gp['geometry'].geom_type=='LineString']
# reproject
Gp = Gp.to_crs("EPSG:3857")
# create point
# create df from tuple -> geodataframe
d = {'lat': [point[0]], 'lng': [point[1]]}
df = pd.DataFrame(d)
gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.lng, df.lat), crs='EPSG:4326')
# reproject
gdf = gdf.to_crs("EPSG:3857")
# buffer
gdfb = gdf.buffer(4850)
# bounding box
bbox = gdfb.total_bounds
# plot and save
fig, ax = plt.subplots(figsize=(8,8))
# Plot highways
Gp.plot(ax=ax, linewidth=0.3, edgecolor=ecol1)
# Plot point
gdf.plot(ax=ax)
# Plot buffer
gdfb.plot(ax=ax, alpha=0.2)

# limits
ax.set_xlim([bbox[0], bbox[2]])
ax.set_ylim([bbox[1], bbox[3]])

fig.tight_layout()
#plt.show()
plt.savefig("posts/osm-urban-form/img-test/{}.png".format(name), dpi = 200)

###################
# save cities plots
###################

# for row_num, city in enumerate(cities):
#     name, point = city
#     print(name)

# function that takes centre points (run in RStudio console)
for row_num, city in enumerate(cities):
    name, point = city
    
    # get data
    # Highways
    Gp = ox.geometries_from_point(center_point = point, tags = highways, dist = dist)
    # select only 'linestring' features
    Gp = Gp.loc[Gp['geometry'].geom_type=='LineString']
    # reproject
    Gp = Gp.to_crs("EPSG:3857")
    
    # Green
    Gb = ox.geometries_from_point(center_point = point, tags = green, dist = dist)
    # select all rows of element type "way" or "relation"
    Gb = Gb.loc[['way', 'relation']]
    # reproject
    Gb = Gb.to_crs("EPSG:3857")
    
    # Amenities
    Ga = ox.geometries_from_point(center_point = point, tags = poi, dist = dist)
    # select only 'point' features
    Ga = Ga.loc[Ga['geometry'].geom_type=='Point']
    # reproject
    Ga = Ga.to_crs("EPSG:3857")
    
    # Blue
    Gw = ox.geometries_from_point(center_point = point, tags = blue, dist = dist)
    # select except 'point' features
    Gw = Gw.loc[Gw['geometry'].geom_type!='Point']
    # reproject
    Gw = Gw.to_crs("EPSG:3857")
    
    # create point
    # create df from tuple -> geodataframe
    d = {'lat': [point[0]], 'lng': [point[1]]}
    df = pd.DataFrame(d)
    gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.lng, df.lat), crs='EPSG:4326')
    # reproject
    gdf = gdf.to_crs("EPSG:3857")
    # buffer
    gdfb = gdf.buffer(4850)
    
    # bounding box
    bbox = gdfb.total_bounds
    
    # plot and save
    fig, ax = plt.subplots(3,1,figsize=(8,24))

    # Plot Highways
    Gp.plot(ax=ax[0], linewidth=0.3, edgecolor=ecol1)
    ax[0].set_title(name)
    ax[0].axis('off')
    # limits
    ax[0].set_xlim([bbox[0], bbox[2]])
    ax[0].set_ylim([bbox[1], bbox[3]])
    
    # Plot Green & Blue
    Gb.plot(ax=ax[1], linewidth=0.1, edgecolor=ecol3, facecolor=ecol3)
    Gw.plot(ax=ax[1], linewidth=1, edgecolor=ecol5, facecolor=ecol5, alpha=1)
    #ax[1].set_title("green & blue")
    ax[1].axis('off')
    # limits
    ax[1].set_xlim([bbox[0], bbox[2]])
    ax[1].set_ylim([bbox[1], bbox[3]])
    
    # Plot amenities
    Ga.plot(ax=ax[2], alpha=0.3, markersize=0.6, color=ecol4)
    #ax[2].set_title("poi")
    ax[2].axis('off')
    # limits
    ax[2].set_xlim([bbox[0], bbox[2]])
    ax[2].set_ylim([bbox[1], bbox[3]])
    
    plt.axis('off')
    fig.tight_layout()
    #plt.show()
    #plt.savefig("img/{}.png".format(name), dpi = 300)
    plt.savefig("posts/osm-urban-form/img-test/{}.png".format(name), dpi = 300)
