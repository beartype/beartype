#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2021 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype :pep:`484`**-compliant type hint data.**

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                           }....................
import typing
from beartype._cave._cavefast import NoneType
from beartype._util.data.hint.pep.sign.datapepsigns import (
    HintSignForwardRef,
    HintSignGeneric,
    HintSignNewType,
    HintSignTypeVar,
)
from beartype._util.py.utilpyversion import (
    IS_PYTHON_3_6,
    IS_PYTHON_AT_LEAST_3_7,
    IS_PYTHON_AT_LEAST_3_8,
    IS_PYTHON_AT_LEAST_3_9,
)
from sys import version_info
from typing import (
    AbstractSet,
    Any,
    AsyncGenerator,
    AsyncIterable,
    AsyncIterator,
    Awaitable,
    ByteString,
    Callable,
    ChainMap,
    Collection,
    Container,
    ContextManager,
    Coroutine,
    Counter,
    DefaultDict,
    Deque,
    Dict,
    FrozenSet,
    Generator,
    Generic,
    ItemsView,
    Iterable,
    Iterator,
    KeysView,
    List,
    MappingView,
    Mapping,
    Match,
    MutableMapping,
    MutableSequence,
    MutableSet,
    Optional,
    Pattern,
    Reversible,
    Sequence,
    Set,
    Tuple,
    Type,
    Union,
    ValuesView,
)

# See the "beartype.cave" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ BASES                             }....................
# Conditionally add the "typing.ForwardRef" superclass depending on the
# current Python version, as this superclass was thankfully publicized
# under Python >= 3.7 after its initial privatization under Python <= 3.6.
HINT_PEP484_TYPE_FORWARDREF = (
    typing.ForwardRef if IS_PYTHON_AT_LEAST_3_7 else
    typing._ForwardRef  # type: ignore [attr-defined]
)
'''
**Forward reference sign** (i.e., arbitrary objects uniquely identifying a
:pep:`484`-compliant type hint unifying one or more subscripted type hint
arguments into a disjunctive set union of these arguments).
'''

# ....................{ HINTS                             }....................
HINT_PEP484_TUPLE_EMPTY = Tuple[()]
'''
:pep:`484`-compliant empty fixed-length tuple type hint.
'''

# ....................{ SETS ~ attr                       }....................
HINT_PEP484_ATTRS_DEPRECATED: FrozenSet[Any] = frozenset()
'''
Frozen set of all :pep:`484`-compliant **deprecated typing attributes** (i.e.,
:pep:`484`-compliant :mod:`typing` type hints obsoleted by more recent PEPs).
'''

# ....................{ SETS ~ sign : type                }....................
# Initialized by the _init() function below due to conditional complexity.
HINT_PEP484_ATTRS_ISINSTANCEABLE: frozenset = None  # type: ignore[assignment]
'''
Frozen set of all :pep:`484`-compliant **standard class signs** (i.e.,
instances of the builtin :mod:`type` type uniquely identifying PEP-compliant
type hints).
'''


# Initialized by the _init() function below due to conditional complexity.
HINT_PEP484_SIGNS_TYPE_ORIGIN: frozenset = None  # type: ignore[assignment]
'''
Frozen set of all signs uniquely identifying :pep:`484`-compliant type hints
originating from an origin type.
'''

# ....................{ INITIALIZERS                      }....................
def _init() -> None:
    '''
    Initialize this submodule.
    '''

    # ..................{ GLOBALS                           }..................
    # Submodule globals to be redefined below.
    global \
        HINT_PEP484_ATTRS_DEPRECATED, \
        HINT_PEP484_ATTRS_ISINSTANCEABLE, \
        HINT_PEP484_SIGNS_TYPE_ORIGIN

    # ..................{ SETS ~ signs : type : origin      }..................
    # List of all signs uniquely identifying PEP 484-compliant type hints
    # originating from an origin type.
    _HINT_PEP484_SIGNS_TYPE_ORIGIN_LIST = [
        AbstractSet,
        AsyncGenerator,
        AsyncIterable,
        AsyncIterator,
        Awaitable,
        ByteString,
        Callable,
        ChainMap,
        Collection,
        Container,
        ContextManager,
        Coroutine,
        Counter,
        DefaultDict,
        Deque,
        Dict,
        FrozenSet,
        Generator,
        ItemsView,
        Iterable,
        Iterator,
        KeysView,
        List,
        MappingView,
        Mapping,
        Match,
        MutableMapping,
        MutableSequence,
        MutableSet,
        Pattern,
        Reversible,
        Sequence,
        Set,
        Tuple,
        Type,
        ValuesView,
    ]

    # If the active Python interpreter targets at least various Python
    # versions, add PEP 484-specific signs introduced in those versions.
    if IS_PYTHON_AT_LEAST_3_7:
        _HINT_PEP484_SIGNS_TYPE_ORIGIN_LIST.extend((
            typing.AsyncContextManager,

            # Although the Python 3.6-specific implementation of the "typing"
            # module *DOES* technically supply these attributes, it does so
            # only non-deterministically. For unknown reasons (whose underlying
            # cause appears to be unwise abuse of private fields of the
            # critical stdlib "abc.ABCMeta" metaclass), the "typing.Hashable"
            # and "typing.Sized" abstract base classes (ABCs) spontaneously
            # interchange themselves with the corresponding
            # "collections.abc.Hashable" and "collections.abc.Sized" ABCs after
            # indeterminate importations and/or reference to these ABCs.
            #
            # This issue is significantly concerning that we would ideally
            # simply drop Python 3.6 support. Unfortunately, that would also
            # mean dropping PyPy3 support, which has yet to stabilize Python
            # 3.7 support. Ergo, we reluctantly preserve Python 3.6 and thus
            # PyPy3 support for the interim.
            typing.Hashable,
            typing.Sized,
        ))

        # If the active Python interpreter targets Python >= 3.7.2...
        #
        # Note that this is the *ONLY* test against Python >= 3.7.2 in the
        # codebase and thus done manually rather than with a global boolean.
        if version_info >= (3, 7, 2):
            # Add the "typing.OrderedDict" sign first introduced by the patch
            # release Python 3.7.2. Yes, this is insane. Yes, this is "typing".
            _HINT_PEP484_SIGNS_TYPE_ORIGIN_LIST.append(typing.OrderedDict)

    # Coerce this list into a frozen set for subsequent constant-time lookup.
    HINT_PEP484_SIGNS_TYPE_ORIGIN = frozenset(
        _HINT_PEP484_SIGNS_TYPE_ORIGIN_LIST)

    # ..................{ SETS ~ signs                      }..................
    HINT_PEP484_ATTRS_ISINSTANCEABLE = frozenset((
        # The "Generic" superclass is explicitly equivalent in PEP 484 to the
        # "Generic[Any]" subscription and thus valid as a standard class sign.
        Generic,
    )) | (
        # If the active Python interpreter targets Python 3.6, add all signs
        # uniquely identifying PEP 484-compliant type hints originating from an
        # origin type to the set of all standard class signs. Insanely, the
        # Python 3.6 implementation of the "typing" module defines *ALL* these
        # signs as unique public classes.
        HINT_PEP484_SIGNS_TYPE_ORIGIN if IS_PYTHON_3_6 else frozenset()
    )

    # If the active Python interpreter targets at least Python >= 3.9 and thus
    # supports PEP 585, add all signs uniquely identifying outdated PEP
    # 484-compliant type hints (e.g., "typing.List[int]") that have since been
    # obsoleted by the equivalent PEP 585-compliant type hints (e.g.,
    # "list[int]"). Happily, this is exactly the set of all PEP 484-compliant
    # signs uniquely identifying PEP 484-compliant type hints originating from
    # origin types.
    if IS_PYTHON_AT_LEAST_3_9:
        HINT_PEP484_ATTRS_DEPRECATED = HINT_PEP484_SIGNS_TYPE_ORIGIN


# Initialize this submodule.
_init()
