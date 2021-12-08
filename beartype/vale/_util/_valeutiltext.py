#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2021 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype validator text utilities** (i.e., callables performing low-level
string-centric operations on behalf of higher-level beartype validators).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                           }....................
# See the "beartype.cave" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ FORMATTERS                        }....................
def format_diagnosis_line(
    validator_repr: str,
    is_obj_valid: bool,
    indent_level: str,
) -> str:
    '''
    Single line of a larger human-readable **validation failure diagnosis**
    (i.e., substring describing how an arbitrary object either satisfies *or*
    fails to satisfy an arbitrary validator), formatted with the passed
    indentation level and boolean value.

    Parameters
    ----------
    validator_repr : str
        **Diagnosis line** (i.e., unformatted single line of a larger diagnosis
        report to be formatted by this function).
    is_obj_valid : bool
        ``True`` only if that arbitrary object satisfies the beartype validator
        described by this specific line.
    indent_level : str
        **Indentation level** (i.e., zero or more adjacent spaces prefixing
        each line of the returned substring for readability).

    Returns
    ----------
    str
        This diagnosis line formatted with this indentation level.
    '''
    assert isinstance(validator_repr, str), (
        f'{repr(validator_repr)} not string.')
    assert isinstance(is_obj_valid, bool), f'{repr(is_obj_valid)} not boolean.'
    assert isinstance(indent_level, str), f'{repr(indent_level)} not string.'

    # String representing this boolean value, padded with spaces on the left as
    # needed to produce a column-aligned line diagnosis resembling:
    #      True == Is[lambda foo: foo.x + foo.y >= 0] &
    #     False == Is[lambda foo: foo.x + foo.y <= 10]
    is_obj_valid_str = (
        ' True == ' if is_obj_valid else
        'False == '
    )

    # Do one thing and do it well.
    return f'{indent_level}{is_obj_valid_str}{validator_repr}'
