import unittest
import requests
import json

from pmr2.ricordo import client

from .base import owlkb_test_available
from .base import rdfstore_test_available
from .base import virtuoso_test_available


@unittest.skipUnless(owlkb_test_available(),
        "OWLKB Webservice is not running.")
class LiveOwlClientTestCase(unittest.TestCase):
    """
    Test cases that requires Tomcat running with the RICORDO owlkb
    webservices installed and running with the Gene Ontology (go.owl)
    defined as the actilve knowledgebase.
    """

    level = 10

    def setUp(self):
        self.client = client.OwlkbClient()

    def test_query(self):
        results = self.client.query_terms('GO_0005886')
        self.assertEqual(len(results), 3)

    def test_regulates_some_query(self):
        results = self.client.query_terms('regulates some GO_0005978')
        self.assertTrue(len(results) > 1)


@unittest.skipUnless(rdfstore_test_available(),
        "Ricordo RDFStore endpoint not running.")
class LiveRicordoClientTestCase(unittest.TestCase):
    """
    Test cases that requires Tomcat running with the RICORDO owlkb
    webservices installed and running with the Gene Ontology (go.owl)
    defined as the actilve knowledgebase.
    """

    level = 10

    def setUp(self):
        self.client = client.RdfStoreClient()

    def test_search_getResourceForAnnotation(self):
        results = self.client.getResourceForAnnotation(
            'http://identifiers.org/obo.go/GO:0031594',
        )
        self.assertTrue(len(results) > 0)

    def test_search_getAnnotationOfResource(self):
        results = self.client.getAnnotationOfResource(
            'http://www.ebi.ac.uk/ricordo/toolbox/sbmlo#BIOMD0000000002_comp1',
        )
        n = results[0]
        self.assertEqual(n['g']['value'],
            'http://ricordo.com')
        self.assertEqual(n['p']['value'],
            'http://biomodels.net/biology-qualifiers#is')
        self.assertEqual(n['a']['value'],
            'http://identifiers.org/obo.go/GO:0031594')


@unittest.skipUnless(virtuoso_test_available(),
        "Virtuso SPARQL endpoint not available.")
class LiveOwlSparqlClientTestCase(unittest.TestCase):
    """
    Test cases that requires Virutoso running with both the FMA and
    GO owl graphs added at the specific designated URLs listed here.
    """

    level = 10

    def setUp(self):
        self.client = client.OwlSparqlClient(graph_urls=(
            'http://models.example.com/go.owl',
            'http://models.example.com/fma.owl',
        ))

    def test_list_all_terms(self):
        results = self.client.get_owl_terms('plasma membrane')
        self.assertEqual(len(results), 230)

    def test_list_go_only(self):
        results = self.client.get_owl_terms('plasma membrane', graph_urls=(
            'http://models.example.com/go.owl',
        ))
        self.assertEqual(len(results), 109)
