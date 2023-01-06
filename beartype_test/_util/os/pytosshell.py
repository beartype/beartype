#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
**Testable path factories** (i.e., callables creating and returning
:class:`pathlib.Path` instances encapsulating testing-specific paths).
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ RELATIVIZERS                       }....................
def shell_quote(text: str) -> str:
    '''
    Shell-quote the passed string in a platform-specific manner.

    If the current platform is:

    * *Not* vanilla Windows (e.g., Linux, macOS), the returned string is
      guaranteed to be suitable for passing as an arbitrary positional argument
      to external commands.
    * Windows, the returned string is suitable for passing *only* to external
      commands parsing arguments in the same manner as the Microsoft C runtime.
      While *all* applications on POSIX-compliant systems are required to parse
      arguments in the same manner (i.e., according to Bourne shell lexing), no
      such standard applies to Windows applications. Shell quoting is therefore
      fragile under Windows -- like pretty much everything.

    Parameters
    ----------
    text : str
        String to be shell-quoted.

    Returns
    ----------
    str
        This string shell-quoted.
    '''
    assert isinstance(text, str), f'{repr(text)} not string.'

    # Defer heavyweight imports.
    from beartype._util.os.utilostest import is_os_windows_vanilla

    # If the current platform is vanilla Windows (i.e., neither Cygwin *NOR* the
    # Windows Subsystem for Linux (WSL)), do *NOT* perform POSIX-compatible
    # quoting. Vanilla Windows is POSIX-incompatible and hence does *NOT* parse
    # command-line arguments according to POSIX standards. In particular,
    # Windows does *NOT* treat single-quoted arguments as single arguments but
    # rather as multiple shell words delimited by the raw literal `'`. This is
    # circumventable by calling an officially undocumented Windows-specific
    # function. (Awesome.)
    if is_os_windows_vanilla():
        import subprocess
        return subprocess.list2cmdline([text])
    # Else, perform POSIX-compatible quoting.
    else:
        import shlex
        return shlex.quote(text)
