import unittest

from pmr2.ricordo.converter import purlobo_to_identifiers
from pmr2.ricordo.engine import Search

from .base import owlkb_test_available
from .base import rdfstore_test_available
from .base import virtuoso_test_available


@unittest.skipUnless(owlkb_test_available()
        and virtuoso_test_available() and rdfstore_test_available(),
        "Virtuso SPARQL endpoint not available.")
class SearchEngineTestCase(unittest.TestCase):
    """
    Search needs all those services to be available.
    """

    level = 10

    def setUp(self):
        self.search = Search(owlkb_rdfstore_uri_map=purlobo_to_identifiers)

    def test_search_query_base(self):
        results = sorted(self.search.query('part_of some GO_0005886'))
        self.assertEqual(len(results), 9)
        go_1518, ids = results[0]
        self.assertEqual(go_1518, 'http://identifiers.org/obo.go/GO:0001518')
        self.assertEqual(len(ids), 9)
