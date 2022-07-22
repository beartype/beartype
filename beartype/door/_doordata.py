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
    _TypeHintAnnotated,
    _TypeHintSubscripted,
    _TypeHintLiteral,
    _TypeHintNewType,
    _TypeHintOriginIsinstanceableArgs1,
    _TypeHintOriginIsinstanceableArgs2,
    _TypeHintOriginIsinstanceableArgs3,
    _TypeHintTuple,
    _TypeHintTypeVar,
    _TypeHintUnion,
)
from beartype.door._proposal.pep484585.doorpep484585callable import (
    _TypeHintCallable)
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

# ....................{ GLOBALS                            }....................
# Further initialized below by the _init() function.
HINT_SIGN_TO_TYPEHINT: Dict[HintSign, Type[TypeHint]] = {
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
        HINT_SIGN_TO_TYPEHINT[sign] = _TypeHintOriginIsinstanceableArgs1
    for sign in HINT_SIGNS_ORIGIN_ISINSTANCEABLE_ARGS_2:
        HINT_SIGN_TO_TYPEHINT[sign] = _TypeHintOriginIsinstanceableArgs2
    for sign in HINT_SIGNS_ORIGIN_ISINSTANCEABLE_ARGS_3:
        HINT_SIGN_TO_TYPEHINT[sign] = _TypeHintOriginIsinstanceableArgs3
    for sign in HINT_SIGNS_UNION:
        HINT_SIGN_TO_TYPEHINT[sign] = _TypeHintUnion


# Initialize this submodule.
_init()
