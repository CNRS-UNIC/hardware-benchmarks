# encoding: utf-8
"""
A population of IF neurons, each of which is injected with a different current.

The model parameters are read from a configuration file "I_f_curve.json".

The model works with PyNN versions 0.7 and 0.8.


Authors: Andrew Davison and Joël Chavas, UNIC, CNRS
Copyright 2014

"""

from __future__ import division
import numpy as np
from pyNN import __version__ as pyNN_version


PYNN07 = pyNN_version.split(".")[1] == '7'
if PYNN07:
    from utility import spike_array_to_neo


def run_model(sim, **options):
    """
    Run a simulation using the parameters read from the file "I_f_curve.json"

    :param sim: the PyNN backend module to be used.
    :param options: should contain a keyword "simulator" which is the name of the PyNN backend module used.
    :return: a tuple (`data`, `times`) where `data` is a Neo Block containing the recorded spikes
             and `times` is a dict containing the time taken for different phases of the simulation.
    """

    import json
    from pyNN.utility import Timer

    timer = Timer()

    g = open("I_f_curve.json", 'r')
    d = json.load(g)

    N = d['param']['N']
    max_current = d['param']['max_current']
    tstop = d['param']['tstop']

    if options['simulator'] == "hardware.brainscales":
        hardware_preset = d['setup'].pop('hardware_preset', None)
        if hardware_preset:
            d['setup']['hardware'] = sim.hardwareSetup[hardware_preset]

    timer.start()
    sim.setup(**d['setup'])

    popcell = sim.Population(N, sim.IF_cond_exp, d['IF_cond_exp'])

    #current_source = []
    #for i in xrange(N):
    #    current_source.append(sim.DCSource(amplitude=(max_current*(i+1)/N)))
    #    popcell[i:(i+1)].inject(current_source[i])
    i_offset = max_current * (1 + np.arange(N))/N
    if PYNN07:
        popcell.tset("i_offset", i_offset)
    else:
        popcell.set("i_offset", i_offset)

    if PYNN07:
        popcell.record()
    else:
        popcell.record('spikes')
        #popcell[0, 1, N-2, N-1].record('v')  # debug

    setup_time = timer.diff()
    sim.run(tstop)
    run_time = timer.diff()

    if PYNN07:
        spike_array = popcell.getSpikes()
        data = spike_array_to_neo(spike_array, popcell, tstop)
    else:
        data = popcell.get_data()

    sim.end()

    closing_time = timer.diff()
    times = {'setup_time': setup_time, 'run_time': run_time, 'closing_time': closing_time}

    return data, times
