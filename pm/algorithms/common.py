import json

from pm4py import read_xes, read_pnml

from pm.storage import StoredFile


class AlgorithmsCommon:
    def run(self, *args) -> StoredFile:
        pass

    def read_xes(self, path):
        return read_xes(path)

    def read_pnml(self, path):
        return read_pnml(path)

    def read_csv(self, path):
        import pandas as pd
        from pm4py.objects.log.util import dataframe_utils
        from pm4py.objects.conversion.log import converter as log_converter

        log_csv = pd.read_csv(path, sep=',')
        log_csv = dataframe_utils.convert_timestamp_columns_in_df(log_csv)
        log_csv = log_csv.sort_values('time:timestamp')
        return log_converter.apply(log_csv)

    def read_pnml_as_log(self, path):
        from pm4py.algo.simulation.playout.petri_net import algorithm as simulator
        net, im, fm = self.read_pnml(path)
        return simulator.apply(net, im, fm, variant=simulator.Variants.EXTENSIVE)

    def inductive(self, log):
        from pm4py.algo.discovery.inductive import algorithm as inductive_miner
        return inductive_miner.apply(log)

    def save(self, file: StoredFile, data):
        f = open(file.path, "w")
        f.write(json.dumps(data, indent=4))
        f.close()
        return file
