import zope.component
from pmr2.json.collection.mixin import JsonCollectionFormMixin

from pmr2.ricordo.browser import form
from pmr2.ricordo.browser.ctitem import QRItem


def item_to_link(request, item):
    # Move this to pmr2.virtuoso helper methods?
    item = QRItem(item)
    view = zope.component.getMultiAdapter((item, request),
        name=item['obj'].portal_type,)
    view.update()

    return {
        'rel': 'bookmark',
        'href': view.href,
        'prompt': view.source,
    }


class QueryForm(JsonCollectionFormMixin, form.QueryForm):

    def update(self):
        super(QueryForm, self).update()
        if self._results:
            self._jc_items = [{
                'href': v['label_src'],
                'data': [
                    {
                        'name': 'label',
                        'value': v['label'],
                    },
                ],
                'links': [item_to_link(self.request, i) for i in v['items']],
            } for v in self.results()]
