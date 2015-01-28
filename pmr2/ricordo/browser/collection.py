import zope.component
from pmr2.json.collection.mixin import JsonCollectionFormMixin

from pmr2.ricordo.browser import form
from pmr2.ricordo.browser.ctitem import QRItem


class QueryForm(JsonCollectionFormMixin, form.QueryForm):

    def _item_to_link(self, item):
        item = QRItem(item)
        view = zope.component.getMultiAdapter((item, self.request),
            name=item['obj'].portal_type,)
        view.update()

        return {
            'rel': 'bookmark',
            'href': view.href,
            'prompt': view.source,
        }

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
                'links': [self._item_to_link(i) for i in v['items']],
            } for v in self.results()]
