#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2022 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype** :mod:`typing` **compatibility layer.**

This submodule declares the exact same set of **public typing attributes**
(i.e., module-scoped attributes listed by the :attr:`typing.__all__` global) as
declared by the :mod:`typing` module for your current Python version. Although
the attributes declared by this submodule *mostly* share the same values as
the attributes declared by :mod:`typing`, notable differences include:

* :pep:`585`-deprecated typing attributes. :pep:`585` deprecated **38 public
  typing attributes** to "...be removed from the typing module in the first
  Python version released 5 years after the release of Python 3.9.0." This
  submodule preserves those attributes under their original names for the
  Python 3.8-specific version of the :mod:`typing` module, thus preserving
  forward compatibility with future Python versions. These include:

  * :attr:`typing.AbstractSet`.
  * :attr:`typing.AsyncContextManager`.
  * :attr:`typing.AsyncGenerator`.
  * :attr:`typing.AsyncIterable`.
  * :attr:`typing.AsyncIterator`.
  * :attr:`typing.Awaitable`.
  * :attr:`typing.ByteString`.
  * :attr:`typing.Callable`.
  * :attr:`typing.ChainMap`.
  * :attr:`typing.Collection`.
  * :attr:`typing.Container`.
  * :attr:`typing.ContextManager`.
  * :attr:`typing.Coroutine`.
  * :attr:`typing.Counter`.
  * :attr:`typing.DefaultDict`.
  * :attr:`typing.Deque`.
  * :attr:`typing.Dict`.
  * :attr:`typing.FrozenSet`.
  * :attr:`typing.Generator`.
  * :attr:`typing.ItemsView`.
  * :attr:`typing.Iterable`.
  * :attr:`typing.Iterator`.
  * :attr:`typing.KeysView`.
  * :attr:`typing.List`.
  * :attr:`typing.Mapping`.
  * :attr:`typing.MappingView`.
  * :attr:`typing.Match`.
  * :attr:`typing.MutableMapping`.
  * :attr:`typing.MutableSequence`.
  * :attr:`typing.MutableSet`.
  * :attr:`typing.OrderedDict`.
  * :attr:`typing.Pattern`.
  * :attr:`typing.Reversible`.
  * :attr:`typing.Set`.
  * :attr:`typing.Tuple`.
  * :attr:`typing.Type`.
  * :attr:`typing.Sequence`.
  * :attr:`typing.ValuesView`.

Usage
----------
:mod:`beartype` users are strongly encouraged to import typing attributes from
this submodule rather than from :mod:`typing` directly: e.g.,

.. code-block:: python

   # Instead of this...
   from typing import Tuple, List, Dict, Set, FrozenSet, Type

   # ...always do this.
   from beartype.typing import Tuple, List, Dict, Set, FrozenSet, Type
'''

# ....................{ IMPORTS                           }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To avoid polluting the public module namespace, external attributes
# *NOT* intended for public importation should be locally imported at module
# scope *ONLY* under alternate private names (e.g., "import re as _re" rather
# than merely "from re").
# WARNING: To preserve PEP 561 compliance with static type checkers (e.g.,
# mypy), external attributes *MUST* be explicitly imported with standard static
# import machinery rather than non-standard dynamic import shenanigans (e.g.,
# "from typing import Annotated" rather than
# "import_typing_attr_or_none('Annotated')").
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from beartype._util.py.utilpyversion import (
    IS_PYTHON_AT_LEAST_3_7   as _IS_PYTHON_AT_LEAST_3_7,
    IS_PYTHON_AT_LEAST_3_7_2 as _IS_PYTHON_AT_LEAST_3_7_2,
    IS_PYTHON_AT_LEAST_3_8   as _IS_PYTHON_AT_LEAST_3_8,
    IS_PYTHON_AT_LEAST_3_9   as _IS_PYTHON_AT_LEAST_3_9,
    IS_PYTHON_AT_LEAST_3_10  as _IS_PYTHON_AT_LEAST_3_10,
)

# ....................{ IMPORTS ~ all                     }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To prevent "mypy --no-implicit-reexport" from raising literally
# hundreds of errors at static analysis time, *ALL* public attributes *MUST* be
# explicitly reimported under the same names with "{exception_name} as
# {exception_name}" syntax rather than merely "{exception_name}". Yes, this is
# ludicrous. Yes, this is mypy. For posterity, these failures resemble:
#     beartype/_cave/_cavefast.py:47: error: Module "beartype.roar" does not
#     explicitly export attribute "BeartypeCallUnavailableTypeException";
#     implicit reexport disabled  [attr-defined]
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# Import all public attributes of the "typing" module both available under all
# supported Python versions and *NOT* deprecated by a subsequent Python version
# under their original names.
from typing import (
    TYPE_CHECKING as TYPE_CHECKING,
    Any as Any,
    AnyStr as AnyStr,
    NewType as NewType,
    Text as Text,
    BinaryIO as BinaryIO,
    ClassVar as ClassVar,
    Generic as Generic,
    Hashable as Hashable,
    IO as IO,
    Match as Match,
    NamedTuple as NamedTuple,
    NewType as NewType,
    NoReturn as NoReturn,
    Optional as Optional,
    Pattern as Pattern,
    Sized as Sized,
    SupportsAbs as SupportsAbs,
    SupportsBytes as SupportsBytes,
    SupportsComplex as SupportsComplex,
    SupportsFloat as SupportsFloat,
    SupportsInt as SupportsInt,
    SupportsRound as SupportsRound,
    Text as Text,
    TextIO as TextIO,
    TypeVar as TypeVar,
    Union as Union,
    cast as cast,
    get_type_hints as get_type_hints,
    no_type_check as no_type_check,
    no_type_check_decorator as no_type_check_decorator,
    overload as overload,
)

# ....................{ IMPORTS ~ version                 }....................
# Import all public attributes of the "typing" module both available under a
# subset of supported Python versions and *NOT* deprecated by a subsequent
# Python version under their original names.

# If the active Python interpreter targets Python >= 3.7...
if _IS_PYTHON_AT_LEAST_3_7:
    from typing import (
        ForwardRef as ForwardRef,
    )

    # If the active Python interpreter targets Python >= 3.8...
    if _IS_PYTHON_AT_LEAST_3_8:
        from typing import (  # type: ignore[attr-defined]
            Final as Final,
            Literal as Literal,
            Protocol as Protocol,
            Reversible as Reversible,
            SupportsIndex as SupportsIndex,
            TypedDict as TypedDict,
            final as final,
            get_args as get_args,
            get_origin as get_origin,
            runtime_checkable as runtime_checkable,
        )

        # If the active Python interpreter targets Python >= 3.10...
        if _IS_PYTHON_AT_LEAST_3_10:
            from typing import (  # type: ignore[attr-defined]
                Concatenate as Concatenate,
                ParamSpec as ParamSpec,
                ParamSpecArgs as ParamSpecArgs,
                ParamSpecKwargs as ParamSpecKwargs,
                TypeAlias as TypeAlias,
                TypeGuard as TypeGuard,
                is_typeddict as is_typeddict,
            )

# ....................{ PEP ~ 585                         }....................
# If the active Python interpreter targets Python < 3.9 and thus fails to
# support PEP 585, import *ALL* public attributes of the "typing" module
# deprecated by PEP 585 as their original values.
#
# This is intentionally performed *BEFORE* the corresponding "else:" branch
# below handling the Python >= 3.9 case. Why? Because mypy. If the order of
# these two branches is reversed, mypy emits errors under Python < 3.9 when
# attempting to subscript any of the builtin types (e.g., "Tuple"): e.g.,
#     error: "tuple" is not subscriptable  [misc]
if not _IS_PYTHON_AT_LEAST_3_9:
    from typing import (
        AbstractSet as AbstractSet,
        AsyncContextManager as AsyncContextManager,
        AsyncGenerator as AsyncGenerator,
        AsyncIterable as AsyncIterable,
        AsyncIterator as AsyncIterator,
        Awaitable as Awaitable,
        ByteString as ByteString,
        Callable as Callable,
        ChainMap as ChainMap,
        Collection as Collection,
        Container as Container,
        ContextManager as ContextManager,
        Coroutine as Coroutine,
        Counter as Counter,
        DefaultDict as DefaultDict,
        Deque as Deque,
        Dict as Dict,
        FrozenSet as FrozenSet,
        Generator as Generator,
        ItemsView as ItemsView,
        Iterable as Iterable,
        Iterator as Iterator,
        KeysView as KeysView,
        List as List,
        Mapping as Mapping,
        MappingView as MappingView,
        Match as Match,
        MutableMapping as MutableMapping,
        MutableSequence as MutableSequence,
        MutableSet as MutableSet,
        Pattern as Pattern,
        Reversible as Reversible,
        Set as Set,
        Tuple as Tuple,
        Type as Type,
        Sequence as Sequence,
        ValuesView as ValuesView,
    )

    # If the active Python interpreter targets Python >= 3.7.2, import *ALL*
    # public attributes of the "typing" module introduced by Python 3.7.2
    # deprecated by PEP 585 as their original values.
    if _IS_PYTHON_AT_LEAST_3_7_2:
        from typing import (  # type: ignore[attr-defined]
            OrderedDict as OrderedDict,
        )
# If the active Python interpreter targets Python >= 3.9 and thus supports PEP
# 585, alias *ALL* public attributes of the "typing" module deprecated by PEP
# 585 to their equivalent values elsewhere in the standard library.
else:
    from collections import (
        ChainMap as ChainMap,
        Counter as Counter,
        OrderedDict as OrderedDict,
        defaultdict as DefaultDict,
        deque as Deque,
    )
    from collections.abc import (
        AsyncIterable as AsyncIterable,
        AsyncIterator as AsyncIterator,
        AsyncGenerator as AsyncGenerator,
        Awaitable as Awaitable,
        ByteString as ByteString,
        Callable as Callable,
        Collection as Collection,
        Container as Container,
        Coroutine as Coroutine,
        Generator as Generator,
        ItemsView as ItemsView,
        Iterable as Iterable,
        Iterator as Iterator,
        KeysView as KeysView,
        Mapping as Mapping,
        MappingView as MappingView,
        MutableMapping as MutableMapping,
        MutableSequence as MutableSequence,
        MutableSet as MutableSet,
        Reversible as Reversible,
        Sequence as Sequence,
        ValuesView as ValuesView,
        Set as AbstractSet,
    )
    from contextlib import (
        AbstractContextManager as ContextManager,
        AbstractAsyncContextManager as AsyncContextManager,
    )
    from typing import (  # type: ignore[attr-defined]
        Annotated,
    )

    Dict = dict  # type: ignore[misc]
    FrozenSet = frozenset  # type: ignore[misc]
    List = list  # type: ignore[misc]
    Set = set  # type: ignore[misc]
    Tuple = tuple  # type: ignore[assignment]
    Type = type  # type: ignore[assignment]
