#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2024 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype Decidedly Object-Oriented Runtime-checking (DOOR) procedural
type-checkers** (i.e., high-level functions type-checking arbitrary objects
against type hints at *any* time during the lifecycle of the active Python
process).
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# CAUTION: This submodule intentionally does *not* import the
# @beartype.beartype decorator. Why? Because that decorator conditionally
# reduces to a noop under certain contexts (e.g., `python3 -O` optimization),
# whereas the API defined by this submodule is expected to unconditionally
# operate as expected regardless of the current context.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from beartype._check.checkmake import (
    make_func_raiser,
    make_func_tester,
)
from beartype._conf.confcls import (
    BEARTYPE_CONF_DEFAULT,
    BeartypeConf,
)

#FIXME: Consider:
#* Once we've gone that far, though, *EVERYBODY* (including us) will then
#  want us to define a new
#  "BeartypeConf.violation_type: Optional[Type[Exception]] = None" option
#  conveniently controlling the three distinct
#  "violation_door_type", "violation_param_type", and
#  "violation_return_type" options. *sigh*
#* To preserve backward compatibility, if we notice that a user has
#  explicitly passed "violation_param_type" and "violation_return_type" but
#  *NOT* "violation_door_type", we can then emit a non-fatal warning
#  encouraging them to instead pass "violation_type".

# ....................{ VALIDATORS                         }....................
def die_if_unbearable(
    # Mandatory flexible parameters.
    obj: object,
    hint: object,

    # Optional keyword-only parameters.
    *,
    conf: BeartypeConf = BEARTYPE_CONF_DEFAULT,
) -> None:
    '''
    Raise an exception if the passed arbitrary object violates the passed type
    hint under the passed beartype configuration.

    Parameters
    ----------
    obj : object
        Arbitrary object to be tested against this hint.
    hint : object
        Type hint to test this object against.
    conf : BeartypeConf, optional
        **Beartype configuration** (i.e., self-caching dataclass encapsulating
        all settings configuring type-checking for the passed object). Defaults
        to ``BeartypeConf()``, the default :math:`O(1)` constant-time
        configuration.

    Raises
    ------
    beartype.roar.BeartypeDecorHintNonpepException
        If this hint is *not* PEP-compliant (i.e., complies with *no* Python
        Enhancement Proposals (PEPs) currently supported by :mod:`beartype`).
    beartype.roar.BeartypeDecorHintPepUnsupportedException
        If this hint is currently unsupported by :mod:`beartype`.
    beartype.roar.BeartypeDoorHintViolation
        If this object violates this hint.

    Examples
    --------
        >>> from beartype.door import die_if_unbearable
        >>> die_if_unbearable(['And', 'what', 'rough', 'beast,'], list[str])
        >>> die_if_unbearable(['its', 'hour', 'come', 'round'], list[int])
        beartype.roar.BeartypeDoorHintViolation: Object ['its', 'hour', 'come',
        'round'] violates type hint list[int], as list index 0 item 'its' not
        instance of int.
    '''
    # conf._is_debug = True

    # Memoized low-level type-checking raiser function either raising an
    # exception or emitting a warning only if the passed object passed violates
    # the type hint passed to this high-level type-checking raiser function.
    #
    # Note that parameters are intentionally passed positionally for efficiency.
    # Since make_func_raiser() is memoized, passing parameters by keyword would
    # raise a non-fatal
    # "_BeartypeUtilCallableCachedKwargsWarning" warning.
    func_raiser = make_func_raiser(hint, conf)

    # Either raise an exception or emit a warning only if the passed object
    # violates this hint.
    func_raiser(obj)  # pyright: ignore[reportUnboundVariable]

# ....................{ TESTERS                            }....................
def is_subhint(subhint: object, superhint: object) -> bool:
    '''
    :data:`True` only if the first passed hint is a **subhint** of the second
    passed hint, in which case this second hint is a **superhint** of this first
    hint.

    Equivalently, this tester returns :data:`True` only if *all* of the
    following conditions apply:

    * These two hints are **semantically related** (i.e., convey broadly similar
      semantics enabling these two hints to be reasonably compared). For
      example:

      * ``callable.abc.Iterable[str]`` and ``callable.abc.Sequence[int]`` are
        semantically related. These two hints both convey container semantics.
        Despite their differing child hints, these two hints are broadly similar
        enough to be reasonably comparable.
      * ``callable.abc.Iterable[str]`` and ``callable.abc.Callable[[], int]``
        are *not* semantically related. Whereas the first hints conveys a
        container semantic, the second hint conveys a callable semantic. Since
        these two semantics are unrelated, these two hints are dissimilar
        enough to *not* be reasonably comparable.

    * The first hint is **semantically equivalent** to or **narrower** than the
      second hint. Equivalently:

      * The first hint matches less than or equal to the total number of all
        possible objects matched by the second hint.
      * The size of the countably infinite set of all possible objects matched
        by the first hint is less than or equal to that of those matched by the
        second hint.

    * The first hint is **compatible** with the second hint. Since the first
      hint is semantically narrower than the second, APIs annotated by the first
      hint may safely replace that hint with the second hint; doing so preserves
      backward compatibility.

    Parameters
    ----------
    subhint : object
        Type hint or type to be tested as the subhint.
    superhint : object
        Type hint or type to be tested as the superhint.

    Returns
    -------
    bool
        :data:`True` only if this first hint is a subhint of this second hint.

    Examples
    --------
        >>> from beartype.door import is_subhint
        >>> is_subhint(int, int)
        True
        >>> is_subhint(Callable[[], list], Callable[..., Sequence[Any]])
        True
        >>> is_subhint(Callable[[], list], Callable[..., Sequence[int]])
        False
    '''

    # Avoid circular import dependencies.
    from beartype.door._cls.doorsuper import TypeHint

    # The one-liner is mightier than the... many-liner.
    return TypeHint(subhint).is_subhint(TypeHint(superhint))

# ....................{ TESTERS ~ is_bearable              }....................
def is_bearable(
    # Mandatory flexible parameters.
    obj: object,
    hint: object,

    # Optional keyword-only parameters.
    *,
    conf: BeartypeConf = BEARTYPE_CONF_DEFAULT,
) -> bool:
    '''
    :data:`True` only if the passed arbitrary object satisfies the passed
    type hint under the passed beartype configuration.

    Parameters
    ----------
    obj : object
        Arbitrary object to be tested against this hint.
    hint : object
        Type hint to test this object against.
    conf : BeartypeConf, optional
        **Beartype configuration** (i.e., self-caching dataclass encapsulating
        all settings configuring type-checking for the passed object). Defaults
        to ``BeartypeConf()``, the default constant-time configuration.

    Returns
    -------
    bool
        :data:`True` only if this object satisfies this hint.

    Raises
    ------
    beartype.roar.BeartypeConfException
        If this configuration is *not* a :class:`BeartypeConf` instance.
    beartype.roar.BeartypeDecorHintForwardRefException
        If this hint contains one or more relative forward references, which
        this tester explicitly prohibits to improve both the efficiency and
        portability of calls to this tester.
    beartype.roar.BeartypeDecorHintNonpepException
        If this hint is *not* PEP-compliant (i.e., complies with *no* Python
        Enhancement Proposals (PEPs) currently supported by :mod:`beartype`).
    beartype.roar.BeartypeDecorHintPepUnsupportedException
        If this hint is currently unsupported by :mod:`beartype`.

    Examples
    --------
        >>> from beartype.door import is_bearable
        >>> is_bearable(['Things', 'fall', 'apart;'], list[str])
        True
        >>> is_bearable(['the', 'centre', 'cannot', 'hold;'], list[int])
        False
    '''

    # Memoized low-level type-checking tester function returning true only if
    # the object passed to that tester satisfies the type hint passed to this
    # high-level type-checking tester function.
    #
    # Note that parameters are intentionally passed positionally for efficiency.
    # Since make_func_tester() is memoized, passing parameters by keyword would
    # raise a non-fatal
    # "_BeartypeUtilCallableCachedKwargsWarning" warning.
    func_tester = make_func_tester(hint, conf)

    # Return true only if the passed object satisfies this hint.
    return func_tester(obj)  # pyright: ignore[reportUnboundVariable]
