"""
MAUD/MILK spotlight tutorial

from https://spotlight.readthedocs.io/en/latest/notebooks/tutorial_milk_surrogate.html
"""

import MILK
import multiprocess
import os
import shutil
import time
from mystic import models
from spotlight import filesystem
from pathlib import Path
from multiprocessing import freeze_support

class CostFunction(models.AbstractFunction):

    def __init__(self, ndim=None, config=None):
        super().__init__(ndim=ndim)
        self.initialized = False
        self.config = config

    def reset(self):
        self.initialized = False

    def function(self, p):
        if not self.initialized:
            self.initialize()
            self.initialized = True
        return self.cost_function(p)

    def initialize(self):

        # get editor and maudText
        self.editor = MILK.parameterEditor.editor()
        self.editor.parseConfig(config)
        self.maudText = MILK.maud.maudText()
        self.maudText.parseConfig(config)

        # set run dir based on process name
        self.editor.run_dirs = f"opt_{multiprocess.current_process().name}"
        self.maudText.run_dirs = self.editor.run_dirs

        # create run dir
        if os.path.exists(self.editor.run_dirs):
            shutil.rmtree(self.editor.run_dirs)
        filesystem.mkdir(self.editor.run_dirs)
        filesystem.cp([str(Path().cwd() / 'templates/template_4768.par')], dest=self.editor.run_dirs) # CHANGE THIS LINE

        # set initial phase fractions
        self.editor.set_val(key='_pd_phase_atom_', value='0.33')
        self.editor.free(key='_pd_phase_atom_', wild=[0])

    def cost_function(self, p):

        t0 = time.time()

        # set lattice parameters as values from optimization
        self.editor.set_val(key='cell_length_a', sobj="alpha", value=str(p[0]))
        self.editor.set_val(key='cell_length_c', sobj="alpha", value=str(p[1]))
        self.editor.set_val(key='cell_length_a', sobj="steel", value=str(p[2]))
        self.editor.set_val(key='cell_length_c', sobj="beta", value=str(p[3]))

        # refine
        self.maudText.refinement(itr='1', ifile=self.editor.ifile, ofile=self.editor.ofile, simple_call=True)

        # get the statistic to return to the optimizer
        self.editor.get_val(key="_refine_ls_wR_factor_all")
        stat = float(self.editor.value[0])

        print(f"Our R-factor is {stat} and it took {time.time() - t0}s to compute")

        return stat
    
# set MILK configuration
config = {"folders": {"work_dir": "",
                      "run_dirs": "ack(wild)",
                      "sub_dir": "",
                      "wild": [0],
                      "wild_range": [[]],
          },
          "compute": {"maud_path": "",
                      "n_maud": 1,
                      "java_opt": "Xmx8G",
                      "clean_old_step_data": False,
                      "cur_step": 1,
                      "log_consol": False,
          },
          "ins": {"riet_analysis_file": "template_4768.par",
                  "riet_analysis_fileToSave": "output.par",
                  "section_title": "Ti64_test_data",
                  "analysis_iteration_number": 4,
                  "LCLS2_detector_config_file": "",
                  "LCLS2_Cspad0_original_image": "",
                  "LCLS2_Cspad0_dark_image": "",
                  "output_plot2D_filename": "plot_",
                  "output_summed_data_filename": "all_spectra",
                  "maud_output_plot_filename": "plot1d_",
                  "output_PF_filename": "PF_",
                  "output_PF": "",
                  "append_simple_result_to": "tmp_simple_results.txt",
                  "append_result_to": "tmp_results.txt",
                  "import_phase": [],
                  "ins_file_name": "MAUDText.ins",
                  "maud_remove_all_datafiles": True,
                  "verbose": 0,
          },
          "interface": {"verbose": 0,
          },
}

## Serial..
from mystic import tools
from mystic.solvers import diffev2
from mystic.math.legacydata import dataset, datapoint
from spotlight.bridge.ouq_models import WrapModel
from spotlight.bridge.ouq_models import InterpModel

## Parallel..
from mystic.solvers import LatticeSolver
from mystic.solvers import NelderMeadSimplexSolver
from mystic.termination import VTR
from pathos.pools import ProcessPool as Pool

# set random seed so we can reproduce results
tools.random_seed(0)

# set bounds for parameters to be +/-5%
target = [2.9306538, 4.6817646, 3.6026807, 3.233392]
lower_bounds = [x * 0.95 for x in target]
upper_bounds = [x * 1.05 for x in target]

# remove prior cached results
if os.path.exists("surrogate"):
    shutil.rmtree("surrogate")

# generate a sampled dataset for the model
truth = WrapModel("surrogate", CostFunction(4), nx=4, ny=None, cached=False)
bounds = list(zip(lower_bounds, upper_bounds))
data = truth.sample(bounds, pts=[2, 1, 1, 1])

# create surrogate model
surrogate = InterpModel("surrogate", nx=4, ny=None, data=truth, smooth=0.0, noise=0.0,
                        method="thin_plate", extrap=False)

if __name__ == "__main__":

    #=============
    # Using a Surrogate Model approach
    #=============
    # go until error < 1e-3
    error = float("inf")
    sign = 1.0
    while error > 1e-3:

        # fit surrogate data
        surrogate.fit(data=data)

        # find minimum/maximum of surrogate
        results = diffev2(lambda x: sign * surrogate(x), bounds, npop=20,
                        bounds=bounds, gtol=500, full_output=True)

        # get minimum/maximum of actual expensive model
        xnew = results[0].tolist()
        ynew = truth(xnew)

        # compute error which is actual model value - surrogate model value
        ysur = results[1]
        error = abs(ynew - ysur)

        # print statements
        print("truth", xnew, ynew)
        print("surrogate", xnew, ysur)
        print("error", ynew - ysur, error)
        print("data", len(data))

        # add latest evaulated point with actual expensive model to be used by surrogate in fitting
        pt = datapoint(xnew, value=ynew)
        data.append(pt)

    # print the best parameters
    print(f"The best solution is {xnew} with Rwp {ynew}")
    print(f"The reference solutions is {target}")
    ratios = [x / y for x, y in zip(target, xnew)]
    print(f"The ratios of to the reference values are {ratios}")

    #===============
    # Using a LatticeSolver approach
    #===============

    # set the ranges
    target = [2.9306538, 4.6817646, 3.6026807, 3.233392]
    lower_bounds = [x * 0.95 for x in target]
    upper_bounds = [x * 1.05 for x in target]

    # set random seed so we can reproduce results
    tools.random_seed(0)

    # create a solver
    solver = LatticeSolver(4, 8)

    # set multi-processing pool
    solver.SetMapper(Pool().map)

    # since we have an search solver
    # we specify what optimization algorithm to use within the search
    # we tell the optimizer to not go more than 50 evaluations of our cost function
    subsolver = NelderMeadSimplexSolver(4)
    subsolver.SetEvaluationLimits(50, 50)
    solver.SetNestedSolver(subsolver)

    # set the range to search for all parameters
    solver.SetStrictRanges(lower_bounds, upper_bounds)

    # find the minimum
    solver.Solve(CostFunction(4), VTR())

    # print the best parameters
    print(f"The best solution is {solver.bestSolution} with Rwp {solver.bestEnergy}")
    print(f"The reference solutions is {target}")
    ratios = [x / y for x, y in zip(target, solver.bestSolution)]
    print(f"The ratios of to the reference values are {ratios}")
