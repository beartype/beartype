#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype **abstract syntax tree (AST) scope** (i.e., low-level dataclass
aggregating all metadata required to detect and manage a lexical scope being
recursively visited by the current AST transformer).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from ast import (
    AST,
    Module,
)
from beartype.typing import (
    TYPE_CHECKING,
    Type,
)
from beartype.claw._ast._scope.clawastscopeafter import (
    BeartypeNodeScopeAfterlist,
    make_node_scope_afterlist_global,
)

# ....................{ CLASSES                            }....................
#FIXME: Unit test us up, please. *sigh*
class BeartypeNodeScope(object):
    '''
    Beartype **abstract syntax tree (AST) scope** (i.e., low-level dataclass
    aggregating all metadata required to detect and manage a lexical scope
    being recursively visited by the current AST transformer).

    Attributes
    ----------
    afterlist : BeartypeNodeScopeAfterlist
        **Lexical scope afterlist** (i.e., dataclass aggregating all metadata
        required to manage the afterlist automating decorator positioning for
        this lexical scope being recursively visited by this AST transformer).
    node_type : type[AST]
        **Lexical scope node type** (i.e., type of the "closest" parent lexical
        scope node of the current node being recursively visited by this AST
        transformer such that that parent node declares a new lexical scope).
        Specifically, if this is:

        * :class:`ast.Module`, the current node directly resides in the **global
          scope** of the current module.
        * :class:`ast.ClassDef`, the current node directly resides in the
          **class scope** of the current class.
        * :class:`ast.FunctionDef`, the current node directly resides in the
          **callable scope** of the current callable.
    '''

    # ..................{ CLASS VARIABLES                    }..................
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # CAUTION: Subclasses declaring uniquely subclass-specific instance
    # variables *MUST* additionally slot those variables. Subclasses violating
    # this constraint will be usable but unslotted, which defeats our purposes.
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # Slot all instance variables defined on this object to reduce the costs of
    # both reading and writing these variables by approximately ~10%.
    __slots__ = (
        'afterlist',
        'node_type',
    )

    # Squelch false negatives from mypy. This is absurd. This is mypy. See:
    #     https://github.com/python/mypy/issues/5941
    if TYPE_CHECKING:
        afterlist: BeartypeNodeScopeAfterlist
        node_type: Type[AST]

    # ....................{ INITIALIZERS                   }....................
    def __init__(
        self,
        afterlist: BeartypeNodeScopeAfterlist,
        node_type: Type[AST],
    ) -> None:
        '''
        Initialize this afterlist scope.

        Parameters
        ----------
        afterlist : BeartypeNodeScopeAfterlist
            **Lexical scope afterlist.** See the class docstring.
        node_type : type[AST]
            **Lexical scope node type.** See the class docstring.
        '''
        assert isinstance(afterlist, BeartypeNodeScopeAfterlist), (
            f'{repr(afterlist)} not afterlist scope.')
        assert isinstance(node_type, type), f'{repr(node_type)} not type.'
        assert issubclass(node_type, AST), f'{repr(node_type)} not node type.'

        # Classify all passed parameters.
        self.afterlist = afterlist
        self.node_type = node_type

    # ..................{ DUNDERS                            }..................
    def __repr__(self) -> str:

        return '\n'.join((
            f'{self.__class__.__name__}(\n',
            f'    afterlist={repr(self.afterlist)},\n',
            f'    node_type={repr(self.node_type)},\n',
            f')',
        ))

# ....................{ FACTORIES                          }....................
#FIXME: Unit test us up, please.
def make_node_scope_global() -> BeartypeNodeScope:
    '''
    Beartype **abstract syntax tree (AST) global scope** (i.e., low-level
    dataclass aggregating all metadata required to detect and manage the global
    scope of the module being recursively visited by the current AST
    transformer).

    Returns
    -------
    BeartypeNodeScope
        AST global scope of the currently visited module. 
    '''

    # Create and return this global scope.
    return BeartypeNodeScope(
        afterlist=make_node_scope_afterlist_global(),
        node_type=Module,
    )
