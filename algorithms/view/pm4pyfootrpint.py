import os

from algorithms.storage import StoredFile
from algorithms.view.common import View
from algorithms.view.record import RecordData


class PM4PyFootrpintData(RecordData):
    def __init__(self, record):
        super().__init__(ViewPM4PyFootprint.ID, record)
        self.ViewPM4PyFootprint = ViewPM4PyFootprint.ID
        self.image = None


class ViewPM4PyFootprint(View):
    ID = 2

    def __init__(self, request, record):
        super().__init__(request, self.ID)
        self._data = PM4PyFootrpintData(record)

    def header(self):
        return {'id': self.ID, 'name': 'PM4Py Footprints', 'tooltip': '.xes, .pnml',
                'href': self.data.href.copy()}

    def load(self, file: StoredFile):
        self.data.image = os.path.join(self.data.MEDIA, os.path.basename(file.path))
        return self.data
