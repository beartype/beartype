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
from beartype._check.cls.call.calldataabc import BeartypeCallDataABC
from beartype._data.func.datafuncarg import ARG_NAME_RETURN
from beartype._data.typing.datatypingport import Hint
from beartype._util.func.utilfunctest import is_func_coro
from beartype._util.hint.pep.proposal.pep484585.pep484585args import (
    get_hint_pep484585_args)
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
