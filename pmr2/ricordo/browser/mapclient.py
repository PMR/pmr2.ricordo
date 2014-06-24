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

from pmr2.ricordo.interfaces import IRicordoConfig
from pmr2.ricordo.converter import purlobo_to_identifiers
from pmr2.ricordo.converter import identifiers_to_purlobo
from pmr2.ricordo.engine import Search

from .form import BaseTermForm


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

    ontological_term  = zope.schema.TextLine(
        title=u'Ontological term',
        description=u'The ontological object for the relationship',
        required=False,
    )


class QueryForm(form.PostForm):

    fields = z3c.form.field.Fields(IQueryForm)
    ignoreContext = True

    results = ()

    def update(self):
        super(QueryForm, self).update()
        self.request['disable_border'] = 1

    @z3c.form.button.buttonAndHandler(u'Search', name='search')
    def handleSearch(self, action):
        """
        Use the engine and search.
        """

        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return

        self.results = []
