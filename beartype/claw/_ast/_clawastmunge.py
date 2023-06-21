#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype **abstract syntax tree (AST) mungers** (i.e., low-level callables
modifying various properties of various nodes in the currently visited AST).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from ast import (
    AST,
    Call,
    Constant,
    Name,
    Subscript,
    expr,
    keyword,
)
from beartype.claw._clawmagic import (
    NODE_CONTEXT_LOAD,
    BEARTYPE_CONF_CACHE_ATTR_NAME,
    BEARTYPE_DECORATOR_ATTR_NAME,
)
from beartype.claw._clawtyping import (
    NodeDecoratable,
)
from beartype._conf.confcls import (
    BEARTYPE_CONF_DEFAULT,
    BeartypeConf,
)
from beartype._util.ast.utilastmunge import copy_node_metadata

# ....................{ DECORATORS                         }....................
#FIXME: Unit test us up, please.
def decorate_node(node: NodeDecoratable, conf: BeartypeConf) -> None:
    '''
    Add a new **child beartype decoration node** (i.e., abstract syntax tree
    (AST) node applying the :func:`beartype.beartype` decorator configured by
    the passed beartype configuration) to the passed **parent decoratable node**
    (i.e., AST node encapsulating the definition of a pure-Python object
    supporting decoration by one or more ``"@"``-prefixed decorations, including
    both pure-Python classes *and* callables).

    Note that this function **prepends** rather than appends this child
    decoration node to the beginning of the list of all child decoration nodes
    for this parent decoratable node. Since that list is "stored outermost first
    (i.e. the first in the list will be applied last)", prepending guarantees
    that the beartype decorator will be applied last (i.e., *after* all other
    decorators). This ensures that explicitly configured beartype decorations
    applied to this decoratable by the end user (e.g.,
    ``@beartype(conf=BeartypeConf(...))``) assume precedence over implicitly
    configured beartype decorations applied by this function.

    Parameters
    ----------
    node : AST
        Decoratable node to add a new child beartype decoration node to.
    conf : BeartypeConf
        **Beartype configuration** (i.e., dataclass configuring the
        :mod:`beartype.beartype` decorator for some decoratable object(s)
        decorated by a parent node passing this dataclass to that decorator).
    '''
    assert isinstance(node, AST), f'{repr(node)} not AST node.'
    assert isinstance(conf, BeartypeConf), f'{repr(conf)} not configuration.'

    # Child decoration node decorating that callable by our beartype decorator.
    beartype_decorator: expr = Name(
        id=BEARTYPE_DECORATOR_ATTR_NAME, ctx=NODE_CONTEXT_LOAD)

    # Copy all source code metadata from this parent callable node onto this
    # child decoration node.
    copy_node_metadata(node_src=node, node_trg=beartype_decorator)

    # If the current beartype configuration is *NOT* the default beartype
    # configuration, this configuration is a user-defined beartype configuration
    # which *MUST* be passed to a call to the beartype decorator. Merely
    # referencing this decorator does *NOT* suffice. In this case...
    if conf != BEARTYPE_CONF_DEFAULT:
        # Replace the reference to this decorator defined above with a
        # call to this decorator passed this configuration.
        beartype_decorator = Call(
            func=beartype_decorator,
            args=[],
            # Node encapsulating the passing of this configuration as
            # the "conf" keyword argument to this call.
            keywords=[make_node_keyword_conf(node_sibling=node)],
        )

        # Copy all source code metadata from this parent callable node onto this
        # child call node.
        copy_node_metadata(node_src=node, node_trg=beartype_decorator)
    # Else, this configuration is simply the default beartype configuration. In
    # this case, avoid passing that configuration to the beartype decorator for
    # both efficiency and simplicity.

    # Prepend this child decoration node to the beginning of the list of all
    # child decoration nodes for this parent callable node. Since this list is
    # "stored outermost first (i.e. the first in the list will be applied
    # last)", prepending guarantees that our decorator will be applied last
    # (i.e., *AFTER* all subsequent decorators). This ensures that explicitly
    # configured @beartype decorations (e.g.,
    # "beartype(conf=BeartypeConf(...))") assume precedence over implicitly
    # configured @beartype decorations inserted by this hook.
    node.decorator_list.insert(0, beartype_decorator)

# ....................{ FACTORIES                          }....................
#FIXME: Unit test us up, please.
def make_node_keyword_conf(node_sibling: AST) -> keyword:
    '''
    Create and return a new **beartype configuration keyword argument node**
    (i.e., abstract syntax tree (AST) node passing the beartype configuration
    associated with the currently visited module as a ``conf`` keyword to a
    :func:`beartype.beartype` decorator orchestrated by the caller).

    Parameters
    ----------
    node_sibling : AST
        Sibling node to copy source code metadata from.

    Returns
    ----------
    keyword
        Keyword node passing this configuration to an arbitrary function.
    '''

    # Node encapsulating the fully-qualified name of that module of the
    # currently visited module, accessed via the "__name__" dunder attribute
    # accessible to any module.
    node_module_name = Name(id='__name__', ctx=NODE_CONTEXT_LOAD)

    # Node encapsulating a reference to the beartype configuration object cache
    # (i.e., dictionary mapping from fully-qualified module names to the
    # beartype configurations associated with those modules).
    node_module_name_to_conf = Name(
        id=BEARTYPE_CONF_CACHE_ATTR_NAME, ctx=NODE_CONTEXT_LOAD)

    # Node encapsulating a reference to this beartype configuration, indirectly
    # (and efficiently) accessed via a dictionary lookup into this object cache.
    # While cumbersome, this indirection is effectively "glue" integrating this
    # AST node generation algorithm with the corresponding Python code
    # subsequently interpreted by Python at runtime during module importation.
    node_conf = Subscript(
        value=node_module_name_to_conf,
        slice=node_module_name,
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
            node_module_name,
            node_module_name_to_conf,
            node_conf,
            node_keyword_conf,
        )
    )

    # Return this "conf" keyword node.
    return node_keyword_conf
