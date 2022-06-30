#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2022 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`484`- and :pep:`585`-compliant **decorated callable type
hint utilities** (i.e., callables generically applicable to both :pep:`484`-
and :pep:`585`-compliant type hints directly annotating the user-defined
callable currently being decorated by :func:`beartype.beartype`).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.roar import BeartypeDecorHintPep484585Exception
from beartype._data.hint.pep.sign.datapepsigns import HintSignCoroutine
from beartype._data.hint.pep.sign.datapepsignset import (
    HINT_SIGNS_RETURN_GENERATOR_ASYNC,
    HINT_SIGNS_RETURN_GENERATOR_SYNC,
)
from beartype._util.func.utilfunctest import (
    is_func_async_coroutine,
    is_func_async_generator,
    is_func_sync_generator,
)
from beartype._util.hint.pep.proposal.pep484585.utilpep484585arg import (
    get_hint_pep484585_args_3)
from beartype._util.hint.pep.utilpepget import get_hint_pep_sign_or_none
from beartype._util.text.utiltextlabel import (
    prefix_callable_decorated_return)
from beartype._data.datatyping import TypeException
from collections.abc import Callable

# ....................{ REDUCERS ~ return                  }....................
def reduce_hint_pep484585_func_return(
    func: Callable, exception_prefix: str) -> object:
    '''
    Reduce the possibly PEP-noncompliant type hint annotating the return of the
    passed callable if any to a simpler form to generate optimally efficient
    type-checking by the :func:`beartype.beartype` decorator.

    Parameters
    ----------
    func : Callable
        Currently decorated callable to be inspected.
    exception_prefix : str
        Human-readable label prefixing the representation of this object in the
        exception message.

    Returns
    ----------
    object
        Single argument subscripting this hint.

    Raises
    ----------
    BeartypeDecorHintPep484585Exception
        If this callable is either:

        * A synchronous generator *not* annotated by a type hint identified by
          a sign in the :data:`HINT_SIGNS_RETURN_GENERATOR_SYNC` set.
        * An asynchronous generator *not* annotated by a type hint identified
          by a sign in the :data:`HINT_SIGNS_RETURN_GENERATOR_ASYNC` set.
    '''

    # Type hint annotating this callable's return, which the caller has already
    # explicitly guaranteed to exist.
    hint = func.__annotations__['return']

    # Sign uniquely identifying this hint if any *OR* "None" otherwise (e.g.,
    # if this hint is an isinstanceable class).
    hint_sign = get_hint_pep_sign_or_none(hint)

    # If the decorated callable is a coroutine...
    if is_func_async_coroutine(func):
        # If this hint is "Coroutine[...]"...
        if hint_sign is HintSignCoroutine:
            # 3-tuple of all child type hints subscripting this hint if
            # subscripted by three such hints *OR* raise an exception.
            hint_args = get_hint_pep484585_args_3(
                hint=hint, exception_prefix=exception_prefix)

            # Reduce this hint to the last child type hint subscripting this
            # hint, whose value is the return type hint for this coroutine.
            #
            # All other child type hints are currently ignorable, as the *ONLY*
            # means of validating objects sent to and yielded from a coroutine
            # is to wrap that coroutine with a @beartype-specific wrapper
            # object, which we are currently unwilling to do. Why? Because
            # safety and efficiency. Coroutines receiving and yielding multiple
            # objects are effectively iterators; type-checking all iterator
            # values is an O(n) rather than O(1) operation, violating the core
            # @beartype guarantee.
            #
            # Likewise, the parent "Coroutine" type is *ALWAYS* ignorable.
            # Since Python itself implicitly guarantees *ALL* coroutines to
            # return coroutine objects, validating that constraint is silly.
            hint = hint_args[-1]
        # Else, this hint is *NOT* "Coroutine[...]". In this case, silently
        # accept this hint as if this hint had instead been expanded to the
        # semantically equivalent PEP 484- or 585-compliant coroutine hint
        # "Coroutine[None, None, {hint}]".
    # Else, the decorated callable is *NOT* a coroutine.
    #
    # If the decorated callable is an asynchronous generator...
    elif is_func_async_generator(func):
        #FIXME: Unit test this up, please!
        # If this hint is semantically invalid as the return annotation of this
        # callable, raise an exception.
        if hint_sign not in HINT_SIGNS_RETURN_GENERATOR_ASYNC:
            _die_of_hint_return_invalid(
                func=func,
                exception_suffix=(
                    ' (i.e., expected either '
                    'collections.abc.AsyncGenerator[YieldType, SendType], '
                    'collections.abc.AsyncIterable[YieldType], '
                    'collections.abc.AsyncIterator[YieldType], '
                    'typing.AsyncGenerator[YieldType, SendType], '
                    'typing.AsyncIterable[YieldType], or '
                    'typing.AsyncIterator[YieldType] '
                    'type hint).'
                ),
            )
        # Else, this hint is valid as the return annotation of this callable.
    # Else, the decorated callable is *NOT* an asynchronous generator.
    #
    # If the decorated callable is a synchronous generator...
    elif is_func_sync_generator(func):
        #FIXME: Unit test this up, please!
        # If this hint is semantically invalid as the return annotation of this
        # callable, raise an exception.
        if hint_sign not in HINT_SIGNS_RETURN_GENERATOR_SYNC:
            _die_of_hint_return_invalid(
                func=func,
                exception_suffix=(
                    ' (i.e., expected either '
                    'collections.abc.Generator[YieldType, SendType, ReturnType], '
                    'collections.abc.Iterable[YieldType], '
                    'collections.abc.Iterator[YieldType], '
                    'typing.Generator[YieldType, SendType, ReturnType], '
                    'typing.Iterable[YieldType], or '
                    'typing.Iterator[YieldType] '
                    'type hint).'
                ),
            )
        # Else, this hint is valid as the return annotation of this callable.
    # Else, the decorated callable is none of the kinds detected above.

    # Return this possibly reduced hint.
    return hint

# ....................{ PRIVATE ~ validators               }....................
def _die_of_hint_return_invalid(
    # Mandatory parameters.
    func: Callable,
    exception_suffix: str,

    # Optional parameters.
    exception_cls: TypeException = BeartypeDecorHintPep484585Exception,
) -> str:
    '''
    Raise an exception of the passed type with a message suffixed by the passed
    substring explaining why the possibly PEP-noncompliant type hint annotating
    the return of the passed decorated callable is contextually invalid.

    Parameters
    ----------
    func : Callable
        Decorated callable whose return is annotated by an invalid type hint.
    exception_cls : TypeException
        Type of exception to be raised. Defaults to
        :exc:`BeartypeDecorHintPep484585Exception`.
    exception_suffix : str
        Substring suffixing the exception message to be raised.

    Raises
    ----------
    :exc:`exception_cls`
        Exception explaining the invalidity of this return type hint.
    '''
    assert callable(func), f'{repr(func)} not callable.'
    assert isinstance(exception_cls, type), f'{repr(exception_cls)} not class.'
    assert isinstance(exception_suffix, str), (
        f'{repr(exception_suffix)} not string.')

    # Type hint annotating this callable's return, which the caller has already
    # explicitly guaranteed to exist.
    hint = func.__annotations__['return']

    # Raise an exception of this type with a message suffixed by this suffix.
    raise exception_cls(
        f'{prefix_callable_decorated_return(func)}type hint '
        f'{repr(hint)} contextually invalid{exception_suffix}.'
    )
