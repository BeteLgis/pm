from pm.algorithms.common import AlgorithmsCommon
from pm.storage import StoredFile


class AlgorithmsPM4PyFootprint(AlgorithmsCommon):
    def run(self, file: StoredFile) -> StoredFile:
        from pm4py.algo.discovery.footprints import algorithm as footprints_discovery
        from pm4py.visualization.footprints import visualizer as fp_visualizer

        if file.ext == '.pnml':
            net, im, fm = self.read_pnml(file.path)
            fp_log = footprints_discovery.apply(net, im, fm)
        else:
            log = self.read_xes(file.path) if file.ext == '.xes' else self.read_csv(file.path)
            fp_log = footprints_discovery.apply(log, variant=footprints_discovery.Variants.ENTIRE_EVENT_LOG)

        gviz = fp_visualizer.apply(fp_log, parameters={fp_visualizer.Variants.SINGLE.value.Parameters.FORMAT: "svg"})
        tempfile = file.files.make_temp(f"{file.fullname}_footprints", '.svg')
        fp_visualizer.save(gviz, tempfile.path)
        return tempfile
