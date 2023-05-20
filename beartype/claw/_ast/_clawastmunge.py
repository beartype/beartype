#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype abstract syntax tree (AST) mungers** (i.e., low-level utilities
modifying various properties of various nodes in the currently visited AST).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from ast import AST
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

    Parameters
    ----------
    node_src: AST
        Source AST node to copy source code metadata from.
    node_trg: AST
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
