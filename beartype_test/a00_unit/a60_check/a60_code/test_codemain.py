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
    from beartype._check.metadata.call.callmetaabc import BeartypeCallMetaABC
    from beartype._check.metadata.call.callmetadecor import new_decor_meta
    from beartype._check.metadata.call.callmetaexternal import (
        BEARTYPE_CALL_EXTERNAL_META)
    from beartype._conf.confcommon import BEARTYPE_CONF_DEFAULT
    from beartype._data.typing.datatypingport import Hint
    from beartype_test.a00_unit.data.data_type import Class
    from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_11

    # ....................{ PASS ~ cached                  }....................
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

    # ....................{ PASS ~ uncached                }....................
    def assert_hint_check_expr_is_uncached(
        # Mandatory parameters.
        hint: Hint,

        # Optional parameters.
        call_meta: BeartypeCallMetaABC = BEARTYPE_CALL_EXTERNAL_META,
    ) -> None:
        '''
        Assert that the :func:`.make_check_expr` code factory avoids memoizing
        the passed **contextual type hint** (i.e., hint whose type-checking
        conditionally depends on caller-specific context and is thus
        unmemoizable) under the passed beartype call metadata.

        Parameters
        ----------
        hint : Hint
            Contextual type hint to be validated.
        call_meta : BeartypeCallMetaABC, default: BEARTYPE_CALL_EXTERNAL_META
            **Beartype call metadata** (i.e., dataclass aggregating *all* common
            metadata encapsulating the user-defined callable, type, or statement
            currently being type-checked by the end user). Defaults to the
            beartype external call metadata singleton, thus sanifying
            :pep:`484`-compliant stringified forward reference type hints
            against the local and global scope of the first third-party caller
            on the current call stack.
        '''

        # Metadata encapsulating the sanification of this contextual hint.
        hint_sane = sanify_hint_any(call_meta=call_meta, hint=hint)

        # Keyword arguments to be passed to the pair of unmemoized
        # make_check_expr() calls below, validating that the make_check_expr()
        # code factory intentionally avoids memoizing this contextual hint.
        make_check_expr_kwargs = dict(
            call_meta=call_meta,
            hint_sane=hint_sane,
            conf=BEARTYPE_CONF_DEFAULT,
        )

        # Code snippets type-checking this hint, intentionally repeated twice.
        check_expr_1 = make_check_expr(**make_check_expr_kwargs)
        check_expr_2 = make_check_expr(**make_check_expr_kwargs)

        # Assert that these snippets are equal but *NOT* identical (and thus
        # recreated rather than memoized by each make_check_expr() call).
        assert check_expr_1 == check_expr_2
        assert check_expr_1 is not check_expr_2, (
            f'make_check_expr() erroneously memoized code type-checking '
            f'contextual hint {repr(hint)}.'
        )

    # ....................{ PASS ~ pep : 484               }....................
    # Assert that the make_check_expr() code factory avoids memoizing PEP
    # 484-compliant stringified forward reference root hints.
    assert_hint_check_expr_is_uncached(
        hint='And_from_the_mirrord_level_where_he_stood')

    # Assert that the make_check_expr() code factory avoids memoizing PEP
    # 585-compliant subclass root hints subscripted by one or more PEP
    # 484-compliant stringified forward reference child hints.
    #
    # Note that this test intentionally exercises the edge case of contextual
    # child hints subscripting otherwise non-contextual root hints such that the
    # former virally "infect" the latter with contextuality.
    assert_hint_check_expr_is_uncached(
        hint=type['At_this_through_all_his_bulk_an_agony'])

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
            # Assert that the make_check_expr() code factory avoids memoizing
            # PEP 673-compliant self root hints.
            assert_hint_check_expr_is_uncached(
                call_meta=decor_meta_pep673, hint=Self)
