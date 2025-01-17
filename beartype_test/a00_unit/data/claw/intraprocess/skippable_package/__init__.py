#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **current package beartype import hook skippable package**
(i.e., data package blacklisted by one or more import hooks published by the
:mod:`beartype.claw` subpackage and thus expected to *not* be type-checked by
the :func:`beartype.beartype` decorator).
'''
