#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **abstract syntax tree (AST) test utility unit tests.**

This submodule unit tests the public API of the private
:mod:`beartype._util.ast.utilasttest` submodule.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS                              }....................
def test_is_node_callable_typed() -> None:
    '''
    Test the :func:`beartype._util.ast.utilasttest.is_node_callable_typed`
    factory.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype._util.ast.utilastget import get_code_child_node
    from beartype._util.ast.utilasttest import is_node_callable_typed

    # ....................{ LOCALS                         }....................
    # Tuple of 2-tuples "(is_node_callable_typed_bool, func_code)" describing
    # example callables to be tested below, where:
    # * "is_node_callable_typed_bool" is the boolean value expected to be
    #   returned by the is_node_callable_typed() tester when passed the
    #   "ast.Callable" AST tree parsed from the "func_code" item.
    # * "func_code" is a triple-quoted string defining an arbitrary callable to
    #   be parsed into the "ast.Callable" AST tree to be passed to the
    #   is_node_callable_typed() tester.
    CALLABLE_DATAS = (
        # Untyped function accepting arbitrary parameters.
        (False, '''def _(a, b, /, c, d, *args, e, f, **kwargs): ...''',),
        # Typed function with an annotated return and unannotated parameters.
        (True, '''def _(a, b, /, c, d, *args, e, f, **kwargs) -> None: ...''',),
        # Typed function with an annotated non-variadic flexible parameter,
        # other unannotated parameters, and an unannotated return.
        (True, '''def _(a, b: int, /, c, d, *args, e, f, **kwargs): ...''',),
        # Typed function with an annotated non-variadic keyword-only parameter
        # defined implicitly, other unannotated parameters, and an unannotated
        # return.
        (True, '''def _(a, b, /, c, d, *args, e, f: bool, **kwargs): ...''',),
        # Typed function with an annotated non-variadic keyword-only parameter
        # defined explicitly, other unannotated parameters, and an unannotated
        # return.
        (True, '''def _(a, b, /, c, d, *, e, f: bool, **kwargs): ...''',),
        # Typed function with an annotated non-variadic positional-only
        # parameter defined explicitly, other unannotated parameters, and an
        # unannotated return.
        (True, '''def _(a, b, /, c, d: float, *, d, e, **kwargs): ...''',),
        # Typed function with an annotated positional variadic argument
        # parameter, other unannotated parameters, and an unannotated return.
        (True, '''def _(a, b, /, c, d, *args: str, e, f, **kwargs): ...''',),
        # Typed function with an annotated keyword variadic argument
        # parameter, other unannotated parameters, and an unannotated return.
        (True, '''def _(a, b, /, c, d, *args, e, f, **kwargs: bytes): ...''',),
    )

    # ....................{ ASSERTS                        }....................
    # For each example callable to be tested...
    for is_node_callable_typed_bool, func_code in CALLABLE_DATAS:
        # "ast.Callable" AST tree parsed from the string defining this callable.
        func_node = get_code_child_node(func_code)

        # Assert that this tester reports the expected boolean when passed this
        # "ast.Callable" AST tree.
        assert is_node_callable_typed(func_node) is is_node_callable_typed_bool
