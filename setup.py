#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import find_packages, setup

with open("README.md") as readme_file:
    readme = readme_file.read()

physicell_requirements = [
    "scipy>=1.5.2",
]

setup_requirements = [
    "pytest-runner>=5.2",
]

test_requirements = [
    "black>=19.10b0",
    "codecov>=2.1.4",
    "flake8>=3.8.3",
    "flake8-debugger>=3.2.1",
    "pytest>=5.4.3",
    "pytest-cov>=2.9.0",
    "pytest-raises>=0.11",
    *physicell_requirements,
]

benchmark_requirements = [
    "awscli>=1.20"
    "quilt3>=3.4",
]

dev_requirements = [
    *setup_requirements,
    *test_requirements,
    *benchmark_requirements,
    "bumpversion>=0.6.0",
    "coverage>=5.1",
    "ipython>=7.15.0",
    "m2r>=0.2.1",
    "pytest-runner>=5.2",
    "Sphinx>=2.0.0b1,<3",
    "sphinx_rtd_theme>=0.4.3",
    "tox>=3.15.2",
    "tox-conda>=0.2.1",
    "twine>=3.1.1",
    "wheel>=0.34.2",
]

requirements = [
    "numpy>=1.16",
    "pandas>=1.1.2",
    "pint>=0.17",
]

extra_requirements = {
    "setup": setup_requirements,
    "test": test_requirements,
    "dev": dev_requirements,
    "physicell": physicell_requirements,
    "benchmark": benchmark_requirements,
    "all": [
        *requirements,
        *dev_requirements,
        *physicell_requirements,
        *benchmark_requirements
    ]
}


setup(
    author="Blair Lyons",
    author_email="blairl@alleninstitute.org",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: Free for non-commercial use",
        "Natural Language :: English",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    description="Simularium Conversion helps convert simulation outputs to the format consumed by the Simularium viewer.",
    entry_points={
        "console_scripts": [],
    },
    install_requires=requirements,
    license="Allen Institute Software License",
    long_description=readme,
    long_description_content_type="text/markdown",
    include_package_data=True,
    keywords="simulariumio",
    name="simulariumio",
    packages=find_packages(exclude=["tests", "*.tests", "*.tests.*"]),
    python_requires=">=3.7",
    setup_requires=setup_requirements,
    test_suite="simulariumio/tests",
    tests_require=test_requirements,
    extras_require=extra_requirements,
    url="https://github.com/allen-cell-animated/simulariumio",
    # Do not edit this string manually, always use bumpversion
    # Details in CONTRIBUTING.rst
    version="1.2.0",
    zip_safe=False,
)
