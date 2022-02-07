#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2022 Beartype authors.
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

# ....................{ IMPORTS                           }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ CALLABLES                         }....................
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

# ....................{ TESTS                             }....................
def test_decor_conf() -> None:
    '''
    Test the :func:`beartype.beartype` decorator by the optional ``conf``
    parameter agnostic of parameters instantiating that configuration.
    '''

    # Defer heavyweight imports.
    from beartype import BeartypeConf, BeartypeStrategy, beartype
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

    # Defer heavyweight imports.
    from beartype import BeartypeConf, beartype

    # @beartype subdecorator printing wrapper function definitions.
    beartype_printing = beartype(conf=BeartypeConf(is_debug=True))

    # Wrapper function decorated by this subdecorator, immediately discarded as
    # *ONLY* the output printed by this decoration is of relevance here.
    beartype_printing(_earthquake)

    # Pytest object freezing the current state of standard output and error as
    # uniquely written to by this unit test up to this statement.
    standard_captured = capsys.readouterr()

    # Assert the prior decoration printed the expected definition.
    assert 'line' in standard_captured.out
    assert 'def _earthquake(' in standard_captured.out
    assert 'return' in standard_captured.out
    assert '# is <function _earthquake ' in standard_captured.out


def test_decor_conf_is_debug_updates_linecache(capsys) -> None:
    '''
    Test the :func:`beartype.beartype` decorator passed the optional ``conf``
    parameter passed the optional ``is_debug`` parameter results
    in an updated linecache.

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

    # Defer heavyweight imports.
    from beartype import BeartypeConf, beartype
    import linecache

    # @beartype subdecorator printing wrapper function definitions.
    beartype_printing = beartype(conf=BeartypeConf(is_debug=True))

    beartyped_earthquake = beartype_printing(_earthquake)

    # Pytest object freezing the current state of standard output and error as
    # uniquely written to by this unit test up to this statement.
    standard_captured = capsys.readouterr()
    standard_lines = standard_captured.out.splitlines(keepends=True)

    # This is probably overkill, but check to see that we generated lines in
    # our linecache that correspond to the ones we printed. This a fragile
    # coupling, but we can relax this later to avoid making those line-by-line
    # comparisons and just check for the decorated function's filename's
    # presence in the cache.
    assert beartyped_earthquake.__code__.co_filename in linecache.cache
    code_len, mtime, code_lines, code_filename = linecache.cache[beartyped_earthquake.__code__.co_filename]
    assert mtime is None
    assert len(code_lines) == len(standard_lines)
    for code_line, standard_line in zip(code_lines, standard_lines):
        assert code_line in standard_line
    assert code_filename == beartyped_earthquake.__code__.co_filename


def test_decor_conf_strategy() -> None:
    '''
    Test the :func:`beartype.beartype` decorator passed the optional ``conf``
    parameter passed the optional ``strategy`` parameter.
    '''

    # Defer heavyweight imports.
    from beartype import BeartypeConf, BeartypeStrategy, beartype

    # Assert that @beartype in configuration mode returns the identity
    # decorator unconditionally preserving all passed objects as is.
    beartype_O0 = beartype(conf=BeartypeConf(strategy=BeartypeStrategy.O0))
    assert beartype_O0(beartype) is beartype
