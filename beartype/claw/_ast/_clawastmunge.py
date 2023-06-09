#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype **abstract syntax tree (AST) mungers** (i.e., low-level utilities
modifying various properties of various nodes in the currently visited AST).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from ast import (
    AST,
    ImportFrom,
    alias,
)
# from beartype.typing import (
#     List,
#     Optional,
#     Union,
# )
from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_8

# ....................{ COPIERS                            }....................
#FIXME: Unit test us up, please.
def copy_node_code_metadata(node_src: AST, node_trg: AST) -> None:
    '''
    Copy all **source code metadata** (i.e., beginning and ending line and
    column numbers) from the passed source abstract syntax tree (AST) node onto
    the passed target AST node.

    This function is an efficient alternative to:

    * The extremely inefficient (albeit still useful)
      :func:`ast.fix_missing_locations` function.
    * The mildly inefficient (and mostly useless) :func:`ast.copy_location`
      function.

    The tradeoffs are as follows:

    * :func:`ast.fix_missing_locations` is ``O(n)`` time complexity for ``n``
      the number of AST nodes across the entire AST tree, but requires only a
      single trivial call and is thus considerably more "plug-and-play" than
      this function.
    * This function is ``O(1)`` time complexity irrespective of the size of the
      AST tree, but requires one still mostly trivial call for each synthetic
      AST node inserted into the AST tree by the
      :class:`BeartypeNodeTransformer` above.

    Caveats
    ----------
    **This function should only be passed nodes that support code metadata.**
    Although *most* nodes do, some nodes do not. Why? Because they are *not*
    actually nodes; they simply masquerade as nodes in documentation for the
    standard :mod:`ast` module, which inexplicably makes *no* distinction
    between the two. These pseudo-nodes include:

    * :class:`ast.Del` nodes.
    * :class:`ast.Load` nodes.
    * :class:`ast.Store` nodes.

    Indeed, this observation implies that these pseudo-nodes may be globalized
    as singletons for efficient reuse throughout our AST generation algorithms.

    Lastly, note that nodes may be differentiated from pseudo-nodes by passing
    the call to the :func:`ast.dump` function in the code snippet presented in
    the docstring for the :class:`BeartypeNodeTransformer` class an additional
    ``include_attributes=True`` parameter: e.g.,

    .. code-block:: python

       print(ast.dump(ast.parse(CODE), indent=4, include_attributes=True))

    Actual nodes have code metadata printed for them; pseudo-nodes do *not*.

    Parameters
    ----------
    node_src : AST
        Source AST node to copy source code metadata from.
    node_trg : AST
        Target AST node to copy source code metadata onto.

    See Also
    ----------
    :func:`ast.copy_location`
        Less efficient analogue of this function running in ``O(k)`` time
        complexity for ``k`` the number of types of source code metadata.
        Typically, ``k == 4``.
    '''
    assert isinstance(node_src, AST), f'{repr(node_src)} not AST node.'
    assert isinstance(node_trg, AST), f'{repr(node_trg)} not AST node.'

    # Copy all source code metadata from this source to target AST node.
    node_trg.lineno     = node_src.lineno
    node_trg.col_offset = node_src.col_offset

    # If the active Python interpreter targets Python >= 3.8, then additionally
    # copy all source code metadata exposed by Python >= 3.8.
    if IS_PYTHON_AT_LEAST_3_8:
        node_trg.end_lineno     = node_src.end_lineno  # type: ignore[attr-defined]
        node_trg.end_col_offset = node_src.end_col_offset  # type: ignore[attr-defined]

# ....................{ FACTORIES                          }....................
#FIXME: Unit test us up, please.
def make_node_importfrom(
    module_name: str,
    attr_name: str,
    node_sibling: AST,
) -> ImportFrom:
    '''
    Create and return a new **import-from abstract syntax tree (AST) node**
    (i.e., node encapsulating an import statement of the alias-style format
    ``from {module_name} import {attr_name}``) importing the attribute with the
    passed name from the module with the passed name.

    Parameters
    ----------
    module_name : str
        Fully-qualified name of the module to import this attribute from.
    attr_name : str
        Unqualified basename of the attribute to import from this module.
    node_sibling : AST
        Sibling AST node to copy source code metadata from.

    Returns
    ----------
    ImportFrom
        Import-from AST node importing this attribute from this module.
    '''
    assert isinstance(module_name, str), f'{repr(module_name)} not string.'
    assert isinstance(attr_name, str), f'{repr(attr_name)} not string.'

    # Node encapsulating the name of the attribute to import from this module.
    node_importfrom_name = alias(attr_name)

    # Node encapsulating the name of the module to import this attribute from.
    node_importfrom = ImportFrom(
        module=module_name, names=[node_importfrom_name])

    # Copy all source code metadata (e.g., line numbers) from this sibling node
    # onto this import from node.
    copy_node_code_metadata(
        node_src=node_sibling, node_trg=node_importfrom)
    copy_node_code_metadata(
        node_src=node_sibling, node_trg=node_importfrom_name)

    # Return this import from node.
    return node_importfrom
