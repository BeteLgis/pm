from pm.algorithms.common import AlgorithmsCommon
from pm.storage import StoredFile


class AlgorithmsLog(AlgorithmsCommon):
    def run(self, file: StoredFile) -> StoredFile:
        return self.save(file.files.make_temp(f"{file.fullname}_log", '.json'), self.read_log(file))
