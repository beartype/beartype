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
#"BeartypeDecorPlace.LAST_BEFORE_DECOR_HOSTILE" position, please.

#FIXME: Handle user-defined beforelists via the "self._conf" instance
#variable, please. *sigh*

# ....................{ IMPORTS                            }....................
from ast import (
    AST,
    Call,
    ClassDef,
    Import,
    ImportFrom,
    Name,
    alias,
    expr,
    unparse,
)
from beartype.claw._ast._scope.clawastscope import BeartypeNodeScope
# from beartype.claw._ast._scope.clawastscopebefore import ImportedAttrNameTrie
from beartype.roar import (
    BeartypeClawAstImportException,
    BeartypeClawImportConfException,
)
from beartype.typing import (
    Optional,
    Union,
)
from beartype._conf.confmain import BeartypeConf
from beartype._conf.confcommon import BEARTYPE_CONF_DEFAULT
from beartype._conf.decorplace.confplaceenum import BeartypeDecorPlace
from beartype._conf.decorplace.confplacetrie import (
    BeartypeDecorPlaceTrieABC,
    BeartypeDecorPlaceTypeTrie,
)
from beartype._data.api.standard.dataast import NODE_CONTEXT_LOAD
from beartype._data.conf.dataconfplace import (
    BeartypeDecorPlaceTrie,
    BeartypeDecorPlaceSubtrie,
)
from beartype._data.claw.dataclawmagic import BEARTYPE_DECORATOR_FUNC_NAME
from beartype._data.kind.datakindiota import (
    SENTINEL,
    Iota,
)
from beartype._data.kind.datakindmap import FROZENDICT_EMPTY
# from beartype._data.kind.datakindset import FROZENSET_EMPTY
from beartype._data.typing.datatyping import (
    ListStrs,
    NodeDecoratable,
    NodeVisitResult,
)
from beartype._util.ast.utilastget import (
    get_node_attr_basenames,
    get_node_repr_indented,
)
from beartype._util.ast.utilastmunge import copy_node_metadata
from beartype._util.kind.maplike.utilmapfrozen import FrozenDict

# ....................{ SUBCLASSES                         }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# CAUTION: To improve forward compatibility with the superclass API over which
# we have *NO* control, avoid accidental conflicts by suffixing *ALL* private
# and public attributes of this subclass by "_beartype".
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

class BeartypeNodeTransformerImportMixin(object):
    '''
    Beartype **decorator-hostile tracker** (i.e., visitor pattern recursively
    tracking imports of third-party decorator-hostile decorators as well as the
    modules and types defining such decorators across *all* import statements in
    the AST tree passed to the :meth:`visit` method of the
    :class:`beartype.claw._ast.clawastmain.BeartypeNodeTransformer` subclass
    also subclassing this mixin).

    This tracker manages the **beartype decorator beforelist** (i.e., collection
    of data structures deciding where the :func:`beartype.beartype` decorator
    should be applied in chains of one or more third-party decorators decorating
    callables and types). This tracker detects third-party decorators well-known
    to be **decorator-hostile** (i.e., decorators hostile to other decorators by
    prematurely terminating decorator chaining such that *no* decorators may
    appear above those decorators in any chain of one or more decorators).

    Attributes
    ----------
    _attr_basenames : Optional[list[str]]
        List of the one or more unqualified basenames comprising the possibly
        fully-qualified name of the current attribute being inspected (e.g.,
        decorator visited by iteration internally performed in the
        :def:`_decorate_node_beartype` method), enabling that inspection to
        reconstruct that name. Specifically, this is either:

        * If the low-level :func:`.get_node_attr_basenames` getter has yet to be
          called by a method of this mixin, :data:`None`.
        * Else, this list.
        '''

    # ..................{ INITIALIZERS                       }..................
    def __init__(self) -> None:
        '''
        Initialize this node transformer mixin.
        '''

        # Initialize our superclass.
        super().__init__()

        # Nullify all instance variables for safety.
        self._attr_basenames: Optional[ListStrs] = None

    # ..................{ MAPPERS                            }..................
    #FIXME: Call from these other mixin methods, please:
    #* The BeartypeNodeTransformerPep526Mixin.visit_AnnAssign() method.
    def map_type_imported_to_instance_if_decor_hostile(
        self, node_name_type: AST, node_name_instance: AST) -> None:
        '''
        Map the type (whose fully-qualified ``"."``-delimited name *or*
        unqualified basename is encapsulated by the first passed AST node)
        previously imported into the currently visited lexical scope of the
        currently visited module (whole name or basename is similarly
        encapsulated by the second passed AST node) to a new instance of that
        type in that scope of that module if that type is well-known to define
        one or more decorator-hostile decorator methods *or* silently reduce to
        a noop otherwise (i.e., if that type is unknown or unparseable as a
        simple reference to a type).

        This public method is intended to be called by external ``visit_*``
        methods of sibling mixins of the
        :class:`beartype.claw._ast.clawastmain.BeartypeNodeTransformer` class.
        Sibling mixins call this method to notify this decorator-hostile tracker
        of an instantiation of a third-party type known to define
        decorator-hostile decorator methods.

        Parameters
        ----------
        node_name_type : AST
            Node possibly encapsulating the fully-qualified name or unqualified
            basename of a previously imported type in an assignment statement.
        node_name_instance : AST
            Node possibly encapsulating the fully-qualified name or unqualified
            basename of a target instance of that type in an assignment
            statement.
        '''
        assert isinstance(node_name_type, AST), (
            f'{repr(node_name_type)} neither attribute nor name AST node.')
        assert isinstance(node_name_instance, AST), (
            f'{repr(node_name_instance)} neither attribute nor name AST node.')

        # Replace the contents of the existing "_attr_basenames" list with the
        # one or more unqualified basenames comprising the possibly
        # fully-qualified name of this type.
        get_node_attr_basenames(
            node=node_name_type, attr_basenames=self._attr_basenames)

        #FIXME: Implement us up, please.
        pass

    # ..................{ VISITORS                           }..................
    def visit_Import(self, node: Import) -> NodeVisitResult:
        '''
        Track the passed **import node** (i.e., node signifying the importation
        of a module or package) if this node signifies an import of a module or
        package defining one or more decorator-hostile decorators.

        Parameters
        ----------
        node : Import
            Possibly problematic import node to be tracked.

        Returns
        -------
        NodeVisitResult
            The passed import node unmodified.
        '''

        # ..................{ PREAMBLE                       }..................
        # Recursively transform *ALL* child nodes of this parent node.
        self.generic_visit(node)  # type: ignore[attr-defined]

        # ..................{ LOCALS                         }..................
        # Metadata describing the current lexical scope being recursively
        # visited by this AST transformer.
        scope: BeartypeNodeScope = self._scopes[-1]  # type: ignore[attr-defined]

        # ..................{ SEARCH                         }..................
        # For each child "alias" node of this parent "Import" node encapsulating
        # the fully-qualified names of the one or more modules being imported by
        # this import statement...
        for import_module_alias in node.names:
            # If this child node is *NOT* an "alias", silently skip this
            # unrecognized node type and continue to the next child node.
            #
            # Note that this should *NEVER* happen. All child nodes of parent
            # "Import" nodes should be aliases. For forward compatibility with
            # future Python versions, ignore this unrecognized node type. See
            # similar commentary below for further discussion.
            if not isinstance(import_module_alias, alias):
                continue
            # Else, this child node is an "alias".

            # Fully-qualified name of the external module or package being
            # imported if any *OR* "None".
            #
            # Note that this name should *NEVER* be "None". Nonetheless, mypy
            # claims this name can actually be "None". How, mypy? Even mypy has
            # no idea. To squelch complaints from mypy, we pretend mypy is sane.
            import_module_name = import_module_alias.name
            if not import_module_name: continue  # <-- *SILENCE, MYPY!*

            # Fully-qualified name of the top-level root package or module
            # transitively containing that package or module (e.g.,
            # "some_package" when "import_module_name" is
            # "some_package.some_module.some_submodule").
            #
            # This root package name is *MUCH* more relevant than the exact
            # submodule name (i.e., "import_module_name") imported by this
            # import statement. Why? Because trivial imports of the form "import
            # {package_name}" are similar to complex imports of the form "import
            # {package_name}.{submodule_name}.{attr_name}". In both cases,
            # Python only imports the top-level root package whose name is
            # "{package_name}" into the current lexical scope. For static
            # analysis purposes, trailing "."-prefixed substrings like
            # ".{submodule_name}.{attr_name}" are almost entirely irrelevant.
            # Consequently, all subsequent logic ignores "import_module_name" in
            # favour of this "import_package_name".
            #
            # Note this has been profiled to be the fastest one-liner parsing
            # the first "."-suffixed substring from a "."-delimited string.
            import_package_name = import_module_name.partition('.')[0]

            # If this import statement does *NOT* import a third-party package
            # known to define decorator-hostile decorators, this import
            # statement is ignorable with respect to @beartype. In this case,
            # silently skip this ignorable package by returning this node as is.
            if import_package_name not in (
                scope.beforelist.attested_module_names):
                return node
            # Else, this import statement imports a third-party module known to
            # define decorator-hostile decorators.

            # Decorator function beforelist unique to that package, defined as
            # a nested frozen dictionary mapping from strings to either the
            # "None" signifying a terminal leaf node *OR* yet another such
            # recursively nested frozen dictionary.
            attested_func_subtrie = (
                scope.beforelist.attested_attr_basename_trie.get(
                    import_package_name))

            # Map the unqualified basename of that package to this subtrie.
            scope.map_beforelist_imported_attr_basename_to_subtrie(
                attr_basename=import_package_name,
                attr_subtrie=attested_func_subtrie,
            )

        # ..................{ RETURN                         }..................
        # Return this node unmodified.
        return node


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

        # ..................{ LOCALS ~ module                }..................
        # Metadata describing the current lexical scope being recursively
        # visited by this AST transformer.
        scope: BeartypeNodeScope = self._scopes[-1]  # type: ignore[attr-defined]

        # Fully-qualified name of the external module being imported from if any
        # *OR* "None".
        #
        # Note that this name should *NEVER* be "None". Nonetheless, mypy claims
        # this name can actually be "None". How, mypy? Even mypy has no idea. To
        # squelch complaints from mypy, we pretend mypy is still sane.
        import_module_name = node.module
        if not import_module_name: return node  # <-- *SILENCE, MYPY!*

        # List of each unqualified basename comprising this name, split from
        # this fully-qualified name on "." delimiters.
        #
        # Note that:
        # * This list is guaranteed to be non-empty. Why? Because Python syntax
        #   prohibits empty import statements (e.g., "from import ugh\n").
        # * The "str.split('.')" and "str.rsplit('.')" calls produce the same
        #   lists under all edge cases. We arbitrarily call the former rather
        #   than the latter for simplicity.
        import_module_basenames = import_module_name.split('.')

        # Fully-qualified name of the top-level root package transitively
        # containing that module (e.g., "some_package" when "import_module_name"
        # is "some_package.some_module.some_submodule").
        import_package_name = import_module_basenames[0]

        # If this import statement does *NOT* import from a third-party package
        # known to define decorator-hostile decorators, this import statement is
        # ignorable with respect to @beartype. In this case, silently reduce to
        # a noop by returning this node unmodified.
        if import_package_name not in (
            scope.beforelist.attested_module_names):
            return node
        # Else, this import statement imports from a third-party package known
        # to define decorator-hostile decorators.

        # ..................{ SEARCH ~ module                }..................
        #FIXME: Revise commentary, please. *sigh*
        # Current and prior possibly nested decorator function beforelists being
        # iterated by the subsequent "while" loop. Specifically, each is either:
        # * If that package directly defines one or more decorator-hostile
        #   decorator functions, a frozen set of the unqualified basename of
        #   each decorator-hostile decorator function defined by that package.
        # * Else if only a submodule of that package directly defines one or
        #   more decorator-hostile decorator functions, yet another such
        #   recursively nested frozen dictionary of the same structure.
        # * Else, "None".
        attested_func_subtrie_parent = (
            scope.beforelist.attested_attr_basename_trie)
        attested_func_subtrie: Union[BeartypeDecorPlaceSubtrie, Iota] = None

        #FIXME: Revise commentary, please. *sigh*
        # Frozen set of the unqualified basename of each decorator-hostile
        # decorator function defined by that third-party module if any *OR* the
        # empty frozen dictionary otherwise.
        attested_funcs_subtrie: BeartypeDecorPlaceTrie = FROZENDICT_EMPTY

        # 0-based indices of the current and last unqualified basenames of the
        # fully-qualified name of the external module being imported from.
        import_module_basename_index_curr = 0
        import_module_basename_index_last = len(import_module_basenames)

        # While unqualified basenames of this name remain to be iterated...
        while (
            import_module_basename_index_curr <=
            import_module_basename_index_last
        ):
            # Current unqualified basename of this name.
            import_module_basename = import_module_basenames[
                import_module_basename_index_curr]

            #FIXME: Revise commentary, please. *sigh*
            # Unwrap the parent frozen dictionary against this unqualified
            # basename into either a nested frozen dictionary, nested frozen
            # set, or "None" (as detailed above).
            attested_func_subtrie = attested_func_subtrie_parent.get(
                import_module_basename, SENTINEL)

            #FIXME: Revise commentary, please. *sigh*
            # If this is a non-recursively nested frozen set, this set is
            # non-recursive and thus terminates this iteration. In this case...
            if attested_func_subtrie is None:
                #FIXME: Revise commentary, please. *sigh*
                # Localize this frozenset for subsequent lookup.
                attested_funcs_subtrie = attested_func_subtrie_parent

                # If this is the last unqualified basename of the
                # fully-qualified name of the external module being imported
                # from, *ALL* unqualified basenames of this name have now been
                # properly visited. In this, terminate this iteration by...
                if (
                    import_module_basename_index_curr ==
                    import_module_basename_index_last
                ):
                    # Immediately halt iteration.
                    break
                # Else, this is *NOT* the last unqualified basename of the
                # fully-qualified name of the external module being imported
                # from, then one or more unqualified basenames of this name
                # remain to be visited. But this set terminates this iteration,
                # preventing these basenames from being visited! This implies
                # the user to have improperly configured a "beartype.claw"
                # import hook with an erroneous beforelist specifying this
                # imported submodule to actually be a decorator-hostile
                # decorator. An object can be a decorator *OR* submodule -- but
                # not both.
                #
                # For example, this edge case arises if:
                # * A caller configures the beartype_this_package() hook with a
                #   beartype configuration resembling:
                #     beartype_this_package(BeartypeConf(
                #         attested_attr_basename_trie=FrozenDict({
                #             'bad_package': frozenset(('bad_submodule',)),})))
                # * One or more submodules of the caller's package import
                #   attributes from that submodule resembling:
                #       from bad_package.bad_submodule import bad_attribute

                # Pretty-printed representation of this import statement.
                node_repr = get_node_repr_indented(node)

                #FIXME: Revise exception message! See the comparable exception
                #raised below, please. *sigh*
                # Raise an explanatory exception.
                raise BeartypeClawAstImportException(
                    f'Beartype configuration {repr(self._conf)} '  # type: ignore[attr-defined]
                    f'decorator function beforelist '
                    f'{repr(scope.beforelist.attested_attr_basename_trie)} '
                    f'nested frozen set of '
                    f'decorator-hostile decorator function basenames '
                    f'{repr(attested_funcs_subtrie)} '
                    f'implies these basenames to represent '
                    f'functions rather than modules, but '
                    f'module "{self._module_name}" import statement '  # type: ignore[attr-defined]
                    f'imports from one or more of these basenames '
                    f'as modules rather than functions:\n'
                    f'\t{node_repr}'
                )
            #FIXME: Revise commentary, please. *sigh*
            # Else, this is *NOT* a frozen set. By elimination, this is either a
            # frozen dictionary *OR* "None".
            #
            # If this is either the empty frozen dictionary *OR* "None", this
            # basename is *NOT* that of a third-party (sub)module known to
            # define decorator-hostile decorator functions, implying this import
            # statement to *NOT* import from such a (sub)module and thus be
            # ignorable with respect to @beartype. In this case, silently reduce
            # to a noop by returning this node unmodified.
            elif attested_func_subtrie is SENTINEL:
                return node
            # Else, this is a non-empty frozen dictionary (by elimination),
            # implying this basename to be that of a third-party (sub)module
            # known to define decorator-hostile decorator functions. In this
            # case, attempt to unwrap this frozen dictionary against the next
            # unqualified basename in this list.
            else:
                #FIXME: Add a validation message, please. *sigh*
                assert isinstance(attested_func_subtrie, FrozenDict)

            # Record the parent frozen dictionary of the next iteration to be
            # the current frozen dictionary.
            attested_func_subtrie_parent = attested_func_subtrie

            # Increment the index of the next unqualified basename to visit.
            import_module_basename_index_curr += 1

        # ..................{ SEARCH ~ decorator             }..................
        # For each child "alias" node of this parent "ImportFrom" node
        # encapsulating the unqualified basenames of the one or more attributes
        # being imported from that module by this import statement...
        for import_attr_alias in node.names:
            # If this child node is *NOT* an "alias", silently skip this
            # unrecognized node type and continue to the next child node.
            #
            # Note that this should *NEVER* happen. All child nodes of parent
            # "ImportFrom" nodes should be aliases. For forward compatibility
            # with future Python versions, ignore this unrecognized node type.
            # See similar commentary below for further discussion.
            if not isinstance(import_attr_alias, alias):
                continue
            # Else, this child node is an "alias".

            # Imported source attribute name (i.e., unqualified basename of this
            # imported attribute as originally defined inside that external
            # module) if any *OR* "None".
            #
            # Note that this name should *NEVER* be "None". Yet, mypy claims
            # this name can actually be "None". How, mypy? Even mypy has no
            # idea. To squelch mypy complaints, we pretend mypy is still sane.
            import_attr_name_src = import_attr_alias.name
            if not import_attr_name_src: continue  # <-- *SILENCE, MYPY!*
            # This name is now guaranteed to be non-"None".

            # Imported target attribute name (i.e., unqualified basename of this
            # imported attribute as newly localized or globalized inside the
            # currently visited module), defined as either...
            import_attr_name_trg = (
                # If this import statement imports this attribute under an alias
                # via the 'as' predicate (e.g., "from mcp import tool as
                # mcp_tool"), that alias.
                #
                # Note that the "alias.asname" instance variable is "None" if
                # undefined, according to the official "ast" documentation.
                import_attr_alias.asname or
                # Else, this import statement imports this attribute under its
                # original name (e.g.,  "from mcp import tool"). In this case,
                # that name.
                import_attr_name_src
            )

            # If...
            if (
                # That module defines one or more decorator-hostile decorators
                # *AND*...
                attested_funcs_subtrie and
                # The unqualified basename of this attribute is that of a
                # decorator-hostile decorator function in that module...
                import_attr_name_src in attested_funcs_subtrie
            ):
                # Map the unqualified basename of this decorator-hostile
                # decorator function as a new terminal trie leaf node (i.e.,
                # key-value pair whose value is "None").
                scope.map_beforelist_imported_attr_basename_to_subtrie(
                    attr_basename=import_attr_name_trg, attr_subtrie=None)
            # Else, either that module defines no decorator-hostile decorator
            # functions *OR* the unqualified basename of this attribute is *NOT*
            # that of a decorator-hostile decorator function in that module. In
            # either case, this import is ignorable with respect to decorator
            # functions.
            #
            # If...
            #
            # Note that this edge case arises with submodule imports resembling:
            #     from langchain_core import runnable
            #     @runnable.chain
            #     def problem_func(...): ...
            elif (
                # That module defines one or more submodules transitively
                # defining one or more decorator-hostile decorators *AND*...
                isinstance(attested_func_subtrie, BeartypeDecorPlaceTrieABC) and
                # The unqualified basename of this attribute is that of such a
                # submodule...
                import_attr_name_src in attested_func_subtrie
            ):
                # Map the unqualified basename of that submodule transitively
                # defining one or more decorator-hostile decorator functions
                # to a new non-terminal trie stem node (i.e., key-value pair
                # whose value is a nested frozen dictionary).
                scope.map_beforelist_imported_attr_basename_to_subtrie(
                    attr_basename=import_attr_name_trg,
                    attr_subtrie=attested_func_subtrie,
                )

            #FIXME: Implement us up, please. *sigh*
            # # If...
            # elif (
            #     # That module defines one or more types defining one or more
            #     # decorator-hostile decorator methods *AND*...
            #     type_to_method_decor_names and
            #     # The unqualified basename of this attribute is that of such a
            #     # type...
            #     import_attr_name in type_to_method_decor_names
            # ):
            #     #FIXME: Implement us up, please. Urgh!
            #     pass
            # # Else, either that module defines no types defining
            # # decorator-hostile decorator methods *OR* the unqualified basename
            # # of this attribute is that of such a type. In either case, this
            # # import is ignorable with respect to @beartype.

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
            BeartypeDecorPlace.LAST_BEFORE_DECOR_HOSTILE):
            self._decorate_node_beartype_last_before_decor_hostile(
                node=node, conf=conf, node_beartype_decorator=node_beartype_decorator)
        # If injecting the @beartype decorator unconditionally last, prepend
        # this child decoration node to the beginning of the list of all child
        # decoration nodes for this parent decoratable node. Prepending
        # guarantees that our decorator will be applied last (i.e., *AFTER* all
        # subsequent decorators).
        elif decoration_position is BeartypeDecorPlace.LAST:
            node.decorator_list.insert(0, node_beartype_decorator)
        # If injecting the @beartype decorator unconditionally first, append
        # this child decoration node to the end of the list of all child
        # decoration nodes for this parent decoratable node.
        elif decoration_position is BeartypeDecorPlace.FIRST:
            node.decorator_list.append(node_beartype_decorator)
        # Else, an unrecognized decorator position was configured. In this case,
        # raise an exception. Note that this should *NEVER* occur.
        else:  # pragma: no cover
            raise BeartypeClawImportConfException(
                f'Beartype configuration {repr(conf)} '
                f'decorator position {repr(decoration_position)} unsupported.'
            )


    def _decorate_node_beartype_last_before_decor_hostile(
        self,
        node: NodeDecoratable,
        conf: BeartypeConf,
        node_beartype_decorator: expr,
    ) -> None:
        '''
        Add a new child :func:`beartype.beartype` decoration node to the passed
        parent decoratable node subject to
        :attr:`BeartypeDecorPlace.LAST_BEFORE_DECOR_HOSTILE` positioning.

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
            # The currently visited module imports neither decorator-hostile
            # decorators *NOR* modules transitively defining such decorators...
            not scope.beforelist.imported_attr_basename_trie
        ):
        # Then this type or callable is decorated by *NO* decorator-hostile
        # decorators. In this case, the @beartype decorator may be safely
        # injected as the last decorator in the chain of decorators
        # decorating this type or callable.
            # Reduce to the trivial implementation of the
            # "BeartypeDecorPlace.LAST" position in the parent
            # _decorate_node_beartype() method.
            node.decorator_list.insert(0, node_beartype_decorator)

            # Halt further processing.
            return
        # Else, this type or callable is decorated *AND* the currently visited
        # module imports either decorator-hostile decorators *OR* modules
        # transitively defining such decorators...

        # 0-based index of the current decorator visited by iteration below in
        # the chain of all decorators decorating this type or callable.
        #
        # Note that this index also efficiently doubles as the position in this
        # decorator chain that the @beartype decorator should be injected into.
        # This index is thus one larger than that of the last decorator-hostile
        # decorator in this decorator chain.
        node_decor_index_curr = 0

        # 0-based index of the last decorator visited by iteration below.
        #
        # Note that this index is guaranteed to be non-negative (i.e., >= 0), as
        # the chain of all decorators decorating this type or callable is
        # guaranteed to be non-empty (by the above validation).
        node_decor_index_last = len(node.decorator_list) - 1

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
        #     "@{module_or_type_name}.{decorator_name}(...)", encapsulated by an
        #     even more complex "ast.Call(func=Attribute(...), ...)" node.
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

        # While the 0-based index of the current decorator is less than or equal
        # to that of the last decorator in this decorator chain...
        while node_decor_index_curr <= node_decor_index_last:
            # Current decorator.
            node_decor = node.decorator_list[node_decor_index_curr]

            # If this decoration is encapsulated by a complex "Call" node,
            # this is a callable call decoration encapsulating either:
            # * An unqualified attribute decoration of the form
            #   "@{decorator_name}(...)".
            # * A qualified attribute decoration of the form
            #   "@{decorator_name}(...)".
            #
            # In either case, reduce this callable call node to the child "Name"
            # or "Attribute" node it encapsulates.
            if isinstance(node_decor, Call):
                node_decor = node_decor.func
            # Else, this decoration is *NOT* encapsulated by a "Call" node.

            # Either:
            # * If this decorator name refers to a previously imported
            #   decorator-hostile decorator, "False".
            # * If this decorator name refers to a previously imported
            #   submodule, type, or instance transitively defining one or more
            #   decorator-hostile decorators, the imported decorator-hostile
            #   attribute name subtrie describing the contents of that
            #   submodule, type, or instance.
            # * Else (i.e., if this decorator name refers to neither a
            #   previously imported decorator-hostile decorator *nor* a
            #   submodule, type, or instance transitively defining these
            #   decorators), "True".
            is_decor_hostile = self._is_node_imported_attr_name(node_decor)

            # If this decorator name refers to a previously imported submodule,
            # type, or instance transitively defining one or more
            # decorator-hostile decorators, this decorator is *NOT* actually a
            # decorator according to the beforelist. But this decorator is a
            # decorator, clearly! This implies the user to have improperly
            # configured a "beartype.claw" import hook with an erroneous
            # beforelist specifying this imported decorator-hostile decorator to
            # actually be a non-decorator submodule, type, or instance. An
            # object can be a decorator *OR* non-decorator -- but not both. In
            # this case...
            if isinstance(is_decor_hostile, BeartypeDecorPlaceTrieABC):
                # Possibly fully-qualified name of this decorator in this
                # lexical scope, defined by "unparsing" this child node. The
                # standard ast.unparse() function "unparses" (i.e., obtains the
                # machine-readable representations of) arbitrary nodes.
                #
                # Note that the parent object of this attribute is described by
                # the external node "node_target.value", encapsulating an
                # arbitrarily complex Python expression. "Unparsing" this
                # expression manually is *ABSOLUTELY* infeasible.
                decor_name = unparse(node_decor)

                # Raise an explanatory exception.
                raise BeartypeClawAstImportException(
                    f'Beartype configuration {repr(self._conf)} '  # type: ignore[attr-defined]
                    f'decorator position beforelist '
                    f'{repr(scope.beforelist.attested_attr_basename_trie)} '
                    f'nested frozen dictionary of decorator-hostile decorators '
                    f'{repr(is_decor_hostile)} erroneously implies '
                    f'object "{node.name}" decorator @{decor_name} '
                    f'to not be a decorator (but instead be a '
                    f'subpackage, submodule, '
                    f'non-decorator type, or '
                    f'non-decorator callable.)'
                )
            # Else, this decorator name does *NOT* refers to a previously
            # imported submodule, type, or instance transitively defining one or
            # more decorator-hostile decorators.

            # If this decorator is *NOT* decorator-hostile, this decorator is
            # presumably compatible with the @beartype decorator. In this case,
            # immediately halt this iteration.
            if is_decor_hostile is False:
                break
            # Else, this decorator is decorator-hostile. In this case, continue
            # searching for the first non-hostile decorator.

            # Increment the 0-based index of the next decorator to be visited.
            node_decor_index_curr += 1

        # If the 0-based index in this decorator chain that the @beartype
        # decorator should be injected into is a valid index into this list,
        # inject the @beartype decorator as the last decorator *BEFORE* (i.e.,
        # below) the last decorator-hostile decorator in the chain of existing
        # decorators decorating this type or callable.
        if node_decor_index_curr <= node_decor_index_last:
            node.decorator_list.insert(
                node_decor_index_curr, node_beartype_decorator)
        # Else, this is *NOT* a valid index into this list. Presumably, this
        # index is one larger than the last valid index into this list. In this
        # case, this type or callable is decorated *ONLY* by decorator-hostile
        # decorators. Since type or callable is decorated by *NO* safe
        # decorators that the @beartype decorator can be injected before,
        # @beartype *MUST* instead be appended after the last decorator (which
        # is also a decorator-hostile decorator) decorating this type or
        # callable. Look. It's complicated.
        else:
            # Sanity-check the expected constraint.
            assert node_decor_index_curr == node_decor_index_last + 1, (
                f'Type or callable "{self._module_name}.{node.name}" '  # type: ignore[attr-defined]
                f'decorated by decorator-hostile decorators, but '
                f'@beartype decoration chain insertion index '
                f'{node_decor_index_curr} != {node_decor_index_last + 1}.'
            )

            # Append @beartype *AFTER* this last decorator.
            node.decorator_list.append(node_beartype_decorator)

    # ....................{ PRIVATE ~ finders              }....................
    #FIXME: Call above, please. *sigh*
    #FIXME: Generalize comments below to refer to "attribute" rather than
    #"decorator", please. *sigh*
    def _is_node_imported_attr_name(
        self, node: AST) -> Union[BeartypeDecorPlaceSubtrie, bool]:
        '''
        :data:`True` if the attribute name (presumably referenced from the
        current scope of the currently visited module) encapsulated by the
        passed node is that of a previously imported decorator-hostile
        decorator, the relevant **imported decorator-hostile attribute name
        subtrie** (i.e., recursive tree structure whose nodes are the
        unqualified basenames of third-party attributes imported into a scope of
        the currently visited module such that these attributes are either
        themselves decorator-hostile decorators *or* submodules, types, or
        instances transitively defining decorator-hostile decorators) if that
        attribute name is instead that of a previously imported submodule, type,
        or instance transitively defining one or more decorator-hostile
        decorators, or :data:`False` otherwise (i.e., if this attribute name is
        *not* that of either a previously imported decorator-hostile decorator
        or a submodule, type, or instance transitively defining such
        decorators).

        This finder identifies whether the passed attribute name refers to a
        previously imported decorator-hostile decorator or not. Specifically,
        this finder (in order):

        #. Splits the possibly fully-qualified attribute name encapsulated by
           this attribute name node on ``"."`` delimiters into its constituent
           unqualified basenames.
        #. For each such unqualified basename:

           * If there exists a child subtrie of the current parent imported
             decorator-hostile attribute name (sub)trie (starting at the root
             decorator-hostile attribute name trie) whose associated key is
             this basename:

             * If that child subtrie is :data:`None` (signifying that child
               subtrie to be a terminal leaf node and thus a decorator-hostile
               decorator function or method), return :data:`True`.
             * Else, recurse into that subtrie.

           * Else, return either:

             * If this is the first unqualified basename and no such child
               subtrie exists, :data:`False`.
             * Else, that child subtrie.

        Parameters
        ----------
        node : AST
            Node possibly encapsulating the name of an attribute referenced from
            some scope of the currently visited module.

        Returns
        -------
        Optional[Union[BeartypeDecorPlaceSubtrie, Iota]]
            Either:

            * If this attribute name refers to a previously imported
              decorator-hostile decorator, :data:`True`.
            * If this attribute name refers to a previously imported submodule,
              type, or instance transitively defining one or more
              decorator-hostile decorators, the imported decorator-hostile
              attribute name subtrie describing the contents of that submodule,
              type, or instance.
            * Else (i.e., if this attribute name refers to neither a previously
              imported decorator-hostile decorator *nor* a submodule, type, or
              instance transitively defining these decorators),
              :data:`False`.
        '''

        # Replace the contents of the existing "_attr_basenames" list with the
        # one or more unqualified basenames comprising the possibly
        # fully-qualified name of this attribute.
        get_node_attr_basenames(node=node, attr_basenames=self._attr_basenames)

        # If this list is empty, the prior getter failed to reconstruct this
        # list from this node (e.g., due to this node being of an unknown type
        # currently unsupported by that getter). This implies it is now unknown
        # whether the desired attribute is has been imported from a problematic
        # third-party package into the currently visited module or not.
        #
        # Note that this should *NEVER* happen. The prior getter *SHOULD*
        # support all relevant types of nodes. However, the Python language and
        # hence AST grammar describing that language is constantly evolving.
        # Since this just happened, it is likely that a future iteration of the
        # Python language has now evolved in an unanticipated (yet, ultimately
        # valid) way. To preserve forward compatibility in @beartype with future
        # Python versions, intentionally ignore this decorator.
        #
        # Sometimes, doing nothing at all is the best thing you can do.
        if not self._attr_basenames:
            return False
        # Else, this list is non-empty, implying the prior getter succeeded in
        # reconstructing this list from this node.

        # Current child (sub)trie of the parent imported attribute name
        # (sub)trie being recursed into by iteration below, initialized to the
        # root imported attribute name trie unique to the current scope of the
        # currently imported module.
        imported_attr_name_subtrie = (
            self._scopes[-1].beforelist.imported_attr_basename_trie)  # type: ignore[attr-defined]

        # For the unqualified basename of either each parent submodule
        # transitively defining this attribute itself or this attribute...
        for node_decorator_basename in self._attr_basenames:
            # Child subtrie of this parent (sub)trie matching this basename if
            # the currently visited module previously imported either a
            # third-party submodule, type, or instance transitively defining one
            # or more decorator-hostile decorators or such a decorator with the
            # same basename *OR* the sentinel.
            imported_attr_name_subtrie = imported_attr_name_subtrie.get(  # type: ignore[assignment]
                node_decorator_basename, SENTINEL)  # type: ignore[arg-type]

            # If the parent (sub)trie contained *NO* basename matching that of a
            # problematic third-party object imported into the currently visited
            # module, this attribute is *NOT* a decorator-hostile decorator.
            # This attribute is thus presumably friendly to the @beartype
            # decorator. In this case, immediately return false.
            #
            # Note that:
            # * *ALL* decorators syntactically following (i.e., applied
            #   semantically earlier to the currently decorated type or
            #   callable) the top-most decorator-friendly decorator in a chain
            #   of decorators *MUST* themselves be decorator-friendly. Why?
            #   Because, if any following decorator was decorator-hostile, then
            #   by definition that decorator-hostile decorator could *NOT* have
            #   been preceded by any other decorators. That's what
            #   decorator-hostile means. But that decorator *WAS* preceded by
            #   this decorator. Proof by contradiction yields this conclusion.
            if imported_attr_name_subtrie is SENTINEL:
                return False
            # Else, the parent (sub)trie contained a basename matching that of a
            # problematic third-party object imported into the currently visited
            # module, implying this attribute *COULD* still be hostile.
            #
            # If this child subtrie is "None", the key-value pair of that parent
            # (sub)trie associated with this "None" value is a terminal leaf
            # node, implying this attribute to be a decorator-hostile decorator.
            # In this case, immediately return true.
            elif imported_attr_name_subtrie is None:
                return True
            # Else, this child subtrie is *NOT* "None". By elimination, this
            # child subtrie *MUST* actually be yet another recursively nested
            # subtrie. In this case, continue matching basenames between this
            # attribute and decorator-hostile decorators imported into the
            # currently visited module.
        # Else, the list of all unqualified basenames comprising the possibly
        # fully-qualified name of this attribute was exhausted:
        # * *AFTER* recursively visiting at least one imported attribute name
        #   (sub)trie with corresponding basenames. Why? Because if at least one
        #   (sub)trie had *NOT* been visited above, this method would have
        #   immediately returned false. But this method has yet to return
        #   anything! Proof by contradiction yields this conclusion.
        # * *BEFORE* recursively visiting all imported attribute name (sub)tries
        #   with associated basenames. Why? Because if all such (sub)tries had
        #   already been visited above, this method would have immediately
        #   returned true. But this method has yet to return anything! QED.

        # Assert sanity. You never know, bear friends. And neither do we.
        assert isinstance(imported_attr_name_subtrie, BeartypeDecorPlaceTrieABC)

        # Return the most recently visited imported attribute name (sub)trie.
        return imported_attr_name_subtrie
