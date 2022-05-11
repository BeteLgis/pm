import os

from pm.storage import StoredFile
from pm.view.common import View
from pm.view.record import RecordData


class PetriData(RecordData):
    def __init__(self, record):
        super().__init__(ViewPetri.ID, record)
        self.ViewPetri = ViewPetri.ID
        self.image = None


class ViewPetri(View):
    ID = 1

    def __init__(self, request, record):
        super().__init__(request, self.ID)
        self._data = PetriData(record)

    def header(self):
        return {'id': self.ID, 'name': 'Petri Net', 'tooltip': '.xes, .pnml, .csv',
                'href': self.data.href.copy()}

    def load(self, file: StoredFile):
        self.data.image = os.path.join(self.data.MEDIA, os.path.basename(file.path))
        return self.data
