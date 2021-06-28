#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2021 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **bare PEP-compliant type hint representations** (i.e., global
constants pertaining to machine-readable strings returned by the :func:`repr`
builtin suffixed by *no* "["- and "]"-delimited subscription representations).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                           }....................
from beartype._cave._cavefast import NoneType
from beartype._util.data.hint.pep.sign import datapepsigns
from beartype._util.data.hint.pep.sign.datapepsigns import (
    HintSignAbstractSet,
    # HintSignAnnotated,
    # HintSignAny,
    HintSignAsyncContextManager,
    HintSignAsyncIterable,
    HintSignAsyncIterator,
    HintSignAsyncGenerator,
    HintSignAwaitable,
    HintSignByteString,
    HintSignCallable,
    HintSignChainMap,
    # HintSignClassVar,
    HintSignCollection,
    # HintSignConcatenate,
    HintSignContainer,
    HintSignCoroutine,
    HintSignContextManager,
    HintSignCounter,
    HintSignDefaultDict,
    HintSignDeque,
    HintSignDict,
    # HintSignFinal,
    HintSignForwardRef,
    HintSignFrozenSet,
    HintSignGenerator,
    HintSignGeneric,
    # HintSignHashable,
    HintSignItemsView,
    HintSignIterable,
    HintSignIterator,
    HintSignKeysView,
    HintSignList,
    # HintSignLiteral,
    HintSignMapping,
    HintSignMappingView,
    HintSignMatch,
    HintSignMutableMapping,
    HintSignMutableSequence,
    HintSignMutableSet,
    # HintSignNamedTuple,
    # HintSignNewType,
    # HintSignOptional,
    HintSignOrderedDict,
    # HintSignParamSpec,
    # HintSignParamSpecArgs,
    # HintSignProtocol,
    HintSignReversible,
    HintSignSequence,
    HintSignSet,
    # HintSignSized,
    HintSignPattern,
    HintSignTuple,
    HintSignType,
    HintSignTypeVar,
    # HintSignTypedDict,
    # HintSignUnion,
    HintSignValuesView,
)
from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_9
from typing import FrozenSet, Set

# See the "beartype.cave" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ MAPPINGS ~ repr                   }....................
# The majority of this dictionary is initialized with automated inspection
# below in the _init() function. The *ONLY* key-value pairs explicitly defined
# here are those *NOT* amenable to such inspection.
HINT_BARE_REPR_TO_SIGN = {
    # ..................{ PEP 484                           }..................
    #FIXME: This is a bit odd. If an unsubscripted "typing.Protocol" is
    #ignorable, why wouldn't an unsubscripted "typing.Generic" be ignorable as
    #well? Consider excising this, please.

    # Identify the unsubscripted PEP 484-compliant "Generic" ABC (explicitly
    # equivalent under PEP 484 to the "Generic[Any]" subscription and thus
    # possibly conveying meaningful semantics) by this sign.
    # Under ...
    #
    # Note this *ONLY* applies to Python >= 3.7. Under Python 3.6,
    # "repr(typing.Generic) == 'typing.Generic'", which is thus already handled
    # by automated inspection below.
    # "<class 'typing.Generic'>":            HintSignGeneric,
    # "<class 'typing_extensions.Generic'>": HintSignGeneric,

    # ..................{ PEP 585                           }..................
    # For synchronicity, these key-value pairs are intentionally defined in the
    # same order as the official list in PEP 585 itself.
    'tuple': HintSignTuple,
    'list': HintSignList,
    'dict': HintSignDict,
    'set': HintSignSet,
    'frozenset': HintSignFrozenSet,
    'type': HintSignType,
    'collections.deque': HintSignDeque,
    'collections.defaultdict': HintSignDefaultDict,
    'collections.OrderedDict': HintSignOrderedDict,
    'collections.Counter': HintSignCounter,
    'collections.ChainMap': HintSignChainMap,
    'collections.abc.Awaitable': HintSignAwaitable,
    'collections.abc.Coroutine': HintSignCoroutine,
    'collections.abc.AsyncIterable': HintSignAsyncIterable,
    'collections.abc.AsyncIterator': HintSignAsyncIterator,
    'collections.abc.AsyncGenerator': HintSignAsyncGenerator,
    'collections.abc.Iterable': HintSignIterable,
    'collections.abc.Iterator': HintSignIterator,
    'collections.abc.Generator': HintSignGenerator,
    'collections.abc.Reversible': HintSignReversible,
    'collections.abc.Container': HintSignContainer,
    'collections.abc.Collection': HintSignCollection,
    'collections.abc.Callable': HintSignCallable,
    'collections.abc.Set': HintSignAbstractSet,
    'collections.abc.MutableSet': HintSignMutableSet,
    'collections.abc.Mapping': HintSignMapping,
    'collections.abc.MutableMapping': HintSignMutableMapping,
    'collections.abc.Sequence': HintSignSequence,
    'collections.abc.MutableSequence': HintSignMutableSequence,
    'collections.abc.ByteString': HintSignByteString,
    'collections.abc.MappingView': HintSignMappingView,
    'collections.abc.KeysView': HintSignKeysView,
    'collections.abc.ItemsView': HintSignItemsView,
    'collections.abc.ValuesView': HintSignValuesView,
    'contextlib.AbstractContextManager': HintSignContextManager,
    'contextlib.AbstractAsyncContextManager': HintSignAsyncContextManager,
    're.Pattern': HintSignPattern,
    're.Match': HintSignMatch,
}
'''
Dictionary mapping from the **bare PEP-compliant type hint representations**
(i.e., machine-readable strings returned by the :func:`repr` builtin suffixed
by *no* "["- and "]"-delimited subscription representations) of all hints
uniquely identifiable by those representations to their identifying signs.
'''

# ....................{ MAPPINGS ~ type                   }....................
# The majority of this dictionary is initialized with automated inspection
# below in the _init() function. The *ONLY* key-value pairs explicitly defined
# here are those *NOT* amenable to such inspection.
HINT_TYPE_NAME_TO_SIGN = {
    # ..................{ PEP 484                           }..................
    # Identify the PEP 484-compliant "None" singleton by the type of that
    # singleton. Although we could identify this singleton by an ad-hoc
    # "HintSignNone" or "HintSignNoneType" object, doing so would be senseless;
    # under PEP 484, this singleton is simply an alias for the "NoneType" class
    # and otherwise conveys *NO* meaningful semantics.
    'NoneType': NoneType,
}
'''
Dictionary mapping from the fully-qualified classnames of all PEP-compliant
type hints uniquely identifiable by those classnames to their identifying
signs.
'''

# ....................{ SETS                              }....................
# Initialized with automated inspection below in the _init() function.
HINT_PEP_BARE_REPRS_DEPRECATED: FrozenSet[str] = None  # type: ignore[assignment]
'''
Frozen set of all **bare deprecated PEP-compliant type hint representations**
(i.e., machine-readable strings returned by the :func:`repr` builtin suffixed
by *no* "["- and "]"-delimited subscription representations for all obsoleted
hints, often by equivalent hints standardized under more recent PEPs).
'''


# Initialized with automated inspection below in the _init() function.
HINT_PEP484_BARE_REPRS_DEPRECATED: FrozenSet[str] = None  # type: ignore[assignment]
'''
Frozen set of all **bare deprecated** :pep:`484`-compliant **type hint
representations** (i.e., machine-readable strings returned by the :func:`repr`
builtin suffixed by *no* "["- and "]"-delimited subscription representations
for all :pep:`484`-compliant type hints obsoleted by :pep:`585`-compliant
subscriptable classes).
'''

# ....................{ INITIALIZERS                      }....................
def _init() -> None:
    '''
    Initialize this submodule.
    '''

    # ..................{ EXTERNALS                         }..................
    # Defer initialization-specific imports.
    from beartype._util.data.hint.pep.datapepmodule import (
        HINT_PEP_MODULE_NAMES)

    # Permit redefinition of these globals below.
    global HINT_PEP_BARE_REPRS_DEPRECATED

    # ..................{ CONSTANTS                         }..................
    # Length of the ignorable substring prefixing the name of each sign.
    _HINT_SIGN_PREFIX_LEN = len('HintSign')

    # Set of the unqualified names of all deprecated PEP 484-compliant typing
    # attributes.
    _HINT_PEP484_TYPING_ATTR_NAMES_DEPRECATED: Set[str] = {}

    # If the active Python interpreter targets Python >= 3.9 and thus
    # supports PEP 585, add the names of all deprecated PEP 484-compliant
    # typing attributes (e.g., "typing.List") that have since been obsoleted by
    # equivalent bare PEP 585-compliant builtin classes (e.g., "list").
    if IS_PYTHON_AT_LEAST_3_9:
        _HINT_PEP484_TYPING_ATTR_NAMES_DEPRECATED.update((
            # ..............{ PEP 484                           }..............
            'AbstractSet',
            'AsyncContextManager',
            'AsyncGenerator',
            'AsyncIterable',
            'AsyncIterator',
            'Awaitable',
            'ByteString',
            'Callable',
            'ChainMap',
            'Collection',
            'Container',
            'ContextManager',
            'Coroutine',
            'Counter',
            'DefaultDict',
            'Deque',
            'Dict',
            'FrozenSet',
            'Generator',
            'Hashable',
            'ItemsView',
            'Iterable',
            'Iterator',
            'KeysView',
            'List',
            'MappingView',
            'Mapping',
            'Match',
            'MutableMapping',
            'MutableSequence',
            'MutableSet',
            'OrderedDict',
            'Pattern',
            'Reversible',
            'Sequence',
            'Set',
            'Sized',
            'Tuple',
            'Type',
            'ValuesView',
        ))

    # Dictionary mapping from the unqualified name of each classes defined by
    # typing modules uniquely identifying PEP-compliant type hints to their
    # corresponding signs.
    _HINT_TYPE_BASENAMES_TO_SIGN = {
        # ................{ PEP 484                           }................
        # All PEP 484-compliant forward references are necessarily instances of
        # the same class.
        'ForwardRef': HintSignForwardRef,

        # The unsubscripted PEP 484-compliant "Generic" superclass is
        # explicitly equivalent under PEP 484 to the "Generic[Any]"
        # subscription and thus slightly conveys meaningful semantics.
        'Generic': HintSignGeneric,

        # All PEP 484-compliant type variables are necessarily instances of the
        # same class.
        'TypeVar': HintSignTypeVar,
    }

    # ..................{ CONSTRUCTION                      }..................
    # For the name of each top-level hinting module...
    for typing_module_name in HINT_PEP_MODULE_NAMES:
        # For each bare relative deprecated PEP 484-compliant representation...
        for typing_attr_name in _HINT_PEP484_TYPING_ATTR_NAMES_DEPRECATED:
            # Add that attribute relative to this module to this set.
            HINT_PEP484_BARE_REPRS_DEPRECATED.add(
                f'{typing_module_name}.{typing_attr_name}')

        # For the name of each sign and that sign...
        for hint_sign_name, hint_sign in datapepsigns.__dict__.items():
            # Unqualified name of the typing attribute identified by this sign.
            typing_attr_name = hint_sign_name[_HINT_SIGN_PREFIX_LEN:]

            # Map from that attribute in this module to this sign.
            HINT_BARE_REPR_TO_SIGN[
                f'{typing_module_name}.{typing_attr_name}'] = hint_sign

        # For the unqualified classname identifying each sign to that sign...
        for hint_type_basename, hint_sign in (
            _HINT_TYPE_BASENAMES_TO_SIGN.items()):
            # Map from that classname in this module to this sign.
            HINT_TYPE_NAME_TO_SIGN[
                f'{typing_module_name}.{hint_type_basename}'] = hint_sign

    # ..................{ SYNTHESIS                         }..................
    # Synthesize the frozen set of all bare deprecated PEP-compliant type hint
    # representations from lower-level PEP-specific sets.
    HINT_PEP_BARE_REPRS_DEPRECATED = frozenset(
        HINT_PEP484_BARE_REPRS_DEPRECATED)

# Initialize this submodule.
_init()
