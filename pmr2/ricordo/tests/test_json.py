import unittest
import json

import zope.component

from Products.PloneTestCase import ptc

try:
    from pmr2.ricordo.browser import collection
    from pmr2.json.tests import base
    _test_json = True
except ImportError:
    _test_json = False


@unittest.skipUnless(_test_json, 'pmr2.json is unavailable')
class RicordoJsonTestCase(ptc.PloneTestCase):
    """
    Testing functionalities of forms that don't fit well into doctests.
    """

    def afterSetUp(self):
        pass

    def test_base_render(self):
        request = base.TestRequest()
        f = collection.QueryForm(self.portal, request)
        results = json.loads(f())
        self.assertEqual(
            [i['name'] for i in results["collection"]['template']['data']],
            ['json.widgets.simple_query', 'json.widgets.term_id',
                'json.buttons.search'],
        )


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(RicordoJsonTestCase))
    return suite
