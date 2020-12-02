#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright 2014-2020 by Cecil Curry.
# See "LICENSE" for further details.

'''
**Beartype** `PEP 484`_**-compliant PEP-noncompliant type hint test data.**

`PEP 484`_-compliant type hints *mostly* indistinguishable from
PEP-noncompliant type hints include:

* :func:`typing.NamedTuple`, a high-level factory function deferring to the
    lower-level :func:`collections.namedtuple` factory function creating and
    returning :class:`tuple` instances annotated by PEP-compliant type hints.
* :func:`typing.TypedDict`, a high-level factory function creating and
    returning :class:`dict` instances annotated by PEP-compliant type hints.

.. _PEP 484:
    https://www.python.org/dev/peps/pep-0484
'''

# ....................{ IMPORTS                           }....................
from beartype_test.unit.data.hint.data_hintmeta import (
    NonPepHintMetadata,
    PepHintPithSatisfiedMetadata,
    PepHintPithUnsatisfiedMetadata,
)
from typing import (
    NamedTuple,
)

# ....................{ COLLECTIONS                       }....................
NamedTupleType = NamedTuple(
    'NamedTupleType', [('fumarole', str), ('enrolled', int)])
'''
PEP-compliant user-defined :func:`collections.namedtuple` instance typed with
PEP-compliant annotations.
'''

# ....................{ ADDERS                            }....................
def add_data(data_module: 'ModuleType') -> None:
    '''
    Add `PEP 484`_**-compliant PEP-noncompliant type hint test data to various
    global containers declared by the passed module.

    Parameters
    ----------
    data_module : ModuleType
        Module to be added to.

    .. _PEP 484:
        https://www.python.org/dev/peps/pep-0484
    '''

    # ..................{ TUPLES                            }..................
    # Add PEP 484-specific PEP-noncompliant test type hints to this dictionary
    # global.
    data_module.HINTS_NONPEP_META.extend((
        # ................{ NAMEDTUPLE                        }................
        # "NamedTuple" instances transparently reduce to standard tuples and
        # *MUST* thus be handled as non-"typing" type hints.
        NonPepHintMetadata(
            hint=NamedTupleType,
            piths_satisfied_meta=(
                # Named tuple containing correctly typed items.
                PepHintPithSatisfiedMetadata(
                    NamedTupleType(fumarole='Leviathan', enrolled=37)),
            ),
            piths_unsatisfied_meta=(
                # String constant.
                PepHintPithUnsatisfiedMetadata('Of ͼarthen concordance that'),

                #FIXME: Uncomment after implementing "NamedTuple" support.
                # # Named tuple containing incorrectly typed items.
                # PepHintPithUnsatisfiedMetadata(
                #     pith=NamedTupleType(fumarole='Leviathan', enrolled=37),
                #     # Match that the exception message raised for this object...
                #     exception_str_match_regexes=(
                #         # Declares the name of this tuple's problematic item.
                #         r'\s[Ll]ist item 0\s',
                #     ),
                # ),
            ),
        ),

        # ................{ COLLECTIONS ~ typeddict           }................
        # "TypedDict" instances transparently reduce to dicts.
        #FIXME: Implement us up, but note when doing so that "TypeDict" was first
        #introduced with Python 3.8.
    ))
