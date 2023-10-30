from typing import Dict, Union
from abc import ABC, abstractmethod
from .trajectory_data import TrajectoryData
from .frame_data import FrameData


class SimulariumFileData(ABC):
    def __init__(self, file_contents: Union[str, bytes]):
        pass

    @abstractmethod
    def get_frame_at_index(self, frame_number: int) -> Union[FrameData, None]:
        pass

    @abstractmethod
    def get_index_for_time(self, time: float) -> int:
        pass

    @abstractmethod
    def get_trajectory_info(self) -> Dict:
        pass

    @abstractmethod
    def get_plot_data(self) -> Dict:
        pass

    @abstractmethod
    def get_trajectory_data_object(self) -> TrajectoryData:
        pass

    @abstractmethod
    def get_file_contents(self) -> Union[Dict, bytes]:
        pass

    @abstractmethod
    def get_num_frames(self) -> int:
        pass
