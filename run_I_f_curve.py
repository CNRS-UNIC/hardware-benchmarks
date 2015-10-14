# encoding: utf-8
"""
f-I curve benchmark.

This script simulates a population of IF neurons, each of which is injected with a different current,
records the spikes, and uses these to calculate the firing frequency as a function of the injected
current.

Model: population of unconnected IF neurons
Measures:
    (1) difference between the measured and expected (calculated analytically) frequencies
    (2) time to setup the simulation
    (3) time to run the simulation
    (4) time for data retrieval and cleanup

Results are saved to a directory 'results/<timestamp>'

Authors: Andrew Davison and Joël Chavas, UNIC, CNRS
Copyright 2014

"""

from __future__ import division
import os
from datetime import datetime
import json
import numpy
from numpy import log
import matplotlib.pyplot as plt
from elephant.statistics import isi


def U(V, i, rm, v_rest):
    return V - i*rm - v_rest


def analysis_quality(data, measurement_base_name, timestamp, **options):
    data_pop = data.segments[0].spiketrains
    g = open("I_f_curve.json", 'r')
    d = json.load(g)
    N = d['param']['N']
    max_current = d['param']['max_current']
    tstop = d['param']['tstop']
    tau_refrac = d['IF_cond_exp']['tau_refrac']
    tau_m = d['IF_cond_exp']['tau_m']
    rm = tau_m / d['IF_cond_exp']['cm']
    v_rest = d['IF_cond_exp']['v_rest']
    v_reset = d['IF_cond_exp']['v_reset']
    v_thresh = d['IF_cond_exp']['v_thresh']
    current = (numpy.arange(N)+1)*max_current/N
    analytic_frequencies = 1000 / (tau_refrac + \
        tau_m * log ( U(v_reset, current, rm, v_rest) / U(v_thresh, current, rm, v_rest) ) )
    frequencies = numpy.zeros(N)
    for i in xrange(N):
        #frequencies[i] = 1000*len(data_pop[i])/float(tstop)
        frequencies[i] = 1000/isi(data_pop[i]).mean()

    #print "Spike times"
    #print data_pop[0]
    #print data_pop[1]
    #print data_pop[-2]
    #print data_pop[-1]
    #print "Analytical frequencies"
    #print analytic_frequencies
    #print "Measured frequencies"
    #print frequencies

    if options['plot_figure']:
        plt.plot(current, analytic_frequencies, label="analytic")
        plt.plot(current, frequencies, label=options["simulator"])
        plt.xlabel("i (nA)")
        plt.ylabel("frequency (Hz)")
        plt.legend(loc='upper left')
        plt.savefig("results/%s/f_I_curve.png" % timestamp)
        #from pyNN.utility.plotting import Figure, Panel
        #from quantities import ms
        #Figure(
        #    Panel(data_pop, markersize=0.2, xticks=True),
        #    Panel(data.segments[0].analogsignalarrays[0].time_slice(0*ms, 100.0*ms), xticks=True)
        #).save("results/%s/spike_raster.png" % timestamp)

    norm_diff_frequency = numpy.linalg.norm(numpy.nan_to_num((frequencies-analytic_frequencies)/analytic_frequencies))
    return {'type':'quality', 'name': measurement_base_name + '#norm_diff_frequency',
            'measure': 'norm', 'value': norm_diff_frequency}


def get_repository_url():
    import subprocess
    url = "unknown"
    p = subprocess.Popen("git remote -v", stdout=subprocess.PIPE, shell=True)
    p.wait()
    for line in p.stdout:
        name, url = line.strip().split('\t')
        url = url.split(' ')[0]
        if name == 'origin':
            break
    return url


def analysis_performance(times, measurement_base_name, results):
    results.append({'type': 'performance', 'name': measurement_base_name + '#setup_time', 'measure': 'time', 'value':times['setup_time']})
    results.append({'type': 'performance', 'name': measurement_base_name + '#run_time', 'measure': 'time', 'value':times['run_time']})
    results.append({'type': 'performance', 'name': measurement_base_name + '#closing_time', 'measure': 'time', 'value':times['closing_time']})
    return results


def output_result(results, options, timestamp):
    output = {"results": results,
              "command_line_options": options,
              "timestamp": timestamp}
    with open("I_f_curve.json", 'r') as f:
        output["configuration"] = {"model": json.load(f)}
    with open("results/%s/I_f_curve_result.json" % timestamp, 'w') as f:
        json.dump(output, f, indent=4)


def benchmarks(sim, **options):
    from I_f_curve import run_model
    data, times = run_model(sim, **options)
    measurement_base_name = get_repository_url() + "/I_f_curve"
    timestamp = datetime.now().isoformat()
    if not os.path.exists("results/" + timestamp):
        os.makedirs("results/" + timestamp)
    results = []
    results.append(analysis_quality(data, measurement_base_name, timestamp, **options))
    results = analysis_performance(times, measurement_base_name, results)
    output_result(results, options, timestamp)


if __name__ == '__main__':
    try:
        from pyNN.utility import get_simulator  # PyNN 0.8
    except ImportError:
        from utility import get_simulator

    sim, options = get_simulator(("--plot-figure", "plot a graph of the result"))
    benchmarks(sim=sim, **vars(options))
