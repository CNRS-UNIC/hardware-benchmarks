"""
A single IF neuron with exponential, conductance-based synapses, fed by two
spike sources.

Run as:

$ python IF_cond_exp.py <simulator>

where <simulator> is 'neuron', 'nest', etc

Andrew Davison, UNIC, CNRS
May 2006

"""

def run_model(**options):
    
    import json
    from pyNN.utility import Timer

    timer = Timer()
    
    sim = options['sim']
    g = open("I_f_curve.json", 'r')
    d = json.load(g)
    
    N = d['param']['N']
    max_current = d['param']['max_current']
    tstop = d['param']['tstop']

    timer.start()
    sim.setup(**d['setup'])
    

    ifcell = sim.IF_cond_exp(**d['IF_cond_exp'])

    popcell = sim.Population(N, ifcell)

    current_source = []
    for i in xrange(N):
        current_source.append(sim.DCSource(amplitude=max_current*i/N))
        popcell[i:(i+1)].inject(current_source[i])

    popcell.record('spikes')

    setup_time = timer.diff()
    sim.run(tstop)
    run_time = timer.diff()

    sim.end()
    closing_time = timer.diff()
    
    times = {'setup_time':setup_time, 'run_time': run_time, 'closing_time':closing_time}
    
    return popcell.get_data(), times