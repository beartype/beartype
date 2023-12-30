#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype **abstract syntax tree (AST) factories** (i.e., low-level callables
creating and returning various types of nodes, typically for inclusion in the
currently visited AST).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from ast import (
    AST,
    Call,
    ImportFrom,
    Name,
    alias,
    keyword,
)
from beartype.typing import (
    List,
    Optional,
)
from beartype._cave._cavemap import NoneTypeOr
from beartype._data.ast.dataast import (
    NODE_CONTEXT_LOAD,
    NODE_CONTEXT_STORE,
)
from beartype._data.hint.datahinttyping import ListNodes
from beartype._data.kind.datakindsequence import LIST_EMPTY
from beartype._util.ast.utilastmunge import copy_node_metadata

# ....................{ FACTORIES                          }....................
#FIXME: Unit test us up, please.
def make_node_call(
    # Mandatory parameters.
    func_name: str,
    node_sibling: AST,

    # Optional parameters.
    nodes_args: ListNodes = LIST_EMPTY,
    nodes_kwargs: List[keyword] = LIST_EMPTY,
) -> Call:
    '''
    Create and return a new **callable call abstract syntax tree (AST) node**
    (i.e., node encapsulating a call to an arbitrary function or method)
    calling the function or method with the passed name, positional arguments,
    and keyword arguments.

    Parameters
    ----------
    func_name : str
        Fully-qualified name of the module to import this attribute from.
    node_sibling : AST
        Sibling node to copy source code metadata from.
    nodes_args : ListNodes, optional
        List of zero or more **positional parameter AST nodes** comprising the
        tuple of all positional parameters to be passed to this call. Defaults
        to the empty list.
    nodes_kwargs : ListNodes, optional
        List of zero or more **keyword parameter AST nodes** comprising the
        dictionary of all keyword parameters to be passed to this call. Defaults
        to the empty list.

    Returns
    -------
    Call
        Callable call node calling this callable with these parameters.
    '''
    assert isinstance(nodes_args, list), f'{repr(nodes_args)} not list.'
    assert isinstance(nodes_kwargs, list), f'{repr(nodes_kwargs)} not list.'
    assert all(
        isinstance(node_args, AST) for node_args in nodes_args), (
        f'{repr(nodes_args)} not list of AST nodes.')
    assert all(
        isinstance(node_kwargs, keyword) for node_kwargs in nodes_kwargs), (
        f'{repr(nodes_kwargs)} not list of keyword nodes.')

    # Child node referencing the callable to be called.
    node_func_name = make_node_name_load(name=func_name, node_sibling=node_sibling)

    # Child node calling this callable.
    node_func_call = Call(
        func=node_func_name,
        args=nodes_args,
        keywords=nodes_kwargs,
    )

    # Copy all source code metadata (e.g., line numbers) from this sibling node
    # onto this new node.
    copy_node_metadata(node_src=node_sibling, node_trg=node_func_call)

    # Return this import-from node.
    return node_func_call


#FIXME: Unit test us up, please.
def make_node_importfrom(
    # Mandatory parameters.
    module_name: str,
    source_attr_name: str,
    node_sibling: AST,

    # Optional parameters.
    target_attr_name: Optional[str] = None,
) -> ImportFrom:
    '''
    Create and return a new **import-from abstract syntax tree (AST) node**
    (i.e., node encapsulating an import statement of the alias-style format
    ``from {module_name} import {attr_name}``) importing the attribute with the
    passed source name from the module with the passed name into the currently
    visited module as a new attribute with the passed target name.

    Parameters
    ----------
    module_name : str
        Fully-qualified name of the module to import this attribute from.
    source_attr_name : str
        Unqualified basename of the attribute to import from this module.
    target_attr_name : Optional[str]
        Either:

        * If this attribute is to be imported into the currently visited module
          under a different unqualified basename, that basename.
        * If this attribute is to be imported into the currently visited module
          under the same unqualified basename as ``source_attr_name``,
          :data:`None`.

        Defaults to :data:`None`.
    node_sibling : AST
        Sibling node to copy source code metadata from.

    Returns
    -------
    ImportFrom
        Import-from node importing this attribute from this module.
    '''
    assert isinstance(module_name, str), f'{repr(module_name)} not string.'
    assert isinstance(source_attr_name, str), (
        f'{repr(source_attr_name)} not string.')
    assert isinstance(target_attr_name, NoneTypeOr[str]), (
        f'{repr(target_attr_name)} neither string nor "None".')

    # Node encapsulating the name of the attribute to import from this module,
    # defined as either...
    node_importfrom_name = (
        # If this attribute is to be imported into the currently visited module
        # under a different basename, do so;
        alias(name=source_attr_name, asname=target_attr_name)
        if target_attr_name else
        # Else, this attribute is to be imported into the currently visited
        # module under the same basename. In this case, do so.
        alias(name=source_attr_name)
    )

    # Node encapsulating the name of the module to import this attribute from.
    node_importfrom = ImportFrom(
        module=module_name,
        names=[node_importfrom_name],
        # Force an absolute import for safety (i.e., prohibit relative imports).
        level=0,
    )

    # Copy all source code metadata (e.g., line numbers) from this sibling node
    # onto these new nodes.
    copy_node_metadata(
        node_src=node_sibling, node_trg=(node_importfrom, node_importfrom_name))

    # Return this import-from node.
    return node_importfrom

# ....................{ FACTORIES ~ name                   }....................
#FIXME: Unit test us up.
def make_node_name_load(name: str, node_sibling: AST) -> Name:
    '''
    Create and return a new **attribute access abstract syntax tree (AST) node**
    (i.e., node encapsulating an access of an attribute) in the current lexical
    scope with the passed name.

    Parameters
    ----------
    name : str
        Fully-qualified name of the attribute to be accessed.
    node_sibling : AST
        Sibling node to copy source code metadata from.

    Returns
    -------
    Name
        Name node accessing this attribute in the current lexical scope.
    '''
    assert isinstance(name, str), f'{repr(name)} not string.'

    # Child node accessing this attribute in the current lexical scope.
    node_name = Name(name, ctx=NODE_CONTEXT_LOAD)

    # Copy all source code metadata (e.g., line numbers) from this sibling node
    # onto this child node.
    copy_node_metadata(node_src=node_sibling, node_trg=node_name)

    # Return this child node.
    return node_name


#FIXME: Unit test us up.
def make_node_name_store(name: str, node_sibling: AST) -> Name:
    '''
    Create and return a new **attribute assignment abstract syntax tree (AST)
    node** (i.e., node encapsulating an assignment of an attribute) in the
    current lexical scope with the passed name.

    Parameters
    ----------
    name : str
        Fully-qualified name of the attribute to be assigned.
    node_sibling : AST
        Sibling node to copy source code metadata from.

    Returns
    -------
    Name
        Name node assigning this attribute in the current lexical scope.
    '''
    assert isinstance(name, str), f'{repr(name)} not string.'

    # Child node assigning this attribute in the current lexical scope.
    node_name = Name(name, ctx=NODE_CONTEXT_STORE)

    # Copy all source code metadata (e.g., line numbers) from this sibling node
    # onto this child node.
    copy_node_metadata(node_src=node_sibling, node_trg=node_name)

    # Return this child node.
    return node_name
