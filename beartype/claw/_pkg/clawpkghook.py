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
from beartype.claw._pkg.clawpkgenum import BeartypeClawCoverage
from beartype.claw._pkg.clawpkgtrie import (
    PackagesTrie,
    # is_packages_trie,
    iter_packages_trie,
    packages_trie,
    packages_trie_lock,
    remove_beartype_pathhook_unless_packages_trie,
)
from beartype.claw._importlib.clawimppath import (
    add_beartype_pathhook,
    # remove_beartype_pathhook,
)
from beartype.roar import BeartypeClawRegistrationException
from beartype.typing import (
    Iterable,
    Optional,
)
from beartype._conf.confcls import BeartypeConf
from beartype._util.text.utiltextident import is_identifier
from collections.abc import Iterable as IterableABC

# ....................{ (UN)HOOKERS                        }....................
#FIXME: Unit test us up, please.
def hook_packages(
    # Keyword-only arguments.
    *,

    # Mandatory keyword-only arguments.
    claw_coverage: BeartypeClawCoverage,
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
    claw_coverage : BeartypeClawCoverage
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

    # Iterable of the passed fully-qualified names of all packages to be hooked.
    package_names = _get_package_names_from_args(
        claw_coverage=claw_coverage,
        conf=conf,
        package_name=package_name,
        package_names=package_names,
    )

    # With a submodule-specific thread-safe reentrant lock...
    with packages_trie_lock:
        # If the caller requested all-packages coverage...
        if claw_coverage is BeartypeClawCoverage.PACKAGES_ALL:
            # Beartype configuration currently associated with *ALL* packages by
            # a prior call to this function if any *OR* "None" (i.e., if this
            # function has yet to be called under this Python interpreter).
            conf_curr = packages_trie.conf_if_hooked

            # If the higher-level beartype_all() function (calling this
            # lower-level adder) has yet to be called under this interpreter,
            # associate this configuration with *ALL* packages.
            if conf_curr is None:
                packages_trie.conf_if_hooked = conf
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
            # than that passed to the current call.
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
                # the global trie configuring all top-level packages.
                subpackages_trie = packages_trie

                # For each unqualified basename comprising the directed path from
                # the root parent package of that package to that package...
                for package_basename in package_basenames:
                    # Current subtrie of that trie describing that parent package if
                    # that parent package was registered by a prior call to the
                    # hook_packages() function *OR* "None" (i.e., if that parent
                    # package has yet to be registered).
                    subpackages_subtrie = subpackages_trie.get(package_basename)

                    # If this is the first registration of that parent package,
                    # register a new subtrie describing that parent package.
                    #
                    # Note that this test could be obviated away by refactoring our
                    # "PackagesTrie" subclass from the "collections.defaultdict"
                    # superclass rather than the standard "dict" class. Since doing
                    # so would obscure erroneous attempts to access non-existing
                    # keys, however, this test is preferable to inviting even *MORE*
                    # bugs into this bug-riddled codebase. Just kidding! There are
                    # absolutely no bugs in this codebase. *wink*
                    if subpackages_subtrie is None:
                        subpackages_subtrie = \
                            subpackages_trie[package_basename] = \
                            PackagesTrie(package_basename=package_basename)
                    # Else, that parent package was already registered by a prior
                    # call to this function.

                    # Iterate the current subtrie one subpackage deeper.
                    subpackages_trie = subpackages_subtrie
                # Since the "package_basenames" list contains at least one basename,
                # the above iteration set the currently examined subdictionary
                # "subpackages_trie" to at least one subtrie of the global package
                # trie. Moreover, that subtrie is guaranteed to describe the current
                # (sub)package being registered.

                # Beartype configuration currently associated with that package by a
                # prior call to this function if any *OR* "None" (i.e., if that
                # package has yet to be registered by a prior call to this
                # function).
                conf_curr = subpackages_trie.conf_if_hooked

                # If that package has yet to be registered, associate this
                # configuration with that package.
                if conf_curr is None:
                    subpackages_trie.conf_if_hooked = conf
                # Else, that package was already registered by a previous call to
                # this function.
                #
                # If the caller passed a different configuration to that prior call
                # than that passed to this current call, raise an exception.
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
                # Else, the caller passed the same configuration to that prior call
                # than that passed to the current call. In this case, silently
                # ignore this redundant request to reregister that package.

        # Lastly, if our beartype import path hook singleton has *NOT* already
        # been added to the standard "sys.path_hooks" list, do so now.
        #
        # Note that we intentionally:
        # * Do so in a thread-safe manner *INSIDE* this lock.
        # * Defer doing so until *AFTER* the above iteration has successfully
        #   registered the desired packages with our global trie. Why? This path
        #   hook subsequently calls the companion get_package_conf_or_none()
        #   function, which accesses this trie.
        add_beartype_pathhook()


#FIXME: Unit test us up, please.
def unhook_packages(
    # Keyword-only arguments.
    *,

    # Mandatory keyword-only arguments.
    claw_coverage: BeartypeClawCoverage,
    conf: BeartypeConf,

    # Optional keyword-only arguments.
    package_name: Optional[str] = None,
    package_names: Optional[Iterable[str]] = None,
) -> None:
    '''
    Unregister a previously registered **beartype package import path hook**
    (i.e., callable inserted to the front of the standard :mod:`sys.path_hooks`
    list recursively applying the :func:`beartype.beartype` decorator to all
    typed callables and classes of all submodules of all packages with the
    passed names on the first importation of those submodules).

    See Also
    ----------
    :func:`.hook_packages`
        Further details.
    '''

    # Iterable of the passed fully-qualified names of all packages to be
    # unhooked.
    package_names = _get_package_names_from_args(
        claw_coverage=claw_coverage,
        conf=conf,
        package_name=package_name,
        package_names=package_names,
    )

    # With a submodule-specific thread-safe reentrant lock...
    with packages_trie_lock:
        # If the caller requested all-packages coverage...
        if claw_coverage is BeartypeClawCoverage.PACKAGES_ALL:
            # Unhook the beartype configuration previously associated with *ALL*
            # packages by a prior call to the beartype_all() function.
            packages_trie.conf_if_hooked = None
        # Else, the caller requested coverage over a subset of packages. In this
        # case...
        else:
            # For the fully-qualified names of each package to be
            # unregistered...
            for package_name in package_names:  # type: ignore[union-attr]
                # List of all subpackages tries describing each parent package
                # transitively containing the passed package (as well as that of
                # that package itself).
                subpackages_tries = list(iter_packages_trie(package_name))

                # Reverse this list in-place, such that:
                # * The first item of this list is the subpackages trie
                #   describing that package itself.
                # * The last item of this list is the subpackages trie
                #   describing the root package of that package.
                subpackages_tries.reverse()

                # Unhook the beartype configuration previously associated with
                # that package by a prior call to the hook_packages() function.
                subpackages_tries[0].conf_if_hooked = None

                # Child sub-subpackages trie of the currently iterated
                # subpackages trie, describing the child subpackage of the
                # current parent package transitively containing that package.
                subsubpackages_trie = None

                # For each subpackages trie describing a parent package
                # transitively containing that package...
                for subpackages_trie in subpackages_tries:
                    # If this is *NOT* the first iteration of this loop (in
                    # which case this subpackages trie is a parent package
                    # rather than that package itself) *AND*...
                    if subsubpackages_trie is not None:
                        # If this child sub-subpackages trie describing this
                        # child sub-subpackage has one or more children, then
                        # this child sub-subpackages trie still stores
                        # meaningful metadata and is thus *NOT* safely
                        # deletable. Moreover, this implies that:
                        # * *ALL* parent subpackages tries of this child
                        #   sub-subpackages trie also still store meaningful
                        #   metadata and are thus also *NOT* safely deletable.
                        # * There exists no more meaningful work to be performed
                        #   by this iteration. Ergo, we immediately halt this
                        #   iteration now.
                        if subsubpackages_trie:
                            break
                        # Else, this child sub-subpackages trie describing this
                        # child sub-subpackage has *NO* children, implying this
                        # child sub-subpackages trie no longer stores any
                        # meaningful metadata and is thus safely deletable.

                        # Unqualified basename of this child sub-subpackage.
                        subsubpackage_basename = (
                            subsubpackages_trie.package_basename)

                        # Delete this child sub-subpackages trie from this
                        # parent subpackages trie.
                        del subpackages_trie[subsubpackage_basename]
                    # Else, this is the first iteration of this loop.

                    # Treat this parent subpackages trie as the child
                    # sub-subpackages trie in the next iteration of this loop.
                    subsubpackages_trie = subpackages_trie

        # Lastly, if *ALL* meaningful metadata has now been removed from our
        # global trie, remove our beartype import path hook singleton from the
        # standard "sys.path_hooks" list.
        #
        # Note that we intentionally:
        # * Do so in a thread-safe manner *INSIDE* this lock.
        # * Defer doing so until *AFTER* the above iteration has successfully
        #   unregistered the desired packages with our global trie.
        remove_beartype_pathhook_unless_packages_trie()

# ....................{ PRIVATE ~ checkers                 }....................
#FIXME: Unit test us up, please.
def _get_package_names_from_args(
    # Keyword-only arguments.
    *,

    # Mandatory keyword-only arguments.
    claw_coverage: BeartypeClawCoverage,
    conf: BeartypeConf,

    # Optional keyword-only arguments.
    package_name: Optional[str] = None,
    package_names: Optional[Iterable[str]] = None,
) -> Optional[Iterable[str]]:
    '''
    Validate all parameters passed by the caller to the parent
    :func:`.hook_packages` or :func:`.unhook_packages` function.

    Returns
    ----------
    Optional[Iterable[str]]
        Iterable of the fully-qualified names of one or more packages to be
        either hooked or unhooked by the parent call.

    See Also
    ----------
    :func:`.hook_packages`
        Further details.
    '''

    # If the "conf" parameter is *NOT* a configuration, raise an exception.
    if not isinstance(conf, BeartypeConf):
        raise BeartypeClawRegistrationException(
            f'Beartype configuration {repr(conf)} invalid (i.e., not '
            f'"beartype.BeartypeConf" instance).'
        )
    # Else, the "conf" parameter is a configuration.

    # If the caller requested all-packages coverage...
    if claw_coverage is BeartypeClawCoverage.PACKAGES_ALL:
        # If the caller improperly passed a package name despite requesting
        # all-packages coverage, raise an exception.
        if package_name is not None:
            raise BeartypeClawRegistrationException(
                f'Coverage {repr(BeartypeClawCoverage.PACKAGES_ALL)} '
                f'but package name {repr(package_name)} passed.'
            )
        # Else, the caller properly passed *NO* package name.
        #
        # If the caller improperly passed multiple package names despite
        # requesting all-packages coverage, raise an exception.
        elif package_names is not None:
            raise BeartypeClawRegistrationException(
                f'Coverage {repr(BeartypeClawCoverage.PACKAGES_ALL)} '
                f'but package names {repr(package_names)} passed.'
            )
        # Else, the caller properly passed *NO* package names.
    # Else, the caller did *NOT* request all-packages coverage. In this case,
    # the caller requested coverage over only a subset of packages.
    else:
        # If the caller requested mono-package coverage...
        if claw_coverage is BeartypeClawCoverage.PACKAGES_ONE:
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

    # Return the iterable of the fully-qualified names of one or more packages
    # to be either hooked or unhooked by the parent call.
    return package_names
