#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **frozen dictionary class hierarchy** (i.e., private classes
implementing immutable mappings, preserving :math:`O(1)` complexity while
prohibiting modification).
'''

# ....................{ TODO                               }....................
#FIXME: Hallelujah! "PEP 814 – Add frozendict built-in type" introduced with
#Python 3.15 obsoletes our bespoke "FrozenDict" defined below. Ergo:
#* Under Python >= 3.15, just trivially alias:
#      FrozenDict = frozendict
#* Under Python <= 3.14, conditionally preserve our existing implementation.

# ....................{ IMPORTS                            }....................
from beartype.roar import BeartypeKindFrozenDictException
from beartype._util.utilobject import get_object_type_basename
from collections.abc import Mapping
from typing import (
    TYPE_CHECKING,
    NoReturn,
    Optional,
    SupportsIndex,
)

# ....................{ CLASSES                            }....................
#FIXME: Consider attempting to generalize with type variables: e.g.,
#    class FrozenDict(dict[S, T]):
#In theory, that should help static type-checkers. In practice, they'll probably
#just complain about everything and be even more of a pain. We sigh. *sigh*
class FrozenDict(dict):
    '''
    **Frozen dictionary** (i.e., immutable mapping preserving :math:`O(1)`
    complexity while prohibiting modification).

    Instances of this dictionary are safely hashable and thus suitable for
    passing as parameters to memoized callables and classes (e.g., our core
    :class:`beartype.BeartypeConf` class).

    Parameters
    ----------
    _hash : Optional[int]
        Either:

        * If this dictionary is hashable, its hash.
        * Else, :data:`None`.

    See Also
    --------
    https://stackoverflow.com/q/1151658/2809027
        StackOverflow question lightly inspiring this implementation.
    '''

    # ..................{ CLASS VARIABLES                    }..................
    # Slot all instance variables defined on this object to minimize the time
    # complexity of both reading and writing variables across frequently called
    # @beartype decorations. Slotting has been shown to reduce read and write
    # costs by approximately ~10%, which is non-trivial.
    __slots__ = ('_hash',)

    # Squelch false negatives from mypy. This is absurd. This is mypy. See:
    #     https://github.com/python/mypy/issues/5941
    if TYPE_CHECKING:
        _hash: Optional[int]

    # ..................{ CLASS METHODS                      }..................
    @classmethod
    def fromkeys(cls, *args, **kwargs) -> 'FrozenDict':

        # Create and return a new immutable dictionary encapsulating the mutable
        # dictionary created and returned by the superclass method.
        #
        # Note that this implementation intentionally calls the dict.fromkeys()
        # class method directly rather than calling super().fromkey(). While
        # seemingly equivalent, the latter implicitly calls the __setitem__()
        # dunder method of this subclass, which then raises an exception.
        return cls(dict.fromkeys(*args, **kwargs))

    # ..................{ INITIALIZERS                       }..................
    def __init__(self, *args, **kwargs) -> None:

        # Instantiate this immutable dictionary with all passed parameters.
        super().__init__(*args, **kwargs)

        # Attempt to precompute the hash for this immutable dictionary at
        # instantiation time, for both efficiency and safety.
        try:
            frozen_items = frozenset(self.items())  # <-- clever stuff
            self._hash = hash(frozen_items)  # <---- more clever stuff
        # If instantiating the frozen set above raises a "TypeError", then one
        # or more passed values are unhashable. In this case, this frozen
        # dictionary will also be unhashable but otherwise usable as an
        # immutable container (e.g., to prohibit accidental modification).
        # Preserve this usability by nullifying this hash, which the __hash__()
        # dunder method subsequently detects and handles by raising a
        # human-readable exception.
        except TypeError:
            self._hash = None

    # ..................{ DUNDERS                            }..................
    def __hash__(self) -> int:  # type: ignore[override]
        '''
        Hash of all key-value pairs in this immutable dictionary.

        Defining this method satisfies the :class:`collections.abc.Hashable`
        abstract base class (ABC), enabling this dictionary to be used as in
        hashable containers (e.g., dictionaries, sets).

        Raises
        ------
        TypeError
            If one or more values of this dictionary are unhashable.
        '''

        # If this dictionary is unhashable, raise a human-readable exception.
        if self._hash is None:
            # Avoid circular import dependencies.
            from beartype._util.utilobject import is_object_hashable

            # For each value of this dictionary...
            #
            # Note that the keys of *ALL* dictionaries (both mutable and
            # immutable) are necessarily hashable and thus need *NOT* be
            # considered here.
            for value in self.values():
                # If this value is unhashable, raise an exception.
                if not is_object_hashable(value):
                    raise TypeError(
                        f'Frozen dictionary {repr(self)} '
                        f'value {repr(value)} unhashable.'
                    )

            # If the above iteration failed to raise an exception, do so anyway.
            # Note that this should *NEVER* occur. Thus we sigh.
            raise TypeError(f'Frozen dictionary {repr(self)} unhashable.')
        # Else, this dictionary is hashable.

        # Return the hash already precomputed by the __init__() method above.
        return self._hash


    def __reduce_ex__(self, protocol: SupportsIndex) -> (
        tuple[type, tuple[dict]]):
        '''
        Pickle this immutable dictionary.

        Parameters
        ----------
        protocol : SupportsIndex
            Pickle protocol under which to pickle this immutable dictionary.

        Returns
        -------
        Tuple[type, Tuple[dict]]
            2-tuple suitable for pickling this immutable dictionary.
        '''

        # Dark magic is both dark and magical.
        return (type(self), (dict(self),))


    def __repr__(self) -> str:
        '''
        Machine-readable representation of this immutable dictionary.
        '''

        # Standard "dict"-based representation of the mutable dictionary
        # encapsulated by this immutable dictionary.
        dict_repr = super().__repr__()

        # Fully-qualified name of the possible subclass of this dictionary.
        type_name = get_object_type_basename(self)

        # Return an appropriate representation of this immutable dictionary.
        return f'{type_name}({dict_repr})'


    def __or__(self, other: Mapping) -> 'FrozenDict':
        '''
        Create and return a new immutable dictionary containing all key-value
        pairs contained in both the current and passed immutable dictionaries.

        Parameters
        ----------
        other: Mapping
            Possibly mutable dictionary to be added to this immutable
            dictionary.

        Returns
        -------
        FrozenDict
            Immutable dictionary adding the current and passed dictionaries.

        Raises
        ------
        BeartypeKindFrozenDictException
            If the passed dictionary is *not* actually a dictionary.
        '''

        # If the passed dictionary is *NOT* a dictionary, raise an exception.
        if not isinstance(other, Mapping):
            raise BeartypeKindFrozenDictException(
                f'Non-dictionary {repr(other)} not addable to '
                f'immutable dictionary {repr(self)}.'
            )
        # Else, the passed dictionary is a dictionary.

        # Standard dictionary uniting this and the passed dictionaries, defined
        # by trivially deferring to the builtin dict.__or__() dunder method.
        dict_united: dict = super().__or__(dict(other))  # type: ignore[misc]

        # Type of immutable dictionary to be created and returned.
        cls = type(self)

        # Create and return a new immutable dictionary wrapping this dictionary.
        return cls(dict_united)

    # ..................{ MUTATORS                           }..................
    # Override all mutators (i.e., "dict" methods attempting to modify the
    # current immutable dictionary) to raise exceptions instead.
    def __setitem__(self, key, value) -> NoReturn:
        raise BeartypeKindFrozenDictException(
            f'Immutable dictionary {repr(self)} '
            f'key {repr(key)} not settable to {repr(value)}.'
        )


    def __delitem__(self, key) -> NoReturn:
        raise BeartypeKindFrozenDictException(
            f'Immutable dictionary {repr(self)} '
            f'key {repr(key)} not deletable.'
        )


    def clear(self) -> NoReturn:
        raise BeartypeKindFrozenDictException(
            f'Immutable dictionary {repr(self)} not clearable.')


    def pop(self, key, default = None) -> NoReturn:
        raise BeartypeKindFrozenDictException(
            f'Immutable dictionary {repr(self)} '
            f'key {repr(key)} with default {repr(default)} not poppable.'
        )


    def popitem(self) -> NoReturn:
        raise BeartypeKindFrozenDictException(
            f'Immutable dictionary {repr(self)} not poppable.')


    def setdefault(self, key, default = None) -> NoReturn:
        raise BeartypeKindFrozenDictException(
            f'Immutable dictionary {repr(self)} '
            f'key {repr(key)} with default {repr(default)} not settable.'
        )


    def update(self, *args, **kwargs) -> NoReturn:
        raise BeartypeKindFrozenDictException(
            f'Immutable dictionary {repr(self)} '
            f'not updatable from positional arguments {repr(args)} '
            f'and keyword arguments {repr(kwargs)}.'
        )
