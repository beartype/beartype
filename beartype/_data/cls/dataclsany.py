#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **any analog class hierarchy** defining runtime-friendly types that
are syntactically distinct from yet semantically analogous to:

* The builtin runtime-friendly root :class:`object` superclass.
* The standard runtime-hostile :class:`typing.Any` type hint singleton.

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from typing import Literal

# ....................{ METACLASSES                        }....................
class _BeartypeAnyMeta(type):
    '''
    Metaclass of the :class:`._BeartypeAny` type.
    '''

    def __instancecheck__(cls: 'BeartypeAny', obj: object) -> Literal[True]:  # type: ignore[misc]
        '''
        Guarantee that ``isinstance({{obj}}, BeartypeAny) is True`` for all
        possible objects ``{{obj}}`` by unconditionally returning :data:`True`.

        Parameters
        ----------
        cls : BeartypeAny
            :class:`.BeartypeAny` class whose metaclass is this metaclass.
        obj : object
            Arbitrary object to be tested as an instance of
            :class:`.BeartypeAny`.

        Returns
        -------
        Literal[True]
            Unconditionally :data:`True`.
        '''

        return True  # <-- lol


    def __subclasscheck__(cls: 'BeartypeAny', subclass: type) -> Literal[True]:  # type: ignore[misc]
        '''
        Guarantee that ``issubclass({{obj}}, BeartypeAny) is True`` for all
        possible types ``{{obj}}`` by unconditionally returning :data:`True`.

        Equivalently, this dunder method returns :data:`True` only when the
        passed object is a type.

        Parameters
        ----------
        cls : BeartypeAny
            :class:`.BeartypeAny` class whose metaclass is this metaclass.
        subclass : type
            Arbitrary type to be tested as a subclass of :class:`.BeartypeAny`.

        Returns
        -------
        Literal[True]
            If the passed object is a type.

        Raises
        ------
        TypeError
            If the passed object is *not* a type.
        '''

        # Return true if the passed object is a type *OR* raise the standard
        # "TypeError" exception expected to be raised by the issubclass()
        # builtin in this common edge case otherwise. To do so trivially, just
        # masquerade as the root "object" superclass. *shrug*
        return issubclass(subclass, object)  # type: ignore[return-value]

# ....................{ CLASSES                            }....................
#FIXME: Unit test us up, please. *sigh*
class BeartypeAny(object, metaclass=_BeartypeAnyMeta):
    '''
    :mod:`beartype`-specific **any analog**, a runtime-friendly isinstanceable
    type that is syntactically distinct from yet semantically analogous to:

    * The builtin runtime-friendly root :class:`object` superclass.
    * The standard runtime-hostile :class:`typing.Any` type hint singleton.

    Caveats
    -------
    **The builtin root** :class:`object` **superclass is more efficient than and
    thus preferable to this heavier-weight pure-Python analog.** This
    pure-Python analog should only be used where using :class:`object` instead
    would invite issues (e.g., ambiguities).
    '''

    pass
