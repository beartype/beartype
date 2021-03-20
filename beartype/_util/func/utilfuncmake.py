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
from beartype._util.text.utiltextmunge import number_lines
from collections.abc import Callable
from functools import update_wrapper
from typing import Any, Dict, Optional

# ....................{ TESTERS ~ kind                    }....................
def make_func(
    # Mandatory arguments.
    name: str,
    code: str,

    # Optional arguments.
    attrs_global: Optional[Dict[str, Any]] = None,
    attrs_local:  Optional[Dict[str, Any]] = None,
    label: Optional[str] = None,
    code_exception_cls: type = _BeartypeUtilCallableException,
    func_wrapped: Optional[Callable] = None
) -> Callable:
    '''
    Dynamically create and return a new function with the passed name declared
    by the passed code snippet and internally accessing the passed dictionaries
    of globally and locally scoped variables.

    Parameters
    ----------
    name : str
        Name of the function to be created.
    code : str
        Code snippet declaring this function, including both this function's
        signature prefixed by zero or more decorations *and* body. **This
        snippet must be unindented.** If this snippet is indented, this factory
        raises a syntax error.
    attrs_global : Dict[str, Any], optional
        Dictionary mapping from the name to value of each **globally scoped
        attribute** (i.e., internally referenced in the body of the function
        declared by this code snippet). Defaults to the empty dictionary.
    attrs_local : Dict[str, Any], optional
        Dictionary mapping from the name to value of each **locally scoped
        attribute** (i.e., internally referenced either in the signature of
        the function declared by this code snippet *or* as decorators
        decorating that function). **Note that this factory necessarily
        modifies the contents of this dictionary.** Defaults to the empty
        dictionary.
    label : str, optional
        Human-readable label describing this function for error-handling
        purposes. Defaults to ``{name}()``.
    code_exception_cls : type, optional
        Class of exception to be raised if this code snippet is syntactically
        invalid. Defaults to :exc:`_BeartypeUtilCallableException`.
    func_wrapped : Callable, optional
        Callable wrapped by the function to be created. If non-``None``,
        special dunder attributes will be propagated (i.e., copied) from this
        wrapped callable into this created function; these include:

        * ``__name__``, this function's unqualified name.
        * ``__doc__``, this function's docstring.
        * ``__module__``, the fully-qualified name of this function's module.

        Defaults to ``None``.

    Returns
    ----------
    Callable
        Function with this name declared by this snippet.

    Raises
    ----------
    _BeartypeUtilCallableException
         If this callable is *not* pure-Python.
    '''
    assert isinstance(name, str), f'{repr(name)} not string.'
    assert isinstance(code, str), f'{repr(code)} not string.'

    # Default all unpassed parameters.
    if attrs_global is None:
        attrs_global = {}
    if attrs_local is None:
        attrs_local = {}
    if label is None:
        label = f'{name}()'
    assert isinstance(attrs_global, dict), (
        f'{repr(attrs_global)} not dictionary.')
    assert isinstance(attrs_local, dict), (
        f'{repr(attrs_local)} not dictionary.')
    assert isinstance(label, str), f'{repr(label)} not string.'

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
        exec(code, attrs_global, attrs_local)

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
        raise code_exception_cls(
            f'{label} unparseable:\n\n{number_lines(code)}') from exception

    # This created function.
    #
    # Note that, as the above logic successfully compiled this function, this
    # dictionary is guaranteed to contain a key with this function's name whose
    # value is this function. Ergo, no additional validation of the existence
    # of this key or the type of this function is warranted.
    func: Callable = attrs_local[name]  # type: ignore[assignment]

    # If this function wraps another callable, propagate dunder attributes from
    # that wrapped callable onto this wrapper function.
    if func_wrapped is not None:
        assert callable(func_wrapped), f'{repr(func_wrapped)} uncallable.'
        update_wrapper(wrapper=func, wrapped=func_wrapped)

    # Return this function.
    return func
