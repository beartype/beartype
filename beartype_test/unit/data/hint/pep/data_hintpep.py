#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright 2014-2020 by Cecil Curry.
# See "LICENSE" for further details.

'''
**Beartype PEP-compliant type hints test data.**

This submodule predefines low-level global constants whose values are
PEP-compliant type hints, exercising known edge cases on behalf of higher-level
unit test submodules.
'''

# ....................{ IMPORTS                           }....................
import sys
from beartype._util.utilobject import is_object_hashable
from beartype_test.unit.data.hint.data_hintmeta import PepHintMetadata
from beartype_test.unit.data.hint.pep.proposal import (
    data_hintpep484,
    _data_hintpep544,
    _data_hintpep585,
    _data_hintpep593,
)

# ....................{ SETS                              }....................
# Initialized by the _init() function below.
HINTS_PEP_HASHABLE = None
'''
Frozen set of **hashable PEP-compliant non-class type hints** (i.e.,
PEP-compliant type hints that are *not* classes but *are* accepted by the
builtin :func:`hash` function *without* raising an exception and thus usable in
hash-based containers like dictionaries and sets).

Hashable PEP-compliant class type hints (e.g., generics, protocols) are largely
indistinguishable from PEP-noncompliant class type hints and thus useless for
testing purposes.
'''


# Initialized by the _init() function below.
HINTS_PEP_IGNORABLE_DEEP = set()
'''
Frozen set of **deeply ignorable PEP-compliant type hints** (i.e.,
PEP-compliant type hints that are *not* shallowly ignorable and thus *not* in
the low-level
:attr:`beartype._util.hint.data.utilhintdata.HINTS_IGNORABLE_SHALLOW` set, but
which are nonetheless ignorable and thus require dynamic testing by the
high-level :func:`beartype._util.hint.utilhinttest.is_hint_ignorable` tester
function to demonstrate this fact).
'''


# Initialized by the _init() function below.
HINTS_PEP_INVALID_CLASS_NONGENERIC = set()
'''
Frozen set of **invalid non-generic classes** (i.e., classes declared by the
:mod:`typing` module used to instantiate PEP-compliant type hints but
themselves invalid as PEP-compliant type hints).
'''

# ....................{ TUPLES                            }....................
# Initialized by the _init() function below.
HINTS_PEP_META = []
'''
Tuple of **PEP-compliant type hint metadata** (i.e., :class:`PepHintMetadata`
instances describing test-specific PEP-compliant type hints with metadata
leveraged by various testing scenarios).

Design
----------
This tuple was initially designed as a dictionary mapping from PEP-compliant
type hints to :class:`PepHintMetadata` instances describing those hints, until
:mod:`beartype` added support for PEPs enabling unhashable PEP-compliant type
hints (e.g., ``collections.abc.Callable[[], str]`` under `PEP 585`_)
impermissible for use as dictionary keys or set members.

.. _PEP 585:
    https://www.python.org/dev/peps/pep-0585
'''

# ....................{ INITIALIZERS                      }....................
def _init() -> None:
    '''
    Initialize this submodule.
    '''

    # Submodule globals to be redefined below.
    global \
        HINTS_PEP_HASHABLE, \
        HINTS_PEP_IGNORABLE_DEEP, \
        HINTS_PEP_INVALID_CLASS_NONGENERIC, \
        HINTS_PEP_META

    # Current submodule, obtained via the standard idiom. See also:
    #     https://stackoverflow.com/a/1676860/2809027
    CURRENT_SUBMODULE = sys.modules[__name__]

    # Tuple of all private submodules of this subpackage to be initialized.
    DATA_HINT_PEP_SUBMODULES = (
        data_hintpep484,
        _data_hintpep544,
        _data_hintpep585,
        _data_hintpep593,
    )

    # Initialize all private submodules of this subpackage.
    for data_hint_pep_submodule in DATA_HINT_PEP_SUBMODULES:
        data_hint_pep_submodule.add_data(CURRENT_SUBMODULE)

    # Assert these global to have been initialized by these private submodules.
    assert HINTS_PEP_IGNORABLE_DEEP, (
        'Set global "HINTS_PEP_IGNORABLE_DEEP" empty.')
    assert HINTS_PEP_INVALID_CLASS_NONGENERIC, (
        'Set global "HINTS_PEP_INVALID_CLASS_NONGENERIC" empty.')
    assert HINTS_PEP_META, 'Tuple global "HINTS_PEP_META" empty.'

    # Assert this global to contain only instances of its expected dataclass.
    assert (
        isinstance(hint_pep_meta, PepHintMetadata)
        for hint_pep_meta in HINTS_PEP_META
    ), f'{repr(HINTS_PEP_META)} not iterable of "PepHintMetadata" instances.'

    # Frozen sets defined *AFTER* initializing these private submodules and
    # thus the lower-level globals required by these sets.
    HINTS_PEP_HASHABLE = frozenset(
        hint_pep_meta.hint
        for hint_pep_meta in HINTS_PEP_META
        if (
            # not isinstance(hint_pep_meta.hint, type) and
            is_object_hashable(hint_pep_meta.hint)
        )
    )
    HINTS_PEP_IGNORABLE_DEEP = frozenset(HINTS_PEP_IGNORABLE_DEEP)
    HINTS_PEP_INVALID_CLASS_NONGENERIC = frozenset(
        HINTS_PEP_INVALID_CLASS_NONGENERIC)
    HINTS_PEP_META = tuple(HINTS_PEP_META)


# Initialize this submodule.
_init()
