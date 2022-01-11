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

# ....................{ TODO                              }....................
#FIXME: Document us in "README.rst", please.

# ....................{ IMPORTS                           }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To avoid polluting the public module namespace, external attributes
# *NOT* intended for public importation should be locally imported at module
# scope *ONLY* under alternate private names (e.g., "import re as _re" rather
# than merely "from re").
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To preserve PEP 561 compliance with static type checkers (e.g.,
# mypy), external attributes *MUST* be explicitly imported with standard static
# import machinery rather than non-standard dynamic import shenanigans (e.g.,
# "from typing import Annotated" rather than
# "import_typing_attr_or_none('Annotated')").
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# Import all public attributes of the "typing" module both available under all
# supported Python versions and *NOT* deprecated by a subsequent Python version
# under their original names.
from typing import (
    TYPE_CHECKING,
    Any,
    AnyStr,
    NewType,
    Text,
    BinaryIO,
    ClassVar,
    ForwardRef,
    Generic,
    Hashable,
    IO,
    Match,
    NamedTuple,
    NewType,
    NoReturn,
    Optional,
    Pattern,
    Sized,
    SupportsAbs,
    SupportsBytes,
    SupportsComplex,
    SupportsFloat,
    SupportsIndex,
    SupportsInt,
    SupportsRound,
    Text,
    TextIO,
    TypeVar,
    Union,
    cast,
    no_type_check,
    no_type_check_decorator,
    overload,
)

# ....................{ IMPORTS ~ private                 }....................
from beartype._util.py.utilpyversion import (
    IS_PYTHON_AT_LEAST_3_8 as _IS_PYTHON_AT_LEAST_3_8,
    IS_PYTHON_AT_LEAST_3_9 as _IS_PYTHON_AT_LEAST_3_9,
)

# ....................{ ALIASES                           }....................
# If the active Python interpreter targets Python >= 3.8...
if _IS_PYTHON_AT_LEAST_3_8:
    from typing import (  # type: ignore[attr-defined]
        Final,
        Literal,
        Protocol,
        Reversible,
        TypedDict,
        final,
        runtime_checkable,
    )

    # If the active Python interpreter targets Python >= 3.9 and thus supports
    # PEP 585, alias *ALL* public attributes of the "typing" module deprecated
    # by PEP 585 to their equivalent values elsewhere in the standard library.
    if _IS_PYTHON_AT_LEAST_3_9:
        from collections import (
            ChainMap,
            Counter,
            OrderedDict,
            defaultdict as DefaultDict,
            deque as Deque,
        )
        from collections.abc import (
            AsyncIterable,
            AsyncIterator,
            AsyncGenerator,
            Awaitable,
            ByteString,
            Callable,
            Collection,
            Container,
            Coroutine,
            Generator,
            ItemsView,
            Iterable,
            Iterator,
            KeysView,
            Mapping,
            MappingView,
            MutableMapping,
            MutableSequence,
            MutableSet,
            Reversible,
            Sequence,
            ValuesView,
            Set as AbstractSet,
        )
        from contextlib import (
            AbstractContextManager as ContextManager,
            AbstractAsyncContextManager as AsyncContextManager,
        )
        from typing import (  # type: ignore[attr-defined]
            Annotated,
        )

        Dict = dict
        FrozenSet = frozenset
        List = list
        Set = set
        Tuple = tuple
        Type = type
    # Else, the active Python interpreter targets Python < 3.9 and thus fails
    # to support PEP 585. In this case, import *ALL* public attributes of the
    # "typing" module deprecated by PEP 585 as their original values.
    else:
        from typing import (  # type: ignore[misc]
            AbstractSet,
            AsyncContextManager,
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
            Mapping,
            MappingView,
            Match,
            MutableMapping,
            MutableSequence,
            MutableSet,
            OrderedDict,
            Pattern,
            Reversible,
            Set,
            Tuple,
            Type,
            Sequence,
            ValuesView,
        )
