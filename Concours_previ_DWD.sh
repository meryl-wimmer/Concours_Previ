#!/usr/bin/bash

download=${1-1} # =1 par défaut, =0 si on ne veut pas télécharger les données
delete=${2-1} # = 1 par défaut, =0 si on veut supprimer les données


today=$(date +%Y%m%d) 

# Récupération des données
if [[ $download ==  1 ]]; then
  for model in icon icon-eu icon-d2;do
	if [ $model = "icon" ]; then
	   domaine=global
	   grid=icosahedral
  	   VAR_LON=CLON
	   var_lon=clon
	   VAR_LAT=CLAT
	   var_lat=clat
	   VAR_T2M=T_2M
	   VAR_RR=TOT_PREC
   	   VAR_VIS=VIS
   	   VAR_LPI=LPI_CON_MAX
	fi
        if [ $model = "icon-eu" ]; then
	   domaine=europe
	   grid=regular-lat-lon
	   VAR_LON=RLON
	   var_lon=rlon
	   VAR_LAT=RLAT
	   var_lat=rlat
	   VAR_T2M=T_2M
	   VAR_RR=TOT_PREC
   	   VAR_VIS=VIS
   	   VAR_LPI=LPI_CON_MAX
	fi
        if [ $model = "icon-d2" ]; then    
	   domaine=germany
	   grid=icosahedral
	   VAR_LON=000_0_clon
	   var_lon=clon
	   VAR_LAT=000_0_clat
	   var_lat=clat
	   VAR_T2M=2d_t_2m
	   VAR_RR=2d_tot_prec
	   VAR_VIS=2d_vis
   	   VAR_LPI=2d_lpi
	fi    
	echo $model $domaine
	i_ech=000

	# Lon Lat
	wget --no-proxy -r -np -nd -A "${model}_${domaine}_${grid}_time-invariant_${today}00_${VAR_LON}.grib2.bz2" https://opendata.dwd.de/weather/nwp/${model}/grib/00/${var_lon}/
	bzip2 -d ${model}_${domaine}_${grid}_time-invariant_${today}00_${VAR_LON}.grib2.bz2
	wget --no-proxy -r -np -nd -A "${model}_${domaine}_${grid}_time-invariant_${today}00_${VAR_LAT}.grib2.bz2" https://opendata.dwd.de/weather/nwp/${model}/grib/00/${var_lat}/
	bzip2 -d ${model}_${domaine}_${grid}_time-invariant_${today}00_${VAR_LAT}.grib2.bz2
        
        # Déplacement vers un dossier data_icon    
        mv icon* ./data_DWD/
        
        # T2m
	for i_ech in {018..054};do
	    wget --no-proxy -r -np -nd -A "${model}_${domaine}_${grid}_single-level_${today}00_${i_ech}_${VAR_T2M}.grib2.bz2" https://opendata.dwd.de/weather/nwp/${model}/grib/00/t_2m/
	    bzip2 -d ${model}_${domaine}_${grid}_single-level_${today}00_${i_ech}_${VAR_T2M}.grib2.bz2
            mv icon* ./data_DWD/
	done
	
	# RR
	for i_ech in {024..048..24};do
	    wget --no-proxy -r -np -nd -A "${model}_${domaine}_${grid}_single-level_${today}00_${i_ech}_${VAR_RR}.grib2.bz2" https://opendata.dwd.de/weather/nwp/${model}/grib/00/tot_prec/
	    bzip2 -d ${model}_${domaine}_${grid}_single-level_${today}00_${i_ech}_${VAR_RR}.grib2.bz2
            mv icon* ./data_DWD/
	done
	
	# Brouillard
	for i_ech in {024..048};do
	    wget --no-proxy -r -np -nd -A "${model}_${domaine}_${grid}_single-level_${today}00_${i_ech}_${VAR_VIS}.grib2.bz2" https://opendata.dwd.de/weather/nwp/${model}/grib/00/vis/
	    bzip2 -d ${model}_${domaine}_${grid}_single-level_${today}00_${i_ech}_${VAR_VIS}.grib2.bz2
            mv icon* ./data_DWD/
        done

        # LPI
	for i_ech in {024..048};do
	  if [[ $model == 'icon-eu' ]];then
	    wget --no-proxy -r -np -nd -A "${model}_${domaine}_${grid}_single-level_${today}00_${i_ech}_${VAR_LPI}.grib2.bz2" https://opendata.dwd.de/weather/nwp/${model}/grib/00/lpi_con_max/
	    bzip2 -d ${model}_${domaine}_${grid}_single-level_${today}00_${i_ech}_${VAR_LPI}.grib2.bz2
            mv icon* ./data_DWD/
	  fi
        done
  done
fi


# Lancement de Concours_previ_DWD.py
./Affichage_valeur_DWD.py -d ${today}00

# Delete temporary files
if [[ $delete == 1 ]];then
    rm -rf ./data_DWD/*
fi
