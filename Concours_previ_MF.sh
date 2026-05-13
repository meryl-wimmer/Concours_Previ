#!/usr/bin/bash
todo=${1-1} # =1 par défaut, sinon =0, dans ce cas, on ne fait que l'affichage
delete=${2-1} # =1 par défaut, sion =0, dans ce cas, on supprime les data


today=$(date +%Y%m%d)00

# Récupération des gribs
if [[ $todo == 1 ]]; then
  for model in arome-3dvarfr arpege-4dvarfr arome-ifsfr;do
    if [[ $model == "arome-3"* ]]; then 
      ./Get_data_MF.py -e OPER -R $model -r $today -s 1 -M arome -c 3dvarfr -d eurw1s40
    fi 
    if [[ $model = "arome-if"* ]]; then 
      ./Get_data_MF.py -e OPER -R $model -r $today -s 1 -M arome -c ifsfr -d eurw1s40
    fi 
    if [[ $model = "arpege"* ]]; then 
      ./Get_data_MF.py -e OPER -R $model -r $today -s 1 -M arpege -c 4dvarfr -d glob01
      ./Get_data_MF.py -e OPER -R $model -r $today -s 1 -M arpege -c 4dvarfr -d glob025
    fi 
  done
fi


# Lancement de Concours_previ_MF.py
./Affichage_valeur_MF.py -d $today

# Delete temporary files
if [[ $delete == 1 ]]; then
  rm -rf ./data_MF/*
fi


