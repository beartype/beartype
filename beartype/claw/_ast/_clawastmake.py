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
    Constant,
    ImportFrom,
    Name,
    Subscript,
    alias,
    # expr,
    keyword,
)
# from beartype.typing import (
#     List,
#     Optional,
#     Union,
# )
from beartype.claw._ast._clawastmagic import (
    NODE_CONTEXT_LOAD,
)
from beartype.claw._ast._clawastmunge import copy_node_metadata
from beartype._conf.confcls import BeartypeConf

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
        Sibling node to copy source code metadata from.

    Returns
    ----------
    ImportFrom
        Import-from node importing this attribute from this module.
    '''
    assert isinstance(module_name, str), f'{repr(module_name)} not string.'
    assert isinstance(attr_name, str), f'{repr(attr_name)} not string.'

    # Node encapsulating the name of the attribute to import from this module.
    node_importfrom_name = alias(attr_name)

    # Node encapsulating the name of the module to import this attribute from.
    node_importfrom = ImportFrom(
        module=module_name, names=[node_importfrom_name])

    # Copy all source code metadata (e.g., line numbers) from this sibling node
    # onto these new nodes.
    copy_node_metadata(
        node_src=node_sibling, node_trg=(node_importfrom, node_importfrom_name))

    # Return this import-from node.
    return node_importfrom


#FIXME: Unit test us up, please.
def make_node_keyword_conf(conf: BeartypeConf, node_sibling: AST) -> keyword:
    '''
    Create and return a new **beartype configuration abstract syntax tree (AST)
    node** (i.e., node passing the passed configuration as a ``conf`` keyword to
    a :mod:`beartype` function orchestrated by the caller).

    Parameters
    ----------
    conf : BeartypeConf
        **Beartype configuration** (i.e., dataclass configuring the
        :mod:`beartype.beartype` decorator for some decoratable object(s)
        decorated by a parent node passing this dataclass to that decorator).
    node_sibling : AST
        Sibling node to copy source code metadata from.

    Returns
    ----------
    keyword
        Keyword node passing this configuration to an arbitrary function.
    '''
    assert isinstance(conf, BeartypeConf), f'{repr(conf)} not configuration.'

    # Object identifier uniquely identifying this configuration.
    conf_id = id(conf)

    # Node encapsulating this object identifier as a literal integer constant.
    node_conf_id = Constant(value=conf_id)

    # Node encapsulating a reference to the beartype configuration object cache
    # (i.e., dictionary mapping from object identifiers to the beartype
    # configurations with those identifiers).
    node_conf_id_to_conf = Name(
        id='beartype_conf_id_to_conf', ctx=NODE_CONTEXT_LOAD)

    # Node encapsulating a reference to this beartype configuration, indirectly
    # (and efficiently) accessed via a dictionary lookup into this object cache.
    # While cumbersome, this indirection is effectively "glue" integrating this
    # AST node generation algorithm with the corresponding Python code
    # subsequently interpreted by Python at runtime during module load.
    node_conf = Subscript(
        value=node_conf_id_to_conf,
        slice=node_conf_id,
        ctx=NODE_CONTEXT_LOAD,
    )

    # Node encapsulating the passing of this beartype configuration by the
    # "conf" keyword argument to an arbitrary function call of some suitable
    # "beartype" function orchestrated by the caller.
    node_keyword_conf = keyword(arg='conf', value=node_conf)

    # Copy all source code metadata (e.g., line numbers) from this sibling node
    # onto these new nodes.
    copy_node_metadata(
        node_src=node_sibling,
        node_trg=(
            node_conf_id,
            node_conf_id_to_conf,
            node_conf,
            node_keyword_conf,
        )
    )

    # Return this "conf" keyword node.
    return node_keyword_conf
