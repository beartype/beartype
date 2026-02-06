#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype **type-checking code factory** unit tests.

This submodule unit tests the public API of the private
:mod:`beartype._check.code.codemain` submodule.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS                              }....................
def test_make_check_expr() -> None:
    '''
    Test the :func:`beartype._check.code.codemain.make_check_expr` code factory.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype._check.code.codemain import make_check_expr
    from beartype._check.convert.convmain import sanify_hint_any
    from beartype._check.metadata.hint.hintsane import HintSane
    from beartype._check.metadata.call.callmetadecor import new_decor_meta
    from beartype._check.metadata.call.callmetaexternal import (
        BEARTYPE_CALL_EXTERNAL_META)
    from beartype._conf.confcommon import BEARTYPE_CONF_DEFAULT
    from beartype_test.a00_unit.data.data_type import Class
    from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_11

    # ....................{ PASS                           }....................
    # Keyword arguments to be passed to the pair of memoized make_check_expr()
    # calls below.
    kwargs_cached = dict(
        call_meta=BEARTYPE_CALL_EXTERNAL_META,
        hint_sane=HintSane(str),
        conf=BEARTYPE_CONF_DEFAULT,
    )

    # Assert this function generates identical code for identical non-contextual
    # hints (i.e., hints whose sanification is *NOT* contextually dependent on
    # the currently type-checked callable, class, or statement) and is thus
    # cached via memoization.
    assert (
        make_check_expr(**kwargs_cached) is
        make_check_expr(**kwargs_cached)
    )

    # ....................{ PASS ~ pep : 484               }....................
    # Metadata encapsulating the reduction of a PEP 484-compliant stringified
    # forward reference type hint to a beartype forward reference proxy.
    hint_sane_pep484_ref_str = sanify_hint_any(
        call_meta=BEARTYPE_CALL_EXTERNAL_META,
        hint='And_from_the_mirrord_level_where_he_stood',
    )

    # Keyword arguments to be passed to the pair of unmemoized make_check_expr()
    # calls below, validating that the make_check_expr() code factory
    # intentionally avoids memoizing forward references (due to contextuality).
    kwargs_pep484_ref_str = dict(
        call_meta=BEARTYPE_CALL_EXTERNAL_META,
        hint_sane=hint_sane_pep484_ref_str,
        conf=BEARTYPE_CONF_DEFAULT,
    )

    # Python code snippet type-checking this hint, intentionally repeated twice.
    check_expr_pep484_ref_str_1 = make_check_expr(**kwargs_pep484_ref_str)
    check_expr_pep484_ref_str_2 = make_check_expr(**kwargs_pep484_ref_str)

    # Assert that these snippets are equal but *NOT* identical (and thus
    # recreated rather than memoized by each make_check_expr() call).
    assert check_expr_pep484_ref_str_1 == check_expr_pep484_ref_str_2
    assert check_expr_pep484_ref_str_1 is not check_expr_pep484_ref_str_2

    # ....................{ PASS ~ pep : 673               }....................
    # If the active Python interpreter targets Python >= 3.11 and thus supports
    # PEP 673 (i.e., the "typing.Self" type hint singleton)...
    if IS_PYTHON_AT_LEAST_3_11:
        # Defer version-specific imports.
        from typing import Self

        # With beartype decorator call metadata encapsulating the implicit
        # decoration of an arbitrary method of an arbitrary type, itself
        # decorated explicitly via a type stack.
        with new_decor_meta(
            cls_stack=(Class,),
            conf=BEARTYPE_CONF_DEFAULT,
            func=Class.instance_method,
        ) as decor_meta_pep673:
            # Metadata encapsulating the reduction of a PEP 673-compliant self
            # type hint to the currently decorated type.
            hint_sane_pep673 = sanify_hint_any(
                call_meta=decor_meta_pep673, hint=Self)

            # Keyword arguments to be passed to the pair of unmemoized
            # make_check_expr() calls below, validating that the
            # make_check_expr() code factory intentionally avoids memoizing
            # forward references (due to contextuality).
            kwargs_pep673 = dict(
                call_meta=decor_meta_pep673,
                hint_sane=hint_sane_pep673,
                conf=BEARTYPE_CONF_DEFAULT,
            )

            # Python code snippet type-checking this hint, intentionally
            # repeated twice.
            check_expr_pep673_1 = make_check_expr(**kwargs_pep673)
            check_expr_pep673_2 = make_check_expr(**kwargs_pep673)

            # Assert that these snippets are equal but *NOT* identical (and thus
            # recreated rather than memoized by each make_check_expr() call).
            assert check_expr_pep673_1 == check_expr_pep673_2
            assert check_expr_pep673_1 is not check_expr_pep673_2
