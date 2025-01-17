#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **Python version-agnostic signs** (i.e., instances of the
:class:`beartype._data.hint.pep.sign.datapepsigncls.HintSign` class
uniquely identifying PEP-compliant type hints in a safe, non-deprecated manner
regardless of the Python version targeted by the active Python interpreter).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# CAUTION: Attributes imported here at module scope *MUST* be explicitly
# deleted from this module's namespace below.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from beartype._data.hint.pep.sign.datapepsigncls import HintSign as _HintSign

# ....................{ SIGNS ~ implicit : pep : (484|585) }....................
# User-defined generics, defined here rather than below to enable explicit
# "typing" exports signed below to trivially alias these generic signs.

HintSignPep484585GenericUnsubscripted = _HintSign(
    name='HintSignPep484585GenericUnsubscripted')
'''
Sign uniquely identifying all :pep:`484`- or :pep:`585`-compliant
**unsubscripted generics** (i.e., types subclassing either the
:pep:`484`-compliant :class:`typing.Generic` superclass, the
:pep:`544`-compliant :class:`typing.Protocol` superclass, or a
:pep:`585`-compliant type hint).
'''


HintSignPep484585GenericSubscripted = _HintSign(
    name='HintSignPep484585GenericSubscripted')
'''
Sign uniquely identifying all :pep:`484`- or :pep:`585`-compliant **subscripted
generics** (i.e., unsubscripted generic types originally parametrized by one or
more :pep:`484`-compliant type variables subscripted by a corresponding number
of arbitrary child type hints): e.g.,

.. code-block:: pycon

   >>> from beartype._util.hint.pep.utilpepget import get_hint_pep_sign_or_none

   # Unsubscripted PEP 585 generic parametrized by a PEP 484 type variable.
   >>> class MuhGeneric[T](list[T]): pass
   >>> get_hint_pep_sign_or_none(MuhGeneric)
   HintSignPep484585GenericUnsubscripted

   # Subscripted PEP 585 generic replacing that type variable with a type.
   >>> get_hint_pep_sign_or_none(MuhGeneric[int])
   HintSignPep484585GenericSubscripted
'''

# ....................{ SIGNS ~ explicit                   }....................
# Signs with explicit analogues in the stdlib "typing" module.
#
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# CAUTION: Signs defined by this module are synchronized with the "__all__"
# list global of the "typing" module bundled with the most recent CPython
# release. For that reason, these signs are:
# * Intentionally declared in the exact same order prefixed by the exact same
#   inline comments as for that list global.
# * Intentionally *NOT* commented with docstrings, both because:
#   * These docstrings would all trivially reduce to a single-line sentence
#     fragment resembling "Alias of typing attribute."
#   * These docstrings would inhibit diffing and synchronization by inspection.
# * Intentionally *NOT* conditionally isolated to the specific range of Python
#   versions whose "typing" module lists these attributes. For example, the
#   "HintSignAsyncContextManager" sign identifying the
#   "typing.AsyncContextManager" attribute that only exists under Python >=
#   3.7 could be conditionally isolated to that range of Python versions.
#   Technically, there exists *NO* impediment to doing so; pragmatically, doing
#   so would be ineffectual. Why? Because attributes *NOT* defined by the
#   "typing" module of the active Python interpreter cannot (by definition) be
#   used to annotate callables decorated by the @beartype decorator.
#
# When bumping beartype to support a new CPython release:
# * Declare one new attribute here for each new "typing" attribute added by
#   that CPython release regardless of whether beartype explicitly supports
#   that attribute yet. The subsequently called die_unless_hint_pep_supported()
#   validator will raise exceptions when passed these attributes.
# * Preserve attributes here that have since been removed from the "typing"
#   module in that CPython release to ensure their continued usability when
#   running beartype against older CPython releases.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# Super-special typing primitives.
HintSignAnnotated       = _HintSign(name='Annotated')
HintSignAny             = _HintSign(name='Any')
HintSignCallable        = _HintSign(name='Callable')
HintSignClassVar        = _HintSign(name='ClassVar')
HintSignConcatenate     = _HintSign(name='Concatenate')
HintSignFinal           = _HintSign(name='Final')
HintSignForwardRef      = _HintSign(name='ForwardRef')
# Generic  <-- ambiguous between subscripted and unsubscripted variants (disambiguated below)
HintSignLiteral         = _HintSign(name='Literal')
HintSignOptional        = _HintSign(name='Optional')
HintSignParamSpec       = _HintSign(name='ParamSpec')
HintSignParamSpecArgs   = _HintSign(name='ParamSpecArgs')
HintSignParamSpecKwargs = _HintSign(name='ParamSpecKwargs')
HintSignProtocol        = _HintSign(name='Protocol')

HintSignTuple           = _HintSign(name='Tuple')
'''
Sign uniquely identifying **variable-length tuple type hints,** including:

* :pep:`484`-compliant type hints of the form ``typing.Tuple[{hint_child_1},
  ...]`` where the last child type hint subscripting this parent hint is an
  ellipses (i.e., ``"..."`` string, :data:`Ellipses` singleton).
* :pep:`585`-compliant type hints of the form ``tuple[{hint_child_1}, ...]``
  where the last child type hint subscripting this parent hint is an ellipses
  (i.e., ``"..."`` string, :data:`Ellipses` singleton).

See Also
--------
HintSignTupleFixed
    Sign uniquely identifying **fixed-length tuple type hints.**
'''

HintSignType         = _HintSign(name='Type')
HintSignTypeVar      = _HintSign(name='TypeVar')
HintSignTypeVarTuple = _HintSign(name='TypeVarTuple')
HintSignUnion        = _HintSign(name='Union')

# ABCs (from collections.abc).
HintSignAbstractSet         = _HintSign(name='AbstractSet')

#FIXME: Permanently remove this sign *AFTER* dropping support for Python 3.15.
HintSignByteString          = _HintSign(name='ByteString')

HintSignContainer           = _HintSign(name='Container')
HintSignContextManager      = _HintSign(name='ContextManager')
HintSignHashable            = _HintSign(name='Hashable')
HintSignItemsView           = _HintSign(name='ItemsView')
HintSignIterable            = _HintSign(name='Iterable')
HintSignIterator            = _HintSign(name='Iterator')
HintSignKeysView            = _HintSign(name='KeysView')
HintSignMapping             = _HintSign(name='Mapping')
HintSignMappingView         = _HintSign(name='MappingView')
HintSignMutableMapping      = _HintSign(name='MutableMapping')
HintSignMutableSequence     = _HintSign(name='MutableSequence')
HintSignMutableSet          = _HintSign(name='MutableSet')
HintSignSequence            = _HintSign(name='Sequence')
HintSignSized               = _HintSign(name='Sized')
HintSignValuesView          = _HintSign(name='ValuesView')
HintSignAwaitable           = _HintSign(name='Awaitable')
HintSignAsyncIterator       = _HintSign(name='AsyncIterator')
HintSignAsyncIterable       = _HintSign(name='AsyncIterable')
HintSignCoroutine           = _HintSign(name='Coroutine')
HintSignCollection          = _HintSign(name='Collection')
HintSignAsyncGenerator      = _HintSign(name='AsyncGenerator')
HintSignAsyncContextManager = _HintSign(name='AsyncContextManager')

# Structural checks, a.k.a. protocols.
HintSignReversible = _HintSign(name='Reversible')
# SupportsAbs   <-- not a useful type hint (already an isinstanceable ABC)
# SupportsBytes   <-- not a useful type hint (already an isinstanceable ABC)
# SupportsComplex   <-- not a useful type hint (already an isinstanceable ABC)
# SupportsFloat   <-- not a useful type hint (already an isinstanceable ABC)
# SupportsIndex   <-- not a useful type hint (already an isinstanceable ABC)
# SupportsInt   <-- not a useful type hint (already an isinstanceable ABC)
# SupportsRound   <-- not a useful type hint (already an isinstanceable ABC)

# Concrete collection types.
HintSignChainMap = _HintSign(name='ChainMap')
HintSignCounter = _HintSign(name='Counter')
HintSignDeque = _HintSign(name='Deque')
HintSignDict = _HintSign(name='Dict')
HintSignDefaultDict = _HintSign(name='DefaultDict')
HintSignList = _HintSign(name='List')
HintSignOrderedDict = _HintSign(name='OrderedDict')
HintSignSet = _HintSign(name='Set')
HintSignFrozenSet = _HintSign(name='FrozenSet')
HintSignNamedTuple = _HintSign(name='NamedTuple')
HintSignTypedDict = _HintSign(name='TypedDict')
HintSignGenerator = _HintSign(name='Generator')

# Other concrete types.
HintSignMatch = _HintSign(name='Match')
HintSignPattern = _HintSign(name='Pattern')

# Other concrete type aliases.
# IO  <-- ambiguous between subscripted and unsubscripted variants
HintSignBinaryIO = HintSignPep484585GenericUnsubscripted
HintSignTextIO = HintSignPep484585GenericUnsubscripted

# One-off things.
# AnyStr   <-- not a unique type hint (merely a constrained "TypeVar")
# assert_never   <-- unusable as a type hint
# assert_type   <-- unusable as a type hint
# cast   <-- unusable as a type hint
# clear_overloads   <-- unusable as a type hint
# dataclass_transform   <-- unusable as a type hint
# final   <-- unusable as a type hint
# get_args   <-- unusable as a type hint
# get_origin   <-- unusable as a type hint
# get_type_hints   <-- unusable as a type hint
# is_protocol    <-- unusable as a type hint
# is_typeddict   <-- unusable as a type hint
HintSignLiteralString = _HintSign(name='LiteralString')
HintSignNever         = _HintSign(name='Never')
HintSignNewType       = _HintSign(name='NewType')
# no_type_check   <-- unusable as a type hint
# no_type_check_decorator   <-- unusable as a type hint
HintSignNoDefault     = _HintSign(name='NoDefault')

# Note that "NoReturn" is contextually valid *ONLY* as a top-level return hint.
# Since this use case is extremely limited, we explicitly generate code for this
# use case outside of the general-purpose code generation pathway for standard
# type hints. Since "NoReturn" is an unsubscriptable singleton, we explicitly
# detect this type hint with an identity test and thus require *NO* sign to
# uniquely identify this type hint.
#
# Theoretically, explicitly defining a sign uniquely identifying this type hint
# could erroneously encourage us to use that sign elsewhere; we should avoid
# that, as "NoReturn" is invalid in almost all possible contexts. Pragmatically,
# doing so nonetheless improves orthogonality when detecting and validating
# PEP-compliant type hints, which ultimately matters more than our subjective
# feelings about the matter. Wisely, we choose pragmatics.
#
# In short, "NoReturn" is insane.
HintSignNoReturn = _HintSign(name='NoReturn')

HintSignNotRequired     = _HintSign(name='NotRequired')
# overload   <-- unusable as a type hint
# override   <-- unusable as a type hint
HintSignParamSpecArgs   = _HintSign(name='ParamSpecArgs')
HintSignParamSpecKwargs = _HintSign(name='ParamSpecKwargs')
HintSignReadOnly        = _HintSign(name='ReadOnly')
HintSignRequired        = _HintSign(name='Required')
# reveal_type         <-- unusable as a type hint
# runtime_checkable   <-- unusable as a type hint
HintSignSelf            = _HintSign(name='Self')
# Text   <-- not actually a type hint (literal alias for "str")
# TYPE_CHECKING   <-- unusable as a type hint
HintSignTypeAlias       = _HintSign(name='TypeAlias')
HintSignTypeGuard       = _HintSign(name='TypeIs')
HintSignTypeIs          = _HintSign(name='TypeIs')
# TypeAliasType  <-- not a unique type hint (merely a C-based type)
HintSignUnpack          = _HintSign(name='Unpack')

# Wrapper namespace for re type aliases.
#
# Note that "typing.__all__" intentionally omits the "Match" and "Pattern"
# attributes, which it oddly considers to comprise another namespace. *shrug*

# ....................{ SIGNS ~ implicit                   }....................
# Signs with *NO* explicit analogues in the stdlib "typing" module but
# nonetheless standardized by one or more PEPs.

HintSignNone = _HintSign(name='None')
'''
Sign uniquely identifying the :data:`None` singleton, explicitly supported by
:pep:`484` but lacking an explicit analogue in the standard :mod:`typing`
module:

    When used in a type hint, the expression None is considered equivalent to
    type(None).
'''


#FIXME: *WOOPS.* Turns out this was an awful idea, thanks to PEP 646 (i.e.,
#tuple type hint unpacking). Probably should have seen that coming. See the
#"data_pep646" test submodule for clarity on what to do now. It's not pretty.
HintSignTupleFixed = _HintSign(name='TupleFixed')
'''
Sign uniquely identifying **fixed-length tuple type hints,** including:

* :pep:`484`-compliant type hints of the form ``typing.Tuple[{hint_child_1},
  ..., {hint_child_N}]`` where ``{hint_child_N}`` is *not* an ellipses (i.e.,
  ``"..."`` string, :data:`Ellipses` singleton).
* :pep:`585`-compliant type hints of the form ``tuple[{hint_child_1}, ...,
  {hint_child_N}]`` where ``{hint_child_N}`` is *not* an ellipses (i.e.,
  ``"..."`` string, :data:`Ellipses` singleton).

Note that:

* The ``"..."`` substring above is *not* a literal ellipses but simply denotes
  an arbitrary number of non-ellipses child type hints.
* The existing :data:`.HintSignTuple` sign uniquely identifies variable-length
  tuple type hints. Why? Because that sign naturally matches the unsubscripted
  :obj:`typing.Tuple` type hint factory, which is semantically equivalent to the
  ``typing.Tuple[object, ...]`` type hint, which is the widest possible
  variable-length tuple type hint.
'''

# ....................{ SIGNS ~ implicit : lib             }....................
# Signs identifying PEP-noncompliant third-party type hints published by...
#
# ....................{ SIGNS ~ implicit : lib : numpy     }....................
HintSignNumpyArray = _HintSign(name='NumpyArray')   # <-- "numpy.typing.NDArray"
'''
...the :mod:`numpy.typing` subpackage.
'''

# ....................{ SIGNS ~ implicit : lib : pandera   }....................
HintSignPanderaAny = _HintSign(name='PanderaAny')   # <-- "pandera.typing.*"
'''
...the :mod:`pandera.typing` subpackage.

Specifically, define a single sign unconditionally matching *all* type hints
published by the :mod:`pandera.typing` subpackage. Why? Because Pandera insanely
publishes its own Pandera-specific PEP-noncompliant runtime type-checking
decorator :func:`pandera.check_types` that supports *only* Pandera-specific
PEP-noncompliant :mod:`pandera.typing` type hints. Since Pandera users are
already accustomed to decorating *all* Pandera-based callables (i.e., callables
accepting one or more parameters and/or returning one or more values which are
Pandera objects) by :func:`pandera.check_types`, attempting to type-check the
same objects already type-checked by that decorator would only inefficiently and
needlessly slow :mod:`beartype` down. Ergo, we ignore *all* Pandera type hints
by:

* Defining this catch-all singleton for Pandera type hints here.
* Denoting this singleton to be unconditionally ignorable elsewhere.
'''

# ....................{ SIGNS ~ implicit : pep : 557       }....................
# dataclasses.InitVar[...].
HintSignPep557DataclassInitVar = _HintSign(name='Pep557DataclassInitVar')
'''
:pep:`557`-compliant :obj:`dataclasses.InitVar` type hint factory, annotating
class-scoped variable annotations of :func:`dataclass.dataclass`-decorated
data classes.
'''

# ....................{ SIGNS ~ implicit : pep : 585       }....................
# os.PathLike[...], weakref.weakref[...], et al.
HintSignPep585BuiltinSubscriptedUnknown = _HintSign(
    name='Pep585BuiltinSubscriptedUnknown')
'''
:pep:`585`-compliant C-based :class:`types.GenericAlias` superclass inheritable
by PEP-noncompliant pure-Python subclasses in either the standard library or
third-party packages, which when subscripted by otherwise PEP-compliant child
type hints produce PEP-noncompliant **unrecognized subscripted builtin type
hints** (i.e., C-based type hints that are *not* isinstanceable types,
instantiated by subscripting pure-Python origin classes unrecognized by
:mod:`beartype` and thus PEP-noncompliant).

Examples include:

* ``os.PathLike[...]`` type hints.
* ``weakref.weakref[...]`` type hints.

Unsurprisingly, :mod:`beartype` reduces C-based unrecognized subscripted builtin
type hints (which are *not* type-checkable as is) to their unsubscripted
pure-Python origin classes (which are type-checkable as is).
'''

# ....................{ SIGNS ~ implicit : pep : 695       }....................
# "type {alias_name}[{typevar_name}] = {alias_value}" statements.

HintSignPep695TypeAliasUnsubscripted = _HintSign(
    name='HintSignPep695TypeAliasUnsubscripted')
'''
:pep:`695`-compliant C-based :class:`types.TypeAliasType` class of all
:pep:`695`-compliant **unsubscripted type aliases** (i.e., objects created as
the left-hand sides of statements of the form ``type {alias_name} =
{alias_value}``).

Most real-world type aliases are unsubscripted and thus identified by this sign.
'''


HintSignPep695TypeAliasSubscripted = _HintSign(
    name='HintSignPep695TypeAliasSubscripted')
'''
Sign uniquely identifying all :pep:`695`-compliant **subscripted type aliases**
(i.e., unsubscripted type aliases originally parametrized by one or more
:pep:`484`-compliant type variables subscripted by a corresponding number of
arbitrary child type hints): e.g.,

.. code-block:: pycon

   >>> from beartype._util.hint.pep.utilpepget import get_hint_pep_sign_or_none

   # Unsubscripted PEP 695 type alias parametrized by a PEP 484 type variable.
   >>> MuhTypeAlias[T] = T | float
   >>> get_hint_pep_sign_or_none(MuhTypeAlias)
   HintSignPep695TypeAliasUnsubscripted

   # Subscripted PEP 695 type alias replacing that type variable with a type.
   >>> get_hint_pep_sign_or_none(MuhTypeAlias[int])
   HintSignPep695TypeAliasSubscripted
'''

# ....................{ CLEANUP                            }....................
# Prevent all attributes imported above from polluting this namespace. Why?
# Logic elsewhere subsequently assumes a one-to-one mapping between the
# attributes of this namespace and signs.
del _HintSign
