#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2022 Beartype authors.
# See "LICENSE" for further details.

'''
**Decidedly Object-Oriented Runtime-checking (DOOR) new-type type hint classes**
(i.e., :class:`beartype.door.TypeHint` subclasses implementing support
for :pep:`484`-compliant :attr:`typing.NewType` type hints).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.door._proposal.pep484.doorpep484class import ClassTypeHint
from beartype._util.hint.pep.proposal.pep484.utilpep484newtype import (
    get_hint_pep484_newtype_class)

# ....................{ SUBCLASSES                         }....................
class NewTypeTypeHint(ClassTypeHint):
    '''
    **New-type type hint wrapper** (i.e., high-level object encapsulating a
    low-level :pep:`484`-compliant :attr:`typing.NewType` type hint).
    '''

    # ..................{ INITIALIZERS                       }..................
    def __init__(self, hint: object) -> None:

        super().__init__(hint)

        supertype = get_hint_pep484_newtype_class(hint)

        # We want to "create" an origin for this NewType that treats the newtype
        # as a subclass of its supertype. For example, if the hint is
        # "NewType("MyType", str)", then the origin should be
        # "class MyString(str): pass".
        try:
            # We create a literal subclass here, which would be non-ideal due to
            # explosive space and time consumption. Thankfully, however,
            # "TypeHint" wrappers are cached. Ergo, this subclass should only be
            # created and cached once per new-type.
            name = getattr(hint, '__name__', str(hint))
            self._origin = type(name, (supertype,), {})
        # Not all types are subclassable (e.g., "Any").
        except TypeError:
            self._origin = supertype
