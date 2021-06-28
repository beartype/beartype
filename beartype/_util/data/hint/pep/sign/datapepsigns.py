#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2021 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **Python version-agnostic signs** (i.e., instances of the
:class:`beartype._util.data.hint.pep.sign.datapepsigncls.HintSign` class
uniquely identifying PEP-compliant type hints in a safe, non-deprecated manner
regardless of the Python version targeted by the active Python interpreter).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                           }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# CAUTION: Attributes imported here at module scope *MUST* be explicitly
# deleted from this module's namespace below.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

from beartype._util.data.hint.pep.sign.datapepsigncls import HintSign

# ....................{ SIGNS                             }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
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
#   Technically, there exsits *NO* impediment to doing so; pragmatically, doing
#   so would be ineffectual. Why? Because attributes *NOT* defined by the
#   "typing" module of the active Python interpreter cannot (by definition) be
#   used to annotate callables decorated by the @beartype decorator.
#
# When bumping beartype to support a new CPython release:
# * Declare one new attribute here for each new "typing" attribute added by
#   that CPython release regardless of whether beartype explicitly supports
#   that attribute yet. The subsequently called die_unless_hint_pep_supported()
#   validator will raise exceptions when passed such attributes.
# * Preserve attributes here that have since been removed from the "typing"
#   module in that CPython release to ensure their continued usability when
#   running beartype against older CPython releases.
#
# Lastly, note that:
# * "NoReturn" is contextually valid *ONLY* as a top-level return hint. Since
#   this use case is extremely limited, we explicitly generate code for this
#   use case outside of the general-purpose code generation pathway for
#   standard type hints. Since "NoReturn" is an unsubscriptable singleton, we
#   explicitly detect this type hint with an identity test and thus require
#   *NO* sign to uniquely identify this type hint. Indeed, explicitly defining
#   a sign uniquely identifying this type hint would erroneously encourage us
#   to use that sign elsewhere. We should *NOT* do that, because "NoReturn" is
#   invalid in almost all possible contexts. Of course, we actually previously
#   did define a "NoReturn" sign and erroneously use that sign elsewhere, which
#   is exactly why we do *NOT* do so now. In short, "NoReturn" is insane.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# Super-special typing primitives.
HintSignAnnotated = HintSign(name='Annotated')
HintSignAny = HintSign(name='Any')
HintSignCallable = HintSign(name='Callable')
HintSignClassVar = HintSign(name='ClassVar')
HintSignConcatenate = HintSign(name='Concatenate')
HintSignFinal = HintSign(name='Final')
HintSignForwardRef = HintSign(name='ForwardRef')
HintSignGeneric = HintSign(name='Generic')
HintSignLiteral = HintSign(name='Literal')
HintSignOptional = HintSign(name='Optional')
HintSignParamSpec = HintSign(name='ParamSpec')
HintSignProtocol = HintSign(name='Protocol')
HintSignTuple = HintSign(name='Tuple')
HintSignType = HintSign(name='Type')
HintSignTypeVar = HintSign(name='TypeVar')
HintSignUnion = HintSign(name='Union')

# ABCs (from collections.abc).
HintSignAbstractSet = HintSign(name='AbstractSet')
HintSignByteString = HintSign(name='ByteString')
HintSignContainer = HintSign(name='Container')
HintSignContextManager = HintSign(name='ContextManager')
HintSignHashable = HintSign(name='Hashable')
HintSignItemsView = HintSign(name='ItemsView')
HintSignIterable = HintSign(name='Iterable')
HintSignIterator = HintSign(name='Iterator')
HintSignKeysView = HintSign(name='KeysView')
HintSignMapping = HintSign(name='Mapping')
HintSignMappingView = HintSign(name='MappingView')
HintSignMutableMapping = HintSign(name='MutableMapping')
HintSignMutableSequence = HintSign(name='MutableSequence')
HintSignMutableSet = HintSign(name='MutableSet')
HintSignSequence = HintSign(name='Sequence')
HintSignSized = HintSign(name='Sized')
HintSignValuesView = HintSign(name='ValuesView')
HintSignAwaitable = HintSign(name='Awaitable')
HintSignAsyncIterator = HintSign(name='Iterator')
HintSignAsyncIterable = HintSign(name='Iterable')
HintSignCoroutine = HintSign(name='Coroutine')
HintSignCollection = HintSign(name='Collection')
HintSignAsyncGenerator = HintSign(name='Generator')
HintSignAsyncContextManager = HintSign(name='ContextManager')

# Structural checks, a.k.a. protocols.
HintSignReversible = HintSign(name='Reversible')
# SupportsAbs   <-- not a useful type hint (already an isinstanceable ABC)
# SupportsBytes   <-- not a useful type hint (already an isinstanceable ABC)
# SupportsComplex   <-- not a useful type hint (already an isinstanceable ABC)
# SupportsFloat   <-- not a useful type hint (already an isinstanceable ABC)
# SupportsIndex   <-- not a useful type hint (already an isinstanceable ABC)
# SupportsInt   <-- not a useful type hint (already an isinstanceable ABC)
# SupportsRound   <-- not a useful type hint (already an isinstanceable ABC)

# Concrete collection types.
HintSignChainMap = HintSign(name='ChainMap')
HintSignCounter = HintSign(name='Counter')
HintSignDeque = HintSign(name='Deque')
HintSignDict = HintSign(name='Dict')
HintSignDefaultDict = HintSign(name='DefaultDict')
HintSignList = HintSign(name='List')
HintSignOrderedDict = HintSign(name='OrderedDict')
HintSignSet = HintSign(name='Set')
HintSignFrozenSet = HintSign(name='FrozenSet')
HintSignNamedTuple = HintSign(name='NamedTuple')
HintSignTypedDict = HintSign(name='TypedDict')
HintSignGenerator = HintSign(name='Generator')

# One-off things.
# AnyStr   <-- not a unique type hint (just a constrained "TypeVar")
# cast   <-- unusable as a type hint
# final   <-- unusable as a type hint
# get_args   <-- unusable as a type hint
# get_origin   <-- unusable as a type hint
# get_type_hints   <-- unusable as a type hint
# is_typeddict   <-- unusable as a type hint
HintSignNewType = HintSign(name='NewType')
# no_type_check   <-- unusable as a type hint
# no_type_check_decorator   <-- unusable as a type hint
# NoReturn   <-- generally unusable as a type hint (see above for commentary)
# overload   <-- unusable as a type hint
HintSignParamSpecArgs = HintSign(name='ParamSpecArgs')
HintSignParamSpecKwargs = HintSign(name='ParamSpecKwargs')
# runtime_checkable   <-- unusable as a type hint
# Text   <-- not actually a type hint (literal alias for "str")
# TYPE_CHECKING   <-- unusable as a type hint
HintSignTypeAlias = HintSign(name='TypeAlias')
HintSignTypeGuard = HintSign(name='TypeGuard')

# Wrapper namespace for re type aliases.
#
# Note that "typing.__all__" intentionally omits the "Match" and "Pattern"
# attributes, which it oddly considers to comprise another namespace. *shrug*
HintSignMatch = HintSign(name='Match')
HintSignPattern = HintSign(name='Pattern')

# ....................{ CLEANUP                           }....................
# Prevent all attributes imported above from polluting this namespace. Why?
# Logic elsewhere subsequently assumes a one-to-one mapping between the
# attributes of this namespace and signs.
del HintSign
