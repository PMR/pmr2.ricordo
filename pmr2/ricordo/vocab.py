import zope.interface
import zope.component
from zope.schema.interfaces import IVocabulary, IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from Products.CMFCore.utils import getToolByName

from pmr2.ricordo.interfaces import IRicordoConfig


class OntologyGraphVocab(SimpleVocabulary):
    """
    Retrieves the list of ontology graphs configured for RICORDO.
    """

    def __init__(self, context):
        portal = getToolByName(context, 'portal_url').getPortalObject()
        config = zope.component.getAdapter(portal, IRicordoConfig)
        terms = [SimpleTerm(url, url, labels)
            for url, labels in config.get_graphs()]
        super(OntologyGraphVocab, self).__init__(terms)

    def getTerm(self, value):
        try:
            return super(OntologyGraphVocab, self).getTerm(value)
        except LookupError:
            return SimpleTerm(value)

def OntologyGraphVocabFactory(context):
    return OntologyGraphVocab(context)

zope.interface.alsoProvides(OntologyGraphVocabFactory, IVocabularyFactory)
