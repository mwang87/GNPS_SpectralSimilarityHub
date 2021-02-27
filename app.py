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
from flask import Flask, send_from_directory, request

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
import tasks


server = Flask(__name__)
app = dash.Dash(__name__, server=server, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = 'GNPS - Similarity'

cache = Cache(app.server, config={
#    'CACHE_TYPE': 'filesystem',
    'CACHE_TYPE': 'null',
    'CACHE_DIR': 'temp/flask-cache',
    'CACHE_DEFAULT_TIMEOUT': 0,
    'CACHE_THRESHOLD': 1000000000
})

server = app.server

app.index_string = """<!DOCTYPE html>
<html>
    <head>
        <!-- Global site tag (gtag.js) - Google Analytics -->
        <script async src="https://www.googletagmanager.com/gtag/js?id=G-V9006NL7V1"></script>
        <script>
            window.dataLayer = window.dataLayer || [];
            function gtag(){dataLayer.push(arguments);}
            gtag('js', new Date());

            gtag('config', 'G-V9006NL7V1');
        </script>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>"""

NAVBAR = dbc.Navbar(
    children=[
        dbc.NavbarBrand(
            html.Img(src="https://gnps-cytoscape.ucsd.edu/static/img/GNPS_logo.png", width="120px"),
            href="https://gnps.ucsd.edu"
        ),
        dbc.Nav(
            [
                dbc.NavItem(dbc.NavLink("GNPS - Similarity Dashboard - Version 0.1", href="#")),
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
                    dbc.InputGroupAddon("Spectrum USI", addon_type="prepend"),
                    dbc.Input(id='usi1', placeholder="Enter GNPS USI", value=""),
                ],
                className="mb-3",
            ),
            html.Hr(),
            dbc.InputGroup(
                [
                    dbc.InputGroupAddon("Spectrum USI", addon_type="prepend"),
                    dbc.Input(id='usi2', placeholder="Enter GNPS USI", value=""),
                ],
                className="mb-3",
            ),
            html.Br(),
            dbc.InputGroup(
                [
                    dbc.InputGroupAddon("MS2 Peak Tolerance", addon_type="prepend"),
                    dbc.Input(id='peak_tolerance', placeholder="Enter Tolerance", value="0.5"),
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
                id="output",
                children=[html.Div([html.Div(id="loading-output-23")])],
                type="default",
            ),
            dcc.Loading(
                id="plot_link",
                children=[html.Div([html.Div(id="loading-output-42")])],
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
            html.A('Basic 14 Da Delta', href="/?usi1=mzspec%3AGNPS%3ATASK-c94f9f981fd8438c9a27d57a228fe08e-spectra%2Fspecs_ms.mgf%3Ascan%3A1&usi2=mzspec%3AGNPS%3ATASK-c94f9f981fd8438c9a27d57a228fe08e-spectra%2Fspecs_ms.mgf%3Ascan%3A260"),
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
                Output('usi1', 'value'), 
                Output('usi2', 'value'), 
                Output('peak_tolerance', 'value')
              ],
              [
                  Input('url', 'search')
              ])
def determine_task(search):
    
    try:
        query_dict = urllib.parse.parse_qs(search[1:])
    except:
        query_dict = {}

    # usi1 = _get_url_param(query_dict, "usi1", 'mzspec:MSV000082796:KP_108_Positive:scan:1974')
    # usi2 = _get_url_param(query_dict, "usi2", 'mzspec:MSV000082796:KP_108_Positive:scan:1977')

    usi1 = _get_url_param(query_dict, "usi1", 'mzspec:GNPS:TASK-c95481f0c53d42e78a61bf899e9f9adb-spectra/specs_ms.mgf:scan:1943')
    usi2 = _get_url_param(query_dict, "usi2", 'mzspec:GNPS:TASK-c95481f0c53d42e78a61bf899e9f9adb-spectra/specs_ms.mgf:scan:1943')
    peak_tolerance = _get_url_param(query_dict, "peak_tolerance", dash.no_update)

    return [usi1, usi2, peak_tolerance]


@app.callback([
                Output('plot_link', 'children')
              ],
              [
                  Input('usi1', 'value'),
                  Input('usi2', 'value'),
                  Input('peak_tolerance', 'value')
              ])
def draw_link(      usi1, usi2, peak_tolerance):
    # Creating Reproducible URL for Plot
    url_params = {}
    url_params["usi1"] = usi1
    url_params["usi2"] = usi2
    url_params["peak_tolerance"] = peak_tolerance
    
    url_provenance = dbc.Button("Link to this Plot", block=True, color="primary", className="mr-1")
    provenance_link_object = dcc.Link(url_provenance, href="/?" + urllib.parse.urlencode(url_params) , target="_blank")

    return [provenance_link_object]


@cache.memoize()
def get_usi_peaks(usi):
    url = "https://metabolomics-usi.ucsd.edu/json/?usi={}".format(usi)
    r = requests.get(url)
    return r.json()

@cache.memoize()
def _calculate_scores(usi1, usi2, alignment_params={}):
    # Getting the USI
    spec1 = get_usi_peaks(usi1)
    spec2 = get_usi_peaks(usi2)

    usi_results = tasks.tasks_compute_similarity_usi.delay(spec1, spec2, alignment_params=alignment_params)
    matchms_modified_cosine_results = tasks.tasks_compute_similarity_matchms.delay(spec1, spec2, scoring_function="modified_cosine", alignment_params=alignment_params)
    matchms_greedy_results = tasks.tasks_compute_similarity_matchms.delay(spec1, spec2, scoring_function="cosine_greedy", alignment_params=alignment_params)

    spec2vec_results = tasks.tasks_compute_similarity_spec2vec.delay(spec1, spec2, alignment_params=alignment_params)
    simile_results = tasks.tasks_compute_similarity_simile.delay(spec1, spec2, alignment_params=alignment_params)
    gnps_results = tasks.tasks_compute_similarity_gnpsalignment.delay(spec1, spec2, alignment_params=alignment_params)
    
    result_list = [ matchms_modified_cosine_results,
                    matchms_greedy_results, 
                    spec2vec_results,
                    simile_results, 
                    gnps_results]

    real_result_list = []

    for result in result_list:
        try:
            result = result.get()
            real_result_list.append(result)
        except:
            pass
        
    return real_result_list

@app.callback([
                Output('output', 'children')
              ],
              [
                  Input('usi1', 'value'),
                  Input('usi2', 'value'),
                  Input('peak_tolerance', 'value')
            ])
def draw_output(usi1, usi2, peak_tolerance):
    alignment_params = {}
    alignment_params["peak_tolerance"] = float(peak_tolerance)

    real_result_list = _calculate_scores(usi1, usi2, alignment_params=alignment_params)

    # Showing the spectra
    image_obj = html.Img(
        src='https://metabolomics-usi.ucsd.edu/svg/mirror?usi1={}&usi2={}&cosine=shifted&fragment_mz_tolerance={}'.format(usi1, usi2, peak_tolerance),
    )
    
    table = dbc.Table.from_dataframe(pd.DataFrame(real_result_list), striped=True, bordered=True, hover=True)

    return [[image_obj, html.Br(), table]]

# API
@server.route("/api/comparison")
def comparison_api():
    usi1 = request.values.get("usi1")
    usi2 = request.values.get("usi2")

    all_results = _calculate_scores(usi1, usi2)

    return json.dumps(all_results) 



if __name__ == "__main__":
    app.run_server(debug=True, port=5000, host="0.0.0.0")
