#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2022 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype callable source code file utility unit tests.**

This submodule unit tests the public API of the private
:mod:`beartype._util.func.utilfuncfile` submodule.
'''

# ....................{ IMPORTS                           }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS ~ code                      }....................
def test_is_func_file() -> None:
    '''
    Test usage of the
    :func:`beartype._util.func.utilfuncfile.is_func_file` function.
    '''

    # Defer test-specific imports.
    from beartype._util.func.utilfuncfile import is_func_file

    # Arbitrary pure-Python callable declared on-disk.
    def but_now_thy_youngest_dearest_one_has_perished():
        return 'The nursling of thy widowhood, who grew,'

    # Arbitrary pure-Python callable declared in-memory.
    like_a_pale_flower = eval('lambda: "by some sad maiden cherished,"')

    # Assert this tester accepts pure-Python callables declared on-disk.
    assert is_func_file(but_now_thy_youngest_dearest_one_has_perished) is True

    # Assert this tester rejects pure-Python callables declared in-memory.
    assert is_func_file(like_a_pale_flower) is False

    # Assert this tester rejects C-based callables.
    assert is_func_file(iter) is False
