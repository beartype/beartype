#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`484`- and :pep:`585`-compliant **decorated callable type
hint reducers** (i.e., low-level callables converting higher-level :pep:`484`-
and :pep:`585`-compliant type hints directly annotating the user-defined
callable currently being decorated by :func:`beartype.beartype` to lower-level
type hints more readily consumable by :mod:`beartype`).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.roar import BeartypeDecorHintPep484585Exception
from beartype._cave._cavemap import NoneTypeOr
from beartype._check.cls.call.calldataabc import BeartypeCallDataABC
from beartype._check.cls.hint.hintsane import (
    HINT_SANE_IGNORABLE,
    HintSane,
)
from beartype._data.func.datafuncarg import ARG_NAME_RETURN
from beartype._data.hint.sign.datahintsigncls import HintSign
from beartype._data.kind.datakindiota import SENTINEL
from beartype._data.typing.datatyping import (
    HintSignOrNoneOrSentinel,
    TypeException,
)
from beartype._data.typing.datatypingport import (
    DictStrToHint,
    Hint,
)
from beartype._data.hint.sign.datahintsignset import (
    HINT_SIGNS_RETURN_GENERATOR_ASYNC,
    HINT_SIGNS_RETURN_GENERATOR_SYNC,
)
from beartype._util.cls.utilclstest import is_type_subclass
from beartype._util.func.utilfunctest import (
    is_func_coro,
    is_func_generator,
    is_func_generator_async,
    is_func_generator_sync,
)
from beartype._util.hint.pep.proposal.pep484585.pep484585args import (
    get_hint_pep484585_args)
from beartype._util.hint.pep.proposal.pep749.pep649749annotate import (
    get_hintable_pep649749_annotations)
from beartype._util.hint.pep.utilpepsign import get_hint_pep_sign_or_none
from beartype._util.text.utiltextprefix import prefix_callable_return
from collections.abc import (
    AsyncGenerator,
    Callable,
    Generator,
)
from typing import Optional

# ....................{ REDUCERS                           }....................
#FIXME: *INSUFFICIENT*. Additionally:
#* Define a new reduce_hint_pep484585_awaitable_return() reducer as well. Any
#  arbitrary "Coroutine[A, B, R]" type hint is a subtype of "Awaitable[R]".
#  Ergo, "Awaitable[R]" is *ALSO* valid as the return hint annotating a
#  coroutine factory callable. However, *ONLY* "Coroutine[A, B, R]" and
#  "Awaitable[R]" are valid as that return hint. Which leads us to...
def reduce_hint_pep484585_coroutine_return(
    call_curr: BeartypeCallDataABC,
    hint: Hint,
    pith_name: Optional[str],
    exception_prefix: str,
    **kwargs
) -> Hint:
    '''
    Reduce the :pep:`484`- or :pep:`585`-compliant coroutine type hint
    annotating the return of the passed callable if that callable is a
    **coroutine factory** (i.e., function whose signature was prefixed by the
    ``async`` keyword *and* whose body contains no ``yield`` statements) *and*
    this hint annotates the return of that coroutine from this uncheckable
    coroutine hint to the checkable return child hint directly subscripting this
    uncheckable coroutine hint (e.g., from ``Coroutine[None, None, str]`` to
    merely :class:`str`).

    This reducer intentionally ignores:

    * The parent ``Coroutine`` type hint factory of this coroutine hint. Since
      Python itself implicitly guarantees *all* coroutine factories to create
      and return coroutine objects, validating that constraint would only
      needlessly consume excess space and time without type-checking anything.
    * All other child type hints directly subscripting this coroutine hint, as
      the *only* means of validating objects sent to and yielded from a
      coroutine would be to wrap the passed coroutine with a
      :func:`beartype`-specific wrapper object, which we are currently unwilling
      to do. Why? Because safety and efficiency. Coroutines receiving and
      yielding multiple objects are effectively iterators; type-checking all
      iterator values is an :math:`O(n)` rather than :math:`O(1)` operation,
      violating the core :mod:`beartype` guarantee. Moreover, explicit is better
      than the implicit. The caller did *not* request that we type-check
      arbitrary coroutines *not* explicitly decorated by the
      :func:`beartype.beartype` decorator. Ergo, we don't.

    Parameters
    ----------
    call_curr : BeartypeCallDataABC
        **Beartype call metadata** (i.e., dataclass aggregating *all* common
        metadata encapsulating the user-defined callable, type, or statement
        currently being type-checked by the end user).
    hint : Hint
        Coroutine type hint to be reduced.
    pith_name : Optional[str]
        Either:

        * If this hint annotates a parameter of some callable, the name of that
          parameter.
        * If this hint annotates the return of some callable, ``"return"``.
        * Else, :data:`None`.
    exception_prefix : str
        Human-readable substring prefixing raised exception messages.

    All remaining keyword-only parameters are silently ignored.

    Returns
    -------
    Hint
        Either:

        * If the passed callable is a coroutine *and* the passed hint annotates
          the return of that coroutine, the return child hint subscripting this
          hint.
        * Else, this hint as is.
    '''
    # print(f'Reducing {hint} annotating {call_curr.decoratee}...')

    # Avoid circular import dependencies.
    from beartype._check.convert._reduce._pep.pep484.redpep484core import (
        reduce_hint_pep484_deprecated)

    # If this hint is a PEP 484-compliant deprecated "typing.Coroutine[...]"
    # hint, emit a non-fatal deprecation warning.
    reduce_hint_pep484_deprecated(hint)

    # If neither...
    if not (
        # This coroutine hint annotates the return of the decorated callable
        # *AND*...
        pith_name == ARG_NAME_RETURN and
        # The decorated callable is a coroutine factory...
        is_func_coro(call_curr.decoratee)
    ):
        # Then either:
        # * This coroutine hint does *NOT* annotate the return of the decorated
        #   callable *OR*...
        # * This coroutine hint annotates the return of the decorated callable
        #   but that callable is *NOT* a coroutine factory.
        #
        # In either case, silently reduce to a noop. Preserve this hint as is!
        return hint
    # Else, this coroutine hint annotates the return of the decorated coroutine
    # factory.

    # 3-tuple of all child hints subscripting this coroutine hint if subscripted
    # by three such hints *OR* raise an exception otherwise (i.e., if this
    # coroutine hint is subscripted by a different number of child hints).
    hints_child: tuple[Hint, Hint, Hint] = get_hint_pep484585_args(  # type: ignore[assignment]
        hint=hint, args_len=3, exception_prefix=exception_prefix)

    # Reduce this coroutine hint to the return child hint subscripting this
    # coroutine hint.
    return hints_child[-1]

# ....................{ CHECKERS                           }....................
# This function is technically a runtime type-checker but explicitly called
# *ONLY* during type hint reduction. For lack of a better home, we thus
# intentionally define this function in this tangentially related submodule.

#FIXME: Actually, this doesn't belong here at all anymore. Shift back to the
#"beartype._util.hint.pep.proposal.pep484585.pep484585func" submodule. Ugh!
#Actually... hmm. Maybe a new private sibling of "convmain", mayhap?
#FIXME: Explicitly call in "redmain", please. *sigh*
#FIXME: Refactor "convmain" to stop doing what it's doing, please. *sigh*
#FIXME: Unit test us up, please. *sigh*
#FIXME: Remove "HintSignAny" from both "HINT_SIGNS_RETURN_GENERATOR_ASYNC" and
#"HINT_SIGNS_RETURN_GENERATOR_SYNC" once this works, please. *sigh*
#FIXME: Revise docstring, please. *sigh*
def die_if_func_return_hint_invalid(
    call_curr: BeartypeCallDataABC,
    hint_sane: HintSane,
    pith_name: Optional[str],
) -> None:
    '''
    Reduce the possibly PEP-noncompliant type hint annotating the return of the
    passed callable if that callable is a **generator factory** (i.e., function
    containing one or more ``yield`` statements) to a simpler form generating
    optimally efficient type-checking by the :func:`beartype.beartype`
    decorator.

    Parameters
    ----------
    call_curr : BeartypeCallDataABC
        **Beartype call metadata** (i.e., dataclass aggregating *all* common
        metadata encapsulating the user-defined callable, type, or statement
        currently being type-checked by the end user).
    hint_sane : HintSane
        **Sanified type hint metadata** (i.e., :data:`.HintSane` object)
        encapsulating the hint to be validated.
    pith_name : Optional[str]
        Either:

        * If this hint annotates a parameter of some callable, the name of that
          parameter.
        * If this hint annotates the return of some callable, ``"return"``.
        * Else, :data:`None`.

    Returns
    -------
    Hint
        Single argument subscripting this hint.

    Raises
    ------
    BeartypeDecorHintPep484585Exception
        If this callable is either:

        * A synchronous generator *not* annotated by a type hint identified by
          a sign in the :data:`HINT_SIGNS_RETURN_GENERATOR_SYNC` set.
        * An asynchronous generator *not* annotated by a type hint identified
          by a sign in the :data:`HINT_SIGNS_RETURN_GENERATOR_ASYNC` set.
    '''
    assert isinstance(call_curr, BeartypeCallDataABC), (
        f'{repr(call_curr)} not beartype call metadata.')
    assert isinstance(hint_sane, HintSane), (
        f'{repr(hint_sane)} not sanified hint metadata.')

    # ....................{ NOOP                           }....................
    # Currently decorated callable, localized for readability and as a
    # negligible microoptimization. *BARF*
    func = call_curr.decoratee

    # If it is *NOT* the case that...
    if not (
        # This hint is unignorable *AND*...
        hint_sane is not HINT_SANE_IGNORABLE and
        # This hint annotates the return of the decorated callable *AND*...
        pith_name == ARG_NAME_RETURN and
        # The decorated callable is either an asynchronous or synchronous
        # generator factory *AND*...
        #
        # Note that this hint annotating the return of the decorated callable
        # implies the decorated callable to exist. Ergo, we needn't test that.
        is_func_generator(func)
    ):
        # Then either this hint is ignorable, this hint does *NOT* annotate the
        # return of the decorated callable, *OR* the decorated callable is
        # neither an asynchronous nor synchronous generator factory. In any
        # case, this combination of hint and decorated callable is irrelevent
        # with respect to this validator. Ergo, silently reduce to a noop.
        return
    # Else, this unignorable hint annotates the return of the decorated callable
    # *AND* the decorated callable is either an asynchronous or synchronous
    # generator factory. Ergo, this hint is a candidate for being validated as
    # that return. Do so below, yo! \o/

    # ....................{ LOCALS                         }....................
    # Hint encapsulated by this metadata.
    hint = hint_sane.hint

    # Sign uniquely identifying this hint.
    hint_sign = get_hint_pep_sign_or_none(hint)

    # ....................{ VALIDATE                       }....................
    # If the decorated callable is a synchronous generator...
    if is_func_generator_sync(func):
        # If this hint is neither...
        if not (
            # A PEP-compliant type hint acceptable as the return annotation of a
            # synchronous generator *NOR*...
            hint_sign in HINT_SIGNS_RETURN_GENERATOR_SYNC or
            # The "collections.abc.Generator" abstract base class (ABC) or an
            # arbitrary class satisfying that pseudo-protocol...
            is_type_subclass(hint, Generator)
        # Then this hint is semantically invalid as the return annotation of
        # this callable. In this case, raise an exception.
        ):
            _die_hint_return_invalid(
                func=func,
                exception_suffix=(
                    ' (i.e., expected either '
                    'collections.abc.Generator[YieldType, SendType, ReturnType], '
                    'collections.abc.Iterable[YieldType], '
                    'collections.abc.Iterator[YieldType], '
                    'typing.Generator[YieldType, SendType, ReturnType], '
                    'typing.Iterable[YieldType], '
                    'typing.Iterator[YieldType], or '
                    'typing.Any type hint).'
                ),
            )
        # Else, this hint is valid as the return annotation of this callable.
    # Else, the decorated callable is *NOT* a synchronous generator.
    #
    # If the decorated callable is an asynchronous generator...
    elif is_func_generator_async(func):
        # If this hint is neither...
        if not (
            # A PEP-compliant type hint acceptable as the return annotation of
            # an synchronous generator *NOR*...
            hint_sign in HINT_SIGNS_RETURN_GENERATOR_ASYNC or
            # The "collections.abc.AsyncGenerator" abstract base class (ABC) or
            # an arbitrary class satisfying that pseudo-protocol...
            is_type_subclass(hint, AsyncGenerator)
        # Then this hint is semantically invalid as the return annotation of
        # this callable. In this case, raise an exception.
        ):
            _die_hint_return_invalid(
                func=func,
                exception_suffix=(
                    ' (i.e., expected either '
                    'collections.abc.AsyncGenerator[YieldType, SendType], '
                    'collections.abc.AsyncIterable[YieldType], '
                    'collections.abc.AsyncIterator[YieldType], '
                    'typing.AsyncGenerator[YieldType, SendType], '
                    'typing.AsyncIterable[YieldType], '
                    'typing.AsyncIterator[YieldType], or '
                    'typing.Any type hint).'
                ),
            )
        # Else, this hint is valid as the return annotation of this callable.
    # Else, the decorated callable is none of the kinds detected above.

# ....................{ PRIVATE ~ validators               }....................
def _die_hint_return_invalid(
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
        :exc:`.BeartypeDecorHintPep484585Exception`.
    exception_suffix : str
        Substring suffixing the exception message to be raised.

    Raises
    ------
    exception_cls
        Exception explaining the invalidity of this return type hint.
    '''
    assert callable(func), f'{repr(func)} not callable.'
    assert isinstance(exception_cls, type), f'{repr(exception_cls)} not class.'
    assert isinstance(exception_suffix, str), (
        f'{repr(exception_suffix)} not string.')

    # "__annotations__" dunder dictionary providing this callable's type hints.
    func_annotations = get_hintable_pep649749_annotations(func)

    # Type hint annotating this callable's return, which the caller has already
    # explicitly guaranteed to exist.
    hint_return = func_annotations[ARG_NAME_RETURN]

    # Raise an exception of this type with a message suffixed by this suffix.
    raise exception_cls(
        f'{prefix_callable_return(func)}type hint {repr(hint_return)} '
        f'contextually invalid{exception_suffix}'
    )
