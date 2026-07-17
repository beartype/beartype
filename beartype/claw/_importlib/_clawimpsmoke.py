#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype **import hook activation smoke test** (i.e., private empty submodule
isolated to the :mod:`beartype` codebase facilitating a crude smoke test).

This submodule enables the **beartype import path hook adder** (i.e., private
:func:`beartype.claw._importlib.clawimpmain.add_beartype_pathhook` function
responsible for adding the :mod:`beartype`-specific path hook to the standard
:mod:`sys.path_hooks` list) to check validate that that path hook is now
successfully activate rather than unsuccessfully inactive (e.g., due to a
competing third-party package registering a competing import hook ignoring the
:mod:`beartype`-specific path hook added by that adder).

This private submodule is *not* intended for importation by downstream callers.
'''
