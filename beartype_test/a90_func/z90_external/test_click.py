#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide Click integration tests.

This submodule functionally tests the :mod:`beartype` package against the
third-party :mod:`click` package.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from beartype_test._util.mark.pytskip import skip_unless_package

# ....................{ TESTS                              }....................
@skip_unless_package('click')
def test_click_commands() -> None:
    '''
    Integration test validating that the :func:`beartype.beartype` decorator
    integrates cleanly with the third-party :class:`click.command` decorator
    and well-known derivatives of that decorator (e.g., the third-party
    :class:`rich_click.command` decorator).
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype import beartype
    from beartype.roar import BeartypeCallHintReturnViolation
    from beartype._util.module.utilmodimport import import_module_attr_or_none
    from click.testing import CliRunner

    # ....................{ LOCALS                         }....................
    # Tuple of the fully-qualified names of all third-package click-centric
    # packages to be dynamically imported and exercised below.
    CLICK_PACKAGE_NAMES = ('click', 'rich_click',)

    # Click test runner with which to exercise these packages.
    click_runner = CliRunner()

    # ....................{ PACKAGES                       }....................
    # For each of these third-package click-centric packages...
    for click_package_name in CLICK_PACKAGE_NAMES:
        # Third-party @command decorator dynamically imported from this package
        # if this package is importable under the active Python interpreter *OR*
        # "None" otherwise (i.e., if this package is unimportable).
        click_command = import_module_attr_or_none(
            module_name=click_package_name, attr_name='command',)

        # If this package is unimportable, continue to the next such package.
        if click_command is None:
            continue
        # Else, this this decorator is importable from this package.

        # ....................{ CALLABLES                  }....................
        @beartype
        @click_command()
        def click_good() -> int:
            '''
            Arbitrary :func:`beartype.beartype`- and
            :func:`click.command`-decorated callable returning a valid value
            satisfying its return type hint.
            '''

            # Feed that face! Feed it good.
            # print('!UGH!')
            return 0xFEEDFACE


        @beartype
        @click_command()
        def click_bad() -> int:
            '''
            Arbitrary :func:`beartype.beartype`- and
            :func:`click.command`-decorated callable returning an invalid value
            violating its return type hint.
            '''

            # Surely, this cannot be!?
            return "A sea of lustre on the horizon's verge"

        # ....................{ PASS                       }....................
        # "click.testing.Result" object produced by invoking this Click test
        # runner against this "good" Click command.
        click_good_result = click_runner.invoke(cli=click_good)
        # print(f'click result: {repr(click_result)}')
        # print(f'click result: {dir(click_result)}')
        # print(f'click result: {click_result.return_value}')
        # print(f'click result: {click_result.exit_code}')

        # Assert that this "good" Click command succeeded without error.
        assert click_good_result.exit_code == 0

        # ....................{ FAIL                       }....................
        # "click.testing.Result" object produced by invoking this Click test
        # runner against this "bad" Click command.
        click_bad_result = click_runner.invoke(cli=click_bad)
        # print(f'click result: {repr(click_result)}')
        # print(f'click result: {click_result.exc_info}')
        # print(f'click result: {dir(click_result.exc_info)}')

        # Assert that this "bad" Click command raised the expected exception.
        # Note that the "click.testing.Result.exc_info" instance variable is a
        # 3-tuple "(exception_type, exception, exception_traceback)".
        assert bool(click_bad_result.exc_info)
        assert click_bad_result.exc_info[0] is BeartypeCallHintReturnViolation
