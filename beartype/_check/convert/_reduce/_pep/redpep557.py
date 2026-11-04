#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`557`-compliant **type hint reducers** (i.e., low-level
low-level callables converting higher-level type hints created by subscripting
the :obj:`dataclasses.InitVar` type hint factory to lower-level type hints more
readily consumable by :mod:`beartype`).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype._check.cls.call.calldataabc import BeartypeCallDataABC
from beartype._data.check.error.dataerrmagic import EXCEPTION_PLACEHOLDER
from beartype._data.func.datafuncarg import ARG_NAME_RETURN
from beartype._data.func.datafunccodeobj import CODE_OBJECT_FILENAME_EVAL
from beartype._data.typing.datatypingport import Hint
from beartype._util.cls.pep.clspep252 import is_type_pep252_descriptor_data
from beartype._util.cls.pep.clspep557 import is_type_pep557_dataclass
from beartype._util.hint.pep.proposal.pep557 import get_hint_pep557_initvar_arg
from beartype._util.hint.pep.proposal.pep749.pep649749annotate import (
    get_hintable_pep649749_annotations)

from beartype._util.func.utilfunccodeobj import get_func_codeobject_or_none
from beartype._util.func.utilfuncwrap import unwrap_func_all
from dataclasses import fields
from inspect import getattr_static
from types import UnionType
from typing import Annotated, Any, Union, get_args, get_origin

# ....................{ REDUCERS                           }....................
def reduce_hint_pep557_initvar(hint: Hint) -> Hint:
    '''
    Reduce the passed :pep:`557`-compliant **dataclass initialization-only
    instance variable type hint** (i.e., subscription of the
    :obj:`dataclasses.InitVar` type hint factory) to the child type hint
    subscripting this parent hint -- which is otherwise functionally useless
    from the admittedly narrow perspective of runtime type-checking.

    This reducer is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator), as the implementation trivially reduces
    to an efficient one-liner.

    Parameters
    ----------
    hint : Hint
        Type variable to be reduced.

    Returns
    -------
    Hint
        Lower-level type hint currently supported by :mod:`beartype`.
    '''

    # Reduce this "typing.InitVar[{hint}]" type hint to merely that "{hint}".
    return get_hint_pep557_initvar_arg(
        hint=hint, exception_prefix=EXCEPTION_PLACEHOLDER)


def reduce_hint_pep557_descriptor_field(
    call_curr: BeartypeCallDataABC,
    hint: Hint,
    pith_name: str,
    exception_prefix: str,
) -> Hint:
    '''Reduce a bound descriptor's annotation on a generated initializer.

    Apply the existing getter-return convention only where the generated
    initializer assigns the parameter to a descriptor-backed dataclass field.
    Ordinary annotations on methods, custom initializers and unbound fields
    still describe the descriptor object itself.
    '''
    if pith_name == ARG_NAME_RETURN or not call_curr.cls_stack:
        return hint

    cls = call_curr.cls_stack[-1]
    func = call_curr.decoratee
    if getattr(func, '__name__', None) != '__init__':
        return hint

    # Dataclasses exposes no public marker for its generated initializer.
    # Check both the function identity in the class namespace and the code
    # produced by dataclasses' exec-based function factory.
    func = unwrap_func_all(func)
    if unwrap_func_all(getattr_static(cls, '__init__')) is not func:
        return hint
    code = get_func_codeobject_or_none(func)
    if (
        code is None or
        code.co_name != '__init__' or
        code.co_filename != CODE_OBJECT_FILENAME_EVAL or
        not is_type_pep557_dataclass(cls)
    ):
        return hint

    # Static lookup avoids calling the descriptor's getter and respects a
    # subclass overriding an inherited field with an ordinary default.
    descriptor_type = type(getattr_static(cls, pith_name, None))
    if not is_type_pep252_descriptor_data(descriptor_type):
        return hint
    if not any(field.init and field.name == pith_name for field in fields(cls)):
        return hint

    return _replace_descriptor_hint(hint, descriptor_type, exception_prefix)


def _replace_descriptor_hint(
    hint: Hint, descriptor_type: type, exception_prefix: str) -> Hint:
    '''Replace matching descriptor alternatives without visiting container items.'''
    if isinstance(hint, type) and hint in descriptor_type.__mro__:
        if is_type_pep252_descriptor_data(hint):
            annotations = get_hintable_pep649749_annotations(
                hintable=hint.__get__, exception_prefix=exception_prefix)
            return annotations.get(ARG_NAME_RETURN, Any) if annotations else Any
        return hint

    origin = get_origin(hint)
    if origin is Annotated:
        inner, *metadata = get_args(hint)
        reduced = _replace_descriptor_hint(inner, descriptor_type, exception_prefix)
        return hint if reduced is inner else Annotated[(reduced, *metadata)]
    if origin is Union or origin is UnionType:
        children = get_args(hint)
        reduced_children = tuple(
            _replace_descriptor_hint(child, descriptor_type, exception_prefix)
            for child in children
        )
        if any(new is not old for new, old in zip(reduced_children, children)):
            return Union[reduced_children]

    return hint
