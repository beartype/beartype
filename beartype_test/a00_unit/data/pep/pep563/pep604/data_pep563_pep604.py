#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`563` + :pep:`604` **integration data submodule.**

This submodule exercises edge cases when combining :pep:`563` via the standard
``from __future__ import annotations`` pragma with :pep:`604`-compliant unions
known to interact problematically with :pep:`563`.
'''

# ....................{ IMPORTS                            }....................
from __future__ import annotations
from beartype import beartype
from dataclasses import dataclass

# ....................{ CLASSES                            }....................
@beartype
@dataclass()
class SpiritMoreVast(object):
    '''
    Arbitrary :pep:`557`-compliant dataclass subclass that exists solely to be
    referred to below in a :pep:`604`-compliant union.
    '''

    than_thine: str = 'Spirit more vast than thine, frame more attuned'
    '''
    Arbitrary field.
    '''


@beartype
@dataclass()
class FrameMoreAttuned(object):
    '''
    Arbitrary :pep:`557`-compliant dataclass subclass that exists solely to be
    referred to below in a :pep:`604`-compliant union.
    '''

    to_beauty: str = 'To beauty, wasting these surpassing powers'
    '''
    Arbitrary field.
    '''


# from beartype import BeartypeConf
# @beartype(conf=BeartypeConf(is_debug=True))
@beartype
@dataclass()
class WithVoiceFarSweeter(object):
    '''
    :pep:`557`-compliant dataclass subclass defining one or more class variables
    annotated by type hints exercising edge cases in :pep:`563` integration
    implemented by the :func:`beartype.beartype` decorator.
    '''

    # ....................{ FIELDS                         }....................
    than_thy_dying_notes: SpiritMoreVastOrFrameMoreAttuned | None  # = None
    '''
    Arbitrary field annotated by an undefined :pep:`604`-compliant union,
    exercising a well-known edge case in :pep:`563` integration.
    '''

# ....................{ HINTS                              }....................
SpiritMoreVastOrFrameMoreAttuned = SpiritMoreVast | FrameMoreAttuned
'''
Arbitrary :pep:`604`-compliant union referenced by the dataclass defined above.
'''
