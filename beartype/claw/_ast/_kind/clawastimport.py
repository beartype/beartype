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
#FIXME: Handle user-defined afterlists via the "self._conf" instance
#variable, please. *sigh*

#FIXME: Track problematic imports across local (i.e., function) scopes as well.
#Local scopes require unique handling, because they are *NEVER* globally
#accessible by any means. Unlike class scopes, imports *ARE* often confined to
#local scopes. Ergo, tracking imports across local scopes would be quite useful.
#The best way to handle local scopes would be to:
#* In the BeartypeNodeTransformer.generic_visit() method:
#  * On entering a new local scope (i.e., function body), append:
#        self._scopes_afterlist.append(self._scopes_afterlist[-1])
#    What this does is efficiently propagate afterlist scopes down from the
#    default afterlist global scope into unique afterlist nested scopes.
#  * On exiting the current local scope (i.e., function body), pop
#    the last item off that stack.
#* On detecting any problematic import:
#  * Decide whether new mutable "ChainMap" objects are needed based on whether
#    the current "self._func_scopes_afterlist[-1]" stack head is an immutable
#    "FrozenDict" object or not: e.g.,
#        scope_afterlist = self._scopes_afterlist[-1]
#        if isinstance(scope_afterlist, FrozenDict):
#            self._scopes_afterlist[-1] = scope_afterlist = scope_afterlist.permute()
#  * Append problematic local imports to "scope_afterlist"
#    rather than global data structures.
#
#That's about it, really. Should work just fine. Fun? Let's hope so. \o/

# ....................{ IMPORTS                            }....................
from ast import (
    ImportFrom,
    alias,
)
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

        # ..................{ TRACK                          }..................
        # If the lexical scope of this parent node is module scope, this node
        # encapsulates a global import statement. In this case...
        if self._scopes.is_scope_module:  # type: ignore[attr-defined]
            #FIXME: *DO STUFF HERE!* For now, just start with the
            #"CLAW_AFTERLIST_MODULE_TO_FUNC_DECORATOR_NAME" global. *shrug*
            pass
        # Else, the lexical scope of this parent node is *NOT* module scope. In
        # this case...
        else:
            #FIXME: Consider tracking problematic imports in nested scopes as
            #well. Since nobody has complained about this yet, this is fine for
            #the moment. Note that two kinds of nested scopes exist:
            #* Class scope. These could be considered a kind of global scope.
            #  Like global scopes, class scopes can be globally accessed outside
            #  of those classes through standard "." lookups. This differs from
            #  local scopes, which cannot be. Ergo, class scopes could probably
            #  be reasonably handled in the "if" block above. That said, class
            #  scopes are also *INCREDIBLY* rare. It's highly unlikely that
            #  *ANYONE* will ever import anything directly in a class scope.
            #  Technically, it can be done. Pragmatically, no one does. Ergo,
            #  class scopes are entirely ignorable... until somebody complains!
            #* Local (i.e., function) scope. Local scopes require unique
            #  handling, because they are *NEVER* globally accessible by any
            #  means. Unlike class scopes, imports *ARE* often confined to local
            #  scopes. Ergo, tracking imports across local scopes would be quite
            #  useful. See the "FIXME:" above for detailed commentary.
            pass

        # ..................{ RETURN                         }..................
        # Return this node unmodified.
        return node
