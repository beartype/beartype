#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2022 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype type-checking testers** (i.e., functions type-checking arbitrary
objects against PEP-compliant type hints, callable at *any* arbitrary time
during the lifecycle of the active Python process).
'''

# ....................{ TODO                              }....................
#FIXME: Optimize us up, please. See this discussion for voluminous details:
#    https://github.com/beartype/beartype/issues/87#issuecomment-1020856517

# ....................{ IMPORTS                           }....................
from beartype import BeartypeConf, beartype
from beartype.roar import (
    BeartypeAbbyHintViolation,
    BeartypeCallHintReturnViolation,
)
from beartype.typing import Callable
from beartype._util.hint.utilhinttest import die_unless_hint

# ....................{ PRIVATE ~ constants               }....................
_TYPE_CHECKER_EXCEPTION_MESSAGE_PREFIX = (
    '@beartyped _get_type_checker._die_if_unbearable() return ')
'''
Irrelevant substring prefixing *all* exception messages raised by *all*
**runtime type-checkers** (i.e., functions created and returned by the
:func: `_get_type_checker` getter).
'''


_TYPE_CHECKER_EXCEPTION_MESSAGE_PREFIX_LEN = (
    len(_TYPE_CHECKER_EXCEPTION_MESSAGE_PREFIX))
'''
Length of the irrelevant substring prefixing *all*
exception messages raised by *all* **runtime type-checkers** (i.e., functions
created and returned by the :func: `_get_type_checker` getter).
'''

# ....................{ PRIVATE ~ hints                   }....................
_BeartypeTypeChecker = Callable[[object], None]
'''
PEP-compliant type hint matching a **runtime type-checker** (i.e., function
created and returned by the :func:`_get_type_checker` getter, raising a
:exc:`BeartypeCallHintReturnViolation` exception when the object passed to that
function violates a PEP-compliant type hint).
'''

# ....................{ VALIDATORS                        }....................
def die_if_unbearable(
    # Mandatory flexible parameters.
    obj: object,
    hint: object,

    # Optional keyword-only parameters.
    *, conf: BeartypeConf = BeartypeConf(),
) -> None:
    '''
    Raise an exception if the passed arbitrary object violates the passed
    PEP-compliant type hint.

    Parameters
    ----------
    obj : object
        Arbitrary object to be tested against this hint.
    hint : object
        PEP-compliant type hint to test this object against.
    conf : BeartypeConf, optional
        **Beartype configuration** (i.e., self-caching dataclass encapsulating
        all flags, options, settings, and other metadata configuring how this
        object is type-checked). Defaults to ``BeartypeConf()``, the default
        beartype configuration.

    Raises
    ----------
    :exc:`BeartypeAbbyHintViolation`
        If this object violates this hint.
    :exc:`BeartypeDecorHintPepUnsupportedException`
        If this hint is a PEP-compliant type hint currently unsupported by
        the :func:`beartype.beartype` decorator.
    :exc:`BeartypeDecorHintNonpepException`
        If this hint is neither a:

        * Supported PEP-compliant type hint.
        * Supported PEP-noncompliant type hint.

    Examples
    ----------
        >>> from beartype.abby import die_if_unbearable
        >>> die_if_unbearable(['And', 'what', 'rough', 'beast,'], list[str])
        >>> die_if_unbearable(['its', 'hour', 'come', 'round'], list[int])
        beartype.roar.BeartypeAbbyHintViolation: Object ['its', 'hour', 'come',
        'round'] violates type hint list[int], as list index 0 item 'its' not
        instance of int.
    '''

    # @beartype-decorated closure raising an
    # "BeartypeCallHintReturnViolation" exception if the parameter passed to
    # this closure violates the hint passed to this parent tester.
    _die_if_unbearable = _get_type_checker(hint, conf)

    # Attempt to type-check this object by passing this object to this closure,
    # which then implicitly type-checks this object as a return value.
    try:
        _die_if_unbearable(obj)
    # If this closure raises an exception as this object violates this hint...
    except BeartypeCallHintReturnViolation as exception:
        # Exception message.
        exception_message = str(exception)

        # Replace the irrelevant substring prefixing this message with a
        # relevant substring applicable to this higher-level function.
        exception_message = (
            f'Object '
            f'{exception_message[_TYPE_CHECKER_EXCEPTION_MESSAGE_PREFIX_LEN:]}'
        )

        # Wrap this exception in a more readable higher-level exception.
        raise BeartypeAbbyHintViolation(exception_message) from exception
    # Else, this closure raised another exception. In this case, percolate this
    # exception back up this call stack.

# ....................{ TESTERS                           }....................
def is_bearable(
    # Mandatory flexible parameters.
    obj: object,
    hint: object,

    # Optional keyword-only parameters.
    *, conf: BeartypeConf = BeartypeConf(),
) -> bool:
    '''
    ``True`` only if the passed arbitrary object satisfies the passed
    PEP-compliant type hint.

    Parameters
    ----------
    obj : object
        Arbitrary object to be tested against this hint.
    hint : object
        PEP-compliant type hint to test this object against.
    conf : BeartypeConf, optional
        **Beartype configuration** (i.e., self-caching dataclass encapsulating
        all flags, options, settings, and other metadata configuring how this
        object is type-checked). Defaults to ``BeartypeConf()``, the default
        beartype configuration.

    Returns
    ----------
    bool
        ``True`` only if this object satisfies this hint.

    Raises
    ----------
    :exc:`BeartypeDecorHintPepUnsupportedException`
        If this hint is a PEP-compliant type hint currently unsupported by
        the :func:`beartype.beartype` decorator.
    :exc:`BeartypeDecorHintNonpepException`
        If this hint is neither a:

        * Supported PEP-compliant type hint.
        * Supported PEP-noncompliant type hint.

    Examples
    ----------
        >>> from beartype.abby import is_bearable
        >>> is_bearable(['Things', 'fall', 'apart;'], list[str])
        True
        >>> is_bearable(['the', 'centre', 'cannot', 'hold;'], list[int])
        False
    '''

    # @beartype-decorated closure raising an
    # "BeartypeCallHintReturnViolation" exception if the parameter passed to
    # this closure violates the hint passed to this parent tester.
    _die_if_unbearable = _get_type_checker(hint, conf)

    # Attempt to...
    try:
        # Type-check this object by passing this object to this closure, which
        # then implicitly type-checks this object as a return value.
        _die_if_unbearable(obj)

        # If this closure fails to raise an exception, this object *MUST*
        # necessarily satisfy this hint. In this case, return true.
        return True
    # If this closure raises an exception as this object violates this hint,
    # silently squelch this exception and return false below.
    except BeartypeCallHintReturnViolation:
        pass
    # Else, this closure raised another exception. In this case, percolate this
    # exception back up this call stack.

    # Return false, since this object violates this hint. (See above.)
    return False

# ....................{ PRIVATE ~ getters                 }....................
def _get_type_checker(
    hint: object, conf: BeartypeConf) -> _BeartypeTypeChecker:
    '''
    Create, cache, and return a **runtime type-checker** (i.e., function
    raising a :exc:`BeartypeCallHintReturnViolation` exception when the object
    passed to that function violates the hint passed to this parent getter
    under the passed beartype configuration).

    Note that this runtime type checker intentionally raises
    :exc:`BeartypeCallHintReturnViolation` rather than
    :exc:`BeartypeCallHintParamViolation` exceptions. Type-checking return
    values is marginally faster than type-checking parameters. Ergo, we
    intentionally annotate this return rather than parameter of this checker.

    Parameters
    ----------
    hint : object
        PEP-compliant type hint to validate all objects passed to this runtime
        type-checker against.
    conf : BeartypeConf, optional
        **Beartype configuration** (i.e., self-caching dataclass encapsulating
        all flags, options, settings, and other metadata configuring how this
        object is type-checked). Defaults to ``BeartypeConf()``, the default
        beartype configuration.

    Returns
    ----------
    _BeartypeTypeChecker
        Runtime type-checker specific to this hint and configuration.

    Raises
    ----------
    :exc:`BeartypeDecorHintPepUnsupportedException`
        If this hint is a PEP-compliant type hint currently unsupported by
        the :func:`beartype.beartype` decorator.
    :exc:`BeartypeDecorHintNonpepException`
        If this hint is neither a:

        * Supported PEP-compliant type hint.
        * Supported PEP-noncompliant type hint.
    '''

    # If this hint is unsupported, raise an exception.
    #
    # Note that this technically duplicates a similar check performed by the
    # @beartype decorator below except that the exception prefix passed here
    # results in substantially more readable and relevant exceptions.
    die_unless_hint(hint=hint, exception_prefix='Functional ')
    # Else, this hint is supported.

    # @beartype-decorated closure raising an
    # "BeartypeCallHintReturnViolation" exception if the parameter passed to
    # this closure violates the hint passed to this parent tester.
    @beartype(conf=conf)
    def _die_if_unbearable(pith) -> hint:  # type: ignore[valid-type]
        return pith

    # Return this closure.
    return _die_if_unbearable
