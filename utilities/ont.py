import pandas as pd

import networkx as nx
import ontospy
from ontospy.gendocs.viz.viz_html_single import *

from rdflib import Graph
from rdflib.extras.external_graph_libs import rdflib_to_networkx_graph


def get_sparql_query_results(endpoint, query_text):
    g = build_ontology_as_rdflib_graph(endpoint)
    query_results = g.query(query_text)
    result_list_df = pd.DataFrame(query_results.bindings)
    columns = [{'name': index, 'id': index} for index in result_list_df.columns]
    return result_list_df.to_dict('records'), columns


def build_html_visualizer(endpoint):
    g = ontospy.Ontospy(endpoint)

    v = HTMLVisualizer(g)
    v.build()
    v.preview()


def build_ontology_as_rdflib_graph(path, fmt='application/rdf+xml'):
    g = Graph()
    g.parse(path, format=fmt)
    return g


def build_ontology_as_networkx(path, fmt='application/rdf+xml'):
    g = build_ontology_as_rdflib_graph(path, fmt)
    g = rdflib_to_networkx_graph(g)
    return g


def get_cytoscape_elements(endpoint):
    g = build_ontology_as_networkx(endpoint)
    cy = nx.readwrite.json_graph.cytoscape_data(g)

    for n in cy['elements']['nodes']:
        for k, v in n.items():
            v['label'] = v.pop('value')
            v['label'] = str(v['label'])
            del v['name']

    for n in cy['elements']['edges']:
        for k, v in n.items():
            v['source'] = str(v['source'])
            v['target'] = str(v['target'])
            del v['weight']

    elements = cy['elements']['nodes'] + cy['elements']['edges']
    return elements
