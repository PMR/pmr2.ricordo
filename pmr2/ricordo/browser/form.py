import zope.component
import zope.interface
import zope.schema
import z3c.form
import z3c.form.field
from z3c.form.interfaces import ISubForm
from z3c.form.browser.checkbox import CheckBoxFieldWidget

from Acquisition import Implicit
from Products.CMFCore.utils import getToolByName

from pmr2.z3cform import form
from pmr2.z3cform import page

from pmr2.app.settings.interfaces import IPMR2GlobalSettings
from pmr2.virtuoso.interfaces import IEngine

from pmr2.ricordo.interfaces import IRicordoConfig
from pmr2.ricordo.converter import purlobo_to_identifiers
from pmr2.ricordo.converter import purlobo_to_owlkb
from pmr2.ricordo.converter import identifiers_to_purlobo
from pmr2.ricordo.engine import Search

from pmr2.ricordo.browser.templates import ViewPageTemplateFile
from pmr2.ricordo.browser.ctitem import QRItem


class IQueryForm(zope.interface.Interface):

    simple_query = zope.schema.TextLine(
        title=u'Ontology term to query',
        description=u'Start by typing the ontology term you wish to find, '
            'then select the desired term out of the possible terms to query '
            'with in the list presented by the drop down.',
        required=True,
    )

    term_id = zope.schema.TextLine(
        title=u'Term ID',
        description=u'',
        required=False,  # hidden
    )

    #ontologies = zope.schema.List(
    #    title=u'Ontologies',
    #    description=u'Choose the ontologies to be used',
    #    required=False,
    #    value_type=zope.schema.Choice(vocabulary='pmr2.ricordo.ontologies'),
    #)


class IAdvanceQueryForm(zope.interface.Interface):

    query = zope.schema.TextLine(
        title=u'Query String',
        description=u'Manchester query to ask the knowledgebase.',
        required=True,
    )


class IBaseTermForm(zope.interface.Interface):

    term = zope.schema.TextLine(
        title=u'Term',
        description=u'',
        required=False,
    )

    ontologies = zope.schema.List(
        title=u'Ontologies',
        description=u'Choose the ontologies to be used',
        required=False,
        value_type=zope.schema.Choice(vocabulary='pmr2.ricordo.ontologies'),
    )


class RootView(Implicit, page.SimplePage):

    template = ViewPageTemplateFile('query_listing.pt')

    def publishTraverse(self, request, name):
        # inject layer.
        zope.interfaces.alsoProvides(request, IJSLayer)
        request['disable_border'] = True
        # return self which is implicit to allow rendering.
        return self


class BaseTermForm(form.PostForm):

    fields = z3c.form.field.Fields(IBaseTermForm)
    fields['ontologies'].widgetFactory = CheckBoxFieldWidget
    ignoreContext = True


class QueryForm(form.PostForm):

    fields = z3c.form.field.Fields(IQueryForm)
    template = ViewPageTemplateFile('query_form.pt')
    ignoreContext = True

    _results = ()
    _cleaned_results = []
    searched = False
    raw_result_count = 0

    def update(self):
        super(QueryForm, self).update()

    def updateWidgets(self):
        super(QueryForm, self).updateWidgets()
        self.widgets['simple_query'].size = 64
        self.widgets['term_id'].mode = 'hidden'

    def _update_subform(self):
        # in case where the more "advanced" form is eventually needed
        form = BaseTermForm(self.context, self.request)
        zope.interface.alsoProvides(form, ISubForm)
        self.base_term_form = form

    def get_query_data(self, data):
        """
        Return the thing to be queried from the incoming data specific
        to this form's interface.
        """

        # this falls back to the simple_query if term_id is not
        # populated
        if not data['term_id']:
            return data['simple_query']

        # XXX totally some side effects here
        term_id = data['term_id']
        simple_query = ''
        if term_id:
            term_url = purlobo_to_owlkb(term_id)
            label = None

            if term_url:
                label = self.search.get_owl_url_label(term_url[0])

            if label:
                simple_query = '%s (%s)' % (label, term_id)

        self.widgets['simple_query'].value = simple_query
        return data['term_id']

    @z3c.form.button.buttonAndHandler(u'Search', name='search')
    def handleSearch(self, action):
        """
        Use the engine and search.
        """

        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return

        self.searched = True

        gs = zope.component.getUtility(IPMR2GlobalSettings)
        settings = zope.component.getAdapter(gs, name='pmr2_virtuoso')
        self.graph_prefix = settings.graph_prefix
        portal = getToolByName(self.context, 'portal_url').getPortalObject()
        self.portal_url = portal.absolute_url()
        self.portal_catalog = getToolByName(self.context, 'portal_catalog')

        ricordo_config = zope.component.queryAdapter(portal, IRicordoConfig)
        owl_urls = ricordo_config is not None and ricordo_config.owl_urls or ()

        self.portal_url = getToolByName(self.context, 'portal_url'
            ).getPortalObject().absolute_url()
        self.search = Search(
            owlkb_graphs=owl_urls,
            owlkb_rdfstore_uri_map=purlobo_to_identifiers,
            rdfstore_owlkb_uri_map=identifiers_to_purlobo,
            sparql_endpoint=settings.sparql_endpoint,
        )
        self._results = self.search.query(self.get_query_data(data))

        self.raw_result_count = len(self._results)

    def resolve_obj(self, graph_iri):
        brain = self.portal_catalog(path=graph_iri.replace(
            self.graph_prefix, '', 1))
        if brain:
            return brain[0]
        return {}

    def render_item(self, item):
        item = QRItem(item)
        view = zope.component.getMultiAdapter((item, self.request),
            name=item['obj'].portal_type,)
        return view()

    def results_i(self):
        self.others = []
        for url, items in self._results:
            term = self.search.get_owl_term(url)
            if term:
                # convert graph value into instance-local type.
                label = term['label']
                definition = term['definition']
                items_i = (
                    {
                        'source': i['g']['value'].replace(
                            self.graph_prefix, self.portal_url, 1),
                        'value': i['r']['value'],
                        'obj': self.resolve_obj(i['g']['value']),
                    }
                    for i in items if i['g']['value'].startswith(
                        self.graph_prefix)
                )
                indexed_items_i = [i for i in items_i if i['obj']]

                if indexed_items_i:
                    yield {
                        'label': label,
                        'definition': definition,
                        'label_src': url,
                        'items': indexed_items_i,
                    }

            else:
                self.others.append((url, items))

    def results(self):
        if not self._cleaned_results:
            self._cleaned_results = list(self.results_i())
        return self._cleaned_results


class RicordoConfigEditForm(form.EditForm):

    fields = z3c.form.field.Fields(IRicordoConfig)

    def getContent(self):
        return zope.component.getAdapter(self.context, IRicordoConfig)

