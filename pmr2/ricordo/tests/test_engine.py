import unittest

from pmr2.ricordo.converter import purlobo_to_identifiers
from pmr2.ricordo.converter import identifiers_to_purlobo
from pmr2.ricordo.engine import Search

from .base import owlkb_test_available
from .base import rdfstore_test_available
from .base import virtuoso_test_available


@unittest.skipUnless(owlkb_test_available() and virtuoso_test_available(),
        "Virtuso SPARQL endpoint not available.")
class SearchEngineWithOwlkbTestCase(unittest.TestCase):
    """
    Search needs all those services to be available.
    """

    level = 20

    def setUp(self):
        # as we are testing the integration with real service, specify
        # that endpoint.
        self.search = Search(
            owlkb_endpoint='http://localhost:8080/ricordo-owlkb-ws/service',
            owlkb_rdfstore_uri_map=purlobo_to_identifiers,
            rdfstore_owlkb_uri_map=identifiers_to_purlobo,
        )

    def test_search_query_base(self):
        results = sorted(self.search.query('part_of some GO_0005886'))
        self.assertEqual(len(results), 9)
        go_1518, ids = results[0]
        self.assertEqual(go_1518, 'http://identifiers.org/obo.go/GO:0001518')
        self.assertEqual(len(ids), 9)


@unittest.skipUnless(virtuoso_test_available(),
        "Virtuso SPARQL endpoint not available.")
class SearchEngineTestCase(unittest.TestCase):
    """
    Search needs all those services to be available.
    """

    level = 10

    def setUp(self):
        self.search = Search(
            owlkb_rdfstore_uri_map=purlobo_to_identifiers,
            rdfstore_owlkb_uri_map=identifiers_to_purlobo,
        )

    def test_search_query_simple(self):
        results = sorted(self.search.query('GO_0005886'))
        self.assertEqual(len(results), 1)
        go_5886, ids = results[0]
        self.assertEqual(go_5886, 'http://identifiers.org/obo.go/GO:0005886')
        self.assertIn(
            'http://www.ebi.ac.uk/ricordo/toolbox/sbmlo#BIOMD0000000101_PM',
            [i['r']['value'] for i in ids]
        )

    def test_get_url_label(self):
        label = self.search.get_owl_url_label(
            'http://identifiers.org/obo.go/GO:0005886')
        self.assertEqual(label, 'plasma membrane')

        label = self.search.get_owl_url_label(
            'http://identifiers.org/go/GO:0005886')
        self.assertEqual(label, 'plasma membrane')
