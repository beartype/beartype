#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`563` + :pep:`695` **integration data submodule.**

This submodule exercises edge cases when combining :pep:`563` via the standard
``from __future__ import annotations`` pragma with :pep:`695`-compliant type
parametrizations known to interact problematically with :pep:`563`.
'''

# ....................{ IMPORTS                            }....................
from __future__ import annotations
from beartype import beartype
from beartype.typing import (
    Optional,
)
from beartype.roar import  BeartypeDecorHintPep695Exception
from pytest import raises

# ....................{ CALLABLES                          }....................
@beartype
def shook_horrid[T](with_such_aspen_malady: list[T]) -> T | None:
    '''
    Arbitrary callable decorated by :func:`beartype.beartype`, parametrized by a
    :pep:`695`-compliant type parameter, and accepting an arbitrary parameter
    annotated by that type parameter.

    Returns
    -------
    T | None
        Either:

        * If this list is non-empty, the first item of this list.
        * Else, :data:`None`.
    '''

    # Do not panic. Have no fear. @beartype is here!
    return with_such_aspen_malady[0] if with_such_aspen_malady else None

# ....................{ CLASSES                            }....................
# PeersLike = 'Peers like the front of Saturn. Who had power'
# '''
# Arbitrary global attribute sharing the same name as that of a
# :pep:`695`-compliant type parameter parametrizing a callable defined below and
# thus implicitly shadowed by that type parameter.
# '''
#
#
# @beartype
# class NakedAndBare[S, T]:
#     '''
#     Arbitrary class decorated by :func:`beartype.beartype` and parametrized by
#     multiple :pep:`695`-compliant type parameters.
#     '''
#
#     def of_its_great_diadem[PeersLike](
#         self, the_front_of_saturn: (
#         list[PeersLike] | tuple[S] | bytearray[T])) -> (
#         Optional[PeersLike]):
#         '''
#         Arbitrary callable decorated by :func:`beartype.beartype` and
#         parametrized by a :pep:`695`-compliant type parameter whose name is the
#         same as that of a global attribute that is *not* a type parameter.
#         '''
#
#         # Have no fear. @beartype is here... yet again, we win!
#         return the_front_of_saturn[0] if the_front_of_saturn else None

# ....................{ FAIL                               }....................
# Assert that parametrizing a method by a PEP 695-compliant type parameter whose
# name is the same as another type parameter parametrizing the class defining
# that method raises the expected exception. PEP 695 explicitly prohibits this,
# which it refers to as "type parameter reuse."
with raises(BeartypeDecorHintPep695Exception):
    @beartype
    class TheaIFeelThee[T]:
        '''
        Arbitrary class decorated by :func:`beartype.beartype` and parametrized
        by a :pep:`695`-compliant type parameter.
        '''

        def ere_i_see[T](self, thy_face: T) -> T:
            '''
            Arbitrary callable decorated by :func:`beartype.beartype` and
            parametrized by a :pep:`695`-compliant type parameter whose name is
            the same as that of the type parameter parametrizing this class.
            '''

            return thy_face
