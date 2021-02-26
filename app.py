# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_table
import plotly.express as px
import plotly.graph_objects as go 
import dash_daq as daq
from dash.dependencies import Input, Output, State
import os
from zipfile import ZipFile
import urllib.parse
from flask import Flask, send_from_directory

import pandas as pd
import requests
import uuid
import werkzeug

import pymzml
import numpy as np
from tqdm import tqdm
import urllib
import json

from collections import defaultdict
import uuid

from flask_caching import Cache



server = Flask(__name__)
app = dash.Dash(__name__, server=server, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = 'GNPS - Group Explorer'

cache = Cache(app.server, config={
    'CACHE_TYPE': 'filesystem',
    'CACHE_DIR': 'temp/flask-cache',
    'CACHE_DEFAULT_TIMEOUT': 0,
    'CACHE_THRESHOLD': 10000
})

server = app.server

NAVBAR = dbc.Navbar(
    children=[
        dbc.NavbarBrand(
            html.Img(src="https://gnps-cytoscape.ucsd.edu/static/img/GNPS_logo.png", width="120px"),
            href="https://gnps.ucsd.edu"
        ),
        dbc.Nav(
            [
                dbc.NavItem(dbc.NavLink("GNPS - Plotter Dashboard - Version 0.3", href="#")),
            ],
        navbar=True)
    ],
    color="light",
    dark=False,
    sticky="top",
)

DATASELECTION_CARD = [
    dbc.CardHeader(html.H5("Data Selection")),
    dbc.CardBody(
        [   
            html.H5(children='GNPS Data Selection'),
            dbc.InputGroup(
                [
                    dbc.InputGroupAddon("GNPS Tall Table USI", addon_type="prepend"),
                    dbc.Input(id='gnps_tall_table_usi', placeholder="Enter GNPS Tall Table USI", value=""),
                ],
                className="mb-3",
            ),
            html.Hr(),
            dbc.InputGroup(
                [
                    dbc.InputGroupAddon("GNPS Quant Table USI", addon_type="prepend"),
                    dbc.Input(id='gnps_quant_table_usi', placeholder="Enter GNPS Quant Table USI", value=""),
                ],
                className="mb-3",
            ),
            dbc.InputGroup(
                [
                    dbc.InputGroupAddon("GNPS Metadata Table USI", addon_type="prepend"),
                    dbc.Input(id='gnps_metadata_table_usi', placeholder="Enter GNPS Metadata Table USI", value=""),
                ],
                className="mb-3",
            ),
            html.Hr(),
            dbc.InputGroup(
                [
                    dbc.InputGroupAddon("Feature ID", addon_type="prepend"),
                    dbc.Input(id='feature', placeholder="Enter Feature", value=""),
                ],
                className="mb-3",
            ),
            html.H5(children='Plot Configuration'),
            dbc.InputGroup(
                [
                    dbc.InputGroupAddon("Metadata Column", addon_type="prepend"),
                    dcc.Dropdown(
                        id='metadata_column',
                        options=[],
                        style={
                            "width": "300px",
                            "height": "100%",
                            "margin-left": "10px",
                            "margin-top": "0.5px"
                        },
                        searchable=True,
                        clearable=False,
                    ),
                ],
                className="mb-3",
            ),
            dbc.InputGroup(
                [
                    dbc.InputGroupAddon("Facet Column", addon_type="prepend"),
                    dcc.Dropdown(
                        id='facet_column',
                        options=[],
                        style={
                            "width": "300px",
                            "height": "100%",
                            "margin-left": "10px",
                            "margin-top": "0.5px"
                        },
                        value=""
                    ),
                ],
                className="mb-3",
            ),
            dbc.InputGroup(
                [
                    dbc.InputGroupAddon("Animation Column (Alpha)", addon_type="prepend"),
                    dcc.Dropdown(
                        id='animation_column',
                        options=[],
                        style={
                            "width": "300px",
                            "height": "100%",
                            "margin-left": "10px",
                            "margin-top": "0.5px"
                        },
                        value=""
                    ),
                ],
                className="mb-3",
            ),
            dbc.InputGroup(
                [
                    dbc.InputGroupAddon("Group Selection", addon_type="prepend"),
                    dcc.Dropdown(
                        id='group_selection',
                        options=[],
                        style={
                            "width": "500px",
                            "height": "100%",
                            "margin-left": "10px",
                            "margin-top": "0.5px"
                        },
                        multi=True,
                        value=""
                    ),
                ],
                className="mb-3",
            ),
            dbc.InputGroup(
                [
                    dbc.InputGroupAddon("Color Column", addon_type="prepend"),
                    dcc.Dropdown(
                        id='color_selection',
                        options=[],
                        style={
                            "width": "300px",
                            "height": "100%",
                            "margin-left": "10px",
                            "margin-top": "0.5px"
                        },
                        value=""
                    ),
                ],
                className="mb-3",
            ),
            dbc.InputGroup(
                [
                    dbc.InputGroupAddon("Theme", addon_type="prepend"),
                    dcc.Dropdown(
                        id='theme',
                        options=[
                            {
                                "label": "ggplot2",
                                "value" : "ggplot2"
                            },
                            {
                                "label": "plotly",
                                "value" : "plotly"
                            },
                            {
                                "label": "seaborn",
                                "value" : "seaborn"
                            },
                            {
                                "label": "simple_white",
                                "value" : "simple_white"
                            },
                        ],
                        value="ggplot2",
                        style={
                            "width": "300px",
                            "height": "100%",
                            "margin-left": "10px",
                            "margin-top": "0.5px"
                        }
                    ),
                ],
                className="mb-3",
            ),
            dbc.InputGroup(
                [
                    dbc.InputGroupAddon("Plot Type", addon_type="prepend"),
                    dcc.Dropdown(
                        id='plot_type',
                        options=[
                            {
                                "label": "box",
                                "value" : "box"
                            },
                            {
                                "label": "violin",
                                "value" : "violin"
                            }
                        ],
                        value="box",
                        style={
                            "width": "300px",
                            "height": "100%",
                            "margin-left": "10px",
                            "margin-top": "0.5px"
                        }
                    ),
                ],
                className="mb-3",
            ),
            dbc.InputGroup(
                [
                    dbc.InputGroupAddon("Plot Export Format", addon_type="prepend"),
                    dcc.Dropdown(
                        id='image_export_format',
                        options=[
                            {'label': 'SVG', 'value': 'svg'},
                            {'label': 'PNG', 'value': 'png'},
                        ],
                        searchable=False,
                        clearable=False,
                        value="svg",
                        style={
                            "width":"150px"
                        }
                    )  
                ],
                className="mb-3",
            ),
            dbc.InputGroup(
                [
                    dbc.InputGroupAddon("Show Plot Points", addon_type="prepend"),
                    daq.ToggleSwitch(
                        id='points_toggle',
                        value=False,
                        style={
                            "margin-top": "5px",
                            "margin-left": "15px"
                        }
                    ),
                ],
                className="mb-3",
            ),
            dbc.InputGroup(
                [
                    dbc.InputGroupAddon("Log Axis", addon_type="prepend"),
                    daq.ToggleSwitch(
                        id='log_axis',
                        value=False,
                        style={
                            "margin-top": "5px",
                            "margin-left": "15px"
                        }
                    ),
                ],
                className="mb-3",
            ),
            html.Hr(),
            html.H5("Mapping Options"),
            dbc.InputGroup(
                [
                    dbc.InputGroupAddon("Latitute Metadata Column", addon_type="prepend"),
                    dcc.Dropdown(
                        id='lat_column',
                        options=[],
                        style={
                            "width": "300px",
                            "height": "100%",
                            "margin-left": "10px",
                            "margin-top": "0.5px"
                        },
                        value="",
                        searchable=True,
                        clearable=False,
                    ),
                ],
                className="mb-3",
            ),
            dbc.InputGroup(
                [
                    dbc.InputGroupAddon("Longitude Metadata Column", addon_type="prepend"),
                    dcc.Dropdown(
                        id='long_column',
                        options=[],
                        style={
                            "width": "300px",
                            "height": "100%",
                            "margin-left": "10px",
                            "margin-top": "0.5px"
                        },
                        value="",
                        searchable=True,
                        clearable=False,
                    ),
                ],
                className="mb-3",
            ),
            dbc.InputGroup(
                [
                    dbc.InputGroupAddon("Map Animation Column", addon_type="prepend"),
                    dcc.Dropdown(
                        id='map_animation_column',
                        options=[],
                        style={
                            "width": "300px",
                            "height": "100%",
                            "margin-left": "10px",
                            "margin-top": "0.5px"
                        },
                        value="",
                        searchable=True,
                        clearable=False,
                    ),
                ],
                className="mb-3",
            ),
            dbc.InputGroup(
                [
                    dbc.InputGroupAddon("Map Scope", addon_type="prepend"),
                    dcc.Dropdown(
                        id='map_scope',
                        options=[
                            {'label': 'world', 'value': 'world'},
                            {'label': 'usa', 'value': 'usa'},
                            {'label': 'europe', 'value': 'europe'},
                            {'label': 'asia', 'value': 'asia'},
                            {'label': 'africa', 'value': 'africa'},
                            {'label': 'north america', 'value': 'north america'},
                            {'label': 'south america', 'value': 'south america'},
                        ],
                        searchable=False,
                        clearable=False,
                        value="world",
                        style={
                            "width":"150px"
                        }
                    )  
                ],
                className="mb-3",
            ),
            html.Hr(),
            html.H5("Deprecated Options"),
            dbc.InputGroup(
                [
                    dbc.InputGroupAddon("GNPS Task", addon_type="prepend"),
                    dbc.Input(id='task', placeholder="Enter GNPS Task"),
                ],
                className="mb-3",
            ),
        ]
    )
]

LEFT_DASHBOARD = [
    html.Div(
        [
            html.Div(DATASELECTION_CARD),
        ]
    )
]

MIDDLE_DASHBOARD = [
    dbc.CardHeader(html.H5("Data Exploration")),
    dbc.CardBody(
        [
            dcc.Loading(
                id="plot_link",
                children=[html.Div([html.Div(id="loading-output-23")])],
                type="default",
            ),
            html.Br(),
            dcc.Loading(
                id="debug-output",
                children=[html.Div([html.Div(id="loading-output-2")])],
                type="default",
            ),
            html.Br(),
            dcc.Loading(
                id="mapping_plot",
                children=[html.Div([html.Div(id="loading-output-8")])],
                type="default",
            ),
        ]
    )
]

CONTRIBUTORS_DASHBOARD = [
    dbc.CardHeader(html.H5("Contributors")),
    dbc.CardBody(
        [
            "Mingxun Wang PhD - UC San Diego",
            html.Br(),
            html.Br(),
            html.H5("Citation"),
            html.A('Mingxun Wang, Jeremy J. Carver, Vanessa V. Phelan, Laura M. Sanchez, Neha Garg, Yao Peng, Don Duy Nguyen et al. "Sharing and community curation of mass spectrometry data with Global Natural Products Social Molecular Networking." Nature biotechnology 34, no. 8 (2016): 828. PMID: 27504778', 
                    href="https://www.nature.com/articles/nbt.3597")
        ]
    )
]

EXAMPLES_DASHBOARD = [
    dbc.CardHeader(html.H5("Examples")),
    dbc.CardBody(
        [
            html.A('Basic', 
                    href=""),
            html.Br(),
            html.A('Plotting Map', 
                    href="/?gnps_tall_table_usi=mzdata%3AGNPS%3ATASK-27697bfdafcc48fd92d302d65498f053-feature_statistics%2Fdata_long.csv&gnps_quant_table_usi=&gnps_metadata_table_usi=&feature=1&metadata=ATTRIBUTE_Sample_Type&facet=&groups=Transect%3BControl%3BCycle&plot_type=box&color=&points_toggle=False&theme=ggplot2&animation_column=&lat_column=Latitude&long_column=Longitude&map_animation_column=&map_scope=usa")
        ]
    )
]

BODY = dbc.Container(
    [
        dcc.Location(id='url', refresh=False),
        dbc.Row([
            dbc.Col(
                dbc.Card(LEFT_DASHBOARD),
                className="w-50"
            ),
            dbc.Col(
                [
                    dbc.Card(MIDDLE_DASHBOARD),
                    html.Br(),
                    dbc.Card(CONTRIBUTORS_DASHBOARD),
                    html.Br(),
                    dbc.Card(EXAMPLES_DASHBOARD)
                ],
                className="w-50"
            ),
        ], style={"marginTop": 30}),
    ],
    fluid=True,
    className="",
)

app.layout = html.Div(children=[NAVBAR, BODY])

def _get_url_param(param_dict, key, default):
    return param_dict.get(key, [default])[0]

@app.callback([
                Output('task', 'value'), 
                Output('feature', 'value'), 
                Output('facet_column', 'value'),
                Output('animation_column', 'value'),
                Output("color_selection", "value"),
                Output('plot_type', 'value'),
                Output('theme', 'value'),
                Output('points_toggle', 'value'),
                Output('map_scope', 'value')],
              [Input('url', 'search')])
def determine_task(search):
    task = dash.no_update
    feature = dash.no_update
    facet = dash.no_update
    animation_column = dash.no_update
    color = dash.no_update
    plot_type = dash.no_update
    theme = dash.no_update
    points_toggle = dash.no_update


    try:
        query_dict = urllib.parse.parse_qs(search[1:])
    except:
        query_dict = {}

    task = _get_url_param(query_dict, "task", "7f8964473236470c89d6b099ebd4de3c")
    feature = _get_url_param(query_dict, "feature", "1")
    facet = _get_url_param(query_dict, "facet", facet)
    animation_column = _get_url_param(query_dict, "animation_column", animation_column)
    color = _get_url_param(query_dict, "color", color)
    plot_type = _get_url_param(query_dict, "plot_type", plot_type)
    theme = _get_url_param(query_dict, "theme", theme)
    points_toggle = _get_url_param(query_dict, "points_toggle", points_toggle)
    map_scope = _get_url_param(query_dict, "map_scope", dash.no_update)

    return [task, feature, facet, animation_column, color, plot_type, theme, points_toggle, map_scope]

@app.callback([
                Output('gnps_tall_table_usi', 'value'), 
                Output('gnps_quant_table_usi', 'value'), 
                Output('gnps_metadata_table_usi', 'value')],
              [
                  Input('url', 'search'),
                  Input('task', 'value'),
              ])
def determine_usi(search, task):
    gnps_tall_table_usi = dash.no_update
    gnps_quant_table_usi = dash.no_update
    gnps_metadata_table_usi = dash.no_update

    triggered_id = [p['prop_id'] for p in dash.callback_context.triggered][0]

    if "task" in triggered_id:
        gnps_tall_table_usi = "mzdata:GNPS:TASK-{}-feature_statistics/data_long.csv".format(task)

    try:
        query_dict = urllib.parse.parse_qs(search[1:])
    except:
        query_dict = {}

    gnps_tall_table_usi = _get_url_param(query_dict, "gnps_tall_table_usi", gnps_tall_table_usi)
    gnps_quant_table_usi = _get_url_param(query_dict, "gnps_quant_table_usi", gnps_quant_table_usi)
    gnps_metadata_table_usi = _get_url_param(query_dict, "gnps_metadata_table_usi", gnps_metadata_table_usi)

    return [
        gnps_tall_table_usi,
        gnps_quant_table_usi,
        gnps_metadata_table_usi
    ]


    
@app.callback([
                Output('metadata_column', 'value'),
                Output('lat_column', 'value'),
                Output('long_column', 'value')
              ],
              [Input('url', 'search'), Input("metadata_column", "options")])
def determine_metadata(search, metadata_columns):
    metadata = dash.no_update
    query_dict = urllib.parse.parse_qs(search[1:])

    try:
        metadata = metadata_columns[0]["value"]
    except:
        pass

    metadata = _get_url_param(query_dict, "metadata", metadata)

    lat_column = _get_url_param(query_dict, "lat_column", dash.no_update)
    long_column = _get_url_param(query_dict, "long_column", dash.no_update)

    return [metadata, lat_column, long_column]

@cache.memoize()
def _get_task_df(gnps_tall_table_usi, gnps_quant_table_usi, gnps_metadata_table_usi):

    if len(gnps_tall_table_usi) > 0:
        task = gnps_tall_table_usi.split(":")[2].split("-")[1]
        filepath = gnps_tall_table_usi.split(":")[2].split("-")[2]

        remote_url = "https://gnps.ucsd.edu/ProteoSAFe/DownloadResultFile?task={}&file={}".format(task, filepath)
        df = pd.read_csv(remote_url, sep=",")

        return df
    
    if len(gnps_quant_table_usi) > 0:
        #TODO: Implement This
        return pd.DataFrame()


# This determines which metadata they can select
@cache.memoize()
@app.callback([
                    Output("metadata_column", "options"), 
                    Output("facet_column", "options"), 
                    Output('animation_column', 'options'), 
                    Output("color_selection", "options"),

                    Output('lat_column', 'options'),
                    Output('long_column', 'options'),
                    Output('map_animation_column', 'options'),
              ],
              [
                  Input('gnps_tall_table_usi', 'value'),
                  Input('gnps_quant_table_usi', 'value'),
                  Input('gnps_metadata_table_usi', 'value'),
              ])
def determine_inputs(gnps_tall_table_usi, gnps_quant_table_usi, gnps_metadata_table_usi):
    triggered_id = [p['prop_id'] for p in dash.callback_context.triggered][0]

    df = _get_task_df(gnps_tall_table_usi, gnps_quant_table_usi, gnps_metadata_table_usi)
    
    block_columns = ["filename", "featureid", "featurearea", "featurert", "featuremz", "Compound_Name", "Smiles", "INCHI"]

    metadata_columns = list(df.keys())
    metadata_columns = [column for column in metadata_columns if not column in block_columns]
    metadata_columns = [ {"label": column, "value": column} for column in metadata_columns]

    import copy
    color_columns = copy.deepcopy(metadata_columns)
    color_columns.append({"label": "featureid", "value": "featureid"} )

    return [metadata_columns, metadata_columns, metadata_columns, color_columns, metadata_columns, metadata_columns, metadata_columns]

# This determines which groups they can select
@cache.memoize()
@app.callback([
                  Output('group_selection', 'options'), 
                  Output('group_selection', 'value')
              ],
              [
                  Input('gnps_tall_table_usi', 'value'),
                  Input('gnps_quant_table_usi', 'value'),
                  Input('gnps_metadata_table_usi', 'value'), 
                  Input("metadata_column", "value"), 
                  Input('url', 'search')])
def determine_inputs2(gnps_tall_table_usi, gnps_quant_table_usi, gnps_metadata_table_usi, metadata_column, search):
    query_dict = urllib.parse.parse_qs(search[1:])
    groups = []

    try:
        groups = query_dict["groups"][0].split(";")
    except:
        groups = []
        
    df = _get_task_df(gnps_tall_table_usi, gnps_quant_table_usi, gnps_metadata_table_usi)
        
    all_groups = list(set(df[metadata_column]))
    groups_options = [ {"label": str(group), "value": str(group)} for group in all_groups]

    # Select all of the columns if not in URL
    if len(groups) == 0:
        groups = all_groups

    return [groups_options, groups]


@app.callback([
                Output('plot_link', 'children')
              ],
              [
                  Input('gnps_tall_table_usi', 'value'),
                  Input('gnps_quant_table_usi', 'value'),
                  Input('gnps_metadata_table_usi', 'value'), 
                Input('feature', 'value'),
                Input("metadata_column", "value"),
                Input("facet_column", "value"),
                Input("animation_column", "value"),
                Input("group_selection", "value"),
                Input("color_selection", "value"),
                Input("theme", "value"),
                Input("plot_type", "value"),
                Input("image_export_format", "value"),
                Input("points_toggle", "value"),
                Input("log_axis", "value"),
                Input("lat_column", "value"),
                Input("long_column", "value"),
                Input("map_animation_column", "value"),
                Input("map_scope", "value"),
              ])
def draw_link(      gnps_tall_table_usi, 
                    gnps_quant_table_usi, 
                    gnps_metadata_table_usi, 
                    feature_id, 
                    metadata_column, 
                    facet_column, 
                    animation_column, 
                    group_selection, 
                    color_selection, 
                    theme, 
                    plot_type, 
                    image_export_format, 
                    points_toggle, 
                    log_axis,
                    lat_column,
                    long_column,
                    map_animation_column,
                    map_scope):
    # Creating Reproducible URL for Plot
    url_params = {}
    url_params["gnps_tall_table_usi"] = gnps_tall_table_usi
    url_params["gnps_quant_table_usi"] = gnps_quant_table_usi
    url_params["gnps_metadata_table_usi"] = gnps_metadata_table_usi

    url_params["feature"] = feature_id
    url_params["metadata"] = metadata_column
    url_params["facet"] = facet_column
    url_params["groups"] = ";".join(group_selection)
    url_params["plot_type"] = plot_type
    url_params["color"] = color_selection
    url_params["points_toggle"] = points_toggle
    url_params["theme"] = theme
    url_params["animation_column"] = animation_column

    # Mapping Options
    url_params["lat_column"] = lat_column
    url_params["long_column"] = long_column
    url_params["map_animation_column"] = map_animation_column
    url_params["map_scope"] = map_scope
    
    url_provenance = dbc.Button("Link to this Plot", block=True, color="primary", className="mr-1")
    provenance_link_object = dcc.Link(url_provenance, href="/?" + urllib.parse.urlencode(url_params) , target="_blank")

    return [provenance_link_object]


@app.callback([
                Output('debug-output', 'children')
              ],
              [
                  Input('gnps_tall_table_usi', 'value'),
                  Input('gnps_quant_table_usi', 'value'),
                  Input('gnps_metadata_table_usi', 'value'), 
                Input('feature', 'value'),
                Input("metadata_column", "value"),
                Input("facet_column", "value"),
                Input("animation_column", "value"),
                Input("group_selection", "value"),
                Input("color_selection", "value"),
                Input("theme", "value"),
                Input("plot_type", "value"),
                Input("image_export_format", "value"),
                Input("points_toggle", "value"),
                Input("log_axis", "value")
            ])
def draw_figure(gnps_tall_table_usi, gnps_quant_table_usi, gnps_metadata_table_usi, feature_id, metadata_column, facet_column, animation_column, group_selection, color_selection, theme, plot_type, image_export_format, points_toggle, log_axis):
    
    print(feature_id, metadata_column, group_selection)
    
    df = _get_task_df(gnps_tall_table_usi, gnps_quant_table_usi, gnps_metadata_table_usi)

    # Filtering to feature
    all_features = str(feature_id).split(",")
    all_features = [int(feature) for feature in all_features]
    df = df[df["featureid"].isin(all_features)]

    # Filtering the groups
    df = df[df[metadata_column].isin(group_selection)]
    
    # Drawing the Plot
    points = "outliers"
    if points_toggle:
        points = "all"

    color_column = None
    try:
        if len(color_selection) > 0:
            color_column = color_selection
    except:
        pass

    # Determing Log Axis
    log_y = log_axis

    # Group Ordering
    column_ordering = {}
    column_ordering[metadata_column] = group_selection

    # Adding prefix for groups
    if df[metadata_column].dtype == np.int64:
        df[metadata_column] = df[metadata_column].astype(str)
        df[metadata_column] = "G:" + df[metadata_column]

        column_ordering[metadata_column] = ["G:" + str(group) for group in column_ordering[metadata_column]]

    # TODO: Determining Animation
    animation_selection = None
    try:
        if len(animation_frame) > 0:
            animation_selection = str(animation_frame)
    except:
        pass

    if len(facet_column) == 0:
        facet_column = None

    if plot_type == "box":
        if facet_column is not None and len(facet_column) > 1:
            fig = px.box(df, x=metadata_column, y="featurearea", template=theme, facet_col=facet_column, color=color_column, points=points, facet_col_wrap=2, category_orders=column_ordering, log_y=log_y, animation_frame=animation_selection, animation_group="filename")
        else:
            if color_column == metadata_column:
                # This means we just want to color the boxes, but not to make them really small
                fig = px.box(df, x=metadata_column, y="featurearea", template=theme, color=color_column, boxmode="overlay", points=points, category_orders=column_ordering, log_y=log_y, animation_frame=animation_selection, animation_group="filename")
            else:
                # this means we want to separate box plots for each color
                fig = px.box(df, x=metadata_column, y="featurearea", template=theme, color=color_column, boxmode="group", points=points, category_orders=column_ordering, log_y=log_y, animation_frame=animation_selection, animation_group="filename")
    elif plot_type == "violin":
        if facet_column is not None and len(facet_column) > 1:
            fig = px.violin(df, x=metadata_column, y="featurearea", template=theme, facet_col=facet_column, color=color_column, points=points, facet_col_wrap=2, category_orders=column_ordering, log_y=log_y)
        else:
            fig = px.violin(df, x=metadata_column, y="featurearea", template=theme, color=color_column, points=points, category_orders=column_ordering, log_y=log_y)

    # Centering the Points
    fig.update_traces(pointpos=0)

    graph_config = {
        "toImageButtonOptions":{
            "format": image_export_format,
            'height': None, 
            'width': None,
        }
    }

    return [dcc.Graph(figure=fig, config=graph_config)]

@app.callback([
                Output('mapping_plot', 'children')
              ],
              [
                  Input('gnps_tall_table_usi', 'value'),
                  Input('gnps_quant_table_usi', 'value'),
                  Input('gnps_metadata_table_usi', 'value'), 
                  Input('feature', 'value'),
                  Input('lat_column', 'value'),
                  Input('long_column', 'value'),
                  Input("image_export_format", "value"),
                  Input("map_animation_column", "value"),
                  Input("map_scope", "value"),
                  Input("log_axis", "value")
            ])
def draw_map(gnps_tall_table_usi, gnps_quant_table_usi, gnps_metadata_table_usi, feature_id, lat_column, long_column, image_export_format, map_animation_column, map_scope, log_axis):
    df = _get_task_df(gnps_tall_table_usi, gnps_quant_table_usi, gnps_metadata_table_usi)

    # Filtering to feature
    all_features = str(feature_id).split(",")
    all_features = [int(feature) for feature in all_features]
    df = df[df["featureid"].isin(all_features)]

    graph_config = {
        "toImageButtonOptions":{
            "format": image_export_format,
            'height': None, 
            'width': None,
        }
    }

    # Preprocessing data
    if log_axis:
        df["featurearea"] = np.log2(df["featurearea"])

    if len(long_column) == 0:
        fig = px.scatter_geo(df, hover_name="featurearea",
                     color="featurearea",
                     size="featurearea", scope=map_scope)
    elif len(map_animation_column) > 0:
        fig = px.scatter_geo(df, lat=lat_column, lon=long_column, animation_frame=map_animation_column, 
                     hover_name="featurearea",
                     color="featurearea",
                     size="featurearea",
                     scope=map_scope)
    else:
        fig = px.scatter_geo(df, lat=lat_column, lon=long_column,
                     hover_name="featurearea",
                     color="featurearea",
                     size="featurearea",
                     scope=map_scope)

    return [dcc.Graph(figure=fig, config=graph_config)]



if __name__ == "__main__":
    app.run_server(debug=True, port=5000, host="0.0.0.0")
