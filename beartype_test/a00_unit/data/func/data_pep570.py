#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`570` **data submodule.**

This submodule exercises :pep:`570` support implemented in the
:func:`beartype.beartype` decorator by declaring callables accepting one or
more **positional-only parameters** (i.e., parameters that *must* be passed
positionally, syntactically followed in the signatures of their callables by
the :pep:`570`-compliant ``/,`` pseudo-parameter).

Caveats
----------
**This submodule requires the active Python interpreter to target Python >=
3.8.** If this is *not* the case, importing this submodule raises an
:class:`SyntaxError` exception. In particular, this submodule *must* not be
imported from module scope. If this submodule is imported from module scope
*and* the active Python interpreter targets Python < 3.8, :mod:`pytest` raises
non-human-readable exceptions at test collection time resembling:

    /usr/lib64/python3.6/site-packages/_pytest/python.py:578: in _importtestmodule
        mod = import_path(self.fspath, mode=importmode)
    /usr/lib64/python3.6/site-packages/_pytest/pathlib.py:531: in import_path
        importlib.import_module(module_name)
    /usr/lib64/python3.6/importlib/__init__.py:126: in import_module
        return _bootstrap._gcd_import(name[level:], package, level)
    <frozen importlib._bootstrap>:994: in _gcd_import
        ???
    <frozen importlib._bootstrap>:971: in _find_and_load
        ???
    <frozen importlib._bootstrap>:955: in _find_and_load_unlocked
        ???
    <frozen importlib._bootstrap>:665: in _load_unlocked
        ???
    /usr/lib64/python3.6/site-packages/_pytest/assertion/rewrite.py:161: in exec_module
        source_stat, co = _rewrite_test(fn, self.config)
    /usr/lib64/python3.6/site-packages/_pytest/assertion/rewrite.py:354: in _rewrite_test
        tree = ast.parse(source, filename=fn_)
    /usr/lib64/python3.6/ast.py:35: in parse
        return compile(source, filename, mode, PyCF_ONLY_AST)
    E     File "/home/leycec/py/beartype/beartype_test/a00_unit/a20_util/func/test_utilfuncarg.py", line 237
    E       /,
    E       ^
    E   SyntaxError: invalid syntax
'''

# ....................{ IMPORTS                            }....................
from typing import Union

# ....................{ CALLABLES                          }....................
def func_args_2_posonly_mixed(
    before_spreading_his_black_wings: Union[bytearray, str],
    reaching_for_the_skies: Union[bool, str] = 'in this forest',
    /,
) -> Union[list, str]:
    '''
    Arbitrary :pep:`570`-compliant callable passed a mandatory and optional
    positional-only parameter, all annotated with PEP-compliant type hints.
    '''

    return (
        before_spreading_his_black_wings + '\n' + reaching_for_the_skies)


def func_args_10_all_except_flex_mandatory(
    in_solitude_i_wander,
    through_the_vast_enchanted_forest,
    the_surrounding_skies='are one',
    /,
    torn_apart_by='the phenomenon of lightning',
    rain_is_pouring_down='my now shivering shoulders',
    *in_the_rain_my_tears_are_forever_lost,
    the_darkened_oaks_are_my_only_shelter,
    red_leaves_are_blown_by='the wind',
    an_ebony_raven_now_catches='my eye.',
    **sitting_in_calmness,
) -> str:
    '''
    Arbitrary :pep:`570`-compliant callable accepting all possible kinds of
    parameters, including both mandatory and optional variants of these kinds
    except mandatory flexible parameters.

    Since callables cannot by definition accept both optional positional-only
    parameters *and* mandatory flexible parameters, this callable necessarily
    omits the latter in favour of the former.
    '''

    # Arbitrary local variable declared in the body of this callable.
    before_spreading_his_black_wings = 'Reaching for the skies.'
    return before_spreading_his_black_wings
