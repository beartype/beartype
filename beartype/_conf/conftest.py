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
)
from beartype._cave._cavemap import NoneTypeOr
from beartype._conf.confenum import (
    BeartypeStrategy,
    BeartypeViolationVerbosity,
)
from beartype._conf.confoverrides import BeartypeHintOverrides
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
