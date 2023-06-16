#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype decorator PEP-noncompliant type hint unit tests.**

This submodule unit tests the :func:`beartype.beartype` decorator with respect
to **PEP-noncompliant type hints** (i.e., :mod:`beartype`-specific annotations
*not* compliant with annotation-centric PEPs).
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TODO                               }....................
#FIXME: Define new unit tests exercising:
#* Python >= 3.8-specific keyword-only parameters.

# ....................{ TESTS ~ pass : param : kind        }....................
def test_nonpep_param_kind_positional_or_keyword_pass() -> None:
    '''
    Test successful usage of the :func:`beartype.beartype` decorator for a
    function call passed non-variadic positional and/or keyword parameters
    annotated with PEP-noncompliant type hints.
    '''

    # Defer test-specific imports.
    from beartype import beartype

    # Decorated callable to be exercised.
    @beartype
    def slaanesh(daemonette: str, keeper_of_secrets: str) -> str:
        return daemonette + keeper_of_secrets

    # Assert that calling this callable with both positional and keyword
    # arguments returns the expected return value.
    assert slaanesh(
        'Seeker of Decadence', keeper_of_secrets="N'Kari") == (
        "Seeker of DecadenceN'Kari")


def test_nonpep_param_kind_variadic_and_keyword_only_pass() -> None:
    '''
    Test successful usage of the :func:`beartype.beartype` decorator for a
    function call passed variadic positional parameters followed by a
    keyword-only parameter, all annotated with PEP-noncompliant type hints.
    '''

    # Defer test-specific imports.
    from beartype import beartype

    # Decorated callable to be exercised.
    @beartype
    def changer_of_ways(
        sky_shark: str, *dark_chronology: int, chaos_spawn: str) -> str:
        return (
            sky_shark +
            str(dark_chronology[0]) +
            str(dark_chronology[-1]) +
            chaos_spawn
        )

    # Assert that calling this callable with variadic positional parameters
    # followed by a keyword-only parameter returns the expected return value.
    assert changer_of_ways(
        'Screamers', 0, 1, 15, 25, chaos_spawn="Mith'an'driarkh") == (
        "Screamers025Mith'an'driarkh")



def test_nonpep_param_kind_variadic_fail() -> None:
    '''
    Test unsuccessful usage of the :func:`beartype.beartype` decorator for a
    function call passed variadic positional parameters annotated with
    PEP-noncompliant type hints.
    '''

    # Defer test-specific imports.
    from beartype import beartype
    from beartype.roar import BeartypeCallHintParamViolation
    from pytest import raises

    # Decorated callable to be exercised.
    @beartype
    def imperium_of_man(
        space_marines: str, *ceaseless_years: int, primarch: str) -> str:
        return space_marines + str(ceaseless_years[1]) + primarch

    # Assert that calling this callable with invalid variadic positional
    # parameters raises the expected exception.
    with raises(BeartypeCallHintParamViolation):
        imperium_of_man(
            'Legiones Astartes', 30, 31, 36, 'M41', primarch='Leman Russ')

# ....................{ TESTS ~ pass : param : type        }....................
def test_nonpep_pass_param_tuple() -> None:
    '''
    Test type-checking for a function call successfully passed a parameter
    annotated with a PEP-noncompliant tuple union.
    '''

    # Import this decorator.
    from beartype import beartype

    # Function to be type-checked. For completeness, test both an actual class
    # *AND* a forward reference to an actual class in this tuple annotation.
    @beartype
    def genestealer(tyranid: str, hive_fleet: (str, 'builtins.int')) -> str:
        return tyranid + str(hive_fleet)

    # Call this function with each of the two types listed in the above tuple.
    assert genestealer('Norn-Queen', 'Behemoth') == 'Norn-QueenBehemoth'
    assert genestealer('Carnifex', 0xDEADBEEF) == 'Carnifex3735928559'


def test_nonpep_pass_param_custom() -> None:
    '''
    Test type-checking for a function call successfully passed a parameter
    annotated as a user-defined class.
    '''

    # Import this decorator.
    from beartype import beartype

    # User-defined type.
    class CustomTestStr(str):
        pass

    # Function to be type-checked.
    @beartype
    def hrud(gugann: str, delphic_plague: CustomTestStr) -> str:
        return gugann + delphic_plague

    # Call this function with each of the above type.
    assert hrud(
        'Troglydium hruddi', delphic_plague=CustomTestStr('Delphic Sink')) == (
        'Troglydium hruddiDelphic Sink')

# ....................{ TESTS ~ fail : param : call        }....................
def test_nonpep_fail_param_call_tuple() -> None:
    '''
    Test type-checking for a function call unsuccessfully passed a parameter
    annotated with a PEP-noncompliant tuple union.
    '''

    # Import this decorator.
    from beartype import beartype
    from beartype.roar import BeartypeCallHintParamViolation
    from pytest import raises

    # Annotated function to be type-checked.
    @beartype
    def eldar(isha: str, asuryan: (str, int)) -> str:
        return isha + asuryan

    # Call this function with an invalid type and assert the expected
    # exception.
    with raises(BeartypeCallHintParamViolation):
        eldar('Mother of the Eldar', 100.100)

# ....................{ TESTS ~ fail : param : hint        }....................
def test_nonpep_param_hint_invalid_fail() -> None:
    '''
    Test type-checking for a function with a parameter annotated with a type
    hint that is neither PEP-compliant *nor* PEP-noncompliant.
    '''

    # Import this decorator.
    from beartype import beartype
    from beartype.roar import BeartypeDecorHintNonpepException
    from beartype_test._util.pytroar import raises_uncached

    # Assert that type-checking a function with an integer parameter annotation
    # raises the expected exception.
    with raises_uncached(BeartypeDecorHintNonpepException):
        @beartype
        def nurgle(nurgling: str, great_unclean_one: 0x8BADF00D) -> str:
            return nurgling + str(great_unclean_one)

# ....................{ TESTS ~ fail : return              }....................
def test_nonpep_fail_return_call() -> None:
    '''
    Test type-checking for a function call unsuccessfully returning a value
    annotated with a PEP-noncompliant type hint.
    '''

    # Import this decorator.
    from beartype import beartype
    from beartype.roar import BeartypeCallHintReturnViolation
    from pytest import raises

    # Annotated function to be type-checked.
    @beartype
    def necron(star_god: str, old_one: str) -> str:
        return 60e6

    # Call this function and assert the expected exception.
    with raises(BeartypeCallHintReturnViolation):
        necron("C'tan", 'Elder Thing')


def test_nonpep_fail_return_hint_nonpep() -> None:
    '''
    Test type-checking for a function with a return value unsuccessfully
    annotated with a type hint that is neither PEP-compliant *nor*
    PEP-noncompliant.
    '''

    # Import this decorator.
    from beartype import beartype
    from beartype.roar import BeartypeDecorHintNonpepException
    from beartype_test._util.pytroar import raises_uncached

    # Assert the expected exception from attempting to type-check a function
    # with a return annotation that is *NOT* a supported type.
    with raises_uncached(BeartypeDecorHintNonpepException):
        @beartype
        def tzeentch(disc: str, lord_of_change: str) -> 0xB16B00B5:
            return len(disc + lord_of_change)
