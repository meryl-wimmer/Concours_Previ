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




# ----------------------------------------------
# Liste de parmaètres
# ----------------------------------------------
param=['t2mMIN','t2mMAX','rr','visi']
grib_key=[{'shortName':'2t'},{'shortName':'2t'},{'shortName':'tp'},{'shortName':'vis'}]
  
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
for i_model in ['icon','icon-eu','icon-d2']:
  if i_model=='icon':
     grid='icosahedral'
     domaine='global'
     var_lon='CLON'
     var_lat='CLAT'
     param=['t2mMIN','t2mMAX','rr']
  elif i_model=='icon-eu':
     grid='regular-lat-lon'
     domaine='europe'
     var_lon='RLON'
     var_lat='RLAT'
     param=['t2mMIN','t2mMAX','rr','visi']
  elif i_model=='icon-d2':
     grid='icosahedral'
     domaine='germany'
     var_lon='000_0_clon'
     var_lat='000_0_clat'
     param=['t2mMIN','t2mMAX','rr','visi']



  for i_param,i_grib_key in zip(param,grib_key):
   # Définition des temps et noms des variables
   if i_param=='t2mMIN':
        if i_model=='icon' or i_model=='icon-eu':
           var='T_2M'
        if i_model=='icon-d2':
           var='2d_t_2m'           
        date_init=time2str(addtime(run,"%Y%m%d%H",hours=18),"%Y%m%d%H")
        date_fin=time2str(addtime(run,"%Y%m%d%H",days=1,hours=18),"%Y%m%d%H")
        T2mMIN=[]

   if i_param=='t2mMAX':
        if i_model=='icon' or i_model=='icon-eu':
           var='T_2M'
        if i_model=='icon-d2':
           var='2d_t_2m'
        date_init=time2str(addtime(run,"%Y%m%d%H",days=1,hours=6),"%Y%m%d%H")
        date_fin=time2str(addtime(run,"%Y%m%d%H",days=2,hours=0),"%Y%m%d%H")
        T2mMAX=[]
  
   if i_param=='rr':
        if i_model=='icon' or i_model=='icon-eu':
           var='TOT_PREC'
        if i_model=='icon-d2':
           var='2d_tot_prec'
        date_init=time2str(addtime(run,"%Y%m%d%H",days=2,hours=0),"%Y%m%d%H")
        date_fin=time2str(addtime(run,"%Y%m%d%H",days=2,hours=0),"%Y%m%d%H")
        RR=[]
   
   if i_param=='visi':
        if i_model=='icon' or i_model=='icon-eu':
           var='VIS'
        if i_model=='icon-d2':
           var='2d_vis'
        date_init=time2str(addtime(run,"%Y%m%d%H",days=1,hours=0),"%Y%m%d%H")
        date_fin=time2str(addtime(run,"%Y%m%d%H",days=2,hours=0),"%Y%m%d%H")
        MinVisi=[]

   I_ech=int((str2time(date_init,"%Y%m%d%H")-str2time(run,"%Y%m%d%H")).total_seconds()//3600)
   F_ech=int((str2time(date_fin,"%Y%m%d%H")-str2time(run,"%Y%m%d%H")).total_seconds()//3600)
   list_ech=list(range(max(cumulRR,I_ech),F_ech+1, int(step)))

   # Lecture des gribs 
   for i_ech in list_ech:

    file= './data_DWD/'+i_model+"_"+domaine+"_"+grid+'_single-level_'+run+'_'+str(i_ech).zfill(3)+"_"+var+".grib2"
    file1='./data_DWD/'+i_model+"_"+domaine+"_"+grid+'_single-level_'+run+'_'+str(i_ech-cumulRR).zfill(3)+"_"+var+".grib2"
    
    if i_param=='rr':
        datahs=xr.open_dataset(file,
                                engine="cfgrib",decode_timedelta=True,
                                backend_kwargs={'filter_by_keys': i_grib_key})
        datah_1s=xr.open_dataset(file1,
                                engine="cfgrib",decode_timedelta=True,
                                backend_kwargs={'filter_by_keys': i_grib_key})
        # décumul des pluies
        data1=datahs-datah_1s
        # renomme la variable de pluies en un nom plus explicite
        data1['rr']=data1['tp']
        
    else:
         data1=xr.open_dataset("./"+file,
                                engine="cfgrib",decode_timedelta=True,
                                backend_kwargs={'filter_by_keys': i_grib_key})

    # Lecture des Lon Lat
    file_lon='./data_DWD/'+i_model+'_'+domaine+'_'+grid+'_time-invariant_'+run+'_'+var_lon+'.grib2'
    if i_model=='icon' or i_model=='icon-d2':
        lon=xr.open_dataset(file_lon,engine="cfgrib",decode_timedelta=True,
                        backend_kwargs={'filter_by_keys':{'shortName':'tlon'}}).tlon.data
      #  lon=lon.tlon.data
    if i_model=='icon-eu':
        lon=xr.open_dataset(file_lon,engine="cfgrib",decode_timedelta=True,
                        backend_kwargs={'filter_by_keys':{'shortName':'lon'}}).lon.data
      #  lon=lon.lon.data

    file_lat='./data_DWD/'+i_model+'_'+domaine+'_'+grid+'_time-invariant_'+run+'_'+var_lat+'.grib2'
    if i_model=='icon' or i_model=='icon-d2':
        lat=xr.open_dataset(file_lat,engine="cfgrib",decode_timedelta=True,
                        backend_kwargs={'filter_by_keys':{'shortName':'tlat'}}).tlat.data
    if i_model=='icon-eu':
        lat=xr.open_dataset(file_lat,engine="cfgrib",decode_timedelta=True,
                        backend_kwargs={'filter_by_keys':{'shortName':'lat'}}).lat.data

    # Distance entre points de grille et position de Blagnac et recherche du point de grille le plus proche
    diff=(lon-lon_Blagnac)**2 + (lat-lat_Blagnac)**2
    if i_model!='icon-eu':
        i=np.where(diff==np.min(diff))[0][0]
    else:
        diff=(lon-lon_Blagnac)**2 + (lat-lat_Blagnac)**2
        index=np.where(diff==np.min(diff))
        i=index[0]
        j=index[1]

    # Valeur de T2m, RR et visibilité au point de grille le plus proche de Blagnac
    if i_param=='t2mMIN':
        if i_model=='icon' or i_model=='icon-d2':
            T2mMIN.append(float(data1.t2m.data[i]) -273.15)
        if i_model=='icon-eu':
            T2mMIN.append(float(data1.t2m.data[i,j]) -273.15)
    
    if i_param=='t2mMAX':
        if i_model=='icon' or i_model=='icon-d2':
            T2mMAX.append(float(data1.t2m.data[i]) -273.15)
        if i_model=='icon-eu':
            T2mMAX.append(float(data1.t2m.data[i,j]) -273.15)
    if i_param=='rr':
        if i_model=='icon':
            RR=float(data1['rr'].data[i])
        if i_model=='icon-d2':
            RR=float(data1['rr'].data[i][0])
        if i_model=='icon-eu':
            RR=float(data1['rr'].data[i,j])
    if i_param=='visi':
        if i_model=='icon-d2':
            MinVisi.append(float(data1['vis'].data[i]))
        if i_model=='icon-eu':
            MinVisi.append(float(data1['vis'].data[i,j]))

  # Affichage des T2m min, T2m max, RR24h, visibilité minimale
  print(i_model,':')
  print('\tT2m min:',np.round(min(T2mMIN),2))
  print('\tT2m max:',np.round(max(T2mMAX),2))
  print('\tRR: ',np.round(RR,2))
  if i_model=='icon-eu' or i_model=='icon-d2':
      print('\tmin visi:',np.round(min(MinVisi),2), 'visibilité < 1000m ? : ', np.round(min(MinVisi),2)<1000)



