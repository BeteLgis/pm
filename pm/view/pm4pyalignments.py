import os

from pm.storage import StoredFile
from pm.view.common import View
from pm.view.record import RecordData


class PM4PyAlignmentsData(RecordData):
    def __init__(self, record):
        super().__init__(ViewPM4PyAlignments.ID, record)
        self.ViewPM4PyAlignments = ViewPM4PyAlignments.ID
        self.image = None


class ViewPM4PyAlignments(View):
    ID = 6

    def __init__(self, request, record):
        super().__init__(request, self.ID)
        self._data = PM4PyAlignmentsData(record)

    def header(self):
        return {'id': self.ID, 'name': 'PM4Py Alignments', 'tooltip': '.xes, .pnml, .csv',
                'href': self.data.href.copy()}

    def load(self, file: StoredFile):
        self.data.image = os.path.join(self.data.MEDIA, os.path.basename(file.path))
        return self.data
