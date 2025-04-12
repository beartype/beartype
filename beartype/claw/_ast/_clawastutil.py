#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
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
    ClassDef,
    Name,
    Subscript,
    expr,
    keyword,
)
from beartype.claw._clawmagic import (
    NODE_CONTEXT_LOAD,
    BEARTYPE_CLAW_STATE_OBJ_NAME,
    BEARTYPE_DECORATOR_FUNC_NAME,
)
from beartype.roar import BeartypeClawImportConfException
from beartype._conf.confmain import BeartypeConf
from beartype._conf.confcommon import BEARTYPE_CONF_DEFAULT
from beartype._conf.confenum import BeartypeDecorationPosition
from beartype._data.hint.datahinttyping import NodeDecoratable
from beartype._util.ast.utilastmake import (
    make_node_kwarg,
    make_node_object_attr_load,
    make_node_str,
)
from beartype._util.ast.utilastmunge import copy_node_metadata

# ....................{ SUBCLASSES                         }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# CAUTION: To improve forward compatibility with the superclass API over which
# we have *NO* control, avoid accidental conflicts by suffixing *ALL* private
# and public attributes of this subclass by "_beartype".
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

class BeartypeNodeTransformerUtilityMixin(object):
    '''
    **Beartype abstract syntax tree (AST) node utility transformer** (i.e.,
    low-level mixin of the high-level
    :class:`beartype.claw._ast.clawastmain.BeartypeNodeTransformer` subclass
    supplementing that subclass with various low-level methods creating,
    modifying, and introspecting common node types and subclass properties).
    '''

    # ....................{ PRIVATE ~ decorators           }....................
    #FIXME: Unit test us up, please.
    def _decorate_node_beartype(
        self, node: NodeDecoratable, conf: BeartypeConf) -> None:
        '''
        Add a new **child beartype decoration node** (i.e., abstract syntax tree
        (AST) node applying the :func:`beartype.beartype` decorator configured
        by the passed beartype configuration) to the passed **parent decoratable
        node** (i.e., AST node encapsulating the definition of a pure-Python
        object supporting decoration by one or more ``"@"``-prefixed
        decorations, including both pure-Python classes *and* callables).

        Note that this function **prepends** rather than appends this child
        decoration node to the beginning of the list of all child decoration
        nodes for this parent decoratable node. Since that list is "stored
        outermost first (i.e. the first in the list will be applied last)",
        prepending guarantees that the beartype decorator will be applied last
        (i.e., *after* all other decorators). This ensures that explicitly
        configured beartype decorations applied to this decoratable by the end
        user (e.g., ``@beartype(conf=BeartypeConf(...))``) assume precedence
        over implicitly configured beartype decorations applied by this
        function.

        Parameters
        ----------
        node : AST
            **Decoratable node** (i.e., parent class or callable node) to add a
            new child beartype decoration node to.
        conf : BeartypeConf
            **Beartype configuration** (i.e., dataclass configuring the
            :mod:`beartype.beartype` decorator for some decoratable object(s)
            decorated by a parent node passing this dataclass to that
            decorator).
        '''
        assert isinstance(node, AST), f'{repr(node)} not AST node.'
        assert isinstance(conf, BeartypeConf), (
            f'{repr(conf)} not configuration.')

        # Child decoration node decorating that callable by the @beartype
        # decorator.
        beartype_decorator: expr = Name(
            id=BEARTYPE_DECORATOR_FUNC_NAME, ctx=NODE_CONTEXT_LOAD)

        # Copy all source code metadata from this parent callable node onto this
        # child decoration node.
        copy_node_metadata(node_src=node, node_trg=beartype_decorator)

        # If the current beartype configuration is *NOT* the default beartype
        # configuration, this configuration is a user-defined beartype
        # configuration which *MUST* be passed to a call to the @beartype
        # decorator. Merely referencing this decorator does *NOT* suffice. In
        # this case...
        if conf != BEARTYPE_CONF_DEFAULT:
            # Replace the reference to this decorator defined above with a
            # call to this decorator passed this configuration.
            beartype_decorator = Call(
                func=beartype_decorator,
                args=[],
                # Node encapsulating the passing of this configuration as
                # the "conf" keyword argument to this call.
                keywords=[
                    self._make_node_keyword_conf_beartype(node_sibling=node)],
            )

            # Copy all source code metadata from this parent callable node onto
            # this child call node.
            copy_node_metadata(node_src=node, node_trg=beartype_decorator)
        # Else, this configuration is simply the default beartype configuration.
        # In this case, avoid passing that configuration to the @beartype
        # decorator for both efficiency and simplicity.

        # Decorator position (i.e., location to which the @beartype decorator
        # will be implicitly injected into the existing chain of zero or more
        # decorators already decorating this parent decoratable node), defined
        # as either...
        decoration_position = (
            # If this parent decoratable node is a parent class node, the
            # class-specific decorator position.
            conf.claw_decoration_position_types
            if isinstance(node, ClassDef) else
            # Else, this parent decoratable node is *NOT* a parent class node.
            # By process of elimination, this parent decoratable node *MUST* be
            # a parent callable node. In this case, fallback to the
            # callable-specific decorator position.
            conf.claw_decoration_position_funcs
        )

        # If injecting the @beartype decorator last, prepend this child
        # decoration node to the beginning of the list of all child decoration
        # nodes for this parent decoratable node. Since this list is "stored
        # outermost first (i.e. the first in the list will be applied last)",
        # prepending guarantees that our decorator will be applied last (i.e.,
        # *AFTER* all subsequent decorators).
        if decoration_position is BeartypeDecorationPosition.LAST:
            node.decorator_list.insert(0, beartype_decorator)
        # If injecting the @beartype decorator first, append this child
        # decoration node to the end of the list of all child decoration nodes
        # for this parent decoratable node.
        elif decoration_position is BeartypeDecorationPosition.FIRST:
            node.decorator_list.append(beartype_decorator)
        # Else, an unrecognized decorator position was configured. In this case,
        # raise an exception. Note that this should *NEVER* occur.
        else:  # pragma: no cover
            raise BeartypeClawImportConfException(
                f'Beartype configuration {repr(conf)} '
                f'decorator position {repr(decoration_position)} unsupported.'
            )

    # ....................{ PRIVATE ~ factories            }....................
    #FIXME: Unit test us up, please.
    def _make_node_keyword_conf_beartype(self, node_sibling: AST) -> keyword:
        '''
        Create and return a new **beartype configuration keyword argument node**
        (i.e., abstract syntax tree (AST) node passing the beartype
        configuration associated with the currently visited module as a ``conf``
        keyword to a :func:`beartype.beartype` decorator orchestrated by the
        caller).

        Parameters
        ----------
        node_sibling : AST
            Sibling node to copy source code metadata from.

        Returns
        -------
        keyword
            Keyword node passing this configuration to an arbitrary function.
        '''

        # Node encapsulating the fully-qualified name of the current module.
        node_module_name = make_node_str(
            text=self._module_name_beartype, node_sibling=node_sibling)  # type: ignore[attr-defined]

        # Node encapsulating a reference to the beartype configuration object
        # cache (i.e., dictionary mapping from fully-qualified module names to
        # the beartype configurations associated with those modules).
        node_module_name_to_conf = make_node_object_attr_load(
            obj_name=BEARTYPE_CLAW_STATE_OBJ_NAME,
            attr_name='module_name_to_beartype_conf',
            node_sibling=node_sibling,
        )

        node_module_name_index: expr = None  # type: ignore[assignment]

        # Expression node encapsulating the indexation of a dictionary by the
        # fully-qualified name of the current module. For simplicity, simply
        # reuse this node.
        node_module_name_index = node_module_name

        # Node encapsulating a reference to this beartype configuration,
        # indirectly (and efficiently) accessed via a dictionary lookup into
        # this object cache. While cumbersome, this indirection is effectively
        # "glue" integrating this AST node generation algorithm with the
        # corresponding Python code subsequently interpreted by Python at
        # runtime during module importation.
        node_conf = Subscript(
            value=node_module_name_to_conf,
            slice=node_module_name_index,  # type: ignore[arg-type]
            ctx=NODE_CONTEXT_LOAD,
        )

        # Node encapsulating the passing of this beartype configuration as the
        # "conf" keyword argument to an arbitrary function call of some suitable
        # "beartype" function orchestrated by the caller.
        node_keyword_conf = make_node_kwarg(
            kwarg_name='conf', kwarg_value=node_conf, node_sibling=node_sibling)

        # Copy all source code metadata (e.g., line numbers) from this sibling
        # node onto these new nodes.
        copy_node_metadata(node_src=node_sibling, node_trg=node_conf)

        # Return this "conf" keyword node.
        return node_keyword_conf

    # ..................{ PRIVATE ~ properties               }..................
    @property
    def _is_scope_module_beartype(self) -> bool:
        '''
        :data:`True` only if the lexical scope of the currently visited node is
        the **module scope** (i.e., this node is declared directly in the body
        of the current user-defined module, implying this node to be a global).

        Returns
        -------
        bool
            :data:`True` only if the current lexical scope is a module scope.
        '''

        # Return true only if the stack of all lexical nodes is currently empty,
        # implying the current node resides directly in the body of a module.
        return not self._scope_stack_beartype  # type: ignore[attr-defined]


    @property
    def _is_scope_class_beartype(self) -> bool:
        '''
        :data:`True` only if the lexical scope of the currently visited node is
        a **class scope** (i.e., this node resides directly in the body of a
        user-defined class).

        Returns
        -------
        bool
            :data:`True` only if the current lexical scope is a class scope.
        '''

        # Return true only if...
        return (
            # The stack of all lexical scope is currently non-empty *AND*...
            bool(self._scope_stack_beartype) and  # type: ignore[attr-defined]
            # The current node resides directly in the body of a class.
            self._scope_stack_beartype[-1] is ClassDef  # type: ignore[attr-defined]
        )
