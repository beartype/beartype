#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype decorator** :pep:`612`-compliant :obj:`typing.Self` **unit tests**.

This submodule unit tests :pep:`612` support implemented in the
:func:`beartype.beartype` decorator.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from beartype_test._util.mark.pytskip import skip_if_python_version_less_than

# ....................{ TESTS                              }....................
@skip_if_python_version_less_than('3.10.0')
def test_decor_pep612() -> None:
    '''
    Test :pep:`612` support implemented in the :func:`beartype.beartype`
    decorator if the active Python interpreter targets Python >= 3.10 *or* skip
    otherwise.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype import beartype
    from beartype.door import (
        die_if_unbearable,
        is_bearable,
    )
    from beartype.roar import BeartypeDecorHintPep612Exception
    from beartype.typing import (
        ParamSpec,
        Tuple,
    )
    from beartype._data.hint.datahinttyping import DictStrToAny
    from pytest import raises

    # ....................{ LOCALs                         }....................
    # Arbitrary parameter specification.
    P = ParamSpec('P')

    # ....................{ CALLABLES                      }....................
    @beartype
    def as_shapes(
        *in_the_weird_clouds: P.args,
        **soft_mossy_lawns: P.kwargs,
    ) -> Tuple[tuple, DictStrToAny]:
        '''
        Arbitrary callable accepting both variadic positional and keyword
        parameters correctly annotated by :pep:`612`-compliant parameter
        specification positional and keyword parameter type hints, decorated by
        :func:`beartype.beartype`.
        '''

        # Return these variadic parameters as is.
        return in_the_weird_clouds, soft_mossy_lawns

    # ....................{ PASS                           }....................
    # Assert that a callable accepting both variadic positional and keyword
    # parameters correctly annotated by valid PEP 612-compliant parameter
    # specification positional and keyword parameter type hints returns the
    # expected object.
    assert as_shapes(
        'Beneath these canopies extend their swells',
        Fragrant_with_perfumed_herbs='and eyed with blooms',
    ) == (
        ('Beneath these canopies extend their swells',),
        {'Fragrant_with_perfumed_herbs': 'and eyed with blooms'},
    )

    # ....................{ FAIL                           }....................
    # Assert that @beartype raises the expected exception when decorating
    # callables accepting only one of rather than both variadic positional and
    # keyword parameters annotated by PEP 612-compliant parameter specification
    # keyword and positional parameter type hints.
    with raises(BeartypeDecorHintPep612Exception):
        @beartype
        def their_noonday_watch(*and_sail_among_the_shades: P.args) -> None:
            pass
    with raises(BeartypeDecorHintPep612Exception):
        @beartype
        def like_vaporous_shapes_half_seen(**beyond_a_well: P.kwargs) -> None:
            pass

    # Assert that @beartype raises the expected exception when decorating
    # callables accepting both variadic positional and keyword parameters such
    # that only one rather than both are annotated.
    with raises(BeartypeDecorHintPep612Exception):
        @beartype
        def dark(*gleaming, **and_of_most_translucent_wave: P.kwargs) -> None:
            pass

    # Assert that @beartype raises the expected exception when decorating
    # callables accepting both variadic positional and keyword parameters such
    # that only one rather than both are annotated by PEP 612-compliant
    # parameter specification keyword and positional parameter type hints.
    with raises(BeartypeDecorHintPep612Exception):
        @beartype
        def images_all(*the_woven_boughs: int, **above: P.kwargs) -> None:
            pass

    # Assert that @beartype raises the expected exception when decorating
    # callables accepting both variadic positional and keyword parameters
    # erroneously annotated by PEP 612-compliant parameter specification keyword
    # and positional parameter type hints (i.e., in erroneous order).
    with raises(BeartypeDecorHintPep612Exception):
        @beartype
        def a_soul_dissolving_odour(
            *to_invite: P.kwargs,
            **to_some_more_lovely_mystery: P.args,
        ) -> None:
            pass

    # Assert that @beartype raises the expected exception when decorating
    # callables accepting non-variadic parameters erroneously annotated by PEP
    # 612-compliant parameter specification keyword and positional parameter
    # type hints.
    with raises(BeartypeDecorHintPep612Exception):
        @beartype
        def through_the_dell(silence_and_twilight_here: P.args) -> None:
            pass
    with raises(BeartypeDecorHintPep612Exception):
        @beartype
        def twin_sisters(keep: P.kwargs) -> None:
            pass

    # Assert that statement-level runtime type-checkers raise the expected
    # exceptions when passed PEP 612-compliant parameter specification variadic
    # parameter type hints.
    with raises(BeartypeDecorHintPep612Exception):
        die_if_unbearable('Minute yet beautiful. One darkest glen', P.args)
    with raises(BeartypeDecorHintPep612Exception):
        is_bearable(
            'Sends from its woods of musk-rose, twined with jasmine,', P.kwargs)
