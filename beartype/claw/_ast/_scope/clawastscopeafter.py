#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype **abstract syntax tree (AST) scope afterlist** (i.e., low-level
dataclass aggregating all metadata required to manage the afterlist automating
decorator positioning for for lexical scopes recursively visited by AST
transformers).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.typing import (
    TYPE_CHECKING,
)
from beartype._data.typing.datatyping import (
    ChainMapStrToChainMapStrs,
    ChainMapStrToStrToChainMapStrs,
)
from beartype._data.claw.dataclawafter import (
    CLAW_AFTERLIST_MODULE_TO_FUNC_DECORATOR_NAMES,
    CLAW_AFTERLIST_MODULE_TO_TYPE_TO_METHOD_DECORATOR_NAMES,
)
from collections import ChainMap

# ....................{ CLASSES                            }....................
#FIXME: Unit test us up, please. *sigh*
class BeartypeNodeScopeAfterlist(object):
    '''
    Beartype **abstract syntax tree (AST) scope afterlist** (i.e., low-level
    dataclass aggregating all metadata required to manage the afterlist
    automating decorator positioning for lexical scopes recursively visited by
    AST transformers).

    Attributes
    ----------
    module_to_func_decorator_names : ChainMapStrToChainMapStrs
        **Afterlist decorator function chain map** (i.e., sequence of
        dictionaries mapping from the fully-qualified name of each third-party
        module to a set-like object implemented for simplicity as a nested chain
        map of the unqualified basename of each problematic decorator function
        of that module which the :func:`beartype.beartype` decorator *must*
        appear after within the chain of decorators for objects decorated by
        that problematic decorator).

        This instance variable is intentionally defined as a chain map rather
        than simple dictionary to transparently support both:

        * Global lexical scopes, which do *not* require a chain map.
        * Local lexical scopes, which require a chain map chaining imports
          across all nested local and global scopes (in that order from most to
          least nested).
    module_to_type_to_method_decorator_names : ChainMapStrToStrToChainMapStrs
        **Afterlist decorator method chain map** (i.e., sequence of dictionaries
        mapping from the fully-qualified name of each third-party module to the
        unqualified basename of each type in that module to a set-like object
        implemented for simplicity as a nested chain map of the unqualified
        basename of each problematic decorator method of that type which the
        :func:`beartype.beartype` decorator *must* appear after within the chain
        of decorators for objects decorated by that problematic decorator).

        This instance variable is intentionally defined as a chain map rather
        than simple dictionary for the same reason as the
        :attr:`.module_to_func_decorator_names` instance variable.
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
        'module_to_func_decorator_names',
        'module_to_type_to_method_decorator_names',
    )

    # Squelch false negatives from mypy. This is absurd. This is mypy. See:
    #     https://github.com/python/mypy/issues/5941
    if TYPE_CHECKING:
        module_to_func_decorator_names: ChainMapStrToChainMapStrs
        module_to_type_to_method_decorator_names: ChainMapStrToStrToChainMapStrs

    # ....................{ INITIALIZERS                   }....................
    def __init__(
        self,
        module_to_func_decorator_names: ChainMapStrToChainMapStrs,
        module_to_type_to_method_decorator_names: ChainMapStrToStrToChainMapStrs,
    ) -> None:
        '''
        Initialize this scope afterlist.

        Parameters
        ----------
        module_to_func_decorator_names : ChainMapStrToChainMapStrs
            **Afterlist decorator function chain map.** See the class docstring.
        module_to_type_to_method_decorator_names : ChainMapStrToStrToChainMapStrs
            **Afterlist decorator method chain map.** See the class docstring.
        '''

        # Shallowly type-check these data structures to be chain maps.
        assert isinstance(module_to_func_decorator_names, ChainMap), (
            f'{repr(module_to_func_decorator_names)} not chain map.')
        assert isinstance(module_to_type_to_method_decorator_names, ChainMap), (
            f'{repr(module_to_type_to_method_decorator_names)} not chain map.')

        # Deeply type-check the contents of these data structures.
        assert all(
            (
                isinstance(module_name, str) and
                isinstance(func_decorator_name, str)
            )
            for module_name, func_decorator_names in (
                module_to_func_decorator_names.items())
            for func_decorator_name in func_decorator_names
        ), (
            f'{repr(module_to_func_decorator_names)} not '
            f'"ChainMap[str, ChainMap[str, object]]".'
        )
        assert all(
            (
                isinstance(module_name, str) and
                isinstance(type_name, str) and
                isinstance(method_decorator_name, str)
            )
            for module_name, type_to_method_decorator_name in (
                module_to_type_to_method_decorator_names.items())
            for type_name, method_decorator_names in (
                type_to_method_decorator_name.items())
            for method_decorator_name in method_decorator_names
        ), (
            f'{repr(module_to_type_to_method_decorator_names)} not '
            f'"ChainMap[str, ChainMap[str, ChainMap[str, object]]]".'
        )

        # Classify all passed parameters.
        self.module_to_func_decorator_names = module_to_func_decorator_names
        self.module_to_type_to_method_decorator_names = (
            module_to_type_to_method_decorator_names)

    # ..................{ DUNDERS                            }..................
    def __repr__(self) -> str:

        return '\n'.join((
            f'{self.__class__.__name__}(\n',
            f'    module_to_func_decorator_names={repr(self.module_to_func_decorator_names)},\n',
            f'    module_to_type_to_method_decorator_names='
            f'{repr(self.module_to_type_to_method_decorator_names)},\n',
            f')',
        ))

    # ..................{ PERMUTERS                          }..................
    def permute(self) -> 'BeartypeNodeScopeAfterlist':
        '''
        Shallow copy of this scope afterlist, typically called to produce a
        mutable copy of this scope afterlist isolated to a new local (e.g.,
        function) scope being visited by the abstract syntax tree (AST)
        transformer tracking problematic third-party imports.

        Specifically, this shallow copy permutes this scope as follows:

        * The :attr:`.module_to_func_decorator_names` instance variable is
          shallowly copied by calling its :meth:`.ChainMap.new_child` method,
          whose :attr:`.ChainMap.maps` list is then prefixed by a new empty
          dictionary enabling callers to track local imports safely.
        * The :attr:`.module_to_type_to_method_decorator_names` instance variable
          is shallowly copied in the same manner.

        Returns
        -------
        BeartypeNodeScopeAfterlist
            Shallow copy of this scope afterlist.
        '''

        # Shallow copies of these chain maps of this parent scope, enabling the
        # caller to track imports safely across a new local scope.
        module_to_func_decorator_names_new = (
            self.module_to_func_decorator_names.new_child())
        module_to_type_to_method_decorator_names_new = (
            self.module_to_type_to_method_decorator_names.new_child())

        # Create and return a shallow copy of this dataclass.
        return BeartypeNodeScopeAfterlist(
            module_to_func_decorator_names=module_to_func_decorator_names_new,
            module_to_type_to_method_decorator_names=(
                module_to_type_to_method_decorator_names_new),
        )

# ....................{ FACTORIES                          }....................
#FIXME: Unit test us up, please.
def make_node_scope_afterlist_global() -> BeartypeNodeScopeAfterlist:
    '''
    Beartype **abstract syntax tree (AST) global scope afterlist** (i.e.,
    low-level dataclass aggregating all metadata required to manage the
    afterlist automating decorator positioning for the global scope of the
    module being recursively visited by the current AST transformer).

    Returns
    -------
    BeartypeNodeScopeAfterlist
        AST global scope afterlist of the currently visited module.
    '''

    # Afterlist decorator function mapping, defined as a mutable chain map
    # coerced from this immutable frozen dictionary singleton.
    module_to_func_decorator_names = ChainMap({
        # Coerce this immutable frozen set of decorator function names into a
        # mutable chain map of these names via the usual dict.fromkeys() trick,
        # well-known to be both the simplest *AND* most efficient means of
        # stuffing a set into a dictionary.
        #
        # Note that the "None" value is both arbitrary and ignorable.
        module_name: ChainMap(dict.fromkeys(func_decorator_names, None))
        for module_name, func_decorator_names in (
            CLAW_AFTERLIST_MODULE_TO_FUNC_DECORATOR_NAMES.items())
    })

    # Afterlist decorator method mapping, defined as a mutable chain map
    # coerced from this immutable frozen dictionary singleton.
    #
    # Note that doing so is complicated by the fact that this parent frozen
    # dictionary maps from strings to nested frozen dictionaries, which *MUST*
    # also be coerced into nested chain maps.
    module_to_type_to_method_decorator_names = ChainMap({
        afterlist_module_name: {
            # Coerce this immutable frozen set of decorator method names into a
            # mutable chain map of these names via the above trick.
            type_name: ChainMap(dict.fromkeys(method_decorator_names, None))
            for type_name, method_decorator_names in (
                type_to_method_decorator_names.items())
        }
        for afterlist_module_name, type_to_method_decorator_names in (
            CLAW_AFTERLIST_MODULE_TO_TYPE_TO_METHOD_DECORATOR_NAMES.items())
    })

    # Create and return this afterlist global scope.
    return BeartypeNodeScopeAfterlist(
        module_to_func_decorator_names=module_to_func_decorator_names,
        module_to_type_to_method_decorator_names=(
            module_to_type_to_method_decorator_names),
    )
