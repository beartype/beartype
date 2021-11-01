#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2021 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **Sphinx** utilities (i.e., callables handling the third-party
:mod:`sphinx` package as an optional runtime dependency of this project).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                           }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To prevent this project from accidentally requiring third-party
# packages as mandatory runtime dependencies, avoid importing from *ANY* such
# package via a module-scoped import. These imports should be isolated to the
# bodies of callables declared below.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from beartype._util.cache.utilcachecall import callable_cached
# from beartype._util.mod.utilmodimport import import_module_attr
from beartype._util.mod.utilmodtest import is_package

# See the "beartype.cave" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ TESTERS                           }....................
#FIXME: Unit test us up, please.
@callable_cached
def is_sphinx() -> bool:
    '''
    ``True`` only if the optional third-party :mod:`sphinx` package is
    importable under the active Python interpreter.
    '''

    # Return true only if Sphinx is importable.
    return is_package('sphinx')


#FIXME: Unit test us up, please. See this point for a reasonably simple Sphinx
#directory layout we might consider harvesting inspiration from:
#    https://stackoverflow.com/q/62651201/2809027
#Note that we probably want to use Sphinx's auto-configuration tool to build
#out a simple "conf.py" and directory layout with.
#FIXME: Actually, this is probably pointless. Although this *SHOULD* work to
#detect mocked objects, that doesn't particularly help us. We'd need to spam
#this function *EVERYWHERE* through the codebase to ignore such objects, which
#isn't the right approach at all. See also this Sphinx-time traceback:
#    https://github.com/SeldonIO/alibi/pull/511#issuecomment-951727266
#The right solution, of course, is to conditionally detect when "autodoc" is
#running. So, let's do that, please.
# def is_object_mocked_sphinx_autodoc(obj: object) -> bool:
#     '''
#     ``True`` only if the passed object is :mod:`sphinx.ext.autodoc`-mocked
#     (i.e., mocked by Sphinx's builtin ``autodoc`` extension, typically via a
#     Sphinx-specific top-level ``conf.py`` configuration file in the downstream
#     codebase enabling listing all modules to be implicitly mocked via the
#     ``autodoc_mock_imports`` list global).
#
#     Parameters
#     ----------
#     obj : object
#         Arbitrary object to be inspected.
#
#     Returns
#     ----------
#     bool
#         ``True`` only if this object is :mod:`sphinx.ext.autodoc`-mocked.
#
#     Raises
#     ----------
#     :exc:`beartype.roar._roarexc._BeartypeUtilModuleException`
#         If either:
#
#         * :mod:`sphinx` is *not* installed under the active Python interpreter.
#         * :mod:`sphinx` is installed under the active Python interpreter but
#           the :func:`sphinx.ext.autodoc.mock.ismock` is unimportable (e.g., due
#           to this version of Sphinx being either overly old or new).
#     '''
#
#     # sphinx.ext.autodoc.mock.ismock() tester safely imported from Sphinx.
#     ismock = import_module_attr(
#         module_attr_name='sphinx.ext.autodoc.mock.ismock',
#         exception_prefix='Sphinx function ',
#     )
#     assert callable(ismock), f'{repr(ismock)} uncallable.'
#
#     # Return true only if this tester returns true when passed this object.
#     return ismock(obj)
