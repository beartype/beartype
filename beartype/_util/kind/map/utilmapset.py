#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **dictionary mutators** (i.e., low-level callables modifying the
contents of passed dictionaries in various general-purpose ways).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.roar._roarexc import _BeartypeUtilMappingException
from beartype.typing import (
    Collection,
    Sequence,
)
from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_9
from beartype._util.text.utiltextrepr import represent_object
from collections.abc import (
    Hashable,
    Sequence as SequenceABC,
    Mapping,
    MutableMapping,
)

# ....................{ MERGERS                            }....................
def merge_mappings(*mappings: Mapping) -> Mapping:
    '''
    Safely merge all passed mappings if these mappings contain no **key-value
    collisions** (i.e., if these mappings either contain different keys *or*
    share one or more key-value pairs) *or* raise an exception otherwise (i.e.,
    if these mappings contain one or more key-value collisions).

    Since this function only safely merges mappings and thus *never* silently
    overrides any key-value pair of either mapping, order is insignificant;
    this function returns the same mapping regardless of the order in which
    these mappings are passed.

    Caveats
    -------
    This function creates and returns a new mapping of the same type as that of
    the first mapping. That type *must* define an ``__init__()`` method with
    the same signature as the standard :class:`dict` type; if this is *not* the
    case, an exception is raised.

    Parameters
    ----------
    mappings: tuple[Mapping]
        Tuple of two or more mappings to be safely merged.

    Returns
    -------
    Mapping
        Mapping of the same type as that of the first mapping created by safely
        merging these mappings.

    Raises
    ------
    _BeartypeUtilMappingException
        If either:

        * No mappings are passed.
        * Only one mappings are passed.
        * Two or more mappings are passed, but these mappings contain one or
          more key-value collisions.

    See Also
    --------
    :func:`.die_if_mappings_two_items_collide`
        Further details.
    '''

    # Return either...
    return (
        # If only two mappings are passed, defer to a function optimized for
        # merging two mappings.
        merge_mappings_two(mappings[0], mappings[1])
        if len(mappings) == 2 else
        # Else, three or more mappings are passed. In this case, defer to a
        # function optimized for merging three or more mappings.
        merge_mappings_two_or_more(mappings)
    )


def merge_mappings_two(mapping_a: Mapping, mapping_b: Mapping) -> Mapping:
    '''
    Safely merge the two passed mappings if these mappings contain no key-value
    collisions *or* raise an exception otherwise.

    Parameters
    ----------
    mapping_a: Mapping
        First mapping to be merged.
    mapping_b: Mapping
        Second mapping to be merged.

    Returns
    -------
    Mapping
        Mapping of the same type as that of the first mapping created by safely
        merging these mappings.

    Raises
    ------
    _BeartypeUtilMappingException
        If these mappings contain one or more key-value collisions.

    See Also
    --------
    :func:`beartype._util.kind.map.utilmaptest.die_if_mappings_two_items_collide`
        Further details.
    '''

    # If the first mapping is empty, return the second mapping as is.
    if not mapping_a:
        return mapping_b
    # Else, the first mapping is non-empty.
    #
    # If the second mapping is empty, return the first mapping as is.
    elif not mapping_b:
        return mapping_a
    # Else, both mappings are non-empty.

    # Avoid circular import dependencies.
    from beartype._util.kind.map.utilmaptest import (
        die_if_mappings_two_items_collide)

    # If these mappings contain a key-value collision, raise an exception.
    die_if_mappings_two_items_collide(mapping_a, mapping_b)
    # Else, these mappings contain *NO* key-value collisions.

    # Merge these mappings. Since no unsafe collisions exist, the order in
    # which these mappings are merged is irrelevant.
    #
    # If the active Python interpreter targets Python >= 3.9 and thus
    # supports "PEP 584 -- Add Union Operators To dict", merge these
    # mappings with the faster and terser dict union operator.
    if IS_PYTHON_AT_LEAST_3_9:
        return mapping_a | mapping_b  # type: ignore[operator]
    # Else, merge these mappings by creating and returning a new mapping of
    # the same type as that of the first mapping initialized from a slower
    # and more verbose dict unpacking operation.
    mapping_merged = (
        mapping_a.copy()
        if isinstance(mapping_a, dict) else
        type(mapping_a)(mapping_a)  # type: ignore[call-arg]
    )
    mapping_merged.update(mapping_b)  # type: ignore[attr-defined]
    return mapping_merged


def merge_mappings_two_or_more(mappings: Sequence[Mapping]) -> Mapping:
    '''
    Safely merge the one or more passed mappings if these mappings contain no
    key-value collisions *or* raise an exception otherwise.

    Parameters
    ----------
    mappings: SequenceABC[Mapping]
        SequenceABC of two or more mappings to be safely merged.

    Returns
    -------
    Mapping
        Mapping of the same type as that of the first mapping created by safely
        merging these mappings.

    Raises
    ------
    _BeartypeUtilMappingException
        If these mappings contain one or more key-value collisions.

    See Also
    --------
    :func:`beartype._util.kind.map.utilmaptest.die_if_mappings_two_items_collide`
        Further details.
    '''
    assert isinstance(mappings, SequenceABC), f'{repr(mappings)} not sequence.'

    # Number of passed mappings.
    MAPPINGS_LEN = len(mappings)

    # If less than two mappings are passed, raise an exception.
    if MAPPINGS_LEN < 2:
        # If only one mapping is passed, raise an appropriate exception.
        if MAPPINGS_LEN == 1:
            raise _BeartypeUtilMappingException(
                f'Two or more mappings expected, but only one mapping '
                f'{represent_object(mappings[0])} passed.')
        # Else, no mappings are passed. Raise an appropriate exception.
        else:
            raise _BeartypeUtilMappingException(
                'Two or more mappings expected, but no mappings passed.')
    # Else, two or more mappings are passed.
    assert isinstance(mappings[0], Mapping), (
        f'First mapping {repr(mappings[0])} not mapping.')

    # Merged mapping to be returned, initialized to the merger of the first two
    # passed mappings.
    mapping_merged = merge_mappings_two(mappings[0], mappings[1])

    # If three or more mappings are passed...
    if MAPPINGS_LEN > 2:
        # For each of the remaining mappings...
        for mapping in mappings[2:]:
            # Merge this mapping into the merged mapping to be returned.
            mapping_merged = merge_mappings_two(mapping_merged, mapping)
    # Else, only two mappings are passed. In these case, these mappings have
    # already been merged above.

    # Return this merged mapping.
    return mapping_merged

# ....................{ UPDATERS                           }....................
def update_mapping(mapping_trg: MutableMapping, mapping_src: Mapping) -> None:
    '''
    Safely update in-place the first passed mapping with all key-value pairs of
    the second passed mapping if these mappings contain no **key-value
    collisions** (i.e., if these mappings either only contain different keys
    *or* share one or more key-value pairs) *or* raise an exception otherwise
    (i.e., if these mappings contain one or more of the same keys associated
    with different values).

    Parameters
    ----------
    mapping_trg: MutableMapping
        Target mapping to be safely updated in-place with all key-value pairs
        of ``mapping_src``. This mapping is modified by this function and
        *must* thus be mutable.
    mapping_src: Mapping
        Source mapping to be safely merged into ``mapping_trg``. This mapping
        is *not* modified by this function and may thus be immutable.

    Raises
    ------
    _BeartypeUtilMappingException
        If these mappings contain one or more key-value collisions.

    See Also
    --------
    :func:`beartype._util.kind.map.utilmaptest.die_if_mappings_two_items_collide`
        Further details.
    '''
    assert isinstance(mapping_trg, MutableMapping), (
        f'{repr(mapping_trg)} not mutable mapping.')
    assert isinstance(mapping_src, Mapping), (
        f'{repr(mapping_src)} not mapping.')

    # If the second mapping is empty, silently reduce to a noop.
    if not mapping_src:
        return
    # Else, the second mapping is non-empty.

    # Avoid circular import dependencies.
    from beartype._util.kind.map.utilmaptest import (
        die_if_mappings_two_items_collide)

    # If these mappings contain a key-value collision, raise an exception.
    die_if_mappings_two_items_collide(mapping_trg, mapping_src)
    # Else, these mappings contain *NO* key-value collisions.

    # Update the former mapping from the latter mapping. Since no unsafe
    # collisions exist, this update is now guaranteed to be safe.
    mapping_trg.update(mapping_src)


def update_mapping_keys(
    # Mandatory parameters.
    mapping: MutableMapping,
    keys: Collection[Hashable],

    # Optional parameters.
    value: object = None,
) -> None:
    '''
    Map the passed keys to the same passed value in the passed mapping.

    This function is an efficient alternative to the standard idiom for adding
    multiple keys to a mapping when those keys *all* share the same value:

    .. code-block:: python

       # This function effectively does this -- except *WAY* faster. "for" loops
       # are excrutiatingly slow, due to raising "StopIteration" exceptions on
       # normal loop termination.
       for key in keys:
            mapping[key] = value

    This function is principally useful for efficiently creating and maintaining
    an **insertion-order mimic set** (i.e., a set-like object that preserves
    insertion order despite not actually being a set). While neither the builtin
    :class:`set` nor :class:`frozenset` types preserve insertion order, the
    builtin :class:`dict` type *does*. An insertion-order mimic set can thus be
    trivially constructed as a dictionary whose:

    * Keys are the desired ordered-preserving set members.
    * Values are ignorable (e.g., :data:`None`).

    Parameters
    ----------
    mapping : MutableMapping
        Mapping to add these key-value pairs to.
    keys : Iterable[Hashable]
        Collection of all keys to be added to this mapping.
    value : object, optional
        Singular value to map *all* of these keys to. Defaults to :data:`None`
        to trivialize insertion-order sets.
    '''
    assert isinstance(mapping, MutableMapping), (
        f'{repr(mapping)} not mutable mapping.')

    # Efficiently map *ALL* of these keys to this same value in this mapping.
    # Dismantled, this is:
    # * "(value,) * len(keys)", a tuple of the same length as the passed
    #   collection of keys whose items are *ALL* the passed value repeated
    #   verbatim. Since Python optimizes tuple creation, this operation is
    #   highly efficient despite superficially appearing to be insane.
    # * "zip(...)", an iterable pairing each of these keys with each of these
    #   duplicate values. If this iterable was itself a tuple, its contents
    #   would resemble:
    #       ((keys[0], value), (keys[1], value), ..., (keys[N], value))
    #
    # Note that this logic also implicitly handles the edge case of the caller
    # passing an empty iterable of keys. Why? Because the zip() builtin
    # dynamically generates an iterable whose length is the minimum of the
    # lengths of the passed iterables. If one of the passed iterables is empty,
    # the iterable that zip() generates will also be empty. Hallelujah, Python!
    mapping.update(zip(keys, (value,) * len(keys)))
