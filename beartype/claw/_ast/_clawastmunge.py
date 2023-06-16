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
    Name,
    expr,
)
from beartype.claw._clawmagic import (
    NODE_CONTEXT_LOAD,
    BEARTYPE_DECORATOR_ATTR_NAME,
)
from beartype.claw._clawtyping import (
    NodeDecoratable,
)
from beartype.typing import (
    Iterable,
    Union,
)
from beartype._conf.confcls import (
    BEARTYPE_CONF_DEFAULT,
    BeartypeConf,
)
from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_8

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

    # Avoid circular import dependencies.
    from beartype.claw._ast._clawastmake import make_node_keyword_conf

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
            keywords=[make_node_keyword_conf(conf=conf, node_sibling=node)],
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

# ....................{ COPIERS                            }....................
#FIXME: Unit test us up, please.
def copy_node_metadata(
    node_src: AST,
    node_trg: Union[AST, Iterable[AST]],
) -> None:
    '''
    Copy all **source code metadata** (i.e., beginning and ending line and
    column numbers) from the passed source abstract syntax tree (AST) node onto
    the passed target AST node(s).

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
    node_trg : Union[AST, Iterable[AST]]
        Either:

        * A single target AST node to copy source code metadata onto.
        * An iterable of zero or more target AST nodes to copy source code
          metadata onto.

    See Also
    ----------
    :func:`ast.copy_location`
        Less efficient analogue of this function running in ``O(k)`` time
        complexity for ``k`` the number of types of source code metadata.
        Typically, ``k == 4``.
    '''
    assert isinstance(node_src, AST), f'{repr(node_src)} not AST node.'

    # If passed only a single target node, wrap this node in a 1-tuple
    # containing only this node for simplicity.
    if isinstance(node_trg, AST):
        node_trg = (node_trg,)
    # In either case, "node_trg" is now an iterable of target nodes.

    # For each passed target node...
    for node_trg_cur in node_trg:
        assert isinstance(node_trg_cur, AST), (
            f'{repr(node_trg_cur)} not AST node.')

        # Copy all source code metadata from this source to target node.
        node_trg_cur.lineno     = node_src.lineno
        node_trg_cur.col_offset = node_src.col_offset

        # If the active Python interpreter targets Python >= 3.8, then also copy
        # all source code metadata exposed by Python >= 3.8.
        if IS_PYTHON_AT_LEAST_3_8:
            node_trg_cur.end_lineno     = node_src.end_lineno  # type: ignore[attr-defined]
            node_trg_cur.end_col_offset = node_src.end_col_offset  # type: ignore[attr-defined]
