#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2022 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype Decidedly Object-Oriented Runtime-checking (DOOR) API.**

This subpackage provides an object-oriented type hint class hierarchy,
encapsulating the crude non-object-oriented type hint declarative API
standardized by the :mod:`typing` module.
'''

# ....................{ TODO                               }....................
#FIXME: Publicly document everything in "README.rst", please. Notably:
#* List all public attributes of "beartype.door" in our "Feature" matrix.
#* This is a great first start on a cheat sheet-style synopsis:
#
#    # This is DOOR. It's a Pythonic API providing an object-oriented interface
#    # to low-level type hints that basically have no interface whatsoever.
#    >>> from beartype.door import TypeHint
#    >>> door_hint = TypeHint(int | str | None)
#    >>> print(door_hint)
#    TypeHint(int | str | None)
#
#    # DOOR hints have Pythonic classes -- unlike normal type hints.
#    >>> type(door_hint)
#    beartype.door.UnionTypeHint
#
#    # DOOR hints can be introspected Pythonically -- unlike normal type hints.
#    >>> from beartype.door import UnionTypeHint
#    >>> isinstance(door_hint, UnionTypeHint)
#    True
#
#    # DOOR hints can be iterated Pythonically -- unlike normal type hints.
#    >>> for door_child_hint in door_hint:
#    ...     print(door_child_hint)
#    TypeHint(<class 'int'>)
#    TypeHint(<class 'str'>)
#    TypeHint(<class 'NoneType'>)
#
#    # DOOR hints support equality Pythonically -- unlike normal type hints.
#    >>> from typing import Union
#    >>> door_hint == TypeHint(Union[int, str, None])
#    True  # <-- this is madness.
#
#    # DOOR hints support comparisons Pythonically -- unlike normal type hints.
#    >>> door_hint <= TypeHint(int | str | bool | None)
#    True  # <-- madness continues.
#
#    # DOOR hints are semantically self-caching.
#    >>> TypeHint(int | str | bool | None) is TypeHint(None | bool | str | int)
#    True  # <-- blowing minds over here.

#FIXME: Create one unique "TypeHint" subclass *FOR EACH UNIQUE KIND OF TYPE
#HINT.* We're currently simply reusing the same
#"_TypeHintOriginIsinstanceableArgs*" family of concrete subclasses to
#transparently handle these unique kinds of type hints. That's fine as an
#internal implementation convenience. Sadly, that's *NOT* fine for users
#actually trying to introspect types. That's the great disadvantage of standard
#"typing" types, after all; they're *NOT* introspectable by type. Ergo, we need
#to explicitly define subclasses like:
#* "beartype.door.ListTypeHint".
#* "beartype.door.MappingTypeHint".
#* "beartype.door.SequenceTypeHint".
#
#And so on. There are a plethora, but ultimately a finite plethora, which is all
#that matters. Do this for our wonderful userbase, please.

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To avoid polluting the public module namespace, external attributes
# should be locally imported at module scope *ONLY* under alternate private
# names (e.g., "from argparse import ArgumentParser as _ArgumentParser" rather
# than merely "from argparse import ArgumentParser").
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from beartype.door._doorcls import (
    TypeHint as TypeHint,
    ClassTypeHint as ClassTypeHint,
)
from beartype.door._doortest import (
    is_subhint as is_subhint,
)
from beartype.door._proposal.doorpep484604 import (
    UnionTypeHint as UnionTypeHint)
from beartype.door._proposal.doorpep586 import (
    LiteralTypeHint as LiteralTypeHint)
from beartype.door._proposal.doorpep593 import (
    AnnotatedTypeHint as AnnotatedTypeHint)
from beartype.door._proposal.pep484.doorpep484newtype import (
    NewTypeTypeHint as NewTypeTypeHint)
from beartype.door._proposal.pep484.doorpep484typevar import (
    TypeVarTypeHint as TypeVarTypeHint)
from beartype.door._proposal.pep484585.doorpep484585callable import (
    CallableTypeHint as CallableTypeHint)

#FIXME: Actually, let's *NOT* publicly expose this for the moment. Why? Because
#we still need to split this into fixed and variadic tuple subclasses.
# from beartype.door._proposal.pep484585.doorpep484585tuple import (
#     _TupleTypeHint as _TupleTypeHint)
