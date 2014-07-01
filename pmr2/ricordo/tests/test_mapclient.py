import unittest
import requests
import json

from pmr2.ricordo.browser import mapclient


class MapClientTestCase(unittest.TestCase):
    """
    """

    def setUp(self):
        self.client = mapclient.MAPClientSearch(
            sparql_endpoint='http://localhost:8890/sparql')

    def test_format_query_none(self):
        self.assertIsNone(self.client.build_query())

    def test_format_query_one(self):
        self.assertEqual(self.client.build_query(
            workflow_object='workflowstep',
        ), 'SELECT ?g ?workflow_object WHERE { GRAPH ?g { ?workflow_object '
            '<http://www.w3.org/2000/01/rdf-schema#subClassOf> '
            '<http://physiomeproject.org/workflow/1.0/rdf-schema#'
            'workflowstep> . } }')

    def test_format_query_two(self):
        ontological_term = mapclient.iristr(
            '<http://purl.org/obo/owlapi/fma#FMA_24974>')
        self.assertEqual(self.client.build_query(
            workflow_object='workflowstep',
            workflow_predicate='workflowfor',
            ontological_term=ontological_term,
        ), 'SELECT ?g ?workflow_object ?workflow_predicate WHERE { GRAPH ?g '
            '{ '
                '?workflow_object '
                '<http://www.w3.org/2000/01/rdf-schema#subClassOf> '
                '<http://physiomeproject.org/workflow/1.0/rdf-schema#'
                'workflowstep> .'
                '\n'
                '?workflow_predicate '
                '<http://physiomeproject.org/workflow/1.0/rdf-schema#'
                'workflowfor> '
                '<http://purl.org/obo/owlapi/fma#FMA_24974> . '
            '} '
        '}')

    def test_format_query_missing_term(self):
        self.assertEqual(self.client.build_query(
            workflow_object='workflowstep',
            workflow_predicate='workflowfor',
        ), 'SELECT ?g ?workflow_object ?workflow_predicate ?ontological_term '
            'WHERE { GRAPH ?g '
            '{ '
                '?workflow_object '
                '<http://www.w3.org/2000/01/rdf-schema#subClassOf> '
                '<http://physiomeproject.org/workflow/1.0/rdf-schema#'
                'workflowstep> .'
                '\n'
                '?workflow_predicate '
                '<http://physiomeproject.org/workflow/1.0/rdf-schema#'
                'workflowfor> '
                '?ontological_term . '
            '} '
        '}')
