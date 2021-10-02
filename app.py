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
import urllib.parse
import pandas as pd
import requests

import numpy as np
import urllib
import json

from flask import Flask, send_from_directory, request
from collections import defaultdict
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
    dbc.CardHeader(
        dbc.Row([
            dbc.Col(html.H5("Data Selection")),
            dbc.Col(
                dbc.Button(
                    "Copy Link to Plot",
                    color="primary",
                    size="sm",
                    className="mr-1",
                    style={"float": "right"},
                    id="copy_link_button",
                ),
            ),
        ])),
    dbc.CardBody(
        [   
            html.H5("USI Data Selection"),
            dbc.InputGroup(
                [
                    dbc.InputGroupAddon("Spectrum USI1", addon_type="prepend"),
                    dbc.Input(id='usi1', placeholder="Enter GNPS USI", value=""),
                ],
                className="mb-3",
            ),
            html.Hr(),
            dbc.InputGroup(
                [
                    dbc.InputGroupAddon("Spectrum USI2", addon_type="prepend"),
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
            dbc.InputGroup(
                [
                    dbc.InputGroupAddon("Peak Filtering Options", addon_type="prepend"),
                    dbc.Checklist(
                        options=[
                            {"label": "Top 6 in +/- 50 Da", "value": "window"},
                            {"label": "Precursor Filter", "value": "precursor"},
                        ],
                        value=[],
                        id="filter_switches",
                        switch=True,
                    ),
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
            )
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
                    href="https://www.nature.com/articles/nbt.3597"),
            html.Br(),
            html.Br(),
            html.A('Huber, F., Ridder, L., Verhoeven, S., Spaaks, J. H., Diblen, F., Rogers, S., & van der Hooft, J. J. (2021). Spec2Vec: Improved mass spectral similarity scoring through learning of structural relationships. PLoS computational biology, 17(2), e1008724.', 
                    href="https://journals.plos.org/ploscompbiol/article?rev=1&id=10.1371/journal.pcbi.1008724"),
            html.Br(),
            html.Br(),
            html.A('Treen, Daniel GC, Trent R. Northen, and Ben Bowen. "SIMILE enables alignment of fragmentation mass spectra with statistical significance." bioRxiv (2021).', 
                    href="https://www.biorxiv.org/content/10.1101/2021.02.24.432767v1"),
            html.Br(),
            html.Br(),
            html.A('Huber, F., Verhoeven, S., Meijer, C., Spreeuw, H., Castilla, E., Geng, C., ... & Spaaks, J. (2020). matchms-processing and similarity evaluation of mass spectrometry data. Journal of Open Source Software, 5(52).', 
                    href="https://eprints.gla.ac.uk/222785/"),
            html.Br(),
            html.Br(),
            html.A('Florian Huber, Sven van der Burg, Justin J.J. van der Hooft, Lars Ridder.  MS2DeepScore - a novel deep learning similarity measure for mass fragmentation spectrum comparisons', 
                    href="https://www.biorxiv.org/node/1907063"),
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
        html.Div(
            [
                dcc.Link(id="query_link", href="#", target="_blank"),
            ],
            style={
                    "display" :"none"
            }
        ),
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
                Output('peak_tolerance', 'value'),
                Output('filter_switches', 'value')
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
    filter_switches = _get_url_param(query_dict, "filter_switches", dash.no_update)

    return [usi1, usi2, peak_tolerance, filter_switches]


@app.callback([
                Output('query_link', 'href'),
              ],
              [
                  Input('usi1', 'value'),
                  Input('usi2', 'value'),
                  Input('peak_tolerance', 'value'),
                  Input('filter_switches', 'value'),
              ])
def draw_link(      usi1, usi2, peak_tolerance, filter_switches):
    # Creating Reproducible URL for Plot
    url_params = {}
    url_params["usi1"] = usi1
    url_params["usi2"] = usi2
    url_params["peak_tolerance"] = peak_tolerance
    url_params["filter_switches"] = filter_switches

    url_params = urllib.parse.urlencode(url_params)

    return [request.host_url + "/?" + url_params]

app.clientside_callback(
    """
    function(n_clicks, button_id, text_to_copy) {
        original_text = "Copy Link"
        if (n_clicks > 0) {
            const el = document.createElement('textarea');
            el.value = text_to_copy;
            document.body.appendChild(el);
            el.select();
            document.execCommand('copy');
            document.body.removeChild(el);
            setTimeout(function(id_to_update, text_to_update){ 
                return function(){
                    document.getElementById(id_to_update).textContent = text_to_update
                }}(button_id, original_text), 1000);
            document.getElementById(button_id).textContent = "Copied!"
            return 'Copied!';
        } else {
            return original_text;
        }
    }
    """,
    Output('copy_link_button', 'children'),
    [
        Input('copy_link_button', 'n_clicks'),
        Input('copy_link_button', 'id'),
    ],
    [
        State('query_link', 'href'),
    ]
)

@cache.memoize()
def get_usi_peaks(usi):
    url = "https://metabolomics-usi.ucsd.edu/json/?usi1={}".format(usi)
    r = requests.get(url)
    return r.json()

@cache.memoize()
def get_usi_peaks_pairs(usi1, usi2, tolerance):
    url = "https://metabolomics-usi.ucsd.edu/json/mirror/?usi1={}&usi2={}&cosine=shifted&fragment_mz_tolerance={}".format(usi1, usi2, tolerance)
    result = requests.get(url).json()

    return result


@cache.memoize()
def _calculate_scores_usi(usi1, usi2, alignment_params={}):
    # Getting the USI
    pair_spectrum_results = get_usi_peaks_pairs(usi1, usi2, alignment_params["peak_tolerance"])
    spec1 = pair_spectrum_results["spectrum1"]
    spec2 = pair_spectrum_results["spectrum2"]

    real_result_list = _calculate_scores_peaks(spec1, spec2, alignment_params=alignment_params)

    real_result_list.append({
                            "sim":pair_spectrum_results["cosine"], 
                            "matched_peaks":pair_spectrum_results["n_peak_matches"],
                            "type": "usi"
                            })

        
    return real_result_list

def _calculate_scores_peaks(spec1, spec2, alignment_params={}):
    # TODO: Do the filtering here
    matchms_modified_cosine_results = tasks.tasks_compute_similarity_matchms.delay(spec1, spec2, scoring_function="modified_cosine", alignment_params=alignment_params)
    matchms_greedy_results = tasks.tasks_compute_similarity_matchms.delay(spec1, spec2, scoring_function="cosine_greedy", alignment_params=alignment_params)

    spec2vec_results = tasks.tasks_compute_similarity_spec2vec.delay(spec1, spec2, alignment_params=alignment_params)
    ms2deepscore_results = tasks.tasks_compute_similarity_ms2deepscore.delay(spec1, spec2, alignment_params=alignment_params)
    simile_results = tasks.tasks_compute_similarity_simile.delay(spec1, spec2, alignment_params=alignment_params)
    gnps_results = tasks.tasks_compute_similarity_gnpsalignment.delay(spec1, spec2, alignment_params=alignment_params)
    
    result_list = [ matchms_modified_cosine_results,
                    matchms_greedy_results, 
                    spec2vec_results,
                    ms2deepscore_results, 
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
                  Input('peak_tolerance', 'value'),
                  Input('filter_switches', 'value'),
            ])
def draw_output(usi1, usi2, peak_tolerance, filter_switches):
    alignment_params = {}
    alignment_params["peak_tolerance"] = float(peak_tolerance)
    alignment_params["precursor_filter"] = "precursor_filter" in filter_switches
    alignment_params["window_filter"] = "window_filter" in filter_switches

    real_result_list = _calculate_scores_usi(usi1, usi2, alignment_params=alignment_params)

    # Showing the spectra
    image_obj = html.Img(
        src='https://metabolomics-usi.ucsd.edu/svg/mirror?usi1={}&usi2={}&cosine=shifted&fragment_mz_tolerance={}'.format(usi1, usi2, peak_tolerance),
    )
    
    table = dbc.Table.from_dataframe(pd.DataFrame(real_result_list), striped=True, bordered=True, hover=True)

    return [[image_obj, html.Br(), table]]

# API
@server.route("/api/comparison", methods = ['POST', 'GET'])
def comparison_api():
    if "usi1" in request.values:
        # USI version
        usi1 = request.values.get("usi1")
        usi2 = request.values.get("usi2")

        all_results = _calculate_scores_usi(usi1, usi2, alignment_params=dict(request.values))
    else:
        # Peaks version
        spec1 = json.loads(request.values.get("spec1"))
        spec2 = json.loads(request.values.get("spec2"))

        all_results = _calculate_scores_peaks(spec1, spec2, alignment_params=dict(request.values))


    return json.dumps(all_results) 



if __name__ == "__main__":
    app.run_server(debug=True, port=5000, host="0.0.0.0")
