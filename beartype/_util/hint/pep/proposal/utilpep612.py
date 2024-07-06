#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2024 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`612`-compliant **parameter specification** (i.e.,
:obj:`typing.ParamSpec` type hints and instance variables of those hints)
utilities.

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.typing import (
    Callable,
    Optional,
)

# ....................{ REDUCERS                           }....................
#FIXME: Unit test us up, please.
def reduce_hint_pep612_args(
    hint: object,
    func: Optional[Callable],
    pith_name: Optional[str],
    exception_prefix: str,
    *args, **kwargs
) -> object:
    '''
    Reduce the passed :pep:`612`-compliant **parameter specification variadic
    positional argument instance variable** (i.e., low-level C-based
    :obj:`typing.ParamSpecArgs` object annotating a variadic positional argument
    with syntax resembling ``*args: P.args`` for ``P`` a low-level C-based
    :obj:`typing.ParamSpec` parent object) to the ignorable :class:`object`
    superclass.

    This reducer effectively ignores *all* :obj:`typing.ParamSpecArgs` objects.
    Although these objects do convey meaningful metadata and semantics, they do
    so in a manner uniquely suited to pure static type-checkers. Why? Because
    type-checking these objects requires tracking parameter specifications
    across disparate callable signatures separated - in the worst case - in both
    space and time. Although :mod:`beartype` could type-check these objects at a
    later date, doing so is highly non-trivial and thus deferred to the
    sacrificial blood sacrifice that is reading this. Sorry. That's you.

    This reducer is intentionally *not* memoized (e.g., by the
    ``callable_cached`` decorator), as reducers cannot be memoized.

    Parameters
    ----------
    hint : object
        Typed dictionary to be reduced.
    func : Optional[Callable]
        Either:

        * If this hint annotates a parameter or return of some callable, that
          callable.
        * Else, :data:`None`.
    pith_name : Optional[str]
        Either:

        * If this hint annotates a parameter of some callable, the name of that
          parameter.
        * If this hint annotates the return of some callable, ``"return"``.
        * Else, :data:`None`.

        Defaults to :data:`None`.
    exception_prefix : str
        Substring prefixing exception messages raised by this reducer.

    All remaining passed arguments are silently ignored.

    Returns
    -------
    object
        Lower-level type hint currently supported by :mod:`beartype`.

    Raises
    ------
    BeartypeDecorHintPep612Exception
        If this hint does *not* annotate a variadic positional argument.
    '''

    #FIXME: Implement us up, please. Note that this will be a bit non-trivial.
    #We still need to:
    #* Generalize resolve_hint() to accept a new parameter:
    #      func_arg_name_to_hint: Optional[DictStrToAny] = None,
    #* Refactor resolve_hint() and children to pass that parameter onto this
    #  function.
    #* Refactor sanify_hint_root_func() to pass that parameter.
    #* Refactor this function to accept that parameter.

    # If this hint does *NOT* annotate a variadic positional argument, raise an
    # exception.
    # if ...:
    #     raise BeartypeDecorHintPep612Exception(...)

    # Reduce *ALL* PEP 612 type hints to an arbitrary ignorable type hint.
    return object


#FIXME: Unit test us up, please.
def reduce_hint_pep612_kwargs(
    hint: object,
    func: Optional[Callable],
    pith_name: Optional[str],
    exception_prefix: str,
    *args, **kwargs
) -> object:
    '''
    Reduce the passed :pep:`612`-compliant **parameter specification variadic
    keyword argument instance variable** (i.e., low-level C-based
    :obj:`typing.ParamSpecKwargs` object annotating a variadic keyword
    argument with syntax resembling ``**kwargs: P.kwargs`` for ``P`` a low-level
    C-based :obj:`typing.ParamSpec` parent object) to the ignorable
    :class:`object` superclass.

    This reducer is intentionally *not* memoized (e.g., by the
    ``callable_cached`` decorator), as reducers cannot be memoized.

    See Also
    --------
    :func:`.reduce_hint_pep612_args`
        Further details.
    '''

    #FIXME: Implement us up, please. Note that this will be a bit non-trivial.
    #We still need to:
    #* Generalize resolve_hint() to accept a new parameter:
    #      func_arg_name_to_hint: Optional[DictStrToAny] = None,
    #* Refactor resolve_hint() and children to pass that parameter onto this
    #  function.
    #* Refactor sanify_hint_root_func() to pass that parameter.
    #* Refactor this function to accept that parameter.

    # If this hint does *NOT* annotate a variadic positional argument, raise an
    # exception.
    # if ...:
    #     raise BeartypeDecorHintPep612Exception(...)

    # Reduce *ALL* PEP 612 type hints to an arbitrary ignorable type hint.
    return object
