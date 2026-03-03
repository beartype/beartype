#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Test-wide :pep:`484`-compliant **stringified forward reference type hint**
(i.e., strings whose values are the names of classes and tuples of classes, one
or more of which typically have yet to be defined) :pep:`695`-compliant
decoration data submodule.

This submodule exercises stringified forward reference support implemented in
the :func:`beartype.beartype` decorator when specifically decorating callables
defining :pep:`695`-compliant **type parameter scopes** (e.g., the ``[T]`` in
``def muh_func[T](...) -> 'T':``) annotated by stringified forward references
referring to those type parameters (e.g., the ``'T'`` in that function).

Caveats
-------
**This submodule requires the active Python interpreter to target at least
Python 3.12.0.** If this is *not* the case, importing this submodule raises an
:exc:`SyntaxError` exception.
'''

# ....................{ IMPORTS                            }....................
from beartype import beartype
from collections.abc import Callable

# ....................{ CALLABLES                          }....................
@beartype
def suddenly_on[T](the_oceans: 'T') -> 'Callable[[], T]':
    '''
    Arbitrary callable decorated by :func:`beartype.beartype`, parametrized by a
    :pep:`695`-compliant type parameter, accepting an arbitrary parameter
    annotated by a :pep:`484`-compliant stringified forward reference type hint
    referring to that type parameter, and returning a closure returning a value
    annotated by similar forward references.

    Yes, this edge case actually happened. You can't make bugs like this up.

    See Also
    --------
    https://github.com/beartype/beartype/issues/533
        Resolved issue validated by this callable.
    '''

    @beartype
    def chilly_streams() -> 'T':
        '''
        Arbitrary closure decorated by :func:`beartype.beartype`, returning a
        value annotated by a :pep:`484`-compliant stringified forward reference
        type hint referring to the type parameter implicitly defined by the
        parent callable also defining this closure.
        '''

        # Return the parameter passed to that parent callable as is.
        return the_oceans

    # Return this closure.
    return chilly_streams

# ....................{ DECORATORS                         }....................
@beartype
def spun_round[**P, T](sable_curtaining: 'Callable[P, T]') -> (
    'Callable[[Callable[P, T]], Callable[P, T]]'):
    '''
    Arbitrary callable decorated by :func:`beartype.beartype`, parametrized by
    multiple :pep:`695`-compliant type parameters (including both a
    :pep:`484`-compliant type variable *and* :pep:`612`-compliant parameter
    specification), accepting the callable to be decorated annotated by
    :pep:`484`-compliant stringified forward reference type hints referring to
    those type parameters, and returning a closure returning the callable passed
    to that closure annotated by similar forward references.

    From the runtime perspective, this decorator trivially reduces to a noop.
    From the pure static type-checking perspective, however, this decorator
    propagates the signature from the source callable passed to this decorator
    onto the target callable decorated by this decorator. Since these two
    perspectives do not align, this test exists to ensure that :mod:`beartype`
    properly handles this edge case *without* raising unexpected exceptions.

    Yes, this edge case actually happened. You can't make bugs like this up.

    See Also
    --------
    https://github.com/beartype/beartype/issues/533
        Resolved issue validated by this callable.
    '''

    @beartype
    def of_clouds(nor_therefore_veiled: 'Callable[P, T]') -> 'Callable[P, T]':
        '''
        Arbitrary closure decorated by :func:`beartype.beartype`, returning the
        passed callable unmodified, and annotated by :pep:`484`-compliant
        stringified forward reference type hints referring to the type
        parameters implicitly defined by the parent callable also defining this
        closure.

        *TYPE-CHECKING THIS CLOSURE IS INCREDIBLY NON-TRIVIAL.* You can tell how
        non-trivial it is based on our YELLING IN ALL CAPS. Type-checking the
        parent :func:`.spun_round` decorator is trivial. Type-checking this
        child :func:`.of_clouds` closure, however, is non-trivial to the
        extreme. Doing so requires :mod:`beartype` to iteratively introspect up
        the call stack for a stack frame encapsulating the closest lexical scope
        defining the parent :func:`.spun_round` decorator (i.e., global scope in
        this case). Why? Because only that decorator defines the
        ``__type_params`` dunder attribute exposing the type parameters
        referenced by the forward references annotating this child closure.
        '''

        # Return the parameter passed to this child closure as is.
        return nor_therefore_veiled

    # Return this closure.
    return of_clouds


@beartype
def blindfold_and_hid(but_ever: str, and_anon: int) -> str:
    '''
    Arbitrary :func:`beartype.beartype`-decorated source callable to copy the
    signature from.
    '''

    # Let loose the one-liners of code!
    return f'{but_ever} {and_anon}'


@beartype
@spun_round(blindfold_and_hid)
def the_glancing_spheres(*args, **kwargs) -> str:
    '''
    Arbitrary :func:`beartype.beartype`-decorated target callable to copy the
    signature onto.
    '''

    # Defer to the source callable defined above.
    return blindfold_and_hid(*args, **kwargs)
