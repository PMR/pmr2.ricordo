import unittest

import zope.component
import zope.interface

from Zope2.App import zcml
from Products.Five import fiveconfigure
from Products.PloneTestCase import PloneTestCase as ptc

from pmr2.ricordo.interfaces import IRicordoConfig

from pmr2.testing.base import TestRequest
from pmr2.ricordo.tests import base
from pmr2.ricordo.browser.ctitem import QRItem
from pmr2.ricordo.browser.ctitem import DefaultView


class CTItemTestCase(ptc.PloneTestCase):
    """
    For the browser side of things.
    """

    def test_base_render(self):
        # simulate a real one
        context = QRItem({
            'obj': {
                'getURL': 'http://nohost/plone/dummy',
                'Title': 'Dummy Object',
            },
            'value': 'some subject',
        })
        request = TestRequest()
        result = DefaultView(context, request)()
        self.assertIn('http://nohost/plone/dummy', result)
        self.assertIn('Dummy Object', result)
