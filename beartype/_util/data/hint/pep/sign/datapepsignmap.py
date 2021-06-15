#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2021 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **PEP-compliant type hint sign mappings** (i.e., dictionary
globals mapping to and fro instances of the
:class:`beartype._util.data.hint.pep.sign.datapepsigncls.HintSign` class,
enabling efficient mapping between non-signs and their associated signs).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                           }....................
from beartype._util.data.hint.pep.datapep import HINT_PEP_MODULE_NAMES
from beartype._util.data.hint.pep.sign import datapepsigns
from beartype._util.data.hint.pep.sign.datapepsigns import (
    HintSignTuple,
    HintSignList,
    HintSignDict,
    HintSignSet,
    HintSignFrozenSet,
    HintSignType,
    HintSignDeque,
    HintSignDefaultDict,
    HintSignOrderedDict,
    HintSignCounter,
    HintSignChainMap,
    HintSignAwaitable,
    HintSignCoroutine,
    HintSignAsyncIterable,
    HintSignAsyncIterator,
    HintSignAsyncGenerator,
    HintSignIterable,
    HintSignIterator,
    HintSignGenerator,
    HintSignReversible,
    HintSignContainer,
    HintSignCollection,
    HintSignCallable,
    HintSignAbstractSet,
    HintSignMutableSet,
    HintSignMapping,
    HintSignMutableMapping,
    HintSignSequence,
    HintSignMutableSequence,
    HintSignByteString,
    HintSignMappingView,
    HintSignKeysView,
    HintSignItemsView,
    HintSignValuesView,
    HintSignContextManager,
    HintSignAsyncContextManager,
    HintSignPattern,
    HintSignMatch,
)
from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_9

# See the "beartype.cave" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ SETS ~ sequence                   }....................
# Initialized below in the _init() function.
HINT_BARE_NAME_TO_SIGN = {}
'''
Dictionary mapping from the unsubscripted machine-readable representations
(i.e., strings returned by the :func:`repr` builtin suffixed by *no* "["- and
"]"-delimited subscription representations) of all **typing origins** (i.e.,
public attributes of any implementation of the :mod:`typing` module currently
supported by this version of this project) to their identifying signs.
'''

# ....................{ INITIALIZERS                      }....................
def _init() -> None:
    '''
    Initialize this submodule.
    '''

    # Length of the ignorable substring prefixing the name of each sign.
    SIGN_PREFIX_LEN = len('HintSign')

    # For the name of each sign and that sign...
    for sign_name, sign in datapepsigns.__dict__.items():
        # Unsubscripted name of the "typing" attribute identified by this sign.
        typing_attr_name = sign_name[SIGN_PREFIX_LEN:]

        # For the name of each top-level hinting modules (i.e., module whose
        # attributes are usable for creating PEP-compliant type hints
        # officially accepted by both static and runtime type checkers)...
        for typing_module_name in HINT_PEP_MODULE_NAMES:
            # Map from that attribute to this sign.
            HINT_BARE_NAME_TO_SIGN[
                f'{typing_module_name}.{typing_attr_name}'] = sign

    # If the active Python interpreter is Python >= 3.9, also map from the
    # unsubscripted name of each class now subscriptable as a PEP 585-compliant
    # generic alias type hint to the sign identifying that class.
    if IS_PYTHON_AT_LEAST_3_9:
        HINT_BARE_NAME_TO_SIGN.update({
            # For synchronicity, these key-value pairs are intentionally defined
            # in the same order as the list in PEP 585.
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
        })

# Initialize this submodule.
_init()
