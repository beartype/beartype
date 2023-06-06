#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype import path hook context managers** (i.e., data structure caching package names
on behalf of the higher-level :func:`beartype.claw._clawmain` submodule, which
beartype import path hooks internally created by that submodule subsequently
lookup when deciding whether or not (and how) to decorate by
:func:`beartype.beartype` the currently imported user-specific submodule).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.claw._pkg.clawpkgtrie import (
    clear_packages_trie,
    packages_trie,
    packages_trie_lock,
    remove_beartype_pathhook_unless_packages_trie,
)
from beartype.typing import (
    Iterator,
    Optional,
)
from beartype._conf.confcls import (
    BEARTYPE_CONF_DEFAULT,
    BeartypeConf,
)
from contextlib import contextmanager

# ....................{ CONTEXTS                           }....................
#FIXME: Unit test us up, please.
@contextmanager
def beartyped(
    # Optional keyword-only parameters.
    *,
    conf: BeartypeConf = BEARTYPE_CONF_DEFAULT,
) -> Iterator[None]:
    '''
    Context manager temporarily registering a new **universal beartype import
    path hook** (i.e., callable inserted to the front of the standard
    :mod:`sys.path_hooks` list recursively decorating *all* typed callables and
    classes of *all* submodules of *all* packages on the first importation of
    those submodules with the :func:`beartype.beartype` decorator, wrapping
    those callables and classes with performant runtime type-checking).

    Specifically, this context manager (in order):

    #. Temporarily registers this hook by calling the public
       :func:`beartype.claw.beartype_all` function.
    #. Runs the body of the caller-defined ``with beartyped(...):`` block.
    #. Unregisters the hook registered by the prior call to that function.

    This context manager is thread-safe.

    Parameters
    ----------
    conf : BeartypeConf, optional
        **Beartype configuration** (i.e., dataclass configuring the
        :mod:`beartype.beartype` decorator for *all* decoratable objects
        recursively decorated by the path hook added by this function).
        Defaults to ``BeartypeConf()``, the default ``O(1)`` configuration.

    Yields
    ----------
    None
        This context manager yields *no* objects.

    See Also
    ----------
    :func:`beartype.claw.beartype_all`
        Arguably unsafer alternative to this function globalizing the effect of
        this function to *all* imports performed anywhere.
    '''

    # Avoid circular import dependencies.
    from beartype.claw import beartype_all

    # Prior global beartype configuration registered by a prior call to the
    # beartype_all() function if any *OR* "None" otherwise.
    packages_trie_conf_if_hooked_old: Optional[BeartypeConf] = None

    # Attempt to...
    try:
        # With a "beartype.claw"-specific thread-safe reentrant lock...
        with packages_trie_lock:
            # Store the prior global beartype configuration if any.
            packages_trie_conf_if_hooked_old = packages_trie.conf_if_hooked

            # Prevent the beartype_all() function from raising an exception on
            # conflicting registrations of beartype configurations.
            packages_trie.conf_if_hooked = None

        # Globalize the passed beartype configuration.
        beartype_all(conf=conf)

        # Defer to the caller's body of the parent "with beartyped(...):" block.
        yield
    # After doing so (regardless of whether doing so raised an exception)...
    finally:
        # With a "beartype.claw"-specific thread-safe reentrant lock...
        with packages_trie_lock:
            # If the current global beartype configuration is still the passed
            # beartype configuration, then the caller's body of the parent "with
            # beartyped(...):" block has *NOT* itself called the beartype_all()
            # function with a conflicting beartype configuration. In this
            # case...
            if packages_trie.conf_if_hooked == conf:
                # Restore the prior global beartype configuration if any.
                packages_trie.conf_if_hooked = packages_trie_conf_if_hooked_old

                # Possibly remove our beartype import path hook added by the
                # above call to beartype_all() if no packages are registered.
                remove_beartype_pathhook_unless_packages_trie()
            # Else, the caller's body of the parent "with beartyped(...):" block
            # has itself called the beartype_all() function with a conflicting
            # beartype configuration. Preserve that configuration as is.


#FIXME: Unit test us up, please.
@contextmanager
def packages_trie_cleared() -> Iterator[None]:
    '''
    Context manager resetting the
    :data:`beartype.claw._pkg.clawpkgtrie.packages_trie` global back to its
    initial state *after* running the body of the caller-defined ``with
    beartyped(...):`` block.

    This context manager is thread-safe.

    Caveats
    ----------
    **This context manager is intentionally hidden from users** rather than
    publicly exported. This context manager is *only* intended to be invoked by
    unit and integration tests in our test suite.

    Yields
    ----------
    None
        This context manager yields *no* objects.
    '''

    # Perform the caller-defined body of the parent "with" statement.
    try:
        yield
    # After doing so, regardless of whether doing so raised an exception...
    finally:
        # With a submodule-specific thread-safe reentrant lock...
        with packages_trie_lock:
            # Reset our global trie back to its initial state.
            clear_packages_trie()
