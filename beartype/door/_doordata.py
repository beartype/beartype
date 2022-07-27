#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2022 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype Decidedly Object-Oriented Runtime-checking (DOOR) data** (i.e.,
global constants internally required throughout the :mod:`beartype.door`
subpackage).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.door._doorcls import (
    TypeHint,
    _TypeHintClass,
    _TypeHintOriginIsinstanceableArgs1,
    _TypeHintOriginIsinstanceableArgs2,
    _TypeHintOriginIsinstanceableArgs3,
    _TypeHintSubscripted,
)
from beartype.door._proposal.doorpep484604 import _TypeHintUnion
from beartype.door._proposal.doorpep586 import _TypeHintLiteral
from beartype.door._proposal.doorpep593 import _TypeHintAnnotated
from beartype.door._proposal.pep484.doorpep484newtype import _TypeHintNewType
from beartype.door._proposal.pep484.doorpep484typevar import _TypeHintTypeVar
from beartype.door._proposal.pep484585.doorpep484585callable import (
    _TypeHintCallable)
from beartype.door._proposal.pep484585.doorpep484585tuple import (
    _TypeHintTuple)
from beartype.roar import (
    BeartypeDoorNonpepException,
    # BeartypeDoorPepUnsupportedException,
)
from beartype.typing import (
    Dict,
    Type,
)
from beartype._data.hint.pep.sign.datapepsigncls import HintSign
from beartype._data.hint.pep.sign.datapepsigns import (
    HintSignAnnotated,
    HintSignCallable,
    HintSignGeneric,
    HintSignLiteral,
    HintSignNewType,
    HintSignTuple,
    HintSignTypeVar,
)
from beartype._util.hint.pep.utilpepget import (
    get_hint_pep_args,
    get_hint_pep_sign_or_none,
)

# ....................{ GETTERS                            }....................
def get_typehint_subclass(hint: object) -> Type[TypeHint]:
    '''
    Concrete :class:`TypeHint` subclass handling the passed low-level unwrapped
    PEP-compliant type hint if any *or* raise an exception otherwise.

    Parameters
    ----------
    hint : object
        Low-level type hint to be inspected.

    Returns
    ----------
    Type[TypeHint]
        Concrete subclass of the abstract :mod:`TypeHint` superclass handling
        this hint.

    Raises
    ----------
    BeartypeDoorNonpepException
        If this API does *not* currently support the passed hint.
    BeartypeDecorHintPepSignException
        If the passed hint is *not* actually a PEP-compliant type hint.
    '''

    # Sign uniquely identifying this hint if any *OR* return None
    # (i.e., if this hint is *NOT* actually a PEP-compliant type hint).
    hint_sign = get_hint_pep_sign_or_none(hint)

    # Private concrete subclass of this ABC handling this hint if any *OR*
    # "None" otherwise (i.e., if no such subclass has been authored yet).
    typehint_subclass = _HINT_SIGN_TO_TYPEHINT.get(hint_sign)

    # If this hint appears to be currently unsupported...
    if typehint_subclass is None:
        # FIXME: The second condition here is kinda intense. Should we really
        # be conflating typing attributes that aren't types with objects that
        # are types? If so, refactor as follows to transparently support
        # the third-party "typing_extensions" module (as much as reasonably
        # can be, anyway):
        #    from beartype._util.hint.pep.utilpeptest import is_hint_pep_typing
        #    if isinstance(hint, type) or is_hint_pep_typing(hint):  # <-- ...still unsure about this
        if isinstance(hint, type) or getattr(hint, "__module__", "") == "typing":
            typehint_subclass = _TypeHintClass
        else:
            raise BeartypeDoorNonpepException(
                f'Type hint {repr(hint)} invalid '
                f'(i.e., either PEP-noncompliant or '
                f'PEP-compliant but currently unsupported).'
            )
    # Else, this hint is supported.

    #FIXME: Add this new global to "datapepsignset" and reference below:
    #    HINT_SIGNS_ORIGINLESS = frozenset((
    #        HintSignNewType,
    #        HintSignTypeVar,
    #    ))
    #
    #Alternately, it might be preferable to refactor this to resemble:
    #    if (
    #       not get_hint_pep_args(hint) and
    #       get_hint_pep_origin_or_none(hint) is None
    #    ):
    #        typehint_subclass = _TypeHintClass
    #
    #That's possibly simpler and cleaner, as it seamlessly conveys the exact
    #condition we're going for -- assuming it works, of course. *sigh*

    # If a subscriptable type has no args, all we care about is the origin.
    if not get_hint_pep_args(hint) and hint_sign not in {
        HintSignNewType,
        HintSignTypeVar,
    }:
        typehint_subclass = _TypeHintClass

    # Return this subclass.
    return typehint_subclass

# ....................{ PRIVATE ~ globals                  }....................
# Further initialized below by the _init() function.
_HINT_SIGN_TO_TYPEHINT: Dict[HintSign, Type[TypeHint]] = {
    HintSignAnnotated: _TypeHintAnnotated,
    HintSignCallable: _TypeHintCallable,
    HintSignGeneric: _TypeHintSubscripted,
    HintSignLiteral: _TypeHintLiteral,
    HintSignNewType: _TypeHintNewType,
    HintSignTuple: _TypeHintTuple,
    HintSignTypeVar: _TypeHintTypeVar,
}
'''
Dictionary mapping from each sign uniquely identifying PEP-compliant type hints
to the :class:`TypeHint` subclass handling those hints.
'''

# ....................{ PRIVATE ~ initializers             }....................
def _init() -> None:
    '''
    Initialize this submodule.
    '''

    # Isolate function-specific imports.
    from beartype._data.hint.pep.sign.datapepsignset import (
        HINT_SIGNS_ORIGIN_ISINSTANCEABLE_ARGS_1,
        HINT_SIGNS_ORIGIN_ISINSTANCEABLE_ARGS_2,
        HINT_SIGNS_ORIGIN_ISINSTANCEABLE_ARGS_3,
        HINT_SIGNS_UNION,
    )

    # Fully initialize the "HINT_SIGN_TO_TYPEHINT" dictionary declared above.
    for sign in HINT_SIGNS_ORIGIN_ISINSTANCEABLE_ARGS_1:
        _HINT_SIGN_TO_TYPEHINT[sign] = _TypeHintOriginIsinstanceableArgs1
    for sign in HINT_SIGNS_ORIGIN_ISINSTANCEABLE_ARGS_2:
        _HINT_SIGN_TO_TYPEHINT[sign] = _TypeHintOriginIsinstanceableArgs2
    for sign in HINT_SIGNS_ORIGIN_ISINSTANCEABLE_ARGS_3:
        _HINT_SIGN_TO_TYPEHINT[sign] = _TypeHintOriginIsinstanceableArgs3
    for sign in HINT_SIGNS_UNION:
        _HINT_SIGN_TO_TYPEHINT[sign] = _TypeHintUnion


# Initialize this submodule.
_init()
