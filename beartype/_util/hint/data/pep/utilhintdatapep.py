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
    utilhintdatapep484,
    utilhintdatapep544,
    utilhintdatapep593,
)

# See the "beartype.__init__" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ SIGNS                             }....................
HINT_PEP_SIGNS_IGNORABLE = set()
'''
Frozen set of all **ignorable signs** (i.e., arbitrary objects uniquely
identifying PEP-compliant type hints unconditionally ignored by the
:func:`beartype.beartype` decorator).

This set is intended to be tested against typing attributes returned by the
:func:`get_hint_pep_sign` getter function.

See Also
----------
:attr:`beartype._util.hint.data.utilhintdata.HINTS_IGNORABLE_SHALLOW`
    Further commentary.
'''


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
PEP-compliant type hints subscripting unsubscripted typing attributes listed in
this dictionary are shallowly type-checkable from wrapper functions generated
by the :func:`beartype.beartype` decorator.
'''

# ....................{ SETS ~ supported                  }....................
# Initialized by the _init() function below.
HINT_PEP_SIGNS_SUPPORTED = None
'''
Frozen set of all **supported signs** (i.e., arbitrary objects uniquely
identifying PEP-compliant type hints).

This set is intended to be tested against typing attributes returned by the
:func:`get_hint_pep_sign` getter function.
'''


# Initialized by the _init() function below.
HINT_PEP_SIGNS_SUPPORTED_DEEP = set()
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
HINT_PEP_SIGNS_SUPPORTED_SHALLOW = set()
'''
Frozen set of all **shallowly supported non-originative signs** (i.e.,
arbitrary objects uniquely identifying PEP-compliant type hints *not*
originating from a non-:mod:`typing` origin type for which the
:func:`beartype.beartype` decorator generates shallow type-checking code).

This set is intended to be tested against typing attributes returned by the
:func:`get_hint_pep_sign` getter function.
'''

# ....................{ SETS ~ subtype                    }....................
# Fully initialized by the _init() function below.
HINT_PEP_BASES_FORWARDREF = set()
'''
Tuple of all **PEP-compliant forward reference type hint superclasses** (i.e.,
superclasses such that all PEP-compliant type hints forward referencing
user-defined types are instances of these superclasses).
'''


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

# ....................{ INITIALIZERS                      }....................
def add_data(data_module: 'ModuleType') -> None:
    '''
    Add PEP-compliant type hint data to various global containers declared by
    the passed module.

    Parameters
    ----------
    data_module : ModuleType
        Module to be added to.
    '''

    # Submodule globals to be redefined below.
    global \
        HINT_PEP_BASES_FORWARDREF, \
        HINT_PEP_SIGNS_SUPPORTED_DEEP, \
        HINT_PEP_SIGNS_SUPPORTED_SHALLOW, \
        HINT_PEP_SIGNS_IGNORABLE, \
        HINT_PEP_SIGNS_SEQUENCE_STANDARD, \
        HINT_PEP_SIGNS_SUPPORTED, \
        HINT_PEP_SIGNS_TYPE_ORIGIN

    # Current submodule, obtained via the standard idiom. See also:
    #     https://stackoverflow.com/a/1676860/2809027
    CURRENT_SUBMODULE = sys.modules[__name__]

    # Tuple of all private submodules of this subpackage to be initialized.
    HINT_DATA_PEP_SUBMODULES = (
        utilhintdatapep484,
        utilhintdatapep544,
        utilhintdatapep593,
    )

    # Initialize all private submodules of this subpackage.
    for hint_data_pep_submodule in HINT_DATA_PEP_SUBMODULES:
        hint_data_pep_submodule.add_data(CURRENT_SUBMODULE)

    # Assert these global to have been initialized by these private submodules.
    assert HINT_PEP_BASES_FORWARDREF, (
        'Set global "HINT_BASES_FORWARDREF" empty.')
    assert HINT_PEP_SIGNS_SUPPORTED_DEEP, (
        'Set global "HINT_PEP_SIGNS_SUPPORTED_DEEP" empty.')
    assert HINT_PEP_SIGNS_SUPPORTED_SHALLOW, (
        'Set global "HINT_PEP_SIGNS_SUPPORTED_SHALLOW" empty.')
    assert HINT_PEP_SIGNS_IGNORABLE, (
        'Set global "HINT_PEP_SIGNS_IGNORABLE" empty.')
    assert HINT_PEP_SIGNS_SEQUENCE_STANDARD, (
        'Set global "HINT_PEP_SIGNS_SEQUENCE_STANDARD" empty.')
    assert HINT_PEP_SIGNS_TYPE_ORIGIN, (
        'Set global "HINT_PEP_SIGNS_TYPE_ORIGIN" empty.')

    # Tuples defined *AFTER* initializing these private submodules and
    # thus the lower-level globals required by these tuples.
    HINT_PEP_BASES_FORWARDREF = tuple(HINT_PEP_BASES_FORWARDREF)

    # Frozen sets defined *AFTER* initializing these private submodules and
    # thus the lower-level globals required by these sets.
    HINT_PEP_SIGNS_SUPPORTED_DEEP = frozenset(HINT_PEP_SIGNS_SUPPORTED_DEEP)
    HINT_PEP_SIGNS_SUPPORTED_SHALLOW = frozenset(
        HINT_PEP_SIGNS_SUPPORTED_SHALLOW)
    HINT_PEP_SIGNS_IGNORABLE = frozenset(HINT_PEP_SIGNS_IGNORABLE)
    HINT_PEP_SIGNS_SEQUENCE_STANDARD = frozenset(
        HINT_PEP_SIGNS_SEQUENCE_STANDARD)
    HINT_PEP_SIGNS_TYPE_ORIGIN = frozenset(HINT_PEP_SIGNS_TYPE_ORIGIN)
    HINT_PEP_SIGNS_SUPPORTED = frozenset(
        # Set of all deeply supported signs.
        HINT_PEP_SIGNS_SUPPORTED_DEEP |
        # Set of all shallowly supported signs *NOT* originating from a
        # non-"typing" origin type.
        HINT_PEP_SIGNS_SUPPORTED_SHALLOW |
        # Set of all shallowly supported signs originating from a non-"typing"
        # origin type.
        HINT_PEP_SIGNS_TYPE_ORIGIN
    )

    # Add PEP-compliant type hint data to various global containers declared by
    # the passed module.
    data_module.HINT_BASES_FORWARDREF.update(HINT_PEP_BASES_FORWARDREF)
    data_module.HINTS_IGNORABLE_SHALLOW.update(HINT_PEP_SIGNS_IGNORABLE)
