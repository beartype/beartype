#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype all-at-once low-level package name cache.**

This private submodule caches package names on behalf of the higher-level
:func:`beartype.claw.beartype_package` function. Beartype import
path hooks internally created by that function subsequently lookup these package
names from this cache when deciding whether or not (and how) to decorate a
submodule being imported with :func:`beartype.beartype`.

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.claw._pkg._clawpkgenum import BeartypeClawCoverage
from beartype.claw._pkg._clawpkgtrie import (
    PackagesTrie,
    packages_trie,
    packages_trie_lock,
)
from beartype.claw._importlib.clawimppath import add_beartype_pathhook
from beartype.roar import BeartypeClawRegistrationException
from beartype.typing import (
    Iterable,
    Optional,
)
from beartype._conf.confcls import BeartypeConf
from beartype._util.text.utiltextident import is_identifier
from collections.abc import Iterable as IterableABC

# ....................{ GETTERS                            }....................
#FIXME: Unit test us up, please.
def get_package_conf_if_added(package_name: str) -> Optional[BeartypeConf]:
    '''
    Beartype configuration with which to type-check the package with the passed
    name if that package *or* a parent package of that package was registered by
    a prior call to the :func:`.add_packages` function *or* :data:`None`
    otherwise (i.e., if neither that package *nor* a parent package of that
    package was registered by such a call).

    Caveats
    ----------
    **This function is only safely callable in a thread-safe manner within a**
    ``with _claw_lock:`` **context manager.** Equivalently, this global is *not*
    safely accessible outside that manager.

    Parameters
    ----------
    package_name : str
        Fully-qualified name of the package to be inspected.

    Returns
    ----------
    Optional[BeartypeConf]
        Either:

        * If that package or a parent package of that package was registered by
          a prior call to the :func:`.add_packages` function, the beartype
          configuration with which to type-check that package.
        * Else, :data:`None`.
    '''

    # ..................{ VALIDATION                         }..................
    # List of each unqualified basename comprising this name, split from this
    # fully-qualified name on "." delimiters. Note that the "str.split('.')" and
    # "str.rsplit('.')" calls produce the exact same lists under all possible
    # edge cases. We arbitrarily call the former rather than the latter for
    # simplicity and readability.
    package_basenames = package_name.split('.')

    # If that package is either the top-level "beartype" package or a subpackage
    # of that package, silently ignore this dangerous attempt to type-check the
    # "beartype" package by the @beartype.beartype decorator. Why? Because doing
    # so is both:
    #
    # * Fundamentally unnecessary. The entirety of the "beartype" package
    #   already religiously guards against type violations with a laborious slew
    #   of type checks littered throughout the codebase -- including assertions
    #   of the form "assert isinstance({arg}, {type}), ...". Further decorating
    #   *ALL* "beartype" callables with automated type-checking only needlessly
    #   reduces the runtime efficiency of the "beartype" package.
    # * Fundamentally dangerous, which is the greater concern. For example, the
    #   beartype.claw._ast.clawastmain.BeartypeNodeTransformer.visit_Module()
    #   dynamically inserts a module-scoped import of the
    #   @beartype._decor.decorcore.beartype_object_nonfatal decorator at the
    #   head of the module currently being imported. But if the
    #   "beartype._decor.decorcore" submodule itself is being imported, then
    #   that importation would destructively induce an infinite circular import!
    #   Could that ever happen? *YES.* Conceivably, an external caller could
    #   force reimportation of all modules by emptying the "sys.modules" cache.
    #
    # Note this edge case is surprisingly common. The public
    # beartype.claw.beartype_all() function implicitly registers *ALL* packages
    # (including "beartype" itself by default) for decoration by @beartype.
    if package_basenames[0] == 'beartype':
        return None
    # Else, that package is neither the top-level "beartype" package *NOR* a
    # subpackage of that package. In this case, register this package.

    # ..................{ ITERATION                          }..................
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # CAUTION: Synchronize logic below with the add_packages() function.
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    # With a submodule-specific thread-safe reentrant lock...
    with packages_trie_lock:
        # Current subtrie of the global package trie describing the currently
        # iterated basename of this package, initialized to the global package
        # trie describing all top-level packages.
        subpackages_trie = packages_trie

        # Beartype configuration registered with that package, defaulting to the
        # beartype configuration registered with the root package cache globally
        # applicable to *ALL* packages if an external caller previously called
        # the public beartype.claw.beartype_all() function *OR* "None" otherwise
        # (i.e., if that function has yet to be called).
        conf_curr = subpackages_trie.conf_if_added

        # For each unqualified basename of each parent package transitively
        # containing this package (as well as that of that package itself)...
        for package_basename in package_basenames:
            # Current subtrie of that trie describing that parent package if
            # that parent package was registered by a prior call to the
            # add_packages() function *OR* "None" otherwise (i.e., if that
            # parent package has yet to be registered).
            subpackages_subtrie = subpackages_trie.get(package_basename)

            # If that parent package has yet to be registered, halt iteration.
            if subpackages_subtrie is None:
                break
            # Else, that parent package was previously registered.

            # Beartype configuration registered with either...
            conf_curr = (
                # That parent package if any *OR*...
                #
                # Since that parent package is more granular (i.e., unique) than
                # any transitive parent package of that parent package, the
                # former takes precedence over the latter when defined.
                subpackages_subtrie.conf_if_added or
                # A transitive parent package of that parent package if any.
                conf_curr
            )

            # Iterate the currently examined subtrie one subpackage deeper.
            subpackages_trie = subpackages_subtrie

    # Return this beartype configuration if any *OR* "None" otherwise.
    return conf_curr

# ....................{ ADDERS                             }....................
#FIXME: Unit test us up, please.
def add_packages(
    # Keyword-only arguments.
    *,

    # Mandatory keyword-only arguments.
    coverage: BeartypeClawCoverage,
    conf: BeartypeConf,

    # Optional keyword-only arguments.
    package_name: Optional[str] = None,
    package_names: Optional[Iterable[str]] = None,
) -> None:
    '''
    Register a new **beartype package import path hook** (i.e., callable
    inserted to the front of the standard :mod:`sys.path_hooks` list recursively
    applying the :func:`beartype.beartype` decorator to all typed callables and
    classes of all submodules of all packages with the passed names on the first
    importation of those submodules).

    Parameters
    ----------
    coverage : BeartypeClawCoverage
        **Import hook coverage** (i.e., competing package scope over which to
        apply the path hook added by this function, each with concomitant
        tradeoffs with respect to runtime complexity and quality assurance).
    conf : BeartypeConf, optional
        **Beartype configuration** (i.e., dataclass configuring the
        :mod:`beartype.beartype` decorator for *all* decoratable objects
        recursively decorated by the path hook added by this function).
    package_name : Optional[str]
        Either:

        * If ``coverage`` is :attr:`BeartypeClawCoverage.PACKAGES_ONE`, the
          fully-qualified name of the package to be type-checked.
        * Else, ignored.

        Defaults to :data:`None`.
    package_names : Optional[Iterable[str]]]
        Either:

        * If ``coverage`` is :attr:`BeartypeClawCoverage.PACKAGES_MANY`, an
          iterable of the fully-qualified names of one or more packages to be
          type-checked.
        * Else, ignored.

        Defaults to :data:`None`.

    Raises
    ----------
    BeartypeClawRegistrationException
        If either:

        * The passed ``package_names`` parameter is either:

          * Neither a string nor an iterable (i.e., fails to satisfy the
            :class:`collections.abc.Iterable` protocol).
          * An empty string or iterable.
          * A non-empty string that is *not* a valid **package name** (i.e.,
            ``"."``-delimited concatenation of valid Python identifiers).
          * A non-empty iterable containing at least one item that is either:

            * *Not* a string.
            * The empty string.
            * A non-empty string that is *not* a valid **package name** (i.e.,
              ``"."``-delimited concatenation of valid Python identifiers).

        * The passed ``conf`` parameter is *not* a beartype configuration (i.e.,
          :class:`BeartypeConf` instance).

    See Also
    ----------
    https://stackoverflow.com/a/43573798/2809027
        StackOverflow answer strongly inspiring the low-level implementation of
        this function with respect to inscrutable :mod:`importlib` machinery.
    '''

    # ..................{ VALIDATION                         }..................
    # This configuration is *NOT* a configuration, raise an exception.
    if not isinstance(conf, BeartypeConf):
        raise BeartypeClawRegistrationException(
            f'Beartype configuration {repr(conf)} invalid (i.e., not '
            f'"beartype.BeartypeConf" instance).'
        )
    # Else, this configuration is a configuration.

    # If the caller did *NOT* request all-packages coverage, the caller
    # requested coverage over a specific subset of packages. In this case...
    if coverage is not BeartypeClawCoverage.PACKAGES_ALL:
        # If the caller requested mono-package coverage...
        if coverage is BeartypeClawCoverage.PACKAGES_ONE:
            # If the caller improperly passed *NO* package name despite
            # requesting mono-package coverage, raise an exception.
            if package_name is None:
                raise BeartypeClawRegistrationException(
                    f'beartype_package() '
                    f'package name {repr(package_name)} invalid.'
                )
            # Else, the caller properly passed a package name.

            # Wrap this package name in a 1-tuple containing only this name.
            # Doing so unifies logic below.
            package_names = (package_name,)
        # Else, the caller requested multi-package coverage.
        # elif coverage is BeartypeClawCoverage.PACKAGES_MANY:

        # If this package names is *NOT* iterable, raise an exception.
        if not isinstance(package_names, IterableABC):
            raise BeartypeClawRegistrationException(
                f'beartype_packages() '
                f'package names {repr(package_name)} not iterable.'
            )
        # Else, this package names is iterable.
        #
        # If *NO* package names were passed, raise an exception.
        elif not package_names:
            raise BeartypeClawRegistrationException(
                'beartype_packages() package names empty.')
        # Else, one or more package names were passed.

        # For each such package name...
        for package_name in package_names:
            # If this package name is *NOT* a string, raise an exception.
            if not isinstance(package_name, str):
                raise BeartypeClawRegistrationException(
                    f'Package name {repr(package_name)} not string.')
            # Else, this package name is a string.
            #
            # If this package name is *NOT* a valid Python identifier, raise an
            # exception.
            elif not is_identifier(package_name):
                raise BeartypeClawRegistrationException(
                    f'Package name {repr(package_name)} invalid '
                    f'(i.e., not "."-delimited Python identifier).'
                )
            # Else, this package name is a valid Python identifier.

    # ..................{ ITERATION                          }..................
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # CAUTION: Synchronize logic below with the get_package_conf_if_added()
    # function. The iteration performed below modifies the global package trie
    # and thus *CANNOT* defer to the same logic.
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    # With a submodule-specific thread-safe reentrant lock...
    with packages_trie_lock:
        # If the caller requested all-packages coverage...
        if coverage is BeartypeClawCoverage.PACKAGES_ALL:
            # Beartype configuration currently associated with *ALL* packages by
            # a prior call to this function if any *OR* "None" (i.e., if this
            # function has yet to be called under this Python interpreter).
            conf_curr = packages_trie.conf_if_added

            # If the higher-level beartype_all() function (calling this
            # lower-level adder) has yet to be called under this interpreter,
            # associate this configuration with *ALL* packages.
            if conf_curr is None:
                packages_trie.conf_if_added = conf
            # Else, beartype_all() was already called under this interpreter.
            #
            # If the caller passed a different configuration to that prior call
            # than that passed to this current call, raise an exception.
            elif conf_curr != conf:
                raise BeartypeClawRegistrationException(
                    f'beartype_all() previously passed '
                    f'conflicting beartype configuration:\n'
                    f'\t----------( OLD "conf" PARAMETER )----------\n'
                    f'\t{repr(conf_curr)}\n'
                    f'\t----------( NEW "conf" PARAMETER )----------\n'
                    f'\t{repr(conf)}\n'
                )
            # Else, the caller passed the same configuration to that prior call
            # than that passed to the current call. In this case, silently
            # ignore this redundant request to re-register all packages.
        # Else, the caller requested coverage over a subset of packages. In this
        # case...
        else:
            # For the fully-qualified name of each package to be registered...
            for package_name in package_names:  # type: ignore[union-attr]
                # List of each unqualified basename comprising this name, split
                # from this fully-qualified name on "." delimiters. Note that
                # the "str.split('.')" and "str.rsplit('.')" calls produce the
                # exact same lists under all possible edge cases. We arbitrarily
                # call the former rather than the latter for simplicity.
                package_basenames = package_name.split('.')

                # Current subtrie of the global package trie describing the
                # currently iterated basename of this package, initialized to
                # the global package trie describing all top-level packages.
                subpackages_trie = packages_trie

                # For each unqualified basename comprising the directed path
                # from the root parent package of that package to that
                # package...
                for package_basename in package_basenames:
                    # Current subtrie of that trie describing that parent
                    # package if that parent package was registered by a prior
                    # call to the add_packages() function *OR* "None" (i.e., if
                    # that parent package has yet to be registered).
                    subpackages_subtrie = subpackages_trie.get(package_basename)

                    # If this is the first registration of that parent package,
                    # register a new subtrie describing that parent package.
                    #
                    # Note that this test could be obviated away by refactoring
                    # our "PackagesTrie" subclass from the
                    # "collections.defaultdict" superclass rather than the
                    # standard "dict" class. Since doing so would obscure
                    # erroneous attempts to access non-existing keys, however,
                    # this test is preferable to inviting even *MORE* bugs into
                    # this bug-riddled codebase. Just kidding! There are
                    # absolutely no bugs in this codebase. *wink*
                    if subpackages_subtrie is None:
                        subpackages_subtrie = \
                            subpackages_trie[package_basename] = \
                            PackagesTrie()
                    # Else, that parent package was already registered by a
                    # prior call to this function.

                    # Iterate the current subtrie one subpackage deeper.
                    subpackages_trie = subpackages_subtrie
                # Since the "package_basenames" list contains at least one
                # basename, the above iteration set the currently examined
                # subdictionary "subpackages_trie" to at least one subtrie of
                # the global package trie. Moreover, that subtrie is guaranteed
                # to describe the current (sub)package being registered.

                # Beartype configuration currently associated with that package
                # by a prior call to this function if any *OR* "None" (i.e., if
                # that package has yet to be registered by a prior call to this
                # function).
                conf_curr = subpackages_trie.conf_if_added

                # If that package has yet to be registered, associate this
                # configuration with that package.
                if conf_curr is None:
                    subpackages_trie.conf_if_added = conf
                # Else, that package was already registered by a previous call
                # to this function.
                #
                # If the caller passed a different configuration to that prior
                # call than that passed to this current call, raise an
                # exception.
                elif conf_curr != conf:
                    raise BeartypeClawRegistrationException(
                        f'Beartype import hook '
                        f'(e.g., beartype.claw.beartype_*() function) '
                        f'previously passed '
                        f'conflicting beartype configuration for '
                        f'package name "{package_name}":\n'
                        f'\t----------( OLD "conf" PARAMETER )----------\n'
                        f'\t{repr(conf_curr)}\n'
                        f'\t----------( NEW "conf" PARAMETER )----------\n'
                        f'\t{repr(conf)}\n'
                    )
                # Else, the caller passed the same configuration to that prior
                # call than that passed to the current call. In this case,
                # silently ignore this redundant request to re-register that
                # package.

        # Lastly, if our beartype import path hook singleton has *NOT* already
        # been added to the standard "sys.path_hooks" list, do so now.
        #
        # Note that we intentionally:
        # * Do so in a thread-safe manner inside this lock.
        # * Defer doing so until *AFTER* the above iteration has successfully
        #   registered the desired packages with our global package trie. Why?
        #   This path hook subsequently calls the companion
        #   get_package_conf_if_added() function, which accesses this trie.
        add_beartype_pathhook()
