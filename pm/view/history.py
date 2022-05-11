from pm.models import Record
from pm.view.common import CommonData, View, Button


class HistoryData(CommonData):
    def __init__(self, record, record2):
        super().__init__(ViewHistory.ID)
        self.ViewHistory = ViewHistory.ID
        self.href.update(record=record, record2=record2)
        self.history = None
        self.unload = Button(label='Unload first', href=self.href.copy(record=False))
        self.unload2 = Button(label='Unload second', href=self.href.copy(record2=False))
        self.unloadboth = Button(label='Unload both', href=self.href.copy(record=False, record2=False))


class ViewHistory(View):
    ID = 0

    def __init__(self, request, record, record2):
        super().__init__(request, self.ID)
        self._data = HistoryData(record, record2)

    def header(self):
        return {'id': self.ID, 'name': 'Home',
                'href': self.data.href.copy()}

    def load(self, view):
        self.data.history = self.__get_history()
        return self.data

    def __get_history(self):
        res = {}
        records = Record.objects.filter(user=self._request.user)
        for rec in records:
            res[rec.id] = {'id': rec.id, 'name': rec.name, 'error': rec.error, 'isloaded': rec.isloaded}
        return res
