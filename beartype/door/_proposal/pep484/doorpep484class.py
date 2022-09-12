#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2022 Beartype authors.
# See "LICENSE" for further details.

'''
**Decidedly Object-Oriented Runtime-checking (DOOR) class type hint classes**
(i.e., :class:`beartype.door.TypeHint` subclasses implementing support
for :pep:`484`-compliant type hints that are, in fact, simple classes).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.door._doorcls import TypeHint
from beartype.typing import Any

# ....................{ SUBCLASSES                         }....................
class ClassTypeHint(TypeHint):
    '''
    **Class type hint wrapper** (i.e., high-level object encapsulating a
    low-level :pep:`484`-compliant type hint that is, in fact, a simple class).

    Caveats
    ----------
    This wrapper also intentionally wraps :pep:`484`-compliant ``None`` type
    hints as the simple type of the ``None`` singleton, as :pep:`484`
    standardized the reduction of the former to the latter:

         When used in a type hint, the expression None is considered equivalent
         to type(None).

    Although a unique ``NoneTypeHint`` subclass of this class specific to the
    ``None`` singleton *could* be declared, doing so is substantially
    complicated by the fact that numerous PEP-compliant type hints internally
    elide ``None`` to the type of that singleton before the `beartype.door` API
    ever sees a distinction. Notably, this includes :pep:`484`-compliant unions
    subscripted by that singleton: e.g.,

    .. code-block

       >>> from typing import Union
       >>> Union[str, None].__args__
       (str, NoneType)
    '''

    # ..................{ PRIVATE                            }..................
    #FIXME: Kinda awkward. We get it, bet let's *NOT* define class variables
    #just to satisfy the pernicious desires of static type-checkers. Gah! Now
    #that we have a hint() property, this would substantially preferable:
    #    @property
    #    def hint(self) -> type:
    #        return self._hint
    _hint: type

    # ..................{ PROPERTIES                         }..................
    @property
    def _is_args_ignorable(self) -> bool:
        '''
        Plain types are their origin.
        '''

        return True

    # ..................{ METHODS                            }..................
    def _is_le_branch(self, branch: TypeHint) -> bool:

        # Everything is a subclass of "Any".
        if branch._origin is Any:
            return True
        # "Any" is only a subclass of "Any". Furthermore, "Any" is unsuitable as
        # the first argument to issubclass() below.
        elif self._origin is Any:
            return False

        #FIXME: Actually, let's avoid the implicit numeric tower for now.
        #Explicit is better than implicit and we really strongly disagree with
        #this subsection of PEP 484, which does more real-world harm than good.
        # # Numeric tower:
        # # https://peps.python.org/pep-0484/#the-numeric-tower
        # if self._origin is float and branch._origin in {float, int}:
        #     return True
        # if self._origin is complex and branch._origin in {complex, float, int}:
        #     return True

        # Return true only if...
        return branch._is_args_ignorable and issubclass(
            self._origin, branch._origin)
