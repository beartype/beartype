#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`673`-compliant **self type hint** (i.e., the
:obj:`typing.Self` type hint singleton) utilities.

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.roar import BeartypeDecorHintPep673Exception
from beartype._data.datatyping import TypeStack

# ....................{ REDUCERS                           }....................
#FIXME: Unit test us up, please.
def reduce_hint_pep673(cls_stack: TypeStack, *args, **kwargs) -> type:
    '''
    Reduce the passed :pep:`673`-compliant **self type hint** (i.e.,
    the :obj:`typing.Self` type hint singleton) to the **currently decorated
    class** (i.e., the most deeply nested class on the passed type stack,
    signifying the class currently being decorated by :func:`beartype.beartype`)
    if any *or* raise an exception otherwise (i.e., if *no* class is currently
    being decorated).

    This reducer is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator), as reducers cannot be memoized.

    Parameters
    ----------
    cls_stack : TypeStack, optional
        **Type stack** (i.e., either tuple of zero or more arbitrary types *or*
        :data:`None`). Defaults to :data:`None`. See also the
        :func:`.beartype_object` decorator for further commentary.

    All remaining passed arguments are silently ignored.

    Returns
    ----------
    type
        Most deeply nested class on this type stack.

    Raises
    ----------
    BeartypeDecorHintPep673Exception
        If either:

        * ``cls_stack`` is :data:`None`.
        * ``cls_stack`` is non-:data:`None` but empty.
    '''

    # If the caller passed *NO* type stack, *NO* class is currently being
    # decorated by @beartype. It follows that either:
    # * @beartype is currently decorating a function or method directly.
    # * A statement-level runtime type-checker (e.g.,
    #   beartype.door.is_bearable()) is currently being called.
    #
    # However, the "typing.Self" type hint *CANNOT* be reliably resolved outside 
    # of a class context. Although @beartype could attempt to heuristically
    # differentiate functions from methods via the first passed argument, Python
    # itself does *NOT* require that argument of a method to be named "self"; 
    # such a heuristic would catastrophically fail in common edge cases. Our
    # only recourse is to raise an exception encouraging the user to refactor
    # their code to decorate classes rather than methods.
    if cls_stack is None:
        #FIXME: Pick up here tomorrow, please.
        raise BeartypeDecorHintPep673Exception('')
    # Else, the caller passed a type stack.


    # Reduce this hint to the currently decorated class (i.e., the most deeply
    # nested class on this type stack, signifying the class currently being
    # decorated by @beartype.beartype).
    return cls_stack[-1]
