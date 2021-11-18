#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from typing import List

import numpy as np
from wheel import metadata

from ..trajectory_converter import TrajectoryConverter
from ..data_objects import TrajectoryData, AgentData, DimensionData
from .cellpack_data import CellpackData
from cellpack.autopack.iotools_simple import RecipeLoader

###############################################################################

log = logging.getLogger(__name__)

###############################################################################


class CellpackConverter(TrajectoryConverter):
    def __init__(self, input_data: CellpackData):
        """
        This object reads packing results outputs
        from Cellpack (http://www.cellpack.org)
        and plot data and writes them in the JSON format used
        by the Simularium viewer

        Parameters
        ----------
        input_data : CellpackData
            An object containing info for reading
            Cellpack simulation trajectory outputs and plot data
        """
        self._data = self._read(input_data)

    @staticmethod
    def _get_bounding_box(self, recipe_data):
        options = recipe_data["options"]
        bb = options["boundingBox"]
        x_size = bb[1][0] - bb[0][0]
        y_size = bb[1][1] - bb[0][1]
        z_size = bb[1][2] - bb[0][2]
        return [
            x_size * self.scale_factor,
            y_size * self.scale_factor,
            z_size * self.scale_factor,
    ]

    def _loop_through_compartment(self, results_data_in, time_step_index, recipe_data):
        if "cytoplasme" in results_data_in:
            if len(results_data_in["cytoplasme"]["ingredients"]) != 0:
                self.loop_through_ingredients(
                    results_data_in["cytoplasme"]["ingredients"],
                    recipe_data["cytoplasme"]["ingredients"],
                    time_step_index,
                )
        if "compartments" in results_data_in:
            for compartment in results_data_in["compartments"]:
                current_compartment = results_data_in["compartments"][compartment]
                if "surface" in current_compartment:
                    self.loop_through_ingredients(
                        current_compartment["surface"]["ingredients"],
                        recipe_data["compartments"][compartment]["surface"][
                            "ingredients"
                        ],
                        time_step_index,
                    )
                if "interior" in current_compartment:
                    self.loop_through_ingredients(
                        current_compartment["interior"]["ingredients"],
                        recipe_data["compartments"][compartment]["interior"][
                            "ingredients"
                        ],
                        time_step_index,
                    )

    @staticmethod
    def _read(input_data: CellpackData) -> TrajectoryData:
        """
        Return a TrajectoryData object containing the Cellpack data
        """
        print("Reading Cellpack Data -------------")
        # load the data from Cellpack output .txt file
        recipe_data = RecipeLoader(input_data.recipe_file_path).read()
        results_data = input_data.results_file.get_contents()

        # parse
        box_size = CellpackConverter._get_bounding_box(recipe_data)
        input_data.meta_data._set_box_size(box_size)
        input_data.metadata.scale_factor *= 0.1

        metadata = make_my_meta(input_data.meta_data) # camera pos
        agent_data = make_agent_data

        display_data = make_display_data(input_data.display_data)
        # # create TrajectoryData
        input_data.spatial_units.multiply(1.0 / input_data.metadata.scale_factor)
        return TrajectoryData(
            meta_data=input_data.meta_data,
            agent_data=agent_data,
            time_units=input_data.time_units,
            spatial_units=input_data.spatial_units,
            plots=input_data.plots,
        )
