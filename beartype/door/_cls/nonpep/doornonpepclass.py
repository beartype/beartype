#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype **Decidedly Object-Oriented Runtime-checking (DOOR) class type hint
classes** (i.e., :class:`beartype.door.TypeHint` subclasses implementing support
for PEP-noncompliant isinstanceable types).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.door._cls.pep.pep484.doorpep484unsubbed import (
    UnsubscriptedTypeHint)
from typing import TYPE_CHECKING

# ....................{ SUBCLASSES                         }....................
class ClassTypeHint(UnsubscriptedTypeHint):
    '''
    **Class type hint wrapper** (i.e., high-level object encapsulating a
    low-level PEP-noncompliant **isinstanceable type** (i.e., permissible for
    use as the second argument to the builtin :class:`isinstance` function)
    that, due to being PEP-noncompliant, is also unsubscripted by definition).

    Caveats
    -------
    This wrapper also intentionally wraps :pep:`484`-compliant :data:``None`
    type hints as the simple type of the :data:``None` singleton, as :pep:`484`
    standardized the reduction of the former to the latter:

         When used in a type hint, the expression None is considered equivalent
         to type(None).

    Although a unique ``NoneTypeHint`` subclass of this class specific to the
    :data:`None` singleton *could* be declared, doing so is substantially
    complicated by the fact that numerous PEP-compliant type hints internally
    elide :data:`None` to the type of that singleton before the
    :mod:`beartype.door` API ever sees a distinction. Notably, this includes
    :pep:`484`-compliant unions subscripted by that singleton: e.g.,

    .. code-block:: python

       >>> from typing import Union
       >>> Union[str, None].__args__
       (str, NoneType)
    '''

    # ..................{ STATIC                             }..................
    # Squelch false negatives from static type checkers.
    if TYPE_CHECKING:
        _hint: type
