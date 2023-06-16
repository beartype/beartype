#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype decorator configuration unit tests.**

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

    # Defer test-specific imports.
    from beartype import (
        BeartypeConf,
        BeartypeStrategy,
        beartype,
    )
    from beartype.roar import BeartypeConfException
    from pytest import raises

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

    # Assert that @beartype raises the expected exception when passed a "conf"
    # parameter that is *NOT* a configuration.
    with raises(BeartypeConfException):
        beartype(conf='Within the daedal earth; lightning, and rain,')


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
    from beartype import BeartypeConf, beartype
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

    # Absolute filename of the fake file declaring the earthquake_beartyped()
    # function.
    earthquake_beartyped_filename = earthquake_beartyped.__code__.co_filename

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
    from beartype.roar import BeartypeCallHintViolation
    from pytest import raises

    # ..................{ LOCALS                             }..................
    # @beartype decorator disabling type-checking.
    nobeartype = beartype(conf=BeartypeConf(strategy=BeartypeStrategy.O0))

    # ..................{ PASS ~ function                    }..................
    def in_the_lone_glare_of_day() -> str:
        '''
        Arbitrary **unignorable invalid callable** (i.e., callable defining at
        least one PEP-compliant type hint and thus *not* ignorable by the
        :func:`beartype.beartype` decorator, which violates that type hint).
        '''

        return b'In the lone glare of day, the snows descend'

    # Assert that this decorator is the identity decorator unconditionally
    # preserving all passed objects as is.
    in_the_lone_glare_of_day_unchecked = nobeartype(in_the_lone_glare_of_day)
    assert in_the_lone_glare_of_day_unchecked is in_the_lone_glare_of_day

    # Assert that calling this decorated callable raises *NO* type-checking
    # violations despite this underlying callable violating type-checking.
    assert isinstance(in_the_lone_glare_of_day_unchecked(), bytes)

    # ..................{ PASS ~ class                       }..................
    @beartype
    class UponThatMountain(object):
        '''
        Arbitrary class decorated by the :func:`beartype.beartype` decorator.
        '''

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

    # Instance of this class.
    upon_that_mountain = UponThatMountain()

    # Assert that calling an invalid method explicitly *NOT* type-checked by
    # @beartype raises *NO* exception.
    assert isinstance(upon_that_mountain.nor_when_the_flakes_burn(), str)

    # Assert that calling an invalid method implicitly type-checked by @beartype
    # raises the expected exception.
    with raises(BeartypeCallHintViolation):
        upon_that_mountain.none_beholds_them_there()

# ....................{ PRIVATE ~ callables                }....................
def _earthquake(and_fiery_flood: int, and_hurricane: int) -> bool:
    '''
    Arbitrary callable to be decorated by the :func:`beartype.beartype`
    decorator.

    This callable is intentionally declared at module scope rather than within
    the unit test(s) referencing this callable below, as the fully-qualified
    name of this callable when declared at module scope is considerably more
    reliable than that of a nested closure.
    '''

    return len(and_fiery_flood) % and_hurricane == 0

