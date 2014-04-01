import unittest

import zope.component
import zope.interface

from Zope2.App import zcml
from Products.Five import fiveconfigure
from Products.PloneTestCase import PloneTestCase as ptc

from pmr2.ricordo.interfaces import IRicordoConfig
from pmr2.ricordo.browser.form import RicordoConfigEditForm

from pmr2.testing.base import TestRequest
from pmr2.ricordo.tests import base


class RicordoConfigTestCase(ptc.PloneTestCase):
    """
    For the browser side of things.
    """

    def test_ricordo_config_form_render(self):
        context = self.portal
        request = TestRequest()
        form = RicordoConfigEditForm(context, request)
        result = form()
        self.assertIn('OWL URLs', result)

    def test_ricordo_config_form_submit(self):
        context = self.portal

        config = zope.component.getAdapter(context, IRicordoConfig)
        self.assertIsNone(config.owl_urls)

        urls = [
            u'http://example.com/graph1.owl',
            u'http://example.com/graph2.owl',
        ]

        request = TestRequest(form={
            'form.widgets.owl_urls': u'\n'.join(urls),
            'form.buttons.apply': 1,
        })
        form = RicordoConfigEditForm(context, request)
        form.update()

        info = zope.component.getAdapter(context, IRicordoConfig)
        self.assertEqual(config.owl_urls, urls)
