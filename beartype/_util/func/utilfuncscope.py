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
from beartype._util.func.utilfunccodeobj import (
    die_unless_func_python,
    get_func_codeobj_or_none,
)
from collections.abc import Callable
from types import CodeType, FrameType
from typing import Any, Dict, Optional, Tuple

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
def is_func_nested(func: Callable) -> bool:
    '''
    ``True`` only if the passed callable is **nested** (i.e., a pure-Python
    callable declared in the body of another pure-Python callable).

    Parameters
    ----------
    func : Callable
        Callable to be inspected.

    Returns
    ----------
    bool
        ``True`` only if this callable is nested.
    '''
    assert callable(func), f'{repr(func)} not callable.'

    # Return true only if the fully-qualified name of this callable contains
    # the one or more ".<locals>" placeholder substrings signifying
    # closure-specific lexical scopes.
    return '.<locals>.' in func.__qualname__


#FIXME: Unit test us up.
#FIXME: Technically, we currently don't call this anywhere. But we probably
#will someday, so let's preserve this intact until then. *shrug*
def is_func_closure(func: Callable) -> bool:
    '''
    ``True`` only if the passed callable is a **closure** (i.e.,
    nested callable accessing one or more variables declared by the parent
    callable also declaring that callable).

    Note that all closures are necessarily nested callables but that the
    converse is *not* necessarily the case. In particular, a nested callable
    accessing no variables declared by the parent callable also declaring that
    callable is *not* a closure.

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
    #
    # Note that the "__closure__" dunder variable is either:
    # * If this callable is a closure, a tuple of zero or more cell variables.
    # * If this callable is a pure-Python non-closure, "None".
    # * If this callable is C-based, undefined.
    return getattr(func, '__closure__', None) is not None

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
    # Mandatory parameters.
    func: Callable,

    # Optional parameters.
    func_stack_frames_ignore: int = 0,
    exception_cls: type = _BeartypeUtilCallableException,
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
       callable if this callable is **nested** (i.e., callable declared in
       another callable) *or* the empty dictionary otherwise (i.e., if this
       callable is directly declared in a module).

    Caveats
    ----------
    **This high-level getter assumes the private low-level**
    :func:`sys._getframe` **getter to exist.** If that getter does *not*
    exist, this getter unconditionally treats this callable as module-scoped by
    setting ``locals`` to be the empty dictionary rather than raising an
    exception. Since that getter exists in all standard Python implementations
    (e.g., CPython, PyPy), this should typically *not* be a real-world concern.

    Parameters
    ----------
    func : Callable
        Callable to be inspected.
    func_stack_frames_ignore : int, optional
        Number of frames on the call stack to be ignored (i.e., silently
        incremented past), such that the next non-ignored frame following the
        last ignored frame is the parent callable or module directly declaring
        the passed callable. Defaults to 0.
    exception_cls : type, optional
        Type of exception to be raised in the event of fatal error. Defaults to
        :class:`_BeartypeUtilCallableException`.

    Returns
    ----------
    Tuple[Dict[str, Any], Dict[str, Any]]
        2-tuple ``(globals, locals)`` of the global and local scope for this
        callable.

    Raises
    ----------
    exception_cls
        If either:

        * The passed callable unwraps to a C-based rather than pure-Python
          wrappee callable.
        * The next non-ignored frame following the last ignored frame is *not*
          the parent callable or module directly declaring the passed callable.
    '''
    assert callable(func), f'{repr(func)} not callable.'

    # Avoid circular import dependencies.
    from beartype._util.func.utilfuncstack import (
        get_func_stack_frame_getter_or_none)
    from beartype._util.func.utilfuncwrap import unwrap_func

    # Lowest-level wrappee callable wrapped by this wrapper callable.
    func_wrappee = unwrap_func(func)

    # If this callable is *NOT* pure-Python, raise an exception.
    #
    # Note that this is critical, as only pure-Python callables define various
    # dunder attributes accessed below (e.g., "__globals__").
    die_unless_func_python(func=func, exception_cls=exception_cls)

    # Dictionary mapping from the name to value of each locally scoped
    # attribute accessible to this wrappee callable to be returned.
    #
    # Note that we intentionally do *NOT* return the global scope for this
    # wrapper callable, as wrappers are typically defined in different modules
    # (and thus different global scopes) by different module authors.
    func_globals: CallableScope = func_wrappee.__globals__  # type: ignore[attr-defined]

    # Dictionary mapping from the name to value of each locally scoped
    # attribute accessible to this wrapper callable to be returned.
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

    # If this callable is nested...
    # print(f'Capturing {func.__qualname__}() local scope...')
    if is_func_nested(func):
        # Either the sys._getframe() getter if the active Python interpreter
        # declares that getter *OR* "None" otherwise.
        get_func_stack_frame = get_func_stack_frame_getter_or_none()

        # If this interpreter declares that getter...
        # print(f'Capturing nested {func.__qualname__}() local scope...')
        if get_func_stack_frame is not None:
            # Get this nested callable's local scope.
            func_locals = _get_func_nested_locals(
                func=func,
                func_stack_frames_ignore=func_stack_frames_ignore,
                exception_cls=exception_cls,
            )
        # Else, this interpreter does *NOT* declare that getter. In this case,
        # we unconditionally treat this nested callable as module-scoped
        # callable instead by preserving "locals" as the empty dictionary.
    # Else, this callable is unnested and thus module-scoped. In this case, we
    # preserve "locals" as the empty dictionary.

    # Return the 2-tuple "(globals, locals)" of these global and local scopes.
    return (func_globals, func_locals)


def _get_func_nested_locals(
    func: Callable,
    func_stack_frames_ignore: int,
    exception_cls: type,
) -> CallableScope:
    '''
    **Local scope** (i.e., dictionary mapping from the name to value of each
    locally scoped attribute accessible from the passed nested callable) for
    this callable.

    Parameters
    ----------
    func : Callable
        Nested callable to be inspected.
    func_stack_frames_ignore : int
        Number of frames on the call stack to be ignored (i.e., silently
        incremented past).
    exception_cls : type
        Type of exception to be raised in the event of fatal error.

    Returns
    ----------
    Dict[str, Any]
        Local scope for this nested callable.

    Raises
    ----------
    exception_cls
        If either:

        * The next non-ignored frame following the last ignored frame is *not*
          the parent callable or module directly declaring the passed callable.
    '''
    assert callable(func), f'{repr(func)} not callable.'
    assert isinstance(func_stack_frames_ignore, int), (
        f'{func_stack_frames_ignore} not integer.')
    assert func_stack_frames_ignore >= 0, (
        f'{func_stack_frames_ignore} negative.')

    # Note that the caller has explicitly validated this only conditionally
    # available private getter to already exist.
    from sys import _getframe

    # ..................{ LOCALS ~ func                     }..................
    # Dictionary mapping from the name to value of each locally scoped
    # attribute accessible to this nested callable to be returned.
    func_locals: CallableScope = {}

    # Fully-qualified name of the module declaring this nested callable if this
    # nested callable was physically declared by an on-disk module *OR* "None".
    func_module_name = func.__module__

    # ..................{ LOCALS ~ func : scope             }..................
    # Fully-qualified name of this nested callable identifying all lexical
    # scopes encapsulating this nested callable, stripped of all ".<locals"
    # placeholder substrings uselessly emphasizing nested callable contexts.
    #
    # For example, for an inner nested callable muh_closure() declared by an
    # outer function muh_func(), this is:
    #     >>> func.__qualname__
    #     'muh_func.<locals>.muh_closure'
    #     >>> func_scopes_name_str
    #     'muh_func.muh_closure'
    func_scopes_name_str = func.__qualname__.replace('.<locals>', '')

    # Human-readable label describing this nested callable in exceptions.
    func_label = f'Nested callable {func_scopes_name_str}()'

    # List of the unqualified names of all lexical scopes encapsulating this
    # nested callable (e.g., "['muh_func', 'muh_closure']").
    func_scopes_name = func_scopes_name_str.split('.')

    # If this nested callable is *NOT* encapsulated by at least two lexical
    # scopes (signifying this nested callable and the parent callable declaring
    # this nested callable), raise an exception.
    if len(func_scopes_name) < 2:
        raise exception_cls(
            f'{func_label} lexical scopes len({repr(func_scopes_name)}) < 2.')
    # Else, this nested callable is encapsulated by at least three lexical scopes.

    # Discard the last lexical scope, which is *NOT* actually a scope but
    # rather simply the unqualified name of the passed callable. Since this
    # nested callable is encapsulated by at least two lexical scopes, this list
    # is guaranteed to contain at least one lexical scope after this reduction.
    func_scopes_name.pop()

    # 0-based index of the current lexical scope to be searched for in the
    # current runtime call stack.
    #
    # Note that:
    # * The set of all callables embodied by the current runtime call stack is
    #   a (typically proper) superset of the set of all callables embodied by
    #   the lexical scopes encapsulating this nested callable. Ergo, some stack
    #   frames have no corresponding lexical scopes (e.g., stack frames
    #   embodying callables defined by different modules) but *ALL* lexical
    #   scopes have a corresponding stack frame.
    # * Stack frames are only efficiently accessible relative to the initial
    #   stack frame embodying this nested callable, which resides at the end of
    #   the call stack. This implies we *MUST* iteratively search up:
    #   * The call stack for frames with relevant lexical scopes and ignore
    #     intervening frames with irrelevant lexical scopes, beginning at the
    #     end of that stack.
    #   * Lexical scopes for scopes with corresponding frames, beginning at the
    #     last lexical scope.
    func_scopes_name_index = len(func_scopes_name) - 1

    # Current lexical scope to be searched for in the runtime call stack.
    func_scopes_name_curr = func_scopes_name[func_scopes_name_index]

    # ..................{ LOCALS ~ func : frame             }..................
    # Ignore additional frames on the call stack embodying:
    # * The current call to this private getter.
    # * The previous call to the public parent getter.
    func_stack_frames_ignore += 2

    # Next non-ignored frame following the last ignored frame.
    func_frame: Optional[FrameType] = _getframe(func_stack_frames_ignore)

    # Code object underlying the parent callable associated with the current
    # stack frame if that callable is pure-Python *OR* "None" otherwise.
    func_frame_codeobj: Optional[CodeType] = None

    # Fully-qualified name of that callable's module.
    func_frame_module_name = ''

    # Unqualified name of that callable.
    func_frame_name = ''

    # ..................{ ALGORITHM                         }..................
    # Iteratively construct the transitive local scope for this nested callable
    # from the local scope of each lexical parent callable of this nested
    # callable on the call stack.
    #
    # While at least one lexical scope remains to be found on the call stack...
    # print(f'{func_label} local scope capturing!')
    while func_scopes_name_index >= 0:
        # Current lexical scope to be searched for in the call stack.
        func_scope_name_curr = func_scopes_name[func_scopes_name_index]

        # While at least one frame remains on the call stack, iteratively
        # search up the call stack until finding a parent callable embodying
        # this lexical scope.
        #
        # Note this also implicitly skips past all other decorators applied
        # *AFTER* (i.e., lexically above) @beartype to this nested callable:
        # e.g.,
        #
        #     # This also skips past all decorators listed above @beartype.
        #     @the_way_of_kings
        #     @words_of_radiance
        #     @oathbringer
        #     @rhythm_of_war
        #     @beartype
        #     def the_stormlight_archive(bruh: str) -> str:
        #         return bruh
        while func_frame:
            # Code object underlying this frame's callable if that callable is
            # pure-Python *OR* "None" otherwise.
            func_frame_codeobj = get_func_codeobj_or_none(func_frame)

            # If that callable is pure-Python, that code object exists. In this
            # case...
            if func_frame_codeobj is not None:
                # Fully-qualified name of that callable's module.
                func_frame_module_name = func_frame.f_globals['__name__']

                # Unqualified name of that callable.
                func_frame_name = func_frame_codeobj.co_name

                # If...
                if (
                    # That callable's name is that of the current lexical scope
                    # to be found *AND*...
                    func_frame_name == func_scopes_name_curr and
                    # That callable's module is that of this nested callable's
                    # and thus resides in the same lexical scope...
                    func_frame_module_name == func_module_name
                ):
                    # Then that callable embodies the current lexical scope to
                    # be found. In this case...

                    # Merge the local scope of that callable into the local scope
                    # of this nested callable in a safe manner preserving all
                    # locals already defined by inner closures such that all
                    # locals already defined by inner closures take precedence
                    # over locals subsequently defined by outer callables.
                    #
                    # Note that:
                    # * This assignment intentionally does *NOT* resemble:
                    #       func_locals.update(func_frame_locals)
                    #   Why? Because doing so would unsafely override locals
                    #   already defined by inner closures with locals
                    #   subsequently defined by outer callables.
                    # * This assignment is semantically equivalent to:
                    #       func_locals |= func_frame.f_locals
                    #   Sadly, that syntax is only available under Python >= 3.9
                    #   via "PEP 584 -- Add Union Operators To dict."
                    func_locals = {**func_frame.f_locals, **func_locals}

                    # Halt inner iteration, since we have now found and handled
                    # a parent callable embodying this lexical scope.
                    break
                # Else, that callable does *NOT* embody the current lexical
                # scope to be found. In this case, silently ignore that
                # callable and proceed to the next frame in the call stack.
            # Else, that callable is C-based. In this case, silently ignore
            # that callable and proceed to the next frame in the call stack.

            # Iterate to the next frame on the call stack.
            func_frame = func_frame.f_back

        # If *NO* frames remain on the call stack, the above iteration failed
        # to find a parent callable on the stack embodying the current lexical
        # scope. In this case, raise an exception.
        if func_frame is None:
            raise exception_cls(
                f'{func_label} parent lexical scope '
                f'"{func_scope_name_curr}" not found on call stack.'
            )

        # Iterate to the next lexical scope to be found.
        func_scopes_name_index += -1

    # Return this nested callable's local scope.
    #
    # Note that this scope *CANNOT* be validated to declare this nested
    # callable. Why? Because this getter function is called by the @beartype
    # decorator when decorating this nested callable, which has yet to be
    # declared until @beartype creates and returns a new wrapper function and
    # is thus unavailable from this scope: e.g.,
    #
    #     # This conditional *ALWAYS* raises an exception, because this nested
    #     # callable has yet to be declared.
    #     if func_name not in func_locals:
    #         raise exception_cls(
    #             f'{func_label} not declared by lexically scoped parent '
    #             f'callable(s) that declared local variables:\n{repr(func_locals)}'
    #         )
    #
    # Ergo, we have *NO* alternative but to blindly assume the above algorithm
    # correctly collected this scope, which we only do because we have
    # exhaustively tested this with *ALL* possible edge cases.
    return func_locals
