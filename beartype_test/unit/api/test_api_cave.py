#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright 2014-2020 by Cecil Curry.
# See "LICENSE" for further details.

'''
**Beartype cave API unit tests.**

This submodule unit tests the public API of the :mod:`beartype.cave` submodule.
'''

# ....................{ IMPORTS                           }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

import argparse, sys

# ....................{ ASSERTERS                         }....................
def _assert_obj_type(obj: object, cls: type) -> None:
    '''
    Assert the passed object to be an instance of the passed type.

    Parameters
    ----------
    types : tuple
        Tuple of arbitrary objects to be validated.
    '''

    # Assert that this type actually is.
    assert isinstance(cls, type)

    # Assert this object to be an instance of this type.
    assert isinstance(obj, cls)


def _assert_tuple(types: tuple) -> None:
    '''
    Assert each item of the passed tuple to be a type.

    Parameters
    ----------
    types : tuple
        Tuple of arbitrary objects to be validated.
    '''

    # Assert that this tuple actually is.
    assert isinstance(types, tuple)

    # Assert that each item of this tuple is a type.
    for item in types:
        assert isinstance(item, type)

# ....................{ TESTS ~ types                     }....................
def test_api_cave_types_core() -> None:
    '''
    Test all **core simple types** (i.e., types unconditionally published for
    *all* supported Python versions regardless of the importability of optional
    third-party dependencies) published by the :mod:`beartype.cave` submodule.
    '''

    # Import this submodule. For each core simple type published by this
    # submodule type, assert below that:
    #
    # * This type is a simple type.
    # * An object expected to be of this type is of this type.
    from beartype import cave

    # Test "AnyType".
    _assert_obj_type(object(), cave.AnyType)

    # Test "NoneType".
    _assert_obj_type(None, cave.NoneType)

    # Test "ClassType".
    class WeHaveFedOurSeaForAThousandYears(object): pass
    _assert_obj_type(WeHaveFedOurSeaForAThousandYears, cave.ClassType)

    # Test "UnavailableType".
    assert isinstance(cave.UnavailableType, type)

    # Test "FileType".
    with open(__file__, 'r') as this_file:
        _assert_obj_type(this_file, cave.FileType)

    # Test "ModuleType".
    _assert_obj_type(sys.modules[__name__], cave.ModuleType)

    # Test "ArgParserType".
    arg_parser = argparse.ArgumentParser()
    _assert_obj_type(arg_parser, cave.ArgParserType)

    # Test "ArgSubparsersType".
    _assert_obj_type(arg_parser.add_subparsers(), cave.ArgSubparsersType)

# ....................{ TESTS ~ tuples                    }....................
def test_api_cave_tuples_core() -> None:
    '''
    Test all **core tuple types** (i.e., tuples of types unconditionally
    published for *all* supported Python versions regardless of the
    importability of optional third-party dependencies) published by the
    :mod:`beartype.cave` submodule.
    '''

    # Import this submodule. For each core tuple type published by this
    # submodule type, assert below that:
    #
    # * This tuple contains only simple types.
    # * One or more objects expected to be of one or more types in this tuple
    #   are of these types.
    from beartype import cave

    # Test "UnavailableTypes".
    _assert_tuple(cave.UnavailableTypes)
    assert cave.UnavailableTypes == ()
