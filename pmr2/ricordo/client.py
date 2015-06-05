from os.path import basename, dirname, join
from glob import glob

import requests
import json

from pmr2.virtuoso.client import SparqlClient
from pmr2.virtuoso.sparql import quote_iri
from pmr2.ricordo.converter import owlkb_to_purlobo


def load_queries(target_dir):
    result = {}
    for fn in glob(join(target_dir, '*.txt')):
        with open(fn) as fd:
            result[basename(fn)[:-4]] = fd.read()
    return result

_base_queries = {}
def _load():
    global _base_queries
    _base_queries = load_queries(join(dirname(__file__),
        'resources', 'rdfstore_query'))

_load()
del _load


class RicordoClient(object):
    """
    Client that access the Ricordo web services (Tomcat version).
    """

    def __init__(self, root_endpoint, requests_session=None):
        self.root_endpoint = root_endpoint

        if requests_session is None:
            requests_session = requests.Session()
            requests_session.headers.update({
                'Accept': 'application/json',
                'Content-type': 'application/json',
            })
        self.requests_session = requests_session

    def get(self, endpoint, query):
        target = '%s/%s/%s' % (self.root_endpoint, endpoint, query)
        return self.requests_session.get(target).json()

    def post(self, endpoint, data):
        target = '%s/%s' % (self.root_endpoint, endpoint)
        return self.requests_session.post(target, data=json.dumps(data)).json()


class OwlkbClient(RicordoClient):
    """
    Owl knowledgebase client.
    """

    def __init__(self,
            root_endpoint='http://localhost:8080/ricordo-owlkb-ws/service',
            *a, **kw):
        super(OwlkbClient, self).__init__(root_endpoint, *a, **kw)

    def query_terms(self, query):
        return [i['id'] for i in self.get(query=query, endpoint='terms').get(
            'terms', {}).get('terms', [])]


class SimpleOwlkbClient(SparqlClient):
    """
    Stripped down client that emulates the owl knowledge for the most
    basic query, i.e. without the manchester style support and the
    deeper more resource intensive description logic reasoning.
    """

    _subclass_query = '''
    SELECT ?s WHERE {
        ?s <http://www.w3.org/2000/01/rdf-schema#subClassOf> %(iri)s .
    }
    '''

    def query_terms(self, query):
        iri = owlkb_to_purlobo(query)
        if iri:
            # should only be one.
            iri = iri[0]
        else:
            # leave as unconverted
            iri = query
        t = self._subclass_query % {'iri': '<%s>' % quote_iri(iri)}
        # include the original term as that's what user wants to query.
        result = [iri]
        result.extend((i['s']['value'] for i in
            self.query(t).get('results', {}).get('bindings')))
        return result


class RdfStoreClient(SparqlClient):
    """
    RICORDO RDF Store client.
    """

    def search(self, target, data):
        t = _base_queries[target] % {'iri': '<%s>' % quote_iri(data)}
        return self.query(t).get('results', {}).get('bindings')

    def getResourceForAnnotation(self, query):
        return self.search('getResourceForAnnotation', query)

    def getAnnotationOfResource(self, query):
        return self.search('getAnnotationOfResource', query)


class OwlSparqlClient(SparqlClient):

    _sparql_query = {
        'term_lookup': """
            select ?s ?o
            %(from_graph_statement)s
            where {
                ?s <http://www.w3.org/2000/01/rdf-schema#label> ?o
                filter regex(?o, "%(keyword)s", "i") .
            } %(limit)s
        """,

        'url_lookup_details': """
            select ?label ?def
            %(from_graph_statement)s
            where {
                <%(iri)s> <http://www.w3.org/2000/01/rdf-schema#label> ?label .
                optional { 
                    <%(iri)s>
                        <http://www.geneontology.org/formats/oboInOwl#def> ?def
                }
            }
        """,

        'url_lookup': """
            select ?o
            %(from_graph_statement)s
            where {
                <%(iri)s> <http://www.w3.org/2000/01/rdf-schema#label> ?o
            }
        """,

    }

    def __init__(self, graph_urls=(), *a, **kw):
        self.graph_urls = graph_urls
        super(OwlSparqlClient, self).__init__(*a, **kw)

    def make_query(self, query_id, graph_urls=None, **kw):
        if graph_urls is None:
            graph_urls = self.graph_urls

        graph_stmt = '\n'.join(['from <%s>' % quote_iri(g) for g in graph_urls])
        kw['from_graph_statement'] = graph_stmt
        return self._sparql_query[query_id] % kw

    def get_terms(self, keyword, limit=None, graph_urls=None):
        """
        Method to provide the labels and the associated identifier for
        the terms within the selected ontologies users will be searching
        their data against.
        """

        limit = limit and ('limit %d' % limit) or ''
        results = self.query(self.make_query('term_lookup', graph_urls,
            keyword=keyword.replace('"', '\\"'),
            limit=limit,
        ))
        return sorted([(i['o']['value'], i['s']['value'])
            for i in results['results']['bindings']])

    def get_url_label(self, url, graph_urls=None):
        """
        Get the rdfs:label associated with the provided url.
        """

        results = self.query(self.make_query('url_lookup', graph_urls,
            iri=quote_iri(url)))['results']['bindings']
        return (results and results[0]['o']['value'] or None)

    def get_term(self, url, graph_urls=None):
        """
        Returns the details of one OWL term by URL.
        """

        results = self.query(self.make_query('url_lookup_details', graph_urls,
            iri=quote_iri(url)))['results']['bindings']
        return (results and {
                'label': results[0]['label']['value'],
                'definition': results[0].get('def', {}).get('value'),
            } or {})
