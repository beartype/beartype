#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **command runners** (i.e., callables running external commands as
subprocesses of the active Python process).

This private submodule is *not* intended for importation by downstream callers.

Command Words Arguments
----------
Most runners accept a mandatory ``command_words`` parameter, a list of one or
more shell words comprising this command whose:

* Mandatory first item is either:

  * This command's absolute or relative path.
  * This command's basename, in which case the first command with that basename
    in the current ``${PATH}`` environment variable will be run. If no such
    command is found, an exception is raised.

* Optional subsequent items are this command's arguments (in order). Note that
  these arguments are passed as is to a low-level system call rather than
  intprereted by a high-level shell (e.g., ``/bin/sh`` on POSIX-compatible
  platforms) and hence should *not* be shell-quoted. Indeed, shell quoting
  these arguments is likely to result in erroneous command behaviour. The
  principal exception to this heuristic are **GNU-style long value options**
  (i.e., ``--``-prefixed options accepting a ``=``-delimited value), whose
  values should either be:

  * Passed as a separate argument *without* being shell-quoted.
  * Concatenated to the current ``--``-prefixed argument delimited by ``=`` and
    shell-quoted.

``Popen()`` Keyword Arguments
----------
Most runners accept the same optional keyword arguments accepted by the
:meth:`subprocess.Popen.__init__` constructor, including:

* ``cwd``, the absolute path of the current working directory (CWD) from which
  this command is to be run. Defaults to the current CWD. **Unfortunately, note
  that this keyword argument appears to be erroneously ignored on numerous
  platforms** (e.g., Windows). For safety, a context manager temporarily
  changing the current directory should typically be leveraged instead.
* ``timeout``, the maximum number of milliseconds this command is to be run
  for. Commands with execution time exceeding this timeout will be mercifully
  killed. Defaults to :data:`None`, in which case this command is run
  indefinitely.
'''

# ....................{ IMPORTS                            }....................
from beartype.typing import (
    Iterable,
    Mapping,
    Optional,
    Tuple,
)
from beartype._data.hint.datahinttyping import CommandWords
from collections.abc import (
    Iterable as IterableABC,
    Mapping as MappingABC,
)
from os import environ
from subprocess import (
    CalledProcessError,
    TimeoutExpired,
    call as subprocess_call,
    check_output as subprocess_check_output,
    run as subprocess_run,
)

# ....................{ GLOBALS                            }....................
BUFFER_SIZE_DEFAULT = -1
'''
Default subprocess buffer size for the current platform (synonymous with the
current :data:`io.DEFAULT_BUFFER_SIZE`) suitable for passing as the ``bufsize``
parameter accepted by :meth:`subprocess.Popen.__init__` method.
'''


BUFFER_SIZE_NONE = 0
'''
Unbuffered subprocess buffer size suitable for passing as the ``bufsize``
parameter accepted by :meth:`subprocess.Popen.__init__` method.

Both reading from and writing to an unbuffered subprocess is guaranteed to
perform exactly one system call (``read()`` and ``write()``, respectively) and
can return short (i.e., produce less bytes than the requested number of bytes).
'''


BUFFER_SIZE_LINE = 1
'''
Line-buffered subprocess buffer size suitable for passing as the ``bufsize``
parameter accepted by :meth:`subprocess.Popen.__init__` method.

Reading from a line-buffered subprocess is guaranteed to block until the
subprocess emits a newline, at which point all output emitted between that
newline inclusive and the prior newline exclusive is consumed.
'''

# ....................{ PRIVATE ~ hints                    }....................
_HINT_POPEN_KWARGS = Mapping[str, object]
'''
PEP-compliant type hint matching the return value of the private
:func:`_init_popen_kwargs` function.
'''


_HINT_POPEN_KWARGS_OPTIONAL = Optional[_HINT_POPEN_KWARGS]
'''
PEP-compliant type hint matching the ``popen_kwargs`` parameter passed to most
callables declared by this submodule.
'''

# ....................{ RUNNERS ~ command                  }....................
#FIXME: Unit test us up, please.
def run_command_forward_stderr_return_stdout(
    # Mandatory parameters.
    command_words: CommandWords,

    # Optional parameters.
    popen_kwargs: _HINT_POPEN_KWARGS_OPTIONAL = None,
) -> str:
    '''
    Run the passed command as a subprocess of the active Python process, raising
    an exception on subprocess failure while both forwarding all standard error
    of this subprocess to the standard error file handle of the active Python
    process *and* capturing and returning all standard output of this
    subprocess.

    This exception contains the exit status of this subprocess.

    Parameters
    ----------
    command_words : CommandWords
        Iterable of one or more shell words comprising this command.
    popen_kwargs : _HINT_POPEN_KWARGS_OPTIONAL
        Dictionary of all keyword arguments to be passed to the
        :meth:`subprocess.Popen.__init__` method. Defaults to :data:`None`, in
        which case the empty dictionary is assumed.

    Returns
    ----------
    str
        All standard output captured from this subprocess, stripped of all
        trailing newlines (as under most POSIX shells) *and* decoded with the
        current locale's preferred encoding (e.g., UTF-8).

    Raises
    ----------
    CalledProcessError
        If the subprocess running this command report non-zero exit status.
    '''

    # Sanitize these arguments.
    popen_kwargs = _init_popen_kwargs(command_words, popen_kwargs)

    # Capture this command's stdout, raising an exception on command failure
    # (including failure due to an expired timeout).
    command_stdout = subprocess_check_output(command_words, **popen_kwargs)

    # Return this stdout, stripped of all trailing newlines.
    return command_stdout.rstrip('\n')


#FIXME: Unit test us up, please.
def run_command_forward_output(
    # Mandatory parameters.
    command_words: CommandWords,

    # Optional parameters.
    popen_kwargs: _HINT_POPEN_KWARGS_OPTIONAL = None,
) -> None:
    '''
    Run the passed command as a subprocess of the active Python process,
    raising an exception on subprocess failure while forwarding all standard
    output and error output by this subprocess to the standard output and error
    file handles of the active Python process.

    This exception contains the exit status of this subprocess.

    Parameters
    ----------
    command_words : CommandWords
        Iterable of one or more shell words comprising this command.
    popen_kwargs : _HINT_POPEN_KWARGS_OPTIONAL
        Dictionary of all keyword arguments to be passed to the
        :meth:`subprocess.Popen.__init__` method. Defaults to :data:`None`, in
        which case the empty dictionary is assumed.

    Raises
    ----------
    CalledProcessError
        If the subprocess running this command report non-zero exit status.
    '''

    # Defer test-specific imports.
    from beartype_test._util.command.pytcmdexit import is_failure

    # 0-based exit status reported by running this command.
    exit_status = run_command_forward_output_return_status(
        command_words=command_words, popen_kwargs=popen_kwargs)

    # If this command failed, raising an exception on command failure. For
    # reusability, we reimplement the subprocess.check_call() function here
    # rather than explicitly call that function. The latter approach would
    # require duplicating logic between this and the
    # run_command_forward_output_return_status() runner called above.
    if is_failure(exit_status):
        raise CalledProcessError(exit_status, command_words)


#FIXME: Unit test us up, please.
def run_command_forward_output_return_status(
    # Mandatory parameters.
    command_words: CommandWords,

    # Optional parameters.
    popen_kwargs: _HINT_POPEN_KWARGS_OPTIONAL = None
) -> int:
    '''
    Run the passed command as a subprocess of the active Python process,
    returning only the exit status of this subprocess while forwarding all
    standard output and error output by this subprocess to the standard output
    and error file handles of the active Python process.

    Caveats
    ----------
    **This function raises no exceptions on subprocess failure.** To do so,
    consider calling the :func:`run_command_forward_output` function instead.

    Parameters
    ----------
    command_words : CommandWords
        Iterable of one or more shell words comprising this command.
    popen_kwargs : _HINT_POPEN_KWARGS_OPTIONAL
        Dictionary of all keyword arguments to be passed to the
        :meth:`subprocess.Popen.__init__` method. Defaults to :data:`None`, in
        which case the empty dictionary is assumed.

    Returns
    ----------
    int
        Exit status returned by this subprocess.
    '''

    # Defer test-specific imports.
    from beartype_test._util.command.pytcmdexit import FAILURE_DEFAULT

    # Sanitize these arguments.
    popen_kwargs = _init_popen_kwargs(command_words, popen_kwargs)

    # Run this command *WITHOUT* raising an exception on command failure.
    try:
        exit_status = subprocess_call(command_words, **popen_kwargs)
    # If this command failed to halt before triggering a timeout, the "timeout"
    # keyword argument was passed *AND* this command has effectively failed.
    # Since the prior call has already guaranteeably terminated this command,
    # this exception is safely convertible into default failure exit status.
    except TimeoutExpired:
        exit_status = FAILURE_DEFAULT

    # Return this exit status.
    return exit_status


def run_command_return_stdout_stderr(
    # Mandatory parameters.
    command_words: CommandWords,

    # Optional parameters.
    popen_kwargs: _HINT_POPEN_KWARGS_OPTIONAL = None,
) -> Tuple[str, str]:
    '''
    Run the passed command as a subprocess of the active Python process, raising
    an exception on subprocess failure while capturing and returning both all
    standard output and error of this subprocess.

    This exception contains the exit status of this subprocess.

    Parameters
    ----------
    command_words : CommandWords
        Iterable of one or more shell words comprising this command.
    popen_kwargs : _HINT_POPEN_KWARGS_OPTIONAL
        Dictionary of all keyword arguments to be passed to the
        :meth:`subprocess.Popen.__init__` method. Defaults to :data:`None`, in
        which case the empty dictionary is assumed.

    Returns
    ----------
    Tuple[str, str]
        All standard output and error (in that order) captured from this
        subprocess, stripped of all trailing newlines (as under most POSIX
        shells) *and* decoded with the current locale's preferred encoding
        (e.g., UTF-8).

    Raises
    ----------
    CalledProcessError
        If the subprocess running this command reports non-zero exit status.
    '''

    # If these keyword arguments are empty, default to the empty dictionary
    # *BEFORE* setting dictionary keys below.
    if popen_kwargs is None:
        popen_kwargs = {}
    # Else, these keyword arguments are non-empty.

    # In either case, these keyword arguments are now a dictionary. Assert this.
    assert isinstance(popen_kwargs, MappingABC), (
        f'{repr(popen_kwargs)} not mapping.')

    # Enable capturing of both standard output and error.
    popen_kwargs['capture_output'] = True

    # Enable raising of a "CalledProcessError" exception when this command
    # reports non-zero exit status.
    popen_kwargs['check'] = True

    # Sanitize these arguments.
    popen_kwargs = _init_popen_kwargs(command_words, popen_kwargs)

    # "subprocess.CompletedProcess" object encapsulating the result of running
    # this command.
    command_result = subprocess_run(command_words, **popen_kwargs)

    # Standard output and error emitted by this command, stripped of all
    # trailing newlines.
    command_stdout = command_result.stdout.rstrip('\n')
    command_stderr = command_result.stderr.rstrip('\n')

    # Return this standard output and error.
    return command_stdout, command_stderr

# ....................{ PRIVATE ~ constants                }....................
_INIT_POPEN_KWARGS_POPEN_KWARGS_NAMES_CLOSE_FDS_CONFLICTING = frozenset((
    'stdin', 'stdout', 'stderr', 'close_fds'))
'''
Frozen set of the names of all keyword parameters which if passed would prevent
the :func:`_init_popen_kwargs` function from safely defaulting the ``close_fds``
parameter to false under **vanilla Microsoft Windows** (i.e., *not* running the
Cygwin POSIX compatibility layer).

See Also
----------
:func:`_init_popen_kwargs`
    Further details.
'''

# ....................{ PRIVATE ~ initializers             }....................
def _init_popen_kwargs(
    # Mandatory parameters.
    command_words: CommandWords,

    # Optional parameters.
    popen_kwargs: _HINT_POPEN_KWARGS_OPTIONAL = None
) -> _HINT_POPEN_KWARGS:
    '''
    Sanitized dictionary of all keyword arguments to pass to the
    :class:`subprocess.Popen` callable when running the command specified by
    the passed shell words with the passed user-defined keyword arguments.

    Caveats
    ----------
    If the current platform is vanilla Windows *and* none of the ``stdin``,
    ``stdout``, ``stderr``, or ``close_fds`` parameters are passed, this
    function defaults the ``close_fds`` parameter if unpassed to :data:`False`.
    Doing so causes this command to inherit all file handles (including stdin,
    stdout, and stderr) from the active Python process. Note that the
    :class:`subprocess.Popen` docstring insists that:

        On Windows, if ``close_fds`` is :data:`True` then no handles will be
        inherited by the child process.

    The child process will then open new file handles for stdin, stdout, and
    stderr. If the current terminal is a Windows Console, the underlying
    terminal devices and hence file handles will remain the same, in which case
    this is *not* an issue. If the current terminal is Cygwin-based (e.g.,
    MinTTY), however, the underlying terminal devices and hence file handles
    will differ, in which case this behaviour prevents interaction between the
    current shell and the vanilla Windows command to be run below. In
    particular, all output from this command will be squelched.

    If at least one of stdin, stdout, or stderr are redirected to a blocking
    pipe, setting ``close_fds`` to :data:`False` can induce deadlocks under
    certain edge-case scenarios. Since all such file handles default to
    :data:`None` and hence are *not* redirected in this case, ``close_fds`` may
    be safely set to :data:`False`.

    On all other platforms, if ``close_fds`` is :data:`True`, no file handles
    *except* stdin, stdout, and stderr will be inherited by the child process.
    This function fundamentally differs in subtle (and only slightly documented
    ways) between vanilla Windows and all other platforms. These discrepancies
    appear to be harmful but probably unavoidable, given the philosophical gulf
    between vanilla Windows and all other platforms.

    Parameters
    ----------
    command_words : CommandWords
        Iterable of one or more shell words comprising this command.
    popen_kwargs : _HINT_POPEN_KWARGS_OPTIONAL
        Dictionary of all keyword arguments to be passed to the
        :meth:`subprocess.Popen.__init__` method. Defaults to :data:`None`, in
        which case the empty dictionary is assumed.

    Returns
    ----------
    _HINT_POPEN_KWARGS
        This dictionary of keyword arguments sanitized.
    '''

    # Defer test-specific imports.
    from beartype._util.kind.utilkinddict import is_mapping_keys_any
    from beartype._util.os.utilostest import is_os_windows_vanilla

    # If these keyword arguments are empty, default to the empty dictionary
    # *BEFORE* validating these arguments as a dictionary below.
    if popen_kwargs is None:
        popen_kwargs = {}
    # Else, these keyword arguments are non-empty.
    #
    # In either case, these keyword arguments are now a dictionary.

    # Validate these parameters *AFTER* defaulting them above if needed.
    assert isinstance(command_words, IterableABC), (
        f'{repr(command_words)} not iterable.')
    assert bool(command_words), '"command_words" empty.'
    assert isinstance(popen_kwargs, MappingABC), (
        f'{repr(popen_kwargs)} not mapping.')

    #FIXME: Uncomment if we ever feel like implementing this additional
    #validation. For the moment, we simply let lower-level functionality in the
    #stdlib do the dirty work for us. :p
    # If the first shell word is this list is unrunnable, raise an exception.
    # die_unless_command(command_words[0])

    # Log the command to be run before doing so.
    # log_debug('Running command: %s', ' '.join(command_words))

    # If this is vanilla Windows *AND* the caller passed no keyword arguments
    # that would prevent us from safely defaulting the "close_fds" parameter to
    # false, sanitize that parameter to false.
    if is_os_windows_vanilla() and not is_mapping_keys_any(
        mapping=popen_kwargs,
        keys=_INIT_POPEN_KWARGS_POPEN_KWARGS_NAMES_CLOSE_FDS_CONFLICTING,
    ):
        popen_kwargs['close_fds'] = False

    # Isolate the current set of environment variables to this command,
    # preventing concurrent changes in these variables in the active process
    # from affecting this command's subprocess.
    popen_kwargs['env'] = environ.copy()

    # Decode command output with the current locale's preferred encoding.
    popen_kwargs['universal_newlines'] = True

    # Return these keyword arguments.
    return popen_kwargs
