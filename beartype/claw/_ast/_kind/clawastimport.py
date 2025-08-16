#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype **afterlist trackers** (i.e., low-level mixins managing the afterlist
automating decorator positioning for :mod:`beartype.claw` import hooks).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ TODO                               }....................
#FIXME: Additionally handle:
#* Absolute imports (e.g., "import problem_package"). This will require a new
#  visite_Import() method altogether. *sigh*
#* Import aliases (e.g., "from problem_package import problem_decor as ohboy").

#FIXME: Handle user-defined afterlists via the "self._conf" instance
#variable, please. *sigh*

# ....................{ IMPORTS                            }....................
from ast import (
    ImportFrom,
    alias,
)
from beartype.claw._ast._scope.clawastscope import BeartypeNodeScope
from beartype._data.typing.datatyping import NodeVisitResult

# ....................{ SUBCLASSES                         }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# CAUTION: To improve forward compatibility with the superclass API over which
# we have *NO* control, avoid accidental conflicts by suffixing *ALL* private
# and public attributes of this subclass by "_beartype".
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

#FIXME: Actually subclass from this mixin, please. *sigh*
class BeartypeNodeTransformerAfterlistMixin(object):
    '''
    Beartype **afterlist tracker** (i.e., visitor pattern recursively
    tracking imports of problematic third-party decorators as well as the
    modules and types providing such decorators across *all* import statements
    in the AST tree passed to the :meth:`visit` method of the
    :class:`beartype.claw._ast.clawastmain.BeartypeNodeTransformer` subclass
    also subclassing this mixin).

    This tracker manages the **beartype decorator afterlist** (i.e., collection
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
        #FIXME: Mypy claims this name can actually be "None". How, mypy? What
        #are talking about? *sigh*
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

        #FIXME: Revise docstring. This is now a nested chain map. *sigh*
        # Collection of the unqualified basename of each third-party decorator
        # function of this external module which the @beartype decorator *MUST*
        # appear after within the chain of decorators for objects decorated by
        # that third-party decorator if any *OR* "None".
        func_decorator_names = (
            scope.afterlist.module_to_func_decorator_names.get(
                import_module_name))

        #FIXME: Revise docstring. This now maps to nested chain maps. *sigh*
        # Nested dictionary mapping from the unqualified basename of each
        # third-party decorator method of each type of this external module
        # which the @beartype decorator *MUST* appear after within the chain of
        # decorators for objects decorated by that third-party decorator if any
        # *OR* "None".
        type_to_method_decorator_names = (
            scope.afterlist.module_to_type_to_method_decorator_names.get(
                import_module_name))

        # ..................{ SEARCH                         }..................
        # If either of these collections is non-empty, this import statement is
        # importing from a problematic third-party module known to declare
        # decorator-hostile decorators. In this case...
        if func_decorator_names or type_to_method_decorator_names:
            # For each AST node of type "ast.alias" encapsulating the one or more
            # attributes being imported from this external module by this import
            # statement...
            for import_attr_alias in node.names:
                # Unqualified basename of this attribute if any *OR* "None".
                #
                # Note that this name should *NEVER* be "None". Nonetheless,
                # mypy claims this name can actually be "None". How, mypy? Even
                # mypy has no idea. To squelch complaints from mypy, we pretend
                # mypy is still sane.
                import_attr_name = import_attr_alias.name
                if not import_attr_name: continue  # <-- *SILENCE, MYPY!*

                #FIXME: Handle "import_attr_alias.asname" too, please. Note that
                #"asname" is "None" if undefined, according to the official
                #"ast" documentation. *sigh*

                # If...
                if (
                    # This external module defines one or more problematic
                    # decorator functions *AND*...
                    func_decorator_names and
                    # The unqualified basename of this attribute is that of a
                    # problematic decorator function in this external module...
                    import_attr_name in func_decorator_names
                ):
                    #FIXME: [SPEED] Inefficient. This permutes both chain maps,
                    #when we actually only need to permute the
                    #"module_to_func_decorator_names" chain map. *shrug*
                    # Render this scope's afterlist safe for modification if
                    # this afterlist is *NOT* yet safely modifiable.
                    scope.permute_afterlist_if_needed()

                    #FIXME: Comment us up, please. The idea here is that we
                    #maintain each "set" of decorator function names as a chain
                    #map rather than an actual set. We only care about the keys
                    #of that chain. Sadly, Python currently lacks a "ChainSet".
                    #So, we have to abuse a "ChainMap" to get what we want.
                    #Technically, we *COULD* implement our own "ChainSet" -- but
                    #this is already taking far too long as it is. We'll just
                    #have to live with a bit of cumbersomeness for now. *sigh*
                    #
                    #By mapping to a nested chain map, we can now simply permute
                    #this nested chain map rather than laboriously searching up
                    #this hierarchy. To do so safely, note that we *NEW CHILD*
                    #this nested chain map first to avoid modifying the parent
                    #nested chain map.
                    func_decorator_names_new = func_decorator_names.new_child()
                    func_decorator_names_new[import_attr_name] = None  # <-- arbitrary value

                    # Note this must be localized only *AFTER* calling the
                    # scope.permute_afterlist_if_needed() method above, which
                    # necessarily reassigns the "scope.afterlist" instance
                    # variable accessed here.
                    module_to_func_decorator_names = (
                        scope.afterlist.module_to_func_decorator_names)

                    #FIXME: Revise commentary, please. *sigh*
                    # Add a new key-value pair to this scope's afterlist mapping
                    # the fully-qualified name of this scope to the unqualified
                    # basename of this problematic decorator.
                    module_to_func_decorator_names[scope.name] = (
                        func_decorator_names_new)
                # Else, either this external module defines no problematic
                # decorator functions *OR* the unqualified basename of this
                # attribute is *NOT* that of a problematic decorator function in
                # this external module. In either case, this import is ignorable
                # with respect to problematic decorator functions.
                #
                # If...
                elif (
                    # This external module defines one or more problematic
                    # decorator methods *AND*...
                    type_to_method_decorator_names and
                    # The unqualified basename of this attribute is that of a
                    # type defining such methods in this external module...
                    import_attr_name in type_to_method_decorator_names
                ):
                    #FIXME: Implement us up, please. Urgh!
                    pass
                # Else, either this external module defines no problematic
                # decorator functions *OR* the unqualified basename of this
                # attribute is *NOT* that of a type defining such methods in
                # this external module. In either case, this import is ignorable
                # with respect to problematic decorator methods.

        # Else, both of these collections are empty. In this case, this import
        # statement is *NOT* importing from a problematic third-party module
        # known to declare decorator-hostile decorators. Ergo, this import
        # statement is ignorable.

        # ..................{ RETURN                         }..................
        # Return this node unmodified.
        return node
