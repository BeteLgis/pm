from pm.algorithms.common import AlgorithmsCommon
from pm.storage import StoredFile


class AlgorithmsPM4PyAlignments(AlgorithmsCommon):
    def run(self, file: StoredFile, file2: StoredFile) -> StoredFile:
        from pm4py.algo.conformance.alignments import algorithm as alignments
        from pm4py.visualization.align_table import visualizer as al_visualizer

        if file.ext == '.pnml' and file2.ext in {'.xes', '.txt'}:
            net, im, fm = self.read_pnml(file.path)
            log = self.read_xes(file2.path) if file2.ext == '.xes' else self.read_csv(file2.path)

        elif file2.ext == '.pnml' and file.ext in {'.xes', '.txt'}:
            net, im, fm = self.read_pnml(file2.path)
            log = self.read_xes(file.path) if file.ext == '.xes' else self.read_csv(file.path)

        elif file.ext == '.pnml' and file2.ext == '.pnml':
            net, im, fm = self.read_pnml(file.path)
            log = self.read_pnml_as_log(file2.path)

        else:
            log = self.read_xes(file.path) if file.ext == '.xes' else self.read_csv(file.path)
            net, im, fm = self.inductive(self.read_xes(file2.path) if file2.ext == '.xes' else self.read_csv(file2.path))

        aligned_traces = alignments.apply_log(log, net, im, fm)
        gviz = al_visualizer.apply(log, aligned_traces, parameters={al_visualizer.Variants.CLASSIC.value.Parameters.FORMAT: "svg"})
        tempfile = file.files.make_temp(f"{file.fullname}_alignments", '.svg')
        al_visualizer.save(gviz, tempfile.path)
        return tempfile
