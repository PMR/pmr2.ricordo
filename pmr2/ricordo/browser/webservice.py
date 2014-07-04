import json
import logging

import zope.component
from zope.publisher.browser import BrowserPage
from Products.CMFCore.utils import getToolByName

from pmr2.z3cform.page import TraversePage
from pmr2.json.mixin import JsonPage
from pmr2.ricordo.client import OwlSparqlClient
from pmr2.ricordo.converter import purlobo_to_identifiers
from pmr2.ricordo.interfaces import IRicordoConfig

logger = logging.getLogger(__name__)


class OwlSparqlPage(TraversePage, JsonPage):

    json_mimetype = 'application/json'

    #client = OwlSparqlClient(graph_urls=(
    #    'http://models.example.com/go.owl',
    #    'http://models.example.com/fma.owl',
    #))

    def update(self):
        limit = None
        if len(self.traverse_subpath) > 1:
            # assume the final element is number of desired elements.
            try:
                limit = int(self.traverse_subpath[-1])
                # got the element, pop that off.
                self.traverse_subpath.pop()
            except ValueError:
                pass

        portal = getToolByName(self.context, 'portal_url').getPortalObject()
        ricordo_config = zope.component.queryAdapter(portal, IRicordoConfig)
        owl_urls = ricordo_config is not None and ricordo_config.owl_urls or ()
        try:
            client = OwlSparqlClient(graph_urls=owl_urls)
            results = client.get_owl_terms(self.url_subpath, limit=limit)
        except:
            results = []
            logger.exception('failed to get owl terms')
        self.results = results

    def render(self):
        return json.dumps({'results': self.results})


class MiriamOwlSparqlPage(OwlSparqlPage):

    def purlobo_to_identifiers(self, url):
        results = purlobo_to_identifiers(url)
        if results:
            return results[0]
        return None

    def render(self):
        # Format the results to include MIRIAM identifiers.org URLs and
        # generate dictionaries as output.

        return json.dumps({'results': [
            {
                'name': name,
                'owlapi_url': url,
                'identifiers_org_uri': self.purlobo_to_identifiers(url),
            }
            for name, url in self.results
        ]})
