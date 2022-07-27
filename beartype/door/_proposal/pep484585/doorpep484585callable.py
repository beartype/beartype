#!/usr/bin/env python3 --------------------( LICENSE                            )--------------------
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
from beartype._data.hint.pep.sign.datapepsignset import HINT_SIGNS_CALLABLE_PARAMS
from beartype._util.hint.pep.proposal.pep484585.utilpep484585callable import (
    get_hint_pep484585_callable_params,
    get_hint_pep484585_callable_return,
)
from beartype._util.hint.pep.utilpepget import get_hint_pep_sign_or_none

# ....................{ SUBCLASSES                         }....................
# FIXME: Document all public and private attributes of this class, please.
class _TypeHintCallable(_TypeHintSubscripted):
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

        self._takes_any_args = False

        if len(self._args) == 0:  # pragma: no cover
            # e.g. `Callable` without any arguments this may be unreachable,
            # (since a bare Callable will go to _TypeHintClass) but it's here
            # for completeness and safety.
            self._takes_any_args = True

            # FIXME: Actually, pretty sure this instead needs to be:
            #    self._args = (..., Any,)  # returns any
            self._args = (Any,)  # returns any
        else:
            # Parameters type hint(s) subscripting this callable type hint.
            self._callable_params = get_hint_pep484585_callable_params(
                self._hint)

            #FIXME: Should we classify this hint as well? Contemplate us up.
            # Return type hint subscripting this callable type hint.
            callable_return = get_hint_pep484585_callable_return(self._hint)

            # If this hint was first subscripted by an ellipsis (i.e., "...")
            # signifying a callable accepting an arbitrary number of parameters
            # of arbitrary types...
            if self._callable_params is Ellipsis:
                # e.g. `Callable[..., Any]`
                self._takes_any_args = True
                self._callable_params = ()  # Ellipsis in not a type, so strip it here.
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

    # ..................{ PROPERTIES                         }..................
    # FIXME: Makes sense -- but let's rename to, say, params_typehint(). Note we
    # intentionally choose "params" rather than "args" here for disambiguity with
    # the low-level "hint.__args__" tuple.
    # FIXME: Inefficient if frequently accessed. Consider:
    # * Improving our @callable_cached decorator to efficiently handle
    #  properties.
    # * Prepend @callable_cached onto this decorator list: e.g.,
    #      @callable_cached
    #      @property
    #      def arg_types(self) -> Tuple[TypeHint, ...]:
    @property
    def arg_types(self) -> Tuple[TypeHint, ...]:
        '''
        Arguments portion of the callable.

        May be an empty tuple if the callable takes no arguments.
        '''

        return self._args_wrapped[:-1]


    # FIXME: Makes sense -- but let's rename to, say, return_typehint().
    @property
    def return_type(self) -> TypeHint:
        # the return type of the callable
        return self._args_wrapped[-1]


    # FIXME: Rename to is_params_ignorable() for orthogonality with
    # is_args_ignorable().
    # FIXME: Refactor the trivially decidable "_takes_any_args" boolean away,
    # please. Instead, just:
    # * Remove "_takes_any_args".
    # * Prepend @callable_cached onto this decorator list as above.
    # * Refactor this property to resemble:
    #      @callable_cached
    #      @property
    #      def is_params_ignorable(self) -> bool:
    #          # Callable[..., ]
    #          return hint._args[0] is Ellipsis
    # FIXME: Alternately, let's assume that "TypeHint(Ellipsis)" behaves as
    # expected. It probably doesn't. So, we'll need to first do something about
    # that. Then this just trivially reduces to:
    #    return hint.params_typehint.is_ignorable()
    #
    # In other words, *JUST EXCISE THIS.* Callers should just call
    # hint.params_typehint.is_ignorable() instead.
    @property
    def takes_any_args(self) -> bool:
        # Callable[..., ]
        return self._takes_any_args

    # FIXME: Rename to is_return_ignorable() for orthogonality.
    # FIXME: Moreover, this test is actually insufficient. There are *MANY*
    # different type hints that are ignorable and thus semantically equivalent to
    # "Any". We will probably need to refactor this to resemble:
    #    @callable_cached
    #    @property
    #    def is_return_ignorable(self) -> bool:
    #        return self.return_typehint.is_ignorable()
    #
    # In other words, *JUST EXCISE THIS.* Callers should just call
    # hint.return_typehint.is_ignorable() instead.
    @property
    def returns_any(self) -> bool:
        # Callable[..., Any]
        return self._args[-1] is Any

    # ..................{ PRIVATE ~ properties               }..................
    # FIXME: Refactor to resemble:
    #    return self.is_params_ignorable and self.is_return_ignorable
    # FIXME: Actually, is this even needed? Pretty sure the superclass
    # implementation should implicitly handle this already, assuming the
    # superclass implementation defers to the new "TypeHint.is_ignorable"
    # property... which it almost certainly doesn't yet. *sigh*
    # FIXME: Additionally, we'll need to add support for ignoring ignorable
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
    def _is_args_ignorable(self) -> bool:
        # Callable[..., Any] (or just `Callable`)
        return self.takes_any_args and self.returns_any

    # ..................{ PRIVATE ~ testers                  }..................
    def _is_le_branch(self, branch: TypeHint) -> bool:

        # If the branch is not subscripted, then we assume it is subscripted
        # with ``Any``, and we simply check that the origins are compatible.
        if branch._is_args_ignorable:
            return issubclass(self._origin, branch._origin)
        if not isinstance(branch, _TypeHintCallable):
            return False
        if not issubclass(self._origin, branch._origin):
            return False

        if not branch.takes_any_args and (
            (
                self.takes_any_args or
                len(self.arg_types) != len(branch.arg_types) or
                any(
                    self_arg > branch_arg
                    for self_arg, branch_arg in zip(
                        self.arg_types, branch.arg_types)
                )
            )
        ):
            return False

        # FIXME: Insufficient, sadly. There are *MANY* different type hints that
        # are ignorable and thus semantically equivalent to "Any". It's likely
        # we should just reduce this to a one-liner resembling:
        #    return self.return_type <= branch.return_type
        #
        # Are we missing something? We're probably missing something. *sigh*
        if not branch.returns_any:
            return (
                False
                if self.returns_any else
                self.return_type <= branch.return_type
            )

        return True
