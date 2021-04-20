# WARNING: This is an automatically generated file and will be overwritten
#          by CellBlender on the next model export.

import sys
import os
import math
import shared
import mcell as m

MODEL_PATH = os.path.dirname(os.path.abspath(__file__))

# ---- model parameters ----

# declare all items from parameter_overrides as variables
for parameter_name, value in shared.parameter_overrides.items():
    setattr(sys.modules[__name__], parameter_name, value)

# auxiliary function used to determine whether a parameter was defined
def not_defined(parameter_name):
    return parameter_name not in globals()

# load parameters from BNGL
bngl_params = m.bngl_utils.load_bngl_parameters(os.path.join(MODEL_PATH, 'Scene_model.bngl'), shared.parameter_overrides)


# ---- simulation setup ----

if not_defined('ITERATIONS'):
    ITERATIONS = 2

if not_defined('TIME_STEP'):
    TIME_STEP = 1e-6

if not_defined('DUMP'):
    DUMP = False

if not_defined('EXPORT_DATA_MODEL'):
    EXPORT_DATA_MODEL = True

if not_defined('SEED'):
    SEED = 1


