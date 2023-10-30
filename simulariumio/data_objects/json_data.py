from typing import Dict, List
import json
import numpy as np

from .frame_data import FrameData
from .simularium_file_data import SimulariumFileData
from .trajectory_data import TrajectoryData
from ..constants import V1_SPATIAL_BUFFER_STRUCT


class JsonData(SimulariumFileData):
    def __init__(self, file_contents: str):
        """
        This object holds JSON encoded simulation trajectory file's
        data while staying close to the original file format

        Parameters
        ----------
        file_contents : str
            A string of the data of an open .simularium file
        """
        self.data = json.loads(file_contents)
        self.n_agents = JsonData._get_n_agents(self.data)

    def _get_n_agents(data: Dict) -> List[int]:
        # return number of agents in each timestamp as a list
        n_agents = []
        bundle_data = data["spatialData"]["bundleData"]
        for time_index in range(data["trajectoryInfo"]["totalSteps"]):
            frame_data = bundle_data[time_index]["data"]
            agent_index = 0
            buffer_index = 0
            while buffer_index + V1_SPATIAL_BUFFER_STRUCT.NSP_INDEX < len(frame_data):
                n_subpoints = int(
                    frame_data[buffer_index + V1_SPATIAL_BUFFER_STRUCT.NSP_INDEX]
                )
                # length of one agents spatial data = SP_INDEX + n_subpoints
                buffer_index += n_subpoints + V1_SPATIAL_BUFFER_STRUCT.SP_INDEX
                agent_index += 1
            n_agents.append(agent_index)
        return n_agents

    def get_frame_at_index(self, frame_number: int) -> FrameData:
        """
        Return frame data for frame at index. If there is no frame at the index,
        return None.
        """
        if frame_number < 0 or frame_number >= len(
            self.data["spatialData"]["bundleData"]
        ):
            # invalid frame number requested
            return None

        frame_data = self.data["spatialData"]["bundleData"][frame_number]
        return FrameData(
            frame_number=frame_number,
            n_agents=self.n_agents[frame_number],
            time=frame_data["time"],
            data=frame_data["data"],
        )

    def get_index_for_time(self, time: float) -> int:
        """
        Return index for frame closest to a given timestamp
        """
        closest_frame = -1
        min_dist = np.inf
        for frame in self.data["spatialData"]["bundleData"]:
            dist = abs(frame["time"] - time)
            if dist < min_dist:
                min_dist = dist
                closest_frame = frame["frameNumber"]
            else:
                # if dist is increasing, we've passed the closest frame
                break

        # frame index must be <= self.get_num_frames() - 1
        return min(closest_frame, self.get_num_frames() - 1)

    def get_trajectory_info(self) -> Dict:
        """
        Return trajectory info block for trajectory, as dict
        """
        return self.data["trajectoryInfo"]

    def get_plot_data(self) -> Dict:
        """
        Return plot data block for trajectory, as dict
        """
        return self.data["plotData"]

    def get_trajectory_data_object(self) -> TrajectoryData:
        """
        Return the data of the trajectory, as a TrajectoryData object
        """
        return TrajectoryData.from_buffer_data(self.data)

    def get_file_contents(self) -> Dict:
        """
        Return raw file data, as a dict
        """
        return self.data

    def get_num_frames(self) -> int:
        """
        Return number of frames in the trajectory
        """
        return len(self.data["spatialData"]["bundleData"])
