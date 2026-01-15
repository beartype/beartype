#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **PEP-noncompliant type hint reducers** (i.e., low-level callables
converting higher-level type hints that do *not* comply with any specific PEP
but are nonetheless shallowly supported by :mod:`beartype` to lower-level type
hints more readily consumable by :mod:`beartype`).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype._check.metadata.hint.hintsane import (
    HINT_SANE_IGNORABLE,
    HintOrSane,
    HintSane,
)
from beartype._cave._cavefast import (
    ThreadLockNonreentrantType,
    ThreadLockReentrantType,
)
from beartype._data.typing.datatypingport import Hint
from beartype._util.hint.utilhinttest import die_unless_hint
from beartype._util.utilobject import is_object_hashable
from threading import (
    Lock,
    RLock,
)

# ....................{ REDUCERS                           }....................
def reduce_hint_nonpep(hint: Hint, exception_prefix: str) -> HintOrSane:
    '''
    Reduce the passed **PEP-noncompliant type hint** (i.e., type hint identified
    by *no* sign, typically but *not* necessarily implying this hint to be an
    isinstanceable type) if this hint satisfies various conditions to another
    possibly PEP-compliant type hint.

    Specifically, if this hint is either:

    * A valid PEP-noncompliant isinstanceable type, this reducer preserves this
      type as is.
    * A valid PEP-compliant hint unrecognized by beartype, this reducer raises
      a :exc:`.BeartypeDecorHintPepUnsupportedException` exception.
    * An invalid and thus PEP-noncompliant hint, this reducer raises an
      :exc:`.BeartypeDecorHintNonpepException` exception.

    This reducer is intentionally *not* memoized (e.g., by the
    ``callable_cached`` decorator), as the implementation trivially reduces to a
    one-liner.

    Parameters
    ----------
    hint : Hint
        PEP-noncompliant hint to be reduced.
    exception_prefix : str
        Human-readable substring prefixing raised exception messages.

    Returns
    -------
    HintOrSane
        Either:

        * If this hint is the root :class:`object` superclass, the ignorable
          :data:`.HINT_SANE_IGNORABLE` singleton. :class:`object` is the
          transitive superclass of all classes. Attributes annotated as
          :class:`object` unconditionally match *all* objects under
          :func:`isinstance`-based type covariance and thus semantically reduce
          to unannotated attributes -- which is to say, they are ignorable.
        * Else, this PEP-noncompliant hint unmodified.

    Raises
    ------
    BeartypeDecorHintPepUnsupportedException
        If this object is a PEP-compliant type hint currently unsupported by
        the :func:`beartype.beartype` decorator.
    BeartypeDecorHintNonpepException
        If this object is neither a:

        * Supported PEP-compliant type hint.
        * Supported PEP-noncompliant type hint.
    '''

    # If this hint is hashable...
    if is_object_hashable(hint):
        # Either:
        # * If this PEP-noncompliant hint is a singleton unsupported by
        #   @beartype but reducible to a possibly PEP-noncompliant hint that is
        #   a different singleton supported by @beartype, the latter.
        # * Else, "None".
        hint_reduced = _HINT_NONPEP_SINGLETON_TO_REDUCTION.get(hint)
        # print(f'Reduced non-PEP hint {repr(hint)} to {repr(hint_reduced)}...')

        # If this hint is reducible, replace this hint by that reduction.
        if hint_reduced is not None:
            hint = hint_reduced  # pyright: ignore
        # Else, this hint is irreducible. In this case, preserve this hint.
    # Else, this hint is unhashable. In this case, preserve this hint as is.

    # If this hint was *NOT* reduced to sanified metadata above...
    if not isinstance(hint, HintSane):
        # If this hint is unsupported by @beartype (after possibly reducing
        # this hint to a supported hint above), raise an exception.
        die_unless_hint(hint=hint, exception_prefix=exception_prefix)
        # Else, this hint is supported by @beartype.
    # Else, this hint was reduced to sanified metadata above. In this case,
    # avoid passing this metadata to the die_unless_hint() raiser above. By
    # definition, this hint has been sanified and is thus supported by
    # @beartype. More importantly, that raiser justifiably fails to recognize
    # "HintSane" instances as supported PEP-compliant type hints.

    # Return this possibly hint reduced hint.
    return hint

# ....................{ PRIVATE ~ globals                  }....................
# The _init() function defined below conditionally initializes this dictionary
# with additional key-value pairs.
_HINT_NONPEP_SINGLETON_TO_REDUCTION: dict[object, HintOrSane] = {
    # ....................{ CORE                           }....................
    # Reduce the root "object" superclass to the ignorable "HINT_SANE_IGNORABLE"
    # singleton. "object" is the transitive superclass of all classes.
    # Attributes annotated as "object" unconditionally match *ALL* objects under
    # isinstance()-based type covariance and thus semantically reduce to
    # unannotated attributes -- which is to say, they are ignorable.
    object: HINT_SANE_IGNORABLE,

    # ....................{ API ~ threading                }....................
    # Reduce the standard "threading.RLock" attribute (which is a pure-Python
    # factory function unusable as a type hint) to the corresponding C-based
    # type underlying this attributes (which is usable as a type hint).
    #
    # Note that the same logic does *NOT* unconditionally extend to the
    # superficially similar "threading.Lock" attribute, which:
    # * Under Python >= 3.13, is a C-based type usable as a type hint.
    # * Under Python <= 3.12, is a C-based factory function unusable as a type
    #   hint.
    #
    # The _init() function defined below conditionally handles these edge cases.
    RLock: ThreadLockReentrantType,
}
'''
Dictionary assisting the :func:`.reduce_hint_nonpep` reducer by mapping from
each PEP-noncompliant type hint that is a singleton internally unsupported by
:mod:`beartype` to a possibly PEP-compliant type hint that is a different
singleton internally supported by :mod:`beartype`.
'''

# ....................{ PRIVATE ~ initializers             }....................
def _init() -> None:
    '''
    Initialize this submodule.
    '''

    # Defer function-specific imports.
    from beartype._util.py.utilpyversion import IS_PYTHON_AT_MOST_3_12

    # If the active Python interpreter targets <= Python 3.12 and thus defines
    # the standard "threading.Lock" attribute to be a C-based factory function
    # unusable as a hint (rather than a C-based type usable as a hint)...
    if IS_PYTHON_AT_MOST_3_12:
        # Update the dictionary global defined above with...
        _HINT_NONPEP_SINGLETON_TO_REDUCTION.update({
            # ....................{ API ~ threading        }....................
            # Reduce this otherwise useless attribute to the corresponding
            # useful C-based type underlying this attribute.
            Lock: ThreadLockNonreentrantType,
        })
    # Else, the active Python interpreter targets >= Python 3.13 and thus
    # defines the standard "threading.Lock" attribute to be a C-based type
    # usable as a type hint. Preserve this type as is.


# Initialize this submodule.
_init()
