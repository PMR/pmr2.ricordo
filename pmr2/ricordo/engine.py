from pmr2.ricordo import client


class Search(object):
    """
    The RICORDO search engine.
    """

    def __init__(self,
            sparql_endpoint='http://localhost:8890/sparql',
            owlkb_endpoint=None,
            owlkb_graphs=(),
            owlgraph_owlkb_uri_map=None,
            owlkb_rdfstore_uri_map=None,
            rdfstore_owlkb_uri_map=None,
        ):
        """
        Instantiate a search object instance, with the end points as
        specified.

        owlkb_endpoint
            - the endpoint for the owl reasoning engine.  If specified
              it must point to the endpoint for the RICORDO OWLKB
              webservice.  Defaults to a simpler service that relies on
              the SPQRAL endpoint.
        rdfstore_endpoint
            - the endpoint to the RICORDO RDFStore webservice.
        owl_sparql_endpoint
            - The Virtuoso SPARQL endpoint, for the OWL graphs
        owlkb_graphs
            - a tuple of graph URLS stored in the Virtuoso rdfstore.  If
              not specified it may return all rdfs:labels matching the
              query as a valid item for nonexistent ids in the RICORDO
              OWLKB as specified.  Consult setup and installation
              instructions.
        owlgraph_owlkb_uri_map
            - not really supported yet.
        owlkb_rdfstore_uri_map
        rdfstore_owlkb_uri_map
            - in the case that URL in the ontology not matching what was
              used to annotate the data stored in the RDF graphs, an
              optional converter can be constructed and provided.
            - the inverse will be used for the label lookup.
        """

        if owlkb_endpoint:
            self.owlkb = client.OwlkbClient(owlkb_endpoint)
        else:
            self.owlkb = client.SimpleOwlkbClient(sparql_endpoint)
        self.rdfstore = client.RdfStoreClient(sparql_endpoint)
        self.owls = client.OwlSparqlClient(owlkb_graphs,
            endpoint=sparql_endpoint)

        self.owlgraph_owlkb_uri_map = owlgraph_owlkb_uri_map
        self.owlkb_rdfstore_uri_map = owlkb_rdfstore_uri_map
        self.rdfstore_owlkb_uri_map = rdfstore_owlkb_uri_map

    def _generate_terms(self, query):
        """
        A generator of relevant ontological terms for a given query
        against the stored ontologies (the owl knowledgebase).
        """

        if self.owlgraph_owlkb_uri_map:
            subbed_query = self.owlgraph_owlkb_uri_map(query)
            terms = self.owlkb.query_terms(subbed_query)
        else:
            terms = self.owlkb.query_terms(query)

        generated = set()

        for term in terms:
            # expand the result terms against the defined mappings if
            # available.

            # XXX refactor the following.
            if self.owlkb_rdfstore_uri_map:
                for expanded_term in self.owlkb_rdfstore_uri_map(term):
                    if expanded_term in generated:
                        continue
                    generated.add(expanded_term)
                    yield expanded_term
            else:
                if term in generated:
                    continue
                generated.add(term)
                yield term

    def query(self, query, method='getResourceForAnnotation'):
        """
        For each ontological term returned by the OWLKB using the query,
        run a search using the defined method in the RDFStore.
        """

        results = []

        for t in self._generate_terms(query):
            items = self.rdfstore.search(target=method, data=t)
            if not items:
                continue
            results.append((t, items))

        return results

    def get_owl_terms(self, keyword, graph_urls=None):
        return self.owls.get_owl_terms(keyword, graph_urls)

    def _map_owlkb_url(self, url):
        if self.rdfstore_owlkb_uri_map:
            mapped = self.rdfstore_owlkb_uri_map(url)
            if mapped:
                return mapped[0]
        return url

    def get_owl_url_label(self, url, graph_urls=None):
        url = self._map_owlkb_url(url)
        return self.owls.get_url_label(url, graph_urls)

    def get_owl_term(self, url, graph_urls=None):
        url = self._map_owlkb_url(url)
        return self.owls.get_term(url, graph_urls)
