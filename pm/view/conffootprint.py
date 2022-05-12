import json

import numpy as np

from pm.storage import StoredFile
from pm.view.common import View
from pm.view.record import ConfData


class ConfFootprintData(ConfData):
    def __init__(self, record, record2):
        super().__init__(ViewConfFootprint.ID, record, record2)
        self.ViewConfFootprint = ViewConfFootprint.ID
        self.head = None
        self.rows = None
        self.head2 = None
        self.rows2 = None
        self.match = None
        self.total = None
        self.conf = None


class ViewConfFootprint(View):
    ID = 5

    def __init__(self, request, record, record2):
        super().__init__(request, self.ID)
        self._data = ConfFootprintData(record, record2)

    def header(self):
        return {'id': self.ID, 'name': 'Conformance Footprints', 'tooltip': '.txt, .xes, .pnml, .csv',
                'href': self.data.href.copy()}

    def load(self, file: StoredFile, file2: StoredFile):
        tmp = json.loads(open(file.path, 'r').read())
        tmp2 = json.loads(open(file2.path, 'r').read())
        steps = tmp['steps']
        steps2 = tmp2['steps']
        stepslen = len(steps)
        steps2len = len(steps2)
        if isinstance(steps, list) and stepslen > 0\
                and isinstance(steps2, list) and steps2len > 0:
            head = tmp['head']
            head2 = tmp2['head']
            headlen = len(head)
            head2len = len(head2)
            step = steps[stepslen - 1]
            step2 = steps2[steps2len - 1]
            matrix = np.matrix(step['matrix'])
            matrix2 = np.matrix(step2['matrix'])
            if head2len < headlen:
                matrix2 = np.pad(matrix2, (0, headlen - head2len), mode='constant', constant_values=(-2))
            elif headlen < head2len:
                matrix = np.pad(matrix, (0, head2len - headlen), mode='constant', constant_values=(-2))
            diff = matrix == matrix2
            self.data.head = head
            self.data.rows = self.__table(step['matrix'], head, diff)
            self.data.head2 = head2
            self.data.rows2 = self.__table(step2['matrix'], head2, diff)
            self.data.total = diff.size
            self.data.match = self.data.total - diff.sum()
            self.data.conf = 1 - self.data.match/self.data.total
            if self.data.conf.is_integer():
                self.data.conf = int(self.data.conf)
        return self.data

    def __table(self, matrix, head, diff):
        rg = range(len(head))
        rows = []
        for i in rg:
            cells = []
            for j in rg:
                cells.append({
                    'val': self._switch(matrix[i][j]),
                    'class': '' if diff[i, j] else 'table-danger'
                })
            rows.append({
                'head': head[i],
                'cells': cells
            })
        return rows
