#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2021 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **dictionary** utilities.

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                           }....................
from beartype.roar._roarexc import _BeartypeUtilMappingException
from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_9
from beartype._util.text.utiltextrepr import represent_object
from collections.abc import Sequence, Mapping
from typing import Sequence as SequenceHint

# ....................{ MERGERS                           }....................
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
    ----------
    This function creates and returns a new mapping of the same type as that of
    the first mapping. That type *must* define an ``__init__()`` method with
    the same signature as the standard :class:`dict` type; if this is *not* the
    case, an exception is raised.

    Parameters
    ----------
    mappings: Tuple[Mapping]
        Tuple of two or more mappings to be safely merged.

    Returns
    ----------
    Mapping
        Mapping of the same type as that of the first mapping created by safely
        merging these mappings.

    Raises
    ----------
    _BeartypeUtilMappingException
        If either:

        * No mappings are passed.
        * Only one mappings are passed.
        * Two or more mappings are passed, but these mappings contain one or
          more **key-value collisions.** A key-value collision occurs when any
          key ``ka`` and associated value ``va`` of the first mapping and any
          key ``kb`` and associated value ``vb`` of the second mapping satisfy
          ``ka == kb && va != vb``. Equivalently, a key-value collision occurs
          when any common keys shared between both mappings are associated with
          different values.
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
    ----------
    Mapping
        Mapping of the same type as that of the first mapping created by safely
        merging these mappings.

    Raises
    ----------
    _BeartypeUtilMappingException
        If these mappings contain one or more key-value collisions.

    See Also
    ----------
    :func:`merge_mappings`
        Further details.
    '''
    assert isinstance(mapping_a, Mapping), f'{repr(mapping_a)} not mapping.'
    assert isinstance(mapping_b, Mapping), f'{repr(mapping_b)} not mapping.'

    # If the first mapping is empty, return the second mapping as is.
    if not mapping_a:
        return mapping_b
    # Else, the first mapping is non-empty.
    #
    # If the second mapping is empty, return the first mapping as is.
    elif not mapping_b:
        return mapping_a
    # Else, both mappings are non-empty.

    # Set of all keys of the first mapping.
    mapping_a_keys = mapping_a.keys()

    # Set of all key collisions (i.e., keys residing in both mappings). Since
    # keys are necessarily hashable, this set intersection is guaranteed to be
    # safe and thus *NEVER* raise a "TypeError" exception.
    #
    # Note that omitting the keys() method call on the latter but *NOT* former
    # mapping behaves as expected and offers a helpful microoptimization.
    mapping_keys_shared = mapping_a_keys & mapping_b  # type: ignore[operator]

    # If one or more keys collide...
    if mapping_keys_shared:
        # Set of all item collisions (i.e., items residing in both mappings).
        # Ideally, we would efficiently intersect these items as follows:
        #     mapping_items_shared = mapping_a.items() & mapping_b.items()
        # Sadly, doing so raises a "TypeError" if one or more values of these
        # mappings are unhashable -- as they typically are in common use cases
        # throughout this codebase. Ergo, we fallback to a less efficient but
        # considerably more robust alternative supporting unhashable values.
        mapping_items_shared = {
            # For each key-value pair of the second mapping, that pair...
            (mapping_b_key, mapping_b_value)
            for mapping_b_key, mapping_b_value in mapping_b.items()
            # If...
            if (
                # This key also resides in the first mapping *AND*...
                mapping_b_key in mapping_a_keys and
                # This key also maps to the same value in the first mapping.
                mapping_a[mapping_b_key] is mapping_b_value
            )
        }

        # If the number of key and item collisions differ, then one or more
        # keys residing in both mappings have differing values. Since merging
        # these mappings as is would silently and thus unsafely override the
        # values associated with these keys in the former mapping with the
        # values associated with these keys in the latter mapping, raise an
        # exception to notify the caller.
        if len(mapping_keys_shared) != len(mapping_items_shared):
            # Set of all safe key collisions (i.e., all colliding keys
            # associated with the same values in both mappings).
            mapping_keys_shared_safe = {
                key_shared for key_shared, _ in mapping_items_shared}

            # Dictionary of all unsafe key-value pairs (i.e., pairs such that
            # merging these keys would silently override the values associated
            # with these keys in either the first or second mappings) from the
            # first and second mappings.
            mapping_a_unsafe = dict(
                (key_shared_unsafe, mapping_a[key_shared_unsafe])
                for key_shared_unsafe in mapping_keys_shared
                if key_shared_unsafe not in mapping_keys_shared_safe
            )
            mapping_b_unsafe = dict(
                (key_shared_unsafe, mapping_b[key_shared_unsafe])
                for key_shared_unsafe in mapping_keys_shared
                if key_shared_unsafe not in mapping_keys_shared_safe
            )

            # Raise a human-readable exception.
            raise _BeartypeUtilMappingException(
                f'Mappings not safely mergeable due to key-value collisions:\n'
                f'~~~~[ mapping_a collisions ]~~~~\n{repr(mapping_a_unsafe)}\n'
                f'~~~~[ mapping_b collisions ]~~~~\n{repr(mapping_b_unsafe)}'
            )
        # Else, the number of key and item collisions are the same, implying
        # that all colliding keys are associated with the same values in both
        # mappings, implying that both mappings contain the same colliding
        # key-value pairs. Since merging these mappings as is will *NOT*
        # silently and thus unsafely override any values of either mapping,
        # merge these mappings as is.
    # Else, no keys collide.

    # Merge these mappings. Since no unsafe collisions exist, the order in
    # which these mappings are merged is irrelevant.
    return (
        # If the active Python interpreter targets Python >= 3.9 and thus
        # supports "PEP 584 -- Add Union Operators To dict", merge these
        # mappings with the faster and terser dict union operator.
        mapping_a | mapping_b  # type: ignore[operator]
        if IS_PYTHON_AT_LEAST_3_9 else
        # Else, merge these mappings by creating and returning a new mapping of
        # the same type as that of the first mapping initialized from a slower
        # and more verbose dict unpacking operation.
        type(mapping_a)(mapping_a, **mapping_b)  # type: ignore[call-arg]
    )


def merge_mappings_two_or_more(mappings: SequenceHint[Mapping]) -> Mapping:
    '''
    Safely merge the one or more passed mappings if these mappings contain no
    key-value collisions *or* raise an exception otherwise.

    Parameters
    ----------
    mappings: Sequence[Mapping]
        Sequence of two or more mappings to be safely merged.

    Returns
    ----------
    Mapping
        Mapping of the same type as that of the first mapping created by safely
        merging these mappings.

    Raises
    ----------
    _BeartypeUtilMappingException
        If these mappings contain one or more key-value collisions.

    See Also
    ----------
    :func:`merge_mappings`
        Further details.
    '''
    assert isinstance(mappings, Sequence), f'{repr(mappings)} not sequence.'

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

    # Return this merged mapping.
    return mapping_merged
