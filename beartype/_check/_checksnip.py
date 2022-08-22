#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2022 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **type-checking function code snippets** (i.e., triple-quoted
pure-Python string constants formatted and concatenated together to dynamically
generate the implementations of functions type-checking arbitrary objects
against arbitrary PEP-compliant type hints).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype._check.checkmagic import (
    VAR_NAME_PITH_ROOT,
)
from beartype._util.text.utiltextmagic import CODE_INDENT_1

# ....................{ CODE                               }....................
FUNC_TESTER_CODE_SIGNATURE = f'''{{code_signature_prefix}}def {{func_name}}(
    {VAR_NAME_PITH_ROOT}: object,
{{code_signature_args}}{CODE_INDENT_1}
) -> bool:'''
'''
Code snippet declaring the signature of all type-checking tester functions
created by the :func:`beartype._check.checkmagic.make_func_tester` factory.

Note that:

* ``code_signature_prefix`` is usually either:

  * For synchronous callables, the empty string.
  * For asynchronous callables (e.g., asynchronous generators, coroutines),
    the space-suffixed keyword ``"async "``.
'''
