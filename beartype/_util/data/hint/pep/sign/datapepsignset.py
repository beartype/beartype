#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2021 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **PEP-compliant type hint sign sets** (i.e., frozen set globals
aggregating instances of the
:class:`beartype._util.data.hint.pep.sign.datapepsigncls.HintSign` class,
enabling efficient categorization of signs as belonging to various categories
of PEP-compliant type hints).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ TODO                              }....................
#FIXME: Remove the following obsolete upstream frozen sets:
#* HINT_PEP484_SIGNS_SEQUENCE_STANDARD.
#* HINT_PEP484_SIGNS_TUPLE.
#* HINT_PEP484_SIGNS_SUPPORTED_SHALLOW.
#* HINT_PEP484_SIGNS_SUPPORTED_DEEP.
#* HINT_PEP484_SIGNS_TYPE.
#* HINT_PEP484_SIGNS_TYPE_ORIGIN.
#* HINT_PEP544_SIGNS_SUPPORTED_DEEP.
#* HINT_PEP585_SIGNS_SEQUENCE_STANDARD.
#* HINT_PEP585_SIGNS_TUPLE.
#* HINT_PEP585_SIGNS_SUPPORTED_DEEP.
#* HINT_PEP585_SIGNS_TYPE.
#* HINT_PEP586_SIGNS_SUPPORTED_DEEP.
#* HINT_PEP593_SIGNS_SUPPORTED_DEEP.
#FIXME: Excise up "HINT_SIGNS_TUPLE", which has been temporarily preserved only
#to simplify the initial refactoring and should be replaced everywhere with
#direct access of the now singular "HintSignTuple" sign.

# ....................{ IMPORTS                           }....................
from beartype._cave._cavefast import NoneType
from beartype._util.data.hint.pep.sign.datapepsigns import (
    HintSignAbstractSet,
    HintSignAnnotated,
    HintSignAny,
    HintSignAsyncContextManager,
    HintSignAsyncGenerator,
    HintSignAsyncIterator,
    HintSignAsyncIterable,
    HintSignAwaitable,
    HintSignByteString,
    HintSignCallable,
    HintSignChainMap,
    HintSignCollection,
    HintSignContainer,
    HintSignContextManager,
    HintSignCoroutine,
    HintSignCounter,
    HintSignDefaultDict,
    HintSignDeque,
    HintSignDict,
    HintSignForwardRef,
    HintSignFrozenSet,
    HintSignGenerator,
    HintSignGeneric,
    HintSignItemsView,
    HintSignIterable,
    HintSignIterator,
    HintSignKeysView,
    HintSignList,
    HintSignLiteral,
    HintSignMapping,
    HintSignMappingView,
    HintSignMatch,
    HintSignMutableMapping,
    HintSignMutableSequence,
    HintSignMutableSet,
    HintSignNewType,
    HintSignOptional,
    HintSignOrderedDict,
    HintSignPattern,
    HintSignProtocol,
    HintSignReversible,
    HintSignSequence,
    HintSignSet,
    HintSignTuple,
    HintSignType,
    HintSignTypeVar,
    HintSignUnion,
    HintSignValuesView,
)

# See the "beartype.cave" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ SETS ~ sequence                   }....................
HINT_SIGNS_SEQUENCE_STANDARD = frozenset((
    HintSignByteString,
    HintSignList,
    HintSignMutableSequence,
    HintSignSequence,
))
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


HINT_SIGNS_TUPLE = frozenset((HintSignTuple,))
'''
Frozen set of all **tuple signs** (i.e., arbitrary objects uniquely identifying
PEP-compliant type hints accepting exactly one subscripted type hint argument
constraining *all* items of compliant tuples).
'''

# ....................{ SETS ~ supported                  }....................
_HINT_SIGNS_SUPPORTED_SHALLOW = frozenset((
    # Note that the "NoReturn" type hint is invalid in almost all possible
    # syntactic contexts and thus intentionally omitted here. See the
    # "datapepsigns" submodule for further commentary.
    HintSignAny,
    HintSignForwardRef,
    HintSignNewType,
    HintSignTypeVar,

    # PEP 484 explicitly supports the "None" singleton: i.e.,
    #     When used in a type hint, the expression None is considered
    #     equivalent to type(None).
    NoneType,
))
'''
Frozen set of all **shallowly supported non-originative signs** (i.e.,
arbitrary objects uniquely identifying PEP-compliant type hints *not*
originating from a non-:mod:`typing` origin type for which the
:func:`beartype.beartype` decorator generates shallow type-checking code).
'''


HINT_SIGNS_SUPPORTED_DEEP = frozenset((
    # Deeply supported PEP 484- and 585-compliant signs.
    HintSignByteString,
    HintSignGeneric,
    HintSignList,
    HintSignMutableSequence,
    HintSignSequence,
    HintSignTuple,

    # Note that "typing.Union" implicitly subsumes "typing.Optional" *ONLY*
    # under Python <= 3.9. The implementations of the "typing" module under
    # those older Python versions transparently reduced "typing.Optional"
    # to "typing.Union" at runtime. Since this reduction is no longer the
    # case, both *MUST* now be explicitly listed here.
    HintSignUnion,
    HintSignOptional,

    # Deeply supported PEP 544-compliant signs.
    HintSignProtocol,

    # Deeply supported PEP 586-compliant signs.
    HintSignLiteral,

    # Deeply supported PEP 593-compliant signs.
    HintSignAnnotated,
))
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
#failures under Python 3.6, but we can deal with that when we get that far. :p

# HINT_SIGNS_TYPE = (
#     HINT_PEP484_SIGNS_TYPE |
#     HINT_PEP585_SIGNS_TYPE
# )
# '''
# Frozen set of all **isinstanceable class signs** (i.e., classes uniquely
# identifying PEP-compliant type hints that are also passable as the second
# argument to the :func:`isinstance` builtin).
# '''


HINT_SIGNS_TYPE_ORIGIN_STDLIB = frozenset((
    HintSignAbstractSet,
    HintSignAsyncContextManager,
    HintSignAsyncGenerator,
    HintSignAsyncIterable,
    HintSignAsyncIterator,
    HintSignAwaitable,
    HintSignByteString,
    HintSignCallable,
    HintSignChainMap,
    HintSignCollection,
    HintSignContainer,
    HintSignContextManager,
    HintSignCoroutine,
    HintSignCounter,
    HintSignDefaultDict,
    HintSignDeque,
    HintSignDict,
    HintSignFrozenSet,
    HintSignGenerator,
    HintSignItemsView,
    HintSignIterable,
    HintSignIterator,
    HintSignKeysView,
    HintSignList,
    HintSignMapping,
    HintSignMappingView,
    HintSignMatch,
    HintSignMutableMapping,
    HintSignMutableSequence,
    HintSignMutableSet,
    HintSignOrderedDict,
    HintSignPattern,
    HintSignReversible,
    HintSignSequence,
    HintSignSet,
    HintSignTuple,
    HintSignType,
    HintSignValuesView,
))
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
HINT_SIGNS_SUPPORTED = frozenset((
    # Set of all deeply supported signs.
    HINT_SIGNS_SUPPORTED_DEEP |
    # Set of all shallowly supported signs *NOT* originating from a class.
    _HINT_SIGNS_SUPPORTED_SHALLOW |
    # Set of all shallowly supported signs originating from a class.
    HINT_SIGNS_TYPE_ORIGIN_STDLIB
))
'''
Frozen set of all **supported signs** (i.e., arbitrary objects uniquely
identifying PEP-compliant type hints).
'''
