#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype **beforelist trackers** (i.e., low-level mixins managing the beforelist
automating decorator positioning for :mod:`beartype.claw` import hooks).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ TODO                               }....................
#FIXME: Unit test the newly defined
#"BeartypeDecorationPosition.LAST_BEFORELIST" position, please.
#FIXME: Once unit-tested, enable that position by default *FOR FUNCTIONS ONLY.*
#It's currently pointless for types. *shrug*

#FIXME: Additionally handle:
#* Absolute imports (e.g., "import problem_package"). This will require a new
#  visite_Import() method altogether. *sigh*
#* Import aliases (e.g., "from problem_package import problem_decor as ohboy").

#FIXME: Handle user-defined beforelists via the "self._conf" instance
#variable, please. *sigh*

# ....................{ IMPORTS                            }....................
from ast import (
    AST,
    Call,
    ClassDef,
    ImportFrom,
    Name,
    # alias,
    expr,
)
from beartype.claw._ast._scope.clawastscope import BeartypeNodeScope
from beartype.roar import BeartypeClawImportConfException
# from beartype.typing import Union
from beartype._conf.confmain import BeartypeConf
from beartype._conf.confcommon import BEARTYPE_CONF_DEFAULT
from beartype._conf.confenum import BeartypeDecorationPosition
from beartype._data.api.standard.dataast import NODE_CONTEXT_LOAD
from beartype._data.claw.dataclawmagic import BEARTYPE_DECORATOR_FUNC_NAME
from beartype._data.kind.datakindmap import FROZENDICT_EMPTY
from beartype._data.typing.datatyping import (
    NodeDecoratable,
    NodeVisitResult,
)
from beartype._util.ast.utilastmunge import copy_node_metadata

# ....................{ SUBCLASSES                         }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# CAUTION: To improve forward compatibility with the superclass API over which
# we have *NO* control, avoid accidental conflicts by suffixing *ALL* private
# and public attributes of this subclass by "_beartype".
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

class BeartypeNodeTransformerImportMixin(object):
    '''
    Beartype **beforelist tracker** (i.e., visitor pattern recursively
    tracking imports of problematic third-party decorators as well as the
    modules and types providing such decorators across *all* import statements
    in the AST tree passed to the :meth:`visit` method of the
    :class:`beartype.claw._ast.clawastmain.BeartypeNodeTransformer` subclass
    also subclassing this mixin).

    This tracker manages the **beartype decorator beforelist** (i.e., collection
    of data structures deciding where the :func:`beartype.beartype` decorator
    should be applied in chains of one or more third-party decorators decorating
    callables and types). This tracker detects third-party decorators well-known
    to be **decorator-hostile** (i.e., decorators hostile to other decorators by
    prematurely terminating decorator chaining such that *no* decorators may
    appear above those decorators in any chain of one or more decorators).
    '''

    # ..................{ VISITORS                           }..................
    def visit_ImportFrom(self, node: ImportFrom) -> NodeVisitResult:
        '''
        Track the passed **import-from node** (i.e., node signifying the
        importation of an attribute from a module or package) if this node
        signifies an import of either:

        * A decorator-hostile decorator.
        * A module defining one or more decorator-hostile decorators.
        * A type defining one or more decorator-hostile decorators.

        Parameters
        ----------
        node : ImportFrom
            Possibly problematic import-from node to be tracked.

        Returns
        -------
        NodeVisitResult
            The passed import-from node unmodified.
        '''

        # ..................{ PREAMBLE                       }..................
        # Recursively transform *ALL* child nodes of this parent node.
        self.generic_visit(node)  # type: ignore[attr-defined]

        # ..................{ LOCALS                         }..................
        # Fully-qualified name of the external module being imported from if any
        # *OR* "None".
        #
        # Note that this name should *NEVER* be "None". Nonetheless, mypy claims
        # this name can actually be "None". How, mypy? Even mypy has no idea. To
        # squelch complaints from mypy, we pretend mypy is still sane.
        import_module_name = node.module
        if not import_module_name: return node  # <-- *SILENCE, MYPY!*

        # Metadata describing the current lexical scope being recursively
        # visited by this AST transformer.
        scope: BeartypeNodeScope = self._scopes[-1]  # type: ignore[attr-defined]

        # If this import statement does *NOT* import from a third-party module
        # known to define decorator-hostile decorators, this import statement is
        # ignorable with respect to @beartype. In this case, silently reduce to
        # a noop by returning this node unmodified.
        if import_module_name not in scope.beforelist.module_names:
            return node
        # Else, this import statement imports from a third-party module known to
        # define decorator-hostile decorators.

        # Set-like chain map of the unqualified basename of each
        # decorator-hostile decorator function defined by this third-party
        # module if any *OR* "None" otherwise.
        func_decorator_names = (
            scope.beforelist.module_to_func_decorator_names.get(
                import_module_name))

        # Nested dictionary mapping from the unqualified basename of each type
        # defined by this third-party module to a set-like chain map of the
        # unqualified basename of each decorator-hostile decorator method
        # defined by that type if any *OR* "None" otherwise.
        type_to_method_decorator_names = (
            scope.beforelist.module_to_type_to_method_decorator_names.get(
                import_module_name))

        # ..................{ SEARCH                         }..................
        # For each "ast.alias" node encapsulating the one or more attributes
        # being imported from that module by this import statement...
        for import_attr_alias in node.names:
            # Unqualified basename of this attribute if any *OR* "None".
            #
            # Note that this name should *NEVER* be "None". Yet, mypy claims
            # this name can actually be "None". How, mypy? Even mypy has no
            # idea. To squelch mypy complaints, we pretend mypy is still sane.
            import_attr_name = import_attr_alias.name
            if not import_attr_name: continue  # <-- *SILENCE, MYPY!*

            #FIXME: Handle "import_attr_alias.asname" too, please. Note that
            #"asname" is "None" if undefined, according to the official
            #"ast" documentation. *sigh*

            # If...
            if (
                # That module defines one or more decorator-hostile decorator
                # functions *AND*...
                func_decorator_names and
                # The unqualified basename of this attribute is that of a
                # decorator-hostile decorator function in that module...
                import_attr_name in func_decorator_names
            ):
                #FIXME: [SPEED] Inefficient. This permutes both chain maps,
                #when we actually only need to permute the
                #"module_to_func_decorator_names" chain map. This could
                #presumably be optimized by passing a new optional
                #"is_permute_module_to_func_decorator_names", which defaults
                #to false. It's fine for now. Fine, we say! *shrug*

                # Render this scope's beforelist safe for modification if this
                # beforelist is *NOT* yet safely modifiable.
                scope.permute_beforelist_if_needed()

                # New nested set-like chain map of the unqualified basename of
                # each decorator-hostile decorator function defined by that
                # module accessible in this scope.
                #
                # Ideally, this set-like data structure would be a "ChainSet"
                # rather than a "ChainMap". Since Python currently lacks a
                # "ChainSet", we abuse the "ChainMap" to construct a
                # "ChainSet"-like data structure such that:
                # * The keys of this chain map are the desired basenames.
                # * The values of this chain map are ignorable.
                #
                # Mapping to a nested chain map allows us to now efficiently
                # permute this nested chain map rather than laboriously
                # searching up the hierarchy of existing scopes for a relevant
                # "module_to_func_decorator_names" entry. To do so safely, we
                # "new child" this nested chain map first to avoid modifying
                # this parent nested chain map.
                func_decorator_names_new = func_decorator_names.new_child()

                # Add the unqualified basename of this decorator-hostile
                # decorator function to this set-like chain map, mapped to an
                # ignorable value.
                func_decorator_names_new[import_attr_name] = None  # <-- arbitrary value

                # Map the fully-qualified name of this scope to this nested
                # set-like chain map of the unqualified basenames of all
                # decorator-hostile decorator functions in this scope.
                scope.beforelist.module_to_func_decorator_names[
                    scope.name] = func_decorator_names_new

                # Add the fully-qualified name of this scope to the set of the
                # fully-qualified names of all scopes known to define
                # decorator-hostile decorators.
                scope.beforelist.module_names.add(scope.name)
            # Else, either that module defines no decorator-hostile decorator
            # functions *OR* the unqualified basename of this attribute is *NOT*
            # that of a decorator-hostile decorator function in that module. In
            # either case, this import is ignorable with respect to decorator
            # functions.
            #
            # If...
            elif (
                # That module defines one or more types defining one or more
                # decorator-hostile decorator methods *AND*...
                type_to_method_decorator_names and
                # The unqualified basename of this attribute is that of such a
                # type...
                import_attr_name in type_to_method_decorator_names
            ):
                #FIXME: Implement us up, please. Urgh!
                pass
            # Else, either that module defines no types defining
            # decorator-hostile decorator methods *OR* the unqualified basename
            # of this attribute is that of such a type. In either case, this
            # import is ignorable with respect to @beartype.

        # ..................{ RETURN                         }..................
        # Return this node unmodified.
        return node

    # ....................{ PRIVATE ~ decorators           }....................
    #FIXME: Revise docstring, please. This method now employs a highly
    #non-trivial algorithm to decide the correct @beartype decorator position in
    #a chain of one or more existing non-@beartype decorators.
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

        # ....................{ NODES                      }....................
        # Child decoration node decorating this parent type or callable node by
        # the @beartype decorator.
        node_beartype_decorator: expr = Name(
            id=BEARTYPE_DECORATOR_FUNC_NAME, ctx=NODE_CONTEXT_LOAD)

        # Copy all source code metadata from this parent type or callable node
        # onto this child decorator node.
        copy_node_metadata(node_src=node, node_trg=node_beartype_decorator)

        # ....................{ NODES ~ conf               }....................
        #FIXME: Isn't this pretty much *ALWAYS* the case? "beartype.claw" import
        #hooks apply a non-default beartype configuration by default, sadly.
        # If the current beartype configuration is *NOT* the default beartype
        # configuration, this configuration is a user-defined beartype
        # configuration which *MUST* be passed to a call to the @beartype
        # decorator. Merely referencing this decorator does *NOT* suffice. In
        # this case...
        if conf != BEARTYPE_CONF_DEFAULT:
            # Replace the reference to this decorator defined above with a call
            # to this decorator passed this configuration.
            node_beartype_decorator = Call(
                func=node_beartype_decorator,
                args=[],
                # Node encapsulating the passing of this configuration as the
                # "conf" keyword argument to this call.
                keywords=[self._make_node_keyword_conf(node_sibling=node)],  # type: ignore[attr-defined]
            )

            # Copy all source code metadata from this parent callable node onto
            # this child call node.
            copy_node_metadata(node_src=node, node_trg=node_beartype_decorator)
        # Else, this configuration is simply the default beartype configuration.
        # In this case, avoid passing that configuration to the @beartype
        # decorator for both efficiency and simplicity.

        # ....................{ POSITION                   }....................
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

        # If injecting the @beartype decorator contextually last, insert this
        # child decoration node immediately *BEFORE* the first existing child
        # decoration node encapsulating a decorator-hostile decorator externally
        # configured by the beforelist and previously detected by the
        # visit_Import*() family of methods defined above.
        #
        # Note that:
        # * This is the default position and thus detected first.
        # * The "node.decorator_list" list of nodes describing the chain of all
        #   existing decorators decorating this type or callable is "stored
        #   outermost first (i.e. the first in the list will be applied last)."
        if decoration_position is (
            BeartypeDecorationPosition.LAST_BEFORELIST):
            self._decorate_node_beartype_last_beforelist(
                node=node, conf=conf, node_beartype_decorator=node_beartype_decorator)
        # If injecting the @beartype decorator unconditionally last, prepend
        # this child decoration node to the beginning of the list of all child
        # decoration nodes for this parent decoratable node. Prepending
        # guarantees that our decorator will be applied last (i.e., *AFTER* all
        # subsequent decorators).
        elif decoration_position is BeartypeDecorationPosition.LAST:
            node.decorator_list.insert(0, node_beartype_decorator)
        # If injecting the @beartype decorator unconditionally first, append
        # this child decoration node to the end of the list of all child
        # decoration nodes for this parent decoratable node.
        elif decoration_position is BeartypeDecorationPosition.FIRST:
            node.decorator_list.append(node_beartype_decorator)
        # Else, an unrecognized decorator position was configured. In this case,
        # raise an exception. Note that this should *NEVER* occur.
        else:  # pragma: no cover
            raise BeartypeClawImportConfException(
                f'Beartype configuration {repr(conf)} '
                f'decorator position {repr(decoration_position)} unsupported.'
            )


    #FIXME: Docstring us up, please.
    def _decorate_node_beartype_last_beforelist(
        self,
        node: NodeDecoratable,
        conf: BeartypeConf,
        node_beartype_decorator: expr,
    ) -> None:
        '''
        Add a new child :func:`beartype.beartype` decoration node to the passed
        parent decoratable node subject to
        :attr:`BeartypeDecorationPosition.LAST_BEFORELIST` positioning.

        This method contextually injects the :func:`beartype.beartype` decorator
        as high (i.e., late) in the chain of decorators decorating the type
        or callable encapsulated by this parent decoratable node as feasible
        while still preserving compatibility with decorator-hostile decorators.
        To do so, this method injects this decorator immediately *before* the
        lowest (i.e., earliest) decorator-hostile decorator decorating this type
        or callable as externally configured by the beforelist and previously
        detected by the ``visit_Import*()`` family of methods defined above.

        Parameters
        ----------
        node : AST
            **Decoratable node** (i.e., parent type or callable node) to add a
            new child beartype decoration node to.
        conf : BeartypeConf
            **Beartype configuration** (i.e., dataclass configuring the
            :mod:`beartype.beartype` decorator for some decoratable object(s)
            decorated by a parent node passing this dataclass to that
            decorator).
        node_beartype_decorator : expr
            Child decoration node decorating this parent type or callable node
            by the :func:`beartype.beartype` decorator.
        '''
        assert isinstance(node_beartype_decorator, expr), (
            f'{repr(node_beartype_decorator)} not AST expression node.')

        # ..................{ LOCALS                         }..................
        # Metadata describing the current lexical scope being recursively
        # visited by this AST transformer.
        scope: BeartypeNodeScope = self._scopes[-1]  # type: ignore[attr-defined]

        # Fully-qualified name of this scope, localized for both readability and
        # as a negligible microoptimization. *sigh*
        module_name = scope.name

        # If either...
        #
        # Note that this is the common case. Since undecorated types and
        # callables *AND* decorator-hostile decorators are all the exception
        # rather than the rule, optimizing for this common case is both
        # desirable and useful.
        if (
            # The currently visited type or callable being decorated by the
            # @beartype decorator is currently undecorated *OR*...
            not node.decorator_list or
            # This type or callable is decorated.
            #
            # The currently visited module imports from *NO* other module known
            # to define one or more decorator-hostile decorators...
            module_name not in scope.beforelist.module_names
        ):
            # Then this type or callable is decorated by *NO* decorator-hostile
            # decorators. In this case, the @beartype decorator may be safely
            # injected as the last decorator in the chain of decorators
            # decorating this type or callable.

            # Reduce to the implementation of the
            # "BeartypeDecorationPosition.LAST" position in the parent
            # _decorate_node_beartype() method.
            node.decorator_list.insert(0, node_beartype_decorator)

            # Halt further processing.
            return
        # Else, this type or callable is decorated *AND* the currently visited
        # module imports from one or more other modules known to define one or
        # more decorator-hostile decorators.

        # Set-like chain map of the unqualified basename of each
        # decorator-hostile decorator function defined by this third-party
        # module if any *OR* the empty frozen dictionary otherwise.
        func_decorator_names = (
            scope.beforelist.module_to_func_decorator_names.get(
                module_name, FROZENDICT_EMPTY))

        #FIXME: Actually consider this mapping below, please. *sigh*
        # # Nested dictionary mapping from the unqualified basename of each type
        # # defined by this third-party module to a set-like chain map of the
        # # unqualified basename of each decorator-hostile decorator method
        # # defined by that type if any *OR* the empty frozen dictionary otherwise.
        # type_to_method_decorator_names = (
        #     scope.beforelist.module_to_type_to_method_decorator_names.get(
        #         module_name, FROZENDICT_EMPTY))

        # ..................{ SEARCH                         }..................
        # For the 0-based index of each child node encapsulating an existing
        # decorator in the chain of all decorators decorating this type or
        # callable *AND* that child node (in descending order of the last to
        # first such decorator)...
        #
        # With respect to AST transformations, there exist four kinds of
        # decorations (in order of increasing complexity). This method *MUST*
        # transparently support each of these kinds:
        # * An unqualified attribute decoration of the form
        #   "@{decorator_name}", encapsulated by a simple "ast.Name" node.
        # * A qualified attribute decoration of the form
        #   "@{module_or_type_name}.{decorator_name}", encapsulated by a less
        #   simple "ast.Attribute" node.
        # * A callable call decoration encapsulating either:
        #   * An unqualified attribute decoration of the form
        #     "@{decorator_name}(...)", encapsulated by a complex
        #     "ast.Call(func=Name(...), ...)" node.
        #   * A qualified attribute decoration of the form
        #     "@{decorator_name}(...)", encapsulated by an even more complex
        #     "ast.Call(func=Attribute(...), ...)" node.
        #
        # Consider this minimal-length example:
        #
        #     @beartype
        #     @beartype.beartype
        #     @beartype(conf=BeartypeConf(is_debug=True))
        #     @beartype.beartype(conf=BeartypeConf(is_debug=True))
        #     def muh_fun(): pass
        #
        # ...which is encapsulated by this AST:
        #     FunctionDef(
        #       name='muh_fun',
        #       args=arguments(),
        #       body=[
        #           Pass()],
        #       decorator_list=[
        #           Name(id='beartype', ctx=Load()),
        #           Attribute(
        #               value=Name(id='beartype', ctx=Load()),
        #               attr='beartype',
        #               ctx=Load()),
        #           Call(
        #               func=Name(id='beartype', ctx=Load()),
        #               keywords=[
        #                   keyword(
        #                       arg='conf',
        #                       value=Call(
        #                           func=Name(id='BeartypeConf', ctx=Load()),
        #                           keywords=[
        #                               keyword(
        #                                   arg='is_debug',
        #                                   value=Constant(value=True))]))]),
        #           Call(
        #               func=Attribute(
        #                   value=Name(id='beartype', ctx=Load()),
        #                   attr='beartype',
        #                   ctx=Load()),
        #               keywords=[
        #                   keyword(
        #                       arg='conf',
        #                       value=Call(
        #                           func=Name(id='BeartypeConf', ctx=Load()),
        #                           keywords=[
        #                               keyword(
        #                                   arg='is_debug',
        #                                   value=Constant(value=True))]))])])])
        node_decorator_index = 0  # <-- for safety, but probably unneeded
        for node_decorator_index, node_decorator in enumerate(
            node.decorator_list):
            # If this decoration is encapsulated by a simple "ast.Name" node,
            # this is an unqualified attribute decoration of the form
            # "@{decorator_name}". In this case...
            if isinstance(node_decorator, Name):
                # If the unqualified basename of this decorator is *NOT* that of
                # a decorator-hostile decorator previously imported into the
                # currently visited module, this decorator is presumably
                # compatible with the @beartype decorator. In this case, halt!
                if node_decorator.id not in func_decorator_names:
                    break
                # Else, the unqualified basename of this decorator is that of a
                # decorator-hostile decorator previously imported into the
                # currently visited module. In this case, continue searching.
            # Else, this decoration is *NOT* encapsulated by an "ast.Name" node.
            #
            # If...

            #FIXME: Finish us up, please. *sigh*

        # Inject the @beartype decorator the last decorator *BEFORE* (i.e.,
        # below) the last decorator-hostile decorator in the chain of existing
        # decorators decorating this type or callable.
        node.decorator_list.insert(
            node_decorator_index, node_beartype_decorator)
