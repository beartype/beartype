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
    NewType,
    NoReturn,
    Optional,
    Pattern,
    Reversible,
    Sequence,
    Set,
    Tuple,
    Type,
    TypeVar,
    Union,
    ValuesView,
)

# See the "beartype.__init__" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ BASES                             }....................
# Conditionally add the "typing.ForwardRef" superclass depending on the
# current Python version, as this superclass was thankfully publicized
# under Python >= 3.7 after its initial privatization under Python <= 3.6.
HINT_PEP484_BASE_FORWARDREF = (
    typing.ForwardRef if IS_PYTHON_AT_LEAST_3_7 else typing._ForwardRef)
'''
**Forward reference sign** (i.e., arbitrary objects uniquely identifying a
`PEP 484`_-compliant type hint unifying one or more subscripted type hint
arguments into a disjunctive set union of these arguments).

.. _PEP 484:
    https://www.python.org/dev/peps/pep-0484
'''

# ....................{ SIGNS ~ sets                      }....................
HINT_PEP484_SIGNS_UNION = frozenset((
    typing.Optional,
    typing.Union,
))
'''
Frozen set of all **union signs** (i.e., arbitrary objects uniquely identifying
`PEP 484`_-compliant type hints unifying one or more subscripted type hint
arguments into a disjunctive set union of these arguments).

If the active Python interpreter targets:

* At least Python 3.9.0, the :attr:`typing.Optional` and
  :attr:`typing.Union` attributes are distinct.
* Less than Python 3.9.0, the :attr:`typing.Optional` attribute reduces to the
  :attr:`typing.Union` attribute, in which case this set is technically
  semantically redundant. Since tests of both object identity and set
  membership are ``O(1)``, this set incurs no significant performance penalty
  versus direct usage of the :attr:`typing.Union` attribute and is thus
  unconditionally used as is irrespective of Python version.

.. _PEP 484:
    https://www.python.org/dev/peps/pep-0484
'''

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

    # ..................{ SETS ~ bases                      }..................
    data_module.HINT_PEP_BASES_FORWARDREF.update((
        # PEP 484-compliant forward reference superclass.
        HINT_PEP484_BASE_FORWARDREF,
    ))

    # ..................{ SETS ~ signs : type               }..................
    data_module.HINT_PEP_SIGNS_TYPE_ORIGIN.update((
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
    ))

    # If the active Python interpreter targets at least various Python
    # versions, add PEP 484-specific signs introduced in those versions.
    if IS_PYTHON_AT_LEAST_3_7:
        data_module.HINT_PEP_SIGNS_TYPE_ORIGIN.update((
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
        ))

        if IS_PYTHON_AT_LEAST_3_8:
            data_module.HINT_PEP_SIGNS_TYPE_ORIGIN.update((
                typing.SupportsIndex,
            ))

    # ..................{ SETS ~ signs : ignorable          }..................
    data_module.HINT_PEP_SIGNS_IGNORABLE.update((
        # The "Any" singleton is semantically synonymous with the ignorable
        # PEP-noncompliant "beartype.cave.AnyType" and hence "object" types.
        Any,

        # The "Generic" superclass imposes no constraints and is thus also
        # semantically synonymous with the ignorable PEP-noncompliant
        # "beartype.cave.AnyType" and hence "object" types. Since PEP
        # 484 stipulates that *ANY* unsubscripted subscriptable PEP-compliant
        # singleton including "typing.Generic" semantically expands to that
        # singelton subscripted by an implicit "Any" argument, "Generic"
        # semantically expands to the implicit "Generic[Any]" singleton.
        Generic,

        # The unsubscripted "Optional" singleton semantically expands to the
        # implicit "Optional[Any]" singleton by the same argument. Since PEP
        # 484 also stipulates that all "Optional[t]" singletons semantically
        # expand to "Union[t, type(None)]" singletons for arbitrary arguments
        # "t", "Optional[Any]" semantically expands to merely "Union[Any,
        # type(None)]". Since all unions subscripted by "Any" semantically
        # reduce to merely "Any", the "Optional" singleton also reduces to
        # merely "Any".
        #
        # This intentionally excludes "Optional[type(None)]", which the
        # "typing" module physically reduces to merely "type(None)". *shrug*
        Optional,

        # The "TypeVar" superclass imposes no constraints, much like the
        # "Generic" superclass.
        TypeVar,

        # The unsubscripted "Union" singleton semantically expands to the
        # implicit "Union[Any]" singleton by the same argument. Since PEP 484
        # stipulates that a union of one type semantically reduces to only that
        # type, "Union[Any]" semantically reduces to merely "Any". Despite
        # their semantic equivalency, however, these objects remain
        # syntactically distinct with respect to object identification: e.g.,
        #     >>> Union is not Union[Any]
        #     True
        #     >>> Union is not Any
        #     True
        #
        # This intentionally excludes:
        #
        # * The "Union[Any]" and "Union[object]" singletons, since the "typing"
        #   module physically reduces:
        #   * "Union[Any]" to merely "Any" (i.e., "Union[Any] is Any"), which
        #     this frozen set already contains.
        #   * "Union[object]" to merely "object" (i.e., "Union[object] is
        #     object"), which this frozen set also already contains.
        # * "Union" singleton subscripted by one or more ignorable type hints
        #   contained in this set (e.g., "Union[Any, bool, str]"). Since there
        #   exist a countably infinite number of these subscriptions, these
        #   subscriptions *CANNOT* be explicitly listed in this set. Instead,
        #   these subscriptions are dynamically detected by the high-level
        #   beartype._util.hint.pep.utilhinttest.is_hint_ignorable() tester
        #   function and thus referred to as deeply ignorable type hints.
        Union,

        # The "ForwardRef" class as an object arguably does *NOT* constitute a
        # valid PEP-compliant type hint. Nonetheless, simply ignoring this
        # class when used as an annotation is a safe minimal-effort approach.
        HINT_PEP484_BASE_FORWARDREF,
    ))

    # ..................{ SETS ~ signs : supported          }..................
    data_module.HINT_PEP_SIGNS_SUPPORTED_SHALLOW.update((
        Any,
        NewType,
        NoReturn,
        TypeVar,
        HINT_PEP484_BASE_FORWARDREF,
    ))
    data_module.HINT_PEP_SIGNS_SUPPORTED_DEEP.update((
        Generic,
        List,
        MutableSequence,
        Sequence,
        Tuple,

        # Note that "typing.Union" implicitly subsumes "typing.Optional" *ONLY*
        # under Python <= 3.9. The implementations of the "typing" module under
        # those older Python versions transparently reduced "typing.Optional"
        # to "typing.Union" at runtime. Since this reduction is no longer the
        # case, both *MUST* now be explicitly listed here.
        Union,
        Optional,
    ))

    # ..................{ SETS ~ signs : subtypes           }..................
    data_module.HINT_PEP_SIGNS_SEQUENCE_STANDARD.update((
        typing.List,
        typing.MutableSequence,
        typing.Sequence,
    ))
