import pathlib
import pandas as pd
import dash_daq as daq
from datetime import date
import math

import dash
from dash import dcc, html, dash_table, Input, Output, State
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import ThemeChangerAIO
import dash_cytoscape as cyto

from utilities.ont import get_cytoscape_elements
from utilities.ont import get_sparql_query_results

# --------------------------------------------------
# ontology configuration details
#
# location of directory 'data'
BASE_PATH = pathlib.Path(__file__).parent.resolve()
DATA_PATH = BASE_PATH.joinpath("data").resolve()

# ontology names
ontologies_df = pd.read_csv(DATA_PATH.joinpath("ontologies.csv"))
ontology_names_as_list = ontologies_df["Name"].unique()

# ontology specific sparql queries
queries_list = pd.DataFrame()
df_query_results = ontologies_df.copy()

# ontology specific cytoscape data elements
ontology_view_elements = []

# ticker names
tickers_as_list = ['BTC', 'ETH', 'BNB', 'XRP']

# --------------------------------------------------
# bootstrap formatting
#
# format colors: primary, secondary, success, info, warning, danger, light, dark, link
# p-2 mb-2 text-left
title_format = "bg-light text-primary text-left"
footer_format = "bg-light text-primary text-left"
accordian_format = "bg-dark text-secondary text-center"
accordian_item_format = "bg-light text-link text-center"
textarea_format = "bg-light text-link text-left"
tab_active_format = "bg-dark text-secondary text-center"
tab_inactive_format = "bg-light text-primary text-center"
view_control_panel_format = "bg-light text-primary text-center"

# --------------------------------------------------
# instantiate the dash server
#
dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css"
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.SKETCHY, dbc_css])
app.config.suppress_callback_exceptions = True

####################################################################################################################
# top container
#
top_container = \
    dbc.Row(
        [
            dbc.Col(
                [
                    # html.Img(src='/assets/brandeis-logo.png', style={'height': '15%'}),
                ],
                width=2,
            ),
            dbc.Col(
                [

                    html.H1("Semantic Web Dashboard", style={"font-weight": "bold"}, className=title_format),
                ],
                width=10,
            ),
        ]
    )

####################################################################################################################
# bottom container
#
bottom_container = \
    dbc.Row(
        [
            dbc.Col(
                [
                    html.Img(src='/assets/brandeis-logo.png', style={'height': '15%'}),
                ],
                width=2,
            ),
            dbc.Col(
                [

                    html.H6("Developed by Brandeis University International Business School",
                            className=footer_format)
                ],
                width=10,
            ),
        ]
    )

####################################################################################################################
# sidebar container
#
sidebar_container = html.Div(
    [
        dbc.Accordion(
            [
                dbc.AccordionItem(
                    [
                        html.P("Select Ontology",
                               className=accordian_item_format,
                               style={"font-weight": "bold"}),
                        dcc.Dropdown(
                            id="ontology-select",
                            placeholder="Select",
                            options=[{"label": i, "value": i} for i in ontology_names_as_list],
                        ),
                        html.Br(),
                        html.P("Description",
                               className=accordian_item_format,
                               style={"text-decoration": "underline", "font-weight": "bold"}),
                        dcc.Markdown(
                            id="ontology-description",
                            children=[],
                            className=accordian_item_format
                        ),
                        html.Br(),
                        html.P("Endpoint",
                               className=accordian_item_format,
                               style={"text-decoration": "underline", "font-weight": "bold"}),
                        dcc.Markdown(
                            id="ontology-endpoint",
                            children=[],
                            className=accordian_item_format
                        ),
                        html.Br(),
                        html.P("Select SPARQL Query",
                               className=accordian_item_format,
                               style={"font-weight": "bold"}),
                        dcc.Dropdown(
                            id="sparql-query-select",
                            disabled=True,
                            options=[{"label": i, "value": i} for i in ontology_names_as_list],
                        ),
                        html.Br(),
                        html.Div(
                            id="submit-button-div",
                            children=[
                                dbc.Button(
                                    id="submit-button",
                                    children="Submit SPARQL Query",
                                    n_clicks=0,
                                    disabled=True,
                                    style={'width': '100%'},
                                ),
                            ],
                        ),
                    ],
                    title="Ontology",
                    className=accordian_item_format,
                ),
                dbc.AccordionItem(
                    [
                        ThemeChangerAIO(aio_id="theme"),
                    ],
                    title="Theme",
                    className=accordian_item_format
                ),
            ],
            start_collapsed=False, always_open=True, flush=True,
            className=accordian_format
        ),
    ],
)

####################################################################################################################
# body container
# view tab
#
body_container_view = \
    dbc.Row(
        [
            dbc.Col(
                [
                    html.Div(
                        [
                            html.Br(),
                            html.P("Control Panel", className=accordian_item_format),
                            dcc.Dropdown(
                                id='ontology-view-update-layout',
                                value='grid',
                                clearable=False,
                                options=[
                                    {'label': name.capitalize(), 'value': name}
                                    for name in ['random', 'grid', 'circle', 'concentric', 'breadthfirst']
                                ],
                            ),
                        ],
                    ),
                ],
                className=view_control_panel_format,
                width=1,
            ),
            dbc.Col(
                [
                    cyto.Cytoscape(
                        id='ontology-view',
                        elements=ontology_view_elements,
                        style={'width': '100%', 'height': '1000px'},
                    )
                ],
                width=10,
            ),
        ]
    )


@app.callback(
    Output('ontology-view', 'layout'),
    Input('ontology-view-update-layout', 'value'))
def update_layout(layout):
    return {'name': layout}


####################################################################################################################
# body container
# query tab
#
body_container_query = \
    html.Div(
        [
            dbc.Accordion(
                [
                    dbc.AccordionItem(
                        [
                            dbc.Row(
                                [
                                    dbc.Col(
                                        [
                                            html.P("Ticker 1",
                                                   className=accordian_item_format,
                                                   style={"font-weight": "bold"}
                                                   ),
                                            dcc.Dropdown(
                                                id="dropdown1-select",
                                                disabled=True,
                                            ),
                                            html.P("",
                                                   className=accordian_item_format,
                                                   style={"font-weight": "bold"}
                                                   ),
                                        ],
                                        width=2,
                                        style={
                                            'background-color': 'var(--bs-light)',
                                            'border-style': 'solid',
                                            'border-width': 'thin'
                                        }
                                    ),
                                    dbc.Col(
                                        [
                                            html.P("Ticker 2",
                                                   className=accordian_item_format,
                                                   style={"font-weight": "bold"}),
                                            dcc.Dropdown(
                                                id="dropdown2-select",
                                                disabled=True,
                                            ),
                                            html.P("",
                                                   className=accordian_item_format,
                                                   style={"font-weight": "bold"}
                                                   ),
                                        ],
                                        width=2,
                                        style={
                                            'background-color': 'var(--bs-light)',
                                            'border-style': 'solid',
                                            'border-width': 'thin'
                                        }
                                    ),
                                    dbc.Col(
                                        [
                                            html.P("Ticker 3",
                                                   className=accordian_item_format,
                                                   style={"font-weight": "bold"}
                                                   ),
                                            dcc.Dropdown(
                                                id="dropdown3-select",
                                                disabled=True,
                                            ),
                                            html.P("",
                                                   className=accordian_item_format,
                                                   style={"font-weight": "bold"}
                                                   ),
                                        ],
                                        width=2,
                                        style={
                                            'background-color': 'var(--bs-light)',
                                            'border-style': 'solid',
                                            'border-width': 'thin'
                                        }
                                    ),
                                    dbc.Col(
                                        [
                                            html.P("Ticker 4",
                                                   className=accordian_item_format,
                                                   style={"font-weight": "bold"}),
                                            dcc.Dropdown(
                                                id="dropdown4-select",
                                                disabled=True,
                                            ),
                                            html.P("",
                                                   className=accordian_item_format,
                                                   style={"font-weight": "bold"}
                                                   ),
                                        ],
                                        width=2,
                                        style={
                                            'background-color': 'var(--bs-light)',
                                            'border-style': 'solid',
                                            'border-width': 'thin'
                                        }
                                    ),
                                ],
                            ),
                            dbc.Row(
                                [
                                    dbc.Col(
                                        [
                                            html.P(" ",
                                                   className=accordian_item_format,
                                                   ),
                                        ],
                                        width=12,
                                    ),
                                ]
                            ),
                            dbc.Row(
                                [
                                    dbc.Col(
                                        [
                                            html.P("Date Range",
                                                   className=accordian_item_format,
                                                   style={"font-weight": "bold"}
                                                   ),
                                            dcc.DatePickerRange(
                                                id='date-range-picker-select',
                                                clearable=True,
                                                disabled=True,
                                            ),
                                        ],
                                        width=2,
                                        style={
                                            'background-color': 'var(--bs-light)',
                                            'border-style': 'solid',
                                            'border-width': 'thin'
                                        }
                                    ),
                                    dbc.Col(
                                        [
                                            html.P("Precision",
                                                   className=accordian_item_format,
                                                   style={"font-weight": "bold"}
                                                   ),
                                            daq.Knob(
                                                id='precision-knob-select',
                                                label="Number of Decimal Points",
                                                labelPosition='bottom',
                                                value=2,
                                                min=0,
                                                max=8,
                                                scale={'start': 0, 'labelInterval': 2, 'interval': 2},
                                                color={"ranges": {"green": [0, 4], "yellow": [4, 6], "red": [6, 8]}},
                                                disabled=True
                                            ),
                                        ],
                                        width=2,
                                        style={
                                            'background-color': 'var(--bs-light)',
                                            'border-style': 'solid',
                                            'border-width': 'thin'
                                        }
                                    ),
                                ],
                            )
                        ],
                        title="Parameters",
                    ),
                    dbc.AccordionItem(
                        [
                            dcc.Textarea(
                                id='sparql-query-text',
                                value='',
                                cols='4',
                                disabled=True,
                                style={'width': '100%', 'height': 200},
                                className=textarea_format
                            ),
                        ],
                        title="Query",
                    ),
                    dbc.AccordionItem(
                        [
                            dash_table.DataTable(
                                id='query-results-table',
                                data=df_query_results.to_dict('records'),
                                columns=[{'id': c, 'name': c} for c in ontologies_df.columns],

                                page_current=0,
                                page_size=25,
                                fixed_rows={'headers': True},

                                style_cell={'textAlign': 'left'},
                                style_as_list_view=True,

                                row_deletable=False,
                                editable=False,
                                filter_action="native",
                                sort_action="native",
                                style_table={"overflowX": "auto", 'overflowY': 'auto'},
                                export_format="csv",
                            )
                        ],
                        title="Query Results",
                    ),
                ],
                start_collapsed=False, always_open=True, flush=True,
            ),
        ],
    )

####################################################################################################################
# body container
#
tab_view = dbc.Tab(
    body_container_view, label="View",
    label_class_name=tab_inactive_format,
    active_label_class_name=tab_active_format,
)
tab_query = dbc.Tab(
    body_container_query, label="Query",
    label_class_name=tab_inactive_format,
    active_label_class_name=tab_active_format,
)
body_container = dbc.Card(
    dbc.Tabs([tab_query, tab_view])
)

####################################################################################################################
# layout
#
app.layout = dbc.Container(
    [
        top_container,
        dbc.Row(
            [
                dbc.Col(
                    [
                        sidebar_container,
                    ],
                    width=2,
                ),
                dbc.Col(
                    [
                        body_container,
                    ],
                    width=10,
                ),
            ]
        ),
        bottom_container,
    ],
    fluid=True,
)


####################################################################################################################
# callbacks
#
@app.callback(
    Output("ontology-description", "children"),
    Output("ontology-endpoint", "children"),
    Output("sparql-query-select", "options"),
    Output("sparql-query-select", "disabled"),
    [Input("ontology-select", "value")]
)
def ontology_select_dropdown_selected(ontology_selected):
    if ontology_selected is None:
        return '', '', [{"label": i, "value": i} for i in ontology_names_as_list], True

    # get attributes regarding the selected ontology
    df = ontologies_df.query(f'Name == "{ontology_selected}"')
    ontology_description = df['Description'].unique()[0]
    ontology_endpoint = df['Endpoint'].unique()[0]
    sparql_query_file = df['Sparql'].unique()[0]
    sparql_query_df = pd.read_csv(DATA_PATH.joinpath(sparql_query_file))
    query_name_list = sparql_query_df['Name'].unique()
    sparql_query_options = []
    for q in query_name_list:
        sparql_query_options.append({'label': q, 'value': q})

    return ontology_description, ontology_endpoint, sparql_query_options, False


@app.callback(
    Output("sparql-query-text", "value"),
    Output("sparql-query-text", "disabled"),
    Output("submit-button", "disabled"),
    Output("dropdown1-select", "disabled"),
    Output("dropdown1-select", "placeholder"),
    Output("dropdown1-select", "options"),
    Output("dropdown2-select", "disabled"),
    Output("dropdown2-select", "placeholder"),
    Output("dropdown2-select", "options"),
    Output("dropdown3-select", "disabled"),
    Output("dropdown3-select", "placeholder"),
    Output("dropdown3-select", "options"),
    Output("dropdown4-select", "disabled"),
    Output("dropdown4-select", "placeholder"),
    Output("dropdown4-select", "options"),
    Output("date-range-picker-select", "disabled"),
    Output("precision-knob-select", "disabled"),
    [Input("sparql-query-select", "value")],
    [State("ontology-select", "value")]
)
def sparql_query_select_dropdown_selected(query_selected, ontology_selected):
    if ontology_selected is None or query_selected is None:
        return ('', True, True,
                True, 'Disabled', [],
                True, 'Disabled', [],
                True, 'Disabled', [],
                True, 'Disabled', [],
                True,
                True,
                )

    df = ontologies_df.query(f'Name == "{ontology_selected}"')
    sparql_query_file = df['Sparql'].unique()[0]
    sparql_query_df = pd.read_csv(DATA_PATH.joinpath(sparql_query_file))
    sparql_query_df.query(f'Name == "{query_selected}"', inplace=True)
    sparql_query = sparql_query_df['Sparql'].unique()[0]

    # determine which of the parameters control are needed for this query

    return (sparql_query, False, False,
            False, 'Select', [{'label': t, 'value': t} for t in tickers_as_list],
            False, 'Select', [{'label': t, 'value': t} for t in tickers_as_list],
            False, 'Select', [{'label': t, 'value': t} for t in tickers_as_list],
            False, 'Select', [{'label': t, 'value': t} for t in tickers_as_list],
            False,
            False)


@app.callback(
    Output("query-results-table", "data"),
    Output("query-results-table", "columns"),
    Output("ontology-view", "elements"),
    [Input("submit-button", "n_clicks")],
    [State("ontology-endpoint", "children"),
     State("sparql-query-text", "value"),
     State("dropdown1-select", "value"),
     State("dropdown2-select", "value"),
     State("dropdown3-select", "value"),
     State("dropdown4-select", "value"),
     State("date-range-picker-select", "start_date"),
     State("date-range-picker-select", "end_date"),
     State("precision-knob-select", "value")
     ]
)
def submit_button_selected(n_clicks, ontology_endpoint, sparql_query_template,
                           dropdown_1, dropdown_2, dropdown_3, dropdown_4,
                           start_date, end_date, precision):
    if n_clicks == 0 or ontology_endpoint is None or sparql_query_template is None:
        data = ontologies_df.to_dict('records')
        columns = [{'id': c, 'name': c} for c in ontologies_df.columns]
        return data, columns, ontology_view_elements

    sparql_query_text = sparql_query_template
    start, end = "<<", ">>"
    start_index = 0
    while True:
        idx_1 = sparql_query_template.find(start, start_index)
        if idx_1 == -1:
            break
        idx_2 = sparql_query_template.find(end, start_index+len(start))
        if idx_2 == -1:
            break
        tag = sparql_query_template[idx_1+len(start): idx_2]
        name_value = tag.split(':')

        if name_value[1].strip() == 'dropdown1':
            sparql_query_text = sparql_query_text.replace(name_value[0], dropdown_1)
        elif name_value[1].strip() == 'dropdown2':
            sparql_query_text = sparql_query_text.replace(name_value[0], dropdown_2)
        elif name_value[1].strip() == 'dropdown3':
            sparql_query_text = sparql_query_text.replace(name_value[0], dropdown_3)
        elif name_value[1].strip() == 'dropdown4':
            sparql_query_text = sparql_query_text.replace(name_value[0], dropdown_4)
        elif name_value[1].strip() == 'start_date':
            sparql_query_text = sparql_query_text.replace(name_value[0], start_date)
        elif name_value[1].strip() == 'end_date':
            sparql_query_text = sparql_query_text.replace(name_value[0], end_date)
        elif name_value[1].strip() == 'precision':
            sparql_query_text = sparql_query_text.replace('precision', str(math.pow(10, int(precision))))

        start_index = idx_2

    print(sparql_query_text)
    results_table, results_columns = get_sparql_query_results(ontology_endpoint, sparql_query_text)
    cytoscape_elements = get_cytoscape_elements(ontology_endpoint)

    return results_table, results_columns, cytoscape_elements


##############################################
# Run the server
#
if __name__ == "__main__":
    app.run_server(debug=True)
