#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`593`-compliant **type metahint reducers** (i.e., low-level
callables converting the higher-level :obj:`typing.TypeAlias` type hint
singleton to lower-level type hints more readily consumable by :mod:`beartype`).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ TODO                               }....................
#FIXME: The current reduce_hint_pep613() reducer defined below is overly
#permissive.
#* If the active Python interpreter targets Python >= 3.12 and thus supports
#  PEP 695, issue a non-fatal deprecation warning. PEP 695 officially deprecates
#  PEP 613.

# ....................{ IMPORTS                            }....................
from beartype.roar import (
    BeartypeDecorHintPep613Exception,
    BeartypeDecorHintPep613DeprecationWarning,
)
from beartype._check.cls.call.calldataabc import BeartypeCallDataABC
from beartype._check.cls.hint.hintsane import HintSane
from beartype._util.error.utilerrwarn import issue_warning
from typing import Optional

# ....................{ REDUCERS                           }....................
def reduce_hint_pep613(
    call_curr: BeartypeCallDataABC,
    hint: object,
    hint_parent_sane: Optional[HintSane],
    pith_name: Optional[str],
    exception_prefix: str,
    **kwargs
) -> object:
    '''
    Reduce the passed :pep:`613`-compliant **type alias** (i.e.,
    :obj:`typing.TypeAlias` type hint singleton) to the ignorable
    :class:`object` superclass.

    This reducer effectively ignores *all* :obj:`typing.TypeAlias` type hint
    singletons, which convey *no* meaningful metadata or semantics. Frankly,
    it's unclear why :pep:`613` even exists. The CPython developer community
    felt similarly, which is why :pep:`695` type aliases deprecate :pep:`613`.

    This reducer is intentionally *not* memoized (e.g., by the
    ``callable_cached`` decorator), as reducers cannot be memoized.

    Parameters
    ----------
    call_curr : BeartypeCallDataABC
        **Beartype call metadata** (i.e., dataclass aggregating *all* common
        metadata encapsulating the user-defined callable, type, or statement
        currently being type-checked by the end user).
    hint : object
        Typed dictionary to be reduced.
    hint_parent_sane : Optional[HintSane]
        Either:

        * If the passed hint is a **root** (i.e., top-most parent hint of a tree
          of child hints), :data:`None`.
        * Else, the passed hint is a **child** of some parent hint. In this
          case, the **sanified parent type hint metadata** (i.e., immutable and
          thus hashable object encapsulating *all* metadata previously returned
          by :mod:`beartype._check.convert.convmain` sanifiers after sanitizing
          the possibly PEP-noncompliant parent hint of this child hint into a
          fully PEP-compliant parent hint).
    pith_name : Optional[str], default: None
        Either:

        * If this hint annotates a parameter of some callable, the name of that
          parameter.
        * If this hint annotates the return of some callable, ``"return"``.
        * Else, :data:`None`.
    exception_prefix : str
        Substring prefixing exception messages raised by this reducer.

    All remaining passed arguments are silently ignored.

    Returns
    -------
    object
        Lower-level type hint currently supported by :mod:`beartype`.

    Warns
    -----
    BeartypeDecorHintPep613DeprecationWarning
        :pep:`613`-compliant type aliases have been officially deprecated by
        :pep:`695`-compliant type aliases.
    '''

    # This hint subscripts a parent hint as a child hint, raise an exception.
    # The "typing.TypeAlias" singleton is valid *ONLY* as a root hint.
    if hint_parent_sane is not None:
        raise BeartypeDecorHintPep613Exception(
            f'{exception_prefix}'
            f'PEP 613 type alias {repr(hint)} erroneously subscripts '
            f'parent type hint {repr(hint_parent_sane.hint)}, '
            f'but valid only as '
            f'root type hint subscripting *NO* parent type hint.'
        )
    # Else, this hint subscripts no parent and is thus a root hint.
    #
    # If this root hint annotates either the return *OR* an arbitrary parameter
    # of some callable, raise an exception. The "typing.TypeAlias" singleton is
    # valid *ONLY* as the root hint of a PEP 526-compliant annotated variable
    # assignment.
    elif pith_name is not None:
        raise BeartypeDecorHintPep613Exception(
            f'{exception_prefix}'
            f'PEP 613 type alias {repr(hint)} erroneously annotates '
            f'callable {repr(call_curr.decoratee)} '
            f'parameter or return "{pith_name}", '
            f'but valid only as root type hint of '
            f'PEP 526-compliant annotated variable assignments: e.g.,\n'
            f'    muh_global_var: TypeAlias = list[str]  # <-- *DIS IZ GUD*'
        )
    # Else, this root hint annotates neither the return *NOR* an arbitrary
    # parameter of some callable and thus annotates a PEP 526-compliant
    # annotated variable assignment.

    #FIXME: Improve this advice, please. When we wrote this a literal lifetime
    #ago, we didn't realize that "typing_extensions" astonishingly provides a
    #backport of the low-level C-based "typing.TypeAliasType" type available in
    #Python >= 3.12 as a high-level pure-Python
    #"typing_extensions.TypeAliasType" class available across all Python
    #versions. It's... pretty astonishing, actually! Instantiating the
    #"typing_extensions.TypeAliasType" class allows users to *MUCH* more
    #conveniently define PEP 695-compliant type aliases in older Python
    #versions. PEP 695 *DEFINITELY* should have at least mentioned this, as this
    #is essential information that makes PEP 695 *MUCH* more amenable. The
    #syntax is a bit wonky, but that's understandable:
    #    # This Python >= 3.12-specific logic...
    #    type ListOrSet[T] = list[T] | set[T]
    #    # ...is equivalent to this version-agnostic logic:
    #    T = TypeVar("T")
    #    ListOrSet = TypeAliasType("ListOrSet", list[T] | set[T], type_params=(T,))
    #FIXME: Unit test that this warning is actually issued. Doing so is probably
    #*ONLY* feasible from within a "beartype.claw"-based unit test. *sigh*

    # Emit a non-fatal deprecation warning.
    issue_warning(
        warning_cls=BeartypeDecorHintPep613DeprecationWarning,
        message=(
            f'{exception_prefix}'
            f'PEP 613 type alias {repr(hint)} deprecated by PEP 695. '
            f'Consider either:\n'
            f'* Requiring Python >= 3.12 and refactoring PEP 613 type aliases '
            f'into PEP 695 type aliases. Note that Python < 3.12 will hate you '
            f'for this: e.g.,\n'
            f'    # Instead of this...\n'
            f'    from typing import TypeAlias\n'
            f'    alias_name: TypeAlias = alias_value\n'
            f'\n'
            f'    # ..."just" do this. Congrats. You destroyed your codebase.\n'
            f'    type alias_name = alias_value\n'
            f'* Refactoring PEP 613 type aliases into PEP 484 '
            f'"typing.NewType"-based type aliases. Note that static '
            f'type-checkers (e.g., mypy, pyright, Pyre) will hate you for '
            f'this: e.g.,\n'
            f'    # Instead of this...\n'
            f'    from typing import TypeAlias\n'
            f'    alias_name: TypeAlias = alias_value\n'
            f'\n'
            f'    # ..."just" do this. Congrats. You destroyed your codebase.\n'
            f'    from typing import NewType\n'
            f'    alias_name = NewType("alias_name", alias_value)\n'
            f'\n'
            f'Combine the above two approaches via The Ultimate Type Alias '
            f'(TUTA), a hidden ninja technique that supports all Python '
            f'versions and static type-checkers but may cause coworker heads '
            f'to pop off like in that one Kingsman scene:\n'
            f'    # Instead of this...\n'
            f'    from typing import TypeAlias\n'
            f'    alias_name: TypeAlias = alias_value\n'
            f'\n'
            f'    # ..."just" do this. If you think this sucks, know that you are not alone.\n'
            f'    from typing import TYPE_CHECKING, NewType, TypeAlias  # <-- sus af\n'
            f'    from sys import version_info  # <-- code just got real\n'
            f'    if TYPE_CHECKING:  # <-- if static type-checking, then PEP 613\n'
            f'        alias_name: TypeAlias = alias_value  # <-- grimdark coding style\n'
            f'    elif version_info >= (3, 12):  # <-- if Python >= 3.12, then PEP 695\n'
            f'        exec("type alias_name = alias_value")  # <-- eldritch abomination\n'
            f'    else:  # <-- if Python < 3.12, then PEP 484\n'
            f'        alias_name = NewType("alias_name", alias_value)  # <-- coworker gives up here\n'
        ),
    )

    # Reduce *ALL* PEP 613 type hints to an arbitrary ignorable type hint.
    return object
