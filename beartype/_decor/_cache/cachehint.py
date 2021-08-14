#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2021 Beartype authors.
# See "LICENSE" for further details.

'''
**Type hint cache** (i.e., singleton dictionary mapping from the
machine-readable representations of all non-self-cached type hints to those
hints).**

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ TODO                              }....................
#FIXME: The coercion function(s) defined below should also rewrite unhashable
#hints to be hashable *IF FEASIBLE.* This isn't always feasible, of course
#(e.g., "Annotated[[]]", "Literal[[]]"). The one notable place where this is
#feasible is with PEP 585-compliant type hints subscripted by unhashable rather
#than hashable iterables, which can *ALWAYS* be safely rewritten to be hashable
#(e.g., coercing "callable[[], None]" to "callable[(), None]").

#FIXME: The coercion function(s) defined below should also coerce PEP
#544-compatible protocols *NOT* decorated by @typing.runtime_checkable to be
#decorated by that decorator, as such protocols are unusable at runtime. Yes,
#we should always try something *REALLY* sneaky and clever.
#
#Specifically, rather than accept "typing" nonsense verbatim, we could instead:
#* Detect PEP 544-compatible protocol type hints *NOT* decorated by
#  @typing.runtime_checkable. The existing is_type_isinstanceable() tester now
#  detects whether arbitrary classes are isinstanceable, so just call that.
#* Emit a non-fatal warning advising the end user to resolve this on their end.
#* Meanwhile, beartype can simply:
#  * Dynamically fabricate a new PEP 544-compatible protocol decorated by
#    @typing.runtime_checkable using the body of the undecorated user-defined
#    protocol as its base. Indeed, simply subclassing a new subclass decorated
#    by @typing.runtime_checkable from the undecorated user-defined protocol as
#    its base with a noop body of "pass" should suffice.
#  * Replacing all instances of the undecorated user-defined protocol with that
#    decorated beartype-defined protocol in annotations. Note this would
#    strongly benefit from some form of memoization or caching. Since this edge
#    case should be fairly rare, even a dictionary would probably be overkill.
#    Just implementing something resembling the following memoized getter
#    in the "utilpep544" submodule would probably suffice:
#        @callable_cached
#        def get_pep544_protocol_checkable_from_protocol_uncheckable(
#            protocol_uncheckable: object) -> Protocol:
#            ...
#
#Checkmate, "typing". Checkmate.

# ....................{ IMPORTS                           }....................
from beartype._cave._cavefast import NotImplementedType, NoneType
from beartype._util.hint.utilhinttest import die_unless_hint
from beartype._data.func.datafunc import METHOD_NAMES_BINARY_DUNDER
from collections.abc import Callable
from typing import Any, Dict, Union

# See the "beartype.cave" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ GLOBALS                           }....................
_HINT_REPR_TO_HINT: Dict[str, Any] = {}
'''
**Type hint cache** (i.e., singleton dictionary mapping from the
machine-readable representations of all non-self-cached type hints to those
hints).**

This dictionary caches:

* :pep:`585`-compliant type hints, which do *not* cache themselves.
* :pep:`563`-compliant **deferred type hints** (i.e., type hints persisted as
  evaluatable strings rather than actual type hints), enabled if the active
  Python interpreter targets either:

  * Python 3.7.0 *and* the module declaring this callable explicitly enables
    :pep:`563` support with a leading dunder importation of the form ``from
    __future__ import annotations``.
  * Python 4.0.0, where `PEP 563`_ is expected to be mandatory.

This dictionary does *not* cache:

* Type hints declared by the :mod:`typing` module, which implicitly cache
  themselves on subscription thanks to inscrutable metaclass magic.

Implementation
--------------
This dictionary is intentionally designed as a naive dictionary rather than
robust LRU cache, for the same reasons that callables accepting hints are
memoized by the :func:`beartype._util.cache.utilcachecall.callable_cached`
rather than the :func:`functools.lru_cache` decorator. Why? Because:

* The number of different type hints instantiated across even worst-case
  codebases is negligible in comparison to the space consumed by those hints.
* The :attr:`sys.modules` dictionary persists strong references to all
  callables declared by previously imported modules. In turn, the
  ``func.__annotations__`` dunder dictionary of each such callable persists
  strong references to all type hints annotating that callable. In turn, these
  two statements imply that type hints are *never* garbage collected but
  instead persisted for the lifetime of the active Python process. Ergo,
  temporarily caching hints in an LRU cache is pointless, as there are *no*
  space savings in dropping stale references to unused hints.
'''

# ....................{ CACHERS                           }....................
#FIXME: Refactor as follows:
#* Finish implementing cache_hint_nonpep563() below.
#* Replace all calls to coerce_hint_pep() with calls to cache_hint_nonpep563().
#* Remove coerce_hint_pep() entirely.
def coerce_hint_pep(
    func: Callable,
    pith_name: str,
    hint: object,
    hint_label: str,
) -> object:
    '''
    Coerce the passed type hint annotating the parameter or return with the
    passed name of the passed callable into the corresponding PEP-compliant
    type hint if needed.

    Specifically, this function:

    * If this hint is a **PEP-noncompliant tuple union** (i.e., tuple of one or
      more standard classes and forward references to standard classes):

      * Coerces this tuple union into the equivalent :pep:`484`-compliant
        union.
      * Replaces this tuple union in the ``__annotations__`` dunder tuple of
        this callable with this :pep:`484`-compliant union.
      * Returns this :pep:`484`-compliant union.

    * Else if this hint is already PEP-compliant, preserves and returns this
      hint unmodified as is.
    * Else (i.e., if this hint is neither PEP-compliant nor -noncompliant and
      thus invalid as a type hint), raise an exception.

    This getter is *not* memoized, due to being only called once per decorated
    callable parameter or return value and being efficient in any case.

    Parameters
    ----------
    func : Callable
        Callable
    pith_name : str
        Either:

        * If this hint annotates a parameter, the name of that parameter.
        * If this hint annotates the return, ``"return"``.
    hint : object
        Type hint to be rendered PEP-compliant.
    hint_label : str
        Human-readable label describing this hint.

    Returns
    ----------
    object
        Either:

        * If this hint is PEP-noncompliant, PEP-compliant type hint converted
          from this hint.
        * If this hint is PEP-compliant, hint unmodified as is.

    Raises
    ----------
    BeartypeDecorHintNonPepException
        If this object is neither:

        * A PEP-noncompliant type hint.
        * A supported PEP-compliant type hint.
    '''
    assert callable(func), f'{repr(func)} not callable.'
    assert isinstance(pith_name, str), f'{pith_name} not string.'

    # Original instance of this hint *PRIOR* to being subsequently coerced.
    hint_old = hint

    # ..................{ MYPY                              }..................
    # If...
    if (
        # This hint annotates the return for the decorated callable *AND*...
        pith_name == 'return' and
        # The decorated callable is a binary dunder method (e.g., __eq__())...
        func.__name__ in METHOD_NAMES_BINARY_DUNDER
    ):
        # Expand this hint to accept both this hint *AND* the "NotImplemented"
        # singleton as valid returns from this method. Why? Because this
        # expansion has been codified by mypy and is thus a de-facto typing
        # standard, albeit one currently lacking formal PEP standardization.
        #
        # Consider this representative binary dunder method:
        #     class MuhClass:
        #         @beartype
        #         def __eq__(self, other: object) -> bool:
        #             if isinstance(other, TheCloud):
        #                 return self is other
        #             return NotImplemented
        #
        # Technically, that method *COULD* be retyped to return:
        #         def __eq__(self, other: object) -> Union[
        #             bool, type(NotImplemented)]:
        #
        # Pragmatically, mypy and other static type checkers do *NOT* currently
        # support the type() builtin in a sane manner and thus raise errors
        # given the otherwise valid logic above. This means that the following
        # equivalent approach also yields the same errors:
        #     NotImplementedType = type(NotImplemented)
        #     class MuhClass:
        #         @beartype
        #         def __eq__(self, other: object) -> Union[
        #             bool, NotImplementedType]:
        #             if isinstance(other, TheCloud):
        #                 return self is other
        #             return NotImplemented
        #
        # Of course, the latter approach can be manually rectified by
        # explicitly typing that type as "Any": e.g.,
        #     NotImplementedType: Any = type(NotImplemented)
        #
        # Of course, expecting users to be aware of these ludicrous sorts of
        # mypy idiosyncrasies merely to annotate an otherwise normal binary
        # dunder method is one expectation too far.
        #
        # Ideally, official CPython developers would resolve this by declaring
        # a new "types.NotImplementedType" type global resembling the existing
        # "types.NoneType" type global. As that has yet to happen, mypy has
        # instead taken the surprisingly sensible course of silently ignoring
        # this edge case by effectively performing the same type expansion as
        # performed here. *applause*
        hint = Union[hint, NotImplementedType]
    # Else, this hint is *NOT* the mypy-compliant "NotImplemented" singleton.
    #
    # ..................{ NON-PEP                           }..................
    # If this hint is a PEP-noncompliant tuple union, coerce this union into
    # the equivalent PEP-compliant union subscripted by the same child hints.
    # By definition, PEP-compliant unions are a superset of PEP-noncompliant
    # tuple unions and thus accept all child hints accepted by the latter.
    elif isinstance(hint, tuple):
        hint = Union.__getitem__(hint)
    # Else, this hint is *NOT* a PEP-noncompliant tuple union.

    # ..................{ COERCION                          }..................
    # If this hint was coerced above into a different instance, replace the
    # original instance of this hint in the annotations dunder dictionary
    # attached to the decorated callable with the new instance of this hint.
    if hint_old is not hint:
        func.__annotations__[pith_name] = hint

    # If this object is neither a PEP-noncompliant type hint *NOR* supported
    # PEP-compliant type hint, raise an exception.
    die_unless_hint(hint=hint, hint_label=hint_label)
    # Else, this object is either a PEP-noncompliant type hint *OR* supported
    # PEP-compliant type hint.

    # Return this hint.
    return hint


def cache_hint_nonpep563(
    func: Callable,
    pith_name: str,
    hint: Any,
    hint_label: str,
) -> Any:
    '''
    Coerce and cache the passed (possibly non-self-cached and/or
    PEP-noncompliant) type hint annotating the parameter or return value with
    the passed name of the passed callable into the equivalent
    :mod:`beartype`-cached PEP-compliant type hint if needed *or* silently
    reduce to a noop otherwise (i.e., if this hint is already both self-cached
    and PEP-compliant).

    Specifically, this function (in order):

    #. If the passed type hint is already self-cached, this hint is already
       PEP-compliant by definition. In this case, this function preserves and
       returns this hint as is.
    #. Else if a semantically equivalent type hint (i.e., having the same
       machine-readable representation) as this hint was already cached by a
       prior call to this function, the current call to this function:

       * Replaces this hint in the ``__annotations__`` dunder tuple of this
         callable with this previously cached hint, minimizing memory space
         consumption across the lifetime of the active Python process.
       * Returns this previously cached hint.

    #. Else if this hint is a **PEP-noncompliant tuple union** (i.e., tuple of
       one or more standard classes and forward references to standard
       classes), this function:

       * Coerces this tuple union into the equivalent :pep:`484`-compliant
         union.
       * Replaces this tuple union in the ``__annotations__`` dunder tuple of
         this callable with this :pep:`484`-compliant union.

    #. Else (i.e., if this hint is neither PEP-compliant nor -noncompliant and
       thus unsupported by :mod:`beartype`), this function raises an exception.
    #. Internally caches this hint with the :data:`_HINT_REPR_TO_HINT`
       dictionary.
    #. Returns this hint.

    This function *cannot* be meaningfully memoized, since the passed type hint
    is *not* guaranteed to be cached somewhere. Only functions passed cached
    type hints can be meaningfully memoized.

    The ``_nonpep563`` substring suffixing the name of this function implies
    this function is intended to be called *after* all possibly `PEP
    563`_-compliant **deferred type hints** (i.e., type hints persisted as
    evaluatable strings rather than actual type hints) annotating this callable
    if any have been evaluated into actual type hints.

    Design
    ------
    This function does *not* bother caching **self-cached type hints** (i.e.,
    type hints that externally cache themselves), as these hints are already
    cached elsewhere. Self-cached type hints include most :pep:`484`-compliant
    type hints declared by the :mod:`typing` module, which means that
    subscripting type hints declared by the :mod:`typing` module with the same
    child type hints reuses the exact same internally cached objects rather
    than creating new uncached objects: e.g.,

    .. code-block:: python

       >>> import typing
       >>> typing.List[int] is typing.List[int]
       True

    Equivalently, this function *only* caches **non-self-cached type hints**
    (i.e., type hints that do *not* externally cache themselves), as these
    hints are *not* already cached elsewhere. Non-self-cached type hints
    include *all* `PEP 585`_-compliant type hints produced by subscripting
    builtin container types, which means that subscripting builtin container
    types with the same child type hints creates new uncached objects rather
    than reusing the same internally cached objects: e.g.,

    .. code-block:: python

       >>> list[int] is list[int]
       False

    Motivation
    ----------
    This function enables callers to coerce non-self-cached type hints into
    :mod:`beartype`-cached type hints. :mod:`beartype` effectively requires
    *all* type hints to be cached somewhere! :mod:`beartype` does *not* care
    who, what, or how is caching those type hints -- only that they are cached
    before being passed to utility functions in the :mod:`beartype` codebase.
    Why? Because most such utility functions are memoized for efficiency by the
    :func:`beartype._util.cache.utilcachecall.callable_cached` decorator, which
    maps passed parameters (typically including the standard ``hint`` parameter
    accepting a type hint) based on object identity to previously cached return
    values. You see the problem, we trust.

    Non-self-cached type hints that are otherwise semantically equal are
    nonetheless distinct objects and will thus be treated as distinct
    parameters by memoization decorators. If this function did *not* exist,
    non-self-cached type hints could *not* be coerced into
    :mod:`beartype`-cached type hints and thus could *not* be memoized,
    reducing the efficiency of :mod:`beartype` for standard type hints.

    Parameters
    ----------
    func : Callable
        Callable annotated by this hint.
    pith_name : str
        Either:

        * If this hint annotates a parameter, the name of that parameter.
        * If this hint annotates the return, ``"return"``.
    hint : object
        Possibly non-self-cached and/or PEP-noncompliant type hint to be
        coerced and cached into the equivalent :mod:`beartype`-cached
        PEP-compliant type hint.
    hint_label : str
        Human-readable label describing this hint.

    Returns
    ----------
    object
        Either:

        * If this hint is either non-self-cached *or* PEP-noncompliant, the
          equivalent :mod:`beartype`-cached PEP-compliant type hint coerced and
          cached from this hint.
        * If this hint is self-cached *and* PEP-compliant, this hint as is.

    Raises
    ----------
    BeartypeDecorHintNonPepException
        If this object is neither:

        * A PEP-noncompliant type hint.
        * A supported PEP-compliant type hint.

    .. _PEP 563:
        https://www.python.org/dev/peps/pep-0563
    .. _PEP 585:
        https://www.python.org/dev/peps/pep-0585
    '''

    #FIXME: Call the new is_hint_pep_uncached() tester here to decide whether
    #or not to cache this hint.

    # If this hint is a PEP-noncompliant tuple union, coerce this union into
    # the equivalent PEP-compliant union subscripted by the same child hints.
    # By definition, PEP-compliant unions are a strict superset of
    # PEP-noncompliant tuple unions and thus accept all child hints accepted by
    # the latter.
    if isinstance(hint, tuple):
        assert callable(func), f'{repr(func)} not callable.'
        assert isinstance(pith_name, str), f'{pith_name} not string.'
        hint = func.__annotations__[pith_name] = Union.__getitem__(hint)
    # Else, this hint is *NOT* a PEP-noncompliant tuple union.

    # If this object is neither a PEP-noncompliant type hint *NOR* supported
    # PEP-compliant type hint, raise an exception.
    die_unless_hint(hint=hint, hint_label=hint_label)
    # Else, this object is either a PEP-noncompliant type hint *OR* supported
    # PEP-compliant type hint.

    # Return this hint.
    return hint
