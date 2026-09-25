#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **type parameter representation utilities** (i.e., low-level
factories generically synthesizing unique machine-readable representations for
:pep:`484`-compliant type variables, pep:`612`-compliant parameter
specifications, and :pep:`646`-compliant type variable tuples).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.roar import (
    BeartypeDecorHintPep484612646Exception,
    # BeartypeException,
)
# from beartype._data.kind.datakindmap import FROZENDICT_EMPTY
from beartype._data.typing.datatyping import (
    Pep484612646TypeArgUnpacked,
    TypeException,
)
from beartype._util.cache.func.utilcachefunc import callable_cached
from beartype._util.hint.pep.proposal.typearg.peptypeargmain import (
    get_hint_typearg_packed_name,
    pack_hint_typearg_unpacked,
)
from beartype._util.kind.maplike.utilmapfrozen import FrozenDict
from beartype._util.text.utiltextidentifier import is_dunder
from beartype._util.utilobjattr import get_object_attr_name_to_value
from beartype._util.utilobjget import get_object_type_basename

# ....................{ FACTORIES                          }....................
@callable_cached
def make_hint_typearg_unpacked_repr(
    # Mandatory parameters.
    hint: Pep484612646TypeArgUnpacked,

    # Optional parameters.
    exception_cls: TypeException = BeartypeDecorHintPep484612646Exception,
    exception_prefix: str = '',
) -> str:
    '''
    **Unique machine-readable representation** of the passed **unpacked type
    parameter** (i.e., :pep:`484`-compliant type variable, pep:`612`-compliant
    unpacked parameter specification, or :pep:`646`-compliant unpacked type
    variable tuples).

    This factory synthesizes the equivalent of a sane :func:`repr` string for
    this unpacked type parameter. Unfortunately, the :func:`repr` builtin
    returns non-unique and thus insane strings for unpacked type parameters:
    e.g.,

    .. code-block:: pycon

       >>> from typing import TypeVar
       >>> repr(TypeVar('T'))
       'T'  # <-- makes sense
       >>> repr(TypeVar('T', bound=int))
       'T'  # <-- *MAKES NO SENSE WTTTTTTTTTTF PYTHON*

    This factory is memoized for efficiency.

    Caveats
    -------
    **This high-level factory should be called in lieu of the low-level**
    :func:`repr` **builtin to ensure uniqueness.** Although unique of
    :func:`repr` strings is a non-issue for cosmetic purposes (e.g., producing
    human-readable exception or warning messages), many other purposes (e.g.,
    machine-readable caching keys) assume uniqueness as a hard prerequisite.

    Parameters
    ----------
    hint : Pep484612646TypeArgPacked
        Unpacked type parameter to be inspected.
    exception_cls : Type[Exception], default: BeartypeDecorHintPep484612646Exception
        Type of exception to be raised in the event of a fatal error. Defaults
        to :exc:`.BeartypeDecorHintForwardRefException`.
    exception_prefix : str, default: ''
        Human-readable substring prefixing raised exception messages. Defaults
        to the empty string.

    Returns
    -------
    str
        Unique machine-readable representation of this unpacked type parameter.
    '''

    # Packed type parameter underlying this an unpacked type parameter.
    hint = pack_hint_typearg_unpacked(  # type: ignore[assignment]
        hint=hint,  # pyright: ignore
        exception_cls=exception_cls,
        exception_prefix=exception_prefix,
    )

    # Unqualified basename of the type of this packed type parameter (e.g.,
    # "TypeVar").
    hint_type_basename = get_object_type_basename(hint)

    # Unqualified basename of this packed type parameter (e.g., "T").
    hint_name = get_hint_typearg_packed_name(hint)  # type: ignore[arg-type]

    # Frozen dictionary mapping from the name to value of each field (i.e.,
    # meaningful instance variable) of the this packed type parameter.
    hint_field_name_to_value = (
        _get_hint_typearg_packed_field_name_to_value(hint))

    # Unique machine-readable representation to be iteratively constructed below
    # and then returned, initialized to a class instantiation-style repr().
    hint_repr = f'{hint_type_basename}({repr(hint_name)}'

    # For the unqualified basename and value of each field of this packed type
    # parameter...
    for hint_field_name, hint_field_value in hint_field_name_to_value.items():
        # Append a comma-delimited repr() of this field.
        #
        # Note that the first and last two characters of this field name are
        # guaranteed by the implementation of the
        # _get_hint_typearg_packed_field_name_to_value() getter to
        # be the ignorable dunder attribute character "_", which we slice off.
        hint_repr += f', {hint_field_name[2:-2]}={repr(hint_field_value)}'

    # Finalize this repr() with a trailing parens.
    hint_repr += ')'

    # Return this repr(), yo! Return it for Johnny.
    return hint_repr

# ....................{ PRIVATE ~ constants                }....................
_HINT_PEP484612646_TYPEARG_UNPACKED_ATTR_NAMES_NONFIELD = frozenset((
    # Type parameter instance variables already hard-coded for readability by
    # the make_hint_typearg_unpacked_repr() factory into the
    # strings created and returned by that factory are effectively meaningless.
    # These include:
    # * The type parameter class.
    # * The type parameter name.
    '__class__',
    '__name__',

    # Type parameters inherit meaningless docstrings from their types.
    '__doc__',
))
'''
Frozen set of the names of all **unpacked type parameter non-fields** (i.e.,
meaningless instance variables of unpacked type parameters).
'''

# ....................{ PRIVATE ~ testers                  }....................
def _is_hint_typearg_packed_field(
    attr_name: str, attr_value: object) -> bool:
    '''
    Predicate suitable for passing as the ``predicate`` parameter to the
    :func:`._get_hint_typearg_packed_field_name_to_value` getter,
    returning :data:`True` only if the passed attribute value constitutes an
    **unpacked type parameter field** (i.e., meaningful instance variable of an
    unpacked type parameter).
    '''

    # Return true only if...
    #
    # Note that tests are intentionally ordered in descending order of
    # efficiency (i.e., from fastest to slowest tests).
    return (
        # This attribute name is *NOT* that of an unpacked type parameter
        # non-field (and is thus that of a field) *AND*...
        attr_name not in (
            _HINT_PEP484612646_TYPEARG_UNPACKED_ATTR_NAMES_NONFIELD) and
        # This attribute value is uncallable (and is thus an instance variable)
        # *AND*...
        not callable(attr_value) and
        # This attribute name is a dunder attribute (i.e., both prefixed and
        # suffixed by "__"), implying this instance variable to be PEP-compliant
        # and thus almost certainly meaningful. For example, this heuristic
        # trivially ignores:
        # * PEP 649-compliant deferred child hint evaluation functions (e.g.,
        #   evaluate_bound()), which are otherwise non-trivial to detect due to
        #   their values being either:
        #   * If the corresponding non-deferred property (e.g., "bound")
        #     references one or more unquoted forward references, a callable.
        #   * Else, "None".
        is_dunder(attr_name)
    )

# ....................{ PRIVATE ~ getters                  }....................
#FIXME: Improve docstring, please. *shrug*
#FIXME: Unit test us up, please. *shrug*
def _get_hint_typearg_packed_field_name_to_value(
    hint) -> FrozenDict[str, object]:
    '''
    Frozen dictionary mapping from the name to value of each **field** (i.e.,
    meaningful instance variable) of the passed packed type parameter.

    This getter is intentionally *not* memoized (e.g., by the
    ``@callable_cached`` decorator), as the only public function calling this
    getter is memoized.
    '''

    #FIXME: Actually, let's just passively let *ALL* exceptions unwind the call
    #stack for the moment. Testing this is a bit of a nightmare. Without
    #testing, the only safe assumption is that the caller deserves to know.
    # # Attempt to...
    # try:

    # Dynamically introspect this dictionary from this type parameter.
    hint_field_name_to_value = get_object_attr_name_to_value(
        hint,
        # Retrieve only the proper subset of type parameter attributes that
        # are actually meaningful fields.
        predicate=_is_hint_typearg_packed_field,
        # Retrieve type parameter attributes unsafely. Doing so permits this
        # getter to raise unexpected exceptions in the event that type
        # parameter properties raise exceptions (which is bad) but also
        # permits this getter to return the values of those properties when
        # they do *NOT* raise exceptions (which is a mandatory requirement
        # of this getter and thus good). Mandatory >>>>>>> bad.
        is_safe=False,
    )

    # Coerce this mutable dictionary into a frozen dictionary.
    hint_field_name_to_value = FrozenDict(hint_field_name_to_value)

    #FIXME: Preserved in the likelihood we'll want to resurrect this later...
    # # If doing so raises a beartype-specific exception, permit that exception to
    # # explosively unwind the call stack. We trust beartype to know what it's
    # # doing. Do you? Let none answer that landmine-laden question.
    # except BeartypeException:
    #     raise
    # # If doing so raises *ANY* other exception (e.g., due to a type parameter
    # # property raising an unexpected exception, which typically occurs when a
    # # PEP 649- and 749-compliant type parameter field was defined to be an
    # # unquoted forward reference to an unresolvable type hint)...
    # except Exception as exception:
    #     #FIXME: Coerce this fatal exception into a non-fatal warning. It's
    #     #better than nuthin'. *shrug*
    #     # Return the empty frozen dictionary. Yeah. We know. We also shrug.
    #     hint_field_name_to_value = FROZENDICT_EMPTY

    # Return this frozen dictionary.
    return hint_field_name_to_value
