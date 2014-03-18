import zope.component
import zope.interface
import zope.schema
import z3c.form
import z3c.form.field
from zope.browserpage.viewpagetemplatefile import ViewPageTemplateFile

from Acquisition import Implicit
from Products.CMFCore.utils import getToolByName

from pmr2.z3cform import form
from pmr2.z3cform import page

from pmr2.app.settings.interfaces import IPMR2GlobalSettings
from pmr2.virtuoso.interfaces import IEngine

from pmr2.ricordo.converter import purlobo_to_identifiers
from pmr2.ricordo.converter import identifiers_to_purlobo
from pmr2.ricordo.engine import Search


class IQueryForm(zope.interface.Interface):

    query = zope.schema.TextLine(
        title=u'Query String',
        description=u'Manchester query to ask the knowledgebase.',
        required=True,
    )


class RootView(Implicit, page.SimplePage):

    template = ViewPageTemplateFile('query_listing.pt')

    def publishTraverse(self, request, name):
        # inject layer.
        zope.interfaces.alsoProvides(request, IJSLayer)
        request['disable_border'] = True
        # return self which is implicit to allow rendering.
        return self


class QueryForm(form.PostForm):

    fields = z3c.form.field.Fields(IQueryForm)
    template = ViewPageTemplateFile('query_form.pt')
    ignoreContext = True

    results = None

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
        self.portal_url = getToolByName(self.context, 'portal_url'
            ).getPortalObject().absolute_url()
        self.portal_catalog = getToolByName(self.context, 'portal_catalog')

        self.search = Search(
            owlkb_rdfstore_uri_map=purlobo_to_identifiers,
            rdfstore_owlkb_uri_map=identifiers_to_purlobo,
            sparql_endpoint=settings.sparql_endpoint,
        )
        self._results = self.search.query(data['query'])

    def resolve_obj(self, graph_iri):
        brain = self.portal_catalog(path=graph_iri.replace(
            self.graph_prefix, '', 1))
        if brain:
            return brain[0]
        return {}

    def results(self):
        self.others = []
        for url, items in self._results:
            label = self.search.get_owl_url_label(url)
            if label:
                # convert graph value into instance-local type.
                items = (
                    {
                        'source': i['g']['value'].replace(
                            self.graph_prefix, self.portal_url, 1),
                        'value': i['r']['value'],
                        'obj': self.resolve_obj(i['g']['value']),
                    }
                    for i in items if i['g']['value'].startswith(
                        self.graph_prefix)
                )
                yield {
                    'label': label,
                    'label_src': url,
                    'items': items,
                }
            else:
                self.others.append((url, items))
