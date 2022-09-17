#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2022 Beartype authors.
# See "LICENSE" for further details.

'''
**Decidedly Object-Oriented Runtime-checking (DOOR) callable type hint classes**
(i.e., :class:`beartype.door.TypeHint` subclasses implementing support for
:pep:`484`- and :pep:`585`-compliant ``Callable[...]`` type hints).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.door._doorcls import (
    TypeHint,
    _TypeHintSubscripted,
)
from beartype.roar import BeartypeDoorPepUnsupportedException
from beartype.typing import (
    Any,
    Tuple,
)
from beartype._data.hint.pep.sign.datapepsignset import (
    HINT_SIGNS_CALLABLE_PARAMS)
from beartype._util.cache.utilcachecall import property_cached
from beartype._util.hint.pep.proposal.pep484585.utilpep484585callable import (
    get_hint_pep484585_callable_params,
    get_hint_pep484585_callable_return,
)
from beartype._util.hint.pep.utilpepget import get_hint_pep_sign_or_none

# ....................{ SUBCLASSES                         }....................
# FIXME: Document all public and private attributes of this class, please.
class CallableTypeHint(_TypeHintSubscripted):
    '''
    **Callable type hint wrapper** (i.e., high-level object encapsulating a
    low-level :pep:`484`- or :pep:`585`-compliant ``Callable[...]`` type hint).

    Attributes (Private)
    --------
    '''

    # ..................{ INITIALIZERS                       }..................
    def _munge_args(self):
        '''
        Perform argument validation for a callable.
        '''

        # Note that a "Callable" without any arguments this may be unreachable,
        # as a bare "Callable" will go to "ClassTypeHint". Nonetheless, this
        # remains handled for completeness and safety.
        if len(self._args) == 0:  # pragma: no cover
            self._args = (..., Any,)
        else:
            # Parameters type hint(s) subscripting this callable type hint.
            self._callable_params = get_hint_pep484585_callable_params(
                self._hint)

            #FIXME: Should we classify this hint as well? Contemplate us up.
            # Return type hint subscripting this callable type hint.
            callable_return = get_hint_pep484585_callable_return(self._hint)

            # If this hint was first subscripted by an ellipsis (i.e., "...")
            # signifying a callable accepting an arbitrary number of parameters
            # of arbitrary types, strip this ellipsis. The ellipsis is *NOT* a
            # PEP-compliant type hint in general and thus *CANNOT* be wrapped by
            # the "TypeHint" wrapper.
            if self._callable_params is Ellipsis:
                # e.g. `Callable[..., Any]`
                self._callable_params = ()
            # Else...
            else:
                # Sign uniquely identifying this parameter list if any *OR*
                # "None" otherwise.
                hint_args_sign = get_hint_pep_sign_or_none(
                    self._callable_params)

                # If this hint was first subscripted by a PEP 612-compliant
                # type hint, raise an exception. *sigh*
                if hint_args_sign in HINT_SIGNS_CALLABLE_PARAMS:
                    raise BeartypeDoorPepUnsupportedException(
                        f'Type hint {repr(self._hint)} '
                        f'PEP 612 child type hint '
                        f'{repr(self._callable_params)} '
                        f'currently unsupported.'
                    )
                # Else, this hint was *NOT* first subscripted by a PEP
                # 612-compliant type hint.

            #FIXME: Note this will fail if "self._callable_params" is a PEP
            #612-compliant "typing.ParamSpec(...)" or "typing.Concatenate[...]"
            #object, as neither are tuples and thus *NOT* addable here.
            # Recreate the tuple of child type hints subscripting this parent
            # callable type hint from the tuple of argument type hints
            # introspected above. Why? Because the latter is saner than the
            # former in edge cases (e.g., ellipsis, empty argument lists).
            self._args = self._callable_params + (callable_return,)  # pyright: ignore[reportGeneralTypeIssues]

        # Perform superclass validation.
        super()._munge_args()

    # ..................{ PROPERTIES ~ bools                 }..................
    # FIXME: Remove this by instead adding support for ignoring ignorable
    # callable type hints to our core is_hint_ignorable() tester. Specifically:
    # * Ignore "Callable[..., {hint_ignorable}]" type hints, where "..." is the
    #  ellipsis singleton and "{hint_ignorable}" is any ignorable type hint.
    #  This has to be handled in a deep manner by:
    #  * Defining a new is_hint_pep484585_ignorable_or_none() tester in the
    #    existing "utilpep484585" submodule, whose initial implementation tests
    #    for *ONLY* ignorable callable type hints.
    #  * Import that tester in the "utilpeptest" submodule.
    #  * Add that tester to the "_IS_HINT_PEP_IGNORABLE_TESTERS" tuple.
    #  * Add example ignorable callable type hints to our test suite's data.
    @property
    def is_ignorable(self) -> bool:
        # Callable[..., Any] (or just `Callable`)
        return self.is_params_ignorable and self.is_return_ignorable


    @property
    def is_params_ignorable(self) -> bool:
        # Callable[..., ???]
        return self._args[0] is Ellipsis


    @property
    def is_return_ignorable(self) -> bool:
        # Callable[???, Any]
        return self.return_hint.is_ignorable

    # ..................{ PROPERTIES ~ hints                 }..................
    @property  # type: ignore
    @property_cached
    def param_hints(self) -> Tuple[TypeHint, ...]:
        '''
        Arguments portion of the callable.

        May be an empty tuple if the callable takes no arguments.
        '''

        return self._args_wrapped_tuple[:-1]


    @property
    def return_hint(self) -> TypeHint:
        '''
        Return type of the callable.
        '''

        return self._args_wrapped_tuple[-1]

    # ..................{ PRIVATE ~ testers                  }..................
    #FIXME: Internally comment us up, please.
    def _is_le_branch(self, branch: TypeHint) -> bool:

        # If the branch is not subscripted, then we assume it is subscripted
        # with ``Any``, and we simply check that the origins are compatible.
        if branch._is_args_ignorable:
            return issubclass(self._origin, branch._origin)
        if not isinstance(branch, CallableTypeHint):
            return False
        if not issubclass(self._origin, branch._origin):
            return False

        if not branch.is_params_ignorable and (
            (
                self.is_params_ignorable or
                len(self.param_hints) != len(branch.param_hints) or
                any(
                    self_arg > branch_arg
                    for self_arg, branch_arg in zip(
                        self.param_hints, branch.param_hints)
                )
            )
        ):
            return False

        # FIXME: Insufficient, sadly. There are *MANY* different type hints that
        # are ignorable and thus semantically equivalent to "Any". It's likely
        # we should just reduce this to a one-liner resembling:
        #    return self.return_hint <= branch.return_hint
        #
        # Are we missing something? We're probably missing something. *sigh*
        if not branch.is_return_ignorable:
            return (
                False
                if self.is_return_ignorable else
                self.return_hint <= branch.return_hint
            )

        return True
