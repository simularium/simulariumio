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
        # get BioPython PDB structure
        builder = StructureBuilder()
        # TODO build structure with a model for each timestep
        
        # save CIF file (TODO: binary version)
        io = MMCIFIO()
        io.set_structure(s)
        io.save(f"{output_path}.cif")
