"""
test_json_writer.py

Unit tests for the JsonWriter class in simulariumio.writers.

Current only tests `save_replacing_nan()` to ensure that:
        * All NaN values are replaced with null (None in Python).
        * Output JSON is valid and does not contain any NaN.
        * Output file is written correctly in `.simularium` format.

Status:
    - Uses pytest with fixtures to generate a minimal TrajectoryData mock.
    - Tests are self-contained and do not require writing to real disk locations.
    - Assumes simulariumio is installed or importable via editable mode (`pip install -e .`).

To run:
    > pytest simulariumio/tests/writers/test_json_writer.py
"""
import json
import os
import tempfile
import numpy as np
import pytest
from simulariumio import TrajectoryData, AgentData, UnitData, DisplayData
from simulariumio.constants import DISPLAY_TYPE, VALUES_PER_3D_POINT, VIZ_TYPE
from simulariumio.writers import JsonWriter

@pytest.fixture
def trajectory_with_nan():
    # Create mock AgentData with NaNs
    agent_data = AgentData.from_dimensions(dimensions=(1, 1, VALUES_PER_3D_POINT))
    agent_data.positions[0][0] = [np.nan, 1.0, 2.0]
    agent_data.radii[0][0] = np.nan
    agent_data.subpoints[0][0] = [0.0, np.nan, 0.0, 1.0, 1.0, 1.0]
    agent_data.types[0].append("A")
    agent_data.unique_ids[0][0] = 1
    agent_data.n_agents[0] = 1
    agent_data.n_subpoints[0][0] = 6
    agent_data.viz_types[0][0] = VIZ_TYPE.FIBER

    # Wrap into a TrajectoryData object
    traj_data = TrajectoryData(
        meta_data=None,
        agent_data=agent_data,
        time_units=UnitData(name="s"),
        spatial_units=UnitData(name="nm"),
        plots=None,
    )
    return traj_data

def test_save_replacing_nan(trajectory_with_nan):
    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = os.path.join(tmpdir, "test_output")

        # Act: Call method under test
        JsonWriter.save_replacing_nan(trajectory_with_nan, output_path, validate_ids=False)

        # Verify file exists
        output_file = output_path + ".simularium"
        assert os.path.exists(output_file)

        # Verify contents
        with open(output_file, "r") as f:
            json_data = json.load(f)

        # Assert that NaN was replaced with null
        positions = json_data["trajectoryInfo"]["agentData"]["positions"][0][0]
        radii = json_data["trajectoryInfo"]["agentData"]["radii"][0][0]
        subpoints = json_data["trajectoryInfo"]["agentData"]["subpoints"][0][0]

        assert positions[0] is None
        assert isinstance(positions[1], float)
        assert radii is None
        assert subpoints[1] is None
