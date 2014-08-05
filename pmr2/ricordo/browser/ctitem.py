# content type specific rendering.

from urlparse import urlparse
from urlparse import urljoin

from zope.component import queryAdapter
from zope.component.hooks import getSite
import zope.interface
from zope.publisher.browser import BrowserView

from Products.CMFCore.utils import getToolByName

from pmr2.app.workspace.interfaces import IStorage

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


class DefaultView(QRItemView):
    """
    Default view
    """


class ExposureFileView(QRItemView):
    """
    Handler for an ExposureFile type subject.
    """

    index = ViewPageTemplateFile('qr_exposurefile.pt')

    def update(self):
        # resolve the exposure object
        obj = self.context.get('obj')
        if not obj:
            return
        # XXX validate the parsed path is local
        parsed = urlparse(self.context['value'])
        catalog = getToolByName(getSite(), 'portal_catalog')
        target = urljoin(obj.getPath(), parsed.path)
        results = catalog(path=target)
        self.subject = None
        if results:
            # if this is missing then this isn't an exposure file, then
            # the template will not render.
            self.subject = results[0]


class WorkspaceView(QRItemView):
    """
    Handler for an Workspace subject.
    """

    index = ViewPageTemplateFile('qr_workspace.pt')

    def update(self):
        obj = self.context.get('obj')
        if not obj:
            return
        # resolve the full path
        workspace = obj.getObject()
        storage = queryAdapter(workspace, IStorage)
        if not storage:
            # XXX handle all these missing things?
            return
        self.fileurl = '%s/@@file/%s/%s' % (
            obj.getPath(), storage.rev, self.context['value'])
