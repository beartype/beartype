#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2021 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **Python version-agnostic signs** (i.e., instances of the
:class:`beartype._util.hint.data.pep.sign.datapepsigncls.HintSign` class
uniquely identifying PEP-compliant type hints in a safe, non-deprecated manner
regardless of the Python version targeted by the active Python interpreter).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                           }....................
from beartype._util.hint.data.pep.sign.datapepsigncls import HintSign

# ....................{ SIGNS                             }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# CAUTION: Attributes defined by this module are intentionally synchronized
# with the "__all__" dunder list global of the "typing" module bundled with the
# most recent CPython release. For that reason, these attributes are
# * Intentionally declared in the exact same order prefixed by the exact same
#   inline comments as for that list global.
# * Intentionally *NOT* commented with docstrings, both because:
#   * These docstrings would all trivially reduce to a single-line sentence
#     fragment resembling "Alias of typing attribute."
#   * These docstrings would inhibit diffing and synchronization by inspection.
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
HintSignAnnotated = HintSign()
HintSignAny = HintSign()
HintSignCallable = HintSign()
HintSignClassVar = HintSign()
HintSignConcatenate = HintSign()
HintSignFinal = HintSign()
HintSignForwardRef = HintSign()
HintSignGeneric = HintSign()
HintSignLiteral = HintSign()
HintSignOptional = HintSign()
HintSignParamSpec = HintSign()
HintSignProtocol = HintSign()
HintSignTuple = HintSign()
HintSignType = HintSign()
HintSignTypeVar = HintSign()
HintSignUnion = HintSign()

# ABCs (from collections.abc).
HintSignAbstractSet = HintSign
HintSignByteString = HintSign()
HintSignContainer = HintSign()
HintSignContextManager = HintSign()
HintSignHashable = HintSign()
HintSignItemsView = HintSign()
HintSignIterable = HintSign()
HintSignIterator = HintSign()
HintSignKeysView = HintSign()
HintSignMapping = HintSign()
HintSignMappingView = HintSign()
HintSignMutableMapping = HintSign()
HintSignMutableSequence = HintSign()
HintSignMutableSet = HintSign()
HintSignSequence = HintSign()
HintSignSized = HintSign()
HintSignValuesView = HintSign()
HintSignAwaitable = HintSign()
HintSignAsyncIterator = HintSign()
HintSignAsyncIterable = HintSign()
HintSignCoroutine = HintSign()
HintSignCollection = HintSign()
HintSignAsyncGenerator = HintSign()
HintSignAsyncContextManager = HintSign()

# Structural checks, a.k.a. protocols.
HintSignReversible = HintSign()
HintSignSupportsAbs = HintSign()
HintSignSupportsBytes = HintSign()
HintSignSupportsComplex = HintSign()
HintSignSupportsFloat = HintSign()
HintSignSupportsIndex = HintSign()
HintSignSupportsInt = HintSign()
HintSignSupportsRound = HintSign()

# Concrete collection types.
HintSignChainMap = HintSign()
HintSignCounter = HintSign()
HintSignDeque = HintSign()
HintSignDict = HintSign()
HintSignDefaultDict = HintSign()
HintSignList = HintSign()
HintSignOrderedDict = HintSign()
HintSignSet = HintSign()
HintSignFrozenSet = HintSign()
HintSignNamedTuple = HintSign()
HintSignTypedDict = HintSign()
HintSignGenerator = HintSign()

# One-off things.
HintSignAnyStr = HintSign()
# cast   <-- unusable as a type hint
# final   <-- unusable as a type hint
# get_args   <-- unusable as a type hint
# get_origin   <-- unusable as a type hint
# get_type_hints   <-- unusable as a type hint
# is_typeddict   <-- unusable as a type hint
HintSignNewType = HintSign()
# no_type_check   <-- unusable as a type hint
# no_type_check_decorator   <-- unusable as a type hint
# NoReturn   <-- generally unusable as a type hint (see above for commentary)
# overload   <-- unusable as a type hint
HintSignParamSpecArgs = HintSign()
HintSignParamSpecKwargs = HintSign()
# runtime_checkable   <-- unusable as a type hint
HintSignText = HintSign()
# TYPE_CHECKING   <-- unusable as a type hint
HintSignTypeAlias = HintSign()
HintSignTypeGuard = HintSign()

# ....................{ CLEANUP                           }....................
# Prevent all attributes imported above from polluting this namespace. Why?
# Logic elsewhere subsequently assumes a one-to-one mapping between the
# attributes of this namespace and signs.
del HintSign
