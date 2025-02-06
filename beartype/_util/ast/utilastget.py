#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype **abstract syntax tree (AST) getters** (i.e., low-level callables
acquiring various properties of various nodes in the currently visited AST).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from ast import (
    AST,
    Module,
    dump as ast_dump,
    parse as ast_parse,
)
from beartype.roar._roarexc import _BeartypeUtilAstException

# ....................{ GETTERS ~ node                     }....................
#FIXME: Unit test us up, please.
def get_node_repr_indented(node: AST) -> str:
    '''
    Human-readable string pretty-printing the contents of the passed abstract
    syntax tree (AST), complete with readable indentation.

    Parameters
    ----------
    node : AST
        AST to be pretty-printed.

    Returns
    -------
    str
        Human-readable string pretty-printing the contents of this AST.
    '''
    assert isinstance(node, AST), f'{repr(node)} not AST.'

    # Return the pretty-printed contents of this AST.
    return ast_dump(node, indent=4)  # type: ignore[call-arg]

# ....................{ GETTERS ~ node                     }....................
#FIXME: Unit test us up, please. When we do, remove the "pragma: no cover" from
#the body of this getter below.
def get_code_child_node(code: str) -> AST:
    '''
    Abstract syntax tree (AST) node parsed from the passed (presumably)
    triple-quoted string defining a single child object.

    This function is principally intended to be called from our test suite as a
    convenient means of "parsing" triple-quoted strings into AST nodes.

    Caveats
    -------
    **This function assumes that this string defines only a single child
    object.** If this string defines either no *or* two or more child objects,
    an exception is raised.

    Parameters
    ----------
    code : str
        Triple-quoted string defining a single child object.

    Returns
    -------
    AST
        AST node encapsulating the object defined by this string.

    Raises
    -------
    _BeartypeUtilAstException
        If this string defines either no *or* two or more child objects.
    '''
    assert isinstance(code, str), f'{repr(code)} not string.'

    # "ast.Module" AST tree parsed from this string.
    node_module = ast_parse(code)

    # If this node is *NOT* actually a module node, raise an exception.
    if not isinstance(node_module, Module):  # pragma: no cover
        raise _BeartypeUtilAstException(
            f'{repr(node_module)} not AST module node.')
    # Else, this node is a module node.

    # List of all direct child nodes of this parent module name.
    nodes_child = node_module.body

    # If this module node contains either no *OR* two or more child nodes, raise
    # an exception.
    if len(nodes_child) != 1:  # pragma: no cover
        raise _BeartypeUtilAstException(
            f'Python code {repr(code)} defines '
            f'{len(nodes_child)} != 1 child objects.'
        )
    # Else, this module node contains exactly one child node.

    # Return this child node.
    return nodes_child[0]
