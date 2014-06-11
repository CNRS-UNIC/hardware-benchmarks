from glob import glob
from os.path import splitext
from pyNN.utility import get_simulator

sim, options = get_simulator(("--debug", "the debug option plots the result"))

list_benchmarks = glob("run_*.py")
for f in list_benchmarks:
    exec("from %s import benchmarks" % splitext(f)[0])
    benchmarks(sim=sim, **vars(options))