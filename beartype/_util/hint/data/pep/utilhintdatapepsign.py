#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2021 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype Python version-agnostic signs** (i.e., arbitrary objects uniquely
identifying PEP-compliant type hints in a safe, non-deprecated manner
regardless of the Python version targeted by the active Python interpreter).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                           }....................
from beartype._util.utilobject import Iota

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
#   that CPython release that beartype explicitly supports. Please avoid adding
#   attributes here for "typing" attributes unsupported by beartype, as doing
#   so would cause @beartype to silently accept type hints created from those
#   "typing" attributes -- thus inducing non-human-readable havoc elsewhere.
# * Preserve attributes here that have since been removed from the "typing"
#   module in that CPython release to ensure their continued usability when
#   running beartype against older CPython releases.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# Super-special typing primitives.
Annotated = Iota()
Any = Iota()
Callable = Iota()
#FIXME: Uncomment after supported by beartype.
# ClassVar = Iota()
# Concatenate = Iota()
# Final = Iota()
ForwardRef = Iota()
Generic = Iota()
Literal = Iota()
Optional = Iota()
#FIXME: Uncomment after supported by beartype.
# ParamSpec = Iota()
Protocol = Iota()
Tuple = Iota()
Type = Iota()
TypeVar = Iota()
Union = Iota()

# ABCs (from collections.abc).
AbstractSet = Iota
ByteString = Iota()
Container = Iota()
ContextManager = Iota()
Hashable = Iota()
ItemsView = Iota()
Iterable = Iota()
Iterator = Iota()
KeysView = Iota()
Mapping = Iota()
MappingView = Iota()
MutableMapping = Iota()
MutableSequence = Iota()
MutableSet = Iota()
Sequence = Iota()
Sized = Iota()
ValuesView = Iota()
Awaitable = Iota()
AsyncIterator = Iota()
AsyncIterable = Iota()
Coroutine = Iota()
Collection = Iota()
AsyncGenerator = Iota()
AsyncContextManager = Iota()

# Structural checks, a.k.a. protocols.
Reversible = Iota()
SupportsAbs = Iota()
SupportsBytes = Iota()
SupportsComplex = Iota()
SupportsFloat = Iota()
SupportsIndex = Iota()
SupportsInt = Iota()
SupportsRound = Iota()

# Concrete collection types.
ChainMap = Iota()
Counter = Iota()
Deque = Iota()
Dict = Iota()
DefaultDict = Iota()
List = Iota()
OrderedDict = Iota()
Set = Iota()
FrozenSet = Iota()
#FIXME: Uncomment after supported by beartype.
# NamedTuple = Iota()
# TypedDict = Iota()
Generator = Iota()

# One-off things.
AnyStr = Iota()
# cast   <-- unusable as a type hint
# final   <-- unusable as a type hint
# get_args   <-- unusable as a type hint
# get_origin   <-- unusable as a type hint
# get_type_hints   <-- unusable as a type hint
# is_typeddict   <-- unusable as a type hint
NewType = Iota()
# no_type_check   <-- unusable as a type hint
# no_type_check_decorator   <-- unusable as a type hint
NoReturn = Iota()
# overload   <-- unusable as a type hint
#FIXME: Uncomment after supported by beartype.
# ParamSpecArgs = Iota()
# ParamSpecKwargs = Iota()
# runtime_checkable   <-- unusable as a type hint
Text = Iota()
# TYPE_CHECKING   <-- unusable as a type hint
# TypeAlias   <-- irrelevant for runtime type checking
#FIXME: Uncomment after supported by beartype.
# TypeGuard = Iota()
