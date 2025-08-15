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
    ChainMapStrToStr,
    ChainMapStrToStrToStr,
)
from beartype._data.claw.dataclawafter import (
    CLAW_AFTERLIST_MODULE_TO_FUNC_DECORATOR_NAME,
    CLAW_AFTERLIST_MODULE_TO_TYPE_TO_METHOD_DECORATOR_NAME,
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
    module_to_func_decorator_name : ChainMapStrToStr
        **Afterlist decorator function chain map** (i.e., sequence of
        dictionaries mapping from the fully-qualified name of each third-party
        module to the unqualified basename of each decorator function of that
        module which the :func:`beartype.beartype` decorator *must* appear after
        within the chain of decorators for objects decorated by that decorator).

        This instance variable is intentionally defined as a chain map rather
        than simple dictionary to transparently support both:

        * Global lexical scopes, which do *not* require a chain map.
        * Local lexical scopes, which require a chain map chaining imports
          across all nested local and global scope (in that order).
    module_to_type_to_method_decorator_name : ChainMapStrToStrToStr
        **Afterlist decorator method chain map** (i.e., sequence of dictionaries
        mapping from the fully-qualified name of each third-party module to the
        unqualified basename of each type in that module to the unqualified
        basename of each decorator method of that type which the
        :func:`beartype.beartype` decorator *must* appear after within the chain
        of decorators for objects decorated by that decorator).

        This instance variable is intentionally defined as a chain map rather
        than simple dictionary for the same reason as the
        :attr:`.module_to_func_decorator_name` instance variable.
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
        'module_to_func_decorator_name',
        'module_to_type_to_method_decorator_name',
    )

    # Squelch false negatives from mypy. This is absurd. This is mypy. See:
    #     https://github.com/python/mypy/issues/5941
    if TYPE_CHECKING:
        module_to_func_decorator_name: ChainMapStrToStr
        module_to_type_to_method_decorator_name: ChainMapStrToStrToStr

    # ....................{ INITIALIZERS                   }....................
    def __init__(
        self,
        module_to_func_decorator_name: ChainMapStrToStr,
        module_to_type_to_method_decorator_name: ChainMapStrToStrToStr,
    ) -> None:
        '''
        Initialize this afterlist scope.

        Parameters
        ----------
        module_to_func_decorator_name : ChainMapStrToStr
            **Afterlist decorator function chain map.** See the class docstring.
        module_to_type_to_method_decorator_name : ChainMapStrToStrToStr
            **Afterlist decorator method chain map.** See the class docstring.
        '''

        # Shallowly type-check these data structures to be chain maps.
        assert isinstance(module_to_func_decorator_name, ChainMap), (
            f'{repr(module_to_func_decorator_name)} not chain map.')
        assert isinstance(module_to_type_to_method_decorator_name, ChainMap), (
            f'{repr(module_to_type_to_method_decorator_name)} not chain map.')

        # Deeply type-check the contents of these data structures.
        assert all(
            (
                isinstance(module_name, str) and
                isinstance(func_decorator_name, str)
            )
            for module_name, func_decorator_name in (
                module_to_func_decorator_name.items())
        ), f'{repr(module_to_func_decorator_name)} not "ChainMap[str, str]".'
        assert all(
            (
                isinstance(module_name, str) and
                isinstance(type_name, str) and
                isinstance(method_decorator_name, str)
            )
            for module_name, type_to_method_decorator_name in (
                module_to_type_to_method_decorator_name.items())
            for type_name, method_decorator_name in (
                type_to_method_decorator_name.items())
        ), (
            f'{repr(module_to_type_to_method_decorator_name)} not '
            f'"ChainMap[str, ChainMap[str, str]]".'
        )

        # Classify all passed parameters.
        self.module_to_func_decorator_name = module_to_func_decorator_name
        self.module_to_type_to_method_decorator_name = (
            module_to_type_to_method_decorator_name)

    # ..................{ DUNDERS                            }..................
    def __repr__(self) -> str:

        return '\n'.join((
            f'{self.__class__.__name__}(\n',
            f'    module_to_func_decorator_name={repr(self.module_to_func_decorator_name)},\n',
            f'    module_to_type_to_method_decorator_name={repr(self.module_to_type_to_method_decorator_name)},\n',
            f')',
        ))

    # ..................{ PERMUTERS                          }..................
    def permute(self) -> 'BeartypeNodeScopeAfterlist':
        '''
        Shallow copy of this afterlist scope, typically called to produce a
        mutable copy of this afterlist scope isolated to a new local (e.g.,
        function) scope being visited by the abstract syntax tree (AST)
        transformer tracking problematic third-party imports.

        Specifically, this shallow copy permutes this scope as follows:

        * The :attr:`.module_to_func_decorator_name` instance variable is
          shallowly copied by calling its :meth:`.ChainMap.new_child` method,
          whose :attr:`.ChainMap.maps` list is then prefixed by a new empty
          dictionary enabling callers to track local imports safely.
        * The :attr:`.module_to_type_to_method_decorator_name` instance variable
          is shallowly copied in the same manner.

        Returns
        -------
        BeartypeNodeScopeAfterlist
            Shallow copy of this afterlist scope.
        '''

        # Shallow copies of these chain maps of this parent scope, enabling the
        # caller to track imports safely across a new local scope.
        module_to_func_decorator_name_new = (
            self.module_to_func_decorator_name.new_child())
        module_to_type_to_method_decorator_name_new = (
            self.module_to_type_to_method_decorator_name.new_child())

        # Create and return a shallow copy of this dataclass.
        return BeartypeNodeScopeAfterlist(
            module_to_func_decorator_name=module_to_func_decorator_name_new,
            module_to_type_to_method_decorator_name=(
                module_to_type_to_method_decorator_name_new),
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
    module_to_func_decorator_name = ChainMap(dict(
        CLAW_AFTERLIST_MODULE_TO_FUNC_DECORATOR_NAME))

    # Afterlist decorator method mapping, defined as a mutable chain map
    # coerced from this immutable frozen dictionary singleton.
    #
    # Note that doing so is complicated by the fact that this parent frozen
    # dictionary maps from strings to nested frozen dictionaries, which *MUST*
    # also be coerced into nested chain maps.
    module_to_type_to_method_decorator_name_dict = {
        afterlist_module_name: ChainMap(dict(type_to_method_decorator_name))
        for afterlist_module_name, type_to_method_decorator_name in (
            CLAW_AFTERLIST_MODULE_TO_TYPE_TO_METHOD_DECORATOR_NAME.items())
    }
    module_to_type_to_method_decorator_name = ChainMap(
        module_to_type_to_method_decorator_name_dict)

    # Create and return this afterlist global scope.
    return BeartypeNodeScopeAfterlist(
        module_to_func_decorator_name=module_to_func_decorator_name,
        module_to_type_to_method_decorator_name=(
            module_to_type_to_method_decorator_name),
    )
