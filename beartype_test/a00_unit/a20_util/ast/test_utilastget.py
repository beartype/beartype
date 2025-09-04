#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **abstract syntax tree (AST) getter utility** unit tests.

This submodule unit tests the public API of the private
:mod:`beartype._util.ast.utilastget` submodule.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS                              }....................
def test_get_node_attr_basenames() -> None:
    '''
    Test the :func:`beartype._util.ast.utilastget.get_node_attr_basenames`
    factory.

    Parameters
    ----------
    node_sibling : 'ast.AST'
        Arbitrary sibling node to be passed as the ``node_sibling`` parameter.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype._util.ast.utilastget import get_node_attr_basenames
    from beartype._util.ast.utilastmake import make_node_from_code_snippet

    # ....................{ LOCALS                         }....................
    # "ast.Name" node encapsulating the unqualified basename of an arbitrary
    # global attribute, parsed from a code snippet.
    node_name = make_node_from_code_snippet('''taste_the_spicy_wreaths''')

    # "ast.Attribute" node encapsulating the fully-qualified basename of an
    # arbitrary global attribute, parsed from a code snippet.
    node_attr = make_node_from_code_snippet('''of_incense.breathed.aloft''')

    # Arbitrary non-empty list to be passed to this getter below.
    attr_basenames = ['from', 'sacred hills']

    # ....................{ ASSERT                         }....................
    # Assert this getter passed a "Name" node returns the expected list.
    assert get_node_attr_basenames(node_name) == ['taste_the_spicy_wreaths']

    # Assert this getter passed an "Attribute" node returns the expected list.
    assert get_node_attr_basenames(node_attr) == [
        'of_incense', 'breathed', 'aloft']

    # ....................{ ASSERT ~ attr_basenames        }....................
    # List of the one or more unqualified basenames comprising the possibly
    # fully-qualified name of the passed "Attribute" node such that the returned
    # list is the passed "attr_basenames" list.
    attr_basenames_new = get_node_attr_basenames(
        node=node_attr, attr_basenames=attr_basenames)

    # Assert these two lists to indeed be the same.
    assert attr_basenames_new is attr_basenames

    # Assert this list to contain the expected basenames.
    assert attr_basenames == ['of_incense', 'breathed', 'aloft']
