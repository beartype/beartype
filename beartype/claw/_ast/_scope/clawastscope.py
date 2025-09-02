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
from beartype.claw._ast._scope.clawastscopebefore import (
    BeartypeNodeScopeBeforelist)
from beartype._cave._cavemap import NoneTypeOr
from beartype._data.conf.dataconfplace import BeartypeDecorPlaceSubtrie
from beartype._util.kind.maplike.utilmapfrozen import FrozenDict

# ....................{ CLASSES                            }....................
#FIXME: Unit test us up, please. *sigh*
class BeartypeNodeScope(object):
    '''
    Beartype **abstract syntax tree (AST) scope** (i.e., low-level dataclass
    aggregating all metadata required to detect and manage a lexical scope
    being recursively visited by the current AST transformer).

    Attributes
    ----------
    beforelist : BeartypeNodeScopeBeforelist
        **Abstract syntax tree (AST) scope beforelist** (i.e., dataclass
        aggregating all metadata required to manage the beforelist automating
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
    _is_beforelist_mutable : bool
        :data:`True` only if this scope beforelist is **modifiable** (i.e., if
        this scope beforelist is unique to this scope). This scope beforelist
        defaults to:

        * If this scope is global, :data:`True`. Global scope beforelists are
          safely shared between *all* global scopes for *all* modules and thus
          safely modifiable as is.
        * If this scope is nested (i.e., either class or callable),
          :data:`False`. Nested scope beforelists are *not* safely shared
          between *all* global scopes for *all* modules and thus *not* safely
          modifiable as is. Instead, nested scope beforelists must be copied from
          their parent global scope beforelists into new beforelists unique to
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
        'beforelist',
        'name',
        'node_type',
        '_is_beforelist_mutable',
    )

    # Squelch false negatives from mypy. This is absurd. This is mypy. See:
    #     https://github.com/python/mypy/issues/5941
    if TYPE_CHECKING:
        beforelist: BeartypeNodeScopeBeforelist
        name: str
        node_type: Type[AST]
        _is_beforelist_mutable: bool

    # ....................{ INITIALIZERS                   }....................
    def __init__(
        self,
        beforelist: BeartypeNodeScopeBeforelist,
        name: str,
        node_type: Type[AST],
    ) -> None:
        '''
        Initialize this beforelist scope.

        Parameters
        ----------
        beforelist : BeartypeNodeScopeBeforelist
            **Lexical scope beforelist.** See the class docstring.
        name : str
            Fully-qualified name of the current lexical scope (i.e.,
            ``.``-delimited absolute name of the module containing this scope
            followed by the relative basenames of zero or more classes and/or
            callables).
        node_type : type[AST]
            **Lexical scope node type.** See the class docstring.
        '''
        assert isinstance(beforelist, BeartypeNodeScopeBeforelist), (
            f'{repr(beforelist)} not beforelist scope.')
        assert isinstance(name, str), f'{repr(name)} not string.'
        assert isinstance(node_type, type), f'{repr(node_type)} not type.'
        assert issubclass(node_type, AST), f'{repr(node_type)} not node type.'

        # Classify all passed parameters.
        self.beforelist = beforelist
        self.name = name
        self.node_type = node_type

        # Record this beforelist to already be safely modifiable *ONLY* if this
        # is a global scope. See also the class docstring.
        self._is_beforelist_mutable = node_type is Module

    # ..................{ DUNDERS                            }..................
    def __repr__(self) -> str:

        return '\n'.join((
            f'{self.__class__.__name__}(\n',
            f'    beforelist={repr(self.beforelist)},\n',
            f'    name={repr(self.name)},\n',
            f'    node_type={repr(self.node_type)},\n',
            f'    _is_beforelist_mutable={repr(self._is_beforelist_mutable)},\n',
            f')',
        ))

    # ..................{ BEFORELIST                         }..................
    def map_imported_attr_name_subtrie(
        self, attr_basename: str, attr_subtrie: BeartypeDecorPlaceSubtrie) -> None:
        '''
        Map the passed unqualified basename of a problematic third-party
        attribute accessible to this scope (e.g., by an import or assignment
        statement) to the passed **imported attribute name subtrie** (i.e.,
        recursive tree structure whose nodes are the unqualified basenames of
        third-party attributes imported into a scope of the currently visited
        module such that these attributes are either themselves
        decorator-hostile decorators *or* submodules transitively defining
        decorator-hostile decorators).

        Parameters
        ----------
        attr_basename : str
            First unqualified basename of an attribute to be mapped.
        attr_subtrie : BeartypeDecorPlaceSubtrie
            Imported attribute name subtrie to map this basename to.
        '''
        assert isinstance(attr_basename, str), (
            f'{repr(attr_basename)} not string.')
        assert isinstance(attr_subtrie, NoneTypeOr[FrozenDict]), (
            f'{repr(attr_subtrie)} neither "None" nor frozen dictionary.')

        # Render this scope's beforelist safe for modification if this
        # beforelist is *NOT* yet safely modifiable.
        self._permute_beforelist_if_needed()

        # Map this unqualified basename of this attribute to this imported
        # attribute name subtrie.
        self.beforelist.imported_attr_name_trie[attr_basename] = attr_subtrie  # type: ignore[index]


    def _permute_beforelist_if_needed(self) -> None:
        '''
        Render this scope's beforelist safe for modification by external callers
        (e.g., to track problematic third-party imports) if this beforelist is
        *not* yet safely **modifiable** (i.e., if this beforelist is still a
        reference to a parent scope's beforelist and is thus *not* unique to
        this scope).

        For both space and time efficiency, beforelists obey the copy-on-write
        design pattern inspired by modern filesystems (e.g., Btrfs). Before
        attempting to modify the contents of this beforelist, callers should
        call this method to render this beforelist safe for modification.
        '''

        # If this beforelist is *NOT* yet safely modifiable, this beforelist is
        # still a reference to a parent scope's beforelist and is thus *NOT*
        # unique to this scope. In this case...
        if not self._is_beforelist_mutable:
            # Replace this shared beforelist with a new beforelist unique to
            # this scope, which may then be safely modified by callers.
            self.beforelist = self.beforelist.permute()

            # Record that this beforelist is now safely modifiable.
            self._is_beforelist_mutable = True
