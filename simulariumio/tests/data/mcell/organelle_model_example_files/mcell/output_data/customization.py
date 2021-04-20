# This file contains hooks to override default MCell4 model
# code behavior for models generated from CellBlender
import shared
import mcell as m

"""
def custom_argparse_and_parameters():
    # When uncommented, this function is called to parse 
    # custom commandline arguments.
    # It is executed before any of the automatically generated 
    # parameter values are set so one can override the parameter 
    # values here as well.
    # To override parameter values, add or overwrite an item in dictionary
    # shared.parameter_overrides, e.g. shared.parameter_overrides['SEED'] = 10
    pass
"""

"""
def custom_config(model):
    # When uncommented, this function is called to set custom
    # model configuration.
    # It is executed after basic parameter setup is done and 
    # before any components are added to the model. 
    pass
"""

"""
def custom_init_and_run(model):
    # When uncommented, this function is called after all the model
    # components defined in CellBlender were added to the model.
    # It allows to add additional model components before initialization 
    # is done and then to customize how simulation is ran.
    model.initialize()
    model.run_iterations(parameters.ITERATIONS)
    model.end_simulation()
"""

