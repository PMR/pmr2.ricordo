import unittest
import json

from Products.PloneTestCase import ptc

from pmr2.ricordo.browser import webservice
from pmr2.testing.base import TestRequest

from .base import virtuoso_test_available


@unittest.skipUnless(virtuoso_test_available(),
        "Virtuso SPARQL endpoint not available.")
class LiveOwlSparqlClientTestCase(ptc.PloneTestCase):
    """
    Test cases that requires Virutoso running with both the FMA and
    GO owl graphs added at the specific designated URLs listed here.

    XXX fix to not use live for the client.
    """

    level = 10

    def setUp(self):
        request = TestRequest()
        self.page = webservice.OwlSparqlPage(self.portal, request)

    def test_query(self):
        self.page.publishTraverse('plasma membrane')
        results = json.loads(self.page())
        self.assertEqual(len(results), 230)
