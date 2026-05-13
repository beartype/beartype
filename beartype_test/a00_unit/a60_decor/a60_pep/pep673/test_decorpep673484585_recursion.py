#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype decorator** :pep:`484`- and :pep:`585`-compliant generics and
:pep:`673`-compliant :obj:`typing.Self` **recursion guard unit tests**.

This submodule unit tests that the :func:`beartype.beartype` decorator has not
regressed with respect to infinitely recursive type-checking previously induced
by **self type hints** (i.e., PEP-compliant type hints referring to the
currently decorated type).
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS                              }....................
def test_decor_pep484585673_sequence_getitem() -> None:
    '''
    Test the :func:`beartype.beartype` decorator against infinitely recursive
    type-checking previously induced by **self type hints** (i.e., PEP-compliant
    type hints referring to the currently decorated type) annotating the
    ``__getitem__()`` dunder method of :pep:`585`-compliant sequence generics.

    This unit test variously tests these self type hints against that method:

    * A :pep:`484`-compliant stringified relative forward reference type hint to
      the currently defined unsubscripted generic.
    * A :pep:`484`-compliant stringified relative forward reference type hint to
      the currently defined subscripted generic.
    * If the active Python interpreter targets Python >= 3.11, a
      :pep:`673`-compliant :obj:`typing.Self` type hint.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype import beartype
    from beartype.roar import BeartypeCallHintReturnViolation
    from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_11
    from beartype_test._util.error.pyterrraise import raises_uncached
    from beartype_test.a00_unit.data.pep.pep484.data_pep484 import T
    from collections.abc import (
        Iterator,
        Sequence,
    )
    from typing import (
        Generic,
        SupportsIndex,
        Union,
    )

    # ....................{ LOCALS                         }....................
    # List of all self hints previously inducing infinitely recursive
    # type-checking to be iteratively tested below.
    hints_self = [
        # PEP 484-compliant stringified relative forward reference type hint to
        # the unsubscripted generic defined below.
        'OfDayAndNight',

        # PEP 484-compliant stringified relative forward reference type hint to
        # the subscripted generic defined below, subscripted by the same PEP
        # 484-compliant type variable subscripting its "Generic[...]" supertype.
        'OfDayAndNight[T]',
    ]

    # If the active Python interpreter targets Python >= 3.11 and thus supports
    # PEP 673...
    if IS_PYTHON_AT_LEAST_3_11:
        # Defer version-specific imports.
        from typing import Self

        # Append a PEP 673-compliant "typing.Self" type hint to this list.
        hints_self.append(Self)

    # ....................{ CLASSES                        }....................
    @beartype
    class UponTheBoundaries(Generic[T]):
        '''
        :pep:`484`-compliant generic subscripted by an arbitrary
        :pep:`484`-compliant type variable.
        '''

        def __init__(self, radiance_faint: T) -> None:
            '''
            Initialize this dataclass with the passed arbitrary value.
            '''

            self.radiance_faint = radiance_faint


        def __repr__(self) -> str:
            '''
            Machine-readable representation of this generic.

            This dunder method is defined purely as a debugging aid in the
            inevitable event of catastrophic failure, which just happened.
            '''

            return f'UponTheBoundaries({repr(self.radiance_faint)})'

    # ....................{ ASSERTS                        }....................
    # For each self hint defined above...
    for hint_self in hints_self:
        # ....................{ CLASSES                    }....................
        @beartype
        class OfDayAndNight(Sequence[UponTheBoundaries[T]]):
            '''
            :pep:`585`-compliant generic sequence of instances of the above
            :pep:`484`-compliant generic.

            This type is intentionally subscripted by an arbitrary
            :pep:`484`-compliant type variable. Doing so renders this type
            subscriptable, enabling the :meth:`__getitem__` dunder method
            defined below to test different code paths in the :mod:`beartype`
            codebase when annotated by both subscripted and unsubscripted type
            hints referring to this type.

            Attributes
            ----------
            _universal_space: list[UponTheBoundaries[T]]
                List of all :class:`.UponTheBoundaries` instances with which
                this sequence was previously initialized.
            '''

            def __init__(self, *universal_space: UponTheBoundaries[T]) -> None:
                '''
                Initialize this sequence to the passed
                :class:`.UponTheBoundaries` instances.
                '''

                self._universal_space = list(universal_space)


            def __iter__(self) -> Iterator[UponTheBoundaries[T]]:
                '''
                Iterate the :class:`.UponTheBoundaries` instances with which
                this sequence was previously initialized.

                This dunder method is required to satisfy the abstract
                :class:`.Sequence` protocol.
                '''

                yield from self._universal_space


            def __len__(self) -> int:
                '''
                Number of :class:`.UponTheBoundaries` instances with which this
                sequence was previously initialized.

                This dunder method is required to satisfy the abstract
                :class:`.Sequence` protocol.
                '''

                return len(self._universal_space)


            def __repr__(self) -> str:
                '''
                Machine-readable representation of this sequence.

                This dunder method is defined purely as a debugging aid in the
                inevitable event of catastrophic failure, which just happened.
                '''

                return f'OfDayAndNight(*{repr(self._universal_space)})'


            def __getitem__(
                self: hint_self, key: SupportsIndex | slice
            ) -> Union[hint_self, UponTheBoundaries[T]]:
                '''
                :class:`.UponTheBoundaries` instance(s) at the passed indices
                with which this sequence was previously initialized.

                This dunder method specifically returns either:

                * If passed a slice, a new instance of this sequence containing
                  *only* the proper subset of :class:`.UponTheBoundaries` items
                  indexed by this slice with which this sequence was previously
                  initialized.
                * If passed any integer *except* -1, the
                  :class:`.UponTheBoundaries` item indexed by this integer with
                  which this sequence was previously initialized.
                * If passed -1, an arbitrary value intentionally violating the
                  type hint annotating this dunder method's return.

                This dunder method erroneously induces infinite recursion during
                type-checking when annotated by one or more self type hints.

                See Also
                --------
                :data:`beartype._data.shame.datashamefunc.BLACKLIST_METHOD_NAMES_HINT_SELF`
                    Further details.
                '''

                # If the caller indexed this sequence with a slice, return a new
                # instance of this sequence containing *ONLY* the proper subset
                # of "UponTheBoundaries" items indexed by this slice with which
                # this sequence was previously initialized.
                if isinstance(key, slice):
                    return OfDayAndNight[T](*self._universal_space[key])
                # If the caller did *NOT* index this sequence with a slice and
                # thus indexed this sequence with an integer instead.
                #
                # If the caller indexed this sequence with the magic number -1,
                # return an arbitrary value violating the type hint annotating
                # this dunder method's return.
                elif key == -1:
                    return 'Upon the boundaries of day and night,'
                # Else, the caller did *NOT* index this sequence with the magic
                # number -1.

                # Return the "UponTheBoundaries" item indexed by this integer
                # with which this sequence was previously initialized as a
                # last-ditch fallback.
                return self._universal_space[key]

        # ....................{ LOCALS                     }....................
        # Arbitrary instances of the PEP 484-compliant generic defined above.
        stretched_himself_in_grief = UponTheBoundaries[str](
            "He stretch'd himself in grief and radiance faint.")
        the_heaven_with_its_stars = UponTheBoundaries[str](
            'There as he lay, the Heaven with its stars')

        # Arbitrary instance of the PEP 585-compliant sequence defined above,
        # initialized by these PEP 484-compliant generics.
        voice_of_coelus = OfDayAndNight[str](
            stretched_himself_in_grief, the_heaven_with_its_stars)

        # ....................{ PASS                       }....................
        # Assert that this sequence contains the expected items when accessed by
        # integer lookup against the __getitem__() dunder method.
        assert voice_of_coelus[0] is stretched_himself_in_grief
        assert voice_of_coelus[1] is the_heaven_with_its_stars

        # Assert that this sequence contains the expected items when accessed by
        # sliced lookup against the __getitem__() dunder method.
        there_as_he_lay = voice_of_coelus[1:]
        assert len(there_as_he_lay) == 1
        assert there_as_he_lay[0] is the_heaven_with_its_stars

        # ....................{ FAIL                       }....................
        # Assert that this sequence raises the expected type-checking violation
        # when accessed by bad magic integer lookup against the __getitem__()
        # dunder method.
        with raises_uncached(BeartypeCallHintReturnViolation):
            voice_of_coelus[-1]
