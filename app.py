
# ======= Libraries =======

import dash
#rom jupyter_dash import JupyterDash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input,Output
#import dash_bootstrap_components as dbc
import pandas as pd
from pyvis.network import Network
import networkx as nx
import visdcc
import numpy as np
from math import log, floor
import json

#import dash_table
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
    
def draw_pyvis(networkx_graph):
   
    pyvis_graph = Network( 
        bgcolor="white", 
        font_color="black",
        notebook=False, 
        directed=True
    )

    for node,node_attrs in networkx_graph.nodes(data=True):
        node_attrs['label']=node
        pyvis_graph.add_node(str(node),**node_attrs)
    
    for source,target,edge_attrs in networkx_graph.edges(data=True):
        if not 'value' in edge_attrs and not 'width' in edge_attrs and 'weight' in edge_attrs:
            edge_attrs['value']=edge_attrs['weight']
            edge_attrs['title']=edge_attrs['section']
            edge_attrs['label']=edge_attrs['section']
        pyvis_graph.add_edge(str(source),str(target),**edge_attrs)
        
    return pyvis_graph 
      

df = pd.read_csv('df.csv')

sections = pd.DataFrame({'section': df['section'].unique()}).sort_values('section')

network = Network( 
    bgcolor="white", 
    font_color="black",
    notebook=False, 
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

with open('regions.json') as f:
    regions = json.load(f)

mapa = px.choropleth(
            df_clusters, 
            geojson=regions, 
            locations='id', 
            featureidkey='properties.name',
            color='cluster', 
            hover_data=['id', 'cluster'],
            animation_frame='year',
            color_discrete_sequence=["#FB8455", "#62D5F0", "#5F96ED"],
            #range_color=(0, 2),
            scope="world",
            labels={'id':'País','cluster':'Segmento'})

mapa.update_geos(showcountries=True, showcoastlines=False, showland=False, showlakes=False, fitbounds="locations")
                  
mapa.update_layout(
                  margin={"r":0,"t":0,"l":0,"b":0}, 
                  coloraxis_showscale=False, 
                  dragmode= False,
                  xaxis={'showgrid': False},
                  yaxis={'showgrid': False},
                  hoverlabel={'bgcolor':"white", 'font_size':14},
                  font={'family':"Helvetica", 'size':12, 'color':"black"}
                 )







# Tab 2
df['color'] = np.select([df['continent_reporter'] == 'Asia', 
                               df['continent_reporter']== 'Africa', 
                               df['continent_reporter'] == 'Americas',
                               df['continent_reporter'] == 'Europe',
                               df['continent_reporter'] == 'Oceania'],
                               ['#FB8455','#E36BF4','#62D5F0','#5F96ED','#18AE95'],
                               default='other')



# ======= APP =======
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']


app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
#app = JupyterDash(__name__, external_stylesheets=external_stylesheets)

app.title = 'Redes comerciales'

app.layout = html.Div([
    html.Title('Redes en el comercio mundial'),
    html.H3('Exportaciones por rama de exportación'),
    html.Div([
        html.Div([
            html.Label(['Fuente: ',html.A('Open Trade Statistics', href='https://tradestatistics.io/')], style={'fontSize':16}),
        ]), 
    ]),
    dcc.Tabs(id='tabs',value='tab-1', children=[
        dcc.Tab(id='tab-1', label='Red completa', children=[
            html.Br(),
            dcc.Markdown("""
                    Para facilitar la visualización, por categoría seleccionada se muestran las exportaciones principales (máximos importes exportados por cada país hacia otro país). 
                    Los datos corresponden al año 2018, en USD.  
                    """, style={'fontSize':14}),
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
            ])
        ]), 
        dcc.Tab(id='tab-2',label='Ego network', children=[
            html.Div([
                html.Br(),
                dcc.Markdown("""
                    En esta sección se puede visualizar la red ego de un país, para un producto determinado. 
                    La red ego consiste de un **nodo central (país seleccionado, 'ego')** y los **nodos con los cuales está conectado ('alters', serían los 5 principales destinos de sus exportaciones del producto seleccionado)**.
                    Es posible expandir el radio de la red ego, visualizando, además de sus principales destinos de exportación de este producto, los 5 principales destinos de exportación del mismo producto para cada uno de sus 5 principales socios comerciales. 
                    """, style={'fontSize':14}),
                html.Div([
                    html.Div([
                        html.P('País'),
                        dcc.Dropdown(id ='input_pais',
                                 options=[{'label': i, 'value': i} for i in df.reporter.unique()],
                                 multi=False,
                                 value='Argentina',
                                 clearable=False),
                    ], className='six columns'),
                    html.Div([
                        html.P('Producto'),
                        dcc.Dropdown(id ='input_section2',
                                 options=[{'label': i, 'value': i} for i in sections.section.unique()],
                                 multi=False,
                                 value='Chemical Products',
                                 clearable=False),
                    ], className='six columns'),

                ], className='row'),
                html.Br(),
                html.Div([
                   html.Div([
                    html.Div([
                        html.P('Radio'),
                    ]),
                    html.Div([
                       dcc.Slider(id='slider_radio',
                                min=1, max=4, step=1, value=1, 
                                marks={
                                    1: {'label': '1'},
                                    2: {'label': '2'},
                                    3: {'label': '3'},
                                    4: {'label': '4'}
                                }) 
                    ]) 
                    ], className='two columns'),
                    html.Div([
                         visdcc.Network(id='network2',
                               data={},
                               options=config_layout)
                    ], className='ten columns') 
                ])
                
            ])
        ]), 
        dcc.Tab(id='tab3', label='Clustering (1962-2018)', children=[
            html.Div([
                html.Br(),
                html.Div([
                    dcc.Markdown("""
                        Segmentación en base a la centralidad de los países en cada rama de comercio.

                    """, style={'fontSize':14})
                ]),
                html.Div([
                   dcc.Graph(id='mapa', figure=mapa) 
                ]), 
                dcc.Markdown("""

                        La centralidad consderada en este caso es **'out degree centrality'**, que mide para cada nodo (país) la fracción de nodos (países) a los que se conecta por enlaces salientes (exportaciones).

                        El algoritmo utilizado es **kmeans**, considerando 3 segmentos en base al 'elbow method'. 

                        Hay exportaciones que quedaron fuera de la visualización pero igualmente fueron tenidas en cuenta al generar las variables para clusterizar.  

                """, style={'fontSize':14})
            ]),
        ])
    ]), 
    html.Div([
        html.Label(['ln: ', html.A('karinabartolome', href='https://www.linkedin.com/in/karinabartolome/')], style={'fontSize':16})
        ]),
    html.Div([
        html.Label(['tw: ', html.A('@karbartolome', href='https://twitter.com/karbartolome')], style={'fontSize':16})
        ])
    
    
])


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


@app.callback(
    Output('network2', 'data'),
    [
     Input('input_pais', 'value'), 
     Input('slider_radio', 'value'), 
     Input('input_section2', 'value')
    ]
)
def update_output(pais, radio, section):
    
    red_particular=(df[df.section==section].copy()
        .set_index(['partner','section', 'color','continent_partner'])
        .groupby(['reporter','continent_reporter']).export_value_usd.nlargest(5).reset_index())

    G = nx.from_pandas_edgelist(df = red_particular,
                                source = 'reporter',
                                target = 'partner',
                                edge_attr = True, 
                                create_using=nx.DiGraph())
    
    
    attr_dict_grupo = df.set_index('reporter')['color'].to_dict()
    nx.set_node_attributes(G, values = attr_dict_grupo, name = 'color')

    S = nx.ego_graph(G, 
                 pais, 
                 radius=radio, 
                 center=True, 
                 undirected=False, 
                 distance=None)

    network_particular = draw_pyvis(S)
    
    data ={'nodes': network_particular.nodes,
           'edges': network_particular.edges}
    
    return data
    

if __name__ == '__main__':
    app.run_server()
    
    
