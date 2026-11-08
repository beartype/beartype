#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype :pep:`646` **type-checking expression snippets** (i.e., triple-quoted
pure-Python string constants formatted and concatenated together to dynamically
generate boolean expressions type-checking arbitrary objects against
:pep:`646`-compliant type hints).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype._data.check.code.datacodename import VAR_NAME_RANDOM_INT
from beartype._data.typing.datatyping import CallableStrFormat

# ....................{ CODE ~ tuple : fixed-variadic      }....................
CODE_PEP646_TUPLE_FIXED_VARIADIC_LEN_MIN = '''
{{indent_curr}}    # True only if this tuple is of at least the minimum length.
{{indent_curr}}    len({pith_curr_var_name}) >= {hints_fixed_len} and'''
'''
:pep:`646`-compliant code snippet type-checking the current pith to contain at
least as many items as the fixed (i.e., prefix and suffix) child hints of a
:pep:`646`-compliant fixed-variadic tuple hint.
'''


CODE_PEP646_TUPLE_FIXED_VARIADIC_CHILD_VARIADIC = '''
{{indent_curr}}    # True only if either this tuple contains no variadic items *OR*
{{indent_curr}}    # this variadic item of this tuple deeply satisfies this hint.
{{indent_curr}}    (len({pith_curr_var_name}) == {hints_fixed_len} or
{{indent_curr}}     {hint_child_placeholder}) and'''
'''
:pep:`646`-compliant code snippet type-checking one variadic item of the
current pith against the variadic child hint of a :pep:`646`-compliant
fixed-variadic tuple hint (e.g., ``str`` for ``tuple[int, *tuple[str, ...]]``).
'''


CODE_PEP646_TUPLE_FIXED_VARIADIC_RANDOM_PITH_CHILD_EXPR = (
    f'''{{pith_curr_var_name}}[{{hints_prefix_len}} + {VAR_NAME_RANDOM_INT} % '''
    f'''(len({{pith_curr_var_name}}) - {{hints_fixed_len}})]''')
'''
:pep:`646`-compliant Python expression yielding a pseudo-random variadic item of
the current tuple pith, intended to be applied when the
:attr:`beartype.BeartypeConf.is_random` boolean is enabled.
'''

# ....................{ FORMATTERS                         }....................
# str.format() methods, globalized to avoid inefficient dot lookups elsewhere.
CODE_PEP646_TUPLE_FIXED_VARIADIC_LEN_MIN_format: CallableStrFormat = (
    CODE_PEP646_TUPLE_FIXED_VARIADIC_LEN_MIN.format)
CODE_PEP646_TUPLE_FIXED_VARIADIC_CHILD_VARIADIC_format: CallableStrFormat = (
    CODE_PEP646_TUPLE_FIXED_VARIADIC_CHILD_VARIADIC.format)
CODE_PEP646_TUPLE_FIXED_VARIADIC_RANDOM_PITH_CHILD_EXPR_format: CallableStrFormat = (
    CODE_PEP646_TUPLE_FIXED_VARIADIC_RANDOM_PITH_CHILD_EXPR.format)
