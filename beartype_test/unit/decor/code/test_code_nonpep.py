#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright 2014-2020 by Cecil Curry.
# See "LICENSE" for further details.

'''
**Beartype decorator PEP-noncompliant type hint unit tests.**

This submodule unit tests the :func:`beartype.beartype` decorator with respect
to **PEP-noncompliant type hints** (i.e., :mod:`beartype`-specific annotations
*not* compliant with annotation-centric PEPs).
'''

# ....................{ IMPORTS                           }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from beartype_test.util.pyterror import raises_uncached
from pytest import raises
from random import Random

# ....................{ TODO                              }....................
#FIXME: Define new unit tests exercising:
#* Python >= 3.8-specific keyword-only parameters.

# ....................{ TESTS ~ pass : param : kind       }....................
def test_nonpep_param_kind_positional_or_keyword_pass() -> None:
    '''
    Test successful usage of the :func:`beartype.beartype` decorator for a
    function call passed non-variadic positional and/or keyword parameters
    annotated with PEP-noncompliant type hints.
    '''

    # Defer heavyweight imports.
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

    # Defer heavyweight imports.
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

    # Defer heavyweight imports.
    from beartype import beartype
    from beartype.roar import BeartypeCallCheckNonPepParamException

    # Decorated callable to be exercised.
    @beartype
    def imperium_of_man(
        space_marines: str, *ceaseless_years: int, primarch: str) -> str:
        return space_marines + str(ceaseless_years[1]) + primarch

    # Assert that calling this callable with invalid variadic positional
    # parameters raises the expected exception.
    with raises(BeartypeCallCheckNonPepParamException):
        imperium_of_man(
            'Legiones Astartes', 30, 31, 36, 'M41', primarch='Leman Russ')

# ....................{ TESTS ~ pass : param : type       }....................
def test_nonpep_pass_param_tuple() -> None:
    '''
    Test type-checking for a function call successfully passed a parameter
    annotated with a PEP-noncompliant tuple union.
    '''

    # Import this decorator.
    from beartype import beartype

    # Function to be type-checked. For completeness, test both an actual class
    # *AND* a the fully-qualified name of a class in this tuple annotation.
    @beartype
    def genestealer(tyranid: str, hive_fleet: (str, 'int')) -> str:
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


def test_nonpep_pass_param_ref() -> None:
    '''
    Test type-checking for a function call successfully passed a parameter
    annotated with a PEP-noncompliant fully-qualified forward reference
    referencing an existing attribute of an external module.
    '''

    # Import this decorator.
    from beartype import beartype

    # Dates between which the Sisters of Battle must have been established.
    ESTABLISHMENT_DATE_MIN = 36000
    ESTABLISHMENT_DATE_MAX = 37000

    # Function to be type-checked.
    @beartype
    def sisters_of_battle(
        leader: str, establishment: 'random.Random') -> int:
        return establishment.randint(
            ESTABLISHMENT_DATE_MIN, ESTABLISHMENT_DATE_MAX)

    # Call this function with an instance of the type named above.
    assert sisters_of_battle('Abbess Sanctorum', Random()) in range(
        ESTABLISHMENT_DATE_MIN, ESTABLISHMENT_DATE_MAX + 1)

# ....................{ TESTS ~ fail : param : call       }....................
def test_nonpep_fail_param_call_ref() -> None:
    '''
    Test type-checking for a function call unsuccessfully passed a parameter
    annotated with a PEP-noncompliant fully-qualified forward reference
    referencing an existing attribute of an external module.
    '''

    # Import this decorator.
    from beartype import beartype
    from beartype.roar import BeartypeCallCheckNonPepParamException

    # Dates between which the Black Legion must have been established.
    ESTABLISHMENT_DATE_MIN = 30000
    ESTABLISHMENT_DATE_MAX = 31000

    # Function to be type-checked.
    @beartype
    def black_legion(primarch: str, establishment: 'random.Random') -> int:
        return establishment.randint(
            ESTABLISHMENT_DATE_MIN, ESTABLISHMENT_DATE_MAX)

    # Call this function with an invalid type and assert the expected
    # exception.
    with raises(BeartypeCallCheckNonPepParamException):
        black_legion('Horus', 'Abaddon the Despoiler')


def test_nonpep_fail_param_call_tuple() -> None:
    '''
    Test type-checking for a function call unsuccessfully passed a parameter
    annotated with a PEP-noncompliant tuple union.
    '''

    # Import this decorator.
    from beartype import beartype
    from beartype.roar import BeartypeCallCheckNonPepParamException

    # Annotated function to be type-checked.
    @beartype
    def eldar(isha: str, asuryan: (str, int)) -> str:
        return isha + asuryan

    # Call this function with an invalid type and assert the expected
    # exception.
    with raises(BeartypeCallCheckNonPepParamException):
        eldar('Mother of the Eldar', 100.100)

# ....................{ TESTS ~ fail : param : hint       }....................
def test_nonpep_param_hint_ref_missing_fail() -> None:
    '''
    Test type-checking for a function with a parameter annotated with a
    PEP-noncompliant fully-qualified forward reference unsuccessfully
    referencing a non-existing attribute of a (hopefully) non-existing module.
    '''

    # Import this decorator.
    from beartype import beartype

    # Assert the expected exception from attempting to type-check a function
    # with a string parameter annotation referencing an unimportable module.
    with raises(ImportError):
        @beartype
        def eye_of_terror(
            ocularis_terribus: str,

            # While highly unlikely that a top-level module with this name will
            # ever exist, the possibility cannot be discounted. Since there
            # appears to be no syntactically valid module name prohibited from
            # existing, this is probably the best we can do.
            segmentum_obscurus: '__rand0m__.Warp',
        ) -> str:
            return ocularis_terribus + segmentum_obscurus

        eye_of_terror('Perturabo', 'Crone Worlds')

    # Assert the expected exception from attempting to type-check a function
    # with a string parameter annotation referencing a missing attribute of an
    # importable module.
    with raises(ImportError):
        @beartype
        def navigator(
            astronomicon: str,

            # While highly unlikely that a top-level module attribute with this
            # name will ever exist, the possibility cannot be discounted. Since
            # there appears to be no syntactically valid module attribute name
            # prohibited from existing, this is probably the best we can do.
            navis_nobilite: 'random.__Psych1cL1ght__',
        ) -> str:
            return astronomicon + navis_nobilite

        navigator('Homo navigo', 'Kartr Hollis')


def test_nonpep_param_hint_invalid_fail() -> None:
    '''
    Test type-checking for a function with a parameter annotated with a type
    hint that is neither PEP-compliant *nor* PEP-noncompliant.
    '''

    # Import this decorator.
    from beartype import beartype
    from beartype.roar import BeartypeDecorHintNonPepException

    # Assert that type-checking a function with an integer parameter annotation
    # raises the expected exception.
    with raises_uncached(BeartypeDecorHintNonPepException):
        @beartype
        def nurgle(nurgling: str, great_unclean_one: 0x8BADF00D) -> str:
            return nurgling + str(great_unclean_one)

# ....................{ TESTS ~ fail : return             }....................
def test_nonpep_fail_return_call() -> None:
    '''
    Test type-checking for a function call unsuccessfully returning a value
    annotated with a PEP-noncompliant type hint.
    '''

    # Import this decorator.
    from beartype import beartype
    from beartype.roar import BeartypeCallCheckNonPepReturnException

    # Annotated function to be type-checked.
    @beartype
    def necron(star_god: str, old_one: str) -> str:
        return 60e6

    # Call this function and assert the expected exception.
    with raises(BeartypeCallCheckNonPepReturnException):
        necron("C'tan", 'Elder Thing')


def test_nonpep_fail_return_hint_nonpep() -> None:
    '''
    Test type-checking for a function with a return value unsuccessfully
    annotated with a type hint that is neither PEP-compliant *nor*
    PEP-noncompliant.
    '''

    # Import this decorator.
    from beartype import beartype
    from beartype.roar import BeartypeDecorHintNonPepException

    # Assert the expected exception from attempting to type-check a function
    # with a return annotation that is *NOT* a supported type.
    with raises_uncached(BeartypeDecorHintNonPepException):
        @beartype
        def tzeentch(disc: str, lord_of_change: str) -> 0xB16B00B5:
            return len(disc + lord_of_change)
