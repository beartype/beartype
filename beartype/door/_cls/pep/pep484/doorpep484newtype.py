#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
**Decidedly Object-Oriented Runtime-checking (DOOR) new-type type hint classes**
(i.e., :class:`beartype.door.TypeHint` subclasses implementing support
for :pep:`484`-compliant :attr:`typing.NewType` type hints).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.door._cls.pep.pep484.doorpep484class import ClassTypeHint
from beartype._util.hint.pep.proposal.pep484.utilpep484newtype import (
    get_hint_pep484_newtype_alias)

# ....................{ SUBCLASSES                         }....................
class NewTypeTypeHint(ClassTypeHint):
    '''
    **New-type type hint wrapper** (i.e., high-level object encapsulating a
    low-level :pep:`484`-compliant :attr:`typing.NewType` type hint).
    '''

    # ..................{ INITIALIZERS                       }..................
    def __init__(self, hint: object) -> None:

        # Initialize the superclass with all passed parameters.
        super().__init__(hint)

        # User-defined class aliased by this "NewType" type hint.
        newtype_class = get_hint_pep484_newtype_alias(hint)

        # We want to "create" an origin for this NewType that treats the newtype
        # as a subclass of its supertype. For example, if the hint is
        # "NewType("MyType", str)", then the origin should be
        # "class MyString(str): pass".
        try:
            #FIXME: Define a new get_hint_pep484_newtype_name() getter ala:
            #    def get_hint_pep484_newtype_name(
            #        hint: Any, exception_prefix: str = '') -> type:
            #        #FIXME: Does this suffice? Does "NewType" guarantee the
            #        #"__name__" instance variable to exist? No idea. *sigh*
            #        return getattr(hint, '__name__')
            #Then, call that below in lieu of the "name = getattr(...)" call.

            # Dynamically synthesize a new subclass.
            #
            # Note that this would typically be non-ideal due to explosive space
            # and time consumption. Thankfully, however, "TypeHint" wrappers are
            # cached; the "_TypeHintMeta" metaclass guarantees this __init__()
            # method to be called exactly once for each "NewType" type hint.
            name = getattr(hint, '__name__', str(hint))
            self._origin = type(name, (newtype_class,), {})
        # Not all types are subclassable (e.g., "Any").
        except TypeError:
            self._origin = newtype_class
