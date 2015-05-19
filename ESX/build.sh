#!/bin/bash

python3 ./scripts/gen-makefile.py \
	-p "esx_src;esx_src/DO3SE/src;esx_src/MAFOR/src" \
	-i iso_fortran_env \
	-f90 "gfortran -pedantic -Wall -fbounds-check -fdefault-real-8 -finit-real=nan -ffree-line-length-none" \
	-b build \
	-o "./esx" \
	esx_src/esx_tester.f90

make

