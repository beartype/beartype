#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
:mod:`pytest` **object factories** (i.e., low-level test-specific utility
functions creating and returning objects, typically for use in higher-level
:mod:`pytest` fixtures defined elsewhere in this test suite).
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from collections.abc import (
    Iterable,
)

# ....................{ CONTEXTS                           }....................
def make_container_from_funcs(func_names: 'Iterable[str]') -> list:
    '''
    List created by iterating over the passed iterable and, for the
    fully-qualified name of each callable in that iterable, dynamically
    importing that callable, calling that callable, and adding the items of the
    container returned by that callable to this list..

    Parameters
    ----------
    func_names : Iterable[str]
        Iterable of the fully-qualified names of all callables to be called.

    Returns
    -------
    T
        Instance of this container, iteratively composed from the containers
        returned by these callables.
    '''
    assert isinstance(func_names, Iterable), f'{repr(func_names)} not iterable.'

    # Defer utility-specific imports.
    from beartype._util.module.utilmodimport import import_module_attr

    # Temporary list with which to compose this container.
    main_list = []

    # For the passed name of each callable...
    for func_name in func_names:
        assert isinstance(func_name, str), f'{repr(func_name)} not string.'

        # This callable dynamically imported as this name.
        func = import_module_attr(func_name)

        # List produced by calling this callable.
        func_list = func()

        # Append all items in this list to this larger list to be returned.
        main_list.extend(func_list)

    # Return this list.
    return main_list
