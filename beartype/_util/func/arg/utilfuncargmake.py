#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Callable-specific signature code generation utilities.

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.roar import BeartypeDecorParamNameException
from beartype._conf.confmain import BeartypeConf
from beartype._data.func.datafuncarg import ARG_NAME_RETURN
from beartype._data.kind.datakindiota import SENTINEL
from beartype._data.typing.datatyping import LexicalScope
from beartype._util.func.arg.utilfuncargiter import (
    ArgKind,
    ArgMandatory,
    iter_func_args,
)
from beartype._util.func.utilfuncscope import add_func_scope_attr
from beartype._util.func.utilfunccodeobj import get_func_codeobject
from beartype._util.func.utilfunctest import is_func_coro, is_func_async_generator
from beartype._util.text.utiltextrepr import represent_object
from collections.abc import Callable
from keyword import iskeyword
from typing import Optional

# ....................{ FACTORIES                          }....................
def make_func_signature(
    # Mandatory parameters.
    func: Callable,
    func_scope: LexicalScope,
    conf: BeartypeConf,

    # Optional parameters.
    func_name: Optional[str] = None,
    is_annotated: bool = True,
    arg_default_override: object = ArgMandatory,
) -> str:
    '''
    Generate a callable-specific wrapper signature augmented by hidden scope
    parameters.

    This factory preserves parameter kinds and default object identities,
    without evaluating the representations of defaults or annotations. It
    introspects the actual callable rather than following ``__wrapped__``.
    Bound methods omit their implicitly supplied first parameter.

    Parameters
    ----------
    func : Callable
        Pure-Python callable whose parameters are to be reproduced.
    func_scope : dict[str, object]
        Scope containing hidden wrapper parameters. Defaults and annotations
        referenced by this signature are added to this dictionary. All hidden
        parameters are keyword-only and precede any variadic keyword parameter.
    conf : BeartypeConf
        Configuration controlling optional debug comments.
    func_name : str or None, optional
        Wrapper name, defaulting to the callable name or ``__beartype_wrapper``
        when that name is not a valid identifier (e.g., a lambda).
    is_annotated : bool, optional
        Whether to reproduce annotations. Defaults to true. Callers already
        copying annotation metadata with ``functools.update_wrapper`` may
        disable this to avoid redundant annotation evaluation.

    arg_default_override : object, optional
        Replacement for all optional parameter defaults, or ``ArgMandatory``
        to preserve their original values. Wrapper generators may use an
        omission sentinel to distinguish omitted defaults from explicitly
        supplied values. The wrapper body must restore omitted defaults before
        forwarding the call.

    Returns
    -------
    str
        Function declaration ending in a colon and newline. Coroutine and
        asynchronous generator functions use ``async def``. Synchronous
        generator functions use ``def``.

    Raises
    ------
    BeartypeDecorParamNameException
        If a parameter uses the reserved ``__bear`` prefix, or the explicitly
        supplied wrapper name is not a valid Python identifier.
    '''
    assert callable(func), f'{repr(func)} uncallable.'
    assert isinstance(func_scope, dict), f'{repr(func_scope)} not dictionary.'
    assert isinstance(conf, BeartypeConf), f'{repr(conf)} not configuration.'
    assert isinstance(is_annotated, bool), f'{repr(is_annotated)} not boolean.'

    if func_name is None:
        func_name = func.__name__
        if not func_name.isidentifier() or iskeyword(func_name):
            func_name = '__beartype_wrapper'
    elif not func_name.isidentifier() or iskeyword(func_name):
        raise BeartypeDecorParamNameException(
            f'Wrapper name {repr(func_name)} not a Python identifier.')

    # Validate the callable before accessing Python-specific attributes.
    func_codeobj = get_func_codeobject(func, is_unwrap=False)
    annotations = func.__annotations__ if is_annotated else {}
    is_async = is_func_coro(func) or is_func_async_generator(func)
    signature = f'{"async " if is_async else ""}def {func_name}(\n'
    is_keyword_only = False
    is_positional_only = False
    code_variadic_keyword = ''

    # Explicit code metadata avoids a parameter-count cache copied by wraps().
    for arg_kind, arg_name, arg_default in iter_func_args(
        func, func_codeobj=func_codeobj, is_unwrap=False):
        if arg_name.startswith('__bear'):
            raise BeartypeDecorParamNameException(
                f'Parameter {repr(arg_name)} reserved by @beartype.')

        # Close the positional-only group before entering the next group.
        if is_positional_only and arg_kind is not ArgKind.POSITIONAL_ONLY:
            signature += '    /,\n'
            is_positional_only = False

        if arg_kind is ArgKind.POSITIONAL_ONLY:
            is_positional_only = True
        elif arg_kind is ArgKind.KEYWORD_ONLY and not is_keyword_only:
            signature += '    *,\n'
            is_keyword_only = True

        declaration = arg_name
        if arg_kind is ArgKind.VARIADIC_POSITIONAL:
            declaration = f'*{declaration}'
            is_keyword_only = True
        elif arg_kind is ArgKind.VARIADIC_KEYWORD:
            declaration = f'**{declaration}'

        arg_hint = annotations.get(arg_name, SENTINEL)
        if arg_hint is not SENTINEL:
            hint_name = add_func_scope_attr(arg_hint, func_scope)
            declaration += f': {hint_name}'
        if arg_default is not ArgMandatory:
            default_name = add_func_scope_attr(
                arg_default if arg_default_override is ArgMandatory else
                arg_default_override, func_scope)
            declaration += f'={default_name}'

        declaration = f'    {declaration},\n'
        if arg_kind is ArgKind.VARIADIC_KEYWORD:
            # Hidden keyword-only parameters must precede **kwargs.
            code_variadic_keyword = declaration
        else:
            signature += declaration

    if is_positional_only:
        signature += '    /,\n'

    return_hint = annotations.get(ARG_NAME_RETURN, SENTINEL)
    return_annotation = ''
    if return_hint is not SENTINEL:
        hint_name = add_func_scope_attr(return_hint, func_scope)
        return_annotation = f' -> {hint_name}'

    if func_scope and not is_keyword_only:
        signature += '    *,\n'
    for arg_name, arg_value in func_scope.items():
        arg_comment = (
            f' # is {represent_object(arg_value)}' if conf.is_debug else '')
        signature += f'    {arg_name}={arg_name},{arg_comment}\n'

    return f'{signature}{code_variadic_keyword}){return_annotation}:\n'
