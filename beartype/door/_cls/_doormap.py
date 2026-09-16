#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype **Decidedly Object-Oriented Runtime-checking (DOOR) getters** (i.e.,
low-level callables introspecting metadata pertaining to high-level
:class:`beartype.door.TypeHint` wrappers).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.door._cls.doorabc import TypeHint
from beartype.door._cls.nonpep.doornonpepclass import ClassTypeHint
from beartype.door._cls.pep.doorpep484604 import UnionTypeHint
from beartype.door._cls.pep.doorpep586 import LiteralTypeHint
from beartype.door._cls.pep.doorpep593 import AnnotatedTypeHint
from beartype.door._cls.pep.pep484.doorpep484any import AnyTypeHint
from beartype.door._cls.pep.pep484.doorpep484newtype import NewTypeTypeHint
from beartype.door._cls.pep.pep484.doorpep484typevar import TypeVarTypeHint
from beartype.door._cls.doorunsubbed import (
    UnsubscriptedTypeHint)
from beartype.door._cls.pep.pep484585.doorpep484585callable import (
    CallableTypeHint)
from beartype.door._cls.pep.pep484585.doorpep484585generic import (
    GenericTypeHint)
from beartype.door._cls.doorsubbed import (
    SubscriptedTypeHint)
from beartype.door._cls.pep.pep484585.doorpep484585tuple import (
    TupleFixedTypeHint,
    TupleVariableTypeHint,
)
from beartype.roar import (
    BeartypeDoorNonpepException,
    BeartypeDoorPepUnsupportedException,
)
from beartype._data.typing.datatypingport import Hint
from beartype._data.hint.sign.datahintsigncls import HintSign
from beartype._data.hint.sign.datahintsigns import (
    HintSignAnnotated,
    HintSignAny,
    HintSignCallable,
    HintSignLiteral,
    HintSignNewType,
    HintSignPep484585GenericSubbed,
    HintSignPep484585GenericUnsubbed,
    HintSignTuple,
    HintSignPep484585TupleFixed,
    HintSignTypeVar,
    HintSignPep646TupleUnpacked,
    HintSignPep646TypeVarTupleUnpacked,
    HintSignTypeVarTuple,
    HintSignUnpack,
)
from beartype._util.hint.pep.utilpepget import get_hint_pep_childs
from beartype._util.hint.pep.utilpepsign import get_hint_pep_sign_or_none
from beartype._util.hint.pep.utilpeptest import is_hint_pep_typing

# ....................{ GETTERS                            }....................
def get_typehint_subclass(hint: Hint) -> type[TypeHint]:
    '''
    Concrete :class:`TypeHint` subclass handling the passed low-level unwrapped
    PEP-compliant type hint if any *or* raise an exception otherwise.

    Parameters
    ----------
    hint : Hint
        Low-level type hint to be inspected.

    Returns
    -------
    type[TypeHint]
        Concrete subclass of the abstract :mod:`TypeHint` superclass handling
        this hint.

    Raises
    ------
    beartype.roar.BeartypeDoorNonpepException
        If this API does *not* currently support the passed hint.
    beartype.roar.BeartypeDecorHintPepSignException
        If the passed hint is *not* actually a PEP-compliant type hint.
    '''

    # ..................{ LOCALS                             }..................
    # Sign uniquely identifying this hint if any *OR* "None" otherwise (i.e., if
    # this hint is either a valid PEP-noncompliant class, an invalid
    # PEP-noncompliant object *NEVER* likely to be supported by beartype, *OR* a
    # valid PEP-compliant hint currently unsupported by beartype).
    hint_sign = get_hint_pep_sign_or_none(hint)

    # ..................{ UNSUPPORTED                        }..................
    # If this hint is *NOT* a standalone type hint, raise an exception. Some
    # PEP 646-compliant objects are merely *MODIFIERS* of the child hints
    # subscripting a parent hint rather than hints in their own right (e.g., the
    # "*tuple[int]" and "typing.Unpack[tuple[int]]" child hints subscripting the
    # parent hint "tuple[*tuple[int]]"). Such objects convey *NO* meaning in
    # isolation and are thus unwrappable.
    #
    # Note that this test is intentionally performed *BEFORE* the fallbacks
    # below. Why? Because "typing.Unpack[...]" is published by the standard
    # "typing" submodule and would thus otherwise be silently misidentified by
    # the "is_hint_pep_typing()" fallback below as an unsubscripted hint,
    # despite conveying nothing. Worse, the equivalent "*tuple[int]" spelling of
    # that same hint is *NOT* published by that submodule and would thus
    # otherwise raise, rendering these two spellings of one object inconsistent.
    if hint_sign in HINT_SIGNS_UNWRAPPABLE:
        raise BeartypeDoorPepUnsupportedException(
            f'Type hint {repr(hint)} unwrappable by '
            f'"beartype.door.TypeHint", as this hint only modifies the child '
            f'hints subscripting a parent hint rather than conveying meaning '
            f'in its own right. Consider wrapping the parent hint '
            f'subscripted by this hint instead: e.g.,\n'
            f'    # Instead of wrapping an unpacked child hint...\n'
            f'    TypeHint(*tuple[int])\n'
            f'\n'
            f'    # Prefer wrapping the parent tuple hint.\n'
            f'    TypeHint(tuple[*tuple[int]])'
        )
    # Else, this hint is a standalone type hint.

    # ..................{ SUBCLASS                           }..................
    # Concrete "TypeHint" subclass to be returned.
    wrapper_subclass: type[TypeHint] = None  # type: ignore[assignment]

    # If this hint is uniquely identified by a sign...
    if hint_sign is not None:
        #FIXME: [SPEED] As a negligible optimization, globalize the
        #_HINT_SIGN_TO_TYPEHINT_SUBTYPE.get() method to avoid repeated lookups here.

        # Concrete "TypeHint" subclass superficially handling *ALL* hints
        # identified by this sign if any *OR* "None" otherwise (i.e., if *NO*
        # such subclass has been authored yet).
        wrapper_subclass = _HINT_SIGN_TO_TYPEHINT_SUBTYPE.get(hint_sign)  # type: ignore[assignment]
        # print(f'Mapping hint {hint} sign {hint_sign} to subclass {wrapper_subclass}...')

        # If...
        if (
            # This hint is superficially handled by a "catch-all" subscripted
            # "TypeHint" subclass despite possibly being unsubscripted *AND*...
            wrapper_subclass in TYPEHINT_SUBTYPES_SUBSCRIPTED_CATCHALL and
            # This hint is unsubscripted...
            not get_hint_pep_childs(hint)
        ):
            # print('Here!')
            # This hint is more accurately handled by the catch-all
            # "UnsubscriptedTypeHint" subclass, which handles *ALL*
            # unsubscripted hints *NOT* handled by some finer-grained subclass.
            wrapper_subclass = UnsubscriptedTypeHint

    # If *NO* "TypeHint" subclass handling this hint has been authored yet...
    if wrapper_subclass is None:
        # If this hint is a type, prefer the concrete "TypeHint" subclass
        # handling all such types.
        if isinstance(hint, type):
            wrapper_subclass = ClassTypeHint
        # Else, this hint is *NOT* a type.
        #
        # If this hint is *NOT* published by the standard "typing" submodule,
        # this hint is *NOT* guaranteed to be a PEP-compliant hint currently
        # unsupported by beartype (e.g., "typing.TypedDict" instance). Since
        # this implies this hint to be a PEP-noncompliant object authored by
        # some third-party package unlikely to ever be supported by a concrete
        # "TypeHint" subclass implemented by us, raise an exception.
        elif not is_hint_pep_typing(hint):
            raise BeartypeDoorNonpepException(
                f'Type hint {repr(hint)} '
                f'currently unsupported by "beartype.door.TypeHint".'
            )
        # Else, this hint is published by the standard "typing" submodule and
        # thus guaranteed to be a PEP-compliant hint merely currently
        # unsupported by beartype (e.g., "typing.TypedDict" instance). In this
        # case, prefer the concrete "TypeHint" subclass handling all such hints.
        else:
            wrapper_subclass = UnsubscriptedTypeHint
        # print(f'[type fallback] hint: {repr(hint)}; sign: {repr(hint_sign)}; wrapper: {repr(wrapper_subclass)}')

    # ..................{ RETURN                             }..................
    # Return this subclass.
    # print(f'Mapped hint {hint} sign {hint_sign} to subclass {wrapper_subclass}!')
    return wrapper_subclass

# ....................{ PRIVATE ~ globals                  }....................
# Further initialized below by the _init() function.
_HINT_SIGN_TO_TYPEHINT_SUBTYPE: dict[HintSign, type[TypeHint]] = {
    HintSignAnnotated:                AnnotatedTypeHint,
    HintSignAny:                      AnyTypeHint,
    HintSignCallable:                 CallableTypeHint,
    HintSignLiteral:                  LiteralTypeHint,
    HintSignNewType:                  NewTypeTypeHint,
    HintSignTuple:                    TupleVariableTypeHint,
    HintSignPep484585TupleFixed:      TupleFixedTypeHint,
    HintSignTypeVar:                  TypeVarTypeHint,
    HintSignPep484585GenericSubbed:   GenericTypeHint,
    HintSignPep484585GenericUnsubbed: GenericTypeHint,
}
'''
Dictionary mapping from each sign uniquely identifying PEP-compliant type hints
to the :class:`.TypeHint` subclass handling those hints.
'''


HINT_SIGNS_UNWRAPPABLE = frozenset((
    # Ambiguously identifies unpacked child hints (e.g., the "typing.Unpack[Ts]"
    # child hint subscripting the parent hint "tuple[typing.Unpack[Ts]]").
    HintSignUnpack,

    # Uniquely identifies unpacked child tuple hints (e.g., the "*tuple[int]"
    # child hint subscripting the parent hint "tuple[*tuple[int]]").
    HintSignPep646TupleUnpacked,

    # Uniquely identifies unpacked type variable tuples (e.g., the "*Ts" child
    # hint subscripting the parent hint "tuple[int, *Ts]").
    HintSignPep646TypeVarTupleUnpacked,

    # Uniquely identifies type variable tuples (e.g., "Ts"). Unlike a type
    # variable, which is a valid hint annotating a parameter or return (e.g.,
    # "def f(x: T) -> T"), a type variable tuple is *ONLY* valid unpacked in a
    # parent hint (e.g., "def f(*args: *Ts)").
    HintSignTypeVarTuple,
))
'''
Frozen set of all **unwrappable signs** (i.e., signs uniquely identifying
objects that modify the child hints subscripting a parent hint rather than
conveying meaning in their own right and are thus unwrappable by the
:class:`beartype.door.TypeHint` superclass).
'''


TYPEHINT_SUBTYPES_SUBSCRIPTED_CATCHALL = frozenset((
    SubscriptedTypeHint,
    TupleVariableTypeHint,
))
'''
Frozen set of all **catch-all subscripted type hint subclasses** (i.e., concrete
:class:`.TypeHint` subclasses superficially assigned by the
:data:`._HINT_SIGN_TO_TYPEHINT_SUBTYPE` dictionary to *all* hints uniquely
identified by various signs, regardless of whether those hints are actually
subscripted or not).
'''

# ....................{ PRIVATE ~ initializers             }....................
def _init() -> None:
    '''
    Initialize this submodule.
    '''

    # ....................{ IMPORTS                        }....................
    # Isolate function-specific imports.
    from beartype._data.hint.sign.datahintsignmap import (
        HINT_SIGN_ORIGIN_ISINSTANCEABLE_TO_ARGS_LEN_RANGE)
    from beartype._data.hint.sign.datahintsignset import HINT_SIGNS_UNION

    # ....................{ INITIALIZE                     }....................
    # Fully initialize the "_HINT_SIGN_TO_TYPEHINT_SUBTYPE" global dictionary.
    #
    # For each sign in the dictionary mapping from signs uniquely identifying
    # type hint factories originating from isinstanceable types to the fixed
    # number of child type hints subscripting those factories...
    for hint_sign in HINT_SIGN_ORIGIN_ISINSTANCEABLE_TO_ARGS_LEN_RANGE.keys():
        # If this sign has *NOT* already been mapped to an existing "TypeHint"
        # subclass, map this sign to the catch-all "SubscriptedTypeHint"
        # subclass.
        if hint_sign not in _HINT_SIGN_TO_TYPEHINT_SUBTYPE:
            _HINT_SIGN_TO_TYPEHINT_SUBTYPE[hint_sign] = SubscriptedTypeHint
        # Else, this sign has already been mapped to an existing "TypeHint"
        # subclass. Preserve this mapping as is.

    # For each sign uniquely identifying a union, map this sign to the
    # union-specific "TypeHint" subclass.
    for hint_sign in HINT_SIGNS_UNION:
        _HINT_SIGN_TO_TYPEHINT_SUBTYPE[hint_sign] = UnionTypeHint

    # ....................{ MONKEY-PATCH                   }....................
    # Logic intentionally performed last *AFTER* initializing this dictionary
    # above. This logic typically monkey-patches items of this dictionary, yo!

    # For each concrete "TypeHint" subclass registered with this dictionary...
    for typehint_cls in _HINT_SIGN_TO_TYPEHINT_SUBTYPE.values():
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
