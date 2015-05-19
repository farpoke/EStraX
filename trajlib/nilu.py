"""
This module provides a helper class NiluTrajectories for reading sets of trajectories
from trajectory files provided by NILU.
"""


import re


class NiluTrajectories:

    def __init__(self, path_or_file=None):
        self.path = path_or_file
        self.trajectories = []
        if path_or_file is not None:
            self.read_from_file(path_or_file)

    @staticmethod
    def _skip_header(file):
        first_line = file.readline()
        header_lines = int(first_line.split()[0])
        for _ in range(header_lines - 1):
            file.readline()

    def _read_trajectories(self, file):
        NiluTrajectories._skip_header(file)
        while True:
            info_line = file.readline().strip()
            if len(info_line) == 0:
                break
            info_split = info_line.split()
            date, time, stop_index, point_count = info_split[1], info_split[3], int(info_split[6]), int(info_split[10])
            header_line = file.readline()
            header_items = re.findall(r' +[^ ]+', header_line)

            acc = 0

            def item_slice(item):
                nonlocal acc
                start, stop = acc, acc + len(item)
                acc = stop
                return start, stop

            header_slices = [item_slice(item) for item in header_items]
            header_names = [item.strip() for item in header_items]

            def read_line():
                line = file.readline()
                return tuple(float(line[start:stop]) for start, stop in header_slices)

            data_rows = [read_line() for _ in range(point_count)]
            transposed = zip(*data_rows)
            data = dict(zip(header_names, transposed))
            self.trajectories.append((date, time, data))

    def read_from_file(self, path_or_file):
        if isinstance(path_or_file, str):
            with open(path_or_file, 'r', encoding='latin-1') as file:
                self._read_trajectories(file)
        else:
            self._read_trajectories(path_or_file)

    def get_trajectories(self, year=None, month=None, day=None, hour=None, datetime=None, z=None):
        if datetime is not None:
            year, month, day, hour = datetime.year, datetime.month, datetime.day, datetime.hour
        date_string = '%d%02d%02d' % (year, month, day)
        time_string = str(hour * 100 * 100)
        for date, time, data in self.trajectories:
            if date != date_string or time != time_string:
                continue
            if z is not None and z != data['Z'][0]:
                continue
            yield data
