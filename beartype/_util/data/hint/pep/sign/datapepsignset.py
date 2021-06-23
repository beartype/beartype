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
#* HINT_PEP484_SIGNS_SUPPORTED_SHALLOW.
#* HINT_PEP484_SIGNS_SUPPORTED_DEEP.
#* HINT_PEP484_ATTRS_ISINSTANCEABLE.
#* HINT_PEP484_SIGNS_TYPE_ORIGIN.
#* HINT_PEP544_SIGNS_SUPPORTED_DEEP.
#* HINT_PEP585_SIGNS_SEQUENCE_STANDARD.
#* HINT_PEP585_SIGNS_SUPPORTED_DEEP.
#* HINT_PEP585_ATTRS_ISINSTANCEABLE.
#* HINT_PEP586_SIGNS_SUPPORTED_DEEP.
#* HINT_PEP593_SIGNS_SUPPORTED_DEEP.

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

# ....................{ SIGNS ~ bare                      }....................
HINT_SIGNS_BARE_IGNORABLE = frozenset((
    # ..................{ PEP (484|585)                     }..................
    # The "Any" singleton is semantically synonymous with the ignorable
    # PEP-noncompliant "beartype.cave.AnyType" and hence "object" types.
    HintSignAny,

    # The "Generic" superclass imposes no constraints and is thus also
    # semantically synonymous with the ignorable PEP-noncompliant
    # "beartype.cave.AnyType" and hence "object" types. Since PEP
    # 484 stipulates that *ANY* unsubscripted subscriptable PEP-compliant
    # singleton including "typing.Generic" semantically expands to that
    # singelton subscripted by an implicit "Any" argument, "Generic"
    # semantically expands to the implicit "Generic[Any]" singleton.
    HintSignGeneric,

    # The unsubscripted "Optional" singleton semantically expands to the
    # implicit "Optional[Any]" singleton by the same argument. Since PEP
    # 484 also stipulates that all "Optional[t]" singletons semantically
    # expand to "Union[t, type(None)]" singletons for arbitrary arguments
    # "t", "Optional[Any]" semantically expands to merely "Union[Any,
    # type(None)]". Since all unions subscripted by "Any" semantically
    # reduce to merely "Any", the "Optional" singleton also reduces to
    # merely "Any".
    #
    # This intentionally excludes "Optional[type(None)]", which the
    # "typing" module physically reduces to merely "type(None)". *shrug*
    HintSignOptional,

    # The unsubscripted "Union" singleton semantically expands to the
    # implicit "Union[Any]" singleton by the same argument. Since PEP 484
    # stipulates that a union of one type semantically reduces to only that
    # type, "Union[Any]" semantically reduces to merely "Any". Despite
    # their semantic equivalency, however, these objects remain
    # syntactically distinct with respect to object identification: e.g.,
    #     >>> Union is not Union[Any]
    #     True
    #     >>> Union is not Any
    #     True
    #
    # This intentionally excludes:
    #
    # * The "Union[Any]" and "Union[object]" singletons, since the "typing"
    #   module physically reduces:
    #   * "Union[Any]" to merely "Any" (i.e., "Union[Any] is Any"), which
    #     this frozen set already contains.
    #   * "Union[object]" to merely "object" (i.e., "Union[object] is
    #     object"), which this frozen set also already contains.
    # * "Union" singleton subscripted by one or more ignorable type hints
    #   contained in this set (e.g., "Union[Any, bool, str]"). Since there
    #   exist a countably infinite number of these subscriptions, these
    #   subscriptions *CANNOT* be explicitly listed in this set. Instead,
    #   these subscriptions are dynamically detected by the high-level
    #   beartype._util.hint.pep.utilhinttest.is_hint_ignorable() tester
    #   function and thus referred to as deeply ignorable type hints.
    HintSignUnion,

    # ..................{ PEP 544                           }..................
    # Note that ignoring the "typing.Protocol" superclass is vital here. For
    # unknown and presumably uninteresting reasons, *ALL* possible objects
    # satisfy this superclass. Ergo, this superclass is synonymous with the
    # "object" root superclass: e.g.,
    #     >>> import typing as t
    #     >>> isinstance(object(), t.Protocol)
    #     True
    #     >>> isinstance('wtfbro', t.Protocol)
    #     True
    #     >>> isinstance(0x696969, t.Protocol)
    #     True
    HintSignProtocol,
))
'''
Frozen set of all **bare ignorable signs** (i.e., arbitrary objects uniquely
identifying type hints that, where unsubscripted, are unconditionally ignorable
by the :func:`beartype.beartype` decorator).
'''

# ....................{ SIGNS ~ origin                    }....................
HINT_SIGNS_TYPE_STDLIB = frozenset((
    # ..................{ PEP (484|585)                     }..................
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
Frozen set of all signs uniquely identifying PEP-compliant type hints
originating from a **standard origin type** (i.e., isinstanceable class such
that *all* objects satisfying this hint are instances of this class).

Any object is trivially type-checkable against an isinstanceable class by
passing that object and class to the :func:`isinstance` builtin. Ergo, *all*
objects annotated by hints identified by signs in this set are guaranteed to at
least be shallowly type-checkable from wrapper functions generated by the
:func:`beartype.beartype` decorator.
'''

# ....................{ SETS ~ supported                  }....................
_HINT_SIGNS_SUPPORTED_SHALLOW = frozenset((
    # ..................{ PEP 484                           }..................
    # Note that the "NoReturn" type hint is invalid in almost all possible
    # syntactic contexts and thus intentionally omitted here. See the
    # "datapepsigns" submodule for further commentary.
    HintSignAny,
    HintSignForwardRef,
    HintSignNewType,
    HintSignTypeVar,

    #FIXME: Non-orthogonal. Types are *NOT* signs. This should be probably be
    #explicitly tested for elsewhere, please.

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
    # ..................{ PEP 484                           }..................
    # Note that "typing.Union" implicitly subsumes "typing.Optional" *ONLY*
    # under Python <= 3.9. The implementations of the "typing" module under
    # those older Python versions transparently reduced "typing.Optional"
    # to "typing.Union" at runtime. Since this reduction is no longer the
    # case, both *MUST* now be explicitly listed here.
    HintSignUnion,
    HintSignOptional,

    # ..................{ PEP (484|585)                     }..................
    HintSignByteString,
    HintSignGeneric,
    HintSignList,
    HintSignMutableSequence,
    HintSignSequence,
    HintSignTuple,

    # ..................{ PEP 544                           }..................
    HintSignProtocol,

    # ..................{ PEP 586                           }..................
    HintSignLiteral,

    # ..................{ PEP 593                           }..................
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


HINT_SIGNS_SUPPORTED = frozenset((
    # Set of all deeply supported signs.
    HINT_SIGNS_SUPPORTED_DEEP |
    # Set of all shallowly supported signs *NOT* originating from a class.
    _HINT_SIGNS_SUPPORTED_SHALLOW |
    # Set of all shallowly supported signs originating from a class.
    HINT_SIGNS_TYPE_STDLIB
))
'''
Frozen set of all **supported signs** (i.e., arbitrary objects uniquely
identifying PEP-compliant type hints).
'''

# ....................{ SETS ~ kind : sequence            }....................
HINT_SIGNS_SEQUENCE_ARGS_ONE = frozenset((
    # ..................{ PEP (484|585)                     }..................
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
