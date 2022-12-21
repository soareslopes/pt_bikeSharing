# -*- coding: utf-8 -*- """ Created on Wed Dec 21 17:30:13 2022  @author: Andre """

'''
00_r5py_TimeMatriz.py
OBJETIVO:
    Calcular os tempos entre pares OD
    
        ETAPA 1:
            1A. Definir as redes (PGF e GTFS)
            1B. Contar os pois dentro de cada hexagono


### INPUTS
# -> 00.1.0_pois_classificados.gpkg
# -> 01.2_limiteLisboa_5k.gpkg

### OUTPUTS 
# -> '02.1_HexagonsPOIScount.gpkg'      -> Hexagonso de destino apenas onde existem POIS (contegem por tipo de POIS)
# -> TODAS AS IMAGENS SÃO GERADAS E GUARDADAS AUTOMATICAMENTE
''' 
# INSTRUÇÃO
# Este código precisa ser corrido tantas vezes quanto forem as composições de
# redes de transporte que se pretende avaliar.

#%% BIBLIOTECAS

import warnings
warnings.filterwarnings("ignore")
import geopandas
import time
import pandas

# plotagem
from matplotlib import pyplot as plt
import contextily as cx

# r5py (matrizes)
import datetime
from r5py import TransportNetwork
from r5py import TravelTimeMatrixComputer, TransitMode, LegMode

#%%#%%######################################################
#########################################################
#########################################################
# Etapa 1 - Calcular tempos entre pares OD
#########################################################

# Definir as redes e entrar os dados
'''A'''

# pasta de trabalho
folder = 'G:/Drives compartilhados/MASTI/MASTI/Tasks/Task3_Impacts_ResourcesOpportunities/pasta_nova/'
limiar = 15         # Time threshold a ser analisado
rede = 'SoPt'    # indicar o nome da rede

# Carregar os dados de entrada
##### origens
df_origens = geopandas.read_file(folder + '01.5_hexagonsLisboaMin.gpkg')
df_origens['geometry'] = df_origens['geometry'].centroid
# Renomear 'h3_polifill' para 'id'
df_origens.rename(columns = {'h3_polyfill':'id'}, inplace = True)

##### destinos
df_destinos = geopandas.read_file(folder + '02.1_HexagonsPOIScount.gpkg')
df_destinos['geometry'] = df_destinos['geometry'].centroid
# Renomear 'h3_polifill' para 'id'
df_destinos.rename(columns = {'h3_polyfill':'id'}, inplace = True)

##### hexagonos
df_hexagons = geopandas.read_file(folder + '01.5_hexagonsLisboaMin.gpkg')
df_hexagons = df_hexagons[['h3_polyfill', 'geometry']]

# Endereços dos ficheiros GTFS e PBF
pbf     = folder + '00_AML.osm.pbf'    ##<<<<<<<<< O pbf escolhido tem que cobrir todos os pontos de origem e destino
metro   = folder + 'data/gtfs_Metro.zip'
CP      = folder + 'data/gtfs_CP.zip'
carris  = folder + 'data/gtfs_Carris.zip'
gira    = folder + 'data/gtfs_GIRA.zip'  ##<<<<<<<<< Ficheiros GTFS em formato zip (txt. dentro do zip, sem subpasta)

# Lista dos tipos de atividades avaliadas
osm_types = ['Education','Supermarket','Healthcare','Sports','Culture','Parks','Eating','Retail','Religious','PublicServices']

#%% Definir a rede GTFS + PBF
#--->> PBF da AML + gtfs da CARRIS+METRO+CP  --->> demorou 2min

start = time.time()
# INSTRUÇÃO:
#           MUDAR OS MODOS QUE SE QUER AVALIAR AQUI
#                                         VVVVVVVVVVVVVVVVVVVVVVVV
transport_network = TransportNetwork(pbf,[metro,CP,carris])
end = time.time()
print('##########\nDuração:\n' + str(round((end - start),2)) + ' seg\n##########')

#%%#################################################
####################################################
####################################################
# Estabelecer os parâmetros da mediçã de tempos
'''B'''

# total de origens
n = len(df_origens)

# pares de intervalos
l1 = list(range(0,n,100))
l2 = l1[1:]
l2.append(n)

# df para conter os resultados parciais
df_final = pandas.DataFrame()

# Loop para gerar os trechos da matriz
start = time.time()
for i in range(len(l1)):
    mid = time.time()
    travel_time_matrix_computer = TravelTimeMatrixComputer(
        transport_network,
        origins         = df_origens[l1[i]:l2[i]], # [df_origens.id == '8a393362b90ffff'], # para testes (Amoreiras)
        destinations    = df_destinos,
        departure       = datetime.datetime(2015,8,17,6,0),
        transport_modes = [TransitMode.TRANSIT, LegMode.WALK]
    )
    
    # Cálculo da matriz
    travel_time_matrix = travel_time_matrix_computer.compute_travel_times()
    
    
    end = time.time()
    df_final = pandas.concat([df_final, travel_time_matrix], axis=0)
    tempo_iteração = str(round((end - mid),2))
    print(f'Iteração:           {i}')
    print(f"Tempo da iteração   {str(round((end - mid),2))}seg")
    print(f'Andamento:          {(round((i/len(l1)), 3))*100}%')
    print(f"Tempo total:        {str(round((end - start),2))}seg")
    print(f'tamanho df_final:   {df_final["from_id"].size}')
    print('............................')

#%% Guardar matriz PT em ficheiro
matriz = df_final
# Formato parquet (mais pequeno e mais rápido)
ficheiro = f'matriz/03.1_matriz{rede}.parquet'
matriz.to_parquet(folder + ficheiro)
##########
# Ler ficheiro local
matriz = pandas.read_parquet(folder + ficheiro)
    
#%%#################################################
####################################################
####################################################
'''C'''

# Carregar as matrizes
matrizGira  = pandas.read_parquet(folder + 'matriz/03.1_matrizPT_Gira.parquet')
matrizSoGira = pandas.read_parquet(folder + 'matriz/03.1_matrizSoGira.parquet')
matrizSoPt = pandas.read_parquet(folder + 'matriz/03.1_matrizSoPt.parquet')


# ESCOLHAR A MATRIZ A SER DESENHADA:
#VVVVVVVVVVVVVVVVVV    
matriz = matrizGira


# Aplicar um limiar de tempo para filtrar as viagens
matriz15 = matriz[matriz['travel_time'] < limiar]

# Juntar matriz de tempos com contagem de pois por hexagono de destino
matriz15 = matriz15.merge(df_destinos, left_on='to_id', right_on='id', how='inner')

# agrupar e somar o total de destinos (por tipo) acessível de cada origem
matrizGroup_15 = matriz15.groupby('from_id').sum()

# adicionar geometria dos poligonos na matriz
matrizGroup_15 = matrizGroup_15.reset_index()
matrizGroup_15.rename(columns = {'from_id':'h3_polyfill'}, inplace = True)
matrizGroup_15 = matrizGroup_15.merge(df_hexagons, on='h3_polyfill', how='inner')

# transformar em GDF
matrizGroup_15 = geopandas.GeoDataFrame(matrizGroup_15)

#%% Produzir mapas - CUMMULATIVE OPPORTUNITES
# para cada rede que se escolher

limite = geopandas.read_file(folder + '01.1_limiteLisboa.gpkg')

# mudar sistema projetivo do mopa para epsg = 3763
matrizGroup_15 = matrizGroup_15.to_crs(3763)
limite = limite.to_crs(3763)

for i in range(len(osm_types)):
    fig, ax = plt.subplots(1, 1, figsize=(15,9))
    cmap = plt.cm.get_cmap('viridis', 7)
    matrizGroup_15.plot(column     = str(osm_types[i]),
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
    plt.title(f"Accessibility to: {osm_types[i]} (cummulative opportunities)\n{rede} | {limiar}min threshold | Lisbon - Portugal")
    cx.add_basemap(ax, crs=matrizGroup_15.crs, alpha=0.8)
    plt.show()
    fig.savefig(folder + f'img/fig{i+1}_{osm_types[i]}_{rede}_{limiar}min.png', bbox_inches='tight', dpi=150)
    
'''FIM DO CÓDIGO'''