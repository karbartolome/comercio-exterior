
# ======= Libraries =======

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input,Output,State
#import dash_bootstrap_components as dbc
import pandas as pd
from pyvis.network import Network
import visdcc
import numpy as np
from math import log, floor
import json

#import re
#import dash_table
#import networkx as nx 
import plotly.express as px
#import plotly.graph_objs as go

def human_format(number):
    if number!=0:
        units = ['', 'K', 'M', 'G', 'T', 'P']
        k = 1000.0
        magnitude = int(floor(log(number, k)))
        return '%.1f%s' % (number / k**magnitude, units[magnitude])
    else:
        return 0

df = pd.read_csv('df.csv')
df = df[df.reporter!=df.partner].copy()

sections = pd.DataFrame({'section': df['section'].unique()}).sort_values('section')

network = Network( 
    bgcolor="white", 
    font_color="black",
    notebook=True, 
    directed=True
)


config_layout={
   'height': '1000px', 'width': '100%',
   "nodes": {
       "borderWidth": 0,
       "borderWidthSelected": 7,
       "fixed": {"x": False, "y": False},
       "font": {"size": 13, "strokeWidth": 1, 'color':'black'},
       "shape": "dot",
       'shapeProperties': {
           'interpolation': False
       }
   },
   "edges": {
       "color": {"inherit": True},
       "smooth": {"type": "horizontal", "forceDirection": "none", "roundness": 0},
       "arrows": {"to": {"enabled": True}},
       "arrowStrikethrough": False,
       "selectionWidth": 5

   },
   "interaction": {"dragNodes": True,
                   "hideEdgesOnDrag": False,
                   "multiselect": False,
                   "navigationButtons": True},
   "physics": {
       "enabled": True,
       "stabilization":True,
       "barnesHut": {"gravitationalConstant": -40000, "springLength": 100,
                     "springConstant": 0.01},
       "minVelocity": 0.75,
       "maxVelocity": 50
}}



# ------ Mapa ------
df_clusters = pd.read_csv('df_clusters.csv')
df_clusters['cluster'] = [i[0:1] for i in df_clusters['cluster'].astype('str')]
df_clusters['cluster']=np.where(df_clusters['cluster']=='n','NA', df_clusters['cluster'])

with open('regions.json') as f:
    regions = json.load(f)

mapa = px.choropleth(
            df_clusters, 
            geojson=regions, 
            locations='id', 
            featureidkey='properties.name',
            color='cluster', 
            hover_data=['id', 'cluster'],
            #animation_frame='cluster',
            color_discrete_sequence=['gray',"#FB8455", "#62D5F0", "#18AE95"],
            #range_color=(0, 2),
            scope="world",
            labels={'id':'País','cluster':'Segmento'})

mapa.update_geos(showcountries=True, showcoastlines=False, showland=False, showlakes=False, fitbounds="locations")
                  
mapa.update_layout(
                  margin={"r":0,"t":0,"l":0,"b":0}, 
                  coloraxis_showscale=False, 
                  xaxis={'showgrid': False},
                  yaxis={'showgrid': False},
                  hoverlabel={'bgcolor':"white", 'font_size':14},
                  font={'family':"Helvetica", 'size':12, 'color':"black"},
                  title={'font': {'size': 20}, 'x': 0.5, 'y': 0.99,
                         'text': 'Segmentación de países según centralidad en exportaciones'}
                 )





# ======= APP =======
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

app.layout = html.Div([
    html.H1('Red de exportaciones'),
    html.H4('Exportaciones por rama de exportación (2018, USD)'),
    html.Label(['Fuente: ', html.A('Open Trade Statistics', href='https://tradestatistics.io/')]),
    dcc.Markdown('Para facilitar la visualización, por categoría seleccionada se muestran las exportaciones principales (máximos importes exportados por cada país hacia otro país).'),
    html.Div([
        html.Div([
            dcc.Dropdown(id ='input_section',
                         options=[{'label': i, 'value': i} for i in sections.section.unique()],
                         multi=False,
                         value='Chemical Products',
                         clearable=False),
            
        ], className='six columns'),
        html.Div([
             visdcc.Network(id='network',
                   data={'nodes': network.nodes,'edges': network.edges},
                   options=config_layout)
        ], className='twelve columns')
    ]),
    html.Br(),
    html.Br(),
    html.Div([
        html.Div([
            html.H4('Clustering'),
            dcc.Markdown("""
                Segmentación en base a la centralidad de los países en cada rama de comercio.
                
                La centralidad consderada en este caso es **'out degree centrality'**, que mide para cada nodo (país) la fracción de nodos (países) a los que se conecta por enlaces salientes (exportaciones).
                
                El algoritmo utilizado para la clusterización es **kmeans**, considerando 3 segmentos en base al 'elbow method'. 
            
                
                
            """)
        ]),
        html.Div([
           dcc.Graph(id='mapa', figure=mapa) 
        ])
    ])
])
   
    
       
    
    #html.Div([
    #        html.Div([dbc.CardBody([
    #            html.H5("Máximo exportador", style={'color': 'grey'}),
    #            html.Div(id='output_maxexpo', style={'font':'30px', 'color':'black'})
    #        ])
    #        ], style={"border": "1px white solid",
    #                  'height': '14rem',
    #                  'background-color': '#f8f9fa'}),
    #        html.Div([dbc.CardBody([
    #            html.H5("Máximo importador", style={'color': 'grey'}),
    #            html.Div(id='output_maximpo', style={'font':'30px', 'color':'black'})
    #        ])
    #        ], style={"border": "1px white solid",
    #                  'height': '14rem',
    #                  'background-color': '#f8f9fa'})
    #], style={'column-count': '2',
    #          'margin-top': '1rem',
    #          'font-size': '0.625rem'}),
    



@app.callback(
    Output('network', 'data'),
    [Input('input_section', 'value')]
)
def update_output(value):
    
    dffilt = df[df.section==value].copy()
    
    vertices=dffilt.groupby(['reporter','continent_reporter'], as_index=False).export_value_usd.sum().copy()
    vertices.columns = ['pais','continente','export_value_usd']
    vertices2=dffilt.loc[~dffilt.partner.isin(vertices.pais.unique()),['partner','continent_partner']]
    vertices2['export_value_usd']=0
    vertices2.columns = ['pais','continente','export_value_usd']
    vertices = pd.concat([vertices,vertices2],axis=0)
    vertices['color'] = np.select([vertices.continente == 'Asia', 
                                   vertices.continente == 'Africa', 
                                   vertices.continente == 'Americas',
                                   vertices.continente == 'Europe',
                                   vertices.continente == 'Oceania'],
                                   ['#FB8455','#E36BF4','#62D5F0','#5F96ED','#18AE95'],
                                   default='other')
    vertices['label']=[human_format(i) for i in vertices.export_value_usd]
    
    dffilt = dffilt.sort_values('export_value_usd',ascending=False).head(300).reset_index(drop=True).copy()

    network = Network(bgcolor="white",font_color="black",notebook=False,directed=True)
    edge_data = zip(dffilt['reporter'], dffilt['partner'], dffilt['export_value_usd'])

    for e in edge_data:
        src = e[0]
        dst = e[1]
        w = e[2]
        network.add_node(src, src, title=src)
        network.add_node(dst, dst, title=dst)
        network.add_edge(src, dst, value=w)

    for node in network.nodes:
        if node['id'] in list(vertices['pais']):
            node['value']=int(vertices.loc[vertices.pais==node['id'],'export_value_usd'].values[0])
            node['title']=node['title']+"<br>Export: "+str(vertices.loc[vertices.pais==node['id'],'label'].values[0])
            node['color']=str(vertices.loc[vertices.pais==node['id'],'color'].values[0])

    data ={'nodes': network.nodes,
           'edges': network.edges}
    
    return data



if __name__ == '__main__':
    app.run_server()
