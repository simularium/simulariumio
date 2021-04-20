# WARNING: This is an automatically generated file and will be overwritten
#          by CellBlender on the next model export.

import os
import shared
import mcell as m

from Scene_parameters import *
from Scene_subsystem import *
from Scene_geometry import *
MODEL_PATH = os.path.dirname(os.path.abspath(__file__))


# ---- observables ----

viz_output = m.VizOutput(
    mode = m.VizMode.CELLBLENDER,
    output_files_prefix = './viz_data/seed_' + str(SEED).zfill(5) + '/Scene',
    every_n_timesteps = 1
)

# ---- declaration of rxn rules defined in BNGL and used in counts ----

# ---- create observables object and add components ----

observables = m.Observables()
observables.add_viz_output(viz_output)

# load observables information from bngl file
observables.load_bngl_observables(os.path.join(MODEL_PATH, 'Scene_model.bngl'), './react_data/seed_' + str(SEED).zfill(5) + '/', shared.parameter_overrides)
