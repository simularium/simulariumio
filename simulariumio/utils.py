import numpy as np
from typing import Dict


def unpack_position_vector(
    vector_dict: Dict[str, str], defaults: np.ndarray
) -> np.ndarray:
    """
    Takes a vector dict describing x, y, z coordinates and default values
    and returns a numpy array representing the 3 coordintes

    Parameters
    ----------
    vector_dict : Dict[str, str]
        Dict representing values of X, Y, and/or Z coordinates
        Keys can either be {'0','1','2'} or {'x','y','z'}
    defaults: np.ndarray
        Numpy array representing default XYZ coordinates. For any coordinates
        not provided in vector_dict, these default values will be used in the
        result vector
    """
    # if no vector information was given, go with the defaults
    if vector_dict is None:
        return defaults

    # if the keys provided in vector_dict are {'x','y','z'}
    if vector_dict.get("x") or vector_dict.get("y") or vector_dict.get("z"):
        # use all positions given, but use defaults if any are missing
        return np.array(
            [
                float(vector_dict.get("x", defaults[0])),
                float(vector_dict.get("y", defaults[1])),
                float(vector_dict.get("z", defaults[2])),
            ]
        )

    # else, assume keys are {'0','1','2'}
    return np.array(
        [
            float(vector_dict.get("0", defaults[0])),
            float(vector_dict.get("1", defaults[1])),
            float(vector_dict.get("2", defaults[2])),
        ]
    )
