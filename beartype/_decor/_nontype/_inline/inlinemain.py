#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype inline decorator** (i.e., low-level decorator binding dynamically
generated type-checkers directly into a callable instrumented by the
:mod:`beartype.claw` abstract syntax tree (AST) transformer, rather than
wrapping that callable with an additional stack frame).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.roar import BeartypeDecorWrapperException
from beartype._check.cls.call.calldatadecorfunc import (
    BeartypeCallDecorFuncData,
    cull_decor_func,
)
from beartype._data.check.code.datacodename import ARG_NAME_CALL_META
from beartype._data.typing.datatyping import LexicalScope
from beartype._decor._nontype._inline.inlineinit import (
    noop_check_args,
    noop_check_return,
    swap_inline_checkers,
)
from beartype._decor._nontype._wrap.wrapmain import (
    generate_code_check_args,
    generate_code_check_return,
)
from beartype._util.bear.utilbearfunc import set_func_beartyped
from beartype._util.func.utilfuncmake import make_func
from collections.abc import Callable

# ....................{ DECORATORS                         }....................
def beartype_func_inline(
    decor_func: BeartypeCallDecorFuncData,
    func_globals: LexicalScope,
) -> Callable:
    '''
    Decorate the callable described by the passed metadata with inline
    type-checking by replacing the no-op checkers bound to that callable by
    real checkers, returning that callable *itself* (rather than a wrapper).

    Parameters
    ----------
    decor_func : BeartypeCallDecorFuncData
        Beartype decorator call metadata describing a callable for which
        :func:`beartype._decor._nontype._inline.inlineinit.is_func_inline_ready`
        is :data:`True`.
    func_globals : LexicalScope
        Global scope in which to define the generated checkers.

    Returns
    -------
    Callable
        That same callable.
    '''

    # Callable to be decorated.
    func = decor_func.func_wrappee

    # Code snippets defining the inline parameter and return checkers if these
    # parameters and return require type-checking *OR* the empty string
    # otherwise, each paired with the hidden parameters of that checker.
    code_args, scope_args = generate_code_check_args(decor_func)
    code_return, scope_return = generate_code_check_return(decor_func)

    # If this callable requires type-checking...
    if code_args or code_return:
        # Register changes to the type hints annotating this callable if any.
        decor_func.set_func_annotations_if_dirty()

        # Minimal metadata snapshotted only now that *BOTH* checkers have been
        # generated, as either may have created the forward scope. Expose this
        # metadata to each checker that requires it.
        call_meta = decor_func.minify()
        if code_args:
            scope_args[ARG_NAME_CALL_META] = call_meta
        if code_return:
            scope_return[ARG_NAME_CALL_META] = call_meta

        # Real checkers if required *OR* the existing no-ops otherwise.
        check_args = check_return = None

        # If parameters require type-checking, define a checker doing so.
        if code_args:
            check_args = make_func(
                func_name=decor_func.func_wrapper_name,
                func_code=code_args,
                func_globals=func_globals,
                func_locals=scope_args,
                func_labeller=decor_func.label_func_wrapper,
                is_debug=decor_func.conf.is_debug,
                exception_cls=BeartypeDecorWrapperException,
            )

        # If the return requires type-checking, define a checker doing so.
        if code_return:
            check_return = make_func(
                func_name=decor_func.func_wrapper_name,
                func_code=code_return,
                func_globals=func_globals,
                func_locals=scope_return,
                func_labeller=decor_func.label_func_wrapper,
                is_debug=decor_func.conf.is_debug,
                exception_cls=BeartypeDecorWrapperException,
            )

        # Bind these checkers in place of the no-ops currently bound.
        swap_inline_checkers(
            func=func,  # type: ignore[arg-type]
            args_old=noop_check_args,
            args_new=check_args or noop_check_args,
            return_old=noop_check_return,
            return_new=check_return or noop_check_return,
        )

        # Declare this callable to be beartyped, preventing redecoration.
        set_func_beartyped(func)
    # Else, this callable requires *NO* type-checking. Preserve the no-ops.

    # Deinitialize this beartype call metadata.
    cull_decor_func(decor_func)

    # Return this callable as is.
    return func
