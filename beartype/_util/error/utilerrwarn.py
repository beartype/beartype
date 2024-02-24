#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2024 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **warning handlers** (i.e., low-level callables manipulating
non-fatal warnings -- which, technically, are also exceptions -- in a
human-readable, general-purpose manner).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.typing import Iterable
from beartype._data.error.dataerrmagic import EXCEPTION_PLACEHOLDER
from beartype._data.hint.datahinttyping import TypeWarning
from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_12
from beartype._util.text.utiltextmunge import uppercase_str_char_first
from collections.abc import Iterable as IterableABC
from warnings import (
    WarningMessage,
    warn,
    warn_explicit,
)

# ....................{ WARNERS                            }....................
#FIXME: Unit test us up, please.
#FIXME: Globally replace all direct calls to the warn() function with calls to
#this utility function instead, please.

# If the active Python interpreter targets Python >= 3.12, the standard
# warnings.warn() function supports the optional "skip_file_prefixes" parameter
# critical for emitting more useful warnings. In this case, define the
# issue_warning() warner to pass that parameter.
if IS_PYTHON_AT_LEAST_3_12:
    # ....................{ IMPORTS                        }....................
    # Defer version-specific imports.
    import beartype
    from os.path import dirname

    # ....................{ WARNERS                        }....................
    def issue_warning(cls: TypeWarning, message: str) -> None:
        # The warning you gave us is surely our last!
        warn(message, cls, skip_file_prefixes=_ISSUE_WARNING_IGNORE_DIRNAMES)  # type: ignore[call-overload]

    # ....................{ PRIVATE ~ globals              }....................
    _ISSUE_WARNING_IGNORE_DIRNAMES = (dirname(beartype.__file__),)
    '''
    Tuple of one or more **ignorable warning dirnames** (i.e., absolute
    directory names of all Python modules to be ignored by the
    :func:`.issue_warning` warner when deciding which source module to associate
    with the issued warning, enabling this warner to associate this warning with
    the original externally defined module to which this warning applies).

    This tuple includes the dirname of the top-level directory providing the
    :mod:`beartype` package, enabling this warner to ignore all stack frames
    produced by internal calls to submodules of this package. Doing so emits
    substantially more useful and readable warnings for external callers.
    '''
# Else, the active Python interpreter targets Python < 3.12. In this case,
# define the issue_warning() warner to avoid passing that parameter.
else:
    def issue_warning(cls: TypeWarning, message: str) -> None:
        # Time to cry your tears! Now cry!
        warn(message, cls)


issue_warning.__doc__ = (
    '''
    Issue (i.e., emit) a non-fatal warning of the passed type with the passed
    message.

    Caveats
    -------
    **This high-level warner should always be called in lieu of the low-level**
    :func:`warnings.warn` **warner.** Whereas the latter issues warnings that
    obfuscate the external user-defined modules to which those warnings apply,
    this warner associates this warning with the applicable user-defined module
    when the active Python interpreter targets Python >= 3.12.

    Parameters
    ----------
    cls: Type[Warning]
        Type of warning to be issued.
    message: str
        Human-readable warning message to be issued.
    '''
)


def reissue_warnings_placeholder(
    # Mandatory parameters.
    warnings: Iterable[WarningMessage],
    target_str: str,

    # Optional parameters.
    source_str: str = EXCEPTION_PLACEHOLDER,
) -> None:
    '''
    Reissue (i.e., re-emit) the passed warning in a safe manner preserving both
    this warning object *and* **associated context (e.g., filename, line
    number)** associated with this warning object, but globally replacing all
    instances of the passed source substring hard-coded into this warning's
    message with the passed target substring.

    Parameters
    ----------
    warnings : Iterable[WarningMessage]
        Iterable of zero or more warnings to be reissued, typically produced by
        an external call to the standard
        ``warnings.catch_warnings(record=True)`` context manager.
    target_str : str
        Target human-readable format substring to replace the passed source
        substring previously hard-coded into this warning's message.
    source_str : Optional[str]
        Source non-human-readable substring previously hard-coded into this
        warning's message to be replaced by the passed target substring.
        Defaults to :data:`.EXCEPTION_PLACEHOLDER`.

    Warns
    -----
    warning
        The passed warning, globally replacing all instances of this source
        substring in this warning's message with this target substring.

    See Also
    --------
    :data:`.EXCEPTION_PLACEHOLDER`
        Further commentary on usage and motivation.
    https://stackoverflow.com/a/77516994/2809027
        StackOverflow answer strongly inspiring this implementation.
    '''
    assert isinstance(warnings, IterableABC), (
        f'{repr(warnings)} not iterable.')
    assert isinstance(source_str, str), f'{repr(source_str)} not string.'
    assert isinstance(target_str, str), f'{repr(target_str)} not string.'

    # For each warning in this iterable of zero or more warnings...
    for warning in warnings:
        assert isinstance(warning, WarningMessage), (
           f'{repr(warning)} not "WarningMessage" instance.')

        # Original warning message, localized as a negligible optimization.
        warning_message_old: str = warning.message  # type: ignore[assignment]

        # Munged warning message globally replacing all instances of this source
        # substring with this target substring.
        #
        # Note that we intentionally call the lower-level str.replace() method
        # rather than the higher-level
        # beartype._util.text.utiltextmunge.replace_str_substrs() function here,
        # as the latter unnecessarily requires this warning message to contain
        # one or more instances of this source substring.
        warning_message_new = warning_message_old.replace(
            source_str, target_str)

        # If doing so actually changed this message...
        if warning_message_new != warning_message_old:
            # Uppercase the first character of this message if needed.
            warning_message_new = uppercase_str_char_first(warning_message_new)
        # Else, this message remains preserved as is.

        # Reissue this warning with a possibly modified message.
        warn_explicit(
            message=warning_message_new,
            category=warning.category,
            filename=warning.filename,
            lineno=warning.lineno,
            source=warning.source,
        )
