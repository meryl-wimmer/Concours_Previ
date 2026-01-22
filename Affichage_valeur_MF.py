#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Python script creating NetCDF file containing 1 variable
Author: Meryl WIMMER
"""

# -------------------------------
# PACKAGES
# -------------------------------

import xarray as xr
import cfgrib
import numpy as np
import os

import warnings
warnings.filterwarnings('ignore',category=DeprecationWarning)

from datetime import datetime, timedelta
def time2str(time,format_time):
    return time.strftime(format_time)
def str2time(time,format_time):
    return datetime.strptime(time, format_time)
def timeChangeFormat(time, format1, format2):
    return time2str(str2time(time, format1),format2)
def addtime(time, format_time,days=0, seconds=0, microseconds=0, milliseconds=0, minutes=0, hours=0, weeks=0):
    return datetime.strptime(time,format_time) + timedelta(days=days, seconds=seconds, microseconds=microseconds, milliseconds=milliseconds, minutes=minutes, hours=hours, weeks=weeks)


import argparse
parser=argparse.ArgumentParser(description="Python script to create netcdf file for each variable: python -m netcdf.create -m H51Y -v trr -r 2025090906 -i 2025090906 -f 2025091312 -s 3",formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument("-d","--date",      required=True,help='Date du run (YYMMDDHH)')
args=parser.parse_args()

root_MF="/cnrm/proc/wimmerm/data_MF/"

# ----------------------------------------------
# Liste de parmaètres
# ----------------------------------------------
param=['t2mMIN','t2mMAX','rr','visi']

# ----------------------------------------------
# Date
# ----------------------------------------------
run=args.date
step=1
cumulRR=24 #h

# ----------------------------------------------
# Blagnac
# ----------------------------------------------
lon_Blagnac=1.367778
lat_Blagnac=43.635

# ----------------------------------------------
# Loop over time step
# ----------------------------------------------
for i_model in ['arpege-4dvarfr','arome-3dvarfr','arome-ifsfr']:
  if i_model=='arpege-4dvarfr':
      model='arpege'
      vconf='4dvarfr'
      domaine='glob01'
  elif i_model=='arome-3dvarfr':
      model='arome'
      vconf='3dvarfr'
      domaine='eurw1s40'
  elif i_model=='arome-ifsfr':
      model='arome'
      vconf='ifsfr'
      domaine='eurw1s40'
  name_model=model+'-'+vconf
  

  # Noms des variables dans les gribs 
  if model=='arpege':
    grib_key=[{'shortName':'2t'},{'shortName':'2t'},[{'shortName':'lsrr'}, {'shortName':'crr'}],{'shortName':'minvis'}]
  else:
    grib_key=[{'shortName':'2t'},{'shortName':'2t'},{'parameterCategory':1,'parameterNumber':65},{'shortName':'minvis'}]


  for i_param,i_grib_key in zip(param,grib_key):
   # Définition des temps et noms des variables 
   if i_param=='t2mMIN':
        date_init=time2str(addtime(run,"%Y%m%d%H",hours=18),"%Y%m%d%H")
        date_fin=time2str(addtime(run,"%Y%m%d%H",days=1,hours=18),"%Y%m%d%H")
        T2mMIN=[]

   if i_param=='t2mMAX':
        date_init=time2str(addtime(run,"%Y%m%d%H",days=1,hours=6),"%Y%m%d%H")
        if model=='arpege':
            date_fin=time2str(addtime(run,"%Y%m%d%H",days=2,hours=0),"%Y%m%d%H")
        if model=='arome':
            date_fin=time2str(addtime(run,"%Y%m%d%H",days=2,hours=0),"%Y%m%d%H")
        T2mMAX=[]
   if i_param=='rr':
        date_init=time2str(addtime(run,"%Y%m%d%H",days=2,hours=0),"%Y%m%d%H")
        date_fin=time2str(addtime(run,"%Y%m%d%H",days=2,hours=0),"%Y%m%d%H")
        RR=[]
   if i_param=='visi':
        date_init=time2str(addtime(run,"%Y%m%d%H",days=1,hours=0),"%Y%m%d%H")
        date_fin=time2str(addtime(run,"%Y%m%d%H",days=2,hours=0),"%Y%m%d%H")
        MinVisi=[]

   I_ech=int((str2time(date_init,"%Y%m%d%H")-str2time(run,"%Y%m%d%H")).total_seconds()//3600)
   F_ech=int((str2time(date_fin,"%Y%m%d%H")-str2time(run,"%Y%m%d%H")).total_seconds()//3600)
   list_ech=list(range(max(cumulRR,I_ech),F_ech+1, int(step)))

   # Lecture des gribs
   for i_ech in list_ech:
     
    file= "/grid."+model+"-forecast."+domaine+"+"+str(i_ech).zfill(4)+":00.grib"
    file1="/grid."+model+"-forecast."+domaine+"+"+str(i_ech-cumulRR).zfill(4)+":00.grib"
    if model=='arpege' and i_param=='rr':
        datahs=xr.open_dataset(root_MF+name_model+'/'+timeChangeFormat(run,"%Y%m%d%H","%Y%m%dT%H%MP")+file,
                                engine="cfgrib",decode_timedelta=True,
                                backend_kwargs={'filter_by_keys': i_grib_key[0]})
        datah_1s=xr.open_dataset(root_MF+name_model+'/'+timeChangeFormat(run,"%Y%m%d%H","%Y%m%dT%H%MP")+file1,
                                engine="cfgrib",decode_timedelta=True,
                                backend_kwargs={'filter_by_keys': i_grib_key[0]})
        
        datahc=xr.open_dataset(root_MF+name_model+'/'+timeChangeFormat(run,"%Y%m%d%H","%Y%m%dT%H%MP")+file,
                                engine="cfgrib",decode_timedelta=True,
                                backend_kwargs={'filter_by_keys': i_grib_key[1]})
        datah_1c=xr.open_dataset(root_MF+name_model+'/'+timeChangeFormat(run,"%Y%m%d%H","%Y%m%dT%H%MP")+file1,
                                engine="cfgrib",decode_timedelta=True,
                                backend_kwargs={'filter_by_keys': i_grib_key[1]})
        list_data=[datahs-datah_1s,datahc - datah_1c]
        data1=xr.merge(list_data,compat='no_conflicts')
        data1['rr']=data1['lsrr']+data1['crr']
        
    elif model=='arome' and i_param=='rr':
        datahs=xr.open_dataset(root_MF+name_model+'/'+timeChangeFormat(run,"%Y%m%d%H","%Y%m%dT%H%MP")+file,
                                engine="cfgrib",decode_timedelta=True,
                                backend_kwargs={'filter_by_keys': i_grib_key})
        datah_1s=xr.open_dataset(root_MF+name_model+'/'+timeChangeFormat(run,"%Y%m%d%H","%Y%m%dT%H%MP")+file1,
                                engine="cfgrib",decode_timedelta=True,
                                backend_kwargs={'filter_by_keys': i_grib_key})
        data1=datahs-datah_1s 
        data1['rr']=data1['tirf']
    else:
         data1=xr.open_dataset(root_MF+name_model+'/'+timeChangeFormat(run,"%Y%m%d%H","%Y%m%dT%H%MP")+file,
                                engine="cfgrib",decode_timedelta=True,
                                backend_kwargs={'filter_by_keys': i_grib_key})
    # Lecture des Lon Lat
    lon=data1.longitude.data
    lat=data1.latitude.data

    # Distance entre points de grille et position de Blagnac et recherche du point de grille le plus proche
    lon_diff=np.abs(lon-lon_Blagnac)
    lat_diff=np.abs(lat-lat_Blagnac)
    i_lon=np.where(lon_diff==np.min(lon_diff))[0][0]
    i_lat=np.where(lat_diff==np.min(lat_diff))[0][0]

    # Valeur de T2m, RR et visibilité au point de grille le plus proche de Blagnac
    if i_param=='t2mMIN':
       T2mMIN.append(float(data1.t2m.data[i_lat,i_lon]) -273.15)
    if i_param=='t2mMAX':
       T2mMAX.append(float(data1.t2m.data[i_lat,i_lon]) -273.15)
    if i_param=='rr':
        RR=float(data1['rr'].data[i_lat,i_lon])
    if i_param=='visi':
       MinVisi.append(float(data1['minvis'].data[i_lat,i_lon]))

  # Affichage des T2m min, T2m max, RR24h, visibilité minimale     
  print(i_model,':')
  print('\tT2m min:',np.round(min(T2mMIN),2))
  print('\tT2m max:',np.round(max(T2mMAX),2))
  print('\tRR: ',np.round(RR,2))
  print('\tmin visi:',np.round(min(MinVisi),2),  'visibilité < 1000m ? : ', np.round(min(MinVisi),2)<1000)



