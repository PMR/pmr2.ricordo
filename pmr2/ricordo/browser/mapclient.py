import zope.component
import zope.interface
import zope.schema
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm

import z3c.form
import z3c.form.field
from z3c.form.interfaces import ISubForm
from z3c.form.browser.checkbox import CheckBoxFieldWidget
from zope.browserpage.viewpagetemplatefile import ViewPageTemplateFile

from Acquisition import Implicit
from Products.CMFCore.utils import getToolByName

from pmr2.z3cform import form
from pmr2.z3cform import page

from pmr2.app.settings.interfaces import IPMR2GlobalSettings
from pmr2.virtuoso.interfaces import IEngine
from pmr2.virtuoso.client import SparqlClient
from pmr2.virtuoso.sparql import quote_iri

from pmr2.ricordo.interfaces import IRicordoConfig
from pmr2.ricordo.converter import purlobo_to_identifiers
from pmr2.ricordo.converter import identifiers_to_purlobo
from pmr2.ricordo.engine import Search

from .form import BaseTermForm


def autowildcard(tokens, fmtstr, **kw):
    try:
        result = fmtstr.format(**kw)
    except KeyError as e:
        token = kw[e[0]] = '?' + e[0]
        tokens.append(token)
        result = autowildcard(tokens, fmtstr, **kw)
    return result


class MAPClientSearch(Search):
    """
    MAPClient specific extensions
    """

    # TODO roll the improved dynamic query construction back into the
    # parent class when things have stablized.

    _root_query = "SELECT ?g {tokens} WHERE {{ GRAPH ?g {{ {queries} }} }}"

    _query_templates = {
        "workflow_predicate":
            "{token} <http://physiomeproject.org/workflow/1.0/rdf-schema#"
                 "{workflow_predicate}> {ontological_term} .",
        "workflow_object":
            "{token} <http://www.w3.org/2000/01/rdf-schema#subClassOf> "
                 "<http://physiomeproject.org/workflow/1.0/rdf-schema#"
                 "{workflow_object}> .",
    }

    def build_query(self, **kw):
        # XXX dict comprehension not 2.6 compat
        # escape all value strings.
        kwords = {k: quote_iri(v) for k, v in kw.items() if v}
        queries = []
        tokens = []
        for k, v in sorted(self._query_templates.items()):
            if kwords.get(k) is None:
                continue
            token = '?' + k
            tokens.append(token)
            q = autowildcard(tokens, v, **kwords)
            queries.append(q)
        if not tokens:
            return None
        return self._root_query.format(
            tokens=' '.join(tokens), queries='\n'.join(queries))

    def search(self, **kw):
        ontological_term = kw.pop('ontological_term')
        if not ontological_term:
            # simple case.
            q = self.build_query(**kw)
            # "pretend" this is the case...
            return [(
                '(All Terms)',
                self.owls.query(q).get('results', {}).get('bindings'),
            )]

        # expand ontological term into all relevant things.

        results = []
        for term in self._generate_terms(ontological_term):
            kw['ontological_term'] = '<%s>' % quote_iri(term)
            q = self.build_query(**kw)
            results.append((
                term, 
                self.owls.query(q).get('results', {}).get('bindings'),
            ))

        return results


class IQueryForm(zope.interface.Interface):

    workflow_object = zope.schema.Choice(
        title=u'Find...',
        description=u'The type of MAP Client object to find',
        vocabulary=SimpleVocabulary.fromItems([
            ('Workflow Project', 'workflowproject'),
            ('Workflow Step', 'workflowstep'),
        ]),
        required=False,
    )

    workflow_predicate = zope.schema.Choice(
        title=u'Relationship',
        description=u'The type of relationship of a workflow for...',
        vocabulary=SimpleVocabulary.fromItems([
            ('Workflow for', 'workflowfor'),
            ('Workflow makes use of', 'workflowmakesuseof'),
        ]),
        required=False,
    )

    ontological_term = zope.schema.TextLine(
        title=u'Ontological term',
        description=u'The ontological term for the workflow relationship.',
        required=False,
    )


class QueryForm(form.PostForm):

    fields = z3c.form.field.Fields(IQueryForm)
    ignoreContext = True
    template = ViewPageTemplateFile('map_query_form.pt')

    _results = ()

    def update(self):
        super(QueryForm, self).update()
        self.request['disable_border'] = 1

    # XXX Much is copied from form.py.  Create a common class/module
    # when the time is right.

    @z3c.form.button.buttonAndHandler(u'Search', name='search')
    def handleSearch(self, action):
        """
        Use the engine and search.
        """

        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return

        gs = zope.component.getUtility(IPMR2GlobalSettings)
        settings = zope.component.getAdapter(gs, name='pmr2_virtuoso')
        self.graph_prefix = settings.graph_prefix

        portal = getToolByName(self.context, 'portal_url').getPortalObject()
        self.portal_url = portal.absolute_url()
        self.portal_catalog = getToolByName(self.context, 'portal_catalog')

        ricordo_config = zope.component.queryAdapter(portal, IRicordoConfig)
        owl_urls = ricordo_config is not None and ricordo_config.owl_urls or ()

        self.engine = MAPClientSearch(
            owlkb_graphs=owl_urls,
            owlkb_rdfstore_uri_map=purlobo_to_identifiers,
            rdfstore_owlkb_uri_map=identifiers_to_purlobo,
            sparql_endpoint=settings.sparql_endpoint,
        )

        self._results = self.engine.search(**data)

    def resolve_obj(self, graph_iri):
        brain = self.portal_catalog(path=graph_iri.replace(
            self.graph_prefix, '', 1))
        if brain:
            return brain[0]
        return {}

    def _process_items(self, items):
        for i in items:
            if not i['g']['value'].startswith(self.graph_prefix):
                continue

            obj = self.resolve_obj(i['g']['value'])
            d = {k: v['value'] for k, v in i.items() if not k == 'g'}
            d.update({
                'source': obj.getURL(),
                'obj': obj,
            })
            yield d

    def results(self):
        for term_url, items in self._results:
            #url = item[
            label = self.engine.get_owl_url_label(term_url)
            if not label:
                # assume the term url is actually text.
                label, term_url = term_url, ''

            yield {
                'label': label,
                'label_src': term_url,
                'items': self._process_items(items),
            }
