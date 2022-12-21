# -*- coding: utf-8 -*- """ Created on Fri Dec 16 11:30:13 2022  @author: Andre """

'''
02.0_count_POIS.py
OBJETIVO:
    Contar o numero de POIS dentor de cada hexagono
    
        ETAPA 1:
            1A. Definir ehexagonos
            1B. Conta POIS


### INPUTS
# -> 01.2_limiteLisboa_5k.gpkg
# -> 00.1.0_pois_classificados.gpkg

### OUTPUTS 
# -> '02.1_HexagonsPOIScount.gpkg'      -> Hexagonso de destino apenas onde existem POIS (contegem por tipo de POIS)
'''   
#%% Carregar as bibliotecas

import geopandas
import pandas as pd
import h3pandas
import warnings
warnings.filterwarnings("ignore")

#%% INPUTS
folder = 'G:/Drives compartilhados/MASTI/MASTI/Tasks/Task3_Impacts_ResourcesOpportunities/pasta_nova/'
limite5k    = geopandas.read_file(folder + '01.2_limiteLisboa_5k.gpkg')
pois        = geopandas.read_file(folder + '00.1.0_pois_classificados.gpkg')

#%%#%%######################################################
#########################################################
#########################################################
# Etapa 1 - contar DESTINOS dentro de hexagonos
#########################################################

# definir os hexagonos de destino
'''A'''

# Contar POIS dentro dos hexagonos de DESTINOS
osm_types = ['Education','Supermarket','Healthcare','Sports','Culture','Parks','Eating','Retail','Religious','PublicServices']

# Criar hexagonos dentro do limite de 5km
hexagons_dest = limite5k.h3.polyfill_resample(resolution = 10)
pois['geometry'] = pois['geometry'].centroid

# minimizar contagem de hexagonos
hexagons_dest = geopandas.sjoin(hexagons_dest, pois, how='inner')
hexagons_dest = hexagons_dest.reset_index()
# excluir duplicatas
hexagons_dest = hexagons_dest.drop_duplicates('h3_polyfill')
hexagons_dest = hexagons_dest[['h3_polyfill', 'geometry']]

# Ordenar colunas
hexagons_dest[['Education','Supermarket','Healthcare','Sports','Culture','Parks','Eating','Retail','Religious','PublicServices']] = ''
hexagons_dest = hexagons_dest[['h3_polyfill','Education', 'Supermarket','Healthcare', 'Sports', 'Culture',
               'Parks', 'Eating', 'Retail','Religious', 'PublicServices', 'geometry']]

# Contar os pois dentro de cada hexagono
'''B'''
# i = 0
for i in range(len(osm_types)):
    # filtrar pois
    # "+1" já que os Types (dentro do df 'POIS') começam em 1, e não em 0
    df = pois[pois['Type'] == i+1].copy() 
    # Adicionar aos POIS em quais hexagonos eles se encontram
    df_join = geopandas.sjoin(hexagons_dest, df, how='inner')
    # criar um valor fixo para cada POIS
    df_join['count'] = 1
    # Agrupar os POIS segundo os Hexagonos em que se encontram e contar quanto estão lá dentro
    df_group = df_join.groupby(by='h3_polyfill').sum()
    df_group = df_group.reset_index()
    df_group = df_group[['h3_polyfill', 'count']]
    # associar a contagem ao Type      
    hexagons_dest = hexagons_dest.merge(df_group, left_on='h3_polyfill', right_on='h3_polyfill', how='left')
    hexagons_dest[osm_types[i]] = hexagons_dest['count'].fillna(0)
    hexagons_dest = hexagons_dest[['h3_polyfill','Education', 'Supermarket','Healthcare', 'Sports', 'Culture',
                   'Parks', 'Eating', 'Retail','Religious', 'PublicServices', 'geometry']]
    del df_join, df_group, df

# Guardar em ficheiro
hexagons_dest.to_file(folder + '02.1_HexagonsPOIScount.gpkg', driver='GPKG')

    
'''FIM DO CÓDIGO'''