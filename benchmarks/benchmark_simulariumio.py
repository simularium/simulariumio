#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import os
import time

import numpy as np
from download_benchmark_resources import Args, download_benchmark_resources

from simulariumio import DISPLAY_TYPE, DisplayData, InputFileData, MetaData
from simulariumio.cytosim import CytosimConverter, CytosimData, CytosimObjectInfo
from simulariumio.springsalad import SpringsaladConverter, SpringsaladData

###############################################################################

LOCAL_RESOURCES_DIR = os.path.join(os.getcwd(), "resources")

###############################################################################


def convert_d_c_cytosim(input_path):
    data = CytosimData(
        meta_data=MetaData(
            box_size=np.array([6.0, 6.0, 1.0]),
            scale_factor=10.0,
        ),
        object_info={
            "fibers": CytosimObjectInfo(
                cytosim_file=InputFileData(
                    file_path=f"{input_path}/fiber_points.txt",
                ),
                display_data={
                    1: DisplayData(
                        name="actin",
                        radius=0.02,
                        display_type=DISPLAY_TYPE.FIBER,
                    ),
                    2: DisplayData(
                        name="myosin",
                        radius=0.02,
                        display_type=DISPLAY_TYPE.FIBER,
                    ),
                    3: DisplayData(
                        name="myosinB",
                        radius=0.02,
                        display_type=DISPLAY_TYPE.FIBER,
                    ),
                },
            ),
        },
    )
    return CytosimConverter(data)


def convert_condensate_springsalad(input_path):
    data = SpringsaladData(
        sim_view_txt_file=InputFileData(
            file_path=f"{input_path}/Above_Ksp_viewer.txt",
        ),
        display_data={
            "ORANGE": DisplayData(
                name="A Linker",
                display_type=DISPLAY_TYPE.SPHERE,
            ),
            "MAGENTA": DisplayData(
                name="A Binding site",
                display_type=DISPLAY_TYPE.SPHERE,
            ),
            "GREEN": DisplayData(
                name="B Binding site",
                display_type=DISPLAY_TYPE.SPHERE,
            ),
            "PINK": DisplayData(
                name="B Linker",
                display_type=DISPLAY_TYPE.SPHERE,
            ),
        },
    )
    return SpringsaladConverter(data)


convert_benchmarks = {
    "d_c": convert_d_c_cytosim,
    "springsalad_condensate": convert_condensate_springsalad,
}


def main():
    argparse.ArgumentParser(
        description="Parses large data files to test speed of SimulariumIO"
    )
    # download data if there's none in resources
    found_data = False
    for item in os.listdir(LOCAL_RESOURCES_DIR):
        if os.path.isdir(os.path.join(LOCAL_RESOURCES_DIR, item)):
            found_data = True
            break
    if not found_data:
        args = Args()
        download_benchmark_resources(args)
    # run benchmarks
    for item in os.listdir(LOCAL_RESOURCES_DIR):
        item_path = os.path.join(LOCAL_RESOURCES_DIR, item)
        if not os.path.isdir(item_path):
            continue
        start_time = time.time()
        converter = convert_benchmarks[item](item_path)
        convert_time = time.time() - start_time
        print(f"{item} convert ran in {convert_time}")
        converter.write_JSON(f"{item}_benchmark")
        write_time = time.time() - start_time - convert_time
        print(f"{item} write ran in {write_time}")


if __name__ == "__main__":
    main()
