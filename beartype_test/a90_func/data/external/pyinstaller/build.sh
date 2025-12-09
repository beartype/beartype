#!/usr/bin/env sh
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

echo 'Building PyInstaller-driven "death_and_darkness" CLI app...'
command pyinstaller --noconfirm --onefile death_and_darkness.py
