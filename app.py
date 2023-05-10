import pathlib
import pandas as pd

import dash
from dash import dcc, html, dash_table, Input, Output, State
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import ThemeChangerAIO
import dash_cytoscape as cyto

from utilities.ont import get_cytoscape_elements
from utilities.ont import get_sparql_query_results

# configuration details
#
# data location
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

# format colors: primary, secondary, success, info, warning, danger, light, dark, link
# p-2 mb-2 text-left
title_format = "bg-light text-black text-left"
footer_format = "bg-light text-black text-left"
accordian_format = "bg-dark text-white text-center"
accordian_item_format = "bg-light text-black text-center"
textarea_format = "bg-dark text-white text-left"
tab_active_format = "bg-dark text-white text-center"
tab_inactive_format = "bg-light text-black text-center"
view_control_panel_format = "bg-light text-black text-center"

# instantiate the Dash server
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

                    html.H1("Semantic Web Dashboard", className=title_format),
                ],
                width=12,
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
                    html.Img(src='/assets/brandeis-logo.png', style={'height': '10%'}),
                ],
                width=2,
            ),
            dbc.Col(
                [

                    html.H6("Dashboard developed by faculty and students of the "
                            "Brandeis University International Business School", className=footer_format)
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
                               className=accordian_item_format),
                        dcc.Dropdown(
                            id="ontology-select",
                            placeholder="Select",
                            options=[{"label": i, "value": i} for i in ontology_names_as_list],
                        ),
                        html.Br(),
                        html.P("Description",
                               className=accordian_item_format,
                               style={"text-decoration": "underline"}),
                        dcc.Markdown(
                            id="ontology-description",
                            children=[],
                            className=accordian_item_format
                        ),
                        html.Br(),
                        html.P("Endpoint",
                               className=accordian_item_format,
                               style={"text-decoration": "underline"}),
                        dcc.Markdown(
                            id="ontology-endpoint",
                            children=[],
                            className=accordian_item_format
                        ),

                        html.Br(),
                        html.P("Select SPARQL Query",
                               className=accordian_item_format),
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
                    className=accordian_item_format
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
                            dcc.Textarea(
                                id='sparql-query-text',
                                value='',
                                cols='4',
                                disabled=True,
                                style={'width': '100%', 'height': 200},
                                className=textarea_format
                            ),
                        ],
                        title="SPARQL Query",
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
    dbc.Tabs([tab_view, tab_query])
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
    [Input("sparql-query-select", "value")],
    [State("ontology-select", "value")]
)
def sparql_query_select_dropdown_selected(query_selected, ontology_selected):
    if ontology_selected is None or query_selected is None:
        return '', True, True

    df = ontologies_df.query(f'Name == "{ontology_selected}"')
    sparql_query_file = df['Sparql'].unique()[0]
    sparql_query_df = pd.read_csv(DATA_PATH.joinpath(sparql_query_file))
    sparql_query_df.query(f'Name == "{query_selected}"', inplace=True)
    sparql_query = sparql_query_df['Sparql'].unique()[0]
    return sparql_query, False, False


@app.callback(
    Output("query-results-table", "data"),
    Output("query-results-table", "columns"),
    Output("ontology-view", "elements"),
    [Input("submit-button", "n_clicks")],
    [State("ontology-endpoint", "children"),
     State("sparql-query-text", "value")]
)
def submit_button_selected(n_clicks, ontology_endpoint, sparql_query_text):
    if n_clicks == 0 or ontology_endpoint is None or sparql_query_text is None:
        data = ontologies_df.to_dict('records')
        columns = [{'id': c, 'name': c} for c in ontologies_df.columns]
        return data, columns, ontology_view_elements

    results_table, results_columns = get_sparql_query_results(ontology_endpoint, sparql_query_text)
    cytoscape_elements = get_cytoscape_elements(ontology_endpoint)

    return results_table, results_columns, cytoscape_elements


##############################################
# Run the server
#
if __name__ == "__main__":
    app.run_server(debug=True)
