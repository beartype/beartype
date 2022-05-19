#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2022 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype all-at-once low-level package name cache.**

This private submodule caches package names on behalf of the higher-level
:func:`beartype.claw.beartype_submodules_on_import` function. Beartype import
path hooks internally created by that function subsequently lookup these package
names from this cache when deciding whether or not (and how) to decorate a
submodule being imported with :func:`beartype.beartype`.

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.roar import BeartypeClawRegistrationException
from beartype.typing import (
    Dict,
    Iterable,
    Optional,
)
from beartype._conf import BeartypeConf
from beartype._util.text.utiltextident import is_identifier
from collections.abc import Iterable as IterableABC
from threading import RLock

# See the "beartype.cave" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ REGISTRARS                         }....................
#FIXME: Unit test us up, please.
#FIXME: Define a comparable removal function named either:
#* cancel_beartype_submodules_on_import(). This is ostensibly the most
#  unambiguous and thus the best choice of those listed here. Obviously,
#  beartype_submodules_on_import_cancel() is a comparable alternative.
#* forget_beartype_on_import().
#* no_beartype_on_import().
def register_package_names(
    # Mandatory keyword-only parameters.
    *,
    package_names: Iterable[str],
    conf: BeartypeConf,
) -> None:
    '''
    Register the packages with the passed names as subject to our **beartype
    import path hook** (i.e., callable inserted to the front of the standard
    :mod:`sys.path_hooks` list recursively applying the
    :func:`beartype.beartype` decorator to all well-typed callables and classes
    defined by all submodules of all packages with the passed names on the first
    importation of those submodules).

    Parameters
    ----------
    package_names : Optional[Iterable[str]]
        Iterable of the fully-qualified names of one or more packages to be
        type-checked by :func:`beartype.beartype`.
    conf : BeartypeConf, optional
        **Beartype configuration** (i.e., self-caching dataclass encapsulating
        all settings configuring type-checking for the passed packages).

    Raises
    ----------
    BeartypeClawRegistrationException
        If either:

        * The passed ``package_names`` parameter is either:

          * *Not* iterable (i.e., fails to satisfy the
            :class:`collections.abc.Iterable` protocol).
          * An empty iterable.
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
    #
    # If this iterable of package names is *NOT* an iterable, raise an
    # exception.
    elif not isinstance(package_names, IterableABC):
        raise BeartypeClawRegistrationException(
            f'Package names {repr(package_names)} not iterable.')
    # Else, this iterable of package names is an iterable.
    #
    # If this iterable of package names is empty, raise an exception.
    elif not package_names:
        raise BeartypeClawRegistrationException('Package names empty.')
    # Else, this iterable of package names is non-empty.

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
                f'Package name "{package_name}" invalid (i.e., not '
                f'"."-delimited Python identifier).'
            )
        # Else, this package name is a valid Python identifier.

    # ..................{ REGISTRATION                       }..................
    # With a submodule-specific thread-safe reentrant lock...
    with _globals_lock:
        # For the fully-qualified name of each package to be registered...
        for package_name in package_names:
            # List of each unqualified basename comprising this name, split from
            # this fully-qualified name on "." delimiters.
            package_basenames = package_name.split('.')

            #FIXME: Implement us up, please. Doing so will require...

# ....................{ PRIVATE ~ classes                  }....................
#FIXME: Docstring us up, please.
class _PackageBasenameToSubpackagesDict(
    Dict[str, Optional['_PackageBasenameToSubpackagesDict']]):
    '''
    **Package name cache value** (i.e., object suitable for caching as a value
    of the :data:`_package_basename_to_subpackages` package names cache,
    associating the unqualified basename of a parent package with the
    unqualified basename of each subpackage to be possibly type-checked on first
    importation by :func:`beartype.beartype`) class.

    Attributes
    ----------
    conf_if_registered : Optional[BeartypeConf]
        Either:

        * If this (sub)package has been explicitly registered by a prior call to
          the :func:`register_package_names` function, the **beartype
          configuration** (i.e., self-caching dataclass encapsulating
          all settings configuring type-checking for this (sub)package).
        * Else, ``None``.
    '''

    # ..................{ CLASS VARIABLES                    }..................
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # CAUTION: Subclasses declaring uniquely subclass-specific instance
    # variables *MUST* additionally slot those variables. Subclasses violating
    # this constraint will be usable but unslotted, which defeats our purposes.
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # Slot all instance variables defined on this object to minimize the time
    # complexity of both reading and writing variables across frequently called
    # cache dunder methods. Slotting has been shown to reduce read and write
    # costs by approximately ~10%, which is non-trivial.
    __slots__ = (
        'conf_if_registered',
    )

# ....................{ PRIVATE ~ globals                  }....................
#FIXME: Revise docstring in accordance with data structure changes, please.
_package_basename_to_subpackages = _PackageBasenameToSubpackagesDict()
'''
**Package name cache** (i.e., non-thread-safe dictionary mapping in a
recursively nested manner from the unqualified basename of each subpackage to be
possibly type-checked on first importation by the :func:`beartype.beartype`
decorator to either the ``None`` singleton if that subpackage is to be
type-checked *or* a nested dictionary satisfying the same structure otherwise
(i.e., if that subpackage is *not* to be type-checked)).

Motivation
----------
This dictionary is intentionally structured as a non-trivial nested data
structure rather than a trivial non-nested flat dictionary. Why? Efficiency.
Consider this flattened set of package names:

    .. code-block:: python

       _package_names = {'a.b', 'a.c', 'd'}

Deciding whether an arbitrary package name is in that set or not requires
worst-case ``O(n)`` iteration across the set of ``n`` package names.

Consider instead this nested dictionary whose keys are package names split on
``.`` delimiters and whose values are either recursively nested dictionaries of
the same format *or* the ``None`` singleton (terminating the current package
name):

    .. code-block:: python

       _package_basename_to_subpackages = {
           'a': {'b': None, 'c': None}, 'd': None}

Deciding whether an arbitrary package name is in this dictionary or not requires
worst-case ``O(h)`` iteration across the height ``h`` of this dictionary
(equivalent to the largest number of ``.`` delimiters for any fully-qualified
package name encapsulated by this dictionary). Since ``h <<<<<<<<<< n``, this
dictionary provides substantially faster worst-case lookup than that set.

Moreover, in the worst case:

* That set requires one inefficient string prefix test for each item.
* This dictionary requires *only* one efficient string equality test for each
  nested key-value pair while descending towards the target package name.

Let's do this, fam.

Caveats
----------
**This global is only safely accessible in a thread-safe manner from within a**
``with _globals_lock:`` **context manager.** Ergo, this global is *not* safely
accessible outside that context manager.

Examples
----------
Instance of this data structure type-checking on import submodules of the root
``package_z`` package, the child ``package_a.subpackage_k`` submodule, and the
``package_a.subpackage_b.subpackage_c`` and
``package_a.subpackage_b.subpackage_d`` submodules:

    >>> _package_basename_to_subpackages = {
    ...     'package_a': {
    ...         'subpackage_b': {
    ...             'subpackage_c': None,
    ...             'subpackage_d': None,
    ...         },
    ...         'subpackage_k': None,
    ...     },
    ...     'package_z': None,
    ... }
'''

# ....................{ PRIVATE ~ globals : threading      }....................
_globals_lock = RLock()
'''
Reentrant reusable thread-safe context manager gating access to otherwise
non-thread-safe private globals defined by this submodule (e.g.,
:data:`_package_basename_to_subpackages`).
'''
