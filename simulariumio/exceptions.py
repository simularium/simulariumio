#!/usr/bin/env python
# -*- coding: utf-8 -*-


class UnsupportedPlotTypeError(Exception):
    """
    This exception is intended to communicate that the requested plot type
    is not one of the supported types and cannot be parsed with simulariumio.
    """

    def __init__(self, plot_type, **kwargs):
        super().__init__(**kwargs)
        self.plot_type = plot_type

    def __str__(self):
        return f"simulariumio does not support this plot type: '{self.plot_type}'."


class MissingDataError(Exception):
    """
    This exception is intended to communicate that the data provided
    is missing a field needed to parse it.
    """

    def __init__(self, field_name, **kwargs):
        super().__init__(**kwargs)
        self.field_name = field_name

    def __str__(self):
        return f"Missing data: '{self.field_name}'."


class DataError(Exception):
    """
    This exception is intended to communicate that something
    is wrong with the data provided.
    """

    def __init__(self, issue, **kwargs):
        super().__init__(**kwargs)
        self.issue = issue

    def __str__(self):
        return f"Problem with Data: '{self.issue}'."


class InputDataError(Exception):
    """
    This exception is intended to communicate that an error occurred
    while the input files were being read or parsed.
    """

    def __init__(self, issue, **kwargs):
        super().__init__(**kwargs)
        self.issue = issue

    def __str__(self):
        return f"Problem with input file: {self.issue}."
