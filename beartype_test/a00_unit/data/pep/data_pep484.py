#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`484` **data submodule.**
'''

# ....................{ IMPORTS                            }....................
from beartype.typing import (
    Any,
    TypeVar,
)
from collections.abc import Sequence as SequenceABC

# ....................{ TYPEVARS ~ un(bounded|constrained) }....................
S = TypeVar('S')
'''
**Unbound type variable** (i.e., matching *any* arbitrary type) locally bound to
different types than the :data:`.T`, :data:`.U`, and :data:`.V` type variables.
'''


T = TypeVar('T')
'''
**Unbound type variable** (i.e., matching *any* arbitrary type) locally bound to
different types than the :data:`.S`, :data:`.U`, and :data:`.V` type variables.
'''


U = TypeVar('U')
'''
**Unbound type variable** (i.e., matching *any* arbitrary type) locally bound to
different types than the :data:`.S`, :data:`.T`, and :data:`.V` type variables.
'''

V = TypeVar('V')
'''
**Unbound type variable** (i.e., matching *any* arbitrary type) locally bound to
different types than the :data:`.S`, :data:`.T`, and :data:`.U` type variables.
'''

# ....................{ TYPEVARS ~ bounded                 }....................
T_any = TypeVar('T_any', bound=Any)
'''
**Unbounded type variable** (i.e., type variable parametrized by the :obj:`.Any`
singleton passed as the ``bound`` keyword argument, semantically equivalent to
an unparametrized type variable).
'''


T_int = TypeVar('T_int', bound=int)
'''
**Integer-bounded type variable** (i.e., type variable parametrized by the
builtin :class:`int` type passed as the ``bound`` keyword argument).
'''


T_sequence = TypeVar('T_sequence', bound=SequenceABC)
'''
**Sequence-bounded type variable** (i.e., type variable parametrized by the
standard :class:`collections.abc.Sequence` abstract base class (ABC) passed as
the ``bound`` keyword argument).
'''

# ....................{ TYPEVARS ~ constrained             }....................
T_int_or_str = TypeVar('T_int_or_str', int, str)
'''
**Integer- or string-constrained type variable** (i.e., type variable
parametrized by both the builtin :class:`int` and :class:`str` types passed as
positional arguments).
'''


T_str_or_bytes = TypeVar('T_str_or_bytes', str, bytes)
'''
**String- or bytes-constrained type variable** (i.e., type variable parametrized
by both the builtin :class:`str` and :class:`bytes` types passed as positional
arguments).
'''
