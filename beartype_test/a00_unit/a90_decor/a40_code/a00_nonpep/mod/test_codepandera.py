#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype decorator PEP-noncompliant Pandera type hint unit tests.**

This submodule unit tests the :func:`beartype.beartype` decorator with respect
to **PEP-noncompliant Pandera type hints** (i.e., :mod:`pandera.typing`-specific
annotations *not* compliant with annotation-centric PEPs).
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from beartype_test._util.mark.pytskip import skip, skip_unless_package

# ....................{ TESTS                              }....................
#FIXME: Remove after no longer broke, please.
# @skip('Currently broke af, yo!')
@skip_unless_package('pandera')
def test_decor_pandera() -> None:
    '''
    Test that the :func:`beartype.beartype` decorator conditionally ignores
    *all* Pandera type hints.

    Pandera type hints violate Python typing standards and thus require use of
    Pandera-specific functionality to type-check. This includes the non-standard
    :func:`pandera.check_types` decorator, which performs ad-hoc
    PEP-noncompliant runtime type-checking of ad-hoc PEP-noncompliant Pandera
    type hints annotating the decorated callable. Since type-checking Pandera
    type hints *de facto* requires usage of this decorator, the PEP-compliant
    :func:`beartype.beartype` decorator *cannot* natively type-check Pandera
    type hints. Instead, :func:`beartype.beartype` can only:

    * Detect that Pandera type hints are type-checked by a prior application of
      :func:`pandera.check_types` on the decorated callable.
    * If so, ignore *all* Pandera type hints.
    * Else, raise an exception.

    Whereas this test suite automates testing of PEP-compliant type hints via
    the :mod:`beartype_test.a00_unit.data` subpackage, Pandera type hints are
    fundamentally non-standard and thus *cannot* be automated in this standard
    manner. These hints can *only* be tested with a non-standard workflow
    implemented by this unit test.

    See Also
    ----------
    https://pandera.readthedocs.io/en/stable/dataframe_models.html
        Official introduction to the :func:`pandera.check_types` decorator.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    #
    # Note that Pandera requires Pandas, which requires NumPy. Ergo, both Pandas
    # and NumPy are guaranteed to be safely importable here.
    from beartype import beartype
    from beartype.roar import BeartypeCallHintParamViolation
    from pandas import (
        DataFrame,
        to_datetime,
    )
    from pandera import (
        # Column,
        DataFrameModel,
        # Index,
        check_types,
    )
    from pandera.dtypes import (
        Int64,
        String,
        Timestamp,
    )
    from pandera.errors import SchemaError
    from pandera.typing import (
        DataFrame as PanderaDataFrame,
        Series,
    )
    from pytest import raises

    # ....................{ LOCALS                         }....................
    # Pandas data frame containing arbitrary sample data satisfying the
    # "PanderasModel" defined below.
    pandas_dataframe_good = DataFrame({
        'Hexspeak': (
            0xCAFED00D,
            0xCAFEBABE,
            0x1337BABE,
        ),
        'OdeToTheWestWind': (
            'Angels of rain and lightning: there are spread',
            'On the blue surface of thine aery surge,',
            'Like the bright hair uplifted from the head',
        ),
        'PercyByssheShelley': to_datetime((
            '1792-08-04',
            '1822-07-08',
            '1851-02-01',
        )),
    })

    # Pandas data frame containing arbitrary sample data violating the
    # "PanderasModel" defined below.
    pandas_dataframe_bad = DataFrame()

    # ....................{ LOCALS                         }....................
    class PanderasModel(DataFrameModel):
        '''
        Pandera model validating the ``pandas_dataframe_good`` defined above.
        '''

        Hexspeak: Series[Int64]
        OdeToTheWestWind: Series[String]
        PercyByssheShelley: Series[Timestamp]


    @beartype
    @check_types
    def to_the_zeniths_height(
        dataframe: PanderaDataFrame[PanderasModel],
        of_some_fierce_maenad: str,
    ) -> str:
        '''
        Arbitrary callable accepting both a parameter annotated by a Pandera
        type hint *and* a parameter annotated by a non-Pandera PEP-compliant
        type hint.

        This callable exercises that:

        * The :func:`pandera.check_types` decorator type-checks the parameter
          annotated by the Pandera type hint.
        * The :func:`beartype.beartype` decorator type-checks the parameter
          annotated by the non-Pandera type hint.
        '''

        # Return this string parameter appended by an arbitrary constant.
        return f'{of_some_fierce_maenad}, even from the dim verge'
    # print(f'PanderaDataFrame[pandera_schema]: {repr(PanderaDataFrame[pandera_schema])}')

    # ....................{ PASS                           }....................
    # Assert that calling this callable with valid parameters returns the
    # expected value.
    assert to_the_zeniths_height(
        dataframe=pandas_dataframe_good,
        of_some_fierce_maenad='Of some fierce Maenad',
    ) == 'Of some fierce Maenad, even from the dim verge'

    # ....................{ FAIL                           }....................
    # Assert that calling this callable with an invalid parameter managed by
    # @beartype raises the expected @beartype exception.
    with raises(BeartypeCallHintParamViolation):
        to_the_zeniths_height(
            dataframe=pandas_dataframe_good,
            of_some_fierce_maenad=b'The locks of the approaching storm.',
        )

    # Assert that calling this callable with an invalid parameter managed by
    # Pandera raises the expected Pandera exception.
    with raises(SchemaError):
        to_the_zeniths_height(
            dataframe=pandas_dataframe_bad,
            of_some_fierce_maenad='Of some fierce Maenad',
        )
