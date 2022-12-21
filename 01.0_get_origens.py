# -*- coding: utf-8 -*- """ Created on Fri Dec 16 11:30:13 2022  @author: Andre """

'''
00_dados.py
OBJETIVO:
    Definir pontos origem e destino
    
        ETAPA 1:
            1A. Limites do concelho de LIsboa
            1B. LImites do buffer de 5km (para evitar efeito de borda)

        ETAPA 2:
            2A. Carregar destinos (ja construidos no script anterior)
            2B. LImitar POIS ao buffer de 5km de LIsboa
            
        ETAPA 3:
            Gerar pontos de ORIGEM: Grid de Hexagonos
            3A. Dentro de Lisboa (concelho)           - definir limite
            3B. Limitados a onde existem edifícios    - hexeagonsMin 

### INPUTS
# -> 01.3_Key_Value_DestType
# -> 00.1.0_pois_classificados.gpkg

### OUTPUTS
# -> '01.1_limiteLisboa.gpkg'           -> Borda geográfica do concelho de Lisboa
# -> '01.2_limiteLisboa_5k.gpkg'        -> Borda expandida (buffer de 5km)
# -> '01.3_pois_classified_5k.gpkg'     -> POIS classificados, limitados aos internos ao buffer de 5km
# -> '01.4_hexagonsLisboa.gpkg'         -> Grid de hexagons     
# -> '01.5_hexagonsLisboaMin.gpkg'      -> MINIMIZADO - HExagonos apenas onde existem edifícios
'''   
#%% Carregar as bibliotecas

import geopandas
import pandas as pd
import h3pandas
import osmnx as ox
import r5py

#%% Ler os ficheiro locais
#Definir a pasta de trabalho
folder = 'G:/Drives compartilhados/MASTI/MASTI/Tasks/Task3_Impacts_ResourcesOpportunities/pasta_nova/'

#%%######################################################
#########################################################
#########################################################
# Etapa 1 . LIMITES GEOGRÁFICOS
#########################################################

#%%
'''A'''

# Limites da cidade
localidade = 'Lisboa, Portugal'
#### LIMITES da cidade
# Pegar o limite de um lugar dentro do OSM
limite = ox.geocode_to_gdf(localidade)
limite = limite[['bbox_north', 'bbox_south', 'bbox_east', 'bbox_west','geometry']]

# --> Guardar ficheiro local
# limite.to_file(folder + '01.1_limiteLisboa.gpkg', driver='GPKG')
del localidade

#%% 
'''B'''

# Buffer de 5km ao redor de lisboa (para evitar efeito de borda)
buffer = limite.buffer(0.05)
limite5k = geopandas.GeoDataFrame()
limite5k['geometry'] = buffer

# Guardar ficheiro local
# limite5k.to_file(folder + '01.2_limiteLisboa_5k.gpkg', driver='GPKG')
del buffer

###########
###########
# read file
# limite5k = geopandas.read_file(folder + '01.2_limiteLisboa_5k.gpkg')

#%%######################################################
#########################################################
#########################################################
# Etapa 2 - DESTINOS
#########################################################
'''A'''

# Carregar os DESTINOS
# ler de ficheiro local
pois = geopandas.read_file(folder + '00.1.0_pois_classificados.gpkg')



'''B'''

# Limitar aos POIS dentro do limite de Lisboa 5km
pois5k = geopandas.sjoin(pois, limite5k, how='inner')
#Guardar Ficheiro
pois5k = pois5k[['osmid', 'Key_Value', 'Type', 'geometry']]
pois5k = geopandas.GeoDataFrame(pois5k)
# pois5k.to_file(folder + '01.3_pois_classified_5k.gpkg', driver='GPKG')

###########
###########
# ler ficheir local
# pois5k = geopandas.read_file(folder + '01.3_pois_classified_5k.gpkg')

#%%######################################################
#########################################################
#########################################################
# Etapa 3
#########################################################
'''A'''

# GERAR PONTOS DE ORIGENS
# Gerar hexagonos dentro do limite da cidade
hexagons = limite.h3.polyfill_resample(resolution = 10) 
'''
DOCUMENTAÇÃO:
Informação sobre o hexagonos (H3). Numero de hesagonos (origens)
a depender do limite geográfico e da resolução
-----
Resolução 9 tem 175m de lateral e "raio"
Resolução 10 tem 66m de lateral e "raio"
-----
AML           --> 30921 hexagonos (res 9)
AML_sem rio   --> 25889 hexagonos (res 9) |  3685 hex (res 8)
Lisboa        --> 750 hexagonos (res 9)   |  5240 hex (res 10)
'''
# limitar número de colunas no DF
hexagons = hexagons.reset_index()
hexagons = hexagons[['h3_polyfill', 'geometry']]

# Guardar ficheiro
# hexagons.to_file(folder + '01.4_hexagonsLisboa.gpkg', driver='GPKG')

#%%
'''B'''

# # Limitar os hexagonos a aqueles que contem edifícios
# Corrigir o DF dos POIS
filtro = {"building": True}
poisAll = ox.geometries_from_bbox(limite.geometry.bounds['maxy'][0],
                                  limite.geometry.bounds['miny'][0],
                                  limite.geometry.bounds['maxx'][0],
                                  limite.geometry.bounds['minx'][0],
                                  filtro)
poisAll['geometry'] = poisAll['geometry'].centroid
poisAll = poisAll[['name','geometry']]
# Unir hexagonos com POIS
hexagonsMin = geopandas.sjoin(hexagons, poisAll, how='inner')
hexagonsMin = hexagonsMin.drop_duplicates('h3_polyfill')

# Guaredar ficheiro 
# hexagonsMin.to_file(folder + '01.5_hexagonsLisboaMin.gpkg', driver='GPKG')

    
'''FIM DO CÓDIGO'''