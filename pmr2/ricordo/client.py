import requests
import json


class RicordoClient(object):

    def __init__(self, root,
            host='127.0.0.1',
            port='8080',
            requests_session=None,
        ):

        self.host = host
        self.port = port
        self.root = root

        if requests_session is None:
            requests_session = requests.Session()
            requests_session.headers.update({
                'Accept': 'application/json',
                'Content-type': 'application/json',
            })
        self.requests_session = requests_session

    @property
    def target(self):
        if not hasattr(self, '_target'):
            self._target = 'http://%s:%s/%s' % (
                self.host, self.port, self.root)
        return self._target

    def get(self, endpoint, query):
        target = '%s/%s/%s' % (self.target, endpoint, query)
        return self.requests_session.get(target).json()

    def post(self, endpoint, data):
        target = '%s/%s' % (self.target, endpoint)
        return self.requests_session.post(target, data=json.dumps(data)).json()


class OwlkbClient(RicordoClient):
    """
    Owl knowledgebase client.
    """

    def __init__(self, root='/ricordo-owlkb-ws/service', *a, **kw):
        super(OwlkbClient, self).__init__(root, *a, **kw)

    def query_terms(self, query):
        return self.get(query=query, endpoint='terms')


class RdfStoreClient(RicordoClient):
    """
    RICORDO RDF Store client.
    """

    def __init__(self, root='/ricordo-rdfstore-ws/service', *a, **kw):
        super(RdfStoreClient, self).__init__(root, *a, **kw)

    def search(self, target, data):
        return self.post(endpoint='search/' + target, data=data)

    def getResourceForAnnotation(self, data):
        return self.search(target='getResourceForAnnotation', data=data)

    def getAnnotationOfResource(self, data):
        return self.search(target='getAnnotationOfResource', data=data)
