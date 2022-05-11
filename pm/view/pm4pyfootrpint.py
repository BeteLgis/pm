import os

from pm.storage import StoredFile
from pm.view.common import View
from pm.view.record import RecordData


class PM4PyFootrpintData(RecordData):
    def __init__(self, record):
        super().__init__(ViewPM4PyFootprint.ID, record)
        self.ViewPM4PyFootprint = ViewPM4PyFootprint.ID
        self.image = None


class ViewPM4PyFootprint(View):
    ID = 3

    def __init__(self, request, record):
        super().__init__(request, self.ID)
        self._data = PM4PyFootrpintData(record)

    def header(self):
        return {'id': self.ID, 'name': 'PM4Py Footprints', 'tooltip': '.xes, .pnml, .csv',
                'href': self.data.href.copy()}

    def load(self, file: StoredFile):
        self.data.image = os.path.join(self.data.MEDIA, os.path.basename(file.path))
        return self.data
