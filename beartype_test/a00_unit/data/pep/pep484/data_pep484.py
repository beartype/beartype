#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`484` **data submodule.**
'''

# ....................{ IMPORTS                            }....................
from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_11
from collections.abc import Sequence as SequenceABC
from typing import (
    Any,
    Generic,
    NamedTuple,
    TypeVar,
)

# ....................{ TYPEVARS ~ un(bounded|constrained) }....................
S = TypeVar('S')
'''
:pep:`484`-compliant **unbound type variable** (i.e., matching *any* arbitrary
type) locally bound to different types than the :data:`.T`, :data:`.U`, and
:data:`.V` type variables.
'''


T = TypeVar('T')
'''
:pep:`484`-compliant **unbound type variable** (i.e., matching *any* arbitrary
type) locally bound to different types than the :data:`.S`, :data:`.U`, and
:data:`.V` type variables.
'''


U = TypeVar('U')
'''
:pep:`484`-compliant **unbound type variable** (i.e., matching *any* arbitrary
type) locally bound to different types than the :data:`.S`, :data:`.T`, and
:data:`.V` type variables.
'''


V = TypeVar('V')
'''
:pep:`484`-compliant **unbound type variable** (i.e., matching *any* arbitrary
type) locally bound to different types than the :data:`.S`, :data:`.T`, and
:data:`.U` type variables.
'''

# ....................{ TYPEVARS ~ bounded                 }....................
T_bound_any = TypeVar('T_bound_any', bound=Any)
'''
:pep:`484`-compliant **unbounded type variable** (i.e., type variable
parametrized by the :obj:`.Any` singleton passed as the ``bound`` keyword
argument, semantically equivalent to an unparametrized type variable).
'''


T_bound_int = TypeVar('T_bound_int', bound=int)
'''
:pep:`484`-compliant **integer-bounded type variable** (i.e., type variable
parametrized by the builtin :class:`int` type passed as the ``bound`` keyword
argument).
'''


T_bound_sequence = TypeVar('T_bound_sequence', bound=SequenceABC)
'''
:pep:`484`-compliant **sequence-bounded type variable** (i.e., type variable
parametrized by the standard :class:`collections.abc.Sequence` abstract base
class (ABC) passed as the ``bound`` keyword argument).
'''

# ....................{ TYPEVARS ~ constrained             }....................
T_constraint_int_or_str = TypeVar('T_constraint_int_or_str', int, str)
'''
:pep:`484`-compliant **integer- or string-constrained type variable** (i.e.,
type variable parametrized by both the builtin :class:`int` and :class:`str`
types passed as positional arguments).
'''


T_constraint_str_or_bytes = TypeVar('T_constraint_str_or_bytes', str, bytes)
'''
:pep:`484`-compliant **string- or bytes-constrained type variable** (i.e., type
variable parametrized by both the builtin :class:`str` and :class:`bytes` types
passed as positional arguments).
'''

# ....................{ NAMED TUPLES                       }....................
NamedTupleFunctionalSubclass = NamedTuple(
    'NamedTupleFunctionalSubclass', [('fumarole', str), ('enrolled', int)])
'''
:pep:`484`-compliant **functionally-constructed named tuple** (i.e.,
:class:`tuple` subclass dynamically constructed by the :obj:`typing.NamedTuple`
type factory, which augments the :obj:`collections.namedtuple` type factory with
annotated type hints).
'''


# If the active Python interpreter targets Python >= 3.11, define PEP
# 484-compliant type hints available *ONLY* under Python >= 3.11.
if IS_PYTHON_AT_LEAST_3_11:
    class NamedTupleGeneric(NamedTuple, Generic[T]):
        '''
        :pep:`484`-compliant **subclass-constructed generic named tuple** (i.e.,
        :class:`tuple` subclass dynamically constructed by subclassing both the
        :obj:`typing.Generic` superclass *and* :obj:`typing.NamedTuple` type
        factory, which augments the :obj:`collections.namedtuple` type factory with
        annotated type hints).
        '''

        now_while_i_cannot: T
        hear_the_citys_din: T
