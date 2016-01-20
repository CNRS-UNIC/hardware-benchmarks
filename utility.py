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
