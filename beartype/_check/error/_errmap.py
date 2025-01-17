#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
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
from beartype._check.error.errcause import ViolationCause

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
        HintSignLiteral,
        HintSignNoReturn,
        HintSignPep484585GenericUnsubscripted,
        HintSignTupleFixed,
        HintSignType,
    )
    from beartype._data.hint.pep.sign.datapepsignset import (
        HINT_SIGNS_MAPPING,
        HINT_SIGNS_ORIGIN_ISINSTANCEABLE,
        HINT_SIGNS_CONTAINER_ARGS_1,
        HINT_SIGNS_UNION,
    )
    from beartype._check.error._errtype import (
        find_cause_instance_type_forwardref,
        find_cause_subclass_type,
        find_cause_type_instance_origin,
    )
    from beartype._check.error._pep.errpep484604 import (
        find_cause_pep484604_union)
    from beartype._check.error._pep.errpep586 import find_cause_pep586_literal
    from beartype._check.error._pep.errpep593 import find_cause_pep593_annotated
    from beartype._check.error._pep.pep484.errpep484noreturn import (
        find_cause_pep484_noreturn)
    from beartype._check.error._pep.pep484585.errpep484585container import (
        find_cause_container_args_1,
        find_cause_tuple_fixed,
    )
    from beartype._check.error._pep.pep484585.errpep484585generic import (
        find_cause_generic_unsubscripted)
    from beartype._check.error._pep.pep484585.errpep484585mapping import (
        find_cause_mapping)

    # Map each originative sign to the appropriate finder *BEFORE* any other
    # mappings. This is merely a generalized fallback subsequently replaced by
    # sign-specific finders below.
    for hint_sign in HINT_SIGNS_ORIGIN_ISINSTANCEABLE:
        HINT_SIGN_TO_GET_CAUSE_FUNC[hint_sign] = find_cause_type_instance_origin

    # Map each 1-argument container sign to its corresponding finder.
    for hint_sign in HINT_SIGNS_CONTAINER_ARGS_1:
        HINT_SIGN_TO_GET_CAUSE_FUNC[hint_sign] = find_cause_container_args_1

    # Map each 2-argument mapping sign to its corresponding finder.
    for hint_sign in HINT_SIGNS_MAPPING:
        HINT_SIGN_TO_GET_CAUSE_FUNC[hint_sign] = find_cause_mapping

    # Map each union-specific sign to its corresponding finder.
    for hint_sign in HINT_SIGNS_UNION:
        HINT_SIGN_TO_GET_CAUSE_FUNC[hint_sign] = find_cause_pep484604_union

    # Map each sign validated by a unique finder to that finder *AFTER* all
    # other mappings. These sign-specific finders are intended to replace all
    # other automated mappings above.
    HINT_SIGN_TO_GET_CAUSE_FUNC.update({
        HintSignAnnotated: find_cause_pep593_annotated,
        HintSignForwardRef: find_cause_instance_type_forwardref,
        HintSignPep484585GenericUnsubscripted: find_cause_generic_unsubscripted,
        HintSignLiteral: find_cause_pep586_literal,
        HintSignNoReturn: find_cause_pep484_noreturn,
        HintSignTupleFixed: find_cause_tuple_fixed,
        HintSignType: find_cause_subclass_type,
    })


# Initialize this submodule.
_init()
