#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2024 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype **configuration class testers** (i.e., low-level callables testing and
validating various metadata of interest to the high-level
:class:`beartype.BeartypeConf` dataclass).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
import beartype
from beartype.roar import (
    BeartypeConfException,
    BeartypeConfParamException,
    BeartypeCallHintParamViolation,
    BeartypeCallHintReturnViolation,
    BeartypeDoorHintViolation,
)
from beartype.typing import Optional
from beartype._cave._cavemap import NoneTypeOr
from beartype._conf.confenum import (
    BeartypeStrategy,
    BeartypeViolationVerbosity,
)
from beartype._conf.confoverrides import (
    BEARTYPE_HINT_OVERRIDES_PEP484_TOWER,
    BeartypeHintOverrides,
)
from beartype._data.hint.datahinttyping import DictStrToAny
from beartype._util.cls.utilclstest import is_type_subclass

# ....................{ RAISERS                            }....................
def die_unless_conf(conf: 'beartype.BeartypeConf') -> None:
    '''
    Raise an exception unless the passed object is a beartype configuration.

    Parameters
    ----------
    conf : beartype.BeartypeConf
        Object to be validated.

    Raises
    ------
    BeartypeConfException
        If this object is *not* a beartype configuration.
    '''

    # Avoid circular import dependencies.
    from beartype._conf.confcls import BeartypeConf

    # If this object is *NOT* a configuration, raise an exception.
    if not isinstance(conf, BeartypeConf):
        raise BeartypeConfException(
            f'{repr(conf)} not beartype configuration.')
    # Else, this object is a configuration.


def die_if_conf_kwargs_invalid(conf_kwargs: DictStrToAny) -> None:
    '''
    Raise an exception if one or more configuration parameters in the passed
    dictionary of such parameters are invalid.

    Parameters
    ----------
    conf_kwargs : Dict[str, object]
        Dictionary mapping from the names to values of *all* possible keyword
        parameters configuring this configuration.

    Raises
    ------
    BeartypeConfParamException
        If one or more configurations parameter in this dictionary are invalid.
    '''

    # ..................{ VALIDATE                           }..................
    # If "claw_is_pep526" is *NOT* a boolean, raise an exception.
    if not isinstance(conf_kwargs['claw_is_pep526'], bool):
        raise BeartypeConfParamException(
            f'Beartype configuration parameter "claw_is_pep526" '
            f'value {repr(conf_kwargs["claw_is_pep526"])} not boolean.'
        )
    # Else, "claw_is_pep526" is a boolean.
    #
    # If "hint_overrides" is *NOT* a frozen dict, raise an exception.
    elif not isinstance(conf_kwargs['hint_overrides'], BeartypeHintOverrides):
        raise BeartypeConfParamException(
            f'Beartype configuration parameter "hint_overrides" '
            f'value {repr(conf_kwargs["hint_overrides"])} not '
            f'frozen dictionary '
            f'(i.e., "beartype.BeartypeHintOverrides" instance).'
        )
    # Else, "hint_overrides" is a frozen dict.
    #
    # If "is_color" is *NOT* a tri-state boolean, raise an exception.
    elif not isinstance(conf_kwargs['is_color'], NoneTypeOr[bool]):
        raise BeartypeConfParamException(
            f'Beartype configuration parameter "is_color" '
            f'value {repr(conf_kwargs["is_color"])} not tri-state boolean '
            f'(i.e., "True", "False", or "None").'
        )
    # Else, "is_color" is a tri-state boolean.
    #
    # If "is_debug" is *NOT* a boolean, raise an exception.
    elif not isinstance(conf_kwargs['is_debug'], bool):
        raise BeartypeConfParamException(
            f'Beartype configuration parameter "is_debug" '
            f'value {repr(conf_kwargs["is_debug"])} not boolean.'
        )
    # Else, "is_debug" is a boolean.
    #
    # If "is_pep484_tower" is *NOT* a boolean, raise an exception.
    elif not isinstance(conf_kwargs['is_pep484_tower'], bool):
        raise BeartypeConfParamException(
            f'Beartype configuration parameter "is_pep484_tower" '
            f'value {repr(conf_kwargs["is_debug"])} not boolean.'
        )
    # Else, "is_pep484_tower" is a boolean.
    #
    # If "strategy" is *NOT* an enumeration member, raise an exception.
    elif not isinstance(conf_kwargs['strategy'], BeartypeStrategy):
        raise BeartypeConfParamException(
            f'Beartype configuration parameter "strategy" '
            f'value {repr(conf_kwargs["strategy"])} not '
            f'"beartype.BeartypeStrategy" enumeration member.'
        )
    # Else, "strategy" is an enumeration member.
    #
    # If "violation_verbosity" is *NOT* an enumeration member, raise an
    # exception.
    elif not isinstance(
        conf_kwargs['violation_verbosity'], BeartypeViolationVerbosity):
        raise BeartypeConfParamException(
            f'Beartype configuration parameter "violation_verbosity" '
            f'value {repr(conf_kwargs["violation_verbosity"])} not '
            f'"beartype.BeartypeViolationVerbosity" enumeration member.'
        )
    # Else, "violation_verbosity" is an enumeration member.
    #
    # If "warning_cls_on_decorator_exception" is neither "None" *NOR* a
    # warning category, raise an exception.
    elif not (
        conf_kwargs['warning_cls_on_decorator_exception'] is None or
        is_type_subclass(
            conf_kwargs['warning_cls_on_decorator_exception'], Warning)
    ):
        raise BeartypeConfParamException(
            f'Beartype configuration parameter '
            f'"warning_cls_on_decorator_exception" value '
            f'{repr(conf_kwargs["warning_cls_on_decorator_exception"])} '
            f'neither "None" nor warning category '
            f'(i.e., "Warning" subclass).'
        )
    # Else, "warning_cls_on_decorator_exception" is either "None" *OR* a
    # warning category.

    # For the name of each keyword parameter whose value is expected to be an
    # exception subclass...
    for arg_name_exception_subclass in _ARG_NAMES_EXCEPTION_SUBCLASS:
        # If the value of this keyword parameter is *NOT* an exception subclass,
        # raise an exception.
        if not is_type_subclass(
            conf_kwargs[arg_name_exception_subclass], Exception):
            raise BeartypeConfParamException(
                f'Beartype configuration parameter '
                f'"{arg_name_exception_subclass}" value '
                f'{repr(conf_kwargs[arg_name_exception_subclass])} not '
                f'exception type.'
            )

# ....................{ DEFAULTERS                         }....................
def default_conf_kwargs_before(conf_kwargs: DictStrToAny) -> None:
    '''
    Sanitize the passed dictionary of configuration parameters by defaulting all
    parameters not explicitly passed by the user to sane internal defaults
    *before* the :func:`.die_if_conf_kwargs_invalid` raiser validates these
    parameters.

    Parameters
    ----------
    conf_kwargs : Dict[str, object]
        Dictionary mapping from the names to values of *all* possible keyword
        parameters configuring this configuration.
    '''

    # ..................{ DEFAULT ~ violation_*type          }..................
    # Default violation type if passed *OR* "None" if unpassed.
    violation_type = conf_kwargs['violation_type']

    # If...
    if (
        # The caller explicitly passed a default violation type...
        violation_type is not None and
        # That is *NOT* an exception subclass...
        not is_type_subclass(violation_type, Exception)
    # Raise an exception.
    ):
        raise BeartypeConfParamException(
            f'Beartype configuration parameter "violation_type" value '
            f'{repr(violation_type)} not exception type.'
        )
    # Else, the caller either passed *NO* default violation type or passed a
    # valid default violation type.

    # If the caller did *NOT* explicitly pass a DOOR violation type, default
    # this type to either the default violation type if passed *OR* the default
    # DOOR violation type if unpassed.
    if conf_kwargs['violation_door_type'] is None:
        conf_kwargs['violation_door_type'] = (
            violation_type or BeartypeDoorHintViolation)
    # Else, the caller explicitly passed a DOOR violation type.

    # If the caller did *NOT* explicitly pass a parameter violation type,
    # default this type to either the default violation type if passed *OR* the
    # default DOOR violation type if unpassed.
    if conf_kwargs['violation_param_type'] is None:
        conf_kwargs['violation_param_type'] = (
            violation_type or BeartypeCallHintParamViolation)

    # If the caller did *NOT* explicitly pass a return violation type, default
    # this type to either the default violation type if passed *OR* the default
    # DOOR violation type if unpassed.
    if conf_kwargs['violation_return_type'] is None:
        conf_kwargs['violation_return_type'] = (
            violation_type or BeartypeCallHintReturnViolation)
    # Else, the caller explicitly passed a DOOR violation type.


def default_conf_kwargs_after(conf_kwargs: DictStrToAny) -> None:
    '''
    Sanitize the passed dictionary of configuration parameters by defaulting all
    parameters not explicitly passed by the user to sane internal defaults
    *after* the :func:`.die_if_conf_kwargs_invalid` raiser validates these
    parameters.

    Parameters
    ----------
    conf_kwargs : Dict[str, object]
        Dictionary mapping from the names to values of *all* possible keyword
        parameters configuring this configuration.
    '''

    # ..................{ DEFAULT ~ hint_overrides           }..................
    # If enabling the PEP 484-compliant implicit numeric tower...
    if conf_kwargs['is_pep484_tower']:
        # Hint overrides if passed by the caller *OR* "None" otherwise.
        hint_overrides = conf_kwargs['hint_overrides']

        # Target hint overrides for the source "float" and "complex" types if
        # any *OR* "None" otherwise.
        hint_overrides_float = hint_overrides.get(float)
        hint_overrides_complex = hint_overrides.get(complex)

        # Whichever of the "float" or "complex" types are already existing
        # overrides in the passed type hint overrides.
        hint_override_cls_conflict: Optional[type] = None

        # If these overrides already define conflicting overrides for either the
        # "float" or "complex" types, record that fact.
        if (
            hint_overrides_float and
            hint_overrides_float != BEARTYPE_HINT_OVERRIDES_PEP484_TOWER[float]
        ):
            hint_override_cls_conflict = float
        elif (
            hint_overrides_complex and
            hint_overrides_complex != BEARTYPE_HINT_OVERRIDES_PEP484_TOWER[
                complex]
        ):
            hint_override_cls_conflict = complex
        # Else, these overrides do *NOT* already define conflicting overrides
        # for either the "float" or "complex" types.

        # If these overrides already define conflicting overrides for either the
        # "float" or "complex" types, raise an exception.
        if hint_override_cls_conflict:
            raise BeartypeConfParamException(
                f'Beartype configuration '
                f'parameter "is_pep484_tower" conflicts with '
                f'parameter "hint_overrides" key '
                f'"{hint_override_cls_conflict.__name__}" '
                f'value '
                f'{repr(hint_overrides[hint_override_cls_conflict])}.'
            )
        # Else, these overrides do *NOT* already define conflicting overrides
        # for either the "float" or "complex" types.

        # Add hint overrides expanding the passed type hint overrides with
        # additional overrides mapping:
        # * The "float" type to the "float | int" type hint.
        # * The "complex" type to the "complex | float | int" type hint.
        conf_kwargs['hint_overrides'] = (
            hint_overrides | BEARTYPE_HINT_OVERRIDES_PEP484_TOWER)  # type: ignore[assignment]
    # Else, the PEP 484-compliant implicit numeric tower is disabled.

# ....................{ PRIVATE ~ globals                  }....................
_ARG_NAMES_EXCEPTION_SUBCLASS = (
    'violation_door_type',
    'violation_param_type',
    'violation_return_type',
)
'''
Tuple of the names of all keyword parameters to the
:meth:`beartype.BeartypeConf.__new__` dunder method whose values are expected to
be exception subclasses.
'''
