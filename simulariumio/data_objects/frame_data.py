from typing import Dict, Union
import numpy as np


class FrameData:
    frame_number: int
    n_agents: int
    time: float
    data: Union[Dict, bytes]

    def __init__(
        self,
        frame_number: int,
        n_agents: int,
        time: float,
        data: Union[bytes, Dict]
    ):
        """
        This object holds frame data for a single frame of simularium data
        """
        self.frame_number = frame_number
        self.n_agents = n_agents
        self.time = time
        self.data = data
