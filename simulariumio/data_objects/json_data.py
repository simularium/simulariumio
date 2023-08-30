from typing import Any, Dict
import json
import numpy as np

from .agent_data import AgentData
from .frame_data import FrameData
from .simularium_file_data import SimulariumFileData
from .trajectory_data import TrajectoryData


class JsonData(SimulariumFileData):
    def __init__(self, file_name: str, file_contents: str):
        """
        This object holds JSON encoded simulation trajectory file's
        data while staying close to the original file format

        Parameters
        ----------
        file_name : str
            Name of the file
        file_contents : str
            A string of the data of an open .simularium file
        """
        self.file_name = file_name
        self.data = json.loads(file_contents)
        self.n_agents = AgentData.from_buffer_data(self.data).n_agents

    def get_frame_at_index(self, frame_number: int) -> FrameData:
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
        return self.data["trajectoryInfo"]

    def get_plot_data(self) -> Dict:
        return self.data["plotData"]

    def get_trajectory_data_object(self) -> TrajectoryData:
        return TrajectoryData.from_buffer_data(self.data)

    def get_file_contents(self) -> Dict:
        return self.data

    def get_num_frames(self) -> int:
        return len(self.data["spatialData"]["bundleData"])

    def get_file_name(self) -> str:
        return self.file_name
