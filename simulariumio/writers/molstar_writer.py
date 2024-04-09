#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from typing import Any, Dict, List

import numpy as np
from Bio.PDB import MMCIFIO
from Bio.PDB.StructureBuilder import StructureBuilder

from ..data_objects import (
    AgentData,
    TrajectoryData,
)
from ..constants import V1_SPATIAL_BUFFER_STRUCT, CURRENT_VERSION, VALUES_PER_3D_POINT
from .writer import Writer

###############################################################################

log = logging.getLogger(__name__)

###############################################################################


class MolstarWriter(Writer):
    @staticmethod
    def save(
        trajectory_data: TrajectoryData, output_path: str,
    ) -> None:
        """
        Save the simularium data in MolStar (https://molstar.org/) 
        output formats at the output path.
        
        TODO: Save in mmCIF format with a model for each timestep.
        
        Parameters
        ----------
        trajectory_data: TrajectoryData
            the data to save
        output_path: str
            where to save the file
        """
        # build BioPython PDB structure
        scale = 1.
        builder = StructureBuilder()
        builder.init_structure(f"simularium_{trajectory_data.meta_data.trajectory_title}")
        for time_ix in range(trajectory_data.agent_data.times.shape[0]):
            builder.init_model(time_ix)
            builder.init_seg("0")
            builder.init_chain("0")
            n_agents = int(trajectory_data.agent_data.n_agents[time_ix])
            for agent_ix in range(n_agents):
                if trajectory_data.agent_data.n_subpoints[time_ix][agent_ix] > 0:
                    continue
                builder.init_residue(
                    resname="R", 
                    field="_", 
                    resseq=agent_ix, 
                    icode="_",
                )
                builder.init_atom(
                    "H",
                    scale * trajectory_data.agent_data.positions[time_ix][agent_ix],
                    b_factor=0.0,
                    occupancy=0.0,
                    altloc="_",
                    fullname="Hydrogen",
                    element="H",
                )
        # save CIF file (TODO: binary version)
        io = MMCIFIO()
        io.set_structure(builder.get_structure())
        io.save(f"{output_path}.cif")
