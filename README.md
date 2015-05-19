# EStraX

This repository contains python code to use the ESX atmospheric model, as well
as code to manage atmospheric data, compute trajectories and plot results.

For the ESX model code please contact David Simpson at Chalmers.

## Files

 * README.md - This readme.
 * ESX/ - Contains build script and is where we placed the ESX code.
 * pyesx/ - Python package for working with ESX.
 * plotting/ - Python package with helpers for plotting lat/lon data.
 * ecmwf/ - Python package for accessing ECMWF netCDF data files.
 * trajlib/ - Python package for computing trajectories.

## Requirements

### ESX
 * perl
 * python2
 * make
 * gfortran

### EStraX modules
 * libnetcdf
 * python3
    - numpy
    - matplotlib
	- pyproj
    - netCDF4

Python version 3.4+ is preferred and what is tested against, but the code could likely
work with older versions given that at least the enum34 package is installed.

### HYSPLIT
 * GRIB
 * netCDF3

Note that HYSPLIT requires an older version of netCDF which may conflict with other versions
and libraries installed. The recommended action if HYSPLIT is to be used is to install the older
version of netCDF, build HYSPLIT and then remove the older netCDF version and install the up
to date version.

## Setup (rudimentary, not quite tested)

### Linux
Use the system package manager to install the prerequisites:
 - perl
 - gfortran
 - python & python3
    - numpy
    - matplotlib
    - pyproj
    - netCDF4

### MinGW
 - Install MinGW. Make sure to include gfortran.
 - Add MinGW/bin and MinGW/msys/1.0/bin folders to the system PATH.
 - Install python (version 2 and/or 3, preferably both) for Windows (not MinGW).
 - From a MinGW terminal (e.g. bash), create a symlink from the windows python 2 executable to /bin/python.exe.
 - Do the same for the python 3 executable to /bin/python3.exe.
 - Optional, but useful:
     - Do the same for the python 2 pip executable to /bin/pip.exe.
     - And for the python 3 pip executable to /bin/pip3.exe.
 - Install numpy by
     - Download the correct wheel(s) from http://www.lfd.uci.edu/~gohlke/pythonlibs/#numpy.
     - Execute pip/pip3 and give them the downloaded wheel(s).
     - This same method can be used to install netCDF4 from the same website.
 - Use pip/pip3 to install matplotlib.
 - If necessary use pip/pip3 to install enum34.

### Cygwin
 - Install Cygwin. Make sure to include gfortran, python (and preferrably python3) and netCDF libraries.
 - At the moment Cygwin does not include setuptools or pip for python3 so this needs a manual install:
     - Download ez_setup.py from https://bootstrap.pypa.io/ez_setup.py
     - Run python3 ez_setup.py to install setuptools etc. for python3.
     - Run easy_install-3.2 pip to install pip for python3.
     - Use pip3 to install required packages (numpy, matplotlib, netCDF4 and possibly enum34).

## Building ESX

The first step would be to aquire the ESX source code from David Simpson at Chalmers.

The easiest way to build ESX is to enter the ESX directory of this repository and run the build.sh shell script
present in this repository. This will run the script ESX/scripts/gen-makefile.py to create a Makefile in the ESX directory.
It will then invoke make to run this Makefile. This will produce build output in the directory ESX/build and, if
successful, create an executable named esx which is the ESX model executable.


