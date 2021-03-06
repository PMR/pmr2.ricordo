import unittest
import json

from Products.PloneTestCase import ptc

from pmr2.ricordo.browser import webservice
from pmr2.testing.base import TestRequest

from .base import virtuoso_test_available


@unittest.skipUnless(virtuoso_test_available(),
        "Virtuso SPARQL endpoint not available.")
class LiveOwlSparqlClientTestCase(ptc.FunctionalTestCase):
    """
    Test cases that requires Virutoso running with both the FMA and
    GO owl graphs added at the specific designated URLs listed here.

    XXX fix to not use live for the client.
    """

    level = 10

    def afterSetUp(self):
        request = TestRequest()
        self.page = webservice.OwlSparqlPage(self.portal, request)

    def test_query(self):
        self.page.publishTraverse(self.page.request, 'plasma membrane')
        results = json.loads(self.page())
        self.assertEqual(len(results['results']), 230)

    def test_query_limit(self):
        self.page.publishTraverse(self.page.request, 'plasma membrane')
        self.page.publishTraverse(self.page.request, '10')
        results = json.loads(self.page())
        self.assertEqual(len(results['results']), 10)

    def test_query_final_not_int(self):
        self.page.publishTraverse(self.page.request, 'dorsal')
        self.page.publishTraverse(self.page.request, 'ventral')
        results = json.loads(self.page())
        self.assertEqual(len(results['results']), 30)

    def test_query_multi_slash(self):
        self.page.publishTraverse(self.page.request, 'dorsal')
        self.page.publishTraverse(self.page.request, 'ventral')
        self.page.publishTraverse(self.page.request, '10')
        results = json.loads(self.page())
        self.assertEqual(len(results['results']), 10)
