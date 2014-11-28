# encoding: utf-8
"""
Run all benchmarks in this repository.

Authors: Andrew Davison and Joël Chavas, UNIC, CNRS
Copyright 2014

"""

from glob import glob
from os.path import splitext

try:
    from pyNN.utility import get_simulator  # PyNN 0.8
except ImportError:
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
                            help="neuron, nest, brian, pcsim or another backend simulator")
        for argument in arguments:
            arg_name, help_text = argument[:2]
            extra_args = {}
            if len(argument) > 2:
                extra_args = argument[2]
            parser.add_argument(arg_name, help=help_text, **extra_args)
        args = parser.parse_args()
        sim = import_module("pyNN.%s" % args.simulator)
        return sim, args


sim, options = get_simulator(("--plot-figure", "plot a graph of the result"))

list_benchmarks = glob("run_*.py")
for f in list_benchmarks:
    exec("from %s import benchmarks" % splitext(f)[0])
    benchmarks(sim=sim, **vars(options))