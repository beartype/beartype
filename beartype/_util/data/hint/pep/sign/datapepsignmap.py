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
from beartype._util.py.utilpyversion import IS_PYTHON_3_6

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

# ....................{ MAPPINGS ~ type : name            }....................
HINT_TYPE_NAME_TO_SIGN = {
    # ..................{ PEP 484                           }..................
    # Identify all PEP 484-compliant forward references (which are necessarily
    # instances of the same class) by this sign.
    'typing.ForwardRef':            HintSignForwardRef,
    'typing_extensions.ForwardRef': HintSignForwardRef,

    # Identify the unsubscripted PEP 484-compliant "Generic" superclass (which
    # is explicitly equivalent under PEP 484 to the "Generic[Any]"
    # subscription and thus slightly conveys meaningful semantics) by this
    # sign.
    'typing.Generic':            HintSignGeneric,
    'typing_extensions.Generic': HintSignGeneric,

    # Identify all PEP 484-compliant type variables (which are necessarily
    # instances of the same class) by this sign.
    'typing.TypeVar':            HintSignTypeVar,
    'typing_extensions.TypeVar': HintSignTypeVar,

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

# ....................{ INITIALIZERS                      }....................
def _init() -> None:
    '''
    Initialize this submodule.
    '''

    # Tuple of the names of *ALL* typing modules (i.e., modules declaring
    # official PEP-compliant type hints) regardless of whether those modules
    # are actually installed.
    HINT_PEP_MODULE_NAMES = ('typing', 'typing_extensions')

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
            HINT_BARE_REPR_TO_SIGN[
                f'{typing_module_name}.{typing_attr_name}'] = sign

# Initialize this submodule.
_init()
