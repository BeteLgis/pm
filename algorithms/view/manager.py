import json
import os
import shutil

from django.http import FileResponse
from django.shortcuts import redirect

from algorithms.algorithms.manager import process_upload
from algorithms.storage import StoredFiles
from algorithms.view.common import *
from algorithms.view.conffootprint import ViewConfFootprint
from algorithms.view.footprint import FootprintData
from algorithms.view.footprint import ViewFootprint
from algorithms.view.history import HistoryData
from algorithms.view.history import ViewHistory
from algorithms.view.pm4pyfootrpint import ViewPM4PyFootprint, PM4PyFootrpintData
from algorithms.view.record import StepsData, RecordData


class AllData(FootprintData, HistoryData):
    def __init__(self):
        super(Data, self).__init__()
        for _class in [HistoryData(None, None),
                       FootprintData(None, None, None), PM4PyFootrpintData(None),
                       StepsData(None, None, None, None),
                       RecordData(None, None), CommonData(None)]:
            for key, value in getattr(_class, '__dict__').items():
                self.__dict__[key] = value
        self.upload = None


class ViewManager(View):
    VIEWS_ALL = {ViewHistory.ID, ViewFootprint.ID, ViewPM4PyFootprint.ID, ViewConfFootprint.ID}
    RAISE = False
    DEFAULT_VIEW = ViewHistory.ID

    def __init__(self, request):
        super().__init__(request, self.DEFAULT_VIEW)
        self._data = AllData()

    def load(self, *_args):
        history = ViewHistory(self._request, None, None)
        self.data.view = self.DEFAULT_VIEW
        self.data.header = history.header()

        try:
            if self.__download_file():
                if self.__delete_record():
                    if self.__update_record():
                        if self.__create_record():
                            self.__read_record()
        except Exception as ex:
            if self.RAISE:
                raise ex
            else:
                self.data.error = ex
        
        self.data.header[self.data.view]['selected'] = 'active'
        self.data._header = {k: self.data.header[k] for k in sorted(self.data.header)}.values()

        return self.data.to_dict()

    def __create_record(self):
        if self._request.method == 'POST':
            if 'upload' in self._request.POST:
                if len(self._request.FILES) != 0:
                    process_upload(self._request_post('name', str, ''), self._request.user, self._request.FILES.get('file'))
                    self.data.redirect = redirect('/')
                    return False
        return True

    def __read_record(self):
        view = self._request_get('view', int, self.DEFAULT_VIEW, self.INDICT, self.VIEWS_ALL)
        record = self._request_get('record', int, None, self.RECORD_LOADED)
        record2 = self._request_get('record2', int, None, self.RECORD_LOADED)

        history = ViewHistory(self._request, record, record2)
        self.data.header = history.header()

        cond = record is not None
        cond2 = record2 is not None
        if cond:
            if cond2:
                self.__load_records(view, record, record2)
            else:
                self.__load_record(view, record)
        elif cond2:
            self.__load_record(view, record2)

        if self.data.view == ViewHistory.ID:
            self.data = history.load(self.data.view)

    def __load_record(self, view, record):
        step = self._request_get('step', int, 0)
        clean = self._request_get('clean', bool, False)
        files = StoredFiles.from_dict(json.loads(Record.objects.get(id=record).json))

        if files.footprint is not None:
            footprint = ViewFootprint(self._request, record, step, clean)
            self.data.header = footprint.header()
            if view == ViewFootprint.ID:
                self.data = footprint.load(files.footprint)

        if files.pm4py_footprint is not None:
            pm4pyfootprint = ViewPM4PyFootprint(self._request, record)
            self.data.header = pm4pyfootprint.header()
            if view == ViewPM4PyFootprint.ID:
                self.data = pm4pyfootprint.load(files.pm4py_footprint)

    def __load_records(self, view, record, record2):
        files = StoredFiles.from_dict(json.loads(Record.objects.get(id=record).json))
        files2 = StoredFiles.from_dict(json.loads(Record.objects.get(id=record2).json))

        if files.footprint is not None and files2.footprint is not None:
            conffootprint = ViewConfFootprint(self._request, record, record2)
            self.data.header = conffootprint.header()
            if view == ViewConfFootprint.ID:
                self.data = conffootprint.load(files.footprint, files2.footprint)

    def __update_record(self):
        if 'save' in self._request.POST:
            record = self._request_post('record', int, None, self.RECORD)
            name = self._request_post('name', str, '')
            if record is not None:
                rec = Record.objects.get(id=record)
                rec.name = name
                rec.save()
                self.data.redirect = redirect('/')
                return False
        return True

    def __delete_record(self):
        record = self._request_get('delete', int, None)
        if record == -1:
            recs = Record.objects.filter(user=self._request.user, error__isnull=False)
            for rec in recs:
                shutil.rmtree(os.path.join(StoredFiles.FILES, str(rec.id)), ignore_errors=True)
                rec.delete()
            self.data.redirect = redirect('/')
            return False

        record = self._request_get('delete', int, None, self.RECORD)
        if record is not None:
            rec = Record.objects.get(id=record)
            shutil.rmtree(os.path.join(StoredFiles.FILES, str(rec.id)), ignore_errors=True)
            rec.delete()
            self.data.redirect = redirect('/')
            return False

        if 'deleteAll' in self._request.POST:
            Record.objects.filter(user=self._request.user).delete()
            shutil.rmtree(StoredFiles.FILES, ignore_errors=True)
            os.makedirs(StoredFiles.FILES)
            shutil.rmtree(StoredFiles.TEMP, ignore_errors=True)
            os.makedirs(StoredFiles.TEMP)
            self.data.redirect = redirect('/')
            return False
        return True

    def __download_file(self):
        record = self._request_get('download', int, None, self.RECORD)
        if record is not None:
            files = StoredFiles.from_dict(json.loads(Record.objects.get(id=record).json))
            self.data.redirect = FileResponse(open(files.src.path, 'rb'), as_attachment=True)
            return False
        return True
