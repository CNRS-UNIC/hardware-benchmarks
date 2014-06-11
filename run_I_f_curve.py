#data = run(model, sim, parameters)
#results=analysis(data)
#json: use type, name(giturl+localpath+variable), description and value,
#a passFail field in the parameter json field (input and output)

#output = span_results(results)


#data = run(sim, model, parameters)
#results=analysis(data) curve:

#output(results)
#(interface: a json file)

#-IFcurve: quality: root mean square
#- execution time:

#mettre parametre dans fichier resultat


import json
import numpy
from numpy import log
import matplotlib.pyplot as plt

def U(V, i, rm, v_rest):
    return V - i*rm - v_rest

def analysis_quality(data, **options):
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
    frequencies = numpy.zeros(N)
    current = numpy.arange(N)*max_current/N
    analytic_frequencies = 1 / (tau_refrac + \
        tau_m * log ( U(v_reset, current, rm, v_rest) / U(v_thresh, current, rm, v_rest) ) )
    frequencies = numpy.zeros(N)
    for i in xrange(N):
        frequencies[i] = len(data_pop[i])/float(tstop)
    analytic_frequencies = 1000*analytic_frequencies
    frequencies = 1000*frequencies
    if options['debug']:
        plt.plot(current, analytic_frequencies)
        plt.plot(current, frequencies)
        plt.xlabel("i (nA)")
        plt.ylabel("frequency (Hz)")
        plt.show()
    norm_diff_frequency = numpy.linalg.norm(numpy.nan_to_num((frequencies-analytic_frequencies)/analytic_frequencies))
    return {'type':'quality', 'name': 'giturl+localpath+norm_diff_frequency', 'measure': 'norm', 'value':norm_diff_frequency}
            
def analysis_performance(times, results):
    results.append({'type': 'performance', 'name': 'giturl+localpath+setup_time', 'measure': 'time', 'value':times['setup_time']})
    results.append({'type': 'performance', 'name': 'giturl+localpath+run_time', 'measure': 'time', 'value':times['run_time']})
    results.append({'type': 'performance', 'name': 'giturl+localpath+closing_time', 'measure': 'time', 'value':times['closing_time']})
    return results

def output_result(results):
    f = open("I_f_curve_result.json", 'w')
    json.dump(results, f, indent=4)
    g = open("I_f_curve.json", 'r')
    d = json.load(g)
    json.dump(d, f, indent=4)
    g.close()
    g = open("compare_to_analytic_I_f_curve.json", 'r')
    d = json.load(g)
    json.dump(d, f, indent=4)
    g.close()
    f.close()
    
def benchmarks(**options):
    from I_f_curve import run_model
    data, times = run_model(**options)
    results =[]
    results.append(analysis_quality(data, **options))
    results = analysis_performance(times, results)
    output_result(results)
    
if __name__ == '__main__':
    from glob import glob
    from os.path import splitext
    from pyNN.utility import get_simulator

    sim, options = get_simulator(("--debug", "the debug option plots the result"))
    benchmarks(sim=sim, **vars(options))