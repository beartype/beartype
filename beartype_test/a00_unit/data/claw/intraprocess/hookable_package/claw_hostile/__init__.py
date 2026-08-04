#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Test-wide **beartype-hostile import hook subpackage initialization submodule**
(i.e., data module mimicking real-world usage of various :func:`beartype.claw`
import hooks on packages and modules concurrently subjected to
**beartype-hostile import hooks** (i.e., external import hooks mimicking
existing competing import hooks published by real-world third-party packages and
modules, which silently override :func:`beartype.claw` import hooks and thus
silently prevent :mod:`beartype` from applying runtime type-checking to *any*
submodules of this subpackage)).
'''

#FIXME: Excise us up, please. *sigh*
# # ....................{ IMPORTS                            }....................
# from beartype.claw._importlib._clawimpfilefinder import (
#     is_beartype_file_finder_path_hook)
# from importlib.machinery import PathFinder
#
# # Mimic imports performed in the "importlib._bootstrap_external" submodule.
# import sys
# import warnings as _warnings
#
# # ....................{ SUBCLASSES                         }....................
# class PathFinderBeartypeHater(PathFinder):
#     '''
#     **Beartype-hostile meta path hook** (i.e., :class:`.PathFinder` subclass
#     explicitly ignoring *only* :mod:`beartype.claw` import hooks, intended to be
#     injected as a drop-in replacement of the standard :mod:`beartype`-friendly
#     :class:`.PathFinder` into the global :obj:`sys.meta_path` list).
#
#     Caveats
#     -------
#     **This path finder is probably non-thread-safe.** This path finder is thus
#     suitable for use only in a single-threaded test suite.
#     '''
#
#     @staticmethod
#     def _path_hooks(path: str) -> object:
#         '''
#         Search the global :obj:`sys.path_hooks` list for an applicable path hook
#         suitable for importing the Python package or module with the passed
#         absolute or relative pathname.
#
#         This override of the standard :meth:`.FileFinder._path_hooks` method
#         monkey-patches that method to explicitly ignore *only*
#         :mod:`beartype.claw` import hooks and thus be :mod:`beartype`-hostile.
#         '''
#
#         #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#         # CAUTION: This code is copied verbatim from the standard implementation
#         # of this method in the Python standard library. Avoid modifying, yo!
#         #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#         if sys.path_hooks is not None and not sys.path_hooks:
#             _warnings.warn('sys.path_hooks is empty', ImportWarning)
#         for hook in sys.path_hooks:
#             #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#             # MINIMALIST MONKEY-PATCH: You Begin Now!
#             #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#             # If this path hook is the beartype-specific file finder path hook
#             # added by the call to the beartype_this_package() import hook
#             # below, simulate a real-world beartype-hostile meta path hook by
#             # silently ignoring this path hook.
#             if is_beartype_file_finder_path_hook(hook):
#                 continue
#             # Else, this path hook is *NOT* beartype-specific. In this case,
#             # defer to this path hook in the standard PEP 302-compliant way.
#             #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#             # MINIMALIST MONKEY-PATCH: You End Now. What? Already!?
#             #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#         #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#         # CAUTION: This code is copied verbatim from the standard implementation
#         # of this method in the Python standard library. Avoid modifying, yo!
#         #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#             try:
#                 return hook(path)
#             except ImportError:
#                 continue
#         else:
#             return None
#
# # ....................{ META PATH                          }....................
# # Register the beartype-hostile meta path hook defined above in the most hostile
# # way possible, which is also (sadly) the most common use pattern for
# # registering *ANY* hook. Specifically, override *ALL* competing path hooks by
# # shoving straight to the front of the line. Beartype hate: "It feels bad."
# sys.meta_path.insert(0, PathFinderBeartypeHater)

# ....................{ IMPORTS                            }....................
from beartype_test.a00_unit.data.claw.intraprocess.hookable_package.claw_hostile import (
    data_claw_claw_hostile)
