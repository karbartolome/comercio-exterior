
# ======= Libraries =======

import dash
import dash_core_components as dcc
import dash_html_components as html
#from dash.dependencies import Input,Output,State
import pandas as pd
from pyvis.network import Network
import visdcc
#import re
#import dash_table
#import networkx as nx 
#import plotly.express as px
#import plotly.graph_objs as go


df=pd.read_csv('df.csv').drop('Unnamed: 0',axis=1)
df=df[~df.export_value_usd.isna()].copy()


vertices = list(set(list(df.reporter_iso)+list(df.partner_iso)))
vertices = pd.DataFrame({'pais':vertices})
vertices=df.groupby('reporter_iso', as_index=False).export_value_usd.sum()
vertices.columns = ['pais','export_value_usd']
vertices['export_value_usd'] = np.where(vertices.export_value_usd==0, 10, vertices.export_value_usd)

vertices['color'] = np.where(vertices.pais == 'arg', 'orange','palegreen')
vertices['size'] = pd.qcut(vertices['export_value_usd'], 4, labels=[10,100,1000,2000])



network = Network(
    height="750px", 
    width="100%", 
    bgcolor="white", 
    font_color="black",
    notebook=False, 
    directed=True
)

sources = df['reporter_iso']
targets = df['partner_iso']
weights = df['export_value_usd']

edge_data = zip(sources, targets, weights)

for e in edge_data:
    src = e[0]
    dst = e[1]
    w = e[2]

    network.add_node(src, src, title=src)
    network.add_node(dst, dst, title=dst)
    network.add_edge(src, dst, value=w, label=w)

neighbor_map = network.get_adj_list()

# add neighbor data to node hover data
for node in network.nodes:
    if node['id'] in list(vertices['pais']):
        node['value']=int(vertices.loc[vertices.pais==node['id'],'size'].values[0])
        node['title']=node['title']+"<br>Export: "+str(vertices.loc[vertices.pais==node['id'],'export_value_usd'].values[0])
        node['color']=str(vertices.loc[vertices.pais==node['id'],'color'].values[0])


config_layout={
   'height': '600px', 'width': '100%',
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

app.layout = html.Div(children=[
    html.H1('Comercio exterior'),
    visdcc.Network(id='network',
                   data={'nodes': network.nodes,
                         'edges': network.edges
                         },
                   options=config_layout)
])


if __name__ == '__main__':
    app.run_server()
