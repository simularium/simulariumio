from ..data_objects import UnitData
import numpy as np


class BondData:
    agent_name_a: str
    agent_name_b: str
    max_length: UnitData

    def __init__(
        self,
        agent_name_a: str,
        agent_name_b: str,
        max_length: UnitData,
    ):
        """
        Parameters
        ----------
        agent_name_a: str
            Name of the first agent of this bond. This must match the
            name in the input file data
        agent_name_b: str
            Name of the second agent of this bond. This must match the
            name in the input file data
        max_length: UnitData
            The max distance at which this bond can exist
        """
        self.agent_name_a = agent_name_a
        self.agent_name_b = agent_name_b
        self.max_length = max_length

    def _do_names_match(self, name_0: str, name_1: str) -> bool:
        return (name_0 == self.agent_name_a and name_1 == self.agent_name_b) or (
            name_0 == self.agent_name_b and name_1 == self.agent_name_a
        )

    def _is_within_range(
        self, pos_0: np.ndarray, pos_1: np.ndarray, units: UnitData
    ) -> bool:
        distance = np.sqrt(np.sum((pos_0 - pos_1) ** 2))
        return distance * units <= self.max_length

    def is_valid_bond(
        self,
        name_0: str,
        pos_0: np.ndarray,
        name_1: str,
        pos_1: np.ndarray,
        units: UnitData,
    ) -> bool:
        return self._do_names_match(name_0, name_1) and self._is_within_range(
            pos_0, pos_1, units
        )
