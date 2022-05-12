import json
import re

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

    def read_log(self, file: StoredFile):
        self.notempty(file)
        if file.ext == '.txt':
            log = self.read_txt(file.path)
        elif file.ext == '.xes':
            log = self.make_log(self.read_xes(file.path))
        elif file.ext == '.pnml':
            log = self.make_log(self.read_pnml_as_log(file.path))
        else:
            log = self.make_log(self.read_csv(file.path))
        return log

    def read_txt(self, path):
        lines = open(path, 'r').readlines()
        traces = {}
        for line in lines:
            key = re.sub('\s+', ' ', line.strip())
            if key not in traces:
                traces[key] = [tuple(key.split(' ')), 0]
            traces[key][1] += 1
        res = []
        for trace in traces:
            res.append(traces[trace])
        res = sorted(res, key=lambda x: (x[1], x[0]), reverse=True)
        return res

    def notempty(self, file: StoredFile):
        lines = open(file.path, 'r').readlines()
        empty = True
        for line in lines:
            if empty and line.strip() != '':
                empty = False
                break
        if empty:
            raise Exception(f"File {file.fullname} is empty.")

    def make_log(self, log):
        from pm4py.algo.filtering.log.variants import variants_filter
        import pm4py
        pm4py.util.variants_util.VARIANT_SPECIFICATION = pm4py.util.variants_util.VariantsSpecifications.LIST
        return variants_filter.get_variants_sorted_by_count(variants_filter.get_variants(log))

    def save(self, file: StoredFile, data):
        f = open(file.path, "w")
        f.write(json.dumps(data, indent=4))
        f.close()
        return file
