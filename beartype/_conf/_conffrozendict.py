#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype frozen dict, used to memoize configuration options such as
hint_overrides.
'''

class _BeartypeFrozenDict(dict):
    '''
    **Frozen dictionary** (i.e., immutable mapping preserving :math:`O(1)`
    complexity while prohibiting modification).

    Instances of this dictionary are safely hashable and thus suitable for
    passing as parameters to memoized callables and classes (e.g., our core
    :class:`beartype.BeartypeConf` class).
    '''

    __slots__ = ('_hash',)  # <-- preserve space efficiency. curse you, Python!

    def __init__(self, *args, **kwargs) -> None:

        # Instantiate this immutable dictionary with all passed parameters.
        super().__init__(*args, **kwargs)

        # Precompute the hash for this immutable dictionary at instantiation
        # time for both efficiency and safety.
        frozen_items = frozenset(self.items())  # <-- clever stuff
        self._hash = hash(frozen_items)  # <---- more clever stuff


    def __hash__(self) -> int:
        return self._hash


    def __setitem__(self, key, value) -> None:
        raise NotImplementedError(
            f'Immutable dictionary {repr(self)}" '
            f'key {repr(key)} not settable to {repr(value)}.'
        )
