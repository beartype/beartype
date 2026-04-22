#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype decorator configuration** unit tests.

This submodule unit tests high-level functionality of the
:func:`beartype.beartype` decorator configured by the optional ``conf``
keyword-only parameter.

This submodule does *not* exercise fine-grained configuration (e.g., of
individual type-checking strategies), which is delegated to more relevant tests
elsewhere; rather, this submodule exercises this decorator to be configurable
as expected from a high-level API perspective.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS                              }....................
def test_decor_conf() -> None:
    '''
    Test the :func:`beartype.beartype` decorator against the optional ``conf``
    parameter agnostic of parameters instantiating that configuration.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype import (
        BeartypeConf,
        BeartypeStrategy,
        beartype,
    )
    from beartype.roar import BeartypeConfException
    from beartype_test._util.error.pyterrraise import raises_uncached

    # ....................{ PASS                           }....................
    # Assert that @beartype in configuration mode returns the default private
    # decorator when repeatedly invoked with the default configuration.
    assert (
        # Assert that the first @beartype call passed *NO* arguments internally
        # creates and returns the same default private decorator as...
        beartype() is
        # Another @beartype call passed *NO* arguments as well as...
        beartype() is
        # Another @beartype call passed the default configuration.
        beartype(conf=BeartypeConf())
    )

    # Assert that @beartype in configuration mode returns the same non-default
    # private decorator when repeatedly invoked with the same non-default
    # configuration.
    assert (
        beartype(conf=BeartypeConf(
            is_debug=True,
            strategy=BeartypeStrategy.On,
        )) is
        beartype(conf=BeartypeConf(
            is_debug=True,
            strategy=BeartypeStrategy.On,
        ))
    )

    # ....................{ FAIL                           }....................
    # Assert that @beartype raises the expected exception when passed a "conf"
    # parameter that is *NOT* a configuration.
    with raises_uncached(BeartypeConfException):
        beartype(conf='Within the daedal earth; lightning, and rain,')

# ....................{ TESTS ~ bool                       }....................
def test_decor_conf_is_debug(capsys) -> None:
    '''
    Test the :func:`beartype.beartype` decorator passed the optional ``conf``
    parameter passed the optional ``is_debug`` parameter.

    Parameters
    ----------
    capsys
        :mod:`pytest` fixture enabling standard output and error to be reliably
        captured and tested against from within unit tests and fixtures.

    Parameters
    ----------
    https://docs.pytest.org/en/latest/how-to/capture-stdout-stderr.html#accessing-captured-output-from-a-test-function
        Official ``capsys`` reference documentation.
    '''

    # ..................{ IMPORTS                            }..................
    # Defer test-specific imports.
    from beartype import (
        BeartypeConf,
        beartype,
    )
    from beartype._util.func.utilfunccodeobj import (
        get_func_codeobject,
        get_codeobject_filename,
    )
    from linecache import cache as linecache_cache

    # ..................{ LOCALS                             }..................
    # @beartype decorator enabling debugging.
    bugbeartype = beartype(conf=BeartypeConf(is_debug=True))

    # _earthquake() function beartyped with debugging enabled.
    earthquake_beartyped = bugbeartype(_earthquake)

    # Pytest object freezing the current state of standard output and error as
    # uniquely written to by this unit test up to this statement.
    std_captured = capsys.readouterr()

    # String of all captured standard output.
    stdout = std_captured.out

    # List of zero or more lines of this captured standard output.
    stdout_lines = stdout.splitlines(keepends=True)

    # ..................{ STDOUT                             }..................
    # Assert the prior decoration printed the expected definition.
    assert 'line' in stdout
    assert 'def _earthquake(' in stdout
    assert 'return' in stdout
    assert '# is <function _earthquake ' in stdout

    # ..................{ LINECACHE                          }..................
    # This is probably overkill, but check to see that we generated lines in our
    # linecache that correspond to the ones we printed. This a fragile coupling.
    # We can relax this later to avoid making those line-by-line comparisons and
    # just check for the decorated function's filename's presence in the cache.

    #FIXME: Just call get_func_filename_or_none() instead. *shrug*
    # Absolute filename of the fake file declaring the earthquake_beartyped()
    # function.
    earthquake_beartyped_filename = (
        get_codeobject_filename(get_func_codeobject(earthquake_beartyped)))

    # Assert that the standard "linecache" module cached metadata describing the
    # earthquake_beartyped() function.
    assert earthquake_beartyped_filename in linecache_cache

    # Metadata describing the earthquake_beartyped() function previously cached
    # by the "linecache" module.
    code_len, code_mtime, code_lines, code_filename = linecache_cache[
        earthquake_beartyped_filename]

    # Assert that "linecache" cached the expected metadata.
    assert code_filename == earthquake_beartyped_filename
    assert code_mtime is None

    # Assert that @bugbeartype printed as many lines of source code as that of
    # the _earthquake() function defined below.
    # print(f'code_lines: {code_lines}\nstdout_lines: {stdout_lines}')
    assert len(code_lines) == len(stdout_lines)

    # For each printed and original line of source code underlying the
    # _earthquake() function...
    for code_line, stdout_line in zip(code_lines, stdout_lines):
        # Assert that this original line of source code is a substring of this
        # printed line of source code -- which contains additional:
        # * Prefixing substrings (e.g., line numbers).
        # * Suffixing substrings (e.g., diagnostic comments).
        assert code_line in stdout_line

# ....................{ TESTS ~ strategy                   }....................
def test_decor_conf_strategy_O0() -> None:
    '''
    Test the :func:`beartype.beartype` decorator passed the optional ``conf``
    parameter passed the optional ``strategy`` parameter whose value is the
    **no-time strategy** (i.e., :attr:`beartype.BeartypeStrategy.O0).
    '''

    # ..................{ IMPORTS                            }..................
    # Defer test-specific imports.
    from beartype import (
        BeartypeConf,
        BeartypeStrategy,
        beartype,
    )
    from beartype.roar import BeartypeCallHintReturnViolation
    from beartype_test._util.error.pyterrraise import raises_uncached

    # ..................{ LOCALS                             }..................
    # @beartype decorator disabling type-checking.
    nobeartype = beartype(conf=BeartypeConf(strategy=BeartypeStrategy.O0))

    # ..................{ CALLABLES                          }..................
    def in_the_lone_glare_of_day() -> str:
        '''
        Arbitrary **unignorable invalid callable** (i.e., callable defining at
        least one PEP-compliant type hint and thus *not* ignorable by the
        :func:`beartype.beartype` decorator, which violates that type hint).
        '''

        return b'In the lone glare of day, the snows descend'

    # ..................{ CLASSES                            }..................
    @beartype
    class UponThatMountain(object):
        '''
        Arbitrary class decorated by the :func:`beartype.beartype` decorator.
        '''

        # ..................{ METHODS                        }..................
        def none_beholds_them_there(self) -> None:
            '''
            Arbitrary method raising a type-checking violation by definition.
            '''

            return 'Upon that Mountain; none beholds them there,'


        @nobeartype
        def nor_when_the_flakes_burn(self) -> None:
            '''
            Arbitrary method raising *no* type-checking violation despite
            violating type-checking.
            '''

            return 'Nor when the flakes burn in the sinking sun,'

        # ....................{ DESCRIPTORS                }....................
        # Builtin C-based descriptor decorators exercising various edge cases.

        #FIXME: Exercise class and property methods as well, please. *sigh*
        # Explicitly disable runtime type-checking for this static method.
        @nobeartype
        @staticmethod
        def without_a_stir(dream: str) -> str:
            return dream

    # ..................{ LOCALS                             }..................
    # Instance of this class.
    upon_that_mountain = UponThatMountain()

    # ..................{ PASS ~ callable                    }..................
    # Assert that this decorator is the identity decorator unconditionally
    # preserving all passed objects as is.
    in_the_lone_glare_of_day_unchecked = nobeartype(in_the_lone_glare_of_day)
    assert in_the_lone_glare_of_day_unchecked is in_the_lone_glare_of_day

    # Assert that calling this decorated callable raises *NO* type-checking
    # violations despite this underlying callable violating type-checking.
    assert isinstance(in_the_lone_glare_of_day_unchecked(), bytes)

    # ..................{ PASS ~ class                       }..................
    # Assert that calling an invalid method explicitly *NOT* type-checked by
    # @beartype raises *NO* exception.
    assert isinstance(upon_that_mountain.nor_when_the_flakes_burn(), str)

    # Assert that calling a valid method explicitly *NOT* type-checked by
    # @beartype raises *NO* exception when passed an invalid parameter.
    assert UponThatMountain.without_a_stir(
        len('Which comes upon the silence, and dies off,')) == 43

    # ..................{ FAIL ~ class                       }..................
    # Assert that calling an invalid method implicitly type-checked by @beartype
    # raises the expected exception.
    with raises_uncached(BeartypeCallHintReturnViolation):
        upon_that_mountain.none_beholds_them_there()


def test_decor_conf_strategy_O1_nonrandom() -> None:
    '''
    Test the :func:`beartype.beartype` decorator passed the optional ``conf``
    parameter disabling the optional ``is_random`` parameter while still
    retaining the **default constant-time strategy** (i.e.,
    :attr:`beartype.BeartypeStrategy.O1`).

    This unit test validates that :mod:`beartype` correctly generates
    deterministic (rather than non-deterministic) type-checks for this use case.
    '''

    # ..................{ IMPORTS                            }..................
    # Defer test-specific imports.
    from beartype import (
        BeartypeConf,
        beartype,
    )
    from beartype.roar import BeartypeCallHintParamViolation
    from beartype_test._util.error.pyterrraise import raises_uncached
    from collections.abc import Iterable

    # ..................{ CALLABLES                          }..................
    @beartype(conf=BeartypeConf(is_random=False))
    def possessed_for_glory(
        two_fair_argent_wings: list[str],
        though_a_primeval_god: Iterable[str],
    ) -> int:
        '''
        Arbitrary callable decorated by a :func:`beartype.beartype` decorator
        enabling deterministic constant-time type-checking accepting both:

        * An arbitrary pure-Python sequence trivially annotated as such.
        * An arbitrary pure-Python **quasiiterable** (i.e., potentially unsafe
          container that is *not* guaranteed to be safely reiterable), which are
          *only* annotatable as either:

          * A deprecated :pep:`484`-compliant ``typing.Iterable[...]`` hint.
            Feasible, but clearly not a great idea due to deprecation.
          * A non-deprecated :pep:`585`-compliant
            ``collections.abc.Iterable[...]`` hint. A significantly better idea.

        :func:`beartype.beartype` currently generates non-deterministic
        type-checking code *only* for sequence and quasiiterable type hints. The
        only means of validating that disabling the :attr:`.Beartype.is_random``
        parameter properly disables non-deterministic type-checking for both is
        thus to annotate a callable by both.
        '''

        # Trivialize this one-liner to the max, Captain!
        return len(two_fair_argent_wings) + len(though_a_primeval_god)

    # ..................{ LOCALS                             }..................
    # Arbitrary Pure-Python empty sequence.
    fain_took_throne = []

    # Arbitrary Pure-Python non-empty sequence containing two or more items all
    # *SATISFYING* the sequence type hints annotating the above callable.
    the_gods_approach = [
        "Ever exalted at the God's approach:",
        'And now, from forth the gloom their plumes immense',
        'Rose, one by one, till all outspreaded were;',
    ]

    # Arbitrary Pure-Python non-empty sequence containing two or more items such
    # that:
    # * Only the first item *VIOLATES* the sequence type hints annotating the
    #   above callable.
    # * All subsequent items *SATISFY* those hints.
    #
    # Why such a specific schema? Because the deterministic type-checking
    # dynamically generated by @beartype when the "is_random" parameter is
    # disabled (as above) currently type-checks *ONLY* the first item of each
    # pure-Python non-empty sequence. While end users should consider this an
    # implementation detail, we are clearly under no such constraints. *wink*
    the_dazzling_globe = [
        b"While still the dazzling globe maintain'd eclipse,",
        "Awaiting for Hyperion's command.",
        'Fain would he have commanded, fain took throne',
        'And bid the day begin, if but for change.',
    ]

    # ..................{ PASS                               }..................
    # Assert that a callable type-checking pure-Python sequences
    # deterministically accepts a pure-Python empty sequence as expected.
    assert possessed_for_glory(
        fain_took_throne, fain_took_throne) is 0

    # ..................{ FAIL                               }..................
    # Assert that this same callable rejects any other object by raising the
    # expected type-checking violation.
    #
    # Note that strings are technically collections of strings under Python
    # semantics (don't ask) and thus a reasonable torture test here.
    with raises_uncached(BeartypeCallHintParamViolation):
        possessed_for_glory(
            "He might not:—No, though a primeval God:",
            "The sacred seasons might not be disturb'd.",
        )

    # ..................{ FAIL                               }..................
    # For a sufficiently large number of iterations, where "sufficiently large"
    # is arbitrarily chosen so as to (hopefully) expose any accidental
    # non-determinism when disabling non-deterministic type-checking...
    for _ in range(42):
        # Assert that this same callable accepts a valid pure-Python non-empty
        # sequence as expected.
        assert possessed_for_glory(
            the_gods_approach, the_gods_approach) is 6

        # Assert that this same callable rejects an invalid pure-Python
        # non-empty sequence by raising the expected type-checking violation.
        with raises_uncached(BeartypeCallHintParamViolation):
            possessed_for_glory(the_dazzling_globe, the_gods_approach)

        # Assert that this same callable rejects an invalid pure-Python
        # non-empty quasiiterable by raising the expected type-checking
        # violation.
        with raises_uncached(BeartypeCallHintParamViolation):
            possessed_for_glory(the_gods_approach, the_dazzling_globe)

# ....................{ PRIVATE ~ callables                }....................
def _earthquake(and_fiery_flood: int, and_hurricane: int) -> bool:
    '''
    Arbitrary callable to be decorated by the :func:`beartype.beartype`
    decorator.

    This callable is intentionally declared at module scope rather than within
    the unit test(s) referencing this callable above, as the fully-qualified
    name of this callable when declared at module scope is considerably more
    reliable than that of a nested closure.
    '''

    return len(and_fiery_flood) % and_hurricane == 0
