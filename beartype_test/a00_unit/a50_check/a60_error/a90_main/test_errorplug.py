#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype error-handling plugin unit tests.**

This submodule unit tests the public API of the private
:mod:`beartype._check.error.errmain` submodule with respect to
:mod:`beartype`-specific plugin APIs (e.g., the ``__instancecheck_str__()``
dunder method).
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
import pytest

# ....................{ TESTS                              }....................
@pytest.mark.parametrize('is_union', (False, True))
def test_get_func_pith_violation_instancecheck_str(is_union: bool) -> None:
    '''
    Test the
    :func:`beartype._check.error.errmain.get_func_pith_violation`
    getter with respect to the :mod:`beartype`-specific
    ``__instancecheck_str__()`` dunder method plugin API.
    '''

    # ..................{ IMPORTS                            }..................
    # Defer test-specific imports.
    from beartype import BeartypeConf
    from beartype.roar import BeartypePlugInstancecheckStrException
    from beartype._check.error.errmain import get_func_pith_violation
    from beartype._check.cls.call.calldatadecorfuncmin import (
        minify_decor_func_kwargs)
    from beartype_test._util.error.pyterrraise import raises_uncached
    from typing import Any, Union

    # ..................{ METACLASSES                        }..................
    class TheMysteryAndMeta(type):
        '''
        Arbitrary metaclass correctly defining the :mod:`beartype`-specific
        ``__instancecheck_str__()`` dunder method.
        '''

        def __instancecheck_str__(cls, obj: Any) -> str:
            '''
            Correct implementation accepting the expected number of parameters
            and returning the passed object as is.
            '''

            # Return the passed object as is.
            return obj


    class TheMajestyOfMeta(type):
        '''
        Arbitrary metaclass incorrectly defining the :mod:`beartype`-specific
        ``__instancecheck_str__()`` dunder method to accept an unexpected number
        of parameters.
        '''

        def __instancecheck_str__(
            cls, the_joy: Any, the_exultation: Any) -> str:
            '''
            Incorrect implementation accepting an unexpected number of
            parameters and returning an arbitrary non-empty string.
            '''

            return 'The mystery and the majesty of Earth,'

    # ..................{ CLASSES                            }..................
    class TheMysteryAnd(object, metaclass=TheMysteryAndMeta):
        '''
        Arbitrary class whose metaclass correctly defines the
        :mod:`beartype`-specific ``__instancecheck_str__()`` dunder method.
        '''

        pass


    class TheMajestyOf(object, metaclass=TheMajestyOfMeta):
        '''
        Arbitrary class whose metaclass incorrectly defines the
        :mod:`beartype`-specific ``__instancecheck_str__()`` dunder method to
        accept an unexpected number of parameters.
        '''

        pass

    # ..................{ LOCALS                             }..................
    def of_yesternight(
        the_sounds_that: TheMysteryAnd,
        of_earth: TheMajestyOf,
    ) -> TheMysteryAnd:
        '''
        Arbitrary callable annotated by classes whose metaclasses both correctly
        and incorrectly defining the :mod:`beartype`-specific
        ``__instancecheck_str__()`` dunder method.
        '''

        return the_sounds_that

    # Exercise the same plugin validation for direct and union annotations.
    if is_union:
        of_yesternight.__annotations__ = {
            name: Union[hint, int]
            for name, hint in of_yesternight.__annotations__.items()
        }

    # Keyword arguments to be unconditionally passed to *ALL* calls of the
    # get_func_pith_violation() getter below.
    kwargs = dict(
        decor_func=minify_decor_func_kwargs(
            func_wrappee=of_yesternight, conf=BeartypeConf()),
    )

    # Arbitrary non-empty string.
    HIS_WAN_EYES = 'Of yesternight? The sounds that soothed his sleep,'

    # ..................{ PASS                               }..................
    # Violation exception created and returned by this getter for a hypothetical
    # call of the function defined above when passed a non-empty string as the
    # value of the parameter annotated by an arbitrary class whose metaclass
    # correctly defines __instancecheck_str__().
    violation = get_func_pith_violation(
        pith_name='the_sounds_that',
        pith_value=HIS_WAN_EYES,
        **kwargs
    )

    # Message of this violation.
    violation_str = str(violation)

    # Assert that this violation contains the passed non-empty string.
    assert HIS_WAN_EYES in violation_str

    # ..................{ FAIL                               }..................
    # Assert that this getter raises the expected exception for a hypothetical
    # call of the function defined above when passed an arbitrary non-string
    # object as the value of the parameter annotated by an arbitrary class whose
    # metaclass correctly defines __instancecheck_str__().
    with raises_uncached(BeartypePlugInstancecheckStrException):
        get_func_pith_violation(
            pith_name='the_sounds_that',
            pith_value=b"As ocean's moon looks on the moon in heaven.",
            **kwargs
        )

    # Assert that this getter raises the expected exception for a hypothetical
    # call of the function defined above when passed an empty string as the
    # value of the parameter annotated by an arbitrary class whose metaclass
    # correctly defines __instancecheck_str__().
    with raises_uncached(BeartypePlugInstancecheckStrException):
        get_func_pith_violation(
            pith_name='the_sounds_that',
            pith_value='',
            **kwargs
        )

    # Assert that this getter raises the expected exception for a hypothetical
    # call of the function defined above when passed a non-empty string as the
    # value of the parameter annotated by an arbitrary class whose metaclass
    # incorrectly defines __instancecheck_str__().
    with raises_uncached(BeartypePlugInstancecheckStrException):
        get_func_pith_violation(
            pith_name='of_earth',
            pith_value='Gaze on the empty scene as vacantly',
            **kwargs
        )


@pytest.fixture(scope='module')
def union_instancecheck_str_types() -> tuple:
    '''
    Classes whose metaclasses define ``__instancecheck_str__()``, and the list
    recording calls to that method. Share these classes across tests to preserve
    their identity under hint caching.
    '''

    # Record diagnostic calls independently of ordinary instance checks.
    hints_diagnosed = []

    class ShapeMeta(type):
        '''Metaclass providing an explanation without naming its class.'''

        def __instancecheck_str__(cls, obj: object) -> str:
            hints_diagnosed.append(cls)
            return 'dimension size 4 does not equal expected size 3'

    class DtypeMeta(type):
        '''Metaclass providing a distinct explanation for another branch.'''

        def __instancecheck_str__(cls, obj: object) -> str:
            hints_diagnosed.append(cls)
            return 'dtype bool does not equal expected dtype uint8'

    class Shape(metaclass=ShapeMeta):
        pass

    class Dtype(metaclass=DtypeMeta):
        pass

    return Shape, Dtype, hints_diagnosed


@pytest.mark.parametrize('is_pep604', (False, True))
@pytest.mark.parametrize('is_nested', (False, True))
@pytest.mark.parametrize('is_mixed', (False, True))
def test_instancecheck_str_union(
    union_instancecheck_str_types: tuple,
    is_pep604: bool,
    is_nested: bool,
    is_mixed: bool,
) -> None:
    '''
    Test union violations include ``__instancecheck_str__()`` return strings and
    successful checks avoid calls to that method, including nested unions.
    '''

    # Defer test-specific imports.
    from beartype import beartype, BeartypeConf
    from beartype.roar import BeartypeCallHintParamViolation
    from beartype_test._util.error.pyterrraise import raises_uncached
    from typing import Union

    Shape, Dtype, hints_diagnosed = union_instancecheck_str_types
    hints_diagnosed.clear()
    hint_union = Shape | Dtype if is_pep604 else Union[Shape, Dtype]
    if is_mixed:
        hint_union = hint_union | int if is_pep604 else Union[hint_union, int]

    def check(value):
        return value

    check.__annotations__ = {
        'value': list[hint_union] if is_nested else hint_union}
    check = beartype(check, conf=BeartypeConf(is_color=False))

    # Every alternative fails. Both explanations must identify their branch,
    # while ordinary types retain their compact failure description.
    with raises_uncached(BeartypeCallHintParamViolation) as exception_info:
        check(['bad'] if is_nested else 'bad')

    message = str(exception_info.value)
    assert 'Shape">: dimension size 4 does not equal expected size 3' in message
    assert 'Dtype">: dtype bool does not equal expected dtype uint8' in message
    if is_mixed:
        assert 'Not int.' in message
    assert set(hints_diagnosed) == {Shape, Dtype}
    assert len(hints_diagnosed) == 2
    if is_nested:
        assert 'list index 0 item' in message

    # Satisfying any child hint requires no calls to __instancecheck_str__().
    hints_diagnosed.clear()
    values = (Shape(), Dtype(), 1) if is_mixed else (Shape(), Dtype())
    for value in values:
        pith = [value] if is_nested else value
        assert check(pith) is pith
    assert not hints_diagnosed


def test_instancecheck_str_union_order(
    union_instancecheck_str_types: tuple,
) -> None:
    '''Test custom explanations retain child order and existing cause grouping.'''

    # Defer test-specific imports.
    from beartype import BeartypeConf
    from beartype.door import die_if_unbearable
    from beartype.roar import BeartypeDoorHintViolation
    from beartype._cache.cacheclear import clear_caches
    from beartype_test._util.error.pyterrraise import raises_uncached
    from typing import Union

    Shape, Dtype, hints_diagnosed = union_instancecheck_str_types
    for hint_first, hint_last in ((Shape, Dtype), (Dtype, Shape)):
        # Equivalent unions share cache keys. Test each ordering independently.
        clear_caches()
        hints_diagnosed.clear()
        hint = Union[hint_first, int, list[str], hint_last]

        with raises_uncached(BeartypeDoorHintViolation) as exception_info:
            die_if_unbearable([1], hint, conf=BeartypeConf(is_color=False))

        message = str(exception_info.value)
        assert hints_diagnosed == [hint_first, hint_last]
        # Preserve the existing shallow summary and deep cause positions.
        # Only the newly appended custom explanations follow child hint order.
        assert (
            message.index('Not int.') <
            message.index('List index 0 item') <
            message.index(f'{hint_first.__name__}">:') <
            message.index(f'{hint_last.__name__}">:')
        )


def test_instancecheck_str_union_origin() -> None:
    '''
    Test union origin checks include the origin class's
    ``__instancecheck_str__()`` return string.
    '''

    # Defer test-specific imports.
    from beartype import BeartypeConf
    from beartype.door import die_if_unbearable
    from beartype.roar import BeartypeDoorHintViolation
    from beartype_test._util.error.pyterrraise import raises_uncached

    class SequenceMeta(type):
        def __instancecheck_str__(cls, obj: object) -> str:
            return 'requires a custom sequence'

    class Sequence(list, metaclass=SequenceMeta):
        pass

    with raises_uncached(BeartypeDoorHintViolation) as exception_info:
        die_if_unbearable(
            'bad', Sequence[int] | int, conf=BeartypeConf(is_color=False))

    assert 'requires a custom sequence' in str(exception_info.value)
