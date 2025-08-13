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
#FIXME: Handle user-defined afterlists via the "self._conf_beartype" instance
#variable, please. *sigh*

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
        if not self._is_scope_module_beartype:  # type: ignore[attr-defined]
            #FIXME: *DO STUFF HERE!* For now, just start with the
            #"CLAW_AFTERLIST_MODULE_TO_FUNC_DECORATOR_NAME" global. *shrug*
            pass
        # Else, the lexical scope of this parent node is *NOT* module scope. In
        # this case...
        else:
            #FIXME: Consider tracking problematic imports in nested scopes as
            #well. Since nobody has complained about this yet, this is fine.
            pass

        # ..................{ RETURN                         }..................
        # Return this node unmodified.
        return node
