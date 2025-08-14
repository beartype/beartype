#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype **afterlist scope dataclasses** (i.e., low-level classes aggregating
all metadata required to manage the afterlist automating decorator positioning
for :mod:`beartype.claw` import hooks).

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
from beartype._data.claw.dataclawafterlist import (
    CLAW_AFTERLIST_MODULE_TO_FUNC_DECORATOR_NAME,
    CLAW_AFTERLIST_MODULE_TO_TYPE_TO_METHOD_DECORATOR_NAME,
)
from collections import ChainMap

# ....................{ CLASSES                            }....................
#FIXME: Actually use this dataclass in the parent "BeartypeClawStateAfterlist"
#dataclass, please. *sigh*
class BeartypeAfterlistScope(object):
    '''
    **Beartype import hook afterlist scope** (i.e., low-level dataclass
    aggregating all metadata required to manage the afterlist automating
    decorator positioning for a specific global or local scope inspected by
    :mod:`beartype.claw` import hooks).

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
        assert isinstance(module_to_func_decorator_name, ChainMap), (
            f'{repr(module_to_func_decorator_name)} not chain map.')
        assert isinstance(module_to_type_to_method_decorator_name, ChainMap), (
            f'{repr(module_to_type_to_method_decorator_name)} not chain map.')
        #FIXME: Additionally assert all key-value pairs of these data structures
        #to be strings. *sigh*

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
    def permute(self) -> 'BeartypeAfterlistScope':
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
        BeartypeAfterlistScope
            Shallow copy of this afterlist scope.
        '''

        # Shallow copies of these chain maps of this parent scope, enabling the
        # caller to track imports safely across a new local scope.
        module_to_func_decorator_name_new = (
            self.module_to_func_decorator_name.new_child())
        module_to_type_to_method_decorator_name_new = (
            self.module_to_type_to_method_decorator_name.new_child())

        # Create and return a shallow copy of this dataclass.
        return BeartypeAfterlistScope(
            module_to_func_decorator_name=module_to_func_decorator_name_new,
            module_to_type_to_method_decorator_name=(
                module_to_type_to_method_decorator_name_new),
        )

# ....................{ FACTORIES                          }....................
def make_afterlist_scope_global() -> BeartypeAfterlistScope:
    '''
    **Beartype import hook afterlist global scope** (i.e., low-level dataclass
    aggregating all metadata required to manage the afterlist automating
    decorator positioning across all global scopes inspected by
    :mod:`beartype.claw` import hooks).
    '''

    # Create and return this afterlist global scope.
    return BeartypeAfterlistScope(
        module_to_func_decorator_name=(
            CLAW_AFTERLIST_MODULE_TO_FUNC_DECORATOR_NAME),
        module_to_type_to_method_decorator_name=(
            CLAW_AFTERLIST_MODULE_TO_TYPE_TO_METHOD_DECORATOR_NAME),
    )
