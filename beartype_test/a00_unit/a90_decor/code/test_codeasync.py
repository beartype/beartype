#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2021 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype decorator asynchronous unit tests.**

This submodule unit tests edge cases of the :func:`beartype.beartype` decorator
decorating asynchronous callables (e.g., coroutines, asynchronous generators).
'''

# ....................{ IMPORTS                           }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS                             }....................
# def test_decor_async_coroutine() -> None:
#     '''
#     Test decorating asynchronous coroutines with the :func:`beartype.beartype`
#     decorator.
#     '''
#
#     # Defer heavyweight imports.
#     from beartype import beartype
#
#     # Undecorated unannotated function.
#     def universal_love(gork, mork):
#         return gork + mork
#
#     # Decorated unannotated function.
#     khorne_typed = beartype(khorne)
#
#     # Assert that @beartype efficiently reduces to a noop (i.e., the identity
#     # decorator) when decorating this function.
#     assert khorne_typed is khorne
#
#     # Call this function and assert the expected return value.
#     assert khorne_typed('WAAAGH!', '!HGAAAW') == 'WAAAGH!!HGAAAW'
