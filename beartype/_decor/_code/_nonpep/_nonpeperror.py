#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2020 Cecil Curry.
# See "LICENSE" for further details.

'''
**Beartype PEP-noncompliant type hint call-time utilities** (i.e., callables
operating on PEP-noncompliant type hints intended to be called by dynamically
generated wrapper functions wrapping decorated callables).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                           }....................
from beartype.roar import (
    BeartypeCallHintNonPepParamException,
    BeartypeCallHintNonPepReturnException,
    _BeartypeCallHintNonPepRaiseException
)
from beartype._util.hint.nonpep.utilhintnonpeptest import (
    die_unless_hint_nonpep)
from beartype._util.text.utiltextlabel import (
    label_callable_decorated_param_value,
    label_callable_decorated_return_value,
)
from beartype._util.text.utiltextcause import (
    get_cause_object_not_nonpep_tuple,
    get_cause_object_not_type,
)

# See the "beartype.__init__" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ RAISERS                           }....................
def raise_nonpep_call_exception(
    func: 'CallableTypes',
    pith_name: str,
    pith_value: object,
) -> None:
    '''
    Raise a human-readable exception detailing the failure of the parameter
    with the passed name *or* return value if this name is the magic string
    ``return`` of the passed decorated function fails to satisfy the
    PEP-noncompliant type hint annotated on this parameter or return value.

    Parameters
    ----------
    func : CallableTypes
        Decorated callable to raise this exception from.
    pith_name : str
        Either:

        * If the object failing to satisfy this hint is a passed parameter, the
          name of this parameter.
        * Else, the magic string ``return`` implying this object to be the
          value returned from this callable.
    pith_value : object
        Passed parameter or returned value failing to satisfy this hint.

    Raises
    ----------
    BeartypeCallHintPepParamException
        If the object failing to satisfy this hint is a parameter.
    BeartypeCallHintPepReturnException
        If the object failing to satisfy this hint is a return value.
    BeartypeDecorHintPepException
        If the type hint annotating this object is *not* PEP-noncompliant.
    _BeartypeCallHintNonPepRaiseException
        If the parameter or return value with the passed name is unannotated.
    '''
    assert callable(func), f'{repr(func)} uncallable.'
    assert isinstance(pith_name, str), f'{repr(pith_name)} not string.'
    # print('''raise_pep_call_exception(
    #     func={!r},
    #     pith_name={!r},
    #     pith_value={!r}',
    # )'''.format(func, pith_name, pith_value))

    # Type of exception to be raised.
    exception_cls = None

    # Human-readable label describing this parameter or return value.
    pith_label = None

    # If the name of this parameter is the magic string implying the passed
    # object to be a return value, set the above local variables appropriately.
    if pith_name == 'return':
        exception_cls = BeartypeCallHintNonPepReturnException
        pith_label = label_callable_decorated_return_value(
            func=func, return_value=pith_value)
    # Else, the passed object is a parameter. In this case, set the above local
    # variables appropriately.
    else:
        exception_cls = BeartypeCallHintNonPepParamException
        pith_label = label_callable_decorated_param_value(
            func=func,
            param_name =pith_name,
            param_value=pith_value,
        )

    # PEP-compliant type hint annotating this parameter or return value if any
    # *OR* "None" otherwise (i.e., if this parameter or return value is
    # unannotated).
    hint = func.__annotations__.get(pith_name, None)

    # If this parameter or return value is unannotated, raise an exception.
    #
    # Note that this should *NEVER* occur, as the caller guarantees this
    # parameter or return value to be annotated. Nonetheless, since callers
    # could deface the "__annotations__" dunder dictionary without our
    # knowledge or permission, precautions are warranted.
    if hint is None:
        raise _BeartypeCallHintNonPepRaiseException(
            f'{pith_label} unannotated.')
    # Else, this parameter or return value is annotated.

    # If type hint is *NOT* PEP-noncompliant, raise an exception.
    die_unless_hint_nonpep(
        hint=hint,
        hint_label=f'{pith_label} non-PEP type hint "{repr(hint)}"',
    )
    # Else, this type hint is PEP-noncompliant.

    # Human-readable error message describing the failure of this pith to
    # satisfy this hint.
    exception_cause = None

    # If this hint is a class...
    if isinstance(hint, type):
        exception_cause = get_cause_object_not_type(
            pith=pith_value, hint=hint)
    # Else if this hint is a tuple of classes...
    elif isinstance(hint, tuple):
        exception_cause = get_cause_object_not_nonpep_tuple(
            pith=pith_value, hint=hint)
    # Else, this hint is *NOT* PEP-noncompliant. But by the prior logic, this
    # hint is PEP-compliant. Resolve this paradox by raising an exception.
    else:
        raise _BeartypeCallHintNonPepRaiseException(
            f'{pith_label} type hint "{repr(hint)}" not PEP-noncompliant '
            f'(i.e., neither class nor tuple of classes).')

    # Raise an exception of the desired class embedding this cause.
    raise exception_cls(
        f'{pith_label} violates PEP type hint '
        f'{repr(hint)}, as {exception_cause}.'
    )
