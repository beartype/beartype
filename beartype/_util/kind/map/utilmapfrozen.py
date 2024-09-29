#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2024 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **frozen dictionary class hierarchy** (i.e., private classes
implementing immutable mappings, preserving :math:`O(1)` complexity while
prohibiting modification).
'''

# ....................{ IMPORTS                            }....................
from collections.abc import Mapping

from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_9
from beartype._util.utilobject import get_object_type_basename
from beartype.roar import BeartypeKindFrozenDictException
from beartype.typing import (
    NoReturn,
    SupportsIndex,
    Tuple,
)

# ....................{ CLASSES                            }....................
# FIXME: Unit test us up, please.
class FrozenDict(dict):
    '''
    **Frozen dictionary** (i.e., immutable mapping preserving :math:`O(1)`
    complexity while prohibiting modification).

    Instances of this dictionary are safely hashable and thus suitable for
    passing as parameters to memoized callables and classes (e.g., our core
    :class:`beartype.BeartypeConf` class).

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

        # Precompute the hash for this immutable dictionary at instantiation
        # time for both efficiency and safety.
        frozen_items = frozenset(self.items())  # <-- clever stuff
        self._hash = hash(frozen_items)  # <---- more clever stuff

    # ..................{ DUNDERS                            }..................
    def __hash__(self) -> int:  # type: ignore[override]
        '''
        Hash of all key-value pairs in this immutable dictionary.

        Defining this method satisfies the :class:`collections.abc.Hashable`
        abstract base class (ABC), enabling this dictionary to be used as in
        hashable containers (e.g., dictionaries, sets).
        '''

        # Return the precomputed hash for this immutable dictionary.
        return self._hash

    def __reduce_ex__(self, protocol: SupportsIndex) -> Tuple[type, object]:
        '''
        Pickle this immutable dictionary.

        Parameters
        ----------
        protocol : SupportsIndex
            Pickle protocol under which to pickle this immutable dictionary.

        Returns
        -------
        Tuple[type, object]
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
            msg = (
                f'Non-dictionary {other!r} not addable to '
                f'immutable dictionary {self!r}.'
            )
            raise BeartypeKindFrozenDictException(
                msg
            )
        # Else, the passed dictionary is a dictionary.

        # Type of immutable dictionary to be created and returned.
        cls = type(self)

        # Standard dictionary uniting this and the passed dictionaries.
        dict_united: dict = None  # type: ignore[assignment]

        # If the active Python interpreter targets Python >= 3.9, the standard
        # "dict" class defines the __or__() dunder method. In this case...
        if IS_PYTHON_AT_LEAST_3_9:
            # Trivially defer to that method to implement this method.
            dict_united = super().__or__(dict(other))  # type: ignore[misc]
        # Else, the active Python interpreter targets Python 3.8. In this case,
        # implement this operation manually via a dictionary merger.
        else:
            # Mutable dictionary uniting these two immutable dictionaries,
            # initialized to the contents of the current immutable dictionary.
            dict_united = dict(self)

            # For each key-value pair in the passed immutable dictionary...
            for other_key, other_value in other.items():
                # Add this key-value pair to this mutable dictionary.
                dict_united[other_key] = other_value

        # Create and return a new immutable dictionary wrapping this dictionary.
        return cls(dict_united)

    # ..................{ MUTATORS                           }..................
    # Override all mutators (i.e., "dict" methods attempting to modify the
    # current immutable dictionary) to raise exceptions instead.
    def __setitem__(self, key, value) -> NoReturn:
        msg = (
            f'Immutable dictionary {self!r} '
            f'key {key!r} not settable to {value!r}.'
        )
        raise BeartypeKindFrozenDictException(
            msg
        )

    def __delitem__(self, key) -> NoReturn:
        msg = (
            f'Immutable dictionary {self!r} '
            f'key {key!r} not deletable.'
        )
        raise BeartypeKindFrozenDictException(
            msg
        )

    def clear(self) -> NoReturn:
        msg = f'Immutable dictionary {self!r} not clearable.'
        raise BeartypeKindFrozenDictException(
            msg)

    def pop(self, key, default=None) -> NoReturn:
        msg = (
            f'Immutable dictionary {self!r} '
            f'key {key!r} with default {default!r} not poppable.'
        )
        raise BeartypeKindFrozenDictException(
            msg
        )

    def popitem(self) -> NoReturn:
        msg = f'Immutable dictionary {self!r} not poppable.'
        raise BeartypeKindFrozenDictException(
            msg)

    def setdefault(self, key, default=None) -> NoReturn:
        msg = (
            f'Immutable dictionary {self!r} '
            f'key {key!r} with default {default!r} not settable.'
        )
        raise BeartypeKindFrozenDictException(
            msg
        )

    def update(self, *args, **kwargs) -> NoReturn:
        msg = (
            f'Immutable dictionary {self!r} '
            f'not updatable from positional arguments {args!r} '
            f'and keyword arguments {kwargs!r}.'
        )
        raise BeartypeKindFrozenDictException(
            msg
        )
