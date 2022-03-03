#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2022 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype.**

For :pep:`8` compliance, this namespace exposes a subset of the metadata
constants published by the :mod:`beartype.meta` submodule. These metadata
constants are commonly inspected (and thus expected) by external automation.
'''

# ....................{ TODO                              }....................
#FIXME: *DROP PYTHON 3.6 SUPPORT.* Seriously. It's dead, people. Code goes on.

#FIXME: Consider significantly expanding the above module docstring, assuming
#Sphinx presents this module in its generated frontmatter.

# ....................{ IMPORTS                           }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# CAUTION: Explicitly list *ALL* public attributes imported below in the
# "__all__" list global declared below to avoid linter complaints.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# CAUTION: To avoid race conditions during setuptools-based installation, this
# module may import *ONLY* from modules guaranteed to exist at the start of
# installation. This includes all standard Python and package submodules but
# *NOT* third-party dependencies, which if currently uninstalled will only be
# installed at some later time in the installation. Likewise, to avoid circular
# import dependencies, the top-level of this module should avoid importing
# package submodules where feasible.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# CAUTION: To avoid polluting the public module namespace, external attributes
# should be locally imported at module scope *ONLY* under alternate private
# names (e.g., "from argparse import ArgumentParser as _ArgumentParser" rather
# than merely "from argparse import ArgumentParser").
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ IMPORTS ~ meta                    }....................
# For PEP 8 compliance, versions constants expected by external automation are
# imported under their PEP 8-mandated names.
from beartype.meta import VERSION as __version__
from beartype.meta import VERSION_PARTS as __version_info__

# ....................{ IMPORTS ~ non-meta                }....................
from sys import modules as _modules

# If this submodule is being imported at install time from our top-level
# "setup.py" script, avoid implicitly importing from *ANY* "beartype" submodule
# other than the "beartype.meta" submodule. By sheer force of will,
# "beartype.meta" is the *ONLY* "beartype" submodule guaranteed to be safely
# importable at install time. All other "beartype" submodules should be assumed
# to be unsafe due to potentially importing one or more optional runtime
# dependencies yet to be installed (e.g., "typing_extensions" package). See
# "setup.py" for further details.
if 'beartype.__is_installing__' not in _modules:
    # Publicize the private @beartype._decor.beartype decorator as
    # @beartype.beartype, preserving all implementation details as private.
    from beartype._decor.main import beartype

    #FIXME: Unit test the existence of:
    #* "beartype.BeartypeStrategy".
    #* "beartype.BeartypeConfiguration".
    # Publicize all top-level configuration attributes required to configure the
    # @beartype.beartype decorator.
    from beartype._decor.conf import (
        BeartypeConf,
        BeartypeStrategy,
    )

# Delete the temporarily imported "sys.modules" global for ultimate safety.
del _modules

# ....................{ GLOBALS                           }....................
# Document all global variables imported into this namespace above.

__version__ = __version__
'''
Human-readable package version as a ``.``-delimited string.

For PEP 8 compliance, this specifier has the canonical name ``__version__``
rather than that of a typical global (e.g., ``VERSION_STR``).
'''


__version_info__ = __version_info__
'''
Machine-readable package version as a tuple of integers.

For PEP 8 compliance, this specifier has the canonical name
``__version_info__`` rather than that of a typical global (e.g.,
``VERSION_PARTS``).
'''


__all__ = [
    'BeartypeConf',
    'BeartypeStrategy',
    'beartype',
    '__version__',
    '__version_info__',
]
'''
Special list global of the unqualified names of all public package attributes
explicitly exported by and thus safely importable from this package.

Caveats
-------
**This global is defined only for conformance with static type checkers,** a
necessary prerequisite for :pep:`561`-compliance. This global is *not* intended
to enable star imports of the form ``from beartype import *`` (now largely
considered a harmful anti-pattern by the Python community), although it
technically does the latter as well.

This global would ideally instead reference *only* a single package attribute
guaranteed *not* to exist (e.g., ``'STAR_IMPORTS_CONSIDERED_HARMFUL'``),
effectively disabling star imports. Since doing so induces spurious static
type-checking failures, we reluctantly embrace the standard approach. For
example, :mod:`mypy` emits an error resembling:

    error: Module 'beartype' does not explicitly export attribute 'beartype';
    implicit reexport disabled.
'''
