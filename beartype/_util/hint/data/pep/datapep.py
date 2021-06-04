#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2021 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype PEP-compliant type hint globals** (i.e., constant global variables
concerning PEP-compliant type hints).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                           }....................
from beartype._util.hint.data.pep.proposal.datapep484 import (
    HINT_PEP484_SIGNS_DEPRECATED,
    HINT_PEP484_SIGNS_IGNORABLE,
    HINT_PEP484_SIGNS_SEQUENCE_STANDARD,
    HINT_PEP484_SIGNS_SUPPORTED_DEEP,
    HINT_PEP484_SIGNS_SUPPORTED_SHALLOW,
    HINT_PEP484_SIGNS_TUPLE,
    HINT_PEP484_SIGNS_TYPE,
    HINT_PEP484_SIGNS_TYPE_ORIGIN,
)
from beartype._util.hint.data.pep.proposal.datapep544 import (
    HINT_PEP544_SIGNS_IGNORABLE,
    HINT_PEP544_SIGNS_SUPPORTED_DEEP,
)
from beartype._util.hint.data.pep.proposal.datapep585 import (
    HINT_PEP585_SIGNS_SEQUENCE_STANDARD,
    HINT_PEP585_SIGNS_SUPPORTED_DEEP,
    HINT_PEP585_SIGNS_TUPLE,
    HINT_PEP585_SIGNS_TYPE,
)
from beartype._util.hint.data.pep.proposal.datapep586 import (
    HINT_PEP586_SIGNS_SUPPORTED_DEEP)
from beartype._util.hint.data.pep.proposal.datapep593 import (
    HINT_PEP593_SIGNS_SUPPORTED_DEEP)
from beartype._util.lib.utilliboptional import (
    IS_LIB_TYPING_EXTENSIONS)

# See the "beartype.cave" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ MODULES                           }....................
HINT_PEP_MODULE_NAMES = frozenset(
    (
        # Name of the official typing module bundled with the Python stdlib.
        'typing',
    ) + (
        # If the third-party "typing_extensions" module backporting "typing"
        # hints introduced in newer Python versions to older Python versions is
        # importable under the active Python interpreter, a 1-tuple of the name
        # of that module;
        ('typing_extensions',)
        if IS_LIB_TYPING_EXTENSIONS else
        # Else, the empty tuple.
        ()
    )
)
'''
Frozen set of the unqualified names of all top-level **hinting modules** (i.e.,
modules declaring attributes usable for creating PEP-compliant type hints
accepted by both static and runtime type checkers).
'''

# ....................{ SIGNS                             }....................
#FIXME: Rename to "HINT_PEP_ATTRS_DEPRECATED" and likewise for all
#upstream frozen sets used to define this frozen set.
#FIXME: Refactor all usage of this frozen set to test unsubscripted attributes
#rather than signs, whose meaning will now be entirely different.
HINT_PEP_SIGNS_DEPRECATED = (
    HINT_PEP484_SIGNS_DEPRECATED
)
'''
Frozen set of all **deprecated signs** (i.e., arbitrary objects uniquely
identifying outdated PEP-compliant type hints that have since been obsoleted by
more recent PEPs).
'''


#FIXME: Rename to "HINT_PEP_ATTRS_IGNORABLE" and likewise for all
#upstream frozen sets used to define this frozen set.
#FIXME: Refactor all usage of this frozen set to test unsubscripted attributes
#rather than signs, whose meaning will now be entirely different.
HINT_PEP_SIGNS_IGNORABLE = (
    HINT_PEP484_SIGNS_IGNORABLE |
    HINT_PEP544_SIGNS_IGNORABLE
)
'''
Frozen set of all **ignorable signs** (i.e., arbitrary objects uniquely
identifying PEP-compliant type hints unconditionally ignored by the
:func:`beartype.beartype` decorator).

See Also
----------
:attr:`beartype._util.hint.data.datahint.HINTS_IGNORABLE_SHALLOW`
    Further commentary.
'''

# ....................{ SIGNS ~ category                  }....................
#FIXME: Shift this frozen set into a new
#"beartype._util.hint.data.pep.sign.datapepsignset" submodule. Note that the
#name of this frozen set should remain the same.
#FIXME: Remove "HINT_PEP484_SIGNS_SEQUENCE_STANDARD" and
#"HINT_PEP585_SIGNS_SEQUENCE_STANDARD" entirely.
HINT_PEP_SIGNS_SEQUENCE_STANDARD = (
    HINT_PEP484_SIGNS_SEQUENCE_STANDARD |
    HINT_PEP585_SIGNS_SEQUENCE_STANDARD
)
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


#FIXME: Shift this frozen set into a new
#"beartype._util.hint.data.pep.sign.datapepsignset" submodule. Note that the
#name of this frozen set should remain the same.
#FIXME: Remove "HINT_PEP484_SIGNS_TUPLE" and "HINT_PEP585_SIGNS_TUPLE"
#entirely.
HINT_PEP_SIGNS_TUPLE = (
    HINT_PEP484_SIGNS_TUPLE |
    HINT_PEP585_SIGNS_TUPLE
)
'''
Frozen set of all **tuple signs** (i.e., arbitrary objects uniquely identifying
PEP-compliant type hints accepting exactly one subscripted type hint argument
constraining *all* items of compliant tuples).
'''

# ....................{ SIGNS ~ supported                 }....................
#FIXME: Shift this frozen set into a new
#"beartype._util.hint.data.pep.sign.datapepsignset" submodule. Note that the
#name of this frozen set should remain the same.
#FIXME: Remove "HINT_PEP484_SIGNS_SUPPORTED_SHALLOW" entirely.
_HINT_PEP_SIGNS_SUPPORTED_SHALLOW = (
    HINT_PEP484_SIGNS_SUPPORTED_SHALLOW
)
'''
Frozen set of all **shallowly supported non-originative signs** (i.e.,
arbitrary objects uniquely identifying PEP-compliant type hints *not*
originating from a non-:mod:`typing` origin type for which the
:func:`beartype.beartype` decorator generates shallow type-checking code).
'''


#FIXME: Shift this frozen set into a new
#"beartype._util.hint.data.pep.sign.datapepsignset" submodule. Note that the
#name of this frozen set should remain the same.
#FIXME: Remove all upstream sets entirely.
HINT_PEP_SIGNS_SUPPORTED_DEEP = (
    HINT_PEP484_SIGNS_SUPPORTED_DEEP |
    HINT_PEP544_SIGNS_SUPPORTED_DEEP |
    HINT_PEP585_SIGNS_SUPPORTED_DEEP |
    HINT_PEP586_SIGNS_SUPPORTED_DEEP |
    HINT_PEP593_SIGNS_SUPPORTED_DEEP
)
'''
Frozen set of all **deeply supported signs** (i.e., arbitrary objects uniquely
identifying PEP-compliant type hints for which the :func:`beartype.beartype`
decorator generates deeply type-checking code).

This set contains *every* sign explicitly supported by one or more conditional
branches in the body of the
:func:`beartype._decor._code._pep._pephint.pep_code_check_hint` function
generating code deeply type-checking the current pith against the PEP-compliant
type hint annotated by a subscription of that attribute.
'''

# ....................{ SIGNS ~ type                      }....................
#FIXME: Unclear whether this is actually useful anymore. Signs no longer have
#anything whatsoever to do with "typing" attributes. Ergo, by definition, there
#are *NO* such things as "instanceable class signs." Fortunately, this is only
#ever used in one place throughout the codebase: naturally, in a single test in
#get_hint_pep_sign(). Given that, let's initially try just commenting this out
#entirely both here and in get_hint_pep_sign(). That will probably cause test
#failures under Python 3.6, but we can do with that when we get that far. :p
HINT_PEP_SIGNS_TYPE = (
    HINT_PEP484_SIGNS_TYPE |
    HINT_PEP585_SIGNS_TYPE
)
'''
Frozen set of all **isinstanceable class signs** (i.e., classes uniquely
identifying PEP-compliant type hints that are also passable as the second
argument to the :func:`isinstance` builtin).
'''


#FIXME: Shift this frozen set into a new
#"beartype._util.hint.data.pep.sign.datapepsignset" submodule. Note that the
#name of this frozen set should remain the same.
#FIXME: Remove all upstream sets entirely.
HINT_PEP_SIGNS_TYPE_ORIGIN_STDLIB = (
    HINT_PEP484_SIGNS_TYPE_ORIGIN |
    # Since all PEP 585-compliant type hints originate from an origin type, the
    # set of all PEP 585-compliant standard class signs also doubles as the
    # set of all PEP 585-compliant original class signs.
    HINT_PEP585_SIGNS_TYPE
)
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

# ....................{ SIGNS ~ supported : all           }....................
#FIXME: Shift this frozen set into a new
#"beartype._util.hint.data.pep.sign.datapepsignset" submodule. Note that the
#name of this frozen set should remain the same.
HINT_PEP_SIGNS_SUPPORTED = (
    # Set of all deeply supported signs.
    HINT_PEP_SIGNS_SUPPORTED_DEEP |
    # Set of all shallowly supported signs *NOT* originating from a
    # non-"typing" origin type.
    _HINT_PEP_SIGNS_SUPPORTED_SHALLOW |
    # Set of all shallowly supported signs originating from a non-"typing"
    # origin type.
    HINT_PEP_SIGNS_TYPE_ORIGIN_STDLIB
)
'''
Frozen set of all **supported signs** (i.e., arbitrary objects uniquely
identifying PEP-compliant type hints).
'''
