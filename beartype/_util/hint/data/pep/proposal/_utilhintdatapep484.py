#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2020 Cecil Curry.
# See "LICENSE" for further details.

'''
**Beartype `PEP 484`_**-compliant type hint data.**

This private submodule is *not* intended for importation by downstream callers.

.. _PEP 484:
    https://www.python.org/dev/peps/pep-0484
'''

# ....................{ IMPORTS                           }....................
import typing
from beartype._util.py.utilpyversion import (
    IS_PYTHON_AT_LEAST_3_7,
    IS_PYTHON_AT_LEAST_3_8,
)
from typing import (
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
    SupportsAbs,
    SupportsBytes,
    SupportsComplex,
    SupportsInt,
    SupportsFloat,
    SupportsRound,
    Tuple,
    Type,
    ValuesView,
)

# See the "beartype.__init__" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ ADDERS                            }....................
def add_data(data_module: 'ModuleType') -> None:
    '''
    Add `PEP 484`_**-compliant type hint data to various global containers
    declared by the passed module.

    Parameters
    ----------
    data_module : ModuleType
        Module to be added to.

    .. _PEP 484:
        https://www.python.org/dev/peps/pep-0484
    '''

    # ..................{ SETS ~ type                       }..................
    data_module.HINT_PEP_SIGNS_TYPE_ORIGIN.update({
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
        SupportsAbs,
        SupportsBytes,
        SupportsComplex,
        SupportsInt,
        SupportsFloat,
        SupportsRound,
        Tuple,
        Type,
        ValuesView,
    })

    # If the active Python interpreter targets at least various Python
    # versions, add PEP 484-specific signs introduced in those versions.
    if IS_PYTHON_AT_LEAST_3_7:
        data_module.HINT_PEP_SIGNS_TYPE_ORIGIN.update({
            typing.AsyncContextManager,
            typing.OrderedDict,

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
        })

        if IS_PYTHON_AT_LEAST_3_8:
            data_module.HINT_PEP_SIGNS_TYPE_ORIGIN.update({
                typing.SupportsIndex,
            })

    # ..................{ SETS ~ supported                  }..................
    data_module.HINT_PEP_SIGNS_DEEP_SUPPORTED.update({
        typing.Generic,
        typing.List,
        typing.MutableSequence,
        typing.Sequence,
        typing.Tuple,

        # Note that "typing.Union" implicitly subsumes "typing.Optional" *ONLY*
        # under Python <= 3.9. The implementations of the "typing" module under
        # those older Python versions transparently reduced "typing.Optional"
        # to "typing.Union" at runtime. Since this reduction is no longer the
        # case, both *MUST* now be explicitly listed here.
        typing.Optional,
        typing.Union,
    })

    # ..................{ SETS ~ category                   }..................
    data_module.HINT_PEP_SIGNS_SEQUENCE_STANDARD.update({
        typing.List,
        typing.MutableSequence,
        typing.Sequence,
    })
    data_module.HINT_PEP_SIGNS_UNION.update({
        typing.Optional,
        typing.Union,
    })
