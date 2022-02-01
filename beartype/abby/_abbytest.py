#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2022 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype type-checking testers** (i.e., functions type-checking arbitrary
objects against PEP-compliant type hints, callable at *any* arbitrary time
during the lifecycle of the active Python process).
'''

# ....................{ IMPORTS                           }....................
from beartype import beartype
from beartype.roar import BeartypeCallHintPepReturnException

# ....................{ VALIDATORS                        }....................
#FIXME: Implement us up, please.
#FIXME: Unit test us up, please.
#FIXME: Document us up, please.
def die_if_bearable(obj, annotation):
    pass

# ....................{ TESTERS                           }....................
#FIXME: Unit test us up, please.
#FIXME: Optimize us up, please. See this discussion for voluminous details:
#    https://github.com/beartype/beartype/issues/87#issuecomment-1020856517
def is_bearable(obj: object, hint: object) -> bool:
    '''
    ``True`` only if the passed arbitrary object satisfies the passed
    PEP-compliant type hint.

    Parameters
    ----------
    obj : object
        Arbitrary object to be tested against this hint.
    hint : object
        PEP-compliant type hint to test this object against.

    Returns
    ----------
    bool
        ``True`` only if this object satisfies this hint.

    Examples
    ----------
        >>> from beartype.abby import is_bearable
        >>> is_bearable(['Things', 'fall', 'apart;'], list[str])
        True
        >>> is_bearable(['the', 'centre', 'cannot', 'hold;'], list[int])
        False
    '''

    # @beartype-decorated closure raising an
    # "BeartypeCallHintPepReturnException" exception if the parameter passed to
    # this closure violates the hint passed to this parent tester.
    #
    # Note that:
    # * Type-checking return values is marginally faster than type-checking
    #   parameters. Ergo, we intentionally annotate this return rather than
    #   parameter of this closure.
    # * This closure intentionally accepts a uniquely named parameter rather
    #   than directly referencing the object passed to this parent tester,
    #   enabling this closure to be subsequently cached and passed other
    #   arbitrary objects.
    @beartype
    def _die_if_pith_violates_hint(pith) -> hint:  # type: ignore[valid-type]
        return pith

    # Attempt to...
    try:
        # Type-check this object by passing this object to this closure, which
        # then implicitly type-checks this object as a return value.
        _die_if_pith_violates_hint(obj)

        # If this closure fails to raise an exception, this object *MUST*
        # necessarily satisfy this hint. In this case, return true.
        return True
    # If this closure raises an exception indicating this object violates this
    # hint, silently squelch this exception and return false below.
    except BeartypeCallHintPepReturnException:
        pass
    # Else, this closure raised another exception. In this case, percolate this
    # exception back up this call stack.

    # Return false, since this object violates this hint. (See above.)
    return False
