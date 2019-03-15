# encoding: utf-8
"""
A population of random spike sources, each with different firing rates.

The model parameters are read from a configuration file "spike_train_statistics.json".

The model works with PyNN versions 0.7 and 0.8.


Authors: Andrew Davison, UNIC, CNRS
Copyright 2014

"""

from __future__ import division, print_function
import numpy
from pyNN import __version__ as pyNN_version
try:
    from pyNN.hardware.brainscales import mapper
except ImportError:
    print("Could not import mapper. Trying to continue...")

PYNN07 = pyNN_version.split(".")[1] == '7'
if PYNN07:
    from utility import spike_array_to_neo


def run_model(sim, **options):
    """
    Run a simulation using the parameters read from the file "spike_train_statistics.json"

    :param sim: the PyNN backend module to be used.
    :param options: should contain a keyword "simulator" which is the name of the PyNN backend module used.
    :return: a tuple (`data`, `times`) where `data` is a Neo Block containing the recorded spikes
             and `times` is a dict containing the time taken for different phases of the simulation.
    """

    import json
    from pyNN.utility import Timer

    print("Running")

    timer = Timer()

    g = open("spike_train_statistics.json", 'r')
    d = json.load(g)

    N = d['param']['N']
    max_rate = d['param']['max_rate']
    tstop = d['param']['tstop']
    d['SpikeSourcePoisson'] = {
        "duration": tstop
    }

    if options['simulator'] == "hardware.brainscales":
        hardware_preset = d['setup'].pop('hardware_preset', None)
        if hardware_preset:
            d['setup']['hardware'] = sim.hardwareSetup[hardware_preset]
        d['SpikeSourcePoisson']['random'] = True
        place = mapper.place()

    timer.start()
    sim.setup(**d['setup'])

    spike_sources = sim.Population(N, sim.SpikeSourcePoisson, d['SpikeSourcePoisson'])
    delta_rate = max_rate/N
    rates = numpy.linspace(delta_rate, max_rate, N)
    print("Firing rates: %s" % rates)
    if PYNN07:
        spike_sources.tset("rate", rates)
    else:
        spike_sources.set(rate=rates)

    if options['simulator'] == "hardware.brainscales":
        for i, spike_source in enumerate(spike_sources):
            place.to(spike_source, hicann=i//8, neuron=i%64)
        place.commit()

    if PYNN07:
        spike_sources.record()
    else:
        spike_sources.record('spikes')

    setup_time = timer.diff()
    sim.run(tstop)
    run_time = timer.diff()

    if PYNN07:
        spike_array = spike_sources.getSpikes()
        data = spike_array_to_neo(spike_array, spike_sources, tstop)
    else:
        data = spike_sources.get_data()

    sim.end()

    closing_time = timer.diff()
    times = {'setup_time': setup_time, 'run_time': run_time, 'closing_time': closing_time}

    return data, times
