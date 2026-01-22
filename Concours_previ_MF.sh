#!/usr/bin/bash

today=2026012200



# Récupération des gribs
for model in arome-3dvarfr arpege-4dvarfr arome-ifsfr;do
    if [[ $model == "arome-3"* ]]; then 
      ./Get_data_MF.py -e OPER -R $model -r $today -s 1 -M arome -c 3dvarfr -d eurw1s40
    fi 
    if [[ $model = "arome-if"* ]]; then 
      ./Get_data_MF.py -e OPER -R $model -r $today -s 1 -M arome -c ifsfr -d eurw1s40
    fi 
    if [[ $model = "arpege"* ]]; then 
      ./Get_data_MF.py -e OPER -R $model -r $today -s 1 -M arpege -c 4dvarfr -d glob01
    fi 
done

# Lancement de Concours_previ_MF.py
./Affichage_valeur_MF.py -d $today

