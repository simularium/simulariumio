#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import numpy as np
from MDAnalysis import Universe
from MDAnalysis.tests.datafiles import PSF, DCD
from simulariumio import MetaData, MolstarWriter, FileConverter, InputFileData
from simulariumio.md import MdConverter, MdData


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "input_path", help="path to input .simularium file", nargs="?", default=""
    )
    parser.add_argument('--md', action=argparse.BooleanOptionalAction)
    parser.set_defaults(md=False)
    parser.add_argument('--sim', action=argparse.BooleanOptionalAction)
    parser.set_defaults(sim=False)
    return parser.parse_args()

def generate_md_cif():
    example_data = MdData(
        md_universe=Universe(PSF, DCD),
        meta_data=MetaData(
            box_size=np.array(3 * [100.]),
            trajectory_title="test",
        ),
    )
    MolstarWriter.save(MdConverter(example_data)._data, "test_simularium_md")

def generate_simularium_cif(input_path):
    MolstarWriter.save(
        FileConverter(
            InputFileData(input_path)
        )._data, 
        "test_simularium"
    )

def main():
    args = parse_args()
    if args.md:
        generate_md_cif()
    if args.sim:
        if not args.input_path:
            raise Exception("Please provide a path to the simularium file.")
        generate_simularium_cif(args.input_path)


if __name__ == "__main__":
    main()
