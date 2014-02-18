import unittest
import requests
import json

from pmr2.ricordo import client


def test_available(text, url):
    try:
        r = requests.get('http://127.0.0.1:8080/ricordo-owlkb-ws/')
        return 'RICORDO-owlkb-webservice' in r.text
    except:
        return False

def owlkb_test_available():
    return test_available('RICORDO-owlkb-webservice',
        'http://127.0.0.1:8080/ricordo-owlkb-ws/')

def rdfstore_test_available():
    return test_available('RICORDO-rdfstore-webservice',
        'http://127.0.0.1:8080/ricordo-rdfstore-ws/')


@unittest.skipUnless(owlkb_test_available(),
        "OWLKB Webservice is not running.")
class LiveOwlClientTestCase(unittest.TestCase):
    """
    Test cases that requires Tomcat running with the RICORDO owlkb
    webservices installed and running with the Gene Ontology (go.owl)
    defined as the actilve knowledgebase.
    """

    def setUp(self):
        self.client = client.OwlkbClient()

    def test_query(self):
        results = self.client.query_terms('GO_0005886')
        self.assertEqual(results['terms']['count'], 3)

    def test_regulates_some_query(self):
        results = self.client.query_terms('regulates some GO_0005978')
        self.assertEqual(results.keys(), ['terms'])


@unittest.skipUnless(rdfstore_test_available(),
        "Ricordo RDFStore endpoint not running.")
class LiveRicordoClientTestCase(unittest.TestCase):
    """
    Test cases that requires Tomcat running with the RICORDO owlkb
    webservices installed and running with the Gene Ontology (go.owl)
    defined as the actilve knowledgebase.
    """

    def setUp(self):
        self.client = client.RdfStoreClient()

    def test_search_getResourceForAnnotation(self):
        results = self.client.getResourceForAnnotation({'query':
            'http://identifiers.org/obo.go/GO:0031594',
        })
        self.assertTrue(results['resources']['count'] > 0)

    def test_search_getAnnotationOfResource(self):
        results = self.client.getAnnotationOfResource({'query':
            'http://www.ebi.ac.uk/ricordo/toolbox/sbmlo#BIOMD0000000002_comp1',
        })
        p, v = results['resources']['resources'][0]['value']
        self.assertEqual(p, 'http://biomodels.net/biology-qualifiers#is')
        self.assertEqual(v, 'http://identifiers.org/obo.go/GO:0031594')
