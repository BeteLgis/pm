import json

from pm.storage import StoredFile
from pm.view.common import View
from pm.view.record import RecordData


class LogData(RecordData):
    def __init__(self, record):
        super().__init__(ViewLog.ID, record)
        self.ViewLog = ViewLog.ID
        self.log = None


class ViewLog(View):
    ID = 2

    def __init__(self, request, record):
        super().__init__(request, self.ID)
        self._data = LogData(record)

    def header(self):
        return {'id': self.ID, 'name': 'Log', 'tooltip': '.xes, .pnml, .csv',
                'href': self.data.href.copy()}

    def load(self, file: StoredFile):
        self.data.log = json.loads(open(file.path, 'r').read())
        return self.data
