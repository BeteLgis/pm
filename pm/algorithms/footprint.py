from pm.algorithms.common import AlgorithmsCommon
from pm.storage import StoredFile


class AlgorithmsFootprint(AlgorithmsCommon):
    def run(self, file: StoredFile) -> StoredFile:
        log = self.read_log(file)
        return self.save(file.files.make_temp(f"{file.fullname}_steps", '.json'), self.spsfootprints(log))

    def spsfootprints(self, log):
        steps = []
        codes = {}
        for trace in log:
            trace = trace[0]
            size = len(trace)
            if size > 1:
                codes[trace[0]] = 0
                for i in range(size - 1):
                    codes[trace[i + 1]] = 1
                    step = {
                        'line': trace,
                        'pi': i, 'ci': i + 1,
                        'pval': trace[i], 'cval': trace[i + 1]
                    }
                    if i + 2 < size:
                        step['pin'] = i + 1
                        step['cin'] = i + 2
                    steps.append(step)
        numcodes = sorted(codes.keys())
        size = len(numcodes)
        rg = range(size)
        for i in rg:
            codes[numcodes[i]] = i

        matrix = [[0 for _ in rg] for _ in rg]
        clean_steps = []
        for step in steps:
            prev = codes[step['pval']]
            cur = codes[step['cval']]
            if matrix[prev][cur] != 2:
                if matrix[cur][prev] == 1:
                    matrix[prev][cur] = 2
                    matrix[cur][prev] = 2
                    clean_steps.append(step)
                elif matrix[prev][cur] != 1:
                    matrix[prev][cur] = 1
                    matrix[cur][prev] = -1
                    clean_steps.append(step)

            step['prev'] = prev
            step['cur'] = cur
            step['matrix'] = [row[:] for row in matrix]

        steps.append({'matrix': matrix})
        clean_steps.append({'matrix': matrix})
        return {
            'head': numcodes,
            'steps': steps,
            'clean_steps': clean_steps
        }
