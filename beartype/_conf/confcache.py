#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype **configuration cache** (i.e., private dictionary singletons enabling
beartype configurations to be efficiently stored and retrieved based on various
criteria, including both by configuration parameters and object identifiers).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.roar import BeartypeClawImportConfException
from beartype.typing import (
    TYPE_CHECKING,
    Dict,
)
from pprint import pformat
from threading import Lock

# If we are currently being statically type-checked rather than run at runtime,
# explicitly notify the current static type-checker of the absolute locations of
# attributes referenced by fully-qualified forward references below. *rollseyes*
if TYPE_CHECKING:
    from beartype import BeartypeConf
# Else, avoid importing the "BeartypeConf" class. Why? Because doing so would
# cause a circular import dependency. *facepalm*

# ....................{ LOCKS                              }....................
beartype_conf_lock = Lock()
'''
**Non-reentrant beartype configuration thread lock** (i.e., low-level thread
locking mechanism implemented as a highly efficient C extension, defined as an
global for non-reentrant reuse elsewhere as a context manager).
'''

# ....................{ PRIVATE ~ classes                  }....................
class _BeartypeConfIdToConf(Dict[int, 'BeartypeConf']):
    '''
    Non-thread-safe **beartype configuration identifier cache** (i.e.,
    dictionary mapping from the object identifier returned by the :func:`id`
    builtin for each unique :class:`BeartypeConf` instance instantiated by a
    prior call of the :meth:`BeartypeConf.__new__` instantiator to that
    instance) dictionary subclass.

    This dictionary subclass improves the human readability of exceptions raised
    by dunder methods of the :class:`dict` superclass (e.g., the
    :meth:`dict.__getitem__` dunder method), whose C-based implementations
    raise non-human-readable exceptions in common use cases encountered by end
    users leveraging beartype import hooks: e.g.,

    .. code-block:: python

        # Otherwise syntactically and semantically correct PEP 562-compliant
        # annotated assignment expressions like this previously raised spurious
        # non-human-readable exceptions from this dictionary resembling:
        #     KeyError: 139812262578032  # <-- what does this even mean!?!?
        loves_philosophy: float = len('The fountains mingle with the river')
    '''

    # ....................{ DUNDERS                        }....................
    def __getitem__(self, beartype_conf_id: int) -> 'BeartypeConf':
        '''
        Return the previously instantiated beartype configuration with the
        passed object identifier.

        Parameters
        ----------
        beartype_conf_id : int
            Object identifier of the beartype configuration to be returned.

        Returns
        ----------
        beartype.BeartypeConf
            Beartype configuration with this object identifier.

        Raises
        ----------
        BeartypeClawImportConfException
            If no beartype configuration with this object identifier has been
            previously instantiated.
        '''

        # Attempt to defer to the superclass implementation.
        try:
            return super().__getitem__(beartype_conf_id)
        # If doing so fails with a low-level non-human-readable exception, raise
        # high-level human-readable exception wrapping that exception instead.
        except KeyError as exception:
            raise BeartypeClawImportConfException(
                f'Beartype configuration with object ID '
                f'{beartype_conf_id} not found. Previously instantiated '
                f'beartype configurations include:\n{pformat(self)}'
            ) from exception

# ....................{ DICTIONARIES                       }....................
beartype_conf_args_to_conf: Dict[tuple, 'BeartypeConf'] = {}
'''
Non-thread-safe **beartype configuration parameter cache** (i.e., dictionary
mapping from the hash of each set of parameters accepted by a prior call of the
:meth:`BeartypeConf.__new__` instantiator to the unique :class:`BeartypeConf`
instance instantiated by that call).

Caveats
----------
**This cache is non-thread-safe.** However, since this cache is only used as a
memoization optimization, the only harmful consequences of a race condition
between threads contending over this cache is a mildly inefficient (but
otherwise harmless) repeated re-memoization of duplicate configurations.
'''


beartype_conf_id_to_conf = _BeartypeConfIdToConf()
'''
Non-thread-safe **beartype configuration identifier cache** (i.e., dictionary
mapping from the object identifier returned by the :func:`id` builtin for each
unique :class:`BeartypeConf` instance instantiated by a prior call of the
:meth:`BeartypeConf.__new__` instantiator to that instance).

Caveats
----------
**This cache is non-thread-safe.** The caller is responsible for guaranteeing
thread-safety on writes to this cache. However, Note that reads of this cache
are implicitly thread-safe. The :meth:`BeartypeConf.__new__` instantiator
thread-safely stores strong references to the currently instantiated beartype
configuration in both this and other caches. Since these caches and thus *all*
configurations persist for the lifetime of the active Python interpreter, reads
are effectively thread-safe.
'''
