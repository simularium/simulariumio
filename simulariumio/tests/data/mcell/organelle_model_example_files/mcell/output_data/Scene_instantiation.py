# WARNING: This is an automatically generated file and will be overwritten
#          by CellBlender on the next model export.

import os
import shared
import mcell as m

from Scene_parameters import *
from Scene_subsystem import *
from Scene_geometry import *
MODEL_PATH = os.path.dirname(os.path.abspath(__file__))


# ---- instantiation ----

# ---- release sites ----

# ---- surface classes assignment ----

# ---- compartments assignment ----

rel_a = m.ReleaseSite(
    name = 'rel_a',
    complex = m.Complex('a'),
    region = Cell - (Organelle_1 + Organelle_2),
    number_to_release = 2
)

rel_b = m.ReleaseSite(
    name = 'rel_b',
    complex = m.Complex('b'),
    region = Organelle_1,
    number_to_release = 0
)

rel_t1 = m.ReleaseSite(
    name = 'rel_t1',
    complex = m.Complex('t1', orientation = m.Orientation.UP),
    region = Organelle_1_top,
    number_to_release = 0
)

rel_t2 = m.ReleaseSite(
    name = 'rel_t2',
    complex = m.Complex('t2', orientation = m.Orientation.UP),
    region = Organelle_2_top,
    number_to_release = 0
)

# ---- create instantiation object and add components ----

instantiation = m.Instantiation()
instantiation.add_geometry_object(Cell)
instantiation.add_geometry_object(Organelle_2)
instantiation.add_geometry_object(Organelle_1)
instantiation.add_release_site(rel_a)
instantiation.add_release_site(rel_b)
instantiation.add_release_site(rel_t1)
instantiation.add_release_site(rel_t2)

# load seed species information from bngl file
instantiation.load_bngl_seed_species(os.path.join(MODEL_PATH, 'Scene_model.bngl'), None, shared.parameter_overrides)

