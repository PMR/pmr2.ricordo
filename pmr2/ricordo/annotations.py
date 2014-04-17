import zope.interface
import zope.component
from zope.schema import fieldproperty
from zope.annotation.interfaces import IAttributeAnnotatable
from zope.annotation import factory
from zope.container.contained import Contained
from persistent import Persistent

from pmr2.ricordo.interfaces import IRicordoConfig


@zope.component.adapter(IAttributeAnnotatable)
@zope.interface.implementer(IRicordoConfig)
class RicordoConfig(Persistent, Contained):

    owl_urls = fieldproperty.FieldProperty(IRicordoConfig['owl_urls'])
    owl_labels = fieldproperty.FieldProperty(IRicordoConfig['owl_labels'])

    def get_graphs(self):
        return zip(self.owl_urls or [], self.owl_labels or [])


RicordoConfigFactory = factory(RicordoConfig)
