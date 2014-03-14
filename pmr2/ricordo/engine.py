from pmr2.ricordo import client


class Search(object):
    """
    The RICORDO search engine.
    """

    def __init__(self,
            owlkb_endpoint='http://localhost:8080/ricordo-owlkb-ws/service',
            sparql_endpoint='http://localhost:8890/sparql',
            owlkb_graphs=(),
            owlgraph_owlkb_uri_map=None,
            owlkb_rdfstore_uri_map=None,
            rdfstore_owlkb_uri_map=None,
        ):
        """
        Instantiate a search object instance, with the end points as
        specified.

        owlkb_endpoint
            - the end point to the RICORDO OWLKB webservice.
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

        self.owlkb = client.OwlkbClient(owlkb_endpoint)
        self.rdfstore = client.RdfStoreClient(sparql_endpoint)
        self.owls = client.OwlSparqlClient(owlkb_graphs,
            endpoint=sparql_endpoint)

        self.owlgraph_owlkb_uri_map = owlgraph_owlkb_uri_map
        self.owlkb_rdfstore_uri_map = owlkb_rdfstore_uri_map
        self.rdfstore_owlkb_uri_map = rdfstore_owlkb_uri_map

    def query(self, query, method='getResourceForAnnotation'):
        """
        For each ontological term returned by the OWLKB using the query,
        run a search using the defined method in the RDFStore.
        """

        results = []
        if self.owlgraph_owlkb_uri_map:
            subbed_query = self.owlgraph_owlkb_uri_map(query)
            terms = self.owlkb.query_terms(subbed_query)
        else:
            terms = self.owlkb.query_terms(query)

        for term in terms:
            if self.owlkb_rdfstore_uri_map:
                real_terms = self.owlkb_rdfstore_uri_map(term)
            else:
                # 1-tuple of original term
                real_terms = (term,)
            for t in real_terms:
                items = self.rdfstore.search(target=method, data=t)
                if not items:
                    continue
                results.append((t, items))
        return results

    def get_owl_terms(self, keyword, graph_urls=None):
        return self.owls.get_owl_terms(keyword, graph_urls)

    def get_owl_url_label(self, url, graph_urls=None):
        if self.rdfstore_owlkb_uri_map:
            mapped = self.rdfstore_owlkb_uri_map(url)
            if mapped:
                url = mapped[0]

        return self.owls.get_url_label(url, graph_urls)
