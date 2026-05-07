#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype import hook blacklists** (i.e., global constants broadly
concerning various third-party modules and packages rather than one specific
third-party module or package).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype._cave._cavefast import RegexCompiledType

# ....................{ GLOBALS                            }....................
BLACKLIST_PACKAGE_NAMES_REGEX: RegexCompiledType = None  # type: ignore[assignment]
'''
Compiled regular expression matching the fully-qualified names of all top-level
packages to be blacklisted by the :func:`.BeartypeSourceFileLoader.get_code`
method.

See commentary inside that method for exhaustive (and exhausting) details.
'''

# ....................{ PRIVATE ~ initializers             }....................
def _init() -> None:
    '''
    Initialize this submodule.
    '''

    # Defer function-specific imports. Mostly just 'cause. Deal with it. \o/
    from re import compile as re_compile

    # Enable this global to be locally initialized below.
    global BLACKLIST_PACKAGE_NAMES_REGEX

    # Frozen set of the fully-qualified names of all top-level packages to be
    # blacklisted by the BeartypeSourceFileLoader.get_code() method.
    #
    # Note that:
    # * This set is defined in an ad-hoc brute-force manner by simply
    #   iteratively adding package names to this set until all tests pass. Yes,
    #   this is absurd. Yes, this is "importlib" Hell. Welcome to Python, son.
    # * If you are reading this, you are wondering exactly how we decided what
    #   package names to even add to this set. The answer is that we manually
    #   inspected circular "ImportError" exceptions raised by the
    #   Coverage.py-specific integration test for suspicious imports of *ANY*
    #   packages residing outside the beartype codebase. For example, a cautious
    #   inspection of the following traceback would note the ultra-suspicious
    #   "import email" import statement, suggesting that the standard "email"
    #   package also needs to be added to this set: e.g.,
    #       Traceback (most recent call last):
    #         File "<frozen runpy>", line 196, in _run_module_as_main
    #         File "<frozen runpy>", line 87, in _run_code
    #         File "/home/leycec/py/pyenv/versions/3.15.0a8/lib/python3.15/site-packages/coverage/__main__.py", line 12, in <module>
    #           sys.exit(main())
    #                    ~~~~^^
    #         File "/home/leycec/py/pyenv/versions/3.15.0a8/lib/python3.15/site-packages/coverage/cmdline.py", line 1163, in main
    #           status = CoverageScript().command_line(argv)
    #         File "/home/leycec/py/pyenv/versions/3.15.0a8/lib/python3.15/site-packages/coverage/cmdline.py", line 853, in command_line
    #           return self.do_run(options, args)
    #                  ~~~~~~~~~~~^^^^^^^^^^^^^^^
    #         File "/home/leycec/py/pyenv/versions/3.15.0a8/lib/python3.15/site-packages/coverage/cmdline.py", line 1042, in do_run
    #           runner.run()
    #           ~~~~~~~~~~^^
    #         File "/home/leycec/py/pyenv/versions/3.15.0a8/lib/python3.15/site-packages/coverage/execfile.py", line 174, in run
    #           self._prepare2()
    #           ~~~~~~~~~~~~~~^^
    #         File "/home/leycec/py/pyenv/versions/3.15.0a8/lib/python3.15/site-packages/coverage/execfile.py", line 139, in _prepare2
    #           pathname, self.package, self.spec = find_module(self.modulename)
    #                                               ~~~~~~~~~~~^^^^^^^^^^^^^^^^^
    #         File "/home/leycec/py/pyenv/versions/3.15.0a8/lib/python3.15/site-packages/coverage/execfile.py", line 58, in find_module
    #           spec = importlib.util.find_spec(mod_main)
    #         File "<frozen importlib.util>", line 90, in find_spec
    #         File "/home/leycec/py/beartype/beartype/claw/_importlib/_clawimpload.py", line 394, in get_code
    #           from beartype.claw._clawstate import claw_state
    #         File "/home/leycec/py/beartype/beartype/__init__.py", line 150, in <module>
    #           _init()
    #           ~~~~~^^
    #         File "/home/leycec/py/beartype/beartype/__init__.py", line 71, in _init
    #           from beartype.meta import (
    #           ...<4 lines>...
    #           )
    #         File "/home/leycec/py/beartype/beartype/meta.py", line 35, in <module>
    #           from importlib.metadata import metadata as _get_package_metadata
    #         File "/home/leycec/py/pyenv/versions/3.15.0a8/lib/python3.15/importlib/metadata/__init__.py", line 14, in <module>
    #           import email  # <-- *THIS IS ULTRA-SUSPICIOUS IMPORT OF DOOMGUY*
    #         File "/home/leycec/py/beartype/beartype/claw/_importlib/_clawimpload.py", line 394, in get_code
    #           from beartype.claw._clawstate import claw_state
    #         File "/home/leycec/py/beartype/beartype/claw/__init__.py", line 210, in <module>
    #           from beartype.claw._clawmain import (
    #           ...<4 lines>...
    #           )
    #         File "/home/leycec/py/beartype/beartype/claw/_clawmain.py", line 24, in <module>
    #           from beartype.claw._package.clawpkgmain import hook_packages
    #         File "/home/leycec/py/beartype/beartype/claw/_package/clawpkgmain.py", line 16, in <module>
    #           from beartype.claw._package.clawpkgtrie import (
    #           ...<5 lines>...
    #           )
    #         File "/home/leycec/py/beartype/beartype/claw/_package/clawpkgtrie.py", line 17, in <module>
    #           from beartype.claw._importlib.clawimpmain import remove_beartype_pathhook
    #         File "/home/leycec/py/beartype/beartype/claw/_importlib/clawimpmain.py", line 18, in <module>
    #           from beartype.claw._importlib._clawimpload import BeartypeSourceFileLoader
    #         File "/home/leycec/py/beartype/beartype/claw/_importlib/_clawimpload.py", line 18, in <module>
    #           from beartype.claw._ast.clawastmain import BeartypeNodeTransformer
    #         File "/home/leycec/py/beartype/beartype/claw/_ast/clawastmain.py", line 21, in <module>
    #           from beartype.claw._ast._kind.clawastassign import (
    #               BeartypeNodeTransformerAssignMixin)
    #         File "/home/leycec/py/beartype/beartype/claw/_ast/_kind/clawastassign.py", line 24, in <module>
    #           from beartype._data.claw.dataclawmagic import BEARTYPE_RAISER_FUNC_NAME
    #         File "/home/leycec/py/beartype/beartype/_data/claw/dataclawmagic.py", line 14, in <module>
    #           from beartype.meta import (
    #           ...<2 lines>...
    #           )
    #       ImportError: cannot import name 'NAME' from partially initialized module 'beartype.meta' (most likely due to a circular import) (/home/leycec/py/beartype/beartype/meta.py)
    _BLACKLIST_PACKAGE_NAMES = frozenset((
        'beartype',
        'calendar',
        'csv',
        'email',
        'importlib',
        'numbers',
        'quopri',
        'shutil',
        'tempfile',
        'time',
        'uu',
        'zipfile',
    ))

    # "|"-delimited string of these names.
    _BLACKLIST_PACKAGE_NAMES_ORED = r'|'.join(_BLACKLIST_PACKAGE_NAMES)

    # Compiled regular expression matching any string starting with these names
    # and either:
    # * Immediately terminating *OR*...
    # * Followed by a "." delimiter (effectively also terminating that name)
    #   followed by one or more arbitrary characters.
    BLACKLIST_PACKAGE_NAMES_REGEX = re_compile(
        rf'^({_BLACKLIST_PACKAGE_NAMES_ORED})(?:\..+)?$')


# Initialize this submodule.
_init()
