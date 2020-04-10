#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2020 Cecil Curry.
# See "LICENSE" for further details.

'''
**Root test configuration** (i.e., early-time configuration guaranteed to be
run by :mod:`pytest` *before* passed command-line arguments are parsed) for
this test suite.

Caveats
----------
For safety, this configuration should contain *only* early-time hooks
absolutely required by :mod:`pytest` design to be defined in this
configuration. Hooks for which this is the case (e.g.,
:func:`pytest_addoption`) are explicitly annotated as such in official
:mod:`pytest` documentation with a note resembling:

    Note

    This function should be implemented only in plugins or ``conftest.py``
    files situated at the tests root directory due to how pytest discovers
    plugins during startup.

This file is the aforementioned ``conftest.py`` file "...situated at the tests
root directory."
'''

# ....................{ IMPORTS                           }....................
import os, sys

# ....................{ HOOKS ~ session : start           }....................
def pytest_sessionstart(session: '_pytest.main.Session') -> None:
    '''
    Hook run immediately *before* starting the current test session (i.e.,
    calling the :func:`pytest.session.main` function).

    Parameters
    ----------
    session: _pytest.main.Session
        :mod:`pytest`-specific test session object.
    '''

    # Sanitize import directories *BEFORE* the first module importation.
    _clean_imports()


#FIXME: Sufficiently general-purpose and widely useful that we should consider
#shifting this into a newly discrete "pytest" plugin -- named, say:
#* "pytest-pretox". Equally clever and meaningful and hence probably the best
#   name suggested here.
#* "pytest-retox". (Clever, and mildly meaningfull.)
#* "pytest-detox". (Clever, but sadly meaningless.)
#Once created, we can then require this plugin in both this *AND* the BETSEE
#codebases. At present, we have no alternative means of sharing this code
#between both codebases. DRY, yo!
def _clean_imports() -> None:
    '''
    Sanitize and validate import directories (i.e., the global :attr:`sys.list`
    of the absolute and relative dirnames of all directories to search for
    modules and packages to be imported from).

    Specifically, this function:

    * If this low-level :mod:`pytest` test harness is *not* isolated to a venv
      (e.g., due to being exercised by the low-level ``pytest`` command),
      reduce to a noop.
    * Else, this harness is isolated to a venv (e.g., due to being exercised by
      the high-level ``tox`` command):

      #. If the top-level directory for this project is listed in the global
         list of all import directories (i.e., :attr:`sys.path`), remove this
         directory from this list. Doing so prevents this test session from
         accidentally importing from modules *not* isolated to this venv,
         including this project being tested.
      #. If the first directory on this list is *not* isolated to this venv,
         raise an exception. This condition implies that modules will be
         imported from outside this venv, which entirely defeats the purpose of
         isolating tests with :mod:`tox` to a venv in the first place.
      #. If the top-level package is *not* isolated to this venv, raise an
         exception. This condition implies that this project has been imported
         from outside this venv -- again defeating the purpose.

    Raises
    ----------
    ValueError
        If either the first directory on :attr:`sys.path` or the top-level
        package are *not* isolated to this venv.
    '''

    # Print a header for disambiguity.
    print('----------[ venv ]----------')

    # Print the absolute dirname of the system-wide Python prefix and current
    # Python prefix, which differs from the former under venvs.
    print('python prefix (system [base]): ' + sys.base_prefix)
    print('python prefix (system [real]): ' + getattr(sys, 'real_prefix', ''))
    print('python prefix (current): ' + sys.prefix)

    # True only if tests are isolated to a venv produced by either...
    #
    # See the betse.util.py.pvenv.is_venv() function, whose implementation is
    # inlined below. While calling that function directly would (of course) be
    # preferable, doing so invites chicken-and-egg issues by importing *BEFORE*
    # sanitizing import directories.
    is_venv = (
        # "virtualenv", which uniquely defines the "sys.real_prefix"
        # attribute to the absolute dirname of the top-level directory
        # containing the system-wide Python interpreter *OR*...
        hasattr(sys, 'real_prefix') or

        # "venv", which (possibly non-uniquely) sets:
        #
        # * The "sys.base_prefix" attribute to the absolute dirname of the
        #   top-level directory containing the system-wide Python interpreter.
        # * The "sys.prefix" attribute to the absolute dirname of the
        #   top-level directory containing the venv-specific Python interpreter
        #   if any *OR* the system-wide Python interpreter otherwise.
        #
        # Note that, as Python >= 3.3 *ALWAYS* defines the "sys.base_prefix"
        # attribute, testing that attribute's existence is unnecessary.
        sys.prefix != sys.base_prefix
    )

    # Print whether tests are isolated to a venv.
    print('venv test isolation: {}'.format(is_venv))

    # If tests are *NOT* isolated to a venv, silently reduce to a noop.
    if not is_venv:
        return
    # ELse, tests are isolated to a venv.

    # Absolute dirname of this project's top-level directory.
    PROJECT_DIRNAME = os.path.dirname(__file__)

    # Absolute dirname of this venv's top-level directory, suffixed by a
    # directory separator for disambiguity when calling str.startswith() below.
    VENV_DIRNAME = sys.prefix + os.path.sep

    # Function-specific tester requiring "VENV_DIRNAME" and called below.
    def _is_import_path_isolated(import_pathname: str) -> bool:
        '''
        ``True`` only if the passed pathname is either isolated to this venv
        *or* is a zipfile.

        Specifically, this function returns ``True`` only if either:

        * This pathname is prefixed by the absolute dirname of this venv's
          top-level directory.
        * This pathname is suffixed by ``.zip``. Regardless of whether this
          path is isolated to this venv, zipfiles are by definition effectively
          isolated from filesystem modification (e.g., ``pip``- and
          ``setuptools``-based package installation) and thus isolated for all
          practical intents and purposes.
        '''

        # Return true only if either...
        return (
            # This pathname is isolated to this venv *OR*...
            import_pathname.startswith(VENV_DIRNAME) or
            # This pathname is a zipfile.
            (
                os.path.isfile(import_pathname) and
                import_pathname.endswith('.zip')
            )
        )


    # Sanitized list of the absolute pathnames of all paths to find modules to
    # be imported from, reordered from the unsanitized list of these pathnames
    # such that pathnames *NOT* isolated to this venv are shifted to the end of
    # this list and thus deprioritized with respect to pathnames isolated to
    # this venv.
    #
    # Ideally, pathnames *NOT* isolated to this venv would simply be removed
    # from this list. Unfortunately, doing so fundamentally breaks the world.
    # Why? Because most venv packages fail to adequately isolate venvs from
    # system-wide paths. Specifically, the "venv" and "virtualenv" packages
    # both create insufficient and arguably broken virtual environments whose
    # "lib/python${PYTHON_VERSION}/" subdirectories contain only a proper
    # subset of all requisite stdlib files -- thus necessitating that the
    # equivalent system-wide pathnames remain on "sys.path". Removing these
    # pathnames induces this fatal exception on attempting to import the stdlib
    # "pkgutil" submodule from within a purportedly isolated "tox" test venv:
    #
    #    INTERNALERROR> Traceback (most recent call last):
    #    INTERNALERROR>   File "/home/leycec/py/betse/.tox/py36/lib/python3.6/site-packages/_pytest/main.py", line 194, in wrap_session
    #    INTERNALERROR>     config.hook.pytest_sessionstart(session=session)
    #    INTERNALERROR>   File "/home/leycec/py/betse/.tox/py36/lib/python3.6/site-packages/pluggy/hooks.py", line 286, in __call__
    #    INTERNALERROR>     return self._hookexec(self, self.get_hookimpls(), kwargs)
    #    INTERNALERROR>   File "/home/leycec/py/betse/.tox/py36/lib/python3.6/site-packages/pluggy/manager.py", line 92, in _hookexec
    #    INTERNALERROR>     return self._inner_hookexec(hook, methods, kwargs)
    #    INTERNALERROR>   File "/home/leycec/py/betse/.tox/py36/lib/python3.6/site-packages/pluggy/manager.py", line 86, in <lambda>
    #    INTERNALERROR>     firstresult=hook.spec.opts.get("firstresult") if hook.spec else False,
    #    INTERNALERROR>   File "/home/leycec/py/betse/.tox/py36/lib/python3.6/site-packages/pluggy/callers.py", line 208, in _multicall
    #    INTERNALERROR>     return outcome.get_result()
    #    INTERNALERROR>   File "/home/leycec/py/betse/.tox/py36/lib/python3.6/site-packages/pluggy/callers.py", line 80, in get_result
    #    INTERNALERROR>     raise ex[1].with_traceback(ex[2])
    #    INTERNALERROR>   File "/home/leycec/py/betse/.tox/py36/lib/python3.6/site-packages/pluggy/callers.py", line 187, in _multicall
    #    INTERNALERROR>     res = hook_impl.function(*args)
    #    INTERNALERROR>   File "/home/leycec/py/betse/conftest.py", line 106, in pytest_sessionstart
    #    INTERNALERROR>     _print_metadata()
    #    INTERNALERROR>   File "/home/leycec/py/betse/conftest.py", line 260, in _print_metadata
    #    INTERNALERROR>     from betse.util.py.module import pymodule
    #    INTERNALERROR>   File "/home/leycec/py/betse/.tox/py36/lib/python3.6/site-packages/betse/util/py/module/pymodule.py", line 31, in <module>
    #    INTERNALERROR>     from betse.util.io.log import logs
    #    INTERNALERROR>   File "/home/leycec/py/betse/.tox/py36/lib/python3.6/site-packages/betse/util/io/log/logs.py", line 54, in <module>
    #    INTERNALERROR>     from betse.util.type import types
    #    INTERNALERROR>   File "/home/leycec/py/betse/.tox/py36/lib/python3.6/site-packages/betse/util/type/types.py", line 22, in <module>
    #    INTERNALERROR>     import functools, inspect, logging, pkg_resources, re
    #    INTERNALERROR>   File "/home/leycec/py/betse/.tox/py36/lib/python3.6/site-packages/pkg_resources/__init__.py", line 31, in <module>
    #    INTERNALERROR>     import pkgutil
    #    INTERNALERROR> ModuleNotFoundError: No module named 'pkgutil'
    #    ERROR: InvocationError for command /home/leycec/py/betse/.tox/py36/bin/pytest /home/leycec/py/betse (exited with code 3)
    sys_path_new = []

    # Sanitized list of the absolute pathnames of all paths to find modules to
    # be imported from that are *NOT* isolated to this venv, appended to the
    # "sys_path_new" list after iteration and thus deprioritized.
    sys_path_nonvenv = []

    # Print the absolute dirname of this venv's top-level directory.
    print('venv dir: {}'.format(sys.prefix))

    # For the pathname of each path to find imports from...
    for import_pathname in sys.path:
        # If this pathname is the empty string (implying this project's
        # top-level directory), ignore this pathname and warn the user.
        if not import_pathname:
            print(
                'WARNING: Ignoring non-isolated empty import directory...',
                file=sys.stderr)
        # Else if this pathname is that of this project's top-level directory,
        # ignore this pathname and warn the user.
        elif import_pathname == PROJECT_DIRNAME:
            print(
                'WARNING: Ignoring non-isolated import directory '
                '"{}"...'.format(import_pathname),
                file=sys.stderr)
        # Else if this pathname is *NOT* isolated to this venv...
        elif not _is_import_path_isolated(import_pathname):
            # Warn the user.
            print(
                'WARNING: Deprioritizing non-isolated import path '
                '"{}"...'.format(import_pathname),
                file=sys.stderr)

            # Append this pathname to the deprioritized list.
            sys_path_nonvenv.append(import_pathname)
        # Else, this pathname is isolated to this venv. In this case,  preserve
        # this pathname's ordering in the sanitized list.
        else:
            sys_path_new.append(import_pathname)
    # The sanitized list has now been purged of offending pathnames.

    # Extend the sanitized list of prioritized pathnames with the
    # corresponding list of deprioritized pathnames.
    sys_path_new.extend(sys_path_nonvenv)

    # Print the unsanitized list of these pathnames.
    print('venv import paths (unsanitized): ' + str(sys.path))

    # Print the sanitized list of these pathnames.
    print('venv import paths (sanitized): ' + str(sys_path_new))

    # Replace the original unsanitized list with this sanitized list as a
    # single atomic assignment, avoiding synchronization issues.
    sys.path = sys_path_new
    # print('import paths: ' + str(sys.path))

    # First pathname on this sanitized list.
    import_pathname_first = sys.path[0]

    # If this pathname is *NOT* isolated to this venv, raise an exception.
    #
    # By the above deprioritization of pathnames *NOT* isolated to this venv in
    # this sanitized list, the first pathname on this list should *ALWAYS* be
    # isolated to this venv.
    #
    if not _is_import_path_isolated(import_pathname_first):
        raise ValueError(
            'Leading import path "{}" not isolated to '
            'venv directory "{}".'.format(import_pathname_first, VENV_DIRNAME))

    # Top-level package, imported only *AFTER* sanity checks above.
    import beartype as package

    # Absolute dirname of the directory defining this package.
    PACKAGE_DIRNAME = os.path.dirname(package.__file__)

    # Print this dirname.
    print('venv project path: ' + PACKAGE_DIRNAME)

    # If this directory is *NOT* isolated to this venv, raise an exception.
    if not _is_import_path_isolated(PACKAGE_DIRNAME):
        raise ValueError(
            'Project import directory "{}" not isolated to '
            'venv directory "{}".'.format(PACKAGE_DIRNAME, VENV_DIRNAME))
