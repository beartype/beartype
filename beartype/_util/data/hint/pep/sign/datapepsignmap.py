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
from beartype._util.data.hint.pep.datapep import HINT_PEP_MODULE_NAMES
from beartype._util.data.hint.pep.sign import datapepsigns
from beartype._util.data.hint.pep.sign.datapepsigns import (
    HintSignAbstractSet,
    HintSignAsyncContextManager,
    HintSignAsyncIterable,
    HintSignAsyncIterator,
    HintSignAsyncGenerator,
    HintSignAwaitable,
    HintSignByteString,
    HintSignCallable,
    HintSignChainMap,
    HintSignCollection,
    HintSignContainer,
    HintSignCoroutine,
    HintSignContextManager,
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
    HintSignMapping,
    HintSignMappingView,
    HintSignMatch,
    HintSignMutableMapping,
    HintSignMutableSequence,
    HintSignMutableSet,
    HintSignOrderedDict,
    HintSignReversible,
    HintSignSequence,
    HintSignSet,
    HintSignPattern,
    HintSignTuple,
    HintSignType,
    HintSignTypeVar,
    HintSignValuesView,
)
from beartype._util.py.utilpyversion import (
    IS_PYTHON_AT_LEAST_3_9,
    IS_PYTHON_3_6,
)

# See the "beartype.cave" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ MAPPINGS ~ repr                   }....................
#FIXME: Actually, let's just one-shot unconditionally define this here. There's
#really *NO* demonstrable reason to try to do so with automation, which is
#implicit and almost certainly broken in edge cases and thus bad.

# Initialized below in the _init() function.
HINT_BARE_REPR_TO_SIGN = {}
'''
Dictionary mapping from the **bare PEP-compliant type hint representations**
(i.e., machine-readable strings returned by the :func:`repr` builtin suffixed
by *no* "["- and "]"-delimited subscription representations) of all hints
uniquely identifiable by those representations to their identifying signs.
'''

# ....................{ MAPPINGS ~ name                   }....................
#FIXME: Remove this entirely, please. This turned out to be overkill, because
#all of the classes mapped to below have sane repr() strings, which means we
#can simply map them with:
#
#    HINT_BARE_REPR_TO_SIGN = {
#        ...
#
#        # Under Python >= 3.7...
#        #
#        # Note that "repr(typing.Generic) == 'typing.Generic'" under Python
#        # 3.6, which is already handled by the above mapping.
#        "<class 'typing.Generic'>": HintSignGeneric,
#
#Note that unsubscripted "typing.List", et al. actually requires *NO* special
#handling under Python 3.6, because "repr(typing.List) == 'typing.List'". Wow;
#what the heck were we thinking there? </facepalm>
HINT_NAME_IF_TYPE_TO_SIGN = {
    # ..................{ PEP 484                           }..................
    # Identify the unsubscripted PEP 484-compliant "Generic" ABC (explicitly
    # equivalent under PEP 484 to the "Generic[Any]" subscription and thus
    # conveying meaningful semantics) by this sign.

    #FIXME: This is a bit odd. If an unsubscripted "typing.Protocol" is
    #ignorable, why wouldn't an unsubscripted "typing.Generic" be ignorable as
    #well? Consider excising this, please.
    'typing.Generic':            HintSignGeneric,
    'typing_extensions.Generic': HintSignGeneric,
}
'''
Dictionary mapping from the fully-qualified names of all PEP-compliant type
hints that are both classes and uniquely identifiable by those names to their
identifying signs.
'''

# If the active Python interpreter targets Python 3.6...
if IS_PYTHON_3_6:
    from beartype._util.data.hint.pep.sign.datapepsignset import (
        HINT_SIGNS_TYPE_STDLIB)

    # For the sign identifying each PEP 484-compliant type hint originating
    # from an origin type, map the unqualified name of that hint's attribute in
    # the "typing" module to that sign (e.g., from "List" to "HintSignList").
    # Insanely, the Python 3.6 version of the "typing" module idiosyncratically
    # defined both subscriptions and unsubscriptions of these hints as classes:
    #     >>> import typing
    #     >>> isinstance(typing.List, type)
    #     True     # <-- this is balls cray-cray
    #     >>> isinstance(typing.List[int], type)
    #     True     # <-- this is balls cray-crayer
    HINT_NAME_IF_TYPE_TO_SIGN.update({
        f'typing.{hint_sign_type_stdlib.name}': hint_sign_type_stdlib
        for hint_sign_type_stdlib in HINT_SIGNS_TYPE_STDLIB
    })

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

    # If the active Python interpreter is Python >= 3.9, also map from the
    # unsubscripted name of each class now subscriptable as a PEP 585-compliant
    # generic alias type hint to the sign identifying that class.
    if IS_PYTHON_AT_LEAST_3_9:
        HINT_BARE_REPR_TO_SIGN.update({
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
