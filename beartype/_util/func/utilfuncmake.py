#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2021 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **callable creation** utilities.

This private submodule implements utility functions dynamically creating new
callables on-the-fly.

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                           }....................
from beartype.roar import _BeartypeUtilCallableException
from beartype._util.func.utilfuncscope import CallableScope
from beartype._util.text.utiltextmunge import number_lines
from collections.abc import Callable
from functools import update_wrapper
from typing import Optional

# ....................{ TESTERS ~ kind                    }....................
def make_func(
    # Mandatory arguments.
    func_name: str,
    func_code: str,

    # Optional arguments.
    func_globals: Optional[CallableScope] = None,
    func_locals:  Optional[CallableScope] = None,
    func_label:   Optional[str] = None,
    func_wrapped: Optional[Callable] = None,
    exception_cls: type = _BeartypeUtilCallableException,
) -> Callable:
    '''
    Dynamically create and return a new function with the passed name declared
    by the passed code snippet and internally accessing the passed dictionaries
    of globally and locally scoped variables.

    Parameters
    ----------
    func_name : str
        Name of the function to be created.
    func_code : str
        Code snippet declaring this function, including both this function's
        signature prefixed by zero or more decorations *and* body. **This
        snippet must be unindented.** If this snippet is indented, this factory
        raises a syntax error.
    func_globals : Dict[str, Any], optional
        Dictionary mapping from the name to value of each **globally scoped
        attribute** (i.e., internally referenced in the body of the function
        declared by this code snippet). Defaults to the empty dictionary.
    func_locals : Dict[str, Any], optional
        Dictionary mapping from the name to value of each **locally scoped
        attribute** (i.e., internally referenced either in the signature of
        the function declared by this code snippet *or* as decorators
        decorating that function). **Note that this factory necessarily
        modifies the contents of this dictionary.** Defaults to the empty
        dictionary.
    func_label : str, optional
        Human-readable label describing this function for error-handling
        purposes. Defaults to ``{name}()``.
    func_wrapped : Callable, optional
        Callable wrapped by the function to be created. If non-``None``,
        special dunder attributes will be propagated (i.e., copied) from this
        wrapped callable into this created function; these include:

        * ``__name__``, this function's unqualified name.
        * ``__doc__``, this function's docstring.
        * ``__module__``, the fully-qualified name of this function's module.

        Defaults to ``None``.
    exception_cls : type, optional
        Class of exception to be raised in the event of a fatal error. Defaults
        to :exc:`_BeartypeUtilCallableException`.

    Returns
    ----------
    Callable
        Function with this name declared by this snippet.

    Raises
    ----------
    exception_cls
        If either:

        * ``func_locals`` contains a key whose value is that of ``func_name``,
          implying the caller already declared a local attribute whose name
          collides with that of this function.
        * This code snippet is syntactically invalid.
        * This code snippet is syntactically valid but fails to declare a
          function with this name.
    '''
    assert isinstance(func_name, str), f'{repr(func_name)} not string.'
    assert isinstance(func_code, str), f'{repr(func_code)} not string.'

    # Default all unpassed parameters.
    if func_globals is None:
        func_globals = {}
    if func_locals is None:
        func_locals = {}
    if func_label is None:
        func_label = f'{func_name}()'
    assert isinstance(func_globals, dict), (
        f'{repr(func_globals)} not dictionary.')
    assert isinstance(func_locals, dict), (
        f'{repr(func_locals)} not dictionary.')
    assert isinstance(func_label, str), f'{repr(func_label)} not string.'

    # If this function's name is already in this local scope, the caller
    # already declared a local attribute whose name collides with this
    # function's. For safety, raise an exception.
    if func_name in func_locals:
        raise exception_cls(
            f'{func_label} already defined by caller locals:\n'
            f'{repr(func_locals)}'
        )

    # Attempt to declare this function as a closure of this factory. For
    # obscure and presumably uninteresting reasons, Python fails to locally
    # declare this closure when the locals() dictionary is passed; to capture
    # this closure, a local dictionary must be passed instead.
    #
    # Note that the same result may also be achieved via the compile() builtin
    # and "types.FunctionType" class: e.g.,
    #
    #     func_code_compiled = compile(
    #         func_code, "<string>", "exec").co_consts[0]
    #     return types.FunctionType(
    #         code=func_code_compiled,
    #         globals=_GLOBAL_ATTRS,
    #         argdefs=('__beartype_func', func)
    #     )
    #
    # Since doing so is both more verbose and obfuscatory for no tangible gain,
    # the current circumspect approach is preferred.
    try:
        # print('\n@beartyped {} wrapper:\n\n{}\n'.format(func_data.func_name, number_lines(func_code)))
        exec(func_code, func_globals, func_locals)

        #FIXME: See above.
        #FIXME: Should "exec" be "single" instead? Does it matter? Is there any
        #performance gap between the two?
        # func_code_compiled = compile(
        #     func_code, func_wrapper_filename, "exec").co_consts[0]
        # return FunctionType(
        #     code=func_code_compiled,
        #     globals=_GLOBAL_ATTRS,
        #
        #     #FIXME: This really doesn't seem right, but... *shrug*
        #     argdefs=tuple(local_attrs.values()),
        # )
    # If doing so fails for any reason...
    except Exception as exception:
        # Raise an exception suffixed by this function's declaration such that
        # each line of that declaration is prefixed by that line's number. This
        # renders "SyntaxError" exceptions referencing arbitrary line numbers
        # human-readable: e.g.,
        #       File "<string>", line 56
        #         if not (
        #          ^
        #     SyntaxError: invalid syntax
        raise exception_cls(
            f'{func_label} unparseable:\n\n'
            f'{number_lines(func_code)}'
        ) from exception

    # If this function's name is *NOT* in this local scope, this code snippet
    # failed to declare this function. In this case, raise an exception.
    if func_name not in func_locals:
        raise exception_cls(
            f'{func_label} undefined by code snippet:\n\n'
            f'{number_lines(func_code)}'
        )

    # Function declared by this code snippet.
    func: Callable = func_locals[func_name]  # type: ignore[assignment]

    # If this function is uncallable and thus *NOT* a function, raise an
    # exception.
    if not callable(func):
        raise exception_cls(
            f'{func_label} defined by code snippet uncallable:\n\n'
            f'{number_lines(func_code)}'
        )

    # If this function wraps another callable, propagate dunder attributes from
    # that wrapped callable onto this wrapper function.
    if func_wrapped is not None:
        assert callable(func_wrapped), f'{repr(func_wrapped)} uncallable.'
        update_wrapper(wrapper=func, wrapped=func_wrapped)

    # Return this function.
    return func
