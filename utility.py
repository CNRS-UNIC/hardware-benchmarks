"""
Utility functions for benchmarks.


Authors: Andrew Davison, UNIC, CNRS
Copyright 2014
"""

import neo


def spike_array_to_neo(spike_array, population, t_stop):
    """
    Convert the spike array produced by PyNN 0.7 to a Neo Block
    (the data format used by PyNN 0.8)
    """
    from datetime import datetime
    segment = neo.Segment(name="I-F curve data", rec_datetime=datetime.now())
    segment.spiketrains = []
    for index in range(len(population)):
        segment.spiketrains.append(
            neo.SpikeTrain(spike_array[:, 1][spike_array[:, 0] == index],
                           t_start=0.0,
                           t_stop=t_stop,
                           units='ms',
                           source_index=index))
    data = neo.Block(name="I-F curve data")
    data.segments.append(segment)
    return data


# copied the following from PyNN 0.8, for use with PyNN 0.7 scripts
def get_simulator(*arguments):
    """
    Import and return a PyNN simulator backend module based on command-line
    arguments.

    The simulator name should be the first positional argument. If your script
    needs additional arguments, you can specify them as (name, help_text) tuples.
    If you need more complex argument handling, you should use argparse
    directly.

    Returns (simulator, command-line arguments)
    """
    import argparse
    from importlib import import_module
    parser = argparse.ArgumentParser()
    parser.add_argument("simulator",
                        help="neuron, nest, brian or another backend simulator")
    for argument in arguments:
        arg_name, help_text = argument[:2]
        extra_args = {}
        if len(argument) > 2:
            extra_args = argument[2]
        parser.add_argument(arg_name, help=help_text, **extra_args)
    args = parser.parse_args()
    sim = import_module("pyNN.%s" % args.simulator)
    return sim, args
