#!/usr/bin/env sh
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.
#
# --------------------( SYNOPSIS                           )--------------------
# PyInstaller build shell script, (re)building both the root
# "death_and_darkness.py" script *AND* dependent "the_blaze" package imported by
# that script into a single platform-specific binary file.
#
# This script is only intended to be run manually from the command-line as a
# developer-friendly debugging aid. This script is *NOT* automatically run by
# the PyInstaller integration test validating this build functionality, which
# instead directly runs a "pyinstaller" subprocess with the requisite arguments.

# ....................{ MAIN                               }....................
echo 'Building PyInstaller-driven "death_and_darkness" CLI app...'
command pyinstaller --noconfirm --onefile death_and_darkness.py
