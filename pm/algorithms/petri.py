from pm.algorithms.common import AlgorithmsCommon
from pm.storage import StoredFile


class AlgorithmsPetri(AlgorithmsCommon):
    def run(self, file: StoredFile) -> StoredFile:
        from pm4py.visualization.petri_net import visualizer as pn_visualizer

        if file.ext == '.pnml':
            net, im, fm = self.read_pnml(file.path)
        else:
            log = self.read_xes(file.path) if file.ext == '.xes' else self.read_csv(file.path)
            net, im, fm = self.inductive(log)

        gviz = pn_visualizer.apply(net, im, fm, parameters={pn_visualizer.Variants.WO_DECORATION.value.Parameters.FORMAT: "svg"})
        tempfile = file.files.make_temp(f"{file.fullname}_petri", '.svg')
        pn_visualizer.save(gviz, tempfile.path)
        return tempfile
