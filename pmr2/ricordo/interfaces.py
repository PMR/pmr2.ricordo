import zope.interface
import zope.schema


class IRicordoConfig(zope.interface.Interface):
    """
    Interface to the annotation that tracks the paths that are to be
    indexed with the RDF Store.
    """

    owl_urls = zope.schema.List(
        title=u'OWL URLs',
        description=u'A list of valid Graph IRIs in the active Virtuoso '
            'instance that contains OWL related triples that this instance of '
            'PMR cares about.',
        required=False,
        value_type=zope.schema.TextLine(
            title=u'URLs',
        )
    )

    owl_labels = zope.schema.List(
        title=u'OWL Labels',
        description=u'Labels are joined with the URLs.',
        required=False,
        value_type=zope.schema.TextLine(
            title=u'Label',
        ),
    )


class IQRItem(zope.interface.Interface):
    """
    A marker interface for a query result item.
    """
