import json
import os.path
from threading import Thread

from django.core.files.uploadedfile import InMemoryUploadedFile

from pm.storage import StoredFiles
from .common import AlgorithmsCommon
from .footprint import AlgorithmsFootprint
from .petri import AlgorithmsPetri
from .pm4pyfootprint import AlgorithmsPM4PyFootprint
from .pm4pyalignments import AlgorithmsPM4PyAlignments
from ..models import Record


class AlgorithmsManager(AlgorithmsCommon):
    def process_upload(self, rname, user, uploaded: InMemoryUploadedFile, uploaded2: InMemoryUploadedFile = None):
        errors = self.validate_ext([uploaded, uploaded2])
        if len(errors) > 0:
            raise Exception(' '.join(errors))

        rec = Record(name=rname, user=user)
        rec.save()
        files = StoredFiles(rec.id, True)
        files.src = files.handle_uploaded_file(uploaded).copy()
        if uploaded2 is not None:
            files.src2 = files.handle_uploaded_file(uploaded2).copy()
        rec.json = json.dumps(files.to_dict(), indent=4)
        rec.save()
        t = Thread(target=AlgorithmsManager.runAll, args=[rec, files], daemon=True)
        t.start()
        return rec

    def validate_ext(self, files):
        errors = []
        files = list(filter(None, files))
        for file in files:
            name, ext = os.path.splitext(file.name)
            if len(files) > 1 and ext not in {'.xes', '.pnml', '.csv'} or ext not in {'.txt', '.xes', '.pnml', '.csv'}:
                errors.append(f"File \'{file.name}\' has inappropriate extension.")
        return errors

    @staticmethod
    def runAll(rec: Record, files: StoredFiles):
        try:
            src = files.src
            src2 = files.src2
            if src.ext in {'.xes', '.pnml', '.csv'}:
                files.petri = AlgorithmsPetri().run(src).copy()
            if src2 is None:
                files.footprint = AlgorithmsFootprint().run(src).copy()
                if src.ext in {'.xes', '.pnml', '.csv'}:
                    files.pm4py_footprint = AlgorithmsPM4PyFootprint().run(src).copy()
            elif src.ext in {'.xes', '.pnml', '.csv'} and src2.ext in {'.xes', '.pnml', '.csv'}:
                files.pm4py_alignments = AlgorithmsPM4PyAlignments().run(src, src2).copy()

            if Record.objects.filter(user=rec.user, id=rec.id).exists():
                rec.json = json.dumps(files.to_dict(), indent=4)
                rec.isloaded = True
                rec.save()
        except Exception as ex:
            if Record.objects.filter(user=rec.user, id=rec.id).exists():
                if hasattr(ex, 'filename'):
                    ex.filename = os.path.basename(ex.filename)
                rec.error = str(ex)
                rec.isloaded = True
                rec.save()
        del files
