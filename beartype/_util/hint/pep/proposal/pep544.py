#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`544`-compliant type hint utilities.

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype._data.api.standard.datatyping import TYPING_MODULE_NAMES
from beartype._data.cls.datacls import TYPES_PEP484_GENERIC_IO
from beartype._data.typing.datatypingport import (
    Hint,
    TypeIs,
)
from beartype._util.cls.utilclstest import is_type_builtin_or_fake
from typing import (
    Protocol as typing_Protocol,  # <------ unoptimized protocol: *BLAGH*
)

# ....................{ TESTERS                            }....................
#FIXME: We'd strongly prefer to annotate this as returning
#"TypeIs[typing_Protocol]" rather than "TypeIs[type]". The former is
#considerably more fine-grained and thus broadly useful than the latter. Sadly,
#both "mypy" and "pyright" complain about this. Both are wrong, of course:
#    beartype/_util/hint/pep/proposal/pep544.py:43: error: Variable
#    "typing.Protocol" is not valid as a type  [valid-type]
#
#Nonsense! "typing.Protocol" is *LITERALLY* a type. It's a type, guys. Like most
#types, it's both a type hint *AND* a type. That's fine. Oh, well.
def is_hint_pep484_generic_io(hint: Hint) -> TypeIs[type]:
    '''
    :data:`True` only if the passed object is a functionally useless
    :pep:`484`-compliant :mod:`typing` **IO generic superclass** (i.e., either
    :class:`typing.IO` itself *or* a subclass of :class:`typing.IO` defined by
    the :mod:`typing` module effectively unusable at runtime due to botched
    implementation details) that is losslessly replaceable with a useful
    :pep:`544`-compliant :mod:`beartype` **IO protocol** (i.e., either
    :class:`.IO` itself *or* a subclass of that class defined by this
    submodule intentionally designed to be usable at runtime).

    This tester is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator), as the implementation trivially reduces
    to an efficient one-liner.

    Parameters
    ----------
    hint : object
        Object to be inspected.

    Returns
    -------
    bool
        :data:`True` only if this object is a :pep:`484`-compliant IO generic
        base class.

    See Also
    --------
    :class:`IO`
        Further commentary.
    '''

    # Avoid circular import dependencies.
    from beartype._util.hint.pep.utilpepget import (
        get_hint_pep_origin_type_or_none)

    # Type originating this hint, defined as either:
    # * If this hint defines the "__origin__" dunder attribute...
    #   * Whose value is a type, that type (which is then said to "originate"
    #     this hint).
    #   * Whose value is *NOT* a type but this hint is a type, this hint itself
    #     (which is then said to "originate" itself).
    # * In all other cases, "None".
    hint_origin = get_hint_pep_origin_type_or_none(
        hint=hint, is_self_fallback=True)

    # Return true only if this originating type is either:
    # * An unsubscripted PEP 484-compliant IO generic base class
    #   (e.g., "typing.IO") *OR*....
    # * A subscripted PEP 484-compliant IO generic base class
    #   (e.g., "typing.IO[str]").
    return hint_origin in TYPES_PEP484_GENERIC_IO


#FIXME: We'd strongly prefer to annotate this as returning
#"TypeIs[typing_Protocol]" rather than "TypeIs[type]". See above for commentary.
def is_hint_pep544_protocol(hint: Hint) -> TypeIs[type]:
    '''
    :data:`True` only if the passed object is a :pep:`544`-compliant
    **protocol** (i.e., subclass of the :class:`typing.Protocol` superclass).

    This tester is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator), as the implementation trivially reduces
    to an efficient one-liner.

    Parameters
    ----------
    hint : object
        Object to be inspected.

    Returns
    -------
    bool
        :data:`True` only if this object is a :pep:`544`-compliant protocol.
    '''

    # Return true only if this hint is...
    return (
        # A type *AND*...
        isinstance(hint, type) and
        # A PEP 544-compliant protocol *AND*...
        issubclass(hint, typing_Protocol) and  # type: ignore[arg-type]
        # *NOT* a builtin type. For unknown reasons, some but *NOT* all
        # builtin types erroneously present themselves to be PEP
        # 544-compliant protocols under Python >= 3.8: e.g.,
        #     >>> from typing import Protocol
        #     >>> issubclass(str, Protocol)
        #     False        # <--- this makes sense
        #     >>> issubclass(int, Protocol)
        #     True         # <--- this makes no sense whatsoever
        #
        # Since builtin types are obviously *NOT* PEP 544-compliant
        # protocols, explicitly exclude all such types. Why, Guido? Why?
        #
        # Do *NOT* ignore fake builtins for the purposes of this test. Why?
        # Because even fake builtins (e.g., "type(None)") erroneously
        # masquerade as PEP 544-compliant protocols! :o
        not is_type_builtin_or_fake(hint)  # pyright: ignore
    )


#FIXME: Unit test us up, please.
def is_hint_pep544_protocol_supertype(hint: Hint) -> TypeIs[type]:
    '''
    :data:`True` only if the passed object is a :pep:`544`-compliant
    **protocol superclass** (i.e., either the :class:`typing.Protocol`,
    :class:`typing_extensions.Protocol`, or :class:`beartype.typing.Protocol`
    superclass).

    This tester is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator), as the implementation trivially reduces
    to an efficient one-liner.

    Parameters
    ----------
    hint : object
        Object to be inspected.

    Returns
    -------
    bool
        :data:`True` only if this object is a :pep:`544`-compliant protocol
        superclass.
    '''

    # Return true only if...
    return (
        # This object is a type *AND*...
        isinstance(hint, type) and
        # The unqualified basename of this type is that of *ALL* protocol
        # superclasses *AND*...
        hint.__name__ == 'Protocol' and
        # A typing-like module declares this type.
        hint.__module__ in TYPING_MODULE_NAMES
    )
