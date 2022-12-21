# -*- coding: utf-8 -*- """ Created on Tue Dec 20 22:45:06 2022  @author: Andre """

'''
04.0_differences.py
OBJETIVO:
    Calcular as diferenças de acessibilidade entrer redes distintas
    
        ETAPA 1:
            1A. Transformar as matrizes OD em DFs com a contagem de Opportunidades
            1B. Gerar DF com as medidas de diferenças
        
        ETAPA 2:
            2A. Gerar mapas das diferenças            


### INPUTS
# -> 01.5_hexagonsLisboaMin.gpkg        -> Origens
# -> 02.1_HexagonsPOIScount.gpkg        -> Destinos
# -> 01.1_limiteLisboa.gpkg             -> Desenho de Lisboa (Borda)
# -> MATRIZES                           -> Pares OD com calculo de menor distância

### OUTPUTS 
# -> '02.1_HexagonsPOIScount.gpkg'      -> Hexagonso de destino apenas onde existem POIS (contegem por tipo de POIS)
# -> TODAS AS IMAGENS SÃO GERADAS E GUARDADAS AUTOMATICAMENTE
''' 

#%% Bibliotecas
import pandas as pd
pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

pd.options.display.float_format = '{:.2f}'.format

from matplotlib import pyplot as plt
import contextily as cx
# import h3pandas
import geopandas


#%% INPUT
folder = 'G:/Drives compartilhados/MASTI/MASTI/Tasks/Task3_Impacts_ResourcesOpportunities/pasta_nova/'
osm_types = ['Education','Supermarket','Healthcare','Sports','Culture','Parks','Eating','Retail','Religious','PublicServices']
# Carregar os dados de entrada
##### hexagonos
df_hexagons = geopandas.read_file(folder + '01.5_hexagonsLisboaMin.gpkg')
df_hexagons = df_hexagons[['h3_polyfill', 'geometry']]

##### destinos
df_destinos = geopandas.read_file(folder + '02.1_HexagonsPOIScount.gpkg')
df_destinos['geometry'] = df_destinos['geometry'].centroid
# Renomear 'h3_polifill' para 'id'
df_destinos.rename(columns = {'h3_polyfill':'id'}, inplace = True)

#carregar matrizes
matrizGira  = pd.read_parquet(folder + 'matriz/03.1_matrizPT_Gira.parquet')
matrizSoGira = pd.read_parquet(folder + 'matriz/03.1_matrizSoGira.parquet')
matrizSoPt = pd.read_parquet(folder + 'matriz/03.1_matrizSoPt.parquet')

limite = geopandas.read_file(folder + '01.1_limiteLisboa.gpkg')

#%%#%%######################################################
#########################################################
#########################################################
# Etapa 1 - Medir Diferenças entre Matrizes
#########################################################
'''A'''

limiar = 15
# para a matriz da rede PT+Gira
mGira = matrizGira.merge(df_destinos, left_on='to_id', right_on='id', how='inner')
mGira = mGira[['from_id', 'to_id', 'travel_time',
               'Education', 'Supermarket', 'Healthcare', 'Sports', 'Culture',
               'Parks', 'Eating', 'Retail', 'Religious', 'PublicServices']]
mGira = mGira[mGira['travel_time'] < limiar]
mGira = mGira.groupby('from_id').sum()
mGira = mGira.reset_index()
mGira = mGira[['from_id', 'Education', 'Supermarket', 'Healthcare', 'Sports', 'Culture','Parks', 'Eating', 'Retail', 'Religious', 'PublicServices']]
mGira = mGira.merge(df_hexagons, left_on='from_id', right_on='h3_polyfill', how='inner' )
mGira = geopandas.GeoDataFrame(mGira)

# para a matriz da rede somente PT (carris|metro|CP)
mSoPt = matrizSoPt.merge(df_destinos, left_on='to_id', right_on='id', how='inner')
mSoPt = mSoPt[['from_id', 'to_id', 'travel_time',
               'Education', 'Supermarket', 'Healthcare', 'Sports', 'Culture',
               'Parks', 'Eating', 'Retail', 'Religious', 'PublicServices']]
mSoPt = mSoPt[mSoPt['travel_time'] < limiar]
mSoPt = mSoPt.groupby('from_id').sum()
mSoPt = mSoPt.reset_index()
mSoPt = mSoPt[['from_id', 'Education', 'Supermarket', 'Healthcare', 'Sports', 'Culture','Parks', 'Eating', 'Retail', 'Religious', 'PublicServices']]
mSoPt = mSoPt.merge(df_hexagons, left_on='from_id', right_on='h3_polyfill', how='inner' )
mSoPt = geopandas.GeoDataFrame(mSoPt)

# Output:
# - dois gdfs com contagem de opportunidades em 15min
# mSoPt e mGira


#%% Calcular as diferenças
'''B'''

mJoin = mGira.merge(mSoPt, on='from_id', how='inner')
mDif = mJoin[['from_id','geometry_x']].copy()
mDif.columns = ['id', 'geometry']
mDif['Education'] = mJoin.Education_x - mJoin.Education_y
mDif['Supermarket'] = mJoin.Supermarket_x - mJoin.Supermarket_y
mDif['Healthcare'] = mJoin.Healthcare_x - mJoin.Healthcare_y
mDif['Sports'] = mJoin.Sports_x - mJoin.Sports_y
mDif['Culture'] = mJoin.Culture_x - mJoin.Culture_y
mDif['Parks'] = mJoin.Parks_x - mJoin.Parks_y
mDif['Eating'] = mJoin.Eating_x - mJoin.Eating_y
mDif['Retail'] = mJoin.Retail_x - mJoin.Retail_y
mDif['Religious'] = mJoin.Religious_x - mJoin.Religious_y
mDif['PublicServices'] = mJoin.PublicServices_x - mJoin.PublicServices_y
mDif = geopandas.GeoDataFrame(mDif)

# Output:
# - um gdf (mDif) contendo as diferenças de opportunidades acess+iveis me 15min

#%%#%%######################################################
#########################################################
#########################################################
# Etapa 2 - Gerar mapas das diferenças
#########################################################
'''A'''

i = 0
mDif = mDif.to_crs(limite.crs)

for i in range(len(osm_types)):
    fig, ax = plt.subplots(1, 1, figsize=(15,9))
    cmap = plt.cm.get_cmap('gist_heat_r', 7)
    mDif.plot(column     = str(osm_types[i]),
                     ax         = ax,
                     cmap       = cmap,
                     # scheme   = 'EqualInterval',
                     # k        = 5,
                     alpha      = 0.75,   
                     vmin      = 0,
                     legend     = True,
                     edgecolor  = 'k',
                     linewidth  = 0)
    limite.plot(ax          =ax,
                facecolor   ="none",
                edgecolor   ='k',
                linewidth   = 2)
                   
    # ax.annotate('ETRS89/ PortugalTM06 | epgs:3763', xy=(-9.123, 38.687)) # para epsg 4326
    ax.annotate('ETRS89 | epgs:3763', xy=(-84850, -108380)) # para epsg 3763
    x, y, arrow_length = 0.0255, 0.975, 0.075
    ax.annotate('N', xy=(x, y), xytext=(x, y-arrow_length),
            arrowprops=dict(facecolor='gray', edgecolor= 'gray',
                            width=4, headwidth=12),
            ha='center', va='center', fontsize=16, xycoords=ax.transAxes)
    plt.title(f"Accessibility to: {osm_types[i]} (cummulative opportunities)\nDifference between Gira+Pt and PT only networks")
    cx.add_basemap(ax, crs=mDif.crs, alpha=0.8)
    plt.show()
    
    fig.savefig(folder + f'img/Differences/fig{i+1}_{osm_types[i]}_Differença_{limiar}min.png', bbox_inches='tight', dpi=150)

'''FIM DO CÓDIGO'''

#%%##################################################################
#####################################################################
# TESTE das matrizes OD (SoPT | PT+Gira | SoGira)
# escolher um hexagono
i = '8a393362b867fff'

# calcular os tempos a parti deste hexagono para as 3 redes
gira15 = matrizGira[matrizGira['from_id'] == i]
soGira15 = matrizSoGira[matrizSoGira['from_id'] == i]
soPt15 = matrizSoPt[matrizSoPt['from_id'] == i]

# produzir mapas para cada uma das redes
mapa = df_hexagons.merge(soPt15, left_on='h3_polyfill', right_on='to_id', how='left')

#%% plotar os mapas
limite = geopandas.read_file(folder + '01.1_limiteLisboa.gpkg')

fig, ax = plt.subplots(1, 1, figsize=(20,16))
cmap = plt.cm.get_cmap('viridis', 7)
mapa.plot(column     = 'travel_time',
            ax         = ax,
            cmap       = cmap,
            # scheme   = 'EqualInterval',
            # k        = 5,
            alpha      = 0.75,   
            #vmin      = 0,
            #vmax      = 100,
            legend     = True,
            edgecolor  = 'k',
            linewidth  = 0)
# df_hexagons[df_hexagons['h3_polyfill'] == i].plot(ax=ax)
limite.plot(ax          =ax,
            facecolor   ="none",
            edgecolor   ='k',
            linewidth   = 2)


#%% TESTE
matrizSoPt['code']  = matrizSoPt['from_id'] + matrizSoPt['to_id']
matrizGira['code']  = matrizGira['from_id'] + matrizGira['to_id']

# limitado a 15min
matrizSoPt15 = matrizSoPt[matrizSoPt['travel_time'] < 15]
matrizGira15 = matrizGira[matrizGira['travel_time'] < 15]

matrizJoin = pd.merge(matrizGira15, matrizSoPt15, on='code', how='inner')
matrizJoin = matrizJoin[[ 'code', 'from_id_x', 'to_id_x', 'travel_time_x', 'travel_time_y']]

matrizJoin.columns = ['code', 'from_id', 'to_id', 'travel_time_PTgira', 'travel_time_PT']

matrizJoin['dif'] = matrizJoin.travel_time_PTgira - matrizJoin.travel_time_PT
matrizJoin[matrizJoin['dif']!=0].describe()

matrizJoin.sort_values('dif')
