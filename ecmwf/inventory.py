"""
This module provides two classes to help with accessing ECMWF netCDF4 files.
"""


import contextlib
import itertools
import os

import netCDF4

from . import interpolation, variables


class Inventory:
    """
    This class keeps an inventory of known ECMWF files and their variables.

    The methods add_directory and add_file can be used to add ECMWF files to the inventory.

    The construct_variable method can be used to access a variable.

    To read data from the variables it is required that the Inventory object is
    used as a context manager using the with statement.

    Example:

        inventory = ecmwf.inventory.Inventory()
        inventory.add_directory('./Data')
        u_wind = inventory.construct_variable(*ecmwf.variables.U_VELOCITY)
        with inventory:
            value = u_wind[time, level, lat, lon]
            # etc...

    """

    def __init__(self):
        self.catalogue = {}
        self.exit_stack = None
        self.open_datasets = None

    def __enter__(self):
        if self.exit_stack is not None:
            raise RuntimeError("Recursive use of Inventory as context manager.")
        self.exit_stack = contextlib.ExitStack()
        self.open_datasets = {}

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.exit_stack.close()
        self.exit_stack = None
        self.open_datasets = None

    def add_directory(self, path, recursive=True):
        abs_norm_path = os.path.normpath(os.path.abspath(path))
        for name in os.listdir(abs_norm_path):
            full_name = os.path.join(abs_norm_path, name)
            if os.path.isfile(full_name):
                self.add_file(full_name)
            elif recursive and os.path.isdir(full_name):
                self.add_directory(full_name)

    def add_file(self, path):
        abs_norm_path = os.path.normpath(os.path.abspath(path))
        if abs_norm_path in self.catalogue:
            return
        try:
            with netCDF4.Dataset(path) as ds:
                catalogue_entry = {'vars': {}, 'time range': None}
                for var_name, var_desc in ds.variables.items():
                    var_type = var_desc.dimensions
                    if var_desc.ndim == 1:
                        if var_name == 'level':
                            assert var_desc.long_name == 'pressure_level'
                        elif var_name == 'time':
                            min_time, max_time = int(var_desc[0]), int(var_desc[-1])
                            catalogue_entry['time range'] = (min_time, max_time)
                    catalogue_entry['vars'][var_name] = var_type
                self.catalogue[path] = catalogue_entry
        except RuntimeError:
            self.catalogue[abs_norm_path] = None
            return

    def get_files_with_variable(self, var_name, var_type):
        if not isinstance(var_type, tuple):
            var_type = tuple(var_type)
        for path, entry in self.catalogue.items():
            if var_name in entry['vars'] and entry['vars'][var_name] == var_type:
                yield path

    def enumerate_paths(self):
        yield from self.catalogue.keys()

    def enumerate_variables(self):
        vars_generator = (entry['vars'].items() for entry in self.catalogue.values())
        yield from set(itertools.chain(*vars_generator))

    def construct_variable(self, var_name, var_type):
        var = Variable(var_name, var_type, inventory=self)
        for path in self.get_files_with_variable(var_name, var_type):
            var.add_file(path)
        return var

    def open_dataset(self, path):
        assert self.exit_stack is not None and self.open_datasets is not None
        if path in self.open_datasets:
            return self.open_datasets[path]
        ds = self.exit_stack.enter_context(netCDF4.Dataset(path))
        self.open_datasets[path] = ds
        return ds


class Variable:
    """
    This class helps with reading ECMWF data by keeping an inventory of data files
    which contains the variable specified during construction. Data may thus be read
    without having to manually access various netCDF files.

    See the Inventory class documentation for a short example.
    """

    def __init__(self, name, type_, inventory=None):
        self.name = name
        self.type = type_ if isinstance(type_, tuple) else tuple(type_)
        self.inventory = inventory
        self.dataset_ranges = {}
        self.dataset_indexing = {}
        self.last_used_dataset = None
        self.interpolation = interpolation.interpolate_lerp

    def __getitem__(self, item):
        if len(item) != len(self.type):
            raise Exception('Invalid number of values to Variable.__getitem__')
        elif self.last_used_dataset is not None and self._dataset_in_range(self.last_used_dataset, item):
            return self._access_dataset(self.last_used_dataset, item)
        else:
            for dataset in self.dataset_ranges:
                if self._dataset_in_range(dataset, item):
                    self.last_used_dataset = dataset
                    return self._access_dataset(dataset, item)
            else:
                raise RuntimeError('No data available for variable ' + self.name + ' at requested point ' + str(item))

    def _dataset_in_range(self, dataset, values):
        ranges = self.dataset_ranges[dataset]
        for value, min_value, max_value in zip(values, *zip(*ranges)):
            if not min_value <= value <= max_value:
                return False
        else:
            return True

    def _access_dataset(self, dataset, values):
        indexing = self.dataset_indexing[dataset]  # A tuple of (indices, sorted values) for each axis.
        interpolation_parameters = tuple(self.interpolation(values[idx], indexing[idx][1])
                                         for idx in range(len(values)))
        data = self.inventory.open_dataset(dataset)

        def get_value(indices=()):
            index_count = len(indices)
            if index_count == len(values):
                return data.variables[self.name][indices]
            else:
                params = interpolation_parameters[index_count]
                return sum(get_value(indices + (indexing[index_count][0][index_index], )) * factor
                           for index_index, factor in params)

        return get_value()

    def add_file(self, path):
        with netCDF4.Dataset(path) as dataset:
            assert dataset.variables[self.name].dimensions == self.type
            margins = [dataset.variables[axis][:] for axis in self.type]
            enumerated_margins = (sorted(enumerate(margin), key=lambda x: x[1]) for margin in margins)
            indexing = [tuple(zip(*margin)) for margin in enumerated_margins]
            for idx in range(len(self.type)):
                if self.type[idx] == 'longitude':
                    # Make longitude wrap around, hopefully correctly.
                    indices, values = indexing[idx]
                    indices += indices[0],
                    values += values[0] + 360,
                    indexing[idx] = indices, values
            self.dataset_indexing[path] = indexing
            ranges = tuple((min(values), max(values)) for _, values in indexing)
            self.dataset_ranges[path] = ranges

    def get_coverage(self, subspace=None):
        if subspace is None:
            subspace = tuple(None for _ in self.type)
        assert len(subspace) == len(self.type)

        def axis_coverage(idx):
            if subspace[idx] is not None:
                return subspace[idx]
            valid_ranges = tuple(ranges for ranges in self.dataset_ranges.values()
                                 if all(value is None or axis_range[0] <= value <= axis_range[1]
                                        for value, axis_range in zip(subspace, ranges)))
            min_coverage = min(ranges[idx][0] for ranges in valid_ranges)
            max_coverage = max(ranges[idx][1] for ranges in valid_ranges)
            return min_coverage, max_coverage

        coverage = tuple(axis_coverage(idx) for idx in range(len(subspace)))
        return coverage