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
    _TypeHintOriginIsinstanceableArgs1,
    _TypeHintOriginIsinstanceableArgs2,
    _TypeHintOriginIsinstanceableArgs3,
    _TypeHintSubscripted,
)
from beartype.door._proposal.pep484.doorpep484class import (
    ClassTypeHint)
from beartype.door._proposal.doorpep484604 import UnionTypeHint
from beartype.door._proposal.doorpep586 import LiteralTypeHint
from beartype.door._proposal.doorpep593 import AnnotatedTypeHint
from beartype.door._proposal.pep484.doorpep484newtype import NewTypeTypeHint
from beartype.door._proposal.pep484.doorpep484typevar import TypeVarTypeHint
from beartype.door._proposal.pep484585.doorpep484585callable import (
    CallableTypeHint)
from beartype.door._proposal.pep484585.doorpep484585tuple import (
    _TupleTypeHint)
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

    # ..................{ SUBCLASS                           }..................
    # Sign uniquely identifying this hint if any *OR* return None (i.e., if this
    # hint is *NOT* actually a PEP-compliant type hint).
    hint_sign = get_hint_pep_sign_or_none(hint)

    # Private concrete subclass of this ABC handling this hint if any *OR*
    # "None" otherwise (i.e., if no such subclass has been authored yet).
    typehint_subclass = _HINT_SIGN_TO_TYPEHINT_CLS.get(hint_sign)

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
            typehint_subclass = ClassTypeHint
        else:
            raise BeartypeDoorNonpepException(
                f'Type hint {repr(hint)} invalid '
                f'(i.e., either PEP-noncompliant or '
                f'PEP-compliant but currently unsupported).'
            )
    # Else, this hint is supported.

    #FIXME: Alternately, it might be preferable to refactor this to resemble:
    #    if (
    #       not get_hint_pep_args(hint) and
    #       get_hint_pep_origin_or_none(hint) is None
    #    ):
    #        typehint_subclass = ClassTypeHint
    #
    #That's possibly simpler and cleaner, as it seamlessly conveys the exact
    #condition we're going for -- assuming it works, of course. *sigh*

    # If a subscriptable type has no args, all we care about is the origin.
    elif (
        not get_hint_pep_args(hint) and
        hint_sign not in _HINT_SIGNS_ORIGINLESS
    ):
        typehint_subclass = ClassTypeHint
    # In any case, this hint is supported by this concrete subclass.

    # Return this subclass.
    return typehint_subclass

# ....................{ PRIVATE ~ globals                  }....................
# Further initialized below by the _init() function.
_HINT_SIGN_TO_TYPEHINT_CLS: Dict[HintSign, Type[TypeHint]] = {
    HintSignAnnotated: AnnotatedTypeHint,
    HintSignCallable:  CallableTypeHint,
    HintSignGeneric:   _TypeHintSubscripted,
    HintSignLiteral:   LiteralTypeHint,
    HintSignNewType:   NewTypeTypeHint,
    HintSignTuple:     _TupleTypeHint,
    HintSignTypeVar:   TypeVarTypeHint,
}
'''
Dictionary mapping from each sign uniquely identifying PEP-compliant type hints
to the :class:`TypeHint` subclass handling those hints.
'''


#FIXME: Consider shifting into "datapepsignset" if still required.
_HINT_SIGNS_ORIGINLESS = frozenset((
    HintSignNewType,
    HintSignTypeVar,
))
'''
Frozen set of all **origin-less signs.**
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
        _HINT_SIGN_TO_TYPEHINT_CLS[sign] = _TypeHintOriginIsinstanceableArgs1
    for sign in HINT_SIGNS_ORIGIN_ISINSTANCEABLE_ARGS_2:
        _HINT_SIGN_TO_TYPEHINT_CLS[sign] = _TypeHintOriginIsinstanceableArgs2
    for sign in HINT_SIGNS_ORIGIN_ISINSTANCEABLE_ARGS_3:
        _HINT_SIGN_TO_TYPEHINT_CLS[sign] = _TypeHintOriginIsinstanceableArgs3
    for sign in HINT_SIGNS_UNION:
        _HINT_SIGN_TO_TYPEHINT_CLS[sign] = UnionTypeHint

    # For each concrete "TypeHint" subclass registered with this dictionary
    # (*AFTER* initializing this dictionary)...
    for typehint_cls in _HINT_SIGN_TO_TYPEHINT_CLS.values():
        # If the unqualified basename of this subclass is prefixed by an
        # underscare, this subclass is private rather than public. In this case,
        # silently ignore this private subclass and continue to the next.
        if typehint_cls.__name__.startswith('_'):
            continue
        # Else, this subclass is public.

        # Sanitize the fully-qualified module name of this public subclass from
        # the private submodule declaring this subclass (e.g.,
        # "beartype.door._proposal.doorpep484604.UnionTypeHintbeartype") to the
        # public "beartype.door" subpackage to both improve the readability of
        # exception messages and discourage end users from accessing that
        # private submodule.
        typehint_cls.__class__.__module__ = 'beartype.door'


# Initialize this submodule.
_init()
