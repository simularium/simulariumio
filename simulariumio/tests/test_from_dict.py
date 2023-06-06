import pytest
import numpy as np

from simulariumio import (
    utils,
    DisplayData,
    CameraData,
    MetaData,
    UnitData,
    ModelMetaData,
    InputFileData
)
from simulariumio.constants import DEFAULT_CAMERA_SETTINGS, DISPLAY_TYPE
from simulariumio.smoldyn import SmoldynData

TEST_CONSTANTS = np.array([10.0, 20.0, 30.0])
x = 100.0
y = 120.0
z = 110.0


@pytest.mark.parametrize(
    "vector_dict, vector_array",
    [
        (
            {
                "x": x,
                "y": y,
                "z": z,
            },
            np.array([x, y, z]),
        ),
        (
            {
                "x": x,
            },
            np.array([x, TEST_CONSTANTS[1], TEST_CONSTANTS[2]]),
        ),
        (
            {
                "not_valid": x,
            },
            np.array([TEST_CONSTANTS[0], TEST_CONSTANTS[1], TEST_CONSTANTS[2]]),
        ),
        (
            {},
            np.array([TEST_CONSTANTS[0], TEST_CONSTANTS[1], TEST_CONSTANTS[2]]),
        ),
    ],
)
def test_unpack_position_vector(vector_dict, vector_array):
    result = utils.unpack_position_vector(vector_dict, TEST_CONSTANTS)
    assert np.array_equal(result, vector_array)


agent_key_0 = "key0"
agent_key_1 = "key1"
name_0 = "name0"
name_1 = "name1"
radius_0 = "1.2"
url_0 = "test.obj"
display_data_dict = {
    "0": {
        agent_key_0: {
            "name": name_0,
            "radius": radius_0,
            "url": url_0,
        }
    },
    "1": {
        agent_key_1: {
            "name": name_1,
        }
    }
}
display_data_objs = {
    agent_key_0: DisplayData.from_dict({
        "name": name_0,
        "radius": radius_0,
        "url": url_0
    }),
    agent_key_1: DisplayData.from_dict({"name": name_1}),
}


@pytest.mark.parametrize(
    "display_dict, data_dict",
    [
        (
            display_data_dict,
            display_data_objs,
        ),
        (
            dict(),
            dict(),
        ),
    ],
)
def test_unpack_display_data(display_dict, data_dict):
    result = utils.unpack_display_data(display_dict)
    assert result == data_dict


position_0 = 25.0
position_1 = 1.0
position_2 = 9.0
position_3 = 111.9
full_camera_data = {
    "position": {
        "x": str(position_1),
        "y": str(position_0)
    },
    "lookAtPosition": {
        "y": str(position_3)
    },
    "upVector": {
        "y": str(position_2)
    },
    "fovDegrees": str(position_0)
}
full_camera_data_obj = CameraData(
    position=np.array([
        position_1,
        position_0,
        DEFAULT_CAMERA_SETTINGS.CAMERA_POSITION[2]
    ]),
    look_at_position=np.array([
        DEFAULT_CAMERA_SETTINGS.LOOK_AT_POSITION[0],
        position_3,
        DEFAULT_CAMERA_SETTINGS.LOOK_AT_POSITION[2],
    ]),
    up_vector=np.array([
        DEFAULT_CAMERA_SETTINGS.UP_VECTOR[0],
        position_2,
        DEFAULT_CAMERA_SETTINGS.UP_VECTOR[2]
    ]),
    fov_degrees=position_0
)
partial_camera_data = {
    "position": {
        "z": position_0
    }
}


@pytest.mark.parametrize(
    "camera_dict, camera_data",
    [
        (
            full_camera_data,
            full_camera_data_obj,
        ),
        (
            partial_camera_data,
            CameraData(
                position=np.array([
                    DEFAULT_CAMERA_SETTINGS.CAMERA_POSITION[0],
                    DEFAULT_CAMERA_SETTINGS.CAMERA_POSITION[1],
                    position_0
                ]),
            ),
        ),
        (
            {},
            CameraData(),
        ),
    ],
)
def test_camera_from_dict(camera_dict, camera_data):
    result = CameraData.from_dict(camera_dict)
    assert result == camera_data


title = "title"
version = "1.0"
authors = "authors"
description = "description"
doi = "doi"
source_code_url = "url0"
source_code_license_url = "url1"
input_data_url = "url2"
raw_output_data_url = "url3"
full_model_meta_data = {
    "title": title,
    "version": version,
    "authors": authors,
    "description": description,
    "doi": doi,
    "sourceCodeUrl": source_code_url,
    "sourceCodeLicenseUrl": source_code_license_url,
    "inputDataUrl": input_data_url,
    "rawOutputDataUrl": raw_output_data_url
}
full_model_meta_data_obj = ModelMetaData(
    title=title,
    version=version,
    authors=authors,
    description=description,
    doi=doi,
    source_code_url=source_code_url,
    source_code_license_url=source_code_license_url,
    input_data_url=input_data_url,
    raw_output_data_url=raw_output_data_url
)
partial_model_meta_data = {
    "title": title,
    "doi": doi
}


@pytest.mark.parametrize(
    "model_meta_data_dict, model_meta_data",
    [
        (
            full_model_meta_data,
            full_model_meta_data_obj,
        ),
        (
            partial_model_meta_data,
            ModelMetaData(
                title=title,
                doi=doi
            ),
        ),
        (
            {},
            ModelMetaData(),
        )
    ],
)
def test_model_data_from_dict(model_meta_data_dict, model_meta_data):
    result = ModelMetaData.from_dict(model_meta_data_dict)
    assert result == model_meta_data


size_x = 10.0
size_y = 11.0
size_z = 12.0
scale_factor = 2.0
full_metadata = {
    "size": {
        "x": size_x,
        "y": size_y,
        "z": size_z
    },
    "cameraDefault": full_camera_data,
    "trajectoryTitle": title,
    "modelInfo": full_model_meta_data,
    "scaleFactor": scale_factor
}
full_metadata_obj = MetaData(
    box_size=np.array([size_x, size_y, size_z]),
    camera_defaults=full_camera_data_obj,
    scale_factor=scale_factor,
    trajectory_title=title,
    model_meta_data=full_model_meta_data_obj
)


@pytest.mark.parametrize(
    "metadata_dict, metadata",
    [
        (
            full_metadata,
            full_metadata_obj,
        ),
        (
            {},
            MetaData(),
        ),
    ],
)
def test_metadata_from_dict(metadata_dict, metadata):
    result = MetaData.from_dict(metadata_dict)
    assert result == metadata


magnitude_0 = 2.0
name0 = "microsecond"
magnitude_1 = 0.1
name1 = "millimeter"
default_name = "second"
default_magnitude = 3.5
full_time_units = {
    "magnitude": magnitude_0,
    "name": name0
}
full_spatial_units = {
    "magnitude": magnitude_1,
    "name": name1
}
partial_units = {
    "name": name0
}


@pytest.mark.parametrize(
    "unit_data_dict, unit_data",
    [
        (
            full_time_units,
            UnitData(
                magnitude=float(magnitude_0),
                name=name0
            ),
        ),
        (
            full_spatial_units,
            UnitData(
                magnitude=float(magnitude_1),
                name=name1
            ),
        ),
        (
            partial_units,
            UnitData(
                name=name0,
                magnitude=default_magnitude
            ),
        ),
        (
            {},
            UnitData(
                name=default_name,
                magnitude=default_magnitude
            )
        ),
    ],
)
def test_unit_data_from_dict(unit_data_dict, unit_data):
    result = UnitData.from_dict(
        unit_data_dict,
        default_name=default_name,
        default_mag=default_magnitude
    )
    assert result == unit_data


display_type = DISPLAY_TYPE.SPHERE
color = "#0080ff"
full_display_data_dict = {
    "name": name_0,
    "radius": radius_0,
    "url": url_0,
    "color": color
}
partial_display_data_dict = {
    "name": name_0,
    "displayType": display_type,
}
full_display_data_obj = DisplayData(
    name=name_0,
    radius=float(radius_0),
    url=url_0,
    color=color,
    display_type=DISPLAY_TYPE.SPHERE
)


@pytest.mark.parametrize(
    "display_data_dict, display_data",
    [
        (
            full_display_data_dict,
            full_display_data_obj,
        ),
        (
            partial_display_data_dict,
            DisplayData(
                name=name_0,
                display_type=display_type,
                radius=1.0
            ),
        ),
    ],
)
def test_display_data_from_dict(display_data_dict, display_data):
    result = DisplayData.from_dict(
        display_data_dict,
        default_display_type=display_type
    )
    assert result == display_data


file_contents_str = """0 0\nS(solution) -0.8748 -0.451012 500\nS(solution) 0.63683 
0.445285 499\nE(front) 0.844989 -0.534784 600\n0.01 0\nS(solution) -0.813601 
-0.465024 500\nS(solution) 0.681931 0.262768 499\nE(front) 0.844989 -0.534784 
600\nES(front) 0.666775 0.745259 606\n0.02 0\nS(solution) -0.828472 -0.517215 
500\nE(front) 0.844989 -0.534784 600\nES(front) 0.262632 -0.964896 602\n"""

full_smoldyn_dict = {
    "fileContents": {
        "fileContents": file_contents_str
    },
    "metaData": full_metadata,
    "displayData": display_data_dict,
    "timeUnits": full_time_units,
    "spatialUnits": full_spatial_units
}

# at the minimum, we must provided file contentes
default_smoldyn_dict = {
    "fileContents": {
        "fileContents": file_contents_str
    }
}


@pytest.mark.parametrize(
    "smoldyn_dict, smoldyn_data",
    [
        (
            full_smoldyn_dict,
            SmoldynData(
                smoldyn_file=InputFileData(file_contents=file_contents_str),
                meta_data=full_metadata_obj,
                display_data=display_data_objs,
                time_units=UnitData(
                    magnitude=float(magnitude_0),
                    name=name0
                ),
                spatial_units=UnitData(
                    magnitude=float(magnitude_1),
                    name=name1
                )
            ),
        ),
        (
            default_smoldyn_dict,
            SmoldynData(
                smoldyn_file=InputFileData(file_contents=file_contents_str)
            ),
        ),
    ],
)
def test_smoldyn_from_dict(smoldyn_dict, smoldyn_data):
    result = SmoldynData.from_dict(smoldyn_dict)
    assert result == smoldyn_data
