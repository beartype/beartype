#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype :mod:`typing` **compatibility layer.**

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

  * :obj:`typing.AbstractSet`.
  * :obj:`typing.AsyncContextManager`.
  * :obj:`typing.AsyncGenerator`.
  * :obj:`typing.AsyncIterable`.
  * :obj:`typing.AsyncIterator`.
  * :obj:`typing.Awaitable`.
  * :obj:`typing.ByteString`.
  * :obj:`typing.Callable`.
  * :obj:`typing.ChainMap`.
  * :obj:`typing.Collection`.
  * :obj:`typing.Container`.
  * :obj:`typing.ContextManager`.
  * :obj:`typing.Coroutine`.
  * :obj:`typing.Counter`.
  * :obj:`typing.DefaultDict`.
  * :obj:`typing.Deque`.
  * :obj:`typing.Dict`.
  * :obj:`typing.FrozenSet`.
  * :obj:`typing.Generator`.
  * :obj:`typing.ItemsView`.
  * :obj:`typing.Iterable`.
  * :obj:`typing.Iterator`.
  * :obj:`typing.KeysView`.
  * :obj:`typing.List`.
  * :obj:`typing.Mapping`.
  * :obj:`typing.MappingView`.
  * :obj:`typing.Match`.
  * :obj:`typing.MutableMapping`.
  * :obj:`typing.MutableSequence`.
  * :obj:`typing.MutableSet`.
  * :obj:`typing.OrderedDict`.
  * :obj:`typing.Pattern`.
  * :obj:`typing.Reversible`.
  * :obj:`typing.Set`.
  * :obj:`typing.Tuple`.
  * :obj:`typing.Type`.
  * :obj:`typing.Sequence`.
  * :obj:`typing.ValuesView`.

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

# ....................{ TODO                               }....................
#FIXME: Fundamentally generalize this submodule to optionally backport
#attributes from "typing_extensions" where available, resolving issue #237 at:
#    https://github.com/beartype/beartype/issues/237
#
#To do so, we'll basically want to discard the entire current implementation of
#this submodule in favour of a fundamentally superior approach resembling:
#    # In "beartype.typing.__init__": the future of typing backports begins today.
#    from typing import TYPE_CHECKING
#
#    # If @beartype is currently being statically type-checked (e.g.,
#    # by mypy or pyright), just defer to the third-party
#    # "typing_extensions" package.
#    #
#    # Note that this does *NOT* mean that @beartype now unconditionally
#    # requires "typing_extensions" at either runtime or static
#    # type-checking time. Any code in an "if TYPE_CHECKING:" is (basically)
#    # just a convincing semantic lie that everything syntactically ignores.
#    if TYPE_CHECKING:
#        from typing_extensions import *  # <-- heh
#    # Else, @beartype is currently being imported from at runtime. This is
#    # the common case. This is also the non-trivial case, because @beartype
#    # does *NOT* require "typing_extensions" as a mandatory runtime
#    # dependency, because @beartype requires *NOTHING* as a runtime
#    # dependency. This is the only rule in @beartype's Rule of Law.
#    else:
#        #FIXME: Unfortunately, to avoid circular import dependencies, these
#        #imports will need to be:
#        #* Moved into equivalent condensed submodules of a new
#        #  "beartype.typing._util" subpackage.
#        #* The original attributes in the "beartype._util" subpackage should
#        #  then quietly alias their new location in the "beartype.typing._util"
#        #  subpackage.
#
#        # Import the requisite machinery that will make the magic happen.
#        from beartype._util.hint.utilhintfactory import TypeHintTypeFactory
#        from beartype._util.api.standard.utiltyping import (
#            import_typing_attr_or_fallback as _import_typing_attr_or_fallback)
#
#        # Dynamically define the "Self" type hint as follows:
#        # * If the active Python interpreter targets Python >= 3.11, just
#        #   defer to the canonical "typing.Self" type hint.
#        # * Else if "typing_extensions" is importable *AND* of a sufficiently
#        #   recent version to define the backported "typing_extensions.Self"
#        #   type hint, fallback to that hint.
#        # * Else, synthesize a placeholder type hint that @beartype internally
#        #   recognizes as semantically equivalent to "typing.Self".
#        Self = _import_typing_attr_or_fallback('Self', object)
#        LiteralString = _import_typing_attr_or_fallback('Self', str)
#        TypeGuard = _import_typing_attr_or_fallback('Self', bool)
#        Annotated = _import_typing_attr_or_fallback('Annotated', bool)
#
#        #FIXME: Repeat the above logic for *ALL* existing "typing" attributes.

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To avoid polluting the public module namespace, external attributes
# *NOT* intended for public importation should be locally imported at module
# scope *ONLY* under alternate private names (e.g., "import re as _re" rather
# than merely "from re").
# WARNING: To preserve PEP 561 compliance with static type checkers (e.g.,
# mypy), external attributes *MUST* be explicitly imported with standard static
# import machinery rather than non-standard dynamic import shenanigans (e.g.,
# "from typing import Annotated" rather than
# "import_typing_attr_or_none('Annotated')").
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# Effectively alias this third-party "beartype.typing" submodule to the standard
# "typing" module by unconditionally importing all explicitly exported public
# attributes from the standard "typing" module *BEFORE* conditionally overriding
# a proper subset of these attributes with non-standard alternatives below.
from typing import *  # pyright: ignore

# ....................{ ALIAS                              }....................
# If the active Python interpreter is *NOT* performing static type-checking
# (e.g., mypy, pyright), override the default implementations of a proper subset
# of public attributes explicitly exported by the standard "typing" module with
# semantically equivalent runtime-friendly alternatives. Specifically...
if not TYPE_CHECKING:
    # ....................{ IMPORTS                        }....................
    # Defer runtime-specific imports.
    from beartype._util.py.utilpyversion import (
        IS_PYTHON_AT_MOST_3_14 as _IS_PYTHON_AT_MOST_3_14,
    )

    # ....................{ PEP ~ 544                      }....................
    # Alias both the PEP 544-compliant "Protocol" superclass and all related
    # "Supports*" protocols to beartype-specific alternatives, which exhibit
    # optimized runtime performed over their default implementations by the
    # standard "typing" module.
    from beartype.typing._typingpep544 import (
        Protocol as Protocol,
        SupportsAbs as SupportsAbs,
        SupportsBytes as SupportsBytes,
        SupportsComplex as SupportsComplex,
        SupportsFloat as SupportsFloat,
        SupportsIndex as SupportsIndex,
        SupportsInt as SupportsInt,
        SupportsRound as SupportsRound,
        runtime_checkable as runtime_checkable,
    )

    # ....................{ PEP ~ 585                      }....................
    # Alias *ALL* PEP 484-compliant public attributes defined by the standard
    # "typing" module that have since been officially deprecated by PEP 585
    # (e.g., "typing.ChainMap") to their semantically equivalent non-deprecated
    # alternatives defined elsewhere in the standard library (e.g.,
    # "collections.ChainMap").
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
        Callable as Callable,
        Collection as Collection,
        Container as Container,
        Coroutine as Coroutine,
        Generator as Generator,
        Hashable as Hashable,
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
        Sized as Sized,
        ValuesView as ValuesView,
        Set as AbstractSet,
    )
    from contextlib import (
        AbstractContextManager as ContextManager,
        AbstractAsyncContextManager as AsyncContextManager,
    )
    from re import (
        Match as Match,
        Pattern as Pattern,
    )

    # Trivially alias all remaining deprecated PEP 484-compliant type hint
    # factories to their equivalent builtins.
    Dict = dict
    FrozenSet = frozenset
    List = list
    Set = set
    Tuple = tuple
    Type = type

    # ....................{ PEP ~ 585 : removed            }....................
    # If the active Python interpreter targets Python <= 3.14 and thus still
    # defines the deprecated "typing.ByteString" type *WITHOUT* yet emitting a
    # "DeprecationWarning" warning, delete that type implicitly imported above
    # in favour of the preferable "collections.abc.ByteString" type.
    #
    # Look. It's complicated. And dumb. Really, really dumb.
    if _IS_PYTHON_AT_MOST_3_14:
        from collections.abc import ByteString
    # Else, the active Python interpreter targets Python >= 3.15 and thus either
    # no longer defines the deprecated "typing.ByteString" type at all *OR* does
    # but only in a manner emitting *WITHOUT* yet emitting a
    # "DeprecationWarning" warning. In either case, permit the __getattr__()
    # dunder function defined below to handle this edge case more cleverly.
# Else, the active Python interpreter is performing static type-checking. In
# this case, force the unclean static type-checker to pretend that this
# "beartype.typing" submodule is a trivial alias of the "typing" module by...
# *DOING ABSOLUTELY NOTHING WHATSOEVER*. Beartype: "You win by doing nothing."

# ....................{ DUNDERS                            }....................
def __getattr__(attr_name: str) -> object:
    '''
    Dynamically retrieve a deprecated attribute with the passed unqualified name
    from this submodule and emit a non-fatal deprecation warning on each such
    retrieval if this submodule defines this attribute *or* raise an exception
    otherwise.

    The Python interpreter implicitly calls this :pep:`562`-compliant module
    dunder function under Python >= 3.7 *after* failing to directly retrieve an
    explicit attribute with this name from this submodule. Since this dunder
    function is only called in the event of an error, neither space nor time
    efficiency are a concern here.

    Parameters
    ----------
    attr_name : str
        Unqualified name of the deprecated attribute to be retrieved.

    Returns
    -------
    object
        Value of this deprecated attribute.

    Warns
    -----
    DeprecationWarning
        If this attribute is deprecated.

    Raises
    ------
    AttributeError
        If this attribute is unrecognized and thus erroneous.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer dunder-specific imports.
    from beartype._util.py.utilpyversion import (
        IS_PYTHON_AT_MOST_3_16,
        IS_PYTHON_AT_LEAST_3_11,
    )

    # ....................{ PEP ~ 585 : removed            }....................
    # Alias *ALL* PEP 484-compliant public attributes defined by the standard
    # "typing" module that have since been quietly removed from that module
    # sooner than PEP 585 mandates these attributes be removed. Technically,
    # CPython itself is violating PEP 585 here. Pragmatically, nobody cares.

    # Alias the PEP 484-compliant "ByteString" type hint singleton to
    # the PEP 585-compliant "collections.abc.ByteString" abstract base
    # class (ABC). Both "collections.abc.ByteString" *AND*
    # "typing.ByteString" have been scheduled for removal under Python
    # 3.17 by the upstream CPython issue:
    #     https://github.com/python/cpython/issues/91896
    #
    # Note that:
    # * These attributes were originally scheduled for removal under Python
    #   3.14. This removal was since deferred by three minor versions (and thus
    #   three years) to inform downstream third-party packages with proper
    #   "DeprecationWarning" warnings emitted by the "typing" module.
    # * Unconditionally importing the "collections.abc.ByteString" type above
    #   under either Python 3.15 or 3.16 would harmfully emit a
    #   "DeprecationWarning" warning for all beartype users importing from this
    #   "beartype.typing" subpackage even for users *NEVER* explicitly importing
    #   "beartype.typing.ByteString". Clearly, that behaviour is unacceptable.
    #   This submodule this behaves more intelligently under Python 3.15 and
    #   3.16 by dynamically deferring the importation of that type until
    #   explicitly accessed by the caller.

    # If...
    if (
        # The active Python interpreter targets at most Python <= 3.16 *AND*...
        IS_PYTHON_AT_MOST_3_16 and
        # The caller is explicitly importing the deprecated
        # "collections.abc.ByteString" type...
        attr_name == 'ByteString'
    ):
        # Import and return this deprecated type.
        from collections.abc import ByteString
        return ByteString
    # Else, either:
    # * The active Python interpreter targets Python >= 3.17, in which case the
    #   deprecated "collections.abc.ByteString" type no longer exists *OR*...
    # * The caller is *NOT* explicitly importing the deprecated
    #   "collections.abc.ByteString" type, in which case the attribute this
    #   caller is explicitly importing is unrecognized.

    # If the active Python interpreter targets Python >= 3.11, the "typing"
    # module defines the __getattr__() dunder method. In this case...
    if IS_PYTHON_AT_LEAST_3_11:
        # Attempt to...
        try:
            # Import the typing.__getattr__() dunder method.
            from typing import __getattr__ as typing_getattr  # type: ignore[attr-defined]

            # Dynamically defer to this method, thus masequerading the
            # "beartype.typing" subpackage as the "typing" module even for the
            # proper subset of attributes only dynamically exposed by that module.
            return typing_getattr(attr_name)
        # If even the above call to the typing.__getattr__() dunder method raised
        # the standard "AttributeError" exception, the caller requested an invalid
        # attribute that genuinely does *NOT* exist. In this case, raise a similar
        # "AttributeError" exception below specific to "beartype.typing".
        except AttributeError:
            pass
    # Else, the active Python interpreter targets Python <= 3.10. In this case,
    # the "typing" module fails to define the __getattr__() dunder method.

    # Raise the same exception raised by Python on accessing a non-existent
    # attribute of a module *NOT* defining this dunder function.
    #
    # Note that Python's non-trivial import machinery silently coerces this
    # "AttributeError" exception into an "ImportError" exception. Just do it!
    raise AttributeError(
        f"module 'beartype.typing' has no attribute '{attr_name}'")
