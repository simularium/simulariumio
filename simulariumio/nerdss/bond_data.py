from ..data_objects import UnitData
from typing import List

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
        self.agent_name_a = agent_name_a
        self.agent_name_b = agent_name_b
        self.max_length = max_length