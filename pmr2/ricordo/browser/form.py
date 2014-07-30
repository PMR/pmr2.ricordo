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
from pmr2.ricordo.converter import identifiers_to_purlobo
from pmr2.ricordo.engine import Search

from .templates import ViewPageTemplateFile


class IQueryForm(zope.interface.Interface):

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

    _qr_templates = {
        'ExposureFile': ViewPageTemplateFile('qr_exposurefile.pt'),
        'Workspace': ViewPageTemplateFile('qr_workspace.pt'),
    }

    _qr_default = ViewPageTemplateFile('qr_default.pt')

    _results = ()

    def update(self):
        super(QueryForm, self).update()
        form = BaseTermForm(self.context, self.request)
        zope.interface.alsoProvides(form, ISubForm)
        self.base_term_form = form

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

        self.portal_url = getToolByName(self.context, 'portal_url'
            ).getPortalObject().absolute_url()
        self.search = Search(
            owlkb_graphs=owl_urls,
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

    def render_item(self, item):
        template = self._qr_templates.get(item['obj'].portal_type,
            self._qr_default)
        return template(self, item=item)

    def results(self):
        self.others = []
        for url, items in self._results:
            label = self.search.get_owl_url_label(url)
            if label:
                # convert graph value into instance-local type.
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
                indexed_items_i = (i for i in items_i if i['obj'])

                # TODO figure out how to get the "true" object to be
                # linked, i.e. exposure items should contain
                # for exposures
                # - full description of the object.
                # - link to the *actual* object of the statement
                # - backlink to the source (the metadata file)
                # for workspace
                # - ?  as is is fine?
                yield {
                    'label': label,
                    'label_src': url,
                    'items': indexed_items_i,
                }
            else:
                self.others.append((url, items))


class RicordoConfigEditForm(form.EditForm):

    fields = z3c.form.field.Fields(IRicordoConfig)

    def getContent(self):
        return zope.component.getAdapter(self.context, IRicordoConfig)

