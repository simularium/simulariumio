#!/usr/bin/env python3

# WARNING: This is an automatically generated file and will be overwritten
#          by CellBlender on the next model export.

import sys
import os
import importlib.util

MODEL_PATH = os.path.dirname(os.path.abspath(__file__))


# ---- import mcell module located in directory specified by system variable MCELL_PATH  ----

MCELL_PATH = os.environ.get('MCELL_PATH', '')
if MCELL_PATH:
    lib_path = os.path.join(MCELL_PATH, 'lib')
    if os.path.exists(os.path.join(lib_path, 'mcell.so')) or \
        os.path.exists(os.path.join(lib_path, 'mcell.pyd')):
        sys.path.append(lib_path)
    else:
        print("Error: Python module mcell.so or mcell.pyd was not found in "
              "directory '" + lib_path + "' constructed from system variable "
              "MCELL_PATH.")
        sys.exit(1)
else:
    print("Error: system variable MCELL_PATH that is used to find the mcell "
          "library was not set.")
    sys.exit(1)

import mcell as m


# ---- customization and argument processing ----

# this module is used to hold any overrides of parameter values
import shared
# import the customization.py module if it exists
if os.path.exists(os.path.join(MODEL_PATH, 'customization.py')):
    import customization
else:
    customization = None

# process command-line arguments
if customization and 'custom_argparse_and_parameters' in dir(customization):
    # custom argument processing and parameter setup
    customization.custom_argparse_and_parameters()
else:
    if len(sys.argv) == 1:
        # no arguments
        pass
    elif len(sys.argv) == 3 and sys.argv[1] == '-seed':
        # overwrite value of seed defined in module parameters
        shared.parameter_overrides['SEED'] = int(sys.argv[2])
    else:
        print("Error: invalid command line arguments")
        print("  usage: " + sys.argv[0] + "[-seed N]")
        sys.exit(1)


# the module parameters uses shared.parameter_overrides to override parameter values
from Scene_parameters import *


# resume simulation if a checkpoint was created
checkpoint_dir = m.run_utils.get_last_checkpoint_dir(SEED)
if checkpoint_dir:
    # change sys.path so that the only the checkpointed files are loaded
    sys.path = m.run_utils.remove_cwd(sys.path)
    sys.path.append(checkpoint_dir)
    
    # prepare import of the 'model' module from the checkpoint
    model_spec = importlib.util.spec_from_file_location(
        'model', os.path.join(checkpoint_dir, 'model.py'))
    model_module = importlib.util.module_from_spec(model_spec)
    
    # run import, this also resumes simulation from the checkpoint
    model_spec.loader.exec_module(model_module)

    # exit after simulation has finished successfully
    sys.exit(0)


# ---- model creation and simulation ----

# create main model object
model = m.Model()

# ---- configuration ----

model.config.time_step = TIME_STEP
model.config.seed = SEED
model.config.total_iterations = ITERATIONS

model.notifications.rxn_and_species_report = True

model.config.partition_dimension = 1.25
model.config.subpartition_dimension = 0.02

# ---- default configuration overrides ----

if customization and 'custom_config' in dir(customization):
    # user-defined model configuration
    customization.custom_config(model)

# ---- add components ----

import Scene_subsystem
import Scene_instantiation
import Scene_observables

model.add_subsystem(Scene_subsystem.subsystem)
model.add_instantiation(Scene_instantiation.instantiation)
model.add_observables(Scene_observables.observables)

# ---- initialization and execution ----

if customization and 'custom_init_and_run' in dir(customization):
    customization.custom_init_and_run(model)
else:
    model.initialize()

    if DUMP:
        model.dump_internal_state()

    if EXPORT_DATA_MODEL and model.viz_outputs:
        model.export_data_model()

    model.run_iterations(ITERATIONS)
    model.end_simulation()
