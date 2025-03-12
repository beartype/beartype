#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **type hint sign sets** (i.e., frozen set globals aggregating
instances of the :class:`beartype._data.hint.pep.sign.datapepsigncls.HintSign`
class, enabling efficient categorization of signs as belonging to various
categories of type hints).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.typing import FrozenSet
from beartype._data.hint.pep.sign.datapepsigncls import HintSign
from beartype._data.hint.pep.sign.datapepsigns import (
    HintSignAbstractSet,
    HintSignAnnotated,
    HintSignAny,
    HintSignAsyncContextManager,
    HintSignAsyncGenerator,
    HintSignAsyncIterator,
    HintSignAsyncIterable,
    HintSignAwaitable,
    HintSignBinaryIO,
    HintSignByteString,
    HintSignCallable,
    HintSignChainMap,
    HintSignClassVar,
    HintSignCollection,
    HintSignConcatenate,
    HintSignContainer,
    HintSignContextManager,
    HintSignCoroutine,
    HintSignCounter,
    HintSignDefaultDict,
    HintSignDeque,
    HintSignDict,
    HintSignFinal,
    HintSignForwardRef,
    HintSignFrozenSet,
    HintSignGenerator,
    HintSignHashable,
    HintSignItemsView,
    HintSignIterable,
    HintSignIterator,
    HintSignKeysView,
    HintSignList,
    HintSignLiteral,
    HintSignLiteralString,
    HintSignMapping,
    HintSignMappingView,
    HintSignMatch,
    HintSignMutableMapping,
    HintSignMutableSequence,
    HintSignMutableSet,
    HintSignNewType,
    HintSignNumpyArray,
    HintSignNone,
    HintSignOptional,
    HintSignOrderedDict,
    # HintSignPanderaAny,
    HintSignParamSpec,
    HintSignPattern,
    HintSignPep484585GenericSubscripted,
    HintSignPep484585GenericUnsubscripted,
    HintSignPep557DataclassInitVar,
    HintSignPep585BuiltinSubscriptedUnknown,
    HintSignPep695TypeAliasSubscripted,
    HintSignPep695TypeAliasUnsubscripted,
    HintSignTypeAlias,
    HintSignProtocol,
    HintSignReversible,
    HintSignSelf,
    HintSignSequence,
    HintSignSet,
    HintSignSized,
    HintSignTextIO,
    HintSignTuple,
    HintSignTupleFixed,
    HintSignType,
    HintSignTypedDict,
    HintSignTypeGuard,
    HintSignTypeVar,
    HintSignUnion,
    HintSignUnpack,
    HintSignValuesView,
)

# ....................{ PRIVATE ~ hints                    }....................
_FrozenSetHintSign = FrozenSet[HintSign]
'''
PEP-compliant type matching matching a frozen set of signs.
'''

# ....................{ SETS ~ args                        }....................
HINT_SIGNS_UNSUBSCRIPTABLE = frozenset((
    # ..................{ PEP 484                            }..................
    # The PEP 484-compliant "typing.Any" singleton is *ALWAYS* unsubscripted and
    # thus clearly unsubscriptable.
    HintSignAny,

    # PEP 484-compliant new types (i.e., "typing.NewType" objects) are *ALWAYS*
    # unsubscripted and thus clearly unsubscriptable.
    HintSignNewType,

    # PEP 484-compliant type variables (i.e., "typing.TypeVar" objects) are
    # *ALWAYS* unsubscripted and thus clearly unsubscriptable.
    HintSignTypeVar,

    # ..................{ PEP (484|585)                      }..................
    # PEP 484- and 585-compliant generics are best wrapped by the standard
    # "GenericTypeHint" wrapper even when directly unsubscripted. Why? Because
    # *ALL* generics are (transitively) semantically subscripted either:
    # * Directly (e.g., "MuhGeneric[int]") *OR*...
    # * Indirectly by one or more of their unerased pseudo-superclasses.
    HintSignPep484585GenericUnsubscripted,

    # ..................{ PEP 612                            }..................
    # PEP 612-compliant parameter specifications (i.e., "typing.ParamSpec"
    # objects) are *ALWAYS* unsubscripted and thus clearly unsubscriptable.
    HintSignParamSpec,
))
'''
Frozen set of the signs uniquely identifying all **unsubscriptable type hints**,
defined as type hints that are acceptable when unsubscripted by child type hints
both:

* Technically, as formally standardized by one or more PEPs.
* Pragmatically, as effectively standardized by common usage throughout
  real-world downstream modules.

This frozen set intentionally excludes:

* :pep:`484`-compliant **type hint factories** published by the standard
  :mod:`typing` module subsequently deprecated by :pep:`585` (e.g.,
  :obj:`typing.Dict`, :obj:`typing.List`). Technically, :mod:`beartype`
  permissively accepts these factories as unsubscripted type hints to avoid
  raising excessive decoration-time exceptions that most users would consider to
  be ignorable and thus noxious false negatives. Pragmatically, these factories
  are intended to *only* be subscripted by child type hints. Since these
  factories have been deprecated, this debate is largely moot in either case.
'''

# ....................{ SETS ~ args : container            }....................
HINT_SIGNS_QUASIITERABLE: _FrozenSetHintSign = frozenset((
    # ..................{ PEP (484|585)                      }..................
    HintSignContainer,
    HintSignIterable,
    HintSignReversible,
))
'''
Frozen set of all **standard single-argument quasi-iterable signs** (i.e.,
arbitrary objects uniquely identifying :pep:`484`- or :pep:`585`-compliant type
hints subscripted by exactly one child type hint constraining *all* items of
compliant collections, which may or may not satisfy the
:class:`collections.abc.Iterable` protocol with guaranteed :math:`O(1)`
read-only access to *only* the first collection item but which are *not*
necessarily safely reiterable).

Equivalently, this frozen set only matches the proper subset of all containers
that are **quasi-iterable** (i.e., that may *not* necessarily be safely
reiterated multiple times, where "safely" implies side effect-free idempotency).
Quasi-iterable containers may thus be modified (rather than preserved) by
reiteration such that each call of the:

* :func:`iter` builtin passed the same quasi-iterable *could* effectively create
  and return a different iterator.
* :func:`next` builtin passed the same quasi-iterable *could*
  nondeterministically return different items in a different order, including
  *no* items at all in the case of exhaustible one-time-only iterators (e.g.,
  generators).
'''


HINT_SIGNS_REITERABLE: _FrozenSetHintSign = frozenset((
    # ..................{ PEP (484|585)                      }..................
    HintSignAbstractSet,
    HintSignCollection,
    HintSignFrozenSet,
    HintSignKeysView,
    HintSignMutableSet,
    HintSignSet,
    HintSignValuesView,

    #FIXME: Deques are actually somewhat more than merely single-argument
    #reiterables. They provide efficient access to both the first *AND* last
    #deque items. Ergo, both should be type-checked. The current approach only
    #type-checkes the first deque item. That's certainly better than nothing,
    #but we can (and should) do better. *sigh*
    HintSignDeque,
))
'''
Frozen set of all **standard single-argument reiterable signs** (i.e., arbitrary
objects uniquely identifying :pep:`484`- or :pep:`585`-compliant type hints
subscripted by exactly one child type hint constraining *all* items of compliant
collections, which necessarily satisfy the :class:`collections.abc.Collection`
protocol with guaranteed :math:`O(1)` read-only access to *only* the first
collection item).

For disambiguity, we prefer the :mod:`beartype`-specific term "reiterable" to
the standard term "collection" in this context. Why? Because numerous other data
structures (e.g., mappings, sequences) are also technically collections but
*not* matched by this frozen set. Why? Because this frozen set only matches the
proper subset of all collections *not* matched by any other such frozen set.

Equivalently, this frozen set only matches the proper subset of all containers
that are **reiterable** (i.e., that may be safely reiterated multiple times,
where "safely" implies side effect-free idempotency). Reiterable containers are
thus preserved (rather than modified) by reiteration such that each call of the:

* :func:`iter` builtin passed the same reiterable effectively creates and
  returns the same iterator.
* :func:`next` builtin passed the same reiterable deterministically returns
  the same items in the same order.
'''


HINT_SIGNS_SEQUENCE: _FrozenSetHintSign = frozenset((
    # ..................{ PEP (484|585)                      }..................
    HintSignList,
    HintSignMutableSequence,
    HintSignSequence,
    HintSignTuple,
))
'''
Frozen set of all **standard single-argument sequence signs** (i.e., arbitrary
objects uniquely identifying :pep:`484`- or :pep:`585`-compliant type hints
subscripted by exactly one child type hint constraining *all* items of compliant
sequences, which necessarily satisfy the :class:`collections.abc.Sequence`
protocol with guaranteed :math:`O(1)` indexation across all sequence items).

This set intentionally includes the:

* :data:`.HintSignTuple` sign, identifying variable-length tuple type hints
  subscripted by a single child type hint followed by an ignorable
  :data:`Ellipses` object (i.e., `"..."` substring sans quotes). As such,
  callers should explicitly ignore :data:`Ellipses` objects that are the second
  child type hints subscripting type hints whose signs are in this set.

This set intentionally excludes the:

* :obj:`typing.AnyStr` sign, which accepts only the :class:`str` and
  :class:`bytes` types as its sole subscripted argument, which does *not*
  unconditionally constrain *all* items (i.e., unencoded and encoded characters
  respectively) of compliant sequences but instead parametrizes this attribute.
* :obj:`typing.ByteString` sign, which conditionally accepts either no or an
  arbitrary number of subscripted arguments depending on whether that sign
  identifies:

  * A :pep:`484`-compliant ``typing.ByteString`` type hint subscriptable *no*
    child type hints.
  * A :pep:`585`-compliant ``collections.abc.ByteString[...]`` type hint
    subscriptable by an arbitrary number of child type hints (but typically
    simply :class:`str`).

  Since neither PEP 484 nor 585 comment on ``ByteString`` in detail (or at all,
  really), this non-orthogonality remains inexplicable, frustrating, and utterly
  unsurprising. We elect to merely shrug. In all likelihood, this is an
  ignorable error that no one particularly cares about -- especially since both
  type hint factories have now been scheduled for removal as deprecated.
* :obj:`typing.Deque` sign, whose compliant objects (i.e.,
  :class:`collections.deque` instances) only `guarantee O(n) indexation across
  all sequence items <collections.deque_>`__:

     Indexed access is ``O(1)`` at both ends but slows to ``O(n)`` in the
     middle. For fast random access, use lists instead.

* :obj:`typing.NamedTuple` sign, which embeds a variadic number of
  PEP-compliant field type hints and thus requires special-cased handling.
* :obj:`typing.Text` sign, which accepts *no* subscripted arguments.
  :obj:`typing.Text` is simply an alias for the builtin :class:`str` type and
  thus handled elsewhere as a PEP-noncompliant type hint.
* :data:`.HintSignTupleFixed` sign, identifying fixed-length tuple type hints
  subscripted by an arbitrary number of child type hints and thus requiring
  special-cased handling.

.. _collections.deque:
   https://docs.python.org/3/library/collections.html#collections.deque
'''


HINT_SIGNS_CONTAINER_ARGS_1: _FrozenSetHintSign = (
    HINT_SIGNS_QUASIITERABLE |
    HINT_SIGNS_REITERABLE |
    HINT_SIGNS_SEQUENCE
)
'''
Frozen set of all **standard single-argument container signs** (i.e., arbitrary
objects uniquely identifying :pep:`484`- and :pep:`585`-compliant type hints
describing standard containers satisfying at least the
:class:`collections.abc.Container` protocol subscripted by exactly one child
type hint constraining *all* items contained in that container).
'''

# ....................{ SETS ~ deprecated                  }....................
#FIXME: Currently unused but preserved for posterity. *shrug*
# HINT_SIGNS_DEPRECATED = frozenset((
#     # ..................{ PEP 613                            }..................
#     # PEP 613-compliant "typing.TypeAlias" type hint singletons have been
#     # deprecated by PEP 695-compliant type aliases under Python >= 3.12.
#     HintSignTypeAlias,
# ))
# '''
# Frozen set of all **deprecated signs** (i.e., arbitrary objects uniquely
# identifying PEP-compliant type hints unconditionally obsoleted by equivalent
# PEP-compliant type hints standardized by more recently released PEPs).
# '''

# ....................{ SETS ~ ignorable                   }....................
HINT_SIGNS_BARE_IGNORABLE: _FrozenSetHintSign = frozenset((
    # ..................{ PEP 484                            }..................
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
    HintSignPep484585GenericUnsubscripted,

    # The unsubscripted "Optional" singleton semantically expands to the
    # implicit "Optional[Any]" singleton by the same argument. Since PEP
    # 484 also stipulates that all "Optional[t]" singletons semantically expand
    #     to "Union[t, type(None)]" singletons for arbitrary arguments "t",
    #     "Optional[Any]" semantically expands to merely "Union[Any,
    #     type(None)]". Since all unions subscripted by "Any" semantically
    #     reduce to merely "Any", the "Optional" singleton also reduces to
    # merely "Any".
    #
    # This intentionally excludes "Optional[type(None)]", which the "typing"
    # module physically reduces to merely "type(None)". *shrug*
    HintSignOptional,

    # The unsubscripted "Union" singleton semantically expands to the implicit
    # "Union[Any]" singleton by the same argument. Since PEP 484 stipulates that
    # a union of one type semantically reduces to only that type, "Union[Any]"
    # semantically reduces to merely "Any". Despite their semantic equivalency,
    # however, these objects remain syntactically distinct with respect to
    # object identification: e.g.,
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
    #   contained in this set (e.g., "Union[Any, bool, str]"). Since there exist
    #   a countably infinite number of these subscriptions, these subscriptions
    #   *CANNOT* be explicitly listed in this set. Instead, these subscriptions
    #   are dynamically detected by the high-level
    #   beartype._util.hint.pep.utilhinttest.is_hint_ignorable() tester function
    #   and thus referred to as deeply ignorable type hints.
    HintSignUnion,

    # ..................{ PEP 544                            }..................
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
identifying unsubscripted type hints that are unconditionally ignorable by the
:func:`beartype.beartype` decorator).
'''

# ....................{ SETS ~ kind                        }....................
HINT_SIGNS_GENERIC: _FrozenSetHintSign = frozenset((
    HintSignPep484585GenericSubscripted,
    HintSignPep484585GenericUnsubscripted,
))
'''
Frozen set of all **generic signs** (i.e., arbitrary objects uniquely
identifying :pep:`484`- or :pep:`585`-compliant type hints describing generic
types, including both subscripted and unsubscripted variants).
'''


HINT_SIGNS_MAPPING: _FrozenSetHintSign = frozenset((
    # ..................{ PEP (484|585)                      }..................
    HintSignChainMap,
    HintSignCounter,
    HintSignDefaultDict,
    HintSignDict,
    HintSignMapping,
    HintSignMutableMapping,
    HintSignOrderedDict,
))
'''
Frozen set of all **mapping signs** (i.e., arbitrary objects uniquely
identifying :pep:`484`- or :pep:`585`-compliant type hints subscripted by
exactly two child type hints constraining *all* key-value pairs of compliant
mappings, which necessarily satisfy the :class:`collections.abc.Mapping`
protocol with guaranteed :math:`O(1)` indexation of at least the first key-value
pair).
'''


HINT_SIGNS_UNION: _FrozenSetHintSign = frozenset((
    # ..................{ PEP 484                            }..................
    HintSignOptional,
    HintSignUnion,
))
'''
Frozen set of all **union signs** (i.e., arbitrary objects uniquely identifying
:pep:`484`- and :pep:`604`-compliant type hints unifying one or more subscripted
type hint arguments into a disjunctive set union of these arguments).

If the active Python interpreter targets:

* Python >= 3.9, the :obj:`typing.Optional` and :obj:`typing.Union`
  attributes are distinct.
* Python < 3.9, the :obj:`typing.Optional` attribute reduces to the
  :obj:`typing.Union` attribute, in which case this set is technically
  semantically redundant. Since tests of both object identity and set
  membership are :math:`O(1)`, this set incurs no significant performance
  penalty versus direct usage of the :obj:`typing.Union` attribute and is thus
  unconditionally used as is irrespective of Python version.
'''

# ....................{ SIGNS ~ origin                     }....................
HINT_SIGNS_ORIGIN_ISINSTANCEABLE: _FrozenSetHintSign = frozenset((
    # ..................{ PEP (484|585)                      }..................
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
    HintSignHashable,
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
    HintSignSized,
    HintSignTuple,
    HintSignTupleFixed,
    HintSignType,
    HintSignValuesView,

    # ..................{ NON-PEP                            }..................
    HintSignPep585BuiltinSubscriptedUnknown,
))
'''
Frozen set of all signs uniquely identifying PEP-compliant type hints
originating from an **isinstanceable origin type** (i.e., isinstanceable class
such that *all* objects satisfying this hint are instances of this class).

All hints identified by signs in this set are guaranteed to define
``__origin__`` dunder instance variables whose values are the standard origin
types they originate from. Since any object is trivially type-checkable against
such a type by passing that object and type to the :func:`isinstance` builtin,
*all* objects annotated by hints identified by signs in this set are at least
shallowly type-checkable from wrapper functions generated by the
:func:`beartype.beartype` decorator.
'''

# ....................{ SIGNS ~ return                     }....................
HINT_SIGNS_RETURN_GENERATOR_ASYNC: _FrozenSetHintSign = frozenset((
    # ..................{ PEP (484|585)                      }..................
    HintSignAsyncGenerator,
    HintSignAsyncIterable,
    HintSignAsyncIterator,
))
'''
Frozen set of all signs uniquely identifying **PEP-compliant asynchronous
generator return type hints** (i.e., hints permissible as the return
annotations of asynchronous generators).

See Also
--------
:data:`.HINT_SIGNS_RETURN_GENERATOR_SYNC`
    Further discussion.
'''


HINT_SIGNS_RETURN_GENERATOR_SYNC: _FrozenSetHintSign = frozenset((
    # ..................{ PEP (484|585)                      }..................
    HintSignGenerator,
    HintSignIterable,
    HintSignIterator,
))
'''
Frozen set of all signs uniquely identifying **PEP-compliant synchronous
generator return type hints** (i.e., hints permissible as the return
annotations of synchronous generators).

Generator callables are simply syntactic sugar for non-generator callables
returning generator objects. For this reason, generator callables *must* be
annotated as returning a type compatible with generator objects -- including:

* :data:`HintSignGenerator`, the narrowest abstract base class (ABC) to which
  all generator objects necessarily conform.
* :data:`HintSignIterator`, the immediate superclass of
  :data:`HintSignGenerator`.
* :data:`HintSignIterable`, the immediate superclass of
  :data:`HintSignIterator`.

Technically, :pep:`484` states that generator callables may only be annotated
as only returning a subscription of the :obj:`typing.Generator` factory:

    The return type of generator functions can be annotated by the generic type
    ``Generator[yield_type, send_type, return_type]`` provided by ``typing.py``
    module:

Pragmatically, official documentation for the :mod:`typing` module seemingly
*never* standardized by an existing PEP additionally states that generator
callables may be annotated as also returning a subscription of either the
:obj:`typing.Iterable` or :obj:`typing.Iterator` factories:

    Alternatively, annotate your generator as having a return type of either
    ``Iterable[YieldType]`` or ``Iterator[YieldType]``:

See Also
--------
https://github.com/beartype/beartype/issues/65#issuecomment-954468111
    Further discussion.
'''

# ....................{ SIGNS ~ type                       }....................
HINT_SIGNS_TYPE_MIMIC: _FrozenSetHintSign = frozenset((
    # ..................{ PEP 484                            }..................
    HintSignNewType,

    # ..................{ PEP 593                            }..................
    HintSignAnnotated,
))
'''
Frozen set of all signs uniquely identifying **PEP-compliant type hint mimics**
(i.e., hints maliciously masquerading as another type by explicitly overriding
their ``__module__`` dunder instance variable to that of that type).

Notably, this set contains the signs of:

* :pep:`484`-compliant :obj:`typing.NewType` type hints under Python >= 3.10,
  which badly masquerade as their first passed argument to such an extreme
  degree that they even intentionally prefix their machine-readable
  representation by the fully-qualified name of the caller's module: e.g.,

  .. code-block:: python

     # Under Python >= 3.10:
     >>> import typing
     >>> new_type = typing.NewType('List', bool)
     >>> repr(new_type)
     __main__.List   # <---- this is genuine bollocks

* :pep:`593`-compliant :obj:`typing.Annotated` type hints, which badly
  masquerade as their first subscripted argument (e.g., the :class:`int` in
  ``typing.Annotated[int, 63]``) such that the value of the ``__module__``
  attributes of these hints is that of that argument rather than their own.
  Oddly, their machine-readable representation remains prefixed by
  ``"typing."``, enabling an efficient test that also generalizes to all other
  outlier edge cases that are probably lurking about.

I have no code and I must scream.
'''

# ....................{ SETS ~ pep : 557                   }....................
HINT_SIGNS_DATACLASS_NONFIELDS: _FrozenSetHintSign = frozenset((
    # ..................{ PEP 526                            }..................
    # PEP 526-compliant "typing.ClassVar[...]" type hints, signifying class
    # variables to actually be class variables rather than dataclass fields.
    HintSignClassVar,

    # ..................{ PEP 557                            }..................
    # PEP 557-compliant "dataclasses.InitVar[...]" type hints, signifying class
    # variables to actually be parameters to be passed to the __init__() method
    # dynamically generated for a dataclass rather than dataclass fields.
    HintSignPep557DataclassInitVar,
))
'''
Frozen set of all **dataclass non-field signs** (i.e., arbitrary objects
uniquely identifying PEP-compliant root type hints annotating attributes defined
at class scope in dataclasses decorated by the :pep:`557`-compliant
:func:`dataclasses.dataclass` decorator to *not* be fields of those dataclasses).
'''

# ....................{ SETS ~ pep : 612                   }....................
HINT_SIGNS_CALLABLE_PARAMS: _FrozenSetHintSign = frozenset((
    # ..................{ PEP 612                            }..................
    HintSignConcatenate,
    HintSignParamSpec,
))
'''
Frozen set of all **callable argument signs** (i.e., arbitrary objects uniquely
identifying PEP-compliant child type hints typing the argument lists of parent
:class:`collections.abc.Callable` type hints).

This set necessarily excludes:

* **Standard callable argument lists** (e.g., ``Callable[[bool, int], str]``),
  which are specified as standard lists and thus identified by *no* signs.
* **Ellipsis callable argument lists** (e.g., ``Callable[..., str]``), which are
  specified as the ellipsis singleton and thus identified by *no* signs.
'''

# ....................{ SETS ~ supported                   }....................
_HINT_SIGNS_SUPPORTED_SHALLOW: _FrozenSetHintSign = frozenset((
    # ..................{ PEP 484                            }..................
    HintSignTypeVar,

    # ..................{ PEP 589                            }..................
    #FIXME: Shift into "HINT_SIGNS_SUPPORTED_DEEP" *AFTER* deeply type-checking
    #typed dictionaries.
    HintSignTypedDict,

    # ..................{ PEP 591                            }..................
    HintSignFinal,

    # ..................{ PEP 613                            }..................
    HintSignTypeAlias,

    # ..................{ PEP 646                            }..................
    HintSignUnpack,

    # ..................{ PEP 647                            }..................
    HintSignTypeGuard,

    # ..................{ PEP 673                            }..................
    HintSignSelf,

    # ..................{ PEP 675                            }..................
    HintSignLiteralString,

    # ..................{ PEP 695                            }..................
    HintSignPep695TypeAliasSubscripted,
    HintSignPep695TypeAliasUnsubscripted,
))
'''
Frozen set of all **shallowly supported non-originative signs** (i.e., arbitrary
objects uniquely identifying PEP-compliant type hints *not* originating from an
isinstanceable type for which the :func:`beartype.beartype` decorator generates
shallow type-checking code).
'''


HINT_SIGNS_SUPPORTED_DEEP: _FrozenSetHintSign = (
    HINT_SIGNS_MAPPING |
    HINT_SIGNS_QUASIITERABLE |
    HINT_SIGNS_REITERABLE |
    HINT_SIGNS_SEQUENCE |
    frozenset((
        # ..................{ PEP 484                        }..................
        # Note that the "NoReturn" type hint is invalid in almost all possible
        # syntactic contexts and thus intentionally omitted here. See the
        # "datapepsigns" submodule for further commentary.

        #FIXME: These should probably be in "HINT_SIGNS_SUPPORTED_SHALLOW",
        #instead.
        HintSignAny,
        HintSignBinaryIO,
        HintSignForwardRef,
        HintSignNewType,
        HintSignNone,
        HintSignTextIO,

        # Note that "typing.Union" implicitly subsumes "typing.Optional" *ONLY*
        # under Python <= 3.9. The implementations of the "typing" module under
        # those older Python versions transparently reduced "typing.Optional" to
        # "typing.Union" at runtime. Since this reduction is no longer the case,
        # both *MUST* now be explicitly listed here.
        HintSignOptional,
        HintSignUnion,

        # ..................{ PEP (484|585)                  }..................
        HintSignPep484585GenericSubscripted,
        HintSignPep484585GenericUnsubscripted,
        HintSignTupleFixed,
        HintSignType,

        # ..................{ PEP 544                        }..................
        HintSignProtocol,

        # ..................{ PEP 557                        }..................
        HintSignPep557DataclassInitVar,

        # ..................{ PEP 586                        }..................
        HintSignLiteral,

        # ..................{ PEP 593                        }..................
        HintSignAnnotated,

        # ..................{ NON-PEP ~ package : numpy      }..................
        #FIXME: This should probably be in "HINT_SIGNS_SUPPORTED_SHALLOW", instead.
        HintSignNumpyArray,
    ))
)
'''
Frozen set of all **deeply supported signs** (i.e., arbitrary objects uniquely
identifying PEP-compliant type hints for which the :func:`beartype.beartype`
decorator generates deeply type-checking code).

This set contains *every* sign explicitly supported by one or more conditional
branches in the body of the
:func:`beartype._check.code.codemake.make_func_pith_code` function
generating code deeply type-checking the current pith against the PEP-compliant
type hint annotated by a subscription of that attribute.
'''


HINT_SIGNS_SUPPORTED: _FrozenSetHintSign = frozenset((
    # Set of all deeply supported signs.
    HINT_SIGNS_SUPPORTED_DEEP |
    # Set of all shallowly supported signs *NOT* originating from a class.
    _HINT_SIGNS_SUPPORTED_SHALLOW |
    # Set of all shallowly supported signs originating from a class.
    HINT_SIGNS_ORIGIN_ISINSTANCEABLE
))
'''
Frozen set of all **supported signs** (i.e., arbitrary objects uniquely
identifying PEP-compliant type hints).
'''

# ....................{ PRIVATE ~ main                     }....................
#FIXME: Preserved for posterity. *sigh*
# def _init() -> None:
#     '''
#     Initialize this submodule.
#     '''
#
#     pass
#
#
# # Initialize this submodule.
# _init()
