import zope.component
import zope.interface
import zope.schema
import z3c.form
import z3c.form.field
from zope.browserpage.viewpagetemplatefile import ViewPageTemplateFile

from Acquisition import Implicit

from pmr2.z3cform import form
from pmr2.z3cform import page

from pmr2.app.settings.interfaces import IPMR2GlobalSettings
from pmr2.virtuoso.interfaces import IEngine

from pmr2.ricordo.converter import purlobo_to_identifiers
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

        search = Search(
            owlkb_rdfstore_uri_map=purlobo_to_identifiers,
            sparql_endpoint=settings.sparql_endpoint,
        )
        self.results = search.query(data['query'])


