import json
import os
import shutil
from zipfile import ZipFile

from django.http import FileResponse
from django.shortcuts import redirect

from pm.algorithms.manager import AlgorithmsManager
from pm.storage import StoredFiles
from pm.view.common import *
from pm.view.conffootprint import ConfFootprintData, ViewConfFootprint
from pm.view.footprint import FootprintData, ViewFootprint
from pm.view.history import HistoryData, ViewHistory
from pm.view.log import LogData, ViewLog
from pm.view.petri import PetriData, ViewPetri
from pm.view.pm4pyalignments import PM4PyAlignmentsData, ViewPM4PyAlignments
from pm.view.pm4pyfootrpint import PM4PyFootrpintData, ViewPM4PyFootprint
from pm.view.record import StepsData, RecordData


class AllData(FootprintData, HistoryData):
    def __init__(self):
        super(Data, self).__init__()
        for _class in [HistoryData(None, None), PetriData(None), LogData(None),
                       FootprintData(None, None, None), PM4PyFootrpintData(None),
                       ConfFootprintData(None, None), PM4PyAlignmentsData(None),
                       StepsData(None, None, None, None),
                       RecordData(None, None), CommonData(None)]:
            for key, value in getattr(_class, '__dict__').items():
                self.__dict__[key] = value
        self.upload = None


class ViewManager(View):
    VIEWS_ALL = {ViewHistory.ID, ViewPetri.ID, ViewLog.ID,
                 ViewFootprint.ID, ViewPM4PyFootprint.ID,
                 ViewConfFootprint.ID, ViewPM4PyAlignments.ID}
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
                    AlgorithmsManager().process_upload(self._request_post('name', str, ''), self._request.user,
                                   self._request.FILES.get('file'), self._request.FILES.get('file2'))
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

        if files.log is not None:
            log = ViewLog(self._request, record)
            self.data.header = log.header()
            if view == ViewLog.ID:
                self.data = log.load(files.log)

        if files.petri is not None:
            petri = ViewPetri(self._request, record)
            self.data.header = petri.header()
            if view == ViewPetri.ID:
                self.data = petri.load(files.petri)

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

        if files.pm4py_alignments is not None:
            pm4pyalignments = ViewPM4PyAlignments(self._request, record)
            self.data.header = pm4pyalignments.header()
            if view == ViewPM4PyAlignments.ID:
                self.data = pm4pyalignments.load(files.pm4py_alignments)

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
            recs = Record.objects.filter(user=self._request.user)
            for rec in recs:
                shutil.rmtree(os.path.join(StoredFiles.FILES, str(rec.id)), ignore_errors=True)
                shutil.rmtree(os.path.join(StoredFiles.TEMP, str(rec.id)), ignore_errors=True)
                rec.delete()
            self.data.redirect = redirect('/')
            return False
        return True

    def __download_file(self):
        record = self._request_get('download', int, None, self.RECORD)
        if record is not None:
            rec = Record.objects.get(id=record)
            files = StoredFiles.from_dict(json.loads(rec.json))
            if files.src2 is None:
                self.data.redirect = FileResponse(open(files.src.path, 'rb'), as_attachment=True)
            else:
                path = os.path.join(StoredFiles.TEMP, str(rec.id))
                os.makedirs(path, exist_ok=True)
                tempfile = StoredFiles(rec.id).make_temp(f"record_{rec.id}", '.zip')
                with ZipFile(tempfile.path, 'w') as zipObj2:
                    zipObj2.write(files.src.path, files.src.fullname)
                    zipObj2.write(files.src2.path, files.src2.fullname)
                self.data.redirect = FileResponse(open(tempfile.path, 'rb'), as_attachment=True)
                shutil.rmtree(path, ignore_errors=True)
            return False
        return True
