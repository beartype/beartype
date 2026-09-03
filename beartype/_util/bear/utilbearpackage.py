#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :mod:`beartype` **package utilities** (i.e., low-level callables
generically applicable to the *entire* :mod:`beartype` package as a whole).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
import sys

# ....................{ TESTERS                            }....................
#FIXME: Unit test us up, please. Probably impossible. Try anyway. At least call
#this tester from a unit test and assert it raises no exceptions, please. *sigh*
def is_beartype_initted_partial() -> bool:
    '''
    :data:`True` only if :mod:`beartype` has been **fully initialized** (i.e.,
    sufficiently imported such that :mod:`beartype.claw` import hooks registered
    by external users may safely type-check under the current call stack
    but has yet to be fully imported).
    '''

    #
    for module_name in _BEARTYPE_INIT_VULNERABLE_MODULE_NAMES:
        if is_module_initted_partial(module_name):
            return True

    return False


# This tester is intentionally defined in this higher-level submodule rather
# than the lower-level "beartype._util.module.utilmodtest" submodule, which
# would ordinarily be the preferred submodule for this tester. Why? Because the
# latter approach induces *UNRESOLVABLE* circular imports from "beartype.claw"
# import hooks under inscrutable edge cases which do *NOT* bear thinking about.
# We tried literally everything. This is the *ONLY* approach that works. "Urgh!"
def is_module_initted_partial(module_name: str) ->  bool:
    '''
    :data:`True` only if the module with the passed fully-qualified name is only
    **partially initialized** (i.e., is currently in the process of being
    imported by standard :mod:`importlib` machinery under the current call stack
    but has yet to be fully imported).

    This tester is intentionally *not* memoized (e.g., by ``@callable_cached``),
    as the importability of modules can dynamically change throughout the
    lifetime of this interpreter in response to dynamic module creation and
    deletion as well as modification to low-level :mod:`importlib` machinery.

    Parameters
    ----------
    module_name : str
        Fully-qualified name of the module to be inspected.

    Returns
    -------
    bool
        :data:`True` only if this module is only partially initialized.
    '''
    assert isinstance(module_name, str), f'{repr(module_name)} not string.'

    # ....................{ MODULE                         }....................
    # Module object encapsulating either the current partial importation of the
    # module with the passed name *OR* the prior full importation of that module
    # if that module either currently is or has already been imported *OR*
    # "None" otherwise (i.e., If that module has yet to be imported).
    module = sys.modules.get(module_name)

    # If that module has yet to be imported, that module *CANNOT* (by
    # definition) be partially initialized. In this case, return false.
    if module is None:
        return False
    # If that module either currently is or has already been imported.

    # ....................{ SPEC                           }....................
    # Module spec describing the importation of that module if an external
    # caller has *NOT* already maliciously deleted the "__spec__" dunder
    # attribute providing that module spec *OR* "None" otherwise (i.e., if a
    # caller has already maliciously deleted that dunder attribute).
    module_spec = getattr(module, '__spec__', None)

    # If a caller has already maliciously deleted that dunder attribute, this
    # tester has *NO* means of deciding whether that module is partially or
    # fully initialized. Why? Because the *ONLY* means of deciding that question
    # is to introspect the private "_initializing" instance variable defined on
    # that spec. This can be trivially demonstrated by intentionally deleting
    # the "__spec__" dunder attribute from the global scope of any arbitrary
    # module and then trivially inducing a circular import between that same
    # module and any other; after doing so, CPython no longer raises the
    # expected "ImportError" exception. In other words, CPython itself requires
    # that same private "_initializing" instance variable defined on module
    # specs to detect circular imports. Destroying module specs thus destroys
    # CPython's ability to detect circular imports. That sounds bad. Ideally,
    # this would mean that we would now either raise a fatal warning *OR* issue
    # a non-fatal warning to inform the user of this badness. Unfortunately,
    # doing even that much would be harmful to the general case. Why? Because
    # module specs are technically optional; although common, they're *ONLY*
    # defined for physical modules imported via standard "importlib" machinery.
    # Module specs are often *NOT* defined for non-physical modules dynamically
    # defined in memory, for example. It's best to make *NO* unsafe assumptions.
    #
    # Thankfully, that this is an *EXTREMELY* unlikely edge case. The *ONLY*
    # reason we even bother handling this awful edge case is because we are
    # beartype. Beartype is QA. In QA, we handle edge cases. It's what we do.
    if module_spec is None:
        return False
    # Else, that module still defines the "__spec__" dunder attribute. Yay! \o/

    # ....................{ INITTED                        }....................
    # Return true only if this module spec enables the CPython-specific private
    # "_initializing" instance variable defined by the standard (albeit private)
    # importlib._bootstrap._load_unlocked() function: e.g.,
    #     # In the standard "importlib._bootstrap" submodule:
    #     def _load_unlocked(spec):
    #         # A helper for direct use by the import system.
    #         module = module_from_spec(spec)
    #
    #         # This must be done before putting the module in sys.modules
    #         # (otherwise an optimization shortcut in import.c becomes
    #         # wrong).
    #         spec._initializing = True
    #         ...
    return getattr(module_spec, '_initializing', False)

# ....................{ TESTERS                            }....................
_BEARTYPE_INIT_VULNERABLE_MODULE_NAMES = (
    'beartype',
    'beartype.claw._clawstate',

    #FIXME: *DEFINITELY* not right. This fragility suggests that
    #is_beartype_initted_partial() reports false results. We probably want to
    #generalize is_module_initted_partial() to additionally attempt to
    #dynamically import that module and ensure that *NO* "ImportError"
    #exception is raised.
    #FIXME: After doing so, comment this out. Everything should just work then.
    'beartype.claw._package.clawpkgtrie',
)
'''
'''
