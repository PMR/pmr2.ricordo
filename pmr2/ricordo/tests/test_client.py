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

    level = 20

    def setUp(self):
        self.client = client.OwlkbClient()

    def test_query(self):
        results = self.client.query_terms('GO_0005886')
        self.assertEqual(len(results), 3)

    def test_regulates_some_query(self):
        results = self.client.query_terms('regulates some GO_0005978')
        self.assertTrue(len(results) > 1)


@unittest.skipUnless(virtuoso_test_available(),
        "Virtuoso is not running")
class LiveSimpleOwlClientTestCase(unittest.TestCase):
    """
    Test cases that requires Tomcat running with the RICORDO owlkb
    webservices installed and running with the Gene Ontology (go.owl)
    defined as the actilve knowledgebase.
    """

    level = 10

    def setUp(self):
        self.client = client.SimpleOwlkbClient()

    def test_query(self):
        results = self.client.query_terms(
            'http://purl.org/obo/owlapi/fma#FMA_9611')
        self.assertEqual(sorted(results), [
            'http://purl.org/obo/owlapi/fma#FMA_24474',
            'http://purl.org/obo/owlapi/fma#FMA_24475',
            'http://purl.org/obo/owlapi/fma#FMA_9611',
        ])

    def test_query_short_go(self):
        results = self.client.query_terms('GO_0005886')
        # Instead of 3 results, only 2 as we don't provide the dummy
        # 'Nothing' value.
        self.assertEqual(len(results), 2)

    def test_query_short_fma(self):
        results = self.client.query_terms('FMA_9611')
        self.assertEqual(sorted(results), [
            'http://purl.org/obo/owlapi/fma#FMA_24474',
            'http://purl.org/obo/owlapi/fma#FMA_24475',
            'http://purl.org/obo/owlapi/fma#FMA_9611',
        ])


@unittest.skipUnless(virtuoso_test_available(),
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
            'http://namespaces.physiomeproject.org/go.owl',
            'http://namespaces.physiomeproject.org/fma.owl',
        ))

    def test_list_all_terms(self):
        results = self.client.get_terms('plasma membrane')
        self.assertEqual(len(results), 230)

    def test_list_all_terms_quoted(self):
        # the double-quote should be escaped and not cause error.
        results = self.client.get_terms('plasma membrane"')
        self.assertEqual(len(results), 0)

    def test_list_go_only(self):
        results = self.client.get_terms('plasma membrane', graph_urls=(
            'http://namespaces.physiomeproject.org/go.owl',
        ))
        self.assertEqual(len(results), 109)

    def test_get_term_label(self):
        result = self.client.get_url_label(
            'http://purl.org/obo/owlapi/gene_ontology#GO_0005886')
        self.assertEqual(result, 'plasma membrane')

    def test_get_term_label_none(self):
        result = self.client.get_url_label(
            'http://purl.org/obo/owlapi/gene_ontology#GO_5886')
        self.assertIsNone(result)
