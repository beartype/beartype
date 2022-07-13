#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2022 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype Decidedly Object-Oriented Runtime-checking (DOOR) testers** (i.e.,
callables testing and validating :class:`beartype.door.TypeHint` instances).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.roar import BeartypeDoorException

# ....................{ VALIDATORS                         }....................
def die_unless_typehint(obj: object) -> None:
    '''
    Raise an exception unless the passed object is a **type hint wrapper**
    (i.e., :class:`TypeHint` instance).

    Parameters
    ----------
    obj : object
        Arbitrary object to be validated.

    Raises
    ----------
    BeartypeDoorException
        If this object is *not* a type hint wrapper.
    '''

    # Avoid circular import dependencies.
    from beartype.door._doorcls import TypeHint

    # If this object is *NOT* a type hint wrapper, raise an exception.
    if not isinstance(obj, TypeHint):
        raise BeartypeDoorException(
            f'{repr(obj)} not type hint wrapper '
            f'(i.e., "beartype.door.TypeHint" instance).'
        )
    # Else, this object is a type hint wrapper.

# ....................{ TESTERS                            }....................
#FIXME: Consider shifting to beartype.abby.is_subhint(), please.
def is_subhint(subhint: object, superhint: object) -> bool:
    '''
    ``True`` only if the first passed hint is a **subhint** of the second passed
    hint, in which case this second hint is a **superhint** of this first hint.

    Equivalently, this tester returns ``True`` only if *all* of the following
    conditions apply:

    * These two hints are **semantically related** (i.e., convey broadly similar
      semantics enabling these two hints to be reasonably compared). For
      example:

      * ``callable.abc.Iterable[str]`` and ``callable.abc.Sequence[int]`` are
        semantically related. These two hints both convey container semantics.
        Despite their differing child hints, these two hints are broadly similar
        enough to be reasonably comparable.
      * ``callable.abc.Iterable[str]`` and ``callable.abc.Callable[[], int]``
        are *not* semantically related. Whereas the first hints conveys a
        container semantic, the second hint conveys a callable semantic. Since
        these two semantics are unrelated, these two hints are dissimilar
        enough to *not* be reasonably comparable.

    * The first hint is **semantically equivalent** to or **narrower** than the
      second hint. Equivalently:

      * The first hint matches less than or equal to the total number of all
        possible objects matched by the second hint.
      * The size of the countably infinite set of all possible objects matched
        by the first hint is less than or equal to that of those matched by the
        second hint.

    * The first hint is **compatible** with the second hint. Since the first
      hint is semantically narrower than the second, APIs annotated by the first
      hint may safely replace that hint with the second hint; doing so preserves
      backward compatibility.

    Parameters
    ----------
    subhint : object
        PEP-compliant type hint or type to be tested as the subhint.
    superhint : object
        PEP-compliant type hint or type to be tested as the superhint.

    Returns
    -------
    bool
        ``True`` only if this first hint is a subhint of this second hint.

    Examples
    --------
        >>> from beartype.door import is_subhint
        >>> is_subhint(int, int)
        True
        >>> is_subhint(Callable[[], list], Callable[..., Sequence[Any]])
        True
        >>> is_subhint(Callable[[], list], Callable[..., Sequence[int]])
        False
    '''

    # Avoid circular import dependencies.
    from beartype.door._doorcls import TypeHint

    # The one-liner is mightier than the... many-liner.
    return TypeHint(subhint).is_subhint(TypeHint(superhint))
