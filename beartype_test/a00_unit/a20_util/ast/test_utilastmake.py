#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **abstract syntax tree (AST) factory utility unit tests.**

This submodule unit tests the public API of the private
:mod:`beartype._util.ast.utilastmake` submodule.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from pytest import fixture

# ....................{ FIXTURES                           }....................
@fixture(scope='session')
def node_sibling() -> 'ast.AST':
    '''
    Session-scoped fixture yielding an arbitrary **abstract syntax tree (AST)
    sibling node** (i.e., node intended to be passed as the ``node_sibling``
    keyword parameter to various AST-centric callables defined throughout the
    :mod:`beartype` codebase).
    '''

    # Defer fixture-specific imports.
    from ast import Constant

    # Yield an arbitrary node sibling, defined purely for simplicity as a string
    # literal node whose string is an arbitrary Python identifier.
    yield Constant('In_folds_of_the_green_serpent')

# ....................{ TESTS ~ factory                    }....................
def test_make_node_object_attr_load(node_sibling: 'ast.AST') -> None:
    '''
    Test the :func:`beartype._util.ast.utilastmake.make_node_object_attr_load`
    factory.

    Parameters
    ----------
    node_sibling : 'ast.AST'
        Arbitrary sibling node to be passed as the ``node_sibling`` parameter.
    '''

    # Defer test-specific imports.
    from beartype.roar import BeartypeClawImportAstException
    from beartype._util.ast.utilastmake import make_node_object_attr_load
    from pytest import raises

    # Assert that this factory raises the expected exception when passed neither
    # the "node_obj" nor "obj_name" parameters.
    with raises(BeartypeClawImportAstException):
        make_node_object_attr_load(
            attr_name='Burn_with_the_poison',
            node_sibling=node_sibling,
        )

    # Assert that this factory raises the expected exception when passed both
    # the "node_obj" and "obj_name" parameters.
    with raises(BeartypeClawImportAstException):
        make_node_object_attr_load(
            attr_name='Burn_with_the_poison',
            node_sibling=node_sibling,
            node_obj=node_sibling,
            obj_name='and_precipitates',
        )
