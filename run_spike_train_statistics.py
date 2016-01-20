# encoding: utf-8
"""
Spike train statistics benchmark.

This script creates a population of Poisson process spike sources, each with a
different rate, records the spikes, then checks that the distributions of interspike
intervals are all exponential, using the Kolmogorov-Smirnov test.

Model: population of SpikeSourcePoisson sources
Measures:
    (1) minimum of p-values from one-sample Kolmogorov-Smirnov test over all rates
    (2) time to setup the simulation
    (3) time to run the simulation
    (4) time for data retrieval and cleanup

Results are saved to a directory 'results/<timestamp>'

Authors: Andrew Davison, UNIC, CNRS
Copyright 2014

"""

from __future__ import division
import os
from datetime import datetime
import json
import numpy
import matplotlib.pyplot as plt
from scipy.stats import kstest, expon
from elephant.statistics import isi


BENCHMARK_NAME = "spike_train_statistics"


def analysis_quality(data, timestamp, **options):
    data_pop = data.segments[0].spiketrains
    g = open("%s.json" % BENCHMARK_NAME, 'r')
    d = json.load(g)
    N = d['param']['N']
    max_rate = d['param']['max_rate']
    delta_rate = max_rate/N
    tstop = d['param']['tstop']
    mean_intervals = 1000.0/numpy.linspace(delta_rate, max_rate, N)
    isi_distributions = []
    for spiketrain in data_pop:
        isi_distributions.append(isi(spiketrain))
        print spiketrain.annotations

    if options['plot_figure']:
         for i, (distr, expected_mean_interval) in enumerate(zip(isi_distributions, mean_intervals)[:8]):
            plt.subplot(4, 2, i + 1)
            counts, bins, _ = plt.hist(distr, bins=50)
            emi = expected_mean_interval
            plt.plot(bins, emi * distr.size * (numpy.exp(-bins[0]/emi) - numpy.exp(-bins[1]/emi)) * expon.pdf(bins, scale=emi), 'r-')
         plt.savefig("results/%s/spike_train_statistics.png" % timestamp)

    p_values = numpy.zeros((N,))
    for i, (distr, expected_mean_interval) in enumerate(zip(isi_distributions, mean_intervals)):
        D, p = kstest(distr, "expon", args=(0, expected_mean_interval),  # args are (loc, scale)
                      alternative='two-sided')
        p_values[i] = p
        print expected_mean_interval, distr.mean(), D, p, distr.size
    # Should we use the D statistic or the p-value as the benchmark?
    # note that D --> 0 is better, p --> 1 is better (but p > 0.01 should be ok, I guess?)
    # D is less variable, but depends on N.
    # taking the minimum p-value means we're more likely to get a false "significantly different" result.
    return {'type':'quality', 'name': 'kolmogorov_smirnov',
            'measure': 'min-p-value', 'value': p_values.min()}


def analysis_performance(times, results):
    results.append({'type': 'performance', 'name':  'setup_time', 'measure': 'time', 'value': times['setup_time']})
    results.append({'type': 'performance', 'name':  'run_time', 'measure': 'time', 'value': times['run_time']})
    results.append({'type': 'performance', 'name':  'closing_time', 'measure': 'time', 'value': times['closing_time']})
    return results


def output_result(results, options, timestamp):
    output = {"results": results,
              "command_line_options": options,
              "timestamp": timestamp}
    with open("I_f_curve.json", 'r') as f:
        output["configuration"] = {"model": json.load(f)}
    print("RESULTS")
    print(output)  # debug
    with open("results/%s/%s.json" % (timestamp, BENCHMARK_NAME), 'w') as f:
        json.dump(output, f, indent=4)


def benchmarks(sim, **options):
    from spike_train_statistics import run_model
    data, times = run_model(sim, **options)
    timestamp = datetime.now().isoformat()
    if not os.path.exists("results/" + timestamp):
        os.makedirs("results/" + timestamp)
    results = []
    results.append(analysis_quality(data, timestamp, **options))
    results = analysis_performance(times, results)
    output_result(results, options, timestamp)


if __name__ == '__main__':
    from pyNN.utility import get_simulator  # PyNN 0.8

    sim, options = get_simulator(("--plot-figure", "plot a graph of the result"))
    benchmarks(sim=sim, **vars(options))
