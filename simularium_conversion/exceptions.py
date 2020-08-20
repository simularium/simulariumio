#!/usr/bin/env python
# -*- coding: utf-8 -*-


class UnsupportedSourceEngineError(Exception):
    """
    This exception is intended to communicate that the requested source simulation engine
    is not one of the supported engines and cannot be parsed with simularium_conversion.
    """

    def __init__(self, source_engine, **kwargs):
        super().__init__(**kwargs)
        self.source_engine = source_engine

    def __str__(self):
        return f"simularium_conversion does not support this source simulation engine: '{self.source_engine}'."


class MissingDataError(Exception):
    """
    This exception is intended to communicate that the data provided is missing a field
    needed to parse outputs from the requested source simulation engine.
    """

    def __init__(self, field_name, **kwargs):
        super().__init__(**kwargs)
        self.field_name = field_name

    def __str__(self):
        return f"Missing data for requested source simulation engine: '{self.field_name}'."