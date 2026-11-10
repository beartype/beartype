#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype inline initializer** (i.e., low-level fail-safe binding no-op
type-checkers to the placeholders of callables instrumented by the
:mod:`beartype.claw` abstract syntax tree (AST) transformer).

Overview
--------
The :class:`beartype.claw._ast._kind.clawastinline.BeartypeNodeTransformerInlineMixin`
instruments a typed callable by injecting two kinds of calls into its body:

* A call at the head of the body, whose callee is the placeholder string
  :data:`.BEARTYPE_INLINE_ARGS_PLACEHOLDER`, type-checking all parameters.
* A call wrapping each returned value, whose callee is the placeholder string
  :data:`.BEARTYPE_INLINE_RETURN_PLACEHOLDER`, type-checking that value.

Both placeholders compile to ``LOAD_CONST`` of a *string*. Calling a string
raises :exc:`TypeError`. The :func:`.beartype_inline_init` decorator is applied
innermost to every instrumented callable and thus binds both placeholders to
harmless no-ops the moment the ``def`` statement executes, regardless of what
any other decorator subsequently does (or fails to do). The
:func:`beartype._decor._nontype._inline.inlinemain.beartype_func_inline` function
later replaces these no-ops by real type-checkers.

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype._data.claw.dataclawmagic import (
    BEARTYPE_INLINE_ARGS_PLACEHOLDER,
    BEARTYPE_INLINE_RETURN_PLACEHOLDER,
)
from collections.abc import Callable
from types import FunctionType

# ....................{ NOOPS                              }....................
def noop_check_args(*args, **kwargs) -> None:
    '''
    No-op inline parameter checker, bound in place of a placeholder whenever no
    real checker is generated (e.g., because the callable is unannotated, is
    decorated by :func:`typing.no_type_check`, or is blacklisted).
    '''

    return None


def noop_check_return(obj: object) -> object:
    '''
    No-op inline return checker, bound in place of a placeholder whenever no
    real checker is generated. Returns the passed object as is.
    '''

    return obj

# ....................{ TESTERS                            }....................
def is_func_inline_ready(func: Callable) -> bool:
    '''
    :data:`True` only if the passed callable is a pure-Python function whose
    code object has had its inline placeholders bound to no-ops by the
    :func:`.beartype_inline_init` decorator and thus awaits real type-checkers.

    Parameters
    ----------
    func : Callable
        Callable to be inspected.

    Returns
    -------
    bool
        :data:`True` only if this callable awaits real inline type-checkers.
    '''

    # Return true only if this callable is a pure-Python function (rather than,
    # say, a bound method, whose "__code__" cannot be reassigned) containing at
    # least one no-op checker in its constants.
    return type(func) is FunctionType and any(
        const is noop_check_args or const is noop_check_return
        for const in func.__code__.co_consts
    )

# ....................{ DECORATORS                         }....................
def beartype_inline_init(func: Callable) -> Callable:
    '''
    Bind the placeholders of the passed callable instrumented by the
    :mod:`beartype.claw` AST transformer to no-op checkers.

    This decorator is applied as the innermost decorator of every instrumented
    callable and thus *cannot* raise.

    Parameters
    ----------
    func : Callable
        Instrumented callable to be initialized.

    Returns
    -------
    Callable
        That same callable.
    '''

    # Replace both placeholder strings with no-ops. If this object is somehow
    # *NOT* a pure-Python function, there is nothing to replace.
    if type(func) is FunctionType:
        swap_inline_checkers(
            func=func,
            args_old=BEARTYPE_INLINE_ARGS_PLACEHOLDER,
            args_new=noop_check_args,
            return_old=BEARTYPE_INLINE_RETURN_PLACEHOLDER,
            return_new=noop_check_return,
        )

    # Return this callable as is.
    return func

# ....................{ SWAPPERS                           }....................
def swap_inline_checkers(
    func: FunctionType,
    args_old: object,
    args_new: Callable,
    return_old: object,
    return_new: Callable,
) -> None:
    '''
    Replace all constants of the code object of the passed function that are
    either equal to or identical to the passed old parameter and return checkers
    (or placeholders) with the passed new checkers, in-place.

    Parameters
    ----------
    func : FunctionType
        Pure-Python function to be modified.
    args_old : object
        Old parameter checker or placeholder string.
    args_new : Callable
        New parameter checker.
    return_old : object
        Old return checker or placeholder string.
    return_new : Callable
        New return checker.
    '''

    # Code object underlying this function.
    code = func.__code__

    # Replace this code object with a clone whose constants are swapped.
    func.__code__ = code.replace(co_consts=tuple([
        args_new if const is args_old or const == args_old else
        return_new if const is return_old or const == return_old else
        const
        for const in code.co_consts
    ]))
