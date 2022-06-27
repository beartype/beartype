#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2022 Beartype authors.
# See "LICENSE" for further details.

'''
**Project-wide functional static type-checker tests.**

This submodule functionally tests the this project's compliance with
third-party static type-checkers and hence :pep:`561`.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from beartype_test.util.mark.pytskip import (
    skip_if_pypy,
    skip_unless_package,
)

# ....................{ TESTS                              }....................
#FIXME: Consider submitting as a StackOverflow post. Dis iz l33t, yo!

# If the third-party "mypy" package is unavailable, skip this test. Note that:
# * "mypy" is the reference standard for static type-checking in Python.
# * Unbelievably, "mypy" violates PEP 8 versioning standards by failing to
#   define the "mypy.__init__.__version__" attribute, which means that passing
#   the optional "minimum_version" parameter to the skip_unless_package()
#   decorator fails on failing to find that attribute. While we *COULD* instead
#   explicitly test the "mypy.version.__version__" attribute, doing so would
#   require defining a new and *MUCH* less trivial
#   @skip_unless_module_attribute decorator. For sanity, we instead currently
#   accept the importability of the "mypy" package as sufficient, which it
#   absolutely isn't, but what you gonna do, right?
#
# Skip this "mypy"-specific functional test unless all of the following apply:
# * The "mypy" package is unimportable under the active Python interpreter.
# * The active Python interpreter is *NOT* PyPy. mypy is currently incompatible
#   with PyPy for inscrutable reasons that should presumably be fixed at some
#   future point. See also:
#     https://mypy.readthedocs.io/en/stable/faq.html#does-it-run-on-pypy
@skip_unless_package('mypy')
@skip_if_pypy()
def test_pep561_mypy() -> None:
    '''
    Functional test testing this project's compliance with :pep:`561` by
    externally running :mod:`mypy` (i.e., the most popular third-party static
    type checker as of this test) against this project's top-level package.
    '''

    # Defer heavyweight imports.
    from beartype_test.util.path.pytpathmain import (
        get_main_mypy_config_file,
        get_main_package_dir,
    )
    from mypy import api

    # List of all command-line options (i.e., "-"-prefixed strings) to be
    # effectively passed to the external "mypy" command.
    #
    # Note this iterable *MUST* be defined as a list rather than tuple. If a
    # tuple, the function called below raises an exception. Hot garbage!
    MYPY_OPTIONS = [
        # Absolute dirname of this project's top-level mypy configuration.
        # Since our "tox" configuration isolates testing to a temporary
        # directory, mypy is unable to find its configuration without help.
        '--config-file', str(get_main_mypy_config_file()),
    ]

    # List of all command-line arguments (i.e., non-options) to be effectively
    # passed to the external "mypy" command.
    #
    # Note this iterable *MUST* be defined as a list rather than tuple. If a
    # tuple, the function called below raises an exception. Steaming trash!
    MYPY_ARGUMENTS = [
        # Absolute dirname of this project's top-level package.
        str(get_main_package_dir()),
    ]

    # Tuple of all command-line options to be effectively passed to the
    # external "mypy" command.
    #
    # Note that we intentionally do *NOT* assert that call to have exited with
    # a successful exit code. Although mypy does exit with success on local
    # developer machines, it inexplicably does *NOT* under remote GitHub
    # Actions-based continuous integration despite "mypy_stderr" being empty.
    # Ergo, we conveniently ignore the former in favour of the latter.
    mypy_stdout, mypy_stderr, _ = api.run(MYPY_OPTIONS + MYPY_ARGUMENTS)
    # mypy_stdout, mypy_stderr, mypy_exit = api.run(MYPY_OPTIONS + MYPY_ARGUMENTS)

    # Assert "mypy" to have emitted *NO* warnings or errors to "stderr".
    #
    # Note that "mypy" predominantly emits both warnings and errors to "stdout"
    # rather than "stderr", despite this contravening sane POSIX semantics.
    # They did this because some guy complained about not being able to
    # trivially grep "mypy" output, regardless of the fact that redirecting
    # stderr to stdout is a trivial shell fragment (e.g., "2>&1"), but let's
    # break everything just because some guy can't shell. See also:
    #     https://github.com/python/mypy/issues/1051
    assert not mypy_stderr

    # Assert "mypy" to have emitted *NO* warnings or errors to "stdout".
    # Unfortunately, doing so is complicated by the failure of "mypy" to
    # conform to sane POSIX semantics. Specifically:
    # * If "mypy" succeeds, "mypy" emits to "stdout" a single line resembling:
    #       Success: no issues found in 83 source files
    # * If "mypy" fails, "mypy" emits to "stdout" *ANY* other line(s).
    #
    # Ergo, asserting this string to start with "Success:" suffices. Note this
    # assertion depends on "mypy" internals and is thus fragile, but that we
    # have *NO* sane alternative.
    assert mypy_stdout.startswith('Success: ')


#FIXME: *OH, BOY.* We thought "pyright" itself officially published the
#"pyright" Python package shim. Nope. It's some unrelated other dude:
#    https://github.com/RobertCraigie/pyright-python
#
#Even that would be fine, except that the "pyright" Python package shim does
#fundamentally unsafe things we absolutely do *NOT* want like online "npm"-based
#auto-installation of the "pyright" JavaScript package if currently not
#installed. Needless to say, this is ludicrous. We're *NOT* going there.
#Instead, we'll need to refactor this test to:
#* Be skipped if the "pyright" command is *NOT* in the current ${PATH}.
#* Internally call that command (e.g., by invoking subprocess.run()).
#
#I'm definitely displeased with the lack of native Python support here, people.

# # If the third-party "pyright" package is unavailable, skip this test. Note
# # that:
# # * "pyright" is the most popular static type-checker for Python, mostly due to
# #   "pylance" (i.e., the most popular Python language plugin for VSCode, itself
# #   the most popular integrated development environment (IDE)) both bundling
# #   *AND* enabling "pyright" by default.
# # * "pyright" is implemented in pure-TypeScript (i.e., JavaScript augmented with
# #   type hints transpiling down to pure-JavaScript at compilation time).
# # * This package is merely a thin shim around the pure-TypeScript core of
# #   "pyright" simplifying the external invocation of "pyright" from Python.
# @skip_unless_package('pyright')
# def test_pep561_pyright() -> None:
#     '''
#     Functional test testing this project's compliance with :pep:`561` by
#     externally running :mod:`pyright` (i.e., the most popular third-party static
#     type checker as of this test) against this project's top-level package.
#
#     See Also
#     ----------
#     :mod:`pytest_pyright`
#         Third-party :mod:`pytest` plugin automating this integration. Since this
#         integration is trivial *and* since :mod:`beartype` assiduously avoids
#         *all* mandatory dependencies, we perform this integration manually.
#         Moreover, this plugin:
#
#         * Internally violates privacy encapsulation in
#           :mod:`pytest` by widely importing private :mod:`pytest` attributes.
#         * Explicitly admonishes downstream dependencies *not* to depend upon
#           this plugin:
#
#             This project was created for internal use within another project of
#             mine, support will be minimal.
#     '''
#
#     # Defer heavyweight imports.
#     from beartype_test.util.path.pytpathmain import (
#         get_main_package_dir,
#     )
#     from pyright import api
#
#     #FIXME: Note that we *COULD* additionally pass the "--verifytypes" option,
#     #which exposes further "pyright" compliants. Let's avoid doing so until
#     #someone explicitly requests we do so, please. This has dragged on enough!
#     # List of all command-line options (i.e., "-"-prefixed strings) to be
#     # effectively passed to the external "pyright" command.
#     #
#     # Note this iterable *MUST* be defined as a list rather than tuple. If a
#     # tuple, the function called below raises an exception. Hot garbage!
#     PYRIGHT_OPTIONS = []
#
#     # List of all command-line arguments (i.e., non-options) to be effectively
#     # passed to the external "pyright" command.
#     #
#     # Note this iterable *MUST* be defined as a list rather than tuple. If a
#     # tuple, the function called below raises an exception. Steaming trash!
#     PYRIGHT_ARGUMENTS = [
#         # Absolute dirname of this project's top-level package.
#         str(get_main_package_dir()),
#     ]
#
#     # Tuple of all command-line options to be effectively passed to the
#     # external "pyright" command.
#     #
#     # Note that we intentionally do *NOT* assert that call to have exited with
#     # a successful exit code. Although pyright does exit with success on local
#     # developer machines, it inexplicably does *NOT* under remote GitHub
#     # Actions-based continuous integration despite "pyright_stderr" being empty.
#     # Ergo, we conveniently ignore the former in favour of the latter.
#     pyright_stdout, pyright_stderr, _ = api.run(PYRIGHT_OPTIONS + PYRIGHT_ARGUMENTS)
#     # pyright_stdout, pyright_stderr, pyright_exit = api.run(PYRIGHT_OPTIONS + PYRIGHT_ARGUMENTS)
#
#     # Assert "pyright" to have emitted *NO* warnings or errors to "stderr".
#     #
#     # Note that "pyright" predominantly emits both warnings and errors to "stdout"
#     # rather than "stderr", despite this contravening sane POSIX semantics.
#     # They did this because some guy complained about not being able to
#     # trivially grep "pyright" output, regardless of the fact that redirecting
#     # stderr to stdout is a trivial shell fragment (e.g., "2>&1"), but let's
#     # break everything just because some guy can't shell. See also:
#     #     https://github.com/python/pyright/issues/1051
#     assert not pyright_stderr
#
#     # Assert "pyright" to have emitted *NO* warnings or errors to "stdout".
#     # Unfortunately, doing so is complicated by the failure of "pyright" to
#     # conform to sane POSIX semantics. Specifically:
#     # * If "pyright" succeeds, "pyright" emits to "stdout" a single line resembling:
#     #       Success: no issues found in 83 source files
#     # * If "pyright" fails, "pyright" emits to "stdout" *ANY* other line(s).
#     #
#     # Ergo, asserting this string to start with "Success:" suffices. Note this
#     # assertion depends on "pyright" internals and is thus fragile, but that we
#     # have *NO* sane alternative.
#     assert pyright_stdout.startswith('Success: ')
