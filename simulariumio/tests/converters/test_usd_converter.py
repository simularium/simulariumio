#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

import numpy as np
import pytest

from simulariumio import DisplayData, JsonWriter, MetaData, UnitData
from simulariumio.constants import DISPLAY_TYPE, VIZ_TYPE
from simulariumio.usd import UsdConverter, UsdData

# Paths to test USD files
ASCII_USD = "simulariumio/tests/data/usd/actin_USDascii.usd"
BINARY_USD = "simulariumio/tests/data/usd/actin_USDbinary.usd"


@pytest.fixture
def ascii_converter():
    return UsdConverter(UsdData(usd_file_path=ASCII_USD, center=False))


@pytest.fixture
def binary_converter():
    return UsdConverter(UsdData(usd_file_path=BINARY_USD, center=False))


@pytest.fixture
def ascii_results(ascii_converter):
    return JsonWriter.format_trajectory_data(ascii_converter._data)


class TestUsdConverterBasic:
    def test_agent_count(self, ascii_converter):
        assert ascii_converter._data.agent_data.n_agents[0] == 8

    def test_frame_count(self, ascii_converter):
        total = len(ascii_converter._data.agent_data.times)
        assert total == 400

    def test_times(self, ascii_converter):
        times = ascii_converter._data.agent_data.times
        assert np.isclose(times[0], 0.0)
        # Frame 2 at 24fps = 1/24
        assert np.isclose(times[1], 1.0 / 24.0)

    def test_agent_types(self, ascii_converter):
        types = ascii_converter._data.agent_data.types[0]
        expected = [
            "actin1", "actin2", "actin3", "actin4",
            "actin5", "actin6", "actin7", "actin8",
        ]
        assert types == expected

    def test_viz_types_default(self, ascii_converter):
        viz = ascii_converter._data.agent_data.viz_types[0]
        for i in range(8):
            assert viz[i] == VIZ_TYPE.DEFAULT


class TestUsdPositionsAndRotations:
    def test_first_frame_position(self, ascii_converter):
        # actin1 at frame 1: translate=(11.259, -0.3637, 5.1427) * metersPerUnit=0.01
        # then auto-scaled by scale_factor
        scale = ascii_converter._data.meta_data.scale_factor
        pos = ascii_converter._data.agent_data.positions[0][0]
        assert np.isclose(pos[0], 11.259010518398657 * 0.01 * scale, atol=1e-3)
        assert np.isclose(pos[1], -0.36371288058467566 * 0.01 * scale, atol=1e-3)
        assert np.isclose(pos[2], 5.142660258715312 * 0.01 * scale, atol=1e-3)

    def test_first_frame_rotation(self, ascii_converter):
        # actin1 at frame 1: rotateXYZ=(-18.1128, 155.2658, -41.9077) degrees
        # stored as radians for the viewer
        rot = ascii_converter._data.agent_data.rotations[0][0]
        assert np.isclose(rot[0], np.radians(-18.112833), atol=1e-3)
        assert np.isclose(rot[1], np.radians(155.26578), atol=1e-3)
        assert np.isclose(rot[2], np.radians(-41.907677), atol=1e-3)


class TestUsdMeshDeduplication:
    def test_single_obj_for_identical_meshes(self, ascii_converter):
        assert len(ascii_converter._obj_data) == 1

    def test_all_meshes_map_to_same_obj(self, ascii_converter):
        obj_files = set(ascii_converter._mesh_to_obj.values())
        assert len(obj_files) == 1
        assert "mesh_0.obj" in obj_files

    def test_eight_meshes_tracked(self, ascii_converter):
        assert len(ascii_converter._mesh_to_obj) == 8


class TestUsdMaterialColors:
    def test_display_data_colors(self, ascii_converter):
        dd = ascii_converter._data.agent_data.display_data
        # actin1 color: (0.272, 0.8, 0.272) -> #45cc45
        assert dd["actin1"].color == "#45cc45"
        # actin2 color: (0.384, 0.8, 0.123) -> #61cc1f
        assert dd["actin2"].color == "#61cc1f"

    def test_display_type_obj(self, ascii_converter):
        dd = ascii_converter._data.agent_data.display_data
        for name in dd:
            assert dd[name].display_type == DISPLAY_TYPE.OBJ

    def test_display_url_is_obj_filename(self, ascii_converter):
        dd = ascii_converter._data.agent_data.display_data
        for name in dd:
            assert dd[name].url == "mesh_0.obj"


class TestUsdRadii:
    def test_radius_from_extent(self, ascii_converter):
        # Extent max dimension: max(6.7858544, 6.7360334, 4.4300746) = 6.7858544
        # radius = 6.7858544 / 2.0 * metersPerUnit(0.01) * scale_factor
        scale = ascii_converter._data.meta_data.scale_factor
        radius = ascii_converter._data.agent_data.radii[0][0]
        expected = 6.7858544 / 2.0 * 0.01 * scale
        assert np.isclose(radius, expected, atol=1e-3)


class TestUsdObjWriting:
    def test_save_creates_files(self, ascii_converter, tmp_path):
        output = str(tmp_path / "test_output")
        ascii_converter.save(output, binary=True)

        assert os.path.exists(output + ".simularium")
        assert os.path.exists(tmp_path / "mesh_0.obj")

    def test_obj_has_correct_geometry(self, ascii_converter, tmp_path):
        output = str(tmp_path / "test_output")
        ascii_converter.save(output, binary=True)

        obj_path = tmp_path / "mesh_0.obj"
        with open(obj_path) as f:
            lines = f.readlines()

        v_lines = [l for l in lines if l.startswith("v ")]
        f_lines = [l for l in lines if l.startswith("f ")]
        assert len(v_lines) == 4768
        assert len(f_lines) == 9528


class TestUsdTypeMapping:
    def test_type_mapping_structure(self, ascii_results):
        tm = ascii_results["trajectoryInfo"]["typeMapping"]
        # Should have entries for each agent type
        assert len(tm) == 8
        # Each should have OBJ display type
        for tid in tm:
            assert tm[tid]["geometry"]["displayType"] == "OBJ"
            assert tm[tid]["geometry"]["url"] == "mesh_0.obj"


class TestUsdBinaryFormat:
    def test_binary_usd_matches_ascii(self, ascii_converter, binary_converter):
        # Both should produce same number of agents
        assert (
            ascii_converter._data.agent_data.n_agents[0]
            == binary_converter._data.agent_data.n_agents[0]
        )
        # Both should produce same mesh dedup
        assert len(ascii_converter._obj_data) == len(binary_converter._obj_data)


class TestUsdDisplayDataOverride:
    def test_user_display_data_override(self):
        custom_display = {
            "actin1": DisplayData(
                name="CustomActin",
                display_type=DISPLAY_TYPE.SPHERE,
                color="#ff0000",
                radius=5.0,
            ),
        }
        converter = UsdConverter(
            UsdData(
                usd_file_path=ASCII_USD,
                display_data=custom_display,
                center=False,
            )
        )
        dd = converter._data.agent_data.display_data
        assert "CustomActin" in dd
        assert dd["CustomActin"].display_type == DISPLAY_TYPE.SPHERE
        assert dd["CustomActin"].color == "#ff0000"
        # Other types should still be auto-detected
        assert "actin2" in dd
        assert dd["actin2"].display_type == DISPLAY_TYPE.OBJ


class TestUsdCentering:
    def test_centered_positions_near_origin(self):
        converter = UsdConverter(
            UsdData(usd_file_path=ASCII_USD, center=True)
        )
        positions = converter._data.agent_data.positions
        # Mean position across all agents at frame 0 should be near origin
        mean_pos = np.mean(positions[0, :8], axis=0)
        assert np.all(np.abs(mean_pos) < 5.0)
