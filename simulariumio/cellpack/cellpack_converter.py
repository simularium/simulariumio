#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import os
import numpy as np
import json
from scipy.spatial.transform import Rotation as R
from typing import Callable, Tuple

from cellpack import RecipeLoader
from ..constants import DISPLAY_TYPE, VIZ_TYPE, VALUES_PER_3D_POINT
from ..data_objects.camera_data import CameraData
from ..trajectory_converter import TrajectoryConverter
from ..data_objects import TrajectoryData, AgentData, DimensionData
from ..data_objects import MetaData, DisplayData
from ..exceptions import InputDataError
from .cellpack_data import HAND_TYPE, CellpackData

###############################################################################

log = logging.getLogger(__name__)

###############################################################################


DEFAULT_CELLPACK_URL = (
    "https://raw.githubusercontent.com/mesoscope/cellPACK_data"
    "/master/cellPACK_database_1.1.0/"
)

# NOTE: Default scale is 0.1, so the actual default r will be 1.0
DEFAULT_RADIUS = 10


class CellpackConverter(TrajectoryConverter):
    def __init__(
        self,
        input_data: CellpackData,
        progress_callback: Callable[[float], None] = None,
        callback_interval: float = 10,
    ):
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
        progress_callback : Callable[[float], None] (optional)
            Callback function that accepts 1 float argument and returns None
            which will be called at a given progress interval, determined by
            callback_interval requested, providing the current percent progress
            Default: None
        callback_interval : float (optional)
            If a progress_callback was provided, the period between updates
            to be sent to the callback, in seconds
            Default: 10
        """
        super().__init__(input_data, progress_callback, callback_interval)
        self._data = self._read(input_data)

    @staticmethod
    def _get_box_center(recipe_data):
        options = recipe_data["options"]
        bb = options["boundingBox"]
        x_pos = (bb[1][0] - bb[0][0]) / 2.0 + bb[0][0]
        y_pos = (bb[1][1] - bb[0][1]) / 2.0 + bb[0][1]
        z_pos = (bb[1][2] - bb[0][2]) / 2.0 + bb[0][2]
        return [
            x_pos,
            y_pos,
            z_pos,
        ]

    @staticmethod
    def _get_boxsize(recipe_data):
        options = recipe_data["options"]
        bb = options["boundingBox"]
        x_size = bb[1][0] - bb[0][0]
        y_size = bb[1][1] - bb[0][1]
        z_size = bb[1][2] - bb[0][2]
        return [
            x_size,
            y_size,
            z_size,
        ]

    @staticmethod
    def _get_euler_from_matrix(data_in, handedness):
        rotation_matrix = [
            data_in[0][0:VALUES_PER_3D_POINT],
            data_in[1][0:VALUES_PER_3D_POINT],
            data_in[2][0:VALUES_PER_3D_POINT],
        ]
        if handedness == HAND_TYPE.LEFT:
            euler = R.from_matrix(rotation_matrix).as_euler("ZYX", degrees=False)
            return [euler[0], euler[1], -euler[2]]
        else:
            return R.from_matrix(rotation_matrix).as_euler("XYZ", degrees=False)

    @staticmethod
    def _get_euler_from_quat(data_in, handedness):
        if handedness == HAND_TYPE.LEFT:
            euler = R.from_quat(data_in).as_euler("ZYX", degrees=False)
            return [euler[0], euler[1], -euler[2]]
        else:
            return R.from_quat(data_in).as_euler("XYZ", degrees=False)

    @staticmethod
    def _is_matrix(data_in):
        if isinstance(data_in[0], list):
            return True
        else:
            return False

    @staticmethod
    def _get_euler(data_in, handedness) -> np.array:
        if CellpackConverter._is_matrix(data_in):
            return CellpackConverter._get_euler_from_matrix(data_in, handedness)
        else:
            return CellpackConverter._get_euler_from_quat(data_in, handedness)

    @staticmethod
    def _unpack_curve(
        data,
        time_step_index: int,
        ingredient_name: str,
        index: int,
        agent_id: int,
        result: AgentData,
        box_center: np.array,
    ):
        curve = "curve" + str(index)
        result.positions[time_step_index][agent_id] = [0, 0, 0]
        result.rotations[time_step_index][agent_id] = [0, 0, 0]
        result.viz_types[time_step_index][agent_id] = VIZ_TYPE.FIBER
        result.n_agents[time_step_index] += 1
        result.types[time_step_index].append(ingredient_name)
        result.unique_ids[time_step_index][agent_id] = agent_id
        r = (
            data["encapsulatingRadius"]
            if ("encapsulatingRadius" in data)
            else DEFAULT_RADIUS
        )
        result.radii[time_step_index][agent_id] = r
        subpoints = (np.array(data[curve]) - np.array(box_center)).flatten()
        result.n_subpoints[time_step_index][agent_id] = len(subpoints)
        for i in range(len(subpoints)):
            result.subpoints[time_step_index][agent_id][i] = subpoints[i]

    @staticmethod
    def _unpack_positions(
        data,
        time_step_index: int,
        ingredient_name: str,
        index: int,
        agent_id,
        result: AgentData,
        box_center: np.array,
        handedness: HAND_TYPE,
        comp_id=0,
    ):
        position = data["results"][index][0]
        offset = np.array([0, 0, 0])
        # TODO: use comp id to compute the offset for surface agents
        if comp_id <= 0:
            offset = offset * -1
        result.positions[time_step_index][agent_id] = [
            (position[0] + offset[0] - box_center[0]),
            (position[1] + offset[1] - box_center[1]),
            (position[2] + offset[2] - box_center[2]),
        ]
        rotation = CellpackConverter._get_euler(data["results"][index][1], handedness)
        result.rotations[time_step_index][agent_id] = rotation
        result.viz_types[time_step_index][agent_id] = VIZ_TYPE.DEFAULT
        result.n_agents[time_step_index] += 1
        result.types[time_step_index].append(ingredient_name)
        result.unique_ids[time_step_index][agent_id] = agent_id
        if "radii" in data:
            result.radii[time_step_index][agent_id] = data["radii"][0]["radii"][0]

        elif "encapsulatingRadius" in data:
            result.radii[time_step_index][agent_id] = data["encapsulatingRadius"]

        else:
            result.radii[time_step_index][agent_id] = DEFAULT_RADIUS
        result.n_subpoints[time_step_index][agent_id] = 0

    @staticmethod
    def _parse_dimensions(all_ingredients, total_steps=1) -> DimensionData:
        """
        Parse cellPack results file to get the total number of agents and
        the max curve length
        """
        result = DimensionData(0, 0)
        for ingredient in all_ingredients:
            ingredient_results_data = ingredient["results"]
            result.max_agents += len(ingredient_results_data["results"])
            if "nbCurve" in ingredient_results_data:
                result.max_agents += ingredient_results_data["nbCurve"]

                for i in range(ingredient_results_data["nbCurve"]):
                    curve = "curve" + str(i)
                    if (
                        len(ingredient_results_data[curve]) * VALUES_PER_3D_POINT
                        > result.max_subpoints
                    ):
                        result.max_subpoints = (
                            len(ingredient_results_data[curve]) * VALUES_PER_3D_POINT
                        )
        result.total_steps = total_steps
        return result

    @staticmethod
    def _get_ingredient_display_data(geo_type, ingredient_data, geometry_url):
        color = ""
        display_type = DISPLAY_TYPE.SPHERE
        url = ""

        if "color" in ingredient_data:
            color = "#%02x%02x%02x" % tuple(
                [int(x * 255) for x in ingredient_data["color"]]
            )

        if geo_type == DISPLAY_TYPE.OBJ and "meshFile" in ingredient_data:
            meshType = (
                ingredient_data["meshType"]
                if ("meshType" in ingredient_data)
                else "file"
            )
            if meshType == "file":
                file_path = os.path.basename(ingredient_data["meshFile"])
                file_name, _ = os.path.splitext(file_path)
                if geometry_url is None:
                    url = f"{DEFAULT_CELLPACK_URL}geometries/"
                else:
                    url = f"{geometry_url}{file_name}.obj"  # noqa: E501
                display_type = DISPLAY_TYPE.OBJ

            elif meshType == "raw":
                # need to build a mesh from the vertices, faces, indexes dictionary
                log.info(meshType, ingredient_data["meshFile"].keys())
        elif geo_type == DISPLAY_TYPE.PDB:
            pdb_file_name = ""
            if "source" in ingredient_data:
                pdb_file_name = ingredient_data["source"]["pdb"]
            elif "pdb" in ingredient_data:
                pdb_file_name = ingredient_data["pdb"]
            if ".pdb" in pdb_file_name:
                url = f"{DEFAULT_CELLPACK_URL}other/{pdb_file_name}"
            else:
                url = pdb_file_name

            display_type = DISPLAY_TYPE.PDB
            url = url

        else:
            display_type = (
                DISPLAY_TYPE.FIBER
                if ingredient_data["Type"] == "Grow"
                else DISPLAY_TYPE.SPHERE
            )
            url = ""
        return {"display_type": display_type, "color": color, "url": url}

    def _process_ingredients(
        self,
        all_ingredients,
        time_step_index: int,
        box_center: np.array,
        geo_type: DISPLAY_TYPE,
        handedness: HAND_TYPE,
        geometry_url: str,
        display_data,
        scale_factor: float = None,
    ) -> Tuple[AgentData, float]:
        dimensions = CellpackConverter._parse_dimensions(all_ingredients)
        spatial_data = AgentData.from_dimensions(dimensions)
        display_data = {} if display_data is None else display_data
        agent_id_counter = 0
        total_agents = 0
        for ingredient in all_ingredients:
            total_agents += len(ingredient["results"].get("results", []))
            total_agents += ingredient["results"].get("nbCurve", 0)

        for ingredient in all_ingredients:
            ingredient_data = ingredient["recipe_data"]
            ingredient_key = ingredient_data["name"]
            ingredient_results_data = ingredient["results"]
            agent_display_data = TrajectoryConverter._get_display_data_for_agent(
                ingredient_key, display_data
            )
            if agent_display_data is None:
                agent_display_data = CellpackConverter._get_ingredient_display_data(
                    geo_type, ingredient_data, geometry_url
                )
                display_data[ingredient_key] = DisplayData(
                    name=ingredient_key,
                    display_type=agent_display_data["display_type"],
                    url=agent_display_data["url"],
                    color=agent_display_data["color"],
                )
            else:
                new_name = agent_display_data.name
                display_data[new_name] = agent_display_data
                ingredient_key = new_name
            if "coordsystem" in ingredient_data:
                handedness = (
                    HAND_TYPE.LEFT
                    if ingredient_data["coordsystem"] == "left"
                    else HAND_TYPE.RIGHT
                )
            if len(ingredient_results_data["results"]) > 0:
                for j in range(len(ingredient_results_data["results"])):
                    CellpackConverter._unpack_positions(
                        ingredient_results_data,
                        time_step_index,
                        ingredient_key,
                        j,
                        agent_id_counter,
                        spatial_data,
                        box_center,
                        handedness,
                    )
                    agent_id_counter += 1
                    self.check_report_progress(agent_id_counter / total_agents)
            elif ingredient_results_data["nbCurve"] > 0:
                for i in range(ingredient_results_data["nbCurve"]):
                    CellpackConverter._unpack_curve(
                        ingredient_results_data,
                        time_step_index,
                        ingredient_key,
                        i,
                        agent_id_counter,
                        spatial_data,
                        box_center,
                    )
                    agent_id_counter += 1
                    self.check_report_progress(agent_id_counter / total_agents)

        spatial_data.display_data = display_data
        return TrajectoryConverter.scale_agent_data(spatial_data, scale_factor)

    @staticmethod
    def _update_meta_data(meta_data: MetaData, box_size: np.array) -> MetaData:
        camera_z_position = box_size[2] if box_size[2] > 10 else 100.0
        meta_data.camera_defaults = CameraData(
            position=np.array([10.0, 0.0, camera_z_position]),
            look_at_position=np.array([10.0, 0.0, 0.0]),
        )

    def _read(self, input_data: CellpackData) -> TrajectoryData:
        """
        Return a TrajectoryData object containing the Cellpack data
        """
        print("Reading Cellpack Data -------------")
        # currently only converts one model, ie one time step
        time_step_index = 0
        # default scale for cellpack => simularium
        # user is supposed to send in the cellPACK scale factor
        # if they send one in at all.
        if input_data.meta_data.scale_factor is not None:
            input_data.meta_data.scale_factor *= 0.1

        try:
            # load the data from Cellpack output JSON file
            recipe_loader = RecipeLoader(input_data.recipe_file_path)
            recipe_data = recipe_loader.recipe_data
            results_data = json.loads(input_data.results_file.get_contents())
            all_ingredients = recipe_loader.get_all_ingredients(results_data)
        except Exception as e:
            raise InputDataError(f"Error reading cellpack input file: {e}")

        box_center = CellpackConverter._get_box_center(recipe_data)
        agent_data, scale_factor = self._process_ingredients(
            all_ingredients,
            time_step_index,
            box_center,
            input_data.geometry_type,
            input_data.handedness,
            input_data.geometry_url,
            input_data.display_data,
            input_data.meta_data.scale_factor,
        )
        # parse
        box_size = np.array(CellpackConverter._get_boxsize(recipe_data))
        input_data.meta_data.scale_factor = scale_factor
        input_data.meta_data._set_box_size(box_size)
        # set camera position based on bounding box
        CellpackConverter._update_meta_data(input_data.meta_data, box_size)
        # create TrajectoryData
        input_data.spatial_units.multiply(1.0 / scale_factor)
        return TrajectoryData(
            meta_data=input_data.meta_data,
            agent_data=agent_data,
            time_units=input_data.time_units,
            spatial_units=input_data.spatial_units,
            plots=input_data.plots,
        )
