#!/usr/bin/env python3 --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2022 Beartype authors.
# See "LICENSE" for further details.

'''
**Decidedly Object-Oriented Runtime-checking (DOOR) callable type hint classes**
(i.e., :class:`beartype.door.TypeHint` subclasses implementing support for
:pep:`484`- and :pep:`585`-compliant ``Tuple[...]`` type hints).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.door._doorcls import (
    TypeHint,
    _TypeHintSubscripted,
)
from beartype.typing import (
    Any,
)

# ....................{ SUBCLASSES                         }....................
# FIXME: Document all public and private attributes of this class, please.
class _TupleTypeHint(_TypeHintSubscripted):
    '''
    **Tuple type hint wrapper** (i.e., high-level object encapsulating a
    low-level :pep:`484`- or :pep:`585`-compliant ``Tuple[...]`` type hint).

    Attributes (Private)
    --------
    '''

    # ..................{ VARIABLES                          }..................
    #FIXME: Non-ideal. These two assignments actually define new *CLASS* rather
    #than *INSTANCE* variables. To define the latter, push these assignments
    #into the existing _munge_args() method defined below, please.
    _is_variable_length: bool = False

    #FIXME: Additionally, this is non-ideal. The superclass __len__() method
    #already returns 0 as expected for "Tuple[()]" type hints. Excise us up!
    _is_empty_tuple: bool = False

    # ..................{ INITIALIZERS                       }..................
    def _munge_args(self):
        """
        Perform argument validation for a tuple.

        Specifically, remove any PEP-noncompliant type hints from the arguments,
        and set internal flags accordingly.
        """

        # e.g. `Tuple` without any arguments
        # This may be unreachable, (since a bare Tuple will go to
        # ClassTypeHint) but it's here for completeness and safety.
        if len(self._args) == 0:  # pragma: no cover
            self._is_variable_length = True
            self._args = (Any,)
        elif len(self._args) == 1 and self._args[0] == ():
            self._is_empty_tuple = True
            self._args = ()
        elif len(self._args) == 2 and self._args[1] is Ellipsis:
            self._is_variable_length = True
            self._args = (self._args[0],)

        super()._munge_args()

    # ..................{ PROPERTIES                         }..................
    #FIXME: Docstring us up, please. This is actually quite valuable.
    #FIXME: Actually, it might be preferable to define two distinct subclasses:
    #* "class _TypeHintTupleVariadic(_TypeHintSequence)", handling variadic
    #  tuple type hints of the form "Tuple[T, ...]".
    #* "class _TypeHintTupleFixed(_TypeHintSubscripted)", handling fixed-length
    #  tuple type hints.
    #
    #Why? Because variadic and fixed-length tuple type hints have *NOTHING*
    #semantically to do with one another. All they share is the common prefix
    #"Tuple[". Aside from that, everything is dissimilar. Indeed, most of the
    #logic below (especially _is_le_branch(), which is kinda cray-cray) would
    #strongly benefit from separating this class into two subclasses.
    #
    #Note that implementing this division will probably require generalizing
    #the TypeHint.__new__() method to support this division.
    @property
    def is_variable_length(self) -> bool:
        # Tuple[T, ...]
        return self._is_variable_length

    # ..................{ PRIVATE ~ properties               }..................
    @property
    def _is_args_ignorable(self) -> bool:
        # Tuple[Any, ...]  or just Tuple
        return (
            self.is_variable_length and
            bool(self._args) and

            #FIXME: Insufficient. Test whether this argument is actually
            #ignorable, please.
            self._args[0] is Any
        )

    # ..................{ PRIVATE ~ testers                  }..................
    def _is_le_branch(self, branch: TypeHint) -> bool:
        if branch._is_args_ignorable:
            return issubclass(self._origin, branch._origin)

        if not isinstance(branch, _TupleTypeHint):
            return False
        if self._is_args_ignorable:
            return False
        if branch._is_empty_tuple:
            return self._is_empty_tuple

        if branch.is_variable_length:
            branch_type = branch._args_wrapped_tuple[0]
            if self.is_variable_length:
                return branch_type <= self._args_wrapped_tuple[0]
            return all(child <= branch_type for child in self._args_wrapped_tuple)

        if self.is_variable_length:
            return (
                branch.is_variable_length
                and self._args_wrapped_tuple[0] <= branch._args_wrapped_tuple[0]
            )

        if len(self._args) != len(branch._args):
            return False

        return all(
            self_child <= branch_child
            for self_child, branch_child in zip(
                self._args_wrapped_tuple, branch._args_wrapped_tuple
            )
        )
