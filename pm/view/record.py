from pm.view.common import CommonData, Button


class RecordData(CommonData):
    MEDIA = ''

    def __init__(self, view, record):
        super().__init__(view)
        self.href.update(record=record)
        self.record = record
        self.MEDIA = f"/media/files/{record}/"


class ConfData(RecordData):
    MEDIA2 = ''

    def __init__(self, view, record, record2):
        super().__init__(view, record)
        self.href.update(record2=record2)
        self.record2 = record2
        self.MEDIA2 = f"/media/files/{record2}/"


class StepsData(RecordData):
    def __init__(self, view, record, step, clean):
        super().__init__(view, record)
        self.href.update(record=record, step=step, clean=clean)
        self.step = step
        self.clean = Button(True, 'Raw', self.href.copy(clean=False)) if clean else \
            Button(False, 'Clean', self.href.copy(clean=True))
        self.first_step = Button(label='First step')
        self.prev_step = Button(label='Previous step')
        self.next_step = Button(label='Next step')
        self.last_step = Button(label='Last step')
        self.head = None
        self.rows = None
        self.line = None
