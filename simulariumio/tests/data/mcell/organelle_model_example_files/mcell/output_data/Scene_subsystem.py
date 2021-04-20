# WARNING: This is an automatically generated file and will be overwritten
#          by CellBlender on the next model export.

import os
import shared
import mcell as m

from Scene_parameters import *

# ---- subsystem ----

MODEL_PATH = os.path.dirname(os.path.abspath(__file__))

unnamed_reaction_rule_1 = m.ReactionRule(
    name = 'unnamed_reaction_rule_1',
    reactants = [ m.Complex('a', orientation = m.Orientation.UP), m.Complex('t1', orientation = m.Orientation.UP) ],
    products = [ m.Complex('a', orientation = m.Orientation.DOWN), m.Complex('t1', orientation = m.Orientation.UP) ],
    fwd_rate = 3e8
)

unnamed_reaction_rule_2 = m.ReactionRule(
    name = 'unnamed_reaction_rule_2',
    reactants = [ m.Complex('c', orientation = m.Orientation.UP), m.Complex('t2', orientation = m.Orientation.UP) ],
    products = [ m.Complex('d', orientation = m.Orientation.DOWN), m.Complex('t2', orientation = m.Orientation.UP) ],
    fwd_rate = 3e9
)

unnamed_reaction_rule_3 = m.ReactionRule(
    name = 'unnamed_reaction_rule_3',
    reactants = [ m.Complex('c', orientation = m.Orientation.DOWN), m.Complex('t1', orientation = m.Orientation.UP) ],
    products = [ m.Complex('c', orientation = m.Orientation.UP), m.Complex('t1', orientation = m.Orientation.UP) ],
    fwd_rate = 3e8
)

# ---- create subsystem object and add components ----

subsystem = m.Subsystem()
subsystem.add_reaction_rule(unnamed_reaction_rule_1)
subsystem.add_reaction_rule(unnamed_reaction_rule_2)
subsystem.add_reaction_rule(unnamed_reaction_rule_3)

# load subsystem information from bngl file
subsystem.load_bngl_molecule_types_and_reaction_rules(os.path.join(MODEL_PATH, 'Scene_model.bngl'), shared.parameter_overrides)

# set additional information about species and molecule types that cannot be stored in BNGL,
# elementary molecule types are already in the subsystem after they were loaded from BNGL
def set_bngl_molecule_types_info(subsystem):
    a = subsystem.find_elementary_molecule_type('a')
    assert a, "Elementary molecule type 'a' was not found"
    a.diffusion_constant_3d = 1e-6

    b = subsystem.find_elementary_molecule_type('b')
    assert b, "Elementary molecule type 'b' was not found"
    b.diffusion_constant_3d = 1e-6

    c = subsystem.find_elementary_molecule_type('c')
    assert c, "Elementary molecule type 'c' was not found"
    c.diffusion_constant_3d = 1e-6

    d = subsystem.find_elementary_molecule_type('d')
    assert d, "Elementary molecule type 'd' was not found"
    d.diffusion_constant_3d = 1e-6

    t1 = subsystem.find_elementary_molecule_type('t1')
    assert t1, "Elementary molecule type 't1' was not found"
    t1.diffusion_constant_2d = 1e-7

    t2 = subsystem.find_elementary_molecule_type('t2')
    assert t2, "Elementary molecule type 't2' was not found"
    t2.diffusion_constant_2d = 1e-8

set_bngl_molecule_types_info(subsystem)
