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
    BeartypeNodeScopeAfterlist)

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
        **Abstract syntax tree (AST) scope afterlist** (i.e., dataclass
        aggregating all metadata required to manage the afterlist automating
        decorator positioning for this scope being recursively visited by the
        parent AST transformer).
    name : str
        Fully-qualified name of the current lexical scope (i.e., ``.``-delimited
        absolute name of the module containing this scope followed by the
        relative basenames of zero or more classes and/or callables). This name
        is guaranteed to be prefixed by the current value of the
        :attr:`.module_name` instance variable.
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
    _is_afterlist_mutable : bool
        :data:`True` only if this scope afterlist is **modifiable** (i.e., if
        this scope afterlist is unique to this scope). This scope afterlist
        defaults to:

        * If this scope is global, :data:`True`. Global scope afterlists are
          safely shared between *all* global scopes for *all* modules and thus
          safely modifiable as is.
        * If this scope is nested (i.e., either class or callable),
          :data:`False`. Nested scope afterlists are *not* safely shared
          between *all* global scopes for *all* modules and thus *not* safely
          modifiable as is. Instead, nested scope afterlists must be copied from
          their parent global scope afterlists into new afterlists unique to
          those nested scopes before being modified.
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
        'name',
        'node_type',
        '_is_afterlist_mutable',
    )

    # Squelch false negatives from mypy. This is absurd. This is mypy. See:
    #     https://github.com/python/mypy/issues/5941
    if TYPE_CHECKING:
        afterlist: BeartypeNodeScopeAfterlist
        name: str
        node_type: Type[AST]
        _is_afterlist_mutable: bool

    # ....................{ INITIALIZERS                   }....................
    def __init__(
        self,
        afterlist: BeartypeNodeScopeAfterlist,
        name: str,
        node_type: Type[AST],
    ) -> None:
        '''
        Initialize this afterlist scope.

        Parameters
        ----------
        afterlist : BeartypeNodeScopeAfterlist
            **Lexical scope afterlist.** See the class docstring.
        name : str
            Fully-qualified name of the current lexical scope (i.e.,
            ``.``-delimited absolute name of the module containing this scope
            followed by the relative basenames of zero or more classes and/or
            callables).
        node_type : type[AST]
            **Lexical scope node type.** See the class docstring.
        '''
        assert isinstance(afterlist, BeartypeNodeScopeAfterlist), (
            f'{repr(afterlist)} not afterlist scope.')
        assert isinstance(name, str), f'{repr(name)} not string.'
        assert isinstance(node_type, type), f'{repr(node_type)} not type.'
        assert issubclass(node_type, AST), f'{repr(node_type)} not node type.'

        # Classify all passed parameters.
        self.afterlist = afterlist
        self.name = name
        self.node_type = node_type

        # Record this afterlist to already be safely modifiable *ONLY* if this
        # is a global scope. See also the class docstring.
        self._is_afterlist_mutable = node_type is Module

    # ..................{ DUNDERS                            }..................
    def __repr__(self) -> str:

        return '\n'.join((
            f'{self.__class__.__name__}(\n',
            f'    afterlist={repr(self.afterlist)},\n',
            f'    name={repr(self.name)},\n',
            f'    node_type={repr(self.node_type)},\n',
            f'    _is_afterlist_mutable={repr(self._is_afterlist_mutable)},\n',
            f')',
        ))

    # ..................{ DUNDERS                            }..................
    def permute_afterlist_if_needed(self) -> None:
        '''
        Render this scope's afterlist safe for modification by external callers
        (e.g., to track problematic third-party imports) if this afterlist is
        *not* yet safely **modifiable** (i.e., if this afterlist is still a
        reference to a parent scope's afterlist and is thus *not* unique to this
        scope).

        For both space and time efficiency, afterlists obey the copy-on-write
        design pattern inspired by modern filesystems (e.g., Btrfs). Before
        attempting to modify the contents of this afterlist, callers should call
        this method to render this afterlist safe for modification.
        '''

        # If this afterlist is *NOT* yet safely modifiable, this afterlist is
        # still a reference to a parent scope's afterlist and is thus *NOT*
        # unique to this scope. In this case...
        if not self._is_afterlist_mutable:
            # Replace this shared afterlist with a new afterlist unique to this
            # scope, which may then be safely modified by callers.
            self.afterlist = self.afterlist.permute()

            # Record that this afterlist is now safely modifiable.
            self._is_afterlist_mutable = True
