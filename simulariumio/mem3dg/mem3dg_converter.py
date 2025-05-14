from netCDF4 import Dataset
import numpy as np
from pathlib import Path

from ..trajectory_converter import TrajectoryConverter
from ..data_objects import (
    AgentData,
    TrajectoryData,
    DimensionData,
    DisplayData,
)
from ..constants import DISPLAY_TYPE
from ..exceptions import InputDataError
from .mem3dg_data import Mem3dgData


class Mem3dgConverter(TrajectoryConverter):
    def __init__(
        self,
        input_data: Mem3dgData,
    ):
        """
        Parameters
        ----------
        input_data : Mem3dgData
            An object containing info for reading
            Mem3DG simulation trajectory output
        """
        self._data = self._read(input_data)

    def write_to_obj(self, filepath, data, frame):
        # Extract XYZ coordinates for vertices
        coordinates = np.array(
            data.groups["Trajectory"].variables["coordinates"][frame]
        )
        coordinates = np.reshape(coordinates, (-1, 3))

        # Extract indices of vertices to make faces (all triangles)
        topology = np.array(data.groups["Trajectory"].variables["topology"][frame])
        topology = np.reshape(topology, (-1, 3))
        # change indices to be 1 indexed instead of 0 indexed for .obj files
        topology += 1

        # Generate one .obj file per frame
        with open(filepath, "w") as file:
            file.write(f"# Frame {frame}\n")
            for v in coordinates:
                file.write(f"v {v[0]} {v[1]} {v[2]}\n")
            for t in topology:
                file.write(f"f {t[0]} {t[1]} {t[2]}\n")

    def _read_traj_data(self, input_data: Mem3dgData) -> AgentData:
        try:
            data = Dataset(input_data.input_file_path, "r")
            n_frames = np.size(data.groups["Trajectory"].variables["time"])
        except Exception as e:
            raise InputDataError(f"Error reading input Mem3DG data: {e}")

        # for now, we are representing converted Mem3DG trajectories as one
        # unique mesh agent per frame
        dimensions = DimensionData(total_steps=n_frames, max_agents=1)
        agent_data = AgentData.from_dimensions(dimensions)
        agent_data.n_timesteps = n_frames

        base_agent_name = input_data.agent_name or "object"
        for frame in range(n_frames):
            agent_data.times[frame] = data.groups["Trajectory"].variables["time"][frame]
            agent_data.n_agents[frame] = 1

            output_file_path = Path(input_data.output_obj_file_path) / f"{frame}.obj"
            self.write_to_obj(output_file_path, data, frame)

            agent_data.radii[frame][0] = input_data.meta_data.scale_factor
            agent_data.unique_ids[frame][0] = frame

            name = str(frame)
            agent_data.types[frame].append(name)
            object_display_data = DisplayData(
                name=f"{base_agent_name}#frame{frame}",
                display_type=DISPLAY_TYPE.OBJ,
                url=f"{frame}.obj",
                color=input_data.agent_color,
            )
            agent_data.display_data[name] = object_display_data
        return agent_data

    def _read(self, input_data: Mem3dgData) -> TrajectoryData:
        """
        Return a TrajectoryData object containing the Mem3DG data
        """
        print("Reading Mem3DG Data -------------")
        if input_data.meta_data.scale_factor is None:
            input_data.meta_data.scale_factor = 1.0
        agent_data = self._read_traj_data(input_data)
        input_data.spatial_units.multiply(1.0 / input_data.meta_data.scale_factor)
        input_data.meta_data._set_box_size()
        result = TrajectoryData(
            meta_data=input_data.meta_data,
            agent_data=agent_data,
            time_units=input_data.time_units,
            spatial_units=input_data.spatial_units,
            plots=input_data.plots,
        )
        return result
