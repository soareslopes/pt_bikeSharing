# -*- coding: utf-8 -*- """ Created on Tue Dec 13 16:45:34 2022  @author: Andre """

'''
00_OSMOSIS.py

Recortar dados PBF (OSM)

inputs:
    - Ficheiro PBF (GeoFabrik)
    - Utiliza o programa JAVA Osmosis
    --> download: https://github.com/openstreetmap/osmosis/releases/tag/0.48.3
    
Output:
    - ficheiro xxx.osm.pbf da área de estudo
    
'''
#%% Biblioteca
import subprocess


#%%######################################################
# Etapa 1
# INSTUÇÕES
# - Fazer download do Osmosis
# - Navegar para a pasta osmosis/bin
# - Mover o arquivo PBF original para esta pasta

#%%######################################################
# Etapa 2
# INPUTS
folder = 'G:/Drives compartilhados/MASTI/MASTI/Tasks/Task3_Impacts_ResourcesOpportunities/r5r/'
# Localização do programa Osmosis
osmosis_location = folder + 'osmosis-0.48.3/bin'
# PBF do país ou região - download do GeoFabrik
pbf_original = folder + '00_AML.osm.pbf'    

# definir as coordenadas do CROP
# bbox de Lisboa com buffer de 5km
top = 'top=38.85'
left = 'left=-9.28'
bottom = 'bottom=38.64'
right = 'right=-9.08'

# nome do ficheiro de saída
pbf_city_name = '00_Lisboa5k.osm.pbf'

#%%######################################################
# Etapa 3
# CORRER O CÓDIGO
# Correr este códico completo: 
subprocess.call([osmosis_location,'--read-pbf',
                 pbf_original , '--bounding-box',
                 top, left, bottom,right, '--wb',
                 pbf_city_name], shell=True)


'''FIM DO CÓDIGO'''