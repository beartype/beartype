#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`695` **type alias data submodule.**

This submodule defines :pep:`695`-compliant type aliases to be exercised
throughout unit tests exercising these aliases. For safety, these aliases are
intentionally isolated from those unit tests.

Motivation
----------
Generic type alias support is unavoidably implemented in an *extremely* fragile
manner throughout the :mod:`beartype` codebase. Recursively "bubbling up" the
concrete child type hints subscripting a generic type alias into the lower-level
target type hint aliased by that generic type alias is so non-trivial that it
necessitates implementing manual support for "bubbling up" across both all
hint-specific dynamic code generators *and* all hint-specific dynamic exception
raisers: which is to say, the *entire* :mod:`beartype._check` subpackage.

Generic type alias support is so widely distributed that the *only* valid
means of testing this support is to exhaustively define here and subsequently
use below at least one generic type alias for *each* other PEP standard
supported by :mod:`beartype`. Non-trivial, thy name is :pep:`695`.

Caveats
-------
**This submodule requires the active Python interpreter to target at least
Python 3.12.0.** If this is *not* the case, importing this submodule raises an
:exc:`SyntaxError` exception.
'''

# ..................{ IMPORTS                                }..................
from beartype.typing import (
    Annotated,
    Union,
)
from beartype.vale import Is
from beartype_test.a00_unit.data.hint.pep.proposal.pep484585.data_pep484585generic import (
    Pep585IterableTContainerT,
    Pep585IterableTupleSTContainerTupleST,
)

# ..................{ SIMPLE                                 }..................
type AliasSimple = int | list[str]
'''
Simple type alias aliasing a standard type hint containing *NO* syntax or
semantics unique to PEP 695-compliant type aliases (e.g., *NO* forward
references, recursion, or type variables).
'''

# ..................{ PEP (484|604)                          }..................
type AliasPep484604[T] = (
    # PEP-noncompliant type.
    float |
    # PEP 604-compliant new union of two or more generic type hints
    # parametrized by the same type variable subscripting this alias.
    list[T] | set[T] |
    # PEP 484-compliant old union of (...waitforit) two or more generic type
    # hints parametrized by the same type variable subscripting this alias.
    Union[dict[T, T] | frozenset[T]]
)
'''
Type alias aliasing a :pep:`604`-compliant new union of:

* A PEP-noncompliant type.
* Two or more generic type hints parametrized by the same type variable
  subscripting this alias.
* A :pep:`484`-compliant old union of two or more generic type hints
  parametrized by the same type variable subscripting this alias.

This alias thus tests that dynamic code generation for both :pep:`484`- and
:pep:`604`-compliant unions preserves :pep:`484`-compliant type variable
mappings while also flattening directly nested unions into the top-level union.
'''

# ..................{ PEP (484|604) ~ depth ~ unparametrized }..................
type AliasPep484604Depth1 = _AliasPep484604Depth2 | float
'''
Type alias aliasing a :pep:`604`-compliant new union of a PEP-noncompliant type
and another type alias aliasing a :pep:`484`-compliant old union of
another PEP-noncompliant type and another type alias aliasing (...waitforit)
another PEP-noncompliant type.

This alias thus tests that dynamic code generation for both :pep:`484`- and
:pep:`604`-compliant unions recursively unflattens deeply nested unions into the
top-level union.
'''


type _AliasPep484604Depth2 = Union[str, _AliasPep484604Depth3]
'''
Type alias aliasing a :pep:`484`-compliant old union of a PEP-noncompliant type
and another type alias aliasing another PEP-noncompliant type.
'''


type _AliasPep484604Depth3 = int
'''
Type alias aliasing a PEP-noncompliant type.
'''

# ..................{ PEP (484|604) ~ depth ~ parametrized   }..................
type AliasPep484604Depth1T[T] = _AliasPep484604Depth2T[T] | float
'''
Type alias aliasing a :pep:`604`-compliant new union of a PEP-noncompliant type
and another type alias subscripted by the same type variable parametrizing this
alias aliasing a :pep:`484`-compliant old union of another PEP-noncompliant type
and another type alias subscripted by the same type variable parametrizing this
alias aliasing that type parameter.

This alias thus tests that dynamic code generation for both :pep:`484`- and
:pep:`604`-compliant unions recursively unflattens deeply nested unions into the
top-level union.
'''


type _AliasPep484604Depth2T[T] = Union[str, _AliasPep484604Depth3T[T]]
'''
Type alias aliasing a :pep:`484`-compliant old union of a PEP-noncompliant type
and another type alias subscripted by the same type variable parametrizing this
alias aliasing another PEP-noncompliant type .
'''


type _AliasPep484604Depth3T[T] = T
'''
**Identity type alias** isomorphically aliasing the type parameter parametrizing
this alias.
'''

# ..................{ PEP 585                                }..................
type AliasPep585Dict[S, T] = dict[S, T]
'''
Type alias aliasing a :pep:`585`-compliant dictionary subscripted by the same
type variables as those parametrizing this alias.
'''


type AliasPep585TupleFixed[S, T] = tuple[S, T]
'''
Type alias aliasing a :pep:`585`-compliant fixed-length tuple type hint
subscripted by the same type variables as those parametrizing this alias.
'''


type AliasPep585Type[T] = type[T]
'''
Type alias aliasing a :pep:`585`-compliant subclass type hint subscripted by the
same type variable as that parametrizing this alias.
'''

# ..................{ PEP 585 ~ generic                      }..................
type AliasPep585IterableTupleSTContainerTupleST[S, T] = (
    Pep585IterableTupleSTContainerTupleST[S, T])
'''
Type alias aliasing a :pep:`585`-compliant generic subscripted by the same type
variables as those parametrizing this alias.
'''


type AliasPep585IterableTContainerT[T] = T | Pep585IterableTContainerT[T] | None
'''
Type alias aliasing a :pep:`604`-compliant union over a type variable, a
:pep:`585`-compliant generic subscripted by that same type variable, and
:data:`None`.

This alias intentionally exercises an edge case that previously induced infinite
recursion. Badness lurks below.
'''

# ..................{ PEP 593                                }..................
type AliasPep593[T] = Annotated[T | bytes, Is[lambda obj: bool(obj)]]
'''
Type alias aliasing a PEP 593-compliant metahint subscripted by the same
type variable as that parametrizing this alias.
'''
