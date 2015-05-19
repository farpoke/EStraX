"""
This module provides a Config class that can be used to read and write ESX configuration files.

The Config class provides different configuration sections used by ESX and each section contains
properties corresponding to the various configuration options. These properties may be read from
and assigned to as if they were normal python member variables.
"""


from enum import Enum

from .namelist import *


class _NamelistProperty:

    def __init__(self, variable, can_be_none=False):
        self.variable = variable
        self.can_be_none = can_be_none

    def __get__(self, instance, owner):
        if instance is None:
            return self
        elif self.variable in instance.namelist:
            return self.nml_to_py(instance.namelist[self.variable])
        else:
            return None

    def __set__(self, instance, value):
        instance.namelist[self.variable] = self.py_to_nml(value)

    def __delete__(self, instance):
        del instance.namelist[self.variable]

    def nml_to_py(self, value):
        return value

    def py_to_nml(self, value):
        return value


class _StringProperty(_NamelistProperty):

    def nml_to_py(self, value):
        return value[1:-1]  # Strip surrounding quotes

    def py_to_nml(self, value):
        return '"' + str(value) + '"'


class _BoolProperty(_NamelistProperty):

    def nml_to_py(self, value):
        if value == 'T':
            return True
        elif value == 'F':
            return False
        else:
            raise ValueError("Namelist has invalid value for boolean.")

    def py_to_nml(self, value):
        assert(isinstance(value, bool))
        return 'T' if value else 'F'


class _RealProperty(_NamelistProperty):

    def nml_to_py(self, value):
        return float(value)

    def py_to_nml(self, value):
        return str(value)


class _IntProperty(_NamelistProperty):

    def nml_to_py(self, value):
        return int(value)

    def py_to_nml(self, value):
        return str(value)


class _FloatProperty(_NamelistProperty):

    def nml_to_py(self, value):
        return float(value)

    def py_to_nml(self, value):
        return str(value)


class _YMDHSProperty(_NamelistProperty):

    def nml_to_py(self, value):
        parts = value.split()
        if len(parts) != 5:
            raise ValueError('YMDHS value not recognized: ' + value)
        return tuple(map(int, parts))

    def py_to_nml(self, value):
        if len(value) != 5:
            raise ValueError('Expected an iterable of length 5.')
        return ' '.join(map(str, value))


class _TableProperty(_NamelistProperty):

    def nml_to_py(self, value):
        # FIXME
        return tuple(tuple(item.strip() for item in line.split(',')) for line in value.splitlines())

    def py_to_nml(self, value):

        def format_item(x):
            if isinstance(x, str):
                return "'" + x + "'"
            elif isinstance(x, (int, float)):
                return str(x)
            elif isinstance(x, Enum):
                return format_item(x.value)
            elif isinstance(x, bool):
                return 'T' if x else 'F'
            else:
                raise ValueError('Not sure how to format item: ' + repr(x))

        lines = []
        for row in value:
            parts = []
            for item in row:
                parts.append(format_item(item))
            lines.append(', '.join(parts))
        return '\n'.join(lines)


class _EnumProperty(_StringProperty):

    def __init__(self, variable, enum_type, **kwargs):
        super().__init__(variable, **kwargs)
        self.enum_type = enum_type

    def nml_to_py(self, value):
        value = super().nml_to_py(value)
        values = dict((member.value, member) for member in self.enum_type)
        if value in values:
            return values[value]
        else:
            raise ValueError('Namelist has unrecognized value: ' + value)

    def py_to_nml(self, value):
        if not isinstance(value, self.enum_type):
            raise ValueError('Property expected a value of type ' + str(self.enum_type))
        return super().py_to_nml(value.value)


class EsxMode(Enum):
    Moving = 'Moving'
    Fixed = 'Fixed'


class EsxUnits(Enum):
    ppb = 'ppb'
    ppt = 'ppt'
    molecules_per_cm3 = 'molec_per_cm3'
    pn_per_cm3 = 'pn_per_cm3'
    molecules_per_cm3_and_second = 'molec/cm3/s'
    cm_per_second = 'cm/s'


class EsxDataSource(Enum):
    Hyde2011 = 'Hyde2011'
    Lagrange0 = 'Lagrange0'
    Config = 'Config'
    CSV = Lagrange0


class ConfigSection:

    @classmethod
    def get_property_names(cls):
        return [prop for prop in dir(cls) if isinstance(getattr(cls, prop), _NamelistProperty)]

    def __init__(self, namelist=None, default_section=None):
        if namelist is None:
            self.namelist = NamelistSection(section_marker=default_section)
        else:
            self.namelist = namelist

    def info_dump(self):
        print('&' + self.namelist.section_marker)

        def get_row(self_, prop_name):
            prop_instance = getattr(type(self_), prop_name)
            prop_value = getattr(self_, prop_name)
            prop_value_txt = str(prop_value)
            if len(prop_value_txt.splitlines()) > 1:
                prop_value_txt = prop_value_txt.splitlines()[0] + ' ...'
            return prop_name, '(%s)' % prop_instance.variable, '=', type(prop_value), prop_value_txt

        rows = [[str(cell) for cell in get_row(self, prop_name)]
                for prop_name in type(self).get_property_names()]
        cols = tuple(zip(*rows))
        col_widths = [max(len(cell) for cell in col) for col in cols]
        formatted_cols = [[cell.ljust(width) for cell in col] for col, width in zip(cols, col_widths)]
        for row in zip(*formatted_cols):
            print('   ', ' '.join(row))

    def assert_no_none_values(self):
        problems = []
        for prop_name in self.get_property_names():
            if getattr(self, prop_name) is None:
                if not getattr(type(self), prop_name).can_be_none:
                    problems.append(prop_name)
        if len(problems) > 0:
            raise Exception('The following properties are None: ' + ', '.join(problems))


class DriverConfig(ConfigSection):

    # Header-comments refer to sections of the ESX/config_esx.nml file.

    ## Start ##
    odir = _StringProperty('esx%odir')
    prefix = _StringProperty('esx%prefix')
    prologue_cmds = _StringProperty('esx%prologue_cmds')
    mode = _EnumProperty('esx%mode', EsxMode)
    units = _EnumProperty('esx%units', EsxUnits)

    dt_extern = _RealProperty('esx%dt_extern')
    dt_phychem = _RealProperty('esx%dt_phychem')

    startdate = _YMDHSProperty('esx%startdate')
    endTime = _RealProperty('esx%endTime')

    ## Output times ##
    printTimes = _StringProperty('esx%printTimes')

    ## Some important options ##
    uses_bcemis = _BoolProperty('esx%uses_bcemis')
    uses_bcVd = _BoolProperty('esx%uses_bcVd')
    uses_bcFb = _BoolProperty('esx%uses_bcFb')
    uses_chem = _BoolProperty('esx%uses_chem')
    uses_mafor = _BoolProperty('esx%uses_mafor')
    uses_dews = _BoolProperty('esx%uses_dews')
    uses_diff = _BoolProperty('esx%uses_diff')
    uses_cpy = _BoolProperty('esx%uses_cpy')
    uses_plotting = _BoolProperty('esx%uses_plotting')

    DataSource = _EnumProperty('esx%DataSource', EsxDataSource)
    DataFile = _StringProperty('esx%DataFile')

    EmisSplitDir = _StringProperty('esx%EmisSplitDir')

    ## z-grid ##
    zgriddefs = _StringProperty('esx%zgriddefs')

    zComp = _RealProperty('esx%zComp')

    ## DiffSpecs ##
    disperse_list = _NamelistProperty('esx%disperse_list')  # FIXME
    DiffSpecs = _TableProperty('esx%DiffSpecs', can_be_none=True)

    ## Diffusion time-step ##
    dt_Zdiff = _RealProperty('esx%dt_Zdiff')

    ## Top boundary ##
    fixedBC = _BoolProperty('esx%fixedBC')

    ## Kz profiles ##
    Kz_method = _StringProperty('esx%Kz_method')

    ## Output species ##
    OutSpecs_list = _TableProperty('esx%OutSpecs_list')  # FIXME

    ## Other output controls ##
    OutputFluxes = _BoolProperty('esx%OutputFluxes')

    ## Plotting ##
    plot_cmds = _StringProperty('esx%plot_cmds', can_be_none=True)

    ## debugging ##
    # FIXME: Convert to enums?
    debug_config = _IntProperty('esx%debug_config')
    debug_driver = _IntProperty('esx%debug_driver')
    debug_Zemis = _IntProperty('esx%debug_Zemis')
    debug_Zdiff = _IntProperty('esx%debug_Zdiff')
    debug_Zchem = _IntProperty('esx%debug_Zchem')
    debug_Kz = _IntProperty('esx%debug_Kz')
    debug_Zmet = _IntProperty('esx%debug_Zmet')
    debug_bics = _IntProperty('esx%debug_bics')
    debug_emis = _IntProperty('esx%debug_emis')
    debug_Zveg = _IntProperty('esx%debug_Zveg')
    debug_cpy = _IntProperty('esx%debug_cpy')
    debug_ddep = _IntProperty('esx%debug_ddep')
    debug_do3se = _IntProperty('esx%debug_do3se')

    ## Conductances and resistance methods ##
    # FIXME: Convert to enums?
    gsto_method = _StringProperty('esx%gsto_method')
    gleaf_method = _StringProperty('esx%gleaf_method')
    gbleaf_method = _StringProperty('esx%gbleaf_method')

    # FIXME: Add "Local data config" ?

    loc_latitude = _FloatProperty('Loc%latitude')
    loc_longitude = _FloatProperty('Loc%longitude')
    loc_ustar = _FloatProperty('Loc%ustar')
    loc_invL = _FloatProperty('Loc%invL')
    loc_rh = _FloatProperty('Loc%rh')
    loc_t2C = _FloatProperty('Loc%t2C')
    loc_psurf = _FloatProperty('Loc%psurf')
    loc_Hmix = _FloatProperty('Loc%Hmix')
    loc_u_ref = _FloatProperty('Loc%u_ref')
    loc_z_ref = _FloatProperty('Loc%z_ref')

    def __init__(self, namelist=None):
        super().__init__(namelist=namelist, default_section='esxDriver_config')


class ChemConfig(ConfigSection):

    BIC = _TableProperty('BIC')

    def __init__(self, namelist=None):
        super().__init__(namelist=namelist, default_section='chem_config')


class VegConfig(ConfigSection):

    Used = _TableProperty('VegUsed')
    DefTypes = _TableProperty('VegDefTypes')
    DefTab = _TableProperty('VegDefTab')
    DefPhenol = _TableProperty('VegDefPhenol')

    emepdo3seDefs = _TableProperty('emepdo3seDefs')

    def __init__(self, namelist=None):
        super().__init__(namelist=namelist, default_section='esxVeg_config')


class Config:

    def __init__(self):
        self.namelist = Namelist()
        self.sections = dict()
        self.driver = self._add_section(DriverConfig)
        self.chem = self._add_section(ChemConfig)
        self.veg = self._add_section(VegConfig)

    def _add_section(self, cls):
        obj = cls()
        self.namelist.sections[obj.namelist.section_marker] = obj.namelist
        self.sections[obj.namelist.section_marker] = obj
        return obj

    def clone(self):
        new_config = Config()
        new_config.namelist.assign_from(self.namelist)
        return new_config

    def read(self, path_or_file):
        self.namelist.read(path_or_file)

    def write(self, path_or_file, no_none=True):
        if no_none:
            self.assert_no_none_values()
        self.namelist.write(path_or_file)

    def assert_no_none_values(self):
        for section in self.sections.values():
            section.assert_no_none_values()

    def info_dump(self):
        for section in self.sections.values():
            section.info_dump()
