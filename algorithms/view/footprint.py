import json

from algorithms.storage import StoredFile
from algorithms.view.common import View
from algorithms.view.record import StepsData


class FootprintData(StepsData):
    def __init__(self, record, step, clean):
        super().__init__(ViewFootprint.ID, record, step, clean)
        self.ViewFootprint = ViewFootprint.ID


class ViewFootprint(View):
    ID = 1

    def __init__(self, request, record, step, clean):
        super().__init__(request, self.ID)
        self._data = FootprintData(record, step, clean)

    def header(self):
        return {'id': self.ID, 'name': 'Footprints', 'tooltip': '.txt, .xes, .pnml',
                'href': self.data.href.copy()}

    def load(self, file: StoredFile):
        tmp = json.loads(open(file.path, 'r').read())
        steps = tmp['clean_steps'] if self.data.clean.value else tmp['steps']
        stepslen = len(steps)
        if isinstance(steps, list) and stepslen > 0:
            last = stepslen - 1
            if self.data.step >= stepslen or self.data.step < 0:
                self.data.step = last
            self.data.first_step.update(value=0, href=self.data.href.copy(step=0))
            self.data.last_step.update(value=last, href=self.data.href.copy(step=last))
            prev = self.data.step - 1 if self.data.step > 0 else self.data.last_step.value
            self.data.prev_step.update(value=prev, href=self.data.href.copy(step=prev))
            next = self.data.step + 1 if self.data.step < self.data.last_step.value else 0
            self.data.next_step.update(value=next, href=self.data.href.copy(step=next))
            self.__table(steps, tmp['head'])
            self.__line(steps[self.data.step])
        return self.data

    def __table(self, steps, head):
        self.data.head = head
        step = steps[self.data.step]
        matrix = step['matrix']
        rg = range(len(head))
        rows = []
        for i in rg:
            cells = []
            for j in rg:
                cells.append({
                    'val': self._switch(matrix[i][j]),
                    'class': ''
                })
            rows.append({
                'head': head[i],
                'cells': cells
            })

        if self.data.step < self.data.last_step.value:
            rows[step['prev']]['cells'][step['cur']]['class'] = 'table-warning'
            rows[step['cur']]['cells'][step['prev']]['class'] = 'table-warning'
            if self.data.step < self.data.last_step.value - 1:
                next = steps[self.data.step + 1]
                rows[next['prev']]['cells'][next['cur']]['class'] = 'table-danger'
                rows[next['cur']]['cells'][next['prev']]['class'] = 'table-danger'
        self.data.rows = rows

    def __line(self, step):
        if 'line' in step:
            line = []
            for code in step['line']:
                line.append({
                    'val': code,
                    'class': '',
                    'text': ''
                })
            if 'pi' in step:
                line[step['pi']]['class'] = 'table-warning'
            if 'ci' in step:
                line[step['ci']]['class'] = 'table-warning'
            if 'pin' in step:
                line[step['pin']]['text'] = 'text-danger'
            if 'cin' in step:
                line[step['cin']]['text'] = 'text-danger'
            self.data.line = line
