
# ======= Libraries =======

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input,Output,State
import pandas as pd
from pyvis.network import Network
import visdcc
import numpy as np
from math import log, floor

#import re
#import dash_table
#import networkx as nx 
#import plotly.express as px
#import plotly.graph_objs as go

def human_format(number):
    if number!=0:
        units = ['', 'K', 'M', 'G', 'T', 'P']
        k = 1000.0
        magnitude = int(floor(log(number, k)))
        return '%.1f%s' % (number / k**magnitude, units[magnitude])
    else:
        return 0

df = pd.read_csv('df.csv').drop('Unnamed: 0', axis=1)
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
       "font": {"size": 13, "strokeWidth": 3, 'color':'black'},
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




# ======= APP =======
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

app.layout = html.Div([
    html.H1('Relaciones comerciales'),
    html.H4('Red de exportaciones por tipo exportación (2018, USD)'),
    html.Div([
        html.Div([
            dcc.Dropdown(id ='input_section',
                         options=[{'label': i, 'value': i} for i in sections.section.unique()],
                         multi=False,
                         value='Chemical Products',
                         clearable=False),
        ], className='six columns'),
    ], className='row'),
    visdcc.Network(id='network',
                   data={'nodes': network.nodes,'edges': network.edges},
                   options=config_layout)
])


@app.callback(
    Output('network', 'data'),
    [Input('input_section', 'value')]
)
def update_output(value):
    
    dffilt = df[df.section==value].copy()
    dffilt = dffilt.sort_values('export_value_usd',ascending=False).head(300).reset_index(drop=True).copy()
    
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
                                   ['#7fc97f','#beaed4','#fdc086','#ffff99','#386cb0'], 
                                   default='other')
    vertices['label']=[human_format(i) for i in vertices.export_value_usd]

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
