import os
import shutil

from django.core.files.uploadedfile import InMemoryUploadedFile

from pm import settings


class StoredFile:
    def __init__(self, files, path='', fullname=''):
        self.files = files
        self.path = path
        self.fullname = fullname
        name, ext = os.path.splitext(path if fullname.strip() == '' else fullname)
        self.name = name
        self.ext = ext

    def copy(self):
        path = os.path.join(self.files.path, self.fullname)
        shutil.copy2(self.path, path)
        self.path = path
        return self

    def to_dict(self):
        return {
            'path': self.path,
            'fullname': self.fullname
        }

    @staticmethod
    def from_dict(files, data):
        return StoredFile(files, data['path'], data['fullname']) if data is not None else None


class StoredFiles:
    FILES = os.path.join(settings.MEDIA_ROOT, 'files')
    TEMP = os.path.join(settings.MEDIA_ROOT, 'temp')

    def __init__(self, id, makedirs=False):
        self.id = id
        self.temp = os.path.join(self.TEMP, str(id))
        self.path = os.path.join(self.FILES, str(id))
        if makedirs:
            os.makedirs(self.temp, exist_ok=True)
            os.makedirs(self.path, exist_ok=True)
        self.src = None
        self.src2 = None
        self.footprint = None
        self.pm4py_footprint = None
        self.pm4py_alignments = None
        self.petri = None
        self.log = None

    def __del__(self):
        shutil.rmtree(self.temp, ignore_errors=True)

    def handle_uploaded_file(self, file: InMemoryUploadedFile):
        path = os.path.join(self.temp, file.name)
        with open(path, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)
        return StoredFile(self, path, file.name)

    def make_temp(self, rawname, ext):
        name = rawname.replace('.', '+') + ext
        path = os.path.join(self.temp, name)
        return StoredFile(self, path, name)

    def to_dict(self):
        return {
            'id': self.id,
            'src': self.src.to_dict() if self.src is not None else None,
            'src2': self.src2.to_dict() if self.src2 is not None else None,
            'footprint': self.footprint.to_dict() if self.footprint is not None else None,
            'pm4py_footprint': self.pm4py_footprint.to_dict() if self.pm4py_footprint is not None else None,
            'pm4py_alignments': self.pm4py_alignments.to_dict() if self.pm4py_alignments is not None else None,
            'petri': self.petri.to_dict() if self.petri is not None else None,
            'log': self.log.to_dict() if self.log is not None else None
        }

    @staticmethod
    def from_dict(data):
        files = StoredFiles(data['id'])
        files.src = StoredFile.from_dict(files, data['src'])
        files.src2 = StoredFile.from_dict(files, data['src2'])
        files.footprint = StoredFile.from_dict(files, data['footprint'])
        files.pm4py_footprint = StoredFile.from_dict(files, data['pm4py_footprint'])
        files.pm4py_alignments = StoredFile.from_dict(files, data['pm4py_alignments'])
        if 'petri' in data:
            files.petri = StoredFile.from_dict(files, data['petri'])
        if 'log' in data:
            files.log = StoredFile.from_dict(files, data['log'])
        return files
