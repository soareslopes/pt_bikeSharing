# -*- coding: utf-8 -*- """ Created on Tue Dec 20 16:35:30 2022  @author: Andre """

#%%
'''
00.1_get_destinations_OSM.py

Capturar POIS a partir da net

ETAPA única:
    INPUTS:
        (1) GeoDataFrame com o limite da área que se pretende capturar.
        
        (2) tags do OMS para servidem de filtro:
            address to a csv file with ';' as the separator
            This script was designed to operate with the "Key_Value_Type_Final.csv" file
            
    OUTPUT:
        (1) GeoDataFrame com os destinos classificados
    
'''

#%% Bibliotecas
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import osmnx as ox
import time

import warnings
warnings.filterwarnings("ignore")

#%% INPUTS

csv_tags = 'G:/Drives compartilhados/MASTI/MASTI/Tasks/Task3_Impacts_ResourcesOpportunities/pasta_nova/00.1.1_Key_Value_DestType.csv'
pbf_file = 'G:/Drives compartilhados/MASTI/MASTI/Tasks/Task3_Impacts_ResourcesOpportunities/pasta_nova/00_AML.osm.pbf'
city = gpd.read_file('G:/Drives compartilhados/MASTI/MASTI/Tasks/Task3_Impacts_ResourcesOpportunities/pasta_nova/01.2_limiteLisboa_5k.gpkg')

destinations = get_destinations(csv_tags, city)

# Guardar em ficheiro local
folder = 'G:/Drives compartilhados/MASTI/MASTI/Tasks/Task3_Impacts_ResourcesOpportunities/pasta_nova/'
destinations.to_file(folder + '00.1.0_pois_classificados.gpkg', driver='GPKG')

#%% Função
def get_destinations(csv_tags, city):
    
    """
    Obtains destinations from the osm.pbf file for the country.

    Parameters
    ----------
    csv_tags : address to a csv file with ';' as the separator
        This script was designed to operate with the "Key_Value_Type_Final.csv" file
      
    city : geodataframe with one row
        This function is intended to be applied within a iterrows method

    Returns
    -------
    dataframe with points
        dataframe has lat and long for each point
    geodataframe 
        dataframe with polygons depicting green areas > 1 Ha

    """

    #########################################################################################
    # Get list of relevant OSM tags
    df_keyvalue = pd.read_csv(csv_tags, sep=';')
        # listagem de valores considerados como tipo 1 a 10
    # Excluir os zeros (para ignorar)
    df_keyvalue = df_keyvalue.loc[df_keyvalue['Type'] > 0]
        
    print ('Getting destinations from the OSM api...')    
    start_cycle = time.time()

    ##############################################    
    ##############################################    
    ##############################################
    ##### 1  - AMENITIES #####
    print ('Getting Amenities...')
    filtro = {"amenity": True} 
    # PYROSM    
    # pois_all = osm_parser.get_pois(custom_filter=filtro)
    # OSMNX
    pois_all = ox.geometries_from_bbox(city.geometry.bounds['maxy'][0],
                                       city.geometry.bounds['miny'][0],
                                       city.geometry.bounds['maxx'][0],
                                       city.geometry.bounds['minx'][0],
                                       filtro)
    
    
    # public pois
    # pois = pois_all[~pois_all['tags'].str.contains('"access":"private"|"access":"customers"|"access":"no"', na = False)]
    pois = pois_all[(pois_all['access'] != 'private') & (pois_all['access'] != 'customers') & (pois_all['access'] != 'no')]
    pois = pois.reset_index()

    # Classificar os pois
    if pois.empty:
        pois['Key_Value'] =  "none"
    else:
        pois['Key_Value'] =  "amenity|" + pois['amenity']

    # juntar os types
    pois = pois.merge(df_keyvalue, how='left', on='Key_Value')

    # mandar fora os que não interessam (sem type) # drop nulls
    pois = pois[pois.Type.notnull()]
    
    # mandar fora as linhas (são erros)
    pois = pois.loc[pois.geom_type !='LineString'] # são pontos, poligonos e multipoligonos
    pois = pois.loc[pois.geom_type !='MultiLineString'] # são pontos, poligonos e multipoligonos

    # limpar colunas    
    pois = pois[['osmid','name','Key_Value', 'Type', 'Type_Name', 'geometry']]
    # dar o codigo osmid
    # pois.rename(columns = {'id':'osmid'}, inplace = True)    
    
    # ficar com os polígonos e multipolygons (os quais vamos transformar em centroids, para verificar no final)
    polygons = pois.loc[pois.geom_type !='Point'] # poligonos e multipoligonos
    
    # final destinations (points)
    #   calculate centroids for all (points, polygons e multipolygons)
    dest_am = pois.copy()
    dest_am['lon'] = pois['geometry'].centroid.x
    dest_am['lat'] = pois['geometry'].centroid.y
    
    # apagar coluna geometry
    # dest_am = dest_am.drop(['geometry'], axis = 1)
    
    # #drop nulls
    dest_am = dest_am[dest_am.lat.notnull()]
    print('possible destinations: ' + str(dest_am['lat'].count()))
   
    # polygons.to_file('/Volumes/GoogleDrive/Shared drives/Cidade15min/temp/polys_am.gpkg')
    # dest_am.to_csv('/Volumes/GoogleDrive/Shared drives/Cidade15min/temp/amenities_points.csv')



    ##############################################    
    ##############################################        
    ##############################################    
    ##### 2 - LEISURE #####
    print ('Getting Leisure...')
    filtro = {"leisure": True}
    # pois_all = osm_parser.get_pois(custom_filter=filtro)
    # OSMNX
    pois_all = ox.geometries_from_bbox(city.geometry.bounds['maxy'][0],
                                       city.geometry.bounds['miny'][0],
                                       city.geometry.bounds['maxx'][0],
                                       city.geometry.bounds['minx'][0],
                                       filtro)
    
    # public pois
    # pois = pois_all[~pois_all['tags'].str.contains('"access":"private"|"access":"customers"|"access":"no"', na = False)]
    pois = pois_all[(pois_all['access'] != 'private') & (pois_all['access'] != 'customers') & (pois_all['access'] != 'no')]
    pois = pois.reset_index()
    
    # Classificar os pois
    if pois.empty:
        pois['Key_Value'] =  "none"
    else:
        pois['Key_Value'] =  "leisure|" + pois['leisure']

    # juntar os types
    pois = pois.merge(df_keyvalue, how='left', on='Key_Value')

    # mandar fora os que não interessam (sem type)
    #drop nulls
    pois = pois[pois.Type.notnull()]

    # mandar fora as linhas (são erros)
    pois = pois.loc[pois.geom_type !='LineString'] # são pontos, poligonos e multipoligonos
    pois = pois.loc[pois.geom_type !='MultiLineString'] # são pontos, poligonos e multipoligonos


    # limpar colunas
    # no caso do leisure, há casos de cidades onde todos são poligonos, pelo que não
    # tem colunas lat e lon    
    # pois = pois[['id','lat','lon','name','Key_Value', 'Type', 'Type_Name', 'geometry']]
    pois = pois[['osmid','name','Key_Value', 'Type', 'Type_Name', 'geometry']]


    # dar o codigo osmid
    pois.rename(columns = {'id':'osmid'}, inplace = True)    
    
    ##########
    #### No caso específico dos leisure, há muitas piscinas que passam por não estarem classificads
    #### como privadas, pelo que iremos mandar fora calculando a área

    # reprojetar para calcular area
    pois = pois.to_crs({'init': 'epsg:3035'}) # project geodataframe to ETRS89-extended
    pois['area_poly'] = pois['geometry'].area
    
    # voltar a WGS84
    pois = pois.to_crs({'init': 'epsg:4326'}) # project geodataframe to WGS84

    
    # pois = pois[pois.area_poly != 0] # pontos
    # pois.to_file('/Volumes/GoogleDrive/Shared drives/Cidade15min/temp/pois2.gpkg')
    
    # piscinas com mais de 500 m2 (publicas)
    pois['remove'] = ((pois.area_poly < 500) & (pois.Key_Value == 'leisure|swimming_pool'))
    pois = pois[pois['remove'] == False]    

    # gardens com mais de 2000 m2
    pois['remove'] = ((pois.area_poly < 2000) & (pois.Key_Value == 'leisure|garden'))
    pois = pois[pois['remove'] == False]   
    
    # parques com mais de 2000 m2
    pois['remove'] = ((pois.area_poly < 2000) & (pois.Key_Value == 'leisure|park'))
    pois = pois[pois['remove'] == False]   
    
    # nature_reserve com mais de 2000 m2
    pois['remove'] = ((pois.area_poly < 2000) & (pois.Key_Value == 'leisure|nature_reserve'))    
    pois = pois[pois['remove'] == False]        
    
    ##########
    
    # ficar com os polígonos e multipolygons (para verificar no final)
    polys = pois.loc[((pois.geom_type == 'Polygon') | (pois.geom_type == 'MultiPolygon'))] # poligonos e multipoligonos
       
    # juntar aos poligonos anteriores
    polygons = pd.concat([polygons,polys])
    # apagar eventuais repetidos
    polygons = polygons.loc[~polygons.osmid.duplicated(), :]
   
    #drop nulls
    dest_ls = pois.copy()
    dest_ls['lon'] = pois['geometry'].centroid.x
    dest_ls['lat'] = pois['geometry'].centroid.y
    
    # #drop nulls
    dest_ls = dest_ls[dest_ls.lat.notnull()]
    print('possible destinations: ' + str(dest_ls['lat'].count()))
       
    
    
    ##############################################    
    ##############################################    
    ##############################################    
    ##### 3 - SHOP #####
    print ('Getting Shop...')
    filtro = {"shop": True}
    # pois_all = osm_parser.get_pois(custom_filter=filtro)
    # OSMNX
    pois_all = ox.geometries_from_bbox(city.geometry.bounds['maxy'][0],
                                       city.geometry.bounds['miny'][0],
                                       city.geometry.bounds['maxx'][0],
                                       city.geometry.bounds['minx'][0],
                                       filtro)
    
    # public pois
    # pois = pois_all[~pois_all['tags'].str.contains('"access":"private"|"access":"customers"|"access":"no"', na = False)]
    pois = pois_all[(pois_all['access'] != 'private') & (pois_all['access'] != 'customers') & (pois_all['access'] != 'no')]
    pois = pois.reset_index()

    # classificar
    if pois.empty:
        pois['Key_Value'] =  "none"
    else:
        pois['Key_Value'] =  "shop|" + pois['shop']

    # juntar os types
    pois = pois.merge(df_keyvalue, how='left', on='Key_Value')

    # mandar fora os que não interessam (sem type)
    #drop nulls
    pois = pois[pois.Type.notnull()]

    # mandar fora as linhas (são erros)
    pois = pois.loc[pois.geom_type !='LineString'] # são pontos, poligonos e multipoligonos
    pois = pois.loc[pois.geom_type !='MultiLineString'] # são pontos, poligonos e multipoligonos

    # limpar colunas    
    pois = pois[['osmid','name','Key_Value', 'Type', 'Type_Name', 'geometry']]  
    
    # ficar com os polígonos e multipolygons (para verificar no final)
    polys = pois.loc[((pois.geom_type == 'Polygon') | (pois.geom_type == 'MultiPolygon'))] # poligonos e multipoligonos
       
    # juntar aos poligonos anteriores
    polygons = pd.concat([polygons,polys])
    # apagar eventuais repetidos
    polygons = polygons.loc[~polygons.osmid.duplicated(), :]

    #calculate centroids for polygons
    dest_sh = pois.copy()
    dest_sh['lon'] = pois['geometry'].centroid.x
    dest_sh['lat'] = pois['geometry'].centroid.y
   
    # #drop nulls
    dest_sh = dest_sh[dest_sh.lat.notnull()]
    print('possible destinations: ' + str(dest_sh['lat'].count()))
    
    
    ##############################################    
    ##############################################    
    ##############################################
    ##### 4 - TOURISM #####
    print ('Getting Tourism...')
    filtro = {"tourism": True}
    # pois_all = osm_parser.get_pois(custom_filter=filtro)
    # OSMNX
    pois_all = ox.geometries_from_bbox(city.geometry.bounds['maxy'][0],
                                       city.geometry.bounds['miny'][0],
                                       city.geometry.bounds['maxx'][0],
                                       city.geometry.bounds['minx'][0],
                                       filtro)
    
    # public pois
    # pois = pois_all[~pois_all['tags'].str.contains('"access":"private"|"access":"customers"|"access":"no"', na = False)]
    pois = pois_all[(pois_all['access'] != 'private') & (pois_all['access'] != 'customers') & (pois_all['access'] != 'no')]
    pois = pois.reset_index()

    # classificar
    if pois.empty:
        pois['Key_Value'] =  "none"
    else:
        pois['Key_Value'] =  "tourism|" + pois['tourism']

    # juntar os types
    pois = pois.merge(df_keyvalue, how='left', on='Key_Value')

    # mandar fora os que não interessam (sem type)
    #drop nulls
    pois = pois[pois.Type.notnull()]

    # mandar fora as linhas (são erros)
    pois = pois.loc[pois.geom_type !='LineString'] # são pontos, poligonos e multipoligonos
    pois = pois.loc[pois.geom_type !='MultiLineString'] # são pontos, poligonos e multipoligonos

    # limpar colunas    
    pois = pois[['osmid','name','Key_Value', 'Type', 'Type_Name', 'geometry']]  
    
    # ficar com os polígonos e multipolygons (para verificar no final)
    polys = pois.loc[((pois.geom_type == 'Polygon') | (pois.geom_type == 'MultiPolygon'))] # poligonos e multipoligonos
       
    # juntar aos poligonos anteriores
    polygons = pd.concat([polygons,polys])
    # apagar eventuais repetidos
    polygons = polygons.loc[~polygons.osmid.duplicated(), :]
 
    # #calculate centroids for polygons
    dest_to = pois.copy()
    dest_to['lon'] = pois['geometry'].centroid.x
    dest_to['lat'] = pois['geometry'].centroid.y
    
    # #drop nulls
    dest_to = dest_to[dest_to.lat.notnull()]
    print('possible destinations: ' + str(dest_to['lat'].count()))


    ##############################################    
    ##############################################    
    ##############################################
    ##### 5 - BUILDINGS #####    
    print ('Getting Buildings...')
    filtro = {"building": True}
    # pois_all = osm_parser.get_pois(custom_filter=filtro)
    # OSMNX
    pois_all = ox.geometries_from_bbox(city.geometry.bounds['maxy'][0],
                                       city.geometry.bounds['miny'][0],
                                       city.geometry.bounds['maxx'][0],
                                       city.geometry.bounds['minx'][0],
                                       filtro)
    
    # public pois
    # pois = pois_all[~pois_all['tags'].str.contains('"access":"private"|"access":"customers"|"access":"no"', na = False)]
    pois = pois_all[(pois_all['access'] != 'private') & (pois_all['access'] != 'customers') & (pois_all['access'] != 'no')]
    pois = pois.reset_index()
    
    # ficar apenas com os polígonos
    pois = pois.loc[pois.geom_type =='Polygon']
    
    # clear duplicates from previous tags
    pois = pois[pois['amenity'].isnull()]
    # no leisure is included in buildings
    pois = pois[pois['shop'].isnull()]
    # no tourism is included in buildings

    
    # classificar
    if pois.empty:
        pois['Key_Value'] =  "none"
    else:
        pois['Key_Value'] =  "building|" + pois['building']

    pois = pois.merge(df_keyvalue, how='left', on='Key_Value') 

    # mandar fora os que não interessam (sem type)
    pois = pois[pois.Type.notnull()]
    
    # limpar colunas    
    # pois = pois[['id','lat','lon','name','Key_Value', 'Type', 'Type_Name', 'geometry']]
    
    # TEMP (Há casos onde os pois não têm os campos lat e lon)
    pois = pois[['osmid','name','Key_Value', 'Type', 'Type_Name', 'geometry']]

    # transformar em centroids para ser mais rapida a análise espacial
    pois_centroids = pois.copy()
    pois_centroids['geometry'] = pois_centroids['geometry'].representative_point()

    # selecionar os que não estão dentro de algum poligono já transformado em centroid
    pois_spatialjoin = gpd.sjoin(pois_centroids, polygons, how="left")
    
    # se o ponto tiver dentro de um polígono da mesma classe, apaga (fica só com os isolados de classes distintas)
    pois_spatialjoin['remove'] = (pois_spatialjoin['Type_left'] == pois_spatialjoin['Type_right'])
    
    # há casos onde o ponto pode estar dentro de 2 poligonos (jardim do IST e IST por exemplo)
    # nesse caso, se for true para um, corrigir para o outro 
    duplicateRows_a = pois_spatialjoin[pois_spatialjoin.duplicated(['osmid_left'])]
    duplicateRows_b = pois_spatialjoin[pois_spatialjoin.duplicated(['osmid_left'], keep='last')]
    
    # se remove for true em qq 1 dos dois, deve sair
    remover_lista_a = duplicateRows_a['osmid_left'][duplicateRows_a['remove']]
    remover_lista_b = duplicateRows_b['osmid_left'][duplicateRows_b['remove']]
    
    remover_lista = pd.concat([remover_lista_a,remover_lista_b])
    del duplicateRows_a, duplicateRows_b
    del remover_lista_a, remover_lista_b
 
    # apagar duplicados (acontece porque há edificios que estão dentro de 2 polígonos do mesmo Type)
    remover_lista.drop_duplicates(inplace = True)
    remove = pd.DataFrame(remover_lista)    
    remove['remove2'] = True
    
    # retirar os que foram identificados como a retirar
    # join tabela de remove
    pois_spatialjoin = pois_spatialjoin.merge(remove, left_on='osmid_left', right_on='osmid_left', how = 'left')
    del remover_lista, remove   
    
    # apagar os que não interessam
    pois_bd = pois_spatialjoin[pois_spatialjoin['remove2'] != True]  
    pois_bd = pois_bd[pois_bd['remove'] != True]  

    # centroids
    dest_bd = pois_bd.copy()
    dest_bd['lon'] = pois_bd['geometry'].centroid.x
    dest_bd['lat'] = pois_bd['geometry'].centroid.y
    
    # # limpar colunas
    # # dest_bd = dest_bd[['lat','lon','name','Key_Value', 'Type', 'Type_Name', 'Subtype', 'SubType_Name']]
    dest_bd = dest_bd[['lat','lon','name_left','Key_Value_left', 'Type_left', 'Type_Name_left']]

    # renomear as colunas
    dest_bd.columns = ['lat','lon','name','Key_Value', 'Type', 'Type_Name']
    
    #drop nulls
    dest_bd = dest_bd[dest_bd.lat.notnull()]
    # gdf = gpd.GeoDataFrame(dest_bd, geometry=gpd.points_from_xy(dest_bd.lon, dest_bd.lat))
    
    print('possible destinations: ' + str(dest_bd['lat'].count()))
   
         
    frames = [dest_am, dest_bd, dest_ls, dest_sh, dest_to]
    destinations = pd.concat(frames)
    destinations = destinations[['osmid', 'name', 'Key_Value', 'Type', 'Type_Name', 'geometry']]
    
    print('Total:')
    print('possible destinations: ' + str(destinations['Type'].count()))
    
    end_cycle = time.time()
    
    totaltime = end_cycle - start_cycle
    ty_res = time.gmtime(totaltime)
    res = time.strftime("%H:%M:%S",ty_res)
    
    print(f'total running time to obtain POIs: {res}')
    print('______________________________________________')

    return destinations


'''FIM DO CÓDIGO'''