#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2024 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype Decidedly Object-Oriented Runtime-checking (DOOR) data** (i.e.,
global constants internally required throughout the :mod:`beartype.door`
subpackage).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.door._cls.doorsuper import TypeHint
from beartype.door._cls.doorsub import TypeHintGeneric
from beartype.door._cls.pep.doorpep484604 import UnionTypeHint
from beartype.door._cls.pep.doorpep586 import LiteralTypeHint
from beartype.door._cls.pep.doorpep593 import AnnotatedTypeHint
from beartype.door._cls.pep.pep484.doorpep484class import ClassTypeHint
from beartype.door._cls.pep.pep484.doorpep484newtype import NewTypeTypeHint
from beartype.door._cls.pep.pep484.doorpep484typevar import TypeVarTypeHint
from beartype.door._cls.pep.pep484585.doorpep484585callable import (
    CallableTypeHint)
from beartype.door._cls.pep.pep484585.doorpep484585tuple import (
    TupleFixedTypeHint,
    TupleVariableTypeHint,
)
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
    HintSignTupleFixed,
    HintSignTypeVar,
)
from beartype._util.hint.pep.utilpepget import (
    get_hint_pep_args,
    get_hint_pep_sign_or_none,
)
from beartype._util.hint.pep.utilpeptest import is_hint_pep_typing

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
    -------
    Type[TypeHint]
        Concrete subclass of the abstract :mod:`TypeHint` superclass handling
        this hint.

    Raises
    ------
    beartype.roar.BeartypeDoorNonpepException
        If this API does *not* currently support the passed hint.
    beartype.roar.BeartypeDecorHintPepSignException
        If the passed hint is *not* actually a PEP-compliant type hint.
    '''

    # ..................{ SUBCLASS                           }..................
    # Sign uniquely identifying this hint if any *OR* "None" otherwise (i.e., if
    # this hint is a PEP-noncompliant class).
    hint_sign = get_hint_pep_sign_or_none(hint)

    # Private concrete subclass of this ABC handling this hint if any *OR*
    # "None" otherwise (i.e., if no such subclass has been authored yet).
    wrapper_subclass = _HINT_SIGN_TO_TYPEHINT_CLS.get(hint_sign)  # type: ignore[arg-type]
    # print(f'hint: {repr(hint)}; sign: {repr(hint_sign)}; wrapper: {repr(wrapper_subclass)}')

    # If this hint appears to be currently unsupported...
    if wrapper_subclass is None:
        # If either...
        if (
            # This hint is a PEP-noncompliant isinstanceable class *OR*...
            isinstance(hint, type) or

            #FIXME: This condition is kinda intense. Should we really be
            #conflating typing attributes that aren't types with objects that
            #are types? Let's investigate exactly which kinds of type hints
            #require this and contemplate something considerably more elegant.
            # An unsupported kind of PEP-compliant type hint (e.g.,
            # "typing.TypedDict" instance)...
            is_hint_pep_typing(hint)
        # Return the concrete "TypeHint" subclass handling all such classes.
        ):
            wrapper_subclass = ClassTypeHint
            # print(f'[type fallback] hint: {repr(hint)}; sign: {repr(hint_sign)}; wrapper: {repr(wrapper_subclass)}')
        # Else, raise an exception.
        else:
            raise BeartypeDoorNonpepException(
                f'Type hint {repr(hint)} '
                f'currently unsupported by "beartype.door.TypeHint".'
            )
    # Else, this hint is supported.

    #FIXME: Alternately, it might be preferable to refactor this to resemble:
    #    if (
    #       not get_hint_pep_args(hint) and
    #       get_hint_pep_origin_type_or_none(hint) is not None
    #    ):
    #        wrapper_subclass = ClassTypeHint
    #
    #That's possibly simpler and cleaner, as it seamlessly conveys the exact
    #condition we're going for -- assuming it works, of course. *sigh*
    #FIXME: While sensible, the above approach induces non-trivial test
    #failures. Let's investigate this further at a later time, please.

    #FIXME: Push the "not" up to the top level of this conditional, please.
    # If this hint is unsubscripted a subscriptable type has no args, all we care about is the origin.
    elif (
        # Unsubscripted (i.e., indexed by *NO* child type hints) *AND*...
        not get_hint_pep_args(hint) and
        #FIXME: No idea, bro. This is pretty weird. For one,
        #"_HINT_SIGNS_ORIGINLESS" doesn't even contain all the signs it should
        #(e.g., "HintSignLiteral", "HintSignUnion"). For another we should just
        #be calling this instead:
        #    get_hint_pep_origin_type_or_none(hint) is not None
        hint_sign not in _HINT_SIGNS_ORIGINLESS
    ):
        wrapper_subclass = ClassTypeHint
    # In any case, this hint is supported by this concrete subclass.

    # Return this subclass.
    return wrapper_subclass

# ....................{ PRIVATE ~ globals                  }....................
# Further initialized below by the _init() function.
_HINT_SIGN_TO_TYPEHINT_CLS: Dict[HintSign, Type[TypeHint]] = {
    HintSignAnnotated:  AnnotatedTypeHint,
    HintSignCallable:   CallableTypeHint,
    HintSignGeneric:    TypeHintGeneric,
    HintSignLiteral:    LiteralTypeHint,
    HintSignNewType:    NewTypeTypeHint,
    HintSignTuple:      TupleVariableTypeHint,
    HintSignTupleFixed: TupleFixedTypeHint,
    HintSignTypeVar:    TypeVarTypeHint,
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
    from beartype.door._cls.doorsub import _TypeHintOriginIsinstanceable
    from beartype._data.hint.pep.sign.datapepsignmap import (
        HINT_SIGN_ORIGIN_ISINSTANCEABLE_TO_ARGS_LEN_RANGE)
    from beartype._data.hint.pep.sign.datapepsignset import HINT_SIGNS_UNION

    # Fully initialize the "_HINT_SIGN_TO_TYPEHINT_CLS" global dictionary.
    #
    # For each sign in the dictionary mapping from signs uniquely identifying
    # type hint factories originating from isinstanceable types to the fixed
    # number of child type hints subscripting those factories...
    for hint_sign in HINT_SIGN_ORIGIN_ISINSTANCEABLE_TO_ARGS_LEN_RANGE.keys():
        # If this sign has *NOT* already been mapped to an existing "TypeHint"
        # subclass, map this sign to the generic private
        # "_TypeHintOriginIsinstanceable" subclass.
        if hint_sign not in _HINT_SIGN_TO_TYPEHINT_CLS:
            _HINT_SIGN_TO_TYPEHINT_CLS[hint_sign] = (
                _TypeHintOriginIsinstanceable)
        # Else, this sign has already been mapped to an existing "TypeHint"
        # subclass. Preserve this mapping as is.

    # For each sign uniquely identifying a union, map this sign to the
    # union-specific "TypeHint" subclass.
    for hint_sign in HINT_SIGNS_UNION:
        _HINT_SIGN_TO_TYPEHINT_CLS[hint_sign] = UnionTypeHint

    # For each concrete "TypeHint" subclass registered with this dictionary
    # (*AFTER* initializing this dictionary)...
    for typehint_cls in _HINT_SIGN_TO_TYPEHINT_CLS.values():
        # If the unqualified basename of this subclass is prefixed by an
        # underscore, this subclass is private rather than public. In this case,
        # silently ignore this private subclass and continue to the next.
        if typehint_cls.__name__.startswith('_'):
            continue
        # Else, this subclass is public.

        # Sanitize the fully-qualified module name of this public subclass from
        # the private submodule declaring this subclass (e.g.,
        # "beartype.door._cls.pep.doorpep484604.UnionTypeHint") to the public
        # "beartype.door" subpackage to both improve the readability of
        # exceptions and discourage users from violating privacy encapsulation.
        typehint_cls.__module__ = 'beartype.door'

# ....................{ MAIN                               }....................
# Initialize this submodule.
_init()
