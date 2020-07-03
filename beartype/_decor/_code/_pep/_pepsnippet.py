#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2020 Cecil Curry.
# See "LICENSE" for further details.

'''
**Beartype decorator** `PEP 484`_ **code constants.**

This private submodule is the `PEP 484`_-specific analogue to the `PEP
484_`-agnostic :mod:`beartype._decor.snippet` submodule.

This private submodule is *not* intended for importation by downstream callers.

.. _PEP 484:
   https://www.python.org/dev/peps/pep-0484
'''

# ....................{ CODE ~ param                      }....................
# P484_CODE_PARAM_VARIADIC_POSITIONAL = '''
#     for __beartype_arg in args[{arg_index!r}:]:
#         if not isinstance(__beartype_arg, {arg_type_expr}):
#             raise __beartype_param_exception(
#                 '{func_name} positional variadic parameter '
#                 '{arg_index} {{}} not a {{!r}}.'.format(
#                     __beartype_trim(__beartype_arg), {arg_type_expr}))
# '''
