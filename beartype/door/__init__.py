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
#* Globally replace "beartype.abby" with "beartype.door" in "README.rst", too.
#* This is a great first start on a cheat sheet-style synopsis:
#
#    # This is DOOR. It's a Pythonic API providing an object-oriented interface
#    # to low-level type hints that basically have no interface whatsoever.
#    >>> from beartype.door import TypeHint
#    >>> union_hint = TypeHint(int | str | None)
#    >>> print(union_hint)
#    TypeHint(int | str | None)
#
#    # DOOR hints have Pythonic classes -- unlike normal type hints.
#    >>> type(union_hint)
#    beartype.door.UnionTypeHint  # <-- what madness is this?
#
#    # DOOR hints can be classified Pythonically -- unlike normal type hints.
#    >>> from beartype.door import UnionTypeHint
#    >>> isinstance(union_hint, UnionTypeHint)  # <-- *shocked face*
#    True
#
#    # DOOR hints can be type-checked Pythonically -- unlike normal type hints.
#    >>> union_hint.is_bearable('The unbearable lightness of type-checking.')
#    True
#    >>> union_hint.die_if_unbearable(b'The @beartype that cannot be named.')
#    beartype.roar.BeartypeDoorHintViolation: Object b'The @beartype that cannot
#    be named.' violates type hint int | str | None, as bytes b'The @beartype
#    that cannot be named.' not str, <class "builtins.NoneType">, or int.
#
#    # DOOR hints can be iterated Pythonically -- unlike normal type hints.
#    >>> for child_hint in union_hint: print(child_hint)
#    TypeHint(<class 'int'>)
#    TypeHint(<class 'str'>)
#    TypeHint(<class 'NoneType'>)
#
#    # DOOR hints can be indexed Pythonically -- unlike normal type hints.
#    >>> union_hint[0]
#    TypeHint(<class 'int'>)
#    >>> union_hint[-1]
#    TypeHint(<class 'str'>)
#
#    # DOOR hints can be sliced Pythonically -- unlike normal type hints.
#    >>> union_hint[0:2]
#    (TypeHint(<class 'int'>), TypeHint(<class 'str'>))
#
#    # DOOR hints supports "in" Pythonically -- unlike normal type hints.
#    >>> TypeHint(int) in union_hint  # <-- it's all true.
#    True
#    >>> TypeHint(bool) in union_hint  # <-- believe it.
#    False
#
#    # DOOR hints are sized Pythonically -- unlike normal type hints.
#    >>> len(union_hint)  # <-- woah.
#    3
#
#    # DOOR hints reduce to booleans Pythonically -- unlike normal type hints.
#    >>> if union_hint: print('This type hint has children.')
#    This type hint has children.
#    >>> if not TypeHint(tuple[()]): print('But this other type hint is empty.')
#    But this other type hint is empty.
#
#    # DOOR hints support equality Pythonically -- unlike normal type hints.
#    >>> from typing import Union
#    >>> union_hint == TypeHint(Union[int, str, None])
#    True  # <-- this is madness.
#
#    # DOOR hints support comparisons Pythonically -- unlike normal type hints.
#    >>> union_hint <= TypeHint(int | str | bool | None)
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
    TypeHint as TypeHint)
from beartype.door._doorcheck import (
    die_if_unbearable as die_if_unbearable,
    is_bearable as is_bearable,
    is_subhint as is_subhint,
)
from beartype.door._proposal.doorpep484604 import (
    UnionTypeHint as UnionTypeHint)
from beartype.door._proposal.doorpep586 import (
    LiteralTypeHint as LiteralTypeHint)
from beartype.door._proposal.doorpep593 import (
    AnnotatedTypeHint as AnnotatedTypeHint)
from beartype.door._proposal.pep484.doorpep484class import (
    ClassTypeHint as ClassTypeHint)
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
