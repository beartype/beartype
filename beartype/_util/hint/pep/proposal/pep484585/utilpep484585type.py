#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2024 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`484`- and :pep:`585`-compliant **subclass type hint
utilities** (i.e., callables generically applicable to both :pep:`484`- and
:pep:`585`-compliant subclass type hints).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype._util.hint.pep.proposal.pep484585.utilpep484585 import (
    get_hint_pep484585_args)
from typing import (
    Type as typing_Type,  # <-- intentional to distinguish from "type" below
)

# ....................{ REDUCERS                           }....................
#FIXME: *PRETTY SURE THIS IS ABSOLUTE TRASH.* Seriously. Unsure what we on about
#when we originally authored this, but *NONE* of this parses as sane at all.
#Let's quietly unwind this, please. *facepalm*
#FIXME: *OH, HO, HO.* This might be essential after all. We note elsewhere:
#     "Note that:
#      * This reduction could be performed elsewhere, but remains here as doing
#        so here dramatically simplifies matters elsewhere.
#      * This reduction *CANNOT* be performed by the is_hint_ignorable() tester,
#        as subclass type hints subscripted by ignorable child type hints are
#        *NOT* ignorable; they're reducible to the "type" superclass."
#
#Clearly, we should have documented that here as well. Examine closer, please.
def reduce_hint_pep484585_type(
    hint: object, exception_prefix: str, *args, **kwargs) -> object:
    '''
    Reduce the passed :pep:`484`- or :pep:`585`-compliant **subclass type
    hint** (i.e., hint constraining objects to subclass that superclass) to the
    :class:`type` superclass if that hint is subscripted by an ignorable child
    type hint (e.g., :attr:`typing.Any`, :class:`type`) *or* preserve this hint
    as is otherwise (i.e., if that hint is *not* subscripted by an ignorable
    child type hint).

    This reducer is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator), as reducers cannot be memoized.

    Parameters
    ----------
    hint : object
        Subclass type hint to be reduced.
    exception_prefix : str
        Human-readable label prefixing the representation of this object in the
        exception message.

    All remaining passed arguments are silently ignored.

    Raises
    ------
    BeartypeDecorHintPep484585Exception
        If this hint is neither a :pep:`484`- nor :pep:`585`-compliant subclass
        type hint.
    '''

    # Avoid circular import dependencies.
    from beartype._util.hint.utilhinttest import is_hint_ignorable

    # If this hint is the unsubscripted PEP 484-compliant subclass type hint,
    # immediately reduce this hint to the "type" superclass.
    #
    # Note that this is *NOT* merely a nonsensical optimization. The
    # implementation of the unsubscripted PEP 484-compliant subclass type hint
    # significantly differs across Python versions. Under some but *NOT* all
    # supported Python versions (notably, Python 3.7 and 3.8), the "typing"
    # module subversively subscripts this hint by a type variable; under all
    # others, this hint remains unsubscripted. In the latter case, passing this
    # hint to the subsequent get_hint_pep484585_args() call would erroneously
    # raise an exception.
    if hint is typing_Type:
        return type
    # Else, this hint is *NOT* the unsubscripted PEP 484-compliant subclass
    # type hint.

    # Superclass subscripting this hint.
    #
    # Note that we intentionally do *NOT* call the high-level
    # get_hint_pep484585_type_superclass() getter here, as the
    # validation performed by that function would raise exceptions for
    # various child type hints that are otherwise permissible (e.g.,
    # "typing.Any").
    hint_superclass = get_hint_pep484585_args(
        hint=hint, args_len=1, exception_prefix=exception_prefix)

    # If this argument is either...
    if (
        # An ignorable type hint (e.g., "object", "typing.Any") *OR*...
        is_hint_ignorable(hint_superclass) or

        #FIXME: *UHM.* What? This isn't the case *AT ALL*, is it? I mean, aren't
        #the only classes that subclass the "type" superclass metaclasses? Don't
        #normal classes just subclass "object"? Aren't normal classes just
        #*INSTANCES* of "type" rather than *SUBCLASSES* of "type"? Pretty sure
        #we were extremely confused when we authored this. *sigh*
        # The "type" superclass, which is effectively ignorable in this
        # context of subclasses, as *ALL* classes necessarily subclass
        # that superclass.
        hint_superclass is type
    ):
        # Reduce this subclass type hint to the "type" superclass.
        hint = type
    # Else, this argument is unignorable and thus irreducible.

    # Return this possibly reduced type hint.
    return hint
