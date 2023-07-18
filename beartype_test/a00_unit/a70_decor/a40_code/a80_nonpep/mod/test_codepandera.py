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
from beartype_test._util.mark.pytskip import skip_unless_package

# ....................{ TESTS                              }....................
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
    from beartype.roar import (
        BeartypeCallHintParamViolation,
        BeartypeCallHintReturnViolation,
    )
    from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_10
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
    # "PanderaModel" defined below.
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
    # "PanderaModel" defined below.
    pandas_dataframe_bad = DataFrame()

    # ....................{ CLASSES                        }....................
    class PanderaModel(DataFrameModel):
        '''
        Pandera model validating the ``pandas_dataframe_good`` defined above.
        '''

        Hexspeak: Series[Int64]
        OdeToTheWestWind: Series[String]
        PercyByssheShelley: Series[Timestamp]

    #FIXME: Preserved for debuggability. Uncomment as needed, please.
    # hint = PanderaDataFrame[PanderaModel]
    # hint_origin = hint.__origin__
    # # print(f'\nrepr(hint): {repr(hint)}')
    # # print(f'\ndir(hint): {dir(hint)}')
    # # print(f'\ntype(hint): {type(hint)}')
    # # from pandera.typing.pandas import DataFrame as NestedPanderaDataFrame
    # # print(f'\nis hint_origin a pandera dataframe? {hint_origin is NestedPanderaDataFrame}')
    # # print(f'\nrepr(hint_origin): {repr(hint_origin)}')
    # # print(f'\ndir(hint_origin): {dir(hint_origin)}')
    # print(f'\nmro(hint_origin): {hint_origin.__mro__}')
    # # print(f'\ntype(hint_origin): {type(hint_origin)}')
    # print(f'\nhint_origin.__orig_bases__: {hint_origin.__orig_bases__}')
    # print(f'is pandas dataframe a pandera dataframe? {isinstance(pandas_dataframe_good, hint_origin)}')
    # print(f'is pandas dataframe an orig dataframe? {isinstance(pandas_dataframe_good, hint_origin.__orig_bases__)}')
    # # print(f'is pandas dataframe a pandera dataframe? {isinstance(pandas_dataframe_good, NestedPanderaDataFrame)}')
    # # print(f'is pandas dataframe an orig dataframe? {isinstance(pandas_dataframe_good, NestedPanderaDataFrame.__orig_bases__)}')
    # from beartype import BeartypeConf
    # @beartype(conf=BeartypeConf(is_debug=True))

    # ....................{ FUNCTIONS                      }....................
    @beartype
    @check_types
    def to_the_zeniths_height(
        dataframe: PanderaDataFrame[PanderaModel],
        of_some_fierce_maenad: str,
    ) -> str:
        '''
        Arbitrary callable decorated first by :mod:`beartype` and then by
        :mod:`pandera`, accepting a parameter annotated by a Pandera type hint
        *and* a parameter annotated by a non-Pandera PEP-compliant type hint.

        This callable exercises that:

        * The :func:`pandera.check_types` decorator type-checks the parameter
          annotated by the Pandera type hint.
        * The :func:`beartype.beartype` decorator type-checks the parameter
          annotated by the non-Pandera type hint.
        '''

        # Return this string parameter appended by an arbitrary constant.
        return f'{of_some_fierce_maenad}, even from the dim verge'
    # print(f'PanderaDataFrame[pandera_schema]: {repr(PanderaDataFrame[pandera_schema])}')


    @check_types
    @beartype
    def all_thy_congregated_might(
        dataframe: PanderaDataFrame[PanderaModel],
        of_some_fierce_maenad: str,
    ) -> str:
        '''
        Arbitrary callable decorated first by :mod:`pandera` and then by
        :mod:`beartype`, accepting a parameter annotated by a Pandera type hint
        *and* a parameter annotated by a non-Pandera PEP-compliant type hint.

        This callable exercises that order of decoration is insignificant.
        '''

        # Return this string parameter appended by an arbitrary constant.
        return f'{of_some_fierce_maenad}, even from the dim verge'


    @beartype
    def from_whose_solid_atmosphere(
        dataframe: PanderaDataFrame[PanderaModel],
        of_some_fierce_maenad: str,
    ) -> str:
        '''
        Arbitrary callable decorated by :mod:`beartype` but *not* by
        :mod:`pandera`, accepting a parameter annotated by a Pandera type hint
        *and* a parameter annotated by a non-Pandera PEP-compliant type hint.

        This callable exercises that the :func:`beartype.beartype` decorator at
        least shallowly type-checks all passed parameters regardless of whether
        this callable is also decorated by the :func:`pandera.check_types`
        decorator.
        '''

        # Return this string parameter appended by an arbitrary constant.
        return f'{of_some_fierce_maenad}, even from the dim verge'


    # Tuple of all functions defined above decorated by @pandera.check_types.
    TEST_FUNCS_PANDERA = (
        to_the_zeniths_height,
        all_thy_congregated_might,
    )

    # Tuple of all functions defined above.
    TEST_FUNCS = TEST_FUNCS_PANDERA + (
        from_whose_solid_atmosphere,
    )

    # ....................{ ASSERTS                        }....................
    # For each function defined above to be tested...
    for test_func in TEST_FUNCS:
        # ....................{ PASS                       }....................
        # Assert that calling this function with valid parameters returns the
        # expected value.
        assert test_func(
            dataframe=pandas_dataframe_good,
            of_some_fierce_maenad='Of some fierce Maenad',
        ) == 'Of some fierce Maenad, even from the dim verge'

        # ....................{ FAIL                       }....................
        # Assert that calling this function with an invalid parameter managed by
        # @beartype raises the expected @beartype exception.
        with raises(BeartypeCallHintParamViolation):
            test_func(
                dataframe=pandas_dataframe_good,
                of_some_fierce_maenad=b'The locks of the approaching storm.',
            )

        # Assert that calling this function with an invalid parameter shallowly
        # type-checked by @beartype raises an... exception.
        #
        # Currently, Pandera currently fails to perform similar shallow
        # type-checking. Instead, Pandera silently ignores parameters that are
        # *NOT* of the expected type. Since this behaviour is both bizarre and
        # erroneous, future releases of Pandera are likely to at least shallowly
        # type-check parameters annotated by Pandera type hints. For forward
        # compatibility, we avoid asserting the exact type of this exception.
        # with raises(Exception):
        with raises(BeartypeCallHintParamViolation):
            test_func(
                dataframe='Black rain, and fire, and hail will burst: oh hear!',
                of_some_fierce_maenad=b'The locks of the approaching storm.',
            )

    # ....................{ ASSERTS ~ pandera              }....................
    # For each function defined above decorated by @pandera.check_types...
    for test_func_pandera in TEST_FUNCS_PANDERA:
        # ....................{ FAIL                       }....................
        # Assert that calling this function with an invalid parameter managed by
        # Pandera raises the expected Pandera exception.
        with raises(SchemaError):
            test_func_pandera(
                dataframe=pandas_dataframe_bad,
                of_some_fierce_maenad='Of some fierce Maenad',
            )

    # ....................{ MORE                           }....................
    # Functions defined above suffice for the trivial case of type-checking a
    # data frame passed as a parameter. Let's generalize that with an additional
    # function also type-checking a series returned as a value.

    # If the active Python interpreter supports Python >= 3.10 and thus the "|"
    # type union operator utilized below...
    if IS_PYTHON_AT_LEAST_3_10:
        @beartype
        @check_types
        def convert_dataframe_column_to_series(
            dataframe: PanderaDataFrame[PanderaModel],
            column_name_or_index: str | int,
        ) -> Series[Int64 | String | Timestamp]:
            '''
            Convert the column of the passed pandas data frame (identified by
            the passed column name or index) into a pandas series.
            '''

            # Return either...
            return (
                # If the caller passed a column name, the non-series column with
                # this name.
                #
                # Note that columns are *NOT* series; ergo, this return value
                # intentionally violates this return type hint. Doing so enables
                # us to assert that @beartype correctly type-checks return
                # violations involving pandera type hints.
                dataframe.loc
                # dataframe.loc[:,column_name_or_index]
                if isinstance(column_name_or_index, str) else
                # Else, the caller passed a column index. In this case, the
                # series converted from the column with this name.
                #
                # Note that this return value intentionally satisfies this hint.
                dataframe.iloc[:,column_name_or_index]
            )

        # Assert that calling this function with valid parameters but returning
        # an invalid value raises the expected exception.
        with raises(BeartypeCallHintReturnViolation):
            convert_dataframe_column_to_series(
                dataframe=pandas_dataframe_good, column_name_or_index='Hexspeak')

        # Assert that calling this function with valid parameters and returning
        # a valid value returns the expected object.
        pandas_series = convert_dataframe_column_to_series(
            dataframe=pandas_dataframe_good, column_name_or_index=0)
        assert len(pandas_series) == 3
