#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype **abstract syntax tree (AST) scopes** (i.e., stack of low-level
dataclasses aggregating all metadata required to detect and manage *all* lexical
scopes being recursively visited by the current AST transformer).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from ast import (
    AST,
    ClassDef,
)
from beartype.roar._roarexc import _BeartypeClawAstNodeScopesException
from beartype.typing import Type
from beartype.claw._ast._scope.clawastscope import (
    BeartypeNodeScope,
    make_node_scope_global,
)
from beartype._data.api.standard.dataast import TYPES_NODE_LEXICAL_SCOPE

# ....................{ CLASSES                            }....................
#FIXME: Unit test us up, please. *sigh*
class BeartypeNodeScopes(list[BeartypeNodeScope]):
    '''
    Beartype **abstract syntax tree (AST) scope stack** (i.e., list of the one
    or more dataclasses aggregating all metadata required to detect and manage
    all lexical scopes being recursively visited by the current AST
    transformer).

    This stack is guaranteed to *always* be non-empty. Specifically:

    * If this stack contains exactly one lexical scope, the current node resides
      in the **global scope** of the current module.
    * Else, the current node does *not* directly reside in the global scope of
      this module. Instead, if the :attr:`BeartypeNodeScope.node_type` instance
      variable of the last item of this stack is:

      * :class:`ast.ClassDef`, the current node directly resides in the **class
        scope** of the current class.
      * :class:`ast.FunctionDef`, the current node directly resides in the
        **callable scope** of the current callable.
    '''

    # ....................{ INITIALIZERS                   }....................
    def __init__(self) -> None:
        '''
        Initialize this AST scope stack.
        '''

        # Global scope of the module currently being recursively visited by the
        # parent AST transformer.
        node_scope_global = make_node_scope_global()

        # Initialize this stack with this global scope.
        self.append(node_scope_global)

    # ....................{ APPENDERS                      }....................
    #FIXME: Unit test us up, please. *sigh*
    def append_scope_nested(self, node_type: Type[AST]) -> None:
        '''
        Append a new AST scope of the passed node type to the top of this stack,
        describing the deepest nested lexical scope currently being visited by
        the parent AST transformer.

        Note that this scope *must* be nested. Ergo, this node type *must* be
        either of the :class:`ast.ClassDef` or :class:`ast.FunctionDef` types.

        Caveats
        -------
        **External callers should always call this high-level convenience method
        rather than the low-level** :meth:`.append` **method,** which is
        considerably less convenient (and arguably dangerous).

        Parameters
        ----------
        node_type : type[AST]
            **Lexical scope node type.** See the :class:`BeartypeNodeScope`
            class docstring.

        Raises
        ------
        _BeartypeClawAstNodeScopesException
            If this node type is neither of the :class:`ast.ClassDef` or
            :class:`ast.FunctionDef` types.
        '''

        # If this node does *NOT* declare a new nested lexical scope (i.e., by
        # defining a new class or callable), raise an exception.
        if node_type not in TYPES_NODE_LEXICAL_SCOPE:
            raise _BeartypeClawAstNodeScopesException(
                f'AST node type {repr(node_type)} not that of nested scope '
                f'(i.e., neither "ast.ClassDef" nor "ast.FunctionDef").'
            )
        # Else, this node declares a new nested lexical scope.

        # New AST scope describing the deepest nested lexical scope currently
        # being visited by the parent AST transformer.
        scope_nested = BeartypeNodeScope(
            # For both efficiency and simplicity, reuse the same afterlist as
            # that of the parent scope of this nested scope. If this nested
            # scope contains one or more problematic imports and thus requires a
            # distinct afterlist unique to this nested scope, the appropriate
            # external AST transformer mixin will permute this parent afterlist
            # into a new nested afterlist as needed.
            #
            # Note that this stack is guaranteed to *ALWAYS* be non-empty. Ergo,
            # this parent scope is guaranteed to *ALWAYS* exist.
            afterlist=self[-1].afterlist,
            node_type=node_type,
        )

        # Append this nested scope to the top of this stack.
        self.append(scope_nested)

    # ..................{ PROPERTIES                         }..................
    @property
    def is_scope_module(self) -> bool:
        '''
        :data:`True` only if the lexical scope of the currently visited node is
        the **module scope** (i.e., this node is declared directly in the body
        of the current user-defined module, implying this node to be a global).

        Returns
        -------
        bool
            :data:`True` only if the current lexical scope is a module scope.
        '''

        # Return true only if this stack contains exactly one scope, presumably
        # describing the global scope of the currently visited module.
        #
        # Note that this is a negligible optimization. We could also test:
        #     return self[-1].node_type is Module
        return len(self) == 1


    @property
    def is_scope_class(self) -> bool:
        '''
        :data:`True` only if the lexical scope of the currently visited node is
        a **class scope** (i.e., this node resides directly in the body of a
        user-defined class).

        Returns
        -------
        bool
            :data:`True` only if the current lexical scope is a class scope.
        '''

        # Return true only if the current node is directly in a class scope.
        return self[-1].node_type is ClassDef
