#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2021 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **callable scope** utilities.

This private submodule implements utility functions dynamically introspecting
the possibly nested lexical scopes enclosing arbitrary callables.

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                           }....................
from beartype.roar import _BeartypeUtilCallableException
from collections.abc import Callable
from typing import Any, Dict, Tuple

# ....................{ HINTS                             }....................
CallableScope = Dict[str, Any]
'''
PEP-compliant type hint matching a **callable socpe** (i.e., dictionary mapping
from the name to value of each locally or globally scoped variable accessible
to a callable).
'''


CallableScopesGlobalsLocals = Tuple[CallableScope, CallableScope]
'''
PEP-compliant type hint matching a 2-tuple ``(globals, locals)`` of the global
and local scope for a passed callable returned by the
:func:`get_func_globals_locals` function.
'''

# ....................{ TESTERS                           }....................
#FIXME: Unit test us up. When doing so, test all edge cases including:
#* A function declared at module scope.
#* A function declared in a closure.
#* A function declared in a nested closure declared in another closure.
#* A method declared by a class declared at module scope.
#* A method declared by a nested class declared in another class declared at
#  module scope.
#* A method declared by a class declared in a closure.
def is_func_closure(func: Callable) -> bool:
    '''
    ``True`` only if the passed callable is a **closure** (i.e., callable
    declared by another callable).

    Parameters
    ----------
    func : Callable
        Callable to be inspected.

    Returns
    ----------
    bool
        ``True`` only if this callable is a closure.
    '''
    assert callable(func), f'{repr(func)} not callable.'

    # Return true only if this callable defines a closure-specific dunder
    # attribute.
    return hasattr(func, '__closure__')

# ....................{ TESTERS                           }....................
#FIXME: Insufficient. We also need to dynamically obtain
#"func_locals" by either:
#* If "func" is actually a @beartype-decorated class, then PEP 563
#  itself provides the algorithm for retrieving this:
#      For classes, localns can be composed by chaining vars of the
#      given class and its base classes (in the method resolution
#      order). Since slots can only be filled after the class was
#      defined, we don't need to consult them for this purpose.
#  That seems... pretty intense. We're fairly certain "typing"
#  might already support something like that? Research us up..
#FIXME: How does this intersect with class and instance methods? Do
#we actually exercise @beartype against class and instance methods
#in our test suite anywhere? We suspect... not. Obviously, we need
#to begin doing that. *sigh*
#FIXME: Actually, it's a bit worse than described above, because
#the decorated callable could be decorated by multiple decorators,
#which means it has *NO* reliable location in the call stack.
#Instead, we *MUST* iteratively search up the call stack until
#finding a parent callable satisfying the constraints:
#    func_name = func.__name__
#    (
#        func_name in func_locals and
#
#        #FIXME: *OH.* Wait. If the decorated callable is decorated
#        #by multiple decorators, then this constraint wouldn't
#        #hold. Even if did, we doubt this callable is actually
#        #available in "func_locals" at this point. Maybe it is?
#        #Maybe closures are declared... *sigh*
#        func_locals[func_name] == func
#    )
#
#Okay. So, the above test probably doesn't work. The only sane
#alternative we can think of is to:
#* Parse "__qualname__" either with "str.[r]split('.')" or a
#  compiled regex. Probably a compiled regex, because we don't just
#  need to split; we need to get the Python identifier preceding
#  the last ".<locals>" in "__qualname__". Right? Compiled regex.
#* Get the Python identifier preceding the last ".<locals>" in
#  "__qualname__". That will give us the name of the parent
#  callable whose *LEXICAL* scope declares this closure.
#* Given that, we can then iteratively search up the current call
#  stack to find that parent callable. Fortunately, we shouldn't
#  have to search far; the parent callable's frame should be *VERY*
#  close to the current frame. Nonetheless, this is still O(n) for
#  n the call stack height in the worst case. *sigh*
#FIXME: Actually, it still might be a bit worse than described
#above, because closures can be nested in closures *AND INNER
#CLOSURES CAN BE ANNOTATED BY TYPE HINTS DECLARED IN THE OUTERMOST
#SCOPE.* We have verified this. This means we now need to
#iteratively synthesize "func_locals" by generalizing the above
#algorithm. Specifically:
#
#* Initialize "func_locals: Dict[str, Any] = {}".
#* For each ".<locals>" in "func.__qualname__":
#  * Iteratively search up the current call stack for the parent
#    callable whose unqualified name (i.e., "__name__") precedes
#    that ".<locals>".
#  * Extend "func_locals" by the "f_locals" dictionary in the call
#    stack for that parent function.
#
#Note that we actually need to perform this iteration in the
#reverse direction (i.e., starting at the outermost scope and
#proceeding inwards) to ensure that inner variables occlude outer
#variables. This suggests we should probably implement this as a
#two-pass algorithm as follows:
#* Define a new "frames_parent = []".
#* In the first pass, we populate "frames_parent" with the call
#  frames of all such parent callables as discovered above (i.e.,
#  by parsing "func.__qualname__" and iterating up the call stack).
#* In the second pass, we iterate "frames_parent" *IN THE REVERSE
#  DIRECTION* (i.e., starting at the end). On each iteration, we
#  extend "func_locals" by the "f_locals" dictionary in the current
#  stack frame being iterated.
#
#Pretty intense stuff. This will work, but it's *NOT* going to be
#trivial, efficient, or easy. It *SHOULD* be robust for at least
#CPython and PyPy, which are the primary use cases. *SHOULD*.
#FIXME: Actually, it still might be a bit worse than described
#above, because (nested) classes also interact with (nested)
#closures. Fortunately, note that decorators can non-trivially
#decide whether they're currently decorating an unbound method
#(which tests as a function from the perspective of isinstance) or
#a non-class function. How? By inspecting the call stack yet again.
#From an exceptionally useful StackOverflow post:
#    Take a look at the output of inspect.stack() when you wrap a
#    method. When your decorator's execution is underway, the
#    current stack frame is the function call to your decorator;
#    the next stack frame down is the @ wrapping action that is
#    being applied to the new method; and the third frame will be
#    the class definition itself, which merits a separate stack
#    frame because the class definition is its own namespace (that
#    is wrapped up to create a class when it is done executing).
#See also:
#    https://stackoverflow.com/a/8793684/2809027
#
#Our intuitive analysis of the situation suggests that, for our
#purposes, (nested) classes and closures should effectively be
#solvable by the exact same algorithm with *NO* special handling
#required for (nested) classes, since (nested) class declarations
#are simply additional frames on the call stack. Nice! Two birds
#with one stone to go.
#FIXME: Note that this StackOverflow answer offers an extreme (albeit
#interesting) means of differentiating unbound methods from functions:
#    https://stackoverflow.com/a/48836522/2809027

#FIXME: Exercise all edge cases with a unit test:
#* Declaring a closure decorated by both @beartype and another
#  decorator (probably just the identity decorator for simplicity).
#* Declaring a closure decorated by both @beartype and another
#  decorator (probably just the identity decorator for simplicity)
#  nested inside of another closure such that the inner closure is
#  annotated by type hints defined by the outer scope declaring the
#  outer closure.
#* Declaring an instance method decorated by both @beartype and
#  another decorator (probably just the identity decorator for
#  simplicity) declared in a class declared in a function.
#* Declaring an instance method decorated by both @beartype and
#  another decorator (probably just the identity decorator for
#  simplicity) declared in a class declared in a closure nested
#  inside of function such that the instance method is annotated by
#  type hints defined by the function declaring the closure.
#This is incredibly fragile, so tests.

def get_func_globals_locals(
    func: Callable,
    func_stack_frames_ignore: int,
) -> CallableScopesGlobalsLocals:
    '''
    2-tuple ``(globals, locals)`` of the global and local scope for the passed
    callable.

    Specifically, this getter returns a 2-tuple containing:

    #. ``globals``, a dictionary mapping from the name to value of each
       **globally scoped attribute** (i.e., global attribute declared by the
       module transitively declaring this callable) accessible to this
       callable.
    #. ``locals``, a dictionary mapping from the name to value of each
       **locally scoped attribute** (i.e., local attribute declared by a parent
       callable transitively declaring this callable) accessible to this
       callable if this callable is a **closure** (i.e., callable declared in
       another callable) *or* the empty dictionary otherwise (i.e., if this
       callable is directly declared in a module).

    Caveats
    ----------
    **This high-level getter assumes the private low-level**
    :func:`sys._getframes` **getter to exist.** If that getter does *not*
    exist, this getter unconditionally treats this callable as module-scoped by
    setting ``locals`` to be the empty dictionary rather than raising an
    exception. Since that getter exists in all standard Python implementations
    (e.g., CPython, PyPy), this should typically *not* be a real-world concern.

    Parameters
    ----------
    func : Callable
        Callable to be inspected.
    func_stack_frames_ignore : int
        Number of frames on the call stack to be ignored (i.e., silently
        incremented past), such that the next non-ignored frame following the
        last ignored frame is the parent callable or module directly declaring
        the passed callable.

    Returns
    ----------
    Tuple[Dict[str, Any], Dict[str, Any]]
        2-tuple ``(globals, locals)`` of the global and local scope for this
        callable.

    Raises
    ----------
    _BeartypeUtilCallableException
        If the next non-ignored frame following the last ignored frame is *not*
        the parent callable or module directly declaring the passed callable.
    '''
    assert callable(func), f'{repr(func)} not callable.'

    # Avoid circular import dependencies.
    from beartype._util.func.utilfuncstack import (
        get_func_stack_frame_getter_or_none)
    from beartype._util.func.utilfuncwrap import unwrap_func

    # Lowest-level wrappee callable wrapped by this wrapper callable.
    func_wrappee = unwrap_func(func)

    # Dictionary mapping from the name to value of each locally scoped attribute
    # accessible to this wrappee callable to be returned.
    #
    # Note that we intentionally do *NOT* return the global scope for this
    # wrapper callable, as wrappers are typically defined in different modules
    # (and thus different global scopes) by different module authors.
    func_globals: CallableScope = func_wrappee.__globals__  # type: ignore[attr-defined]

    # Dictionary mapping from the name to value of each locally scoped attribute
    # accessible to this wrapper callable to be returned.
    #
    # Note that we intentionally *DO* return the local scope for this wrapper
    # rather than wrappee callable, as local scope can *ONLY* be obtained by
    # dynamically inspecting local attributes bound to call frames on the
    # current call stack. However, this wrapper was called at a higher call
    # frame than this wrappee. All local attributes declared within the body of
    # this wrapper callable are irrelevant to this wrappee callable, as Python
    # syntactically parsed the latter at a later time than the former. If we
    # returned the local scope for this wrappee rather than wrapper callable,
    # we would erroneously return local attributes that this wrappee callable
    # originally had no lexical access to. That's bad. So, we don't do that.
    func_locals: CallableScope = {}

    # If this callable is a closure...
    if is_func_closure(func):
        # Either the sys._getframes() getter if the active Python interpreter
        # declares that getter *OR* "None" otherwise.
        get_func_stack_frame = get_func_stack_frame_getter_or_none()

        # If this interpreter declare that getter...
        if get_func_stack_frame is not None:
            assert isinstance(func_stack_frames_ignore, int), (
                f'{func_stack_frames_ignore} not integer.')
            assert func_stack_frames_ignore >= 0, (
                f'{func_stack_frames_ignore} negative.')

            # Unqualified name of the passed callable.
            func_name = func.__name__

            # Ignore an additional frame on the call stack identifying the
            # current call to this getter.
            func_stack_frames_ignore += 1

            # Next non-ignored frame following the last ignored frame.
            func_frame = get_func_stack_frame(func_stack_frames_ignore)

            #FIXME: Generalize all of the following logic to iteratively search
            #up the call stack:
            #* First, we need to get past all of the decorators that could have
            #  been applied *AFTER* @beartype to this callable. So, search up
            #  until we find a parent callable declaring the passed callable.
            #* Then, we need to iteratively extend our locals with parent
            #  callable locals until hitting a "<module>" boundary. We recall
            #  seeing something somewhere about the special strings "<module>"
            #  and "__module__" being useful for this purpose. That said, the
            #  simplest solution may simply be to detect changes in the module
            #  name. Note that we can trivially obtain module names with:
            #      caller_module = func_frame.f_globals['__name__']
            #  That said, it'd still be nice to detect module boundaries.
            #  Perhaps simply leave a "FIXME" comment for later, yes?

            # Unqualified name of the parent callable embodied by this frame.
            func_frame_name = func_frame.f_code.co_name

            # Dictionary mapping from the name to value of each locally scoped
            # attribute accessible in the body of this parent callable.
            func_frame_locals: CallableScope = func_frame.f_locals

            # If this parent callable does *NOT* declare the passed callable,
            # raise an exception.
            if func_name not in func_frame_locals:
                raise _BeartypeUtilCallableException(
                    f'Closure {func_name}() not declared by parent callable '
                    f'{func_frame_name}() with locals:\n'
                    f'{func_frame_locals}'
                )
            # Else, this parent callable declares the passed callable.

            # Extend the local scope of the passed callable with the local
            # scope of this parent callable.
            func_locals.update(func_frame_locals)
        # Else, this interpreter does *NOT* declare that getter. In this case,
        # we unconditionally treat this closure as module-scoped instead by
        # preserving "locals" as the empty dictionary.
    # Else, this callable is *NOT* a closure and thus module-scoped. In this
    # case, we preserve "locals" as the empty dictionary.

    # Return the 2-tuple "(globals, locals)" of these global and local scopes.
    return (func_globals, func_locals)
