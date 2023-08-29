from typing import Dict, Union
from .trajectory_data import TrajectoryData
from .frame_data import FrameData


class SimulariumFileData:
    def __init__(self, file_name: str, file_contents: Union[str, bytes]):
        pass

    def get_frame_at_index(self, frame_number: int) -> Union[FrameData, None]:
        """
        Return frame data for frame at index. If there is no frame at the index,
        return None.
        """
        pass

    def get_index_for_time(self, time: float) -> int:
        """
        Return index for frame closest to a given timestamp
        """
        pass

    def get_trajectory_info(self) -> Dict:
        """
        Return trajectory info block for trajectory, as dict
        """
        pass

    def get_plot_data(self) -> Dict:
        pass

    def get_trajectory_data_object(self) -> TrajectoryData:
        """
        Return the data of the trajectory, as a TrajectoryData object
        """
        pass

    def get_file_contents(self) -> Union[Dict, bytes]:
        """
        Return raw file data, as dict for JSON file or as bytes for binary file
        """
        pass

    def get_num_frames(self) -> int:
        """
        Return number of frames in the trajectory
        """
        pass
