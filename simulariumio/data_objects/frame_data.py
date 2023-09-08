from typing import Dict, Union


class FrameData:
    def __init__(
        self, frame_number: int, n_agents: int, time: float, data: Union[bytes, Dict]
    ):
        """
        This object holds frame data for a single frame of simularium data

        Parameters
        ----------
        frame_number : int
            Index of frame in the simulation
        n_agents : int
            Number of agents included in the frame
        time : float
            Elapsed simulation time of the frame
        data : bytes or dict
            Spatial data for the frame, as a byte array for binary encoded
            .simularium files or as a dict for JSON .simularium files
        """
        self.frame_number = frame_number
        self.n_agents = n_agents
        self.time = time
        self.data = data
