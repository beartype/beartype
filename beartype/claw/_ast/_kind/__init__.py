#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

# ....................{ TODO                               }....................
#FIXME: Additionally handle:
#* Absolute imports (e.g., "import problem_package"). This will require a new
#  visit_Import() method altogether. That said, the implementation should be
#  trivial. Why? Because this commentary in "beartype.claw.__init__":
#      Module imports effectively dynamically define a new submodule of the
#      current source submodule whose name is that submodule. Thus, for example,
#      an import of a problematic module "import celery" inside another
#      previously non-problematic submodule "muh_package.muh_submodule"
#      effectively dynamically defines a new problematic
#      "muh_package.muh_submodule.celery" submodule. This can be trivially
#      handled by just adding new entries resembling:
#          _BEFORELIST_SCHEMA_MODULE_TO_TYPE_TO_DECORATOR_NAME = FrozenDict({
#              'celery': {'Celery': 'task'},
#              'typer': {'Typer': 'command'},
#
#              # This new submodule is also known to be problematic!
#              'muh_package.muh_submodule.celery': {'Celery': 'task'},  # <-- so bad, bro
#          })
#  Note that one silly edge case exists:
#  * Absolute imports of attributes (e.g., "import
#    problem_package.bad_decorator"). These are silly, because they trivially
#    reduce to absolute imports of the top-level package (e.g., "import
#    problem_package"). In other words, simply ignore all trailing "."-delimited
#    components following the top-level package name.
#* Relative imports (e.g., "from .sibling import bad_decorator"). This should
#  also be mostly trivial. Each "." prefixing a module name being imported from
#  simply deletes a trailing "."-delimited component from the fully-qualified
#  name of the currently visited *MODULE* (not scope).
#
#  Aliasing, in other words. Just alias existing entries. \o/
