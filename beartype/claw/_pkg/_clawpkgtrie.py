#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype package configuration trie.**

This private submodule caches package names on behalf of the higher-level
:func:`beartype.claw.beartype_package` function. Beartype import
path hooks internally created by that function subsequently lookup these package
names from this cache when deciding whether or not (and how) to decorate a
submodule being imported with :func:`beartype.beartype`.

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.typing import (
    Dict,
    Optional,
)
from beartype._conf.confcls import BeartypeConf

# ....................{ CLASSES                            }....................
#FIXME: Unit test us up, please.
class PackageBasenameToSubpackages(
    #FIXME: Use "beartype.typing.Self" here instead once we backport that.
    Dict[str, Optional['PackageBasenameToSubpackages']]):
    '''
    **(Sub)package configuration (sub)trie** (i.e., recursively nested
    dictionary mapping from the unqualified basename of each subpackage of the
    current package to be runtime type-checked on the first importation of that
    subpackage to another instance of this class similarly describing the
    sub-subpackages of that subpackage).

    This (sub)cache is suitable for caching as the values of:

    * The :data:`.package_basename_to_subpackages` global dictionary.
    * Each (sub)value mapped to by that global dictionary.

    Attributes
    ----------
    conf_if_added : Optional[BeartypeConf]
        Either:

        * If this (sub)package has been explicitly registered by a prior call to
          the :func:`add_package_names` function, the **beartype
          configuration** (i.e., dataclass encapsulating all settings
          configuring type-checking for this (sub)package).
        * Else, :data:`None`.
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
        'conf_if_added',
    )

    # ..................{ INITIALIZERS                       }..................
    def __init__(self, *args, **kwargs) -> None:
        '''
        Initialize this package name (sub)cache.

        All passed parameters are passed as is to the superclass
        :meth:`dict.__init__` method.
        '''

        # Initialize our superclass with all passed parameters.
        super().__init__(*args, **kwargs)

        #FIXME: Rename "conf_if_added" to "conf_if_added", please.
        # Nullify all subclass-specific parameters for safety.
        self.conf_if_added: Optional[BeartypeConf] = None

# ....................{ GLOBALS                            }....................
#FIXME: Revise docstring in accordance with data structure changes, please.
#Everything scans up until "...either the :data:`None` singleton if that
#subpackage is to be type-checked." Is that *REALLY* how this works? *sigh*
package_basename_to_subpackages = PackageBasenameToSubpackages()
'''
**Package configuration trie** (i.e., non-thread-safe dictionary implementing a
prefix tree such that each key-value pair maps from the unqualified basename of
each subpackage to be possibly type-checked on the first importation of that
subpackage to either the :data:`None` singleton if that subpackage is to be
type-checked *or* a nested dictionary satisfying the same structure otherwise
(i.e., if that subpackage is *not* to be type-checked)).

Motivation
----------
This dictionary is intentionally implemented as a nested trie data structure
rather than a trivial non-nested flat dictionary. Why? Efficiency. Consider this
flattened set of package names:

    .. code-block:: python

       _package_names = {'a.b', 'a.c', 'd'}

Deciding whether an arbitrary package name is in this set requires worst-case
``O(n)`` iteration across the set of ``n`` package names.

Consider instead this nested dictionary whose keys are package names split on
``"."`` delimiters and whose values are either recursively nested dictionaries
of the same format *or* the :data:`None` singleton (terminating the current
package name):

    .. code-block:: python

       _package_basename_to_subpackages = {
           'a': {'b': None, 'c': None}, 'd': None}

Deciding whether an arbitrary package name is in this dictionary only requires
worst-case ``O(h)`` iteration across the height ``h`` of this dictionary
(equivalent to the largest number of ``"."`` delimiters for any fully-qualified
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
``with _claw_lock:`` **context manager.** Equivalently, this global is *not*
safely accessible outside that manager.

Examples
----------
Instance of this data structure type-checking on import submodules of the root
``package_z`` package, the child ``package_a.subpackage_k`` submodule, and the
``package_a.subpackage_b.subpackage_c`` and
``package_a.subpackage_b.subpackage_d`` submodules:

    >>> _package_basename_to_subpackages = _PackageBasenameToSubpackages({
    ...     'package_a': _PackageBasenameToSubpackages({
    ...         'subpackage_b': _PackageBasenameToSubpackages({
    ...             'subpackage_c': None,
    ...             'subpackage_d': None,
    ...         }),
    ...         'subpackage_k': None,
    ...     }),
    ...     'package_z': None,
    ... })
'''
