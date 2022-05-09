import json
import os.path
from threading import Thread

from django.core.files.uploadedfile import InMemoryUploadedFile

from algorithms.storage import StoredFiles
from .footprint import footprint, pm4py_footprint
from ..models import Record


def process_upload(rname, user, uploaded: InMemoryUploadedFile):
    name, ext = os.path.splitext(uploaded.name)
    if ext not in ['.txt', '.xes', '.pnml']:
        raise Exception(f"File \'{uploaded.name}\' has inappropriate extension.")

    rec = Record(name=rname, user=user)
    rec.save()
    files = StoredFiles(rec.id, True)
    files.src = files.handle_uploaded_file(uploaded).copy()
    rec.json = json.dumps(files.to_dict(), indent=4)
    rec.save()
    t = Thread(target=make_steps, args=[rec, files], daemon=True)
    t.start()
    return rec


def make_steps(rec: Record, files: StoredFiles):
    try:
        files.footprint = footprint(files.src).copy()
        if files.src.ext in {'.xes', '.pnml'}:
            files.pm4py_footprint = pm4py_footprint(files.src).copy()

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
