#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
**Project ``README.rst`` functional tests.**

This submodule functionally tests the syntactic validity of this project's
top-level ``README.rst`` file.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from beartype_test._util.mark.pytskip import skip_unless_package

# ....................{ TESTS                              }....................
#FIXME: Consider submitting as a StackOverflow post. Dis iz l33t, yo!

# If the third-party "docutils" package satisfying this minimum version is
# unavailable, skip this test. Note that:
#
# * "docutils" is the reference standard for parsing reStructuredText (reST).
#   Unsurprisingly, even Sphinx parses reST with "docutils".
# * This test makes assumptions about the "docutils" public API satisfied
#   *ONLY* by this minimum version.
@skip_unless_package(package_name='docutils', minimum_version='0.15')
def test_doc_readme(monkeypatch) -> None:
    '''
    Functional test testing the syntactic validity of this project's top-level
    ``README.rst`` file by monkeypatching the public :mod:`docutils` singleton
    responsible for emitting warnings and errors to instead convert these
    warnings and errors into a test failure.

    Parameters
    ----------
    monkeypatch : MonkeyPatch
        Builtin fixture object permitting object attributes to be safely
        modified for the duration of this test.
    '''

    # Defer test-specific imports.
    from docutils.core import publish_parts
    from docutils.utils import Reporter
    from beartype_test._util.path.pytpathmain import get_main_readme_file

    # Decoded plaintext contents of this project's readme file as a string.
    #
    # Note this encoding *MUST* explicitly be passed here. Although macOS and
    # Linux both default to this encoding, Windows defaults to the single-byte
    # encoding "cp1252" for backward compatibility. Failing to pass this
    # encoding here results in a non-human-readable test failure under Windows:
    #     UnicodeDecodeError: 'charmap' codec can't decode byte 0x9d in
    #     position 1495: character maps to <undefined>
    README_CONTENTS = get_main_readme_file().read_text(encoding='utf-8')

    # List of all warning and error messages emitted by "docutils" during
    # parsing of this project's top-level "README.rst" file.
    system_messages = []

    # Original non-monkey-patched method of the public :mod:`docutils`
    # singleton emitting warnings and errors *BEFORE* patching this method.
    system_message_unpatched = Reporter.system_message

    def system_message_patched(reporter, level, message, *args, **kwargs):
        '''
        Method of the public :mod:`docutils` singleton emitting warnings and
        errors redefined as a closure collecting these warnings and errors into
        the local list defined above.
        '''

        # Call this non-monkey-patched method with all passed parameters as is.
        message_result = system_message_unpatched(
            reporter, level, message, *args, **kwargs)

        # If this message is either a warning *OR* error, append this message
        # to the above list.
        if level >= reporter.WARNING_LEVEL:
            system_messages.append(message)
        # Else, this message is neither a warning *NOR* error. In this case,
        # silently ignore this message.

        # Return value returned by the above call as is.
        return message_result

    # Temporarily install this monkey-patch for the duration of this test.
    monkeypatch.setattr(
        Reporter,
        name='system_message',
        value=system_message_patched,
    )

    # Attempt to render this "README.rst" file as reST, implicitly invoking this
    # monkey-patch.
    publish_parts(source=README_CONTENTS, writer_name='html4css1')

    # Assert "docutils" to have emitted *NO* warnings or errors.
    assert not system_messages
