# content type specific rendering.

import zope.interface
from zope.publisher.browser import BrowserView

from pmr2.ricordo.interfaces import IQRItem
from pmr2.ricordo.browser.templates import ViewPageTemplateFile


@zope.interface.implementer(IQRItem)
class QRItem(dict):
    """
    Query Result dictionary that has an implementer for ZCA
    """


class QRItemView(BrowserView):

    index = ViewPageTemplateFile('qr_default.pt')

    def update(self):
        pass

    def render(self):
        return self.index()

    def __call__(self):
        self.update()
        return self.render()


class Default(QRItemView):
    """
    Default view
    """


class ExposureFile(QRItemView):
    """
    Handler for an ExposureFile type subject.
    """

    index = ViewPageTemplateFile('qr_exposurefile.pt')

    def update(self):
        # resolve the exposure object
        pass


class Workspace(QRItemView):
    """
    Handler for an Workspace subject.
    """

    index = ViewPageTemplateFile('qr_workspace.pt')

    def update(self):
        pass
