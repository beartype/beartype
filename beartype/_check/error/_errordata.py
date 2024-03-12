#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2024 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype exception data** (i.e., high-level globals and constants leveraged
throughout the :mod:`beartype._check.error` subpackage).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.typing import (
    Callable,
    Dict,
)
from beartype._data.hint.pep.sign.datapepsigncls import HintSign
from beartype._check.error._errorcause import ViolationCause

# ....................{ GLOBALS                            }....................
# Initialized with automated inspection below in the _init() function.
HINT_SIGN_TO_GET_CAUSE_FUNC: Dict[
    HintSign, Callable[[ViolationCause], ViolationCause]] = {}
'''
Dictionary mapping each **sign** (i.e., arbitrary object uniquely identifying a
category of type hints) to a private getter function defined by this submodule
whose signature matches that of the :func:`._find_cause` function and
which is dynamically dispatched by that function to describe type-checking
failures specific to that unsubscripted :mod:`typing` attribute.
'''

# ....................{ PRIVATE ~ initializers             }....................
def _init() -> None:
    '''
    Initialize this submodule.
    '''

    # Defer heavyweight imports.
    from beartype._data.hint.pep.sign.datapepsigns import (
        HintSignAnnotated,
        HintSignForwardRef,
        HintSignGeneric,
        HintSignLiteral,
        HintSignNoReturn,
        HintSignTuple,
        HintSignType,
    )
    from beartype._data.hint.pep.sign.datapepsignset import (
        HINT_SIGNS_MAPPING,
        HINT_SIGNS_ORIGIN_ISINSTANCEABLE,
        HINT_SIGNS_SEQUENCE_ARGS_1,
        HINT_SIGNS_UNION,
    )
    from beartype._check.error._errortype import (
        find_cause_instance_type_forwardref,
        find_cause_subclass_type,
        find_cause_type_instance_origin,
    )
    from beartype._check.error._pep.errorpep484604union import (
        find_cause_union)
    from beartype._check.error._pep.errorpep586 import (
        find_cause_literal)
    from beartype._check.error._pep.errorpep593 import (
        find_cause_annotated)
    from beartype._check.error._pep.pep484.errornoreturn import (
        find_cause_noreturn)
    from beartype._check.error._pep.pep484585.errorgeneric import (
        find_cause_generic)
    from beartype._check.error._pep.pep484585.errormapping import (
        find_cause_mapping)
    from beartype._check.error._pep.pep484585.errorsequence import (
        find_cause_sequence_args_1,
        find_cause_tuple,
    )

    # Map each originative sign to the appropriate getter *BEFORE* any other
    # mappings. This is merely a generalized fallback subsequently replaced by
    # sign-specific getters below.
    for pep_sign_origin_isinstanceable in HINT_SIGNS_ORIGIN_ISINSTANCEABLE:
        HINT_SIGN_TO_GET_CAUSE_FUNC[pep_sign_origin_isinstanceable] = (
            find_cause_type_instance_origin)

    # Map each mapping sign to its corresponding getter.
    for pep_sign_mapping in HINT_SIGNS_MAPPING:
        HINT_SIGN_TO_GET_CAUSE_FUNC[pep_sign_mapping] = find_cause_mapping

    # Map each 1-argument sequence sign to its corresponding getter.
    for pep_sign_sequence_args_1 in HINT_SIGNS_SEQUENCE_ARGS_1:
        HINT_SIGN_TO_GET_CAUSE_FUNC[pep_sign_sequence_args_1] = (
            find_cause_sequence_args_1)

    # Map each union-specific sign to its corresponding getter.
    for pep_sign_type_union in HINT_SIGNS_UNION:
        HINT_SIGN_TO_GET_CAUSE_FUNC[pep_sign_type_union] = find_cause_union

    # Map each sign validated by a unique getter to that getter *AFTER* all
    # other mappings. These sign-specific getters are intended to replace all
    # other automated mappings above.
    HINT_SIGN_TO_GET_CAUSE_FUNC.update({
        HintSignAnnotated: find_cause_annotated,
        HintSignForwardRef: find_cause_instance_type_forwardref,
        HintSignGeneric: find_cause_generic,
        HintSignLiteral: find_cause_literal,
        HintSignNoReturn: find_cause_noreturn,
        HintSignTuple: find_cause_tuple,
        HintSignType: find_cause_subclass_type,
    })


# Initialize this submodule.
_init()
