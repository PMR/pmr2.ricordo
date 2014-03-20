import json
import logging

from zope.publisher.browser import BrowserPage

from pmr2.z3cform.page import TraversePage
from pmr2.json.mixin import JsonPage
from pmr2.ricordo.client import OwlSparqlClient

logger = logging.getLogger(__name__)


class OwlSparqlPage(TraversePage, JsonPage):

    json_mimetype = 'application/json'

    #client = OwlSparqlClient(graph_urls=(
    #    'http://models.example.com/go.owl',
    #    'http://models.example.com/fma.owl',
    #))

    client = OwlSparqlClient()

    def render(self):
        try:
            results = self.client.get_owl_terms(self.url_subpath)
        except:
            results = []
            logger.exception('failed to get owl terms')
        return json.dumps({'results': results})
