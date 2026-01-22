#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Python script to download forecasts data
Author: Meryl WIMMER
"""

from epygram.extra import usevortex as vtx
import os
from datetime import datetime, timedelta
def time2str(time,format_time):
    return time.strftime(format_time)
def str2time(time,format_time):
    return datetime.strptime(time, format_time)
def timeChangeFormat(time, format1, format2):
    return time2str(str2time(time, format1),format2)
def addtime(time, format_time,days=0, seconds=0, microseconds=0, milliseconds=0, minutes=0, hours=0, weeks=0):
    return datetime.strptime(time,format_time) + timedelta(days=days, seconds=seconds, microseconds=microseconds, milliseconds=milliseconds, minutes=minutes, hours=hours, weeks=weeks)


# To run in a terminal
import argparse
parser=argparse.ArgumentParser(description="Python script to plot download gribs:\n./Get_Olive.py -e H3UU -r 2025070100 -i 2025070111 -f 2025070112 -s 1 -m arpege -d glob01\n./Get_Olive.py -e OPER -R ARP -r 2025070100 -i 2025070111 -f 2025070112 -s 1 -m arpege -d glob01\n./Get_Olive.py -e OPER -R ARO -r 2025070100 -i 2025070111 -f 2025070112 -s 1 -m arpege -d eurw1s40",formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument("-e","--exp",           type=str,required=True,help='Exp Olive name or OPER)')
parser.add_argument("-R","--rename",        type=str,required=False,help='Rename OPER as ... (ARO, ARP, ...)')
parser.add_argument("-r","--dateR",         type=str,required=True,help='Run time (YYYYMMDDHH : 2025062400 : réseau)')
parser.add_argument("-s","--step",          type=str,required=True,help='Time step (in hour)')
parser.add_argument("-M","--model",         type=str,required=True,help='model (arome, arpege, ...)')
parser.add_argument("-c","--conf",          type=str,required=True,help='vconf (3dvarfr, 4dvarfr, pearp, ifsfr, ...)')
parser.add_argument("-d","--domain",        type=str,required=True,help='Domain (eurw1s40, glob01, lfa, ...)')
parser.add_argument("-m","--member",        type=str,required=False,help='Member number if PEARP')
args=parser.parse_args()

root_MF="/cnrm/proc/wimmerm/data_MF/"

# Olive name
exp_Olive=args.exp
if args.rename is not None:
    name=args.rename
else:
    name=args.exp

if args.member:
    member=args.member
    name=name+'_mb'+member.zfill(3)
else:
    member=None

# Model config
model=args.model
domaine=args.domain
vconf=args.conf

# Date
date=timeChangeFormat(args.dateR,'%Y%m%d%H','%Y%m%dT%H%MP')
dateI=addtime(args.dateR,'%Y%m%d%H',hours=18)
if model=='arpege':
    dateF=addtime(args.dateR,'%Y%m%d%H',days=2,hours=6)
if model=='arome':
    dateF=addtime(args.dateR,'%Y%m%d%H',days=2,hours=3)


I_ech=int((dateI-str2time(args.dateR,"%Y%m%d%H")).total_seconds()//3600)
F_ech=int((dateF-str2time(args.dateR,"%Y%m%d%H")).total_seconds()//3600)
liste_ech=list(range(I_ech,F_ech+1, int(args.step))) #[i for i in range(0, forecast_term+1,1)]
print(liste_ech)
print(dateI, I_ech)




# Folder where to store data
root_tmp=root_MF+name+"/"+date
os.system('mkdir -p'+root_tmp)

# Files name to get
if domaine!='lfa':
   gribname=f"grid."+model+"-forecast."+domaine+"+00[term].grib"

   if member==None:
       # Get data
       resource_grib = vtx.get_resources(experiment=exp_Olive, 
                                  date=date, 
                                  term=liste_ech,
                                  getmode='epygram',
                                  origin='hst',                                 
                                  model=model,
                                  cutoff="production",
                                  block='forecast',
                                  vapp=model, 
                                  vconf=vconf,
                                  geometry=domaine,
                                  kind='gridpoint',
                                  namespace='vortex.archive.fr', 
                                  nativefmt = 'grib',
                                  local=f"{str(root_tmp)}/{gribname}") 
   else:
       # Get data
       resource_grib = vtx.get_resources(experiment=exp_Olive, 
                                  date=date, 
                                  term=liste_ech,
                                  getmode='epygram',
                                  origin='hst',                                 
                                  model=model,
                                  cutoff="production",
                                  block='forecast',
                                  vapp=model, 
                                  vconf=vconf,
                                  member=int(member),
                                  geometry=domaine,
                                  kind='gridpoint',
                                  namespace='vortex.archive.fr', 
                                  nativefmt = 'grib',
                                  local=f"{str(root_tmp)}/{gribname}") 

else:
   gribname=f"historic.arpege.tl1798-c22+00[term]:00.fa"
   
   if member==None:
     # Get data
     resource_grib = vtx.get_resources(experiment=exp_Olive, 
                                  date=date, 
                                  term=liste_ech,
                                  getmode='epygram',
                                  origin='hst',                                 
                                  model=model,
                                  cutoff="production",
                                  block='forecast',
                                  vapp=model, 
                                  vconf=vconf,
                                  geometry='global1798',
                                  kind='historic', #gridpoint',
                                  namespace='vortex.archive.fr', 
                                  nativefmt = 'fa',
                                  local=f"{str(root_tmp)}/{gribname}") 
   else:
     # Get data
     resource_grib = vtx.get_resources(experiment=exp_Olive, 
                                  date=date, 
                                  term=liste_ech,
                                  getmode='epygram',
                                  origin='hst',                                 
                                  model=model,
                                  cutoff="production",
                                  block='forecast',
                                  vapp=model, 
                                  vconf=vconf,
                                  member=int(member),
                                  geometry='global1798',
                                  kind='historic', #gridpoint',
                                  namespace='vortex.archive.fr', 
                                  nativefmt = 'fa',
                                  local=f"{str(root_tmp)}/{gribname}") 

