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
from beartype.roar import BeartypeConfParamException
from beartype._cave._cavemap import NoneTypeOr
from beartype._conf.confenum import (
    BeartypeStrategy,
    BeartypeViolationVerbosity,
)
from beartype._conf.confoverrides import BeartypeHintOverrides
from beartype._data.hint.datahinttyping import DictStrToAny
from beartype._util.cls.utilclstest import is_type_subclass

# ....................{ RAISERS                            }....................
def die_if_conf_invalid(conf_kwargs: DictStrToAny) -> None:
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
    # If "violation_param_type" is *NOT* an exception, raise an
    # exception.
    elif not is_type_subclass(conf_kwargs['violation_param_type'], Exception):
        raise BeartypeConfParamException(
            f'Beartype configuration parameter "violation_param_type" '
            f'value {repr(conf_kwargs["violation_param_type"])} not '
            f'exception type.'
        )
    # Else, "violation_param_type" is an exception.
    #
    # If "violation_return_type" is *NOT* an exception, raise an
    # exception.
    elif not is_type_subclass(conf_kwargs['violation_return_type'], Exception):
        raise BeartypeConfParamException(
            f'Beartype configuration parameter "violation_return_type" '
            f'value {repr(conf_kwargs["violation_return_type"])} not '
            f'exception type.'
        )
    # Else, "violation_return_type" is an exception.
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
