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
        obj = self.portal.portal_catalog(portal_type='Document')[0]
        context = QRItem({
            'obj': obj,
            'value': 'some subject',
        })
        request = TestRequest()
        view = DefaultView(context, request)
        result = view()
        self.assertIn('http://nohost/plone/front-page', result)
        self.assertIn('Welcome to Plone', result)
        self.assertEqual(view.href, 'http://nohost/plone/front-page')
