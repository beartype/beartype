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
    Attribute,
    Name,
    dump as ast_dump,
)
from beartype.typing import Optional
from beartype._data.typing.datatyping import (
    ListStrs,
    NodeAttrName,
)

# ....................{ GETTERS ~ str                      }....................
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


#FIXME: Unit test us up, please.
def get_node_attr_basenames(
    # Mandatory parameters.
    node: NodeAttrName,

    # Optional parameters.
    attr_basenames: Optional[ListStrs] = None,
) -> ListStrs:
    '''
    List of the one or more unqualified basenames comprising the possibly
    fully-qualified ``"."``-delimited name of the passed **attribute name node**
    (i.e., :class:`ast.Name` node *or* hierarchical nesting of one or more
    :class:`ast.Attribute` nodes terminating in a :class:`ast.Name` node) if
    this node is parsable by this getter *or* the empty list otherwise (i.e., if
    this node is unparsable by this getter).

    This getter recursively "unparses" (i.e., decompiles) the hierarchically
    nested contents of this node, albeit without actually employing recursion.
    This getter instead internally iterates over a list of the one or more
    unqualified basenames comprising this name, enabling this iteration to
    reconstruct this name.

    A list is required, as the AST grammar hierarchically nests zero or more
    :class:`.Attribute` nodes encapsulating this name in the *reverse* order of
    the expected nesting. Specifically, an attribute name qualified by N number
    of ``"."``-delimited substrings (where N >= 3) is encapsulated by a
    hierarchical nesting of N-1 :class:`.Attribute` nodes followed by 1
    :class:`.Name` node: e.g.,

    .. code-block:: python

       @package.module.submodule.decorator
       def muh_fun(): pass

    ...which is encapsulated by this AST:

    .. code-block:: python

       FunctionDef(
           name='muh_fun',
           args=arguments(),
           body=[
               Pass()],
           decorator_list=[
               Attribute(
                   value=Attribute(
                       value=Attribute(
                           value=Name(id='package', ctx=Load()),
                           attr='module',
                           ctx=Load()),
                       attr='submodule',
                       ctx=Load()),
                   attr='decorator',
                   ctx=Load()),
           ])

    That is, the :class:`.attr` instance variable of the *outermost*
    :class:`Attribute` node yields the *last* ``"."``-delimited substring of the
    fully-qualified name of that decorator. This reconstruction algorithm thus
    resembles Reverse Polish Notation, for those familiar with ancient
    calculators that no longer exist. So, nobody.

    Parameters
    ----------
    node : NodeAttrName
        Attribute name node to be unparsed.
    attr_basenames : Optional[ListStrs], default: None
        Existing caller-defined list to be efficiently cleared, reused, and
        returned by this getter if any *or* :data:`None` otherwise, in which
        case this getter instantiates and returns a new list.

    Returns
    -------
    str
        Fully-qualified name *or* unqualified basename of this name node.
    '''
    assert isinstance(node, AST), f'{repr(node)} not AST.'

    # If the caller explicitly passed *NO* pre-initialized list, initialize this
    # to the empty list.
    if attr_basenames is None:
        attr_basenames = []
    # Else, the caller explicitly passed a pre-initialized list. In this case...
    else:
        assert isinstance(attr_basenames, list), (
            f'{repr(attr_basenames)} not list.')

        # Clear this list.
        attr_basenames.clear()
    # In either case, this local variable is now the empty list.

    # While the next unqualified basename name comprising this name is still
    # encapsulated by an "Attribute" node...
    #
    # Note that the AST grammar hierarchically nests "Attribute" nodes in the
    # *REVERSE* of the expected nesting. That is, the "attr" instance variable
    # of the *OUTERMOST* "Attribute" node yields the *LAST* "."-delimited
    # substring of the fully-qualified name of this attribute. This
    # reconstruction algorithm thus resembles Reverse Polish Notation, for those
    # familiar with ancient calculators that no longer exist. So, nobody.
    while isinstance(node, Attribute):
        # Append the unqualified basename of this parent submodule of this
        # attribute encapsulated by this "Attribute" child node to this list.
        #
        # Note that, as described above, "Attribute" child nodes are
        # hierarchically nested in the reverse of the expected order. In theory,
        # this basename should be *PREPENDED* rather than *APPENDED* to produce
        # the partially-qualified name of this decorator. In practice, doing so
        # is inefficient. Why? Because:
        # * List appending exhibits average-time O(1) constant-time complexity.
        # * List prepending exhibits average-time O(n) linear-time complexity.
        #
        # This algorithm thus prefers appending, which then necessitates this
        # list be reversed after algorithm termination. It's a small price to
        # pay for a substantial optimization.
        attr_basenames.append(node.attr)

        # Unwrap one hierarchical level of this "Attribute" parent node into its
        # next "Attribute" or "Name" child node.
        node = node.value  # type: ignore[assignment]
    # Else, this name is *NOT* encapsulated by an "Attribute" node.

    #FIXME: Also handle "ast.Subscript" nodes produce by statements resembling:
    #    muh_object.muh_var[muh_index]

    # If the trailing unqualified basename of this attribute is encapsulated by
    # a "Name" node...
    if isinstance(node, Name):
        # Append this trailing unqualified basename to this list.
        attr_basenames.append(node.id)
    # Else, the trailing unqualified basename of this attribute is *NOT*
    # encapsulated by a "Name" node.
    #
    # Note that this should *NEVER* happen. All attribute names should be
    # encapsulated by either "Attribute" or "Name" nodes. However, the Python
    # language and hence AST grammar describing that language is constantly
    # evolving. Since this just happened, it is likely that a future iteration
    # of the Python language has now evolved in an unanticipated (yet,
    # ultimately valid) way. To preserve forward compatibility in @beartype with
    # future Python versions, intentionally ignore this unknown AST node type.
    #
    # Sometimes, doing nothing at all is the best thing you can do.

    # List of the one or more unqualified basenames comprising the possibly
    # partially-qualified name encapsulated by this node, albeit in the expected
    # non-reversed order.
    #
    # Note that this one-liner has been profiled to be slightly faster than the
    # comparable reversed() builtin. See also:
    #     https://www.geeksforgeeks.org/python/python-reversed-vs-1-which-one-is-faster
    attr_basenames = attr_basenames[::-1]

    # Return this non-reversed list.
    return attr_basenames
