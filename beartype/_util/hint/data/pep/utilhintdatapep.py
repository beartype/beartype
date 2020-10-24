#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2020 Cecil Curry.
# See "LICENSE" for further details.

'''
**Beartype PEP-compliant type hint globals** (i.e., constant global variables
concerning PEP-compliant type hints).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                           }....................
import sys
from beartype._util.hint.data.pep.proposal import (
    _utilhintdatapep484,
    _utilhintdatapep544,
    _utilhintdatapep593,
)
from typing import Any

# See the "beartype.__init__" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ MAPPINGS ~ origin                 }....................
# Initialized by the _init() function below.
HINT_PEP_SIGNS_TYPE_ORIGIN = set()
'''
Frozen set of all **signs** (i.e., arbitrary objects) uniquely identifying
PEP-compliant type hints originating from an **origin type** (i.e.,
non-:mod:`typing` class such that *all* objects satisfying this hint are
instances of this class).

Since any arbitrary object is trivially type-checkable against an
:func:`isinstance`-able class by passing that object and class to the
:func:`isinstance` builtin, *all* parameters and return values annotated by
PEP-compliant type hints subscripting argumentless typing attributes listed in
this dictionary are shallowly type-checkable from wrapper functions generated
by the :func:`beartype.beartype` decorator.
'''

# ....................{ SETS                              }....................
# Initialized by the _init() function below.
HINT_PEP_SIGNS_DEEP_SUPPORTED = set()
'''
Frozen set of all **deeply supported signs** (i.e., arbitrary objects uniquely
identifying PEP-compliant type hints for which the :func:`beartype.beartype`
decorator generates deeply type-checking code).

This set contains *every* sign explicitly supported by one or more conditional
branches in the body of the
:func:`beartype._decor._code._pep._pephint.pep_code_check_hint` function
generating code deeply type-checking the current pith against the PEP-compliant
type hint annotated by a subscription of that attribute.

This set is intended to be tested against typing attributes returned by the
:func:`get_hint_pep_sign` getter function.
'''


# Initialized by the _init() function below.
HINT_PEP_SIGNS_SUPPORTED = None
'''
Frozen set of all **supported signs** (i.e., arbitrary objects uniquely
identifying PEP-compliant type hints).

This set is intended to be tested against typing attributes returned by the
:func:`get_hint_pep_sign` getter function.
'''

# ....................{ SETS ~ subtype                    }....................
# Initialized by the _init() function below.
HINT_PEP_SIGNS_SEQUENCE_STANDARD = set()
'''
Frozen set of all **standard sequence signs** (i.e., arbitrary objects uniquely
identifying PEP-compliant type hints accepting exactly one subscripted type
hint argument constraining *all* items of compliant sequences, which
necessarily satisfy the :class:`collections.abc.Sequence` protocol with
guaranteed ``O(1)`` indexation across all sequence items).

This set intentionally excludes the:

* :attr:`typing.AnyStr` sign, which accepts only the :class:`str` and
  :class:`bytes` types as its sole subscripted argument, which does *not*
  unconditionally constrain *all* items (i.e., unencoded and encoded characters
  respectively) of compliant sequences but instead parametrizes this attribute.
* :attr:`typing.ByteString` sign, which accepts *no* subscripted arguments.
  :attr:`typing.ByteString` is simply an alias for the
  :class:`collections.abc.ByteString` abstract base class (ABC) and thus
  already handled by our fallback logic for supported PEP-compliant type hints.
* :attr:`typing.Deque` sign, whose compliant objects (i.e.,
  :class:`collections.deque` instances) only `guarantee O(n) indexation across
  all sequence items <collections.deque_>`__:

     Indexed access is ``O(1)`` at both ends but slows to ``O(n)`` in the
     middle. For fast random access, use lists instead.

* :attr:`typing.NamedTuple` sign, which embeds a variadic number of
  PEP-compliant field type hints and thus requires special-cased handling.
* :attr:`typing.Text` sign, which accepts *no* subscripted arguments.
  :attr:`typing.Text` is simply an alias for the builtin :class:`str` type and
  thus handled elsewhere as a PEP-noncompliant type hint.
* :attr:`typing.Tuple` sign, which accepts a variadic number of subscripted
  arguments and thus requires special-cased handling.

.. _collections.deque:
   https://docs.python.org/3/library/collections.html#collections.deque
'''


# Initialized by the _init() function below.
HINT_PEP_SIGNS_UNION = set()
'''
Frozen set of all **union signs** (i.e., arbitrary objects uniquely identifying
PEP-compliant type hints unifying one or more subscripted type hint arguments
into a disjunctive set union of these arguments).

If the active Python interpreter targets:

* At least Python 3.9.0, the :attr:`typing.Optional` and
  :attr:`typing.Union` attributes are distinct.
* Less than Python 3.9.0, the :attr:`typing.Optional` attribute reduces to the
  :attr:`typing.Union` attribute, in which case this set is technically
  semantically redundant. Since tests of both object identity and set
  membership are ``O(1)``, this set incurs no significant performance penalty
  versus direct usage of the :attr:`typing.Union` attribute and is thus
  unconditionally used as is irrespective of Python version.
'''

# ....................{ INITIALIZERS                      }....................
def _init() -> None:
    '''
    Initialize this submodule.
    '''

    # Submodule globals to be redefined below.
    global \
        HINT_PEP_SIGNS_TYPE_ORIGIN, \
        HINT_PEP_SIGNS_DEEP_SUPPORTED, \
        HINT_PEP_SIGNS_SUPPORTED, \
        HINT_PEP_SIGNS_SEQUENCE_STANDARD, \
        HINT_PEP_SIGNS_UNION

    # Current submodule, obtained via the standard idiom. See also:
    #     https://stackoverflow.com/a/1676860/2809027
    CURRENT_SUBMODULE = sys.modules[__name__]

    # Tuple of all private submodules of this subpackage to be initialized.
    HINT_DATA_PEP_SUBMODULES = (
        _utilhintdatapep484,
        _utilhintdatapep544,
        _utilhintdatapep593,
    )

    # Initialize all private submodules of this subpackage.
    for hint_data_pep_submodule in HINT_DATA_PEP_SUBMODULES:
        hint_data_pep_submodule.add_data(CURRENT_SUBMODULE)

    # Assert these global to have been initialized by these private submodules.
    assert HINT_PEP_SIGNS_TYPE_ORIGIN, (
        'Set global "HINT_PEP_SIGNS_TYPE_ORIGIN" empty.')
    assert HINT_PEP_SIGNS_DEEP_SUPPORTED, (
        'Set global "HINT_PEP_SIGNS_DEEP_SUPPORTED" empty.')
    assert HINT_PEP_SIGNS_SEQUENCE_STANDARD, (
        'Set global "HINT_PEP_SIGNS_SEQUENCE_STANDARD" empty.')
    assert HINT_PEP_SIGNS_UNION, 'Set global "HINT_PEP_SIGNS_UNION" empty.'

    # Frozen sets defined *AFTER* initializing these private submodules and
    # thus the lower-level globals required by these sets.
    HINT_PEP_SIGNS_TYPE_ORIGIN = frozenset(HINT_PEP_SIGNS_TYPE_ORIGIN)
    HINT_PEP_SIGNS_DEEP_SUPPORTED = frozenset(HINT_PEP_SIGNS_DEEP_SUPPORTED)
    HINT_PEP_SIGNS_SEQUENCE_STANDARD = frozenset(
        HINT_PEP_SIGNS_SEQUENCE_STANDARD)
    HINT_PEP_SIGNS_UNION = frozenset(HINT_PEP_SIGNS_UNION)
    HINT_PEP_SIGNS_SUPPORTED = frozenset(
        # Set of all deeply supported signs.
        HINT_PEP_SIGNS_DEEP_SUPPORTED |
        # Set of all shallowly supported signs originating from a non-"typing"
        # origin type.
        HINT_PEP_SIGNS_TYPE_ORIGIN |
        # Set of all shallowly supported signs *NOT* originating from a
        # non-"typing" origin type.
        set((Any,))
    )


# Initialize this submodule.
_init()
