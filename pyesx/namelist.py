"""
This module provides a Namelist class for reading and writing Fortran namelist files, which
are used by ESX for configuration.
"""


from collections import OrderedDict


class Namelist:

    def __init__(self, path=None, file=None):
        self.path = path
        self.sections = OrderedDict()
        if file is not None:
            self.read_file(file)
        elif path is not None:
            with open(path, 'r') as file:
                self.read_file(file)

    def __getitem__(self, item):
        return self.sections[item]

    def __setitem__(self, key, value):
        self.sections[key] = value

    def __delitem__(self, key):
        del self.sections[key]

    def assign_from(self, namelist):
        for section_name, other_section in namelist.sections.items():
            my_section = self.sections.get(section_name, NamelistSection(section_marker=section_name))
            for key, value in other_section.items():
                my_section[key] = value
            self.sections[section_name] = my_section

    def read_file(self, file):
        current_section = None
        current_variable = None
        current_value = None

        def output_variable():
            nonlocal current_variable, current_value
            if current_variable is None or current_value is None:
                return
            current_section[current_variable] = current_value.strip()
            current_variable = None
            current_value = None

        for line in file:
            # Remove comments
            comment = line.find('!')
            if comment >= 0:
                line = line[:comment]
            # Remove whitespace and ignore empty lines.
            line = line.strip()
            if len(line) == 0:
                continue
            # Check if this is the start of a section...
            if line.startswith('&'):
                if current_section is not None:
                    raise RuntimeError('Invalid ESX config; section not ended yet.')
                marker = line[1:]
                if marker in self.sections:
                    current_section = self.sections[marker]
                else:
                    current_section = NamelistSection(section_marker=marker)
                continue
            # Otherwise demand that a section is active...
            elif current_section is None:
                raise RuntimeError('Invalid ESX config; content outside of section.')
            # Check if this is the end of the section...
            if line == '/':
                output_variable()
                self[current_section.section_marker] = current_section
                current_section = None
                continue
            # Check if it looks like we're starting an assignment.
            assignment = line.find('=')
            if assignment > 0:
                output_variable()
                current_variable = line[:assignment].strip()
                current_value = line[assignment+1:].strip()
            # Otherwise assume it's part of the last value
            elif current_value is None:
                raise RuntimeError('Invalid ESX config; unexpected content.')
            else:
                current_value += '\n' + line

    def read(self, path_or_file):
        if isinstance(path_or_file, str):
            with open(path_or_file, 'r') as file:
                self.read_file(file)
        else:
            self.read_file(path_or_file)

    def dump(self):
        print('<pyesx.namelist.Namelist>')
        for section in self.sections.values():
            print(section.section_marker)
            for key, value in section.items():
                value_lines = value.splitlines(False)
                if len(value_lines) == 1:
                    print('   ', key, '=', value)
                else:
                    print('   ', key, '=')
                    for line in value_lines:
                        print('   ', '   ', line)
        print('')

    def write_file(self, file):
        for section in self.sections.values():
            print('&' + section.section_marker, file=file)
            for key, value in section.items():
                print(key, '=', value if len(value.splitlines()) == 1 else '\n'+value, file=file)
            print('/', file=file)

    def write(self, path_or_file):
        if isinstance(path_or_file, str):
            with open(path_or_file, 'w') as file:
                self.write_file(file)
        else:
            self.write_file(path_or_file)


class NamelistSection(OrderedDict):

    def __init__(self, *args, **kwargs):
        if 'section_marker' in kwargs:
            self.section_marker = kwargs['section_marker']
            del kwargs['section_marker']
        else:
            self.section_marker = ''
        super().__init__(*args, **kwargs)
