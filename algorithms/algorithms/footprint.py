import json
import re

from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.objects.petri_net.importer import importer as pnml_importer

from algorithms.storage import StoredFile


def footprint(file: StoredFile) -> StoredFile:
    check(file)
    log = []
    match file.ext:
        case '.txt':
            log = read_txt(file)
        case '.xes':
            log = read_xes(file)
        case '.pnml':
            log = read_pnml(file)
    data = spsfootprints(log)

    tempfile = file.files.make_temp(f"{file.fullname}_steps", '.json')
    f = open(tempfile.path, "w")
    f.write(json.dumps(data, indent=4))
    f.close()
    return tempfile


def check(file: StoredFile):
    lines = open(file.path, 'r').readlines()
    empty = True
    for line in lines:
        if empty and line.strip() != '':
            empty = False
            break
    if empty:
        raise Exception(f"File {file.fullname} is empty.")


def read_txt(file: StoredFile):
    res = []
    lines = open(file.path, 'r').readlines()
    traces = {}
    for line in lines:
        key = re.sub('\s+', ' ', line.strip())
        if key not in traces:
            traces[key] = {'count': 0}
            res.append(key.split(' '))
        traces[key]['count'] += 1
    return res


def read_xes(file: StoredFile):
    return read_log(xes_importer.apply(file.path))


def read_pnml(file: StoredFile):
    from pm4py.algo.simulation.playout.petri_net import algorithm as simulator

    net, im, fm = pnml_importer.apply(file.path)
    return read_log(simulator.apply(net, im, fm, variant=simulator.Variants.EXTENSIVE))


def read_log(log):
    res = []
    for trace in log:
        tmp = []
        for event in trace:
            tmp.append(event['concept:name'])
        res.append(tmp)
    return res


def spsfootprints(log):
    steps = []
    codes = {}
    for trace in log:
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


def pm4py_footprint(file: StoredFile) -> StoredFile:
    from pm4py.algo.discovery.footprints import algorithm as footprints_discovery
    from pm4py.visualization.footprints import visualizer as fp_visualizer

    if file.ext == '.pnml':
        net, im, fm = pnml_importer.apply(file.path)
        fp_log = footprints_discovery.apply(net, im, fm)
    else:
        log = xes_importer.apply(file.path)
        fp_log = footprints_discovery.apply(log, variant=footprints_discovery.Variants.ENTIRE_EVENT_LOG)

    gviz = fp_visualizer.apply(fp_log, parameters={fp_visualizer.Variants.SINGLE.value.Parameters.FORMAT: "svg"})
    tempfile = file.files.make_temp(f"{file.fullname}_img", '.svg')
    fp_visualizer.save(gviz, tempfile.path)
    return tempfile
