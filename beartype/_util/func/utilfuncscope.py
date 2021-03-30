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
from beartype._util.utilobject import get_object_scopes_name
from collections.abc import Callable
from types import CodeType
from typing import Any, Dict, Optional

# ....................{ HINTS                             }....................
CallableScope = Dict[str, Any]
'''
PEP-compliant type hint matching a **callable socpe** (i.e., dictionary mapping
from the name to value of each locally or globally scoped variable accessible
to a callable).
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
    # one or more "." delimiters, each signifying a nested lexical scope. Since
    # *ALL* callables (i.e., both pure-Python and C-based) define a non-empty
    # "__qualname__" dunder variable containing at least their unqualified
    # names, this simplistic test is guaranteed to be safe.
    #
    # Note this function intentionally tests for the general-purpose existence
    # of a "." delimiter rather than the special-cased existence of a
    # ".<locals>." placeholder substring. Why? Because there are two types of
    # nested callables:
    # * Non-methods, which are lexically nested in a parent callable whose
    #   scope encapsulates all previously declared local variables. For unknown
    #   reasons, the unqualified names of nested non-method callables are
    #   *ALWAYS* prefixed by ".<locals>." in their "__qualname__" variables:
    #       >>> from collections.abc import Callable
    #       >>> def muh_parent_callable() -> Callable:
    #       ...     def muh_nested_callable() -> None: pass
    #       ...     return muh_nested_callable
    #       >>> muh_nested_callable = muh_parent_callable()
    #       >>> muh_parent_callable.__qualname__
    #       'muh_parent_callable'
    #       >>> muh_nested_callable.__qualname__
    #       'muh_parent_callable.<locals>.muh_nested_callable'
    # * Methods, which are lexically nested in the scope encapsulating all
    #   previously declared class variables (i.e., variables declared in class
    #   scope and thus accessible as method annotations). For unknown reasons,
    #   the unqualified names of methods are *NEVER* prefixed by ".<locals>."
    #   in their "__qualname__" variables: e.g.,
    #       >>> from typing import ClassVar
    #       >>> class MuhClass(object):
    #       ...    # Class variable declared in class scope.
    #       ...    muh_class_var: ClassVar[type] = int
    #       ...    # Instance method annotated by this class variable.
    #       ...    def muh_method(self) -> muh_class_var: return 42
    #       >>> MuhClass.muh_method.__qualname__
    #       'MuhClass.muh_method'
    return '.' in func.__qualname__


#FIXME: Unit test us up.
#FIXME: Technically, we currently don't call this anywhere. But we probably
#will someday, so let's preserve this intact until then. *shrug*
# def is_func_closure(func: Callable) -> bool:
#     '''
#     ``True`` only if the passed callable is a **closure** (i.e.,
#     nested callable accessing one or more variables declared by the parent
#     callable also declaring that callable).
#
#     Note that all closures are necessarily nested callables but that the
#     converse is *not* necessarily the case. In particular, a nested callable
#     accessing no variables declared by the parent callable also declaring that
#     callable is *not* a closure.
#
#     Parameters
#     ----------
#     func : Callable
#         Callable to be inspected.
#
#     Returns
#     ----------
#     bool
#         ``True`` only if this callable is a closure.
#     '''
#     assert callable(func), f'{repr(func)} not callable.'
#
#     # Return true only if this callable defines a closure-specific dunder
#     # attribute.
#     #
#     # Note that the "__closure__" dunder variable is either:
#     # * If this callable is a closure, a tuple of zero or more cell variables.
#     # * If this callable is a pure-Python non-closure, "None".
#     # * If this callable is C-based, undefined.
#     return getattr(func, '__closure__', None) is not None

# ....................{ GETTERS                           }....................
#FIXME: Unit test us up, please.
def get_func_globals(
    # Mandatory parameters.
    func: Callable,

    # Optional parameters.
    exception_cls: type = _BeartypeUtilCallableException,
) -> CallableScope:
    '''
    **Global scope** (i.e., a dictionary mapping from the name to value of each
    globally scoped attribute declared by the module transitively declaring
    the passed pure-Python callable) for this callable.

    This getter transparently supports **wrapper callables** (i.e.,
    higher-level callables whose identifying metadata was propagated from other
    lowel-level callables at either decoration time via the
    :func:`functools.wraps` decorator *or* after declaration via the
    :func:`functools.update_wrapper` function).
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
    Dict[str, Any]
        Global scope for this callable.

    Raises
    ----------
    exception_cls
        If this callable is a wrapper wrapping a C-based rather than
        pure-Python wrappee callable.
    '''
    assert callable(func), f'{repr(func)} not callable.'

    # Avoid circular import dependencies.
    from beartype._util.func.utilfuncwrap import unwrap_func

    # If this callable is *NOT* pure-Python, raise an exception. C-based
    # callables do *NOT* define the "__globals__" dunder attribute.
    die_unless_func_python(func=func, exception_cls=exception_cls)
    # Else, this callable is pure-Python.

    # Lowest-level wrappee callable wrapped by this wrapper callable.
    func_wrappee = unwrap_func(func)

    # Dictionary mapping from the name to value of each locally scoped
    # attribute accessible to this wrappee callable to be returned.
    #
    # Note that we intentionally do *NOT* return the global scope for this
    # wrapper callable, as wrappers are typically defined in different modules
    # (and thus different global scopes) by different module authors.
    return func_wrappee.__globals__  # type: ignore[attr-defined]


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

def get_func_locals(
    # Mandatory parameters.
    func: Callable,

    # Optional parameters.
    func_stack_frames_ignore: int = 0,
    exception_cls: type = _BeartypeUtilCallableException,
) -> CallableScope:
    '''
    **Local scope** for the passed callable.

    This getter returns either:

    * If this callable is **nested** (i.e., is a method *or* is a non-method
      callable declared in the body of another callable), a dictionary mapping
      from the name to value of each **locally scoped attribute** (i.e., local
      attribute declared by a parent callable transitively declaring this
      callable) accessible to this callable.
    * Else, the empty dictionary otherwise (i.e., if this callable is a
      function directly declared by a module).

    This getter transparently supports methods, which in Python are lexically
    nested in the scope encapsulating all previously declared **class
    variables** (i.e., variables declared from class scope and thus accessible
    as type hints when annotating the methods of that class). When declaring a
    class, Python creates a stack frame for the declaration of that class whose
    local scope is the set of all class-scope attributes declared in the body
    of that class (including class variables, class methods, static methods,
    and instance methods). When passed any method, this getter finds and
    returns that local scope. When passed the ``MuhClass.muh_method` method
    declared by the following example, for example, this getter returns the
    local scope containing the key ``'muh_class_var'`` with value ``int``:

    .. code-block:: python

       >>> from typing import ClassVar
       >>> class MuhClass(object):
       ...    # Class variable declared in class scope.
       ...    muh_class_var: ClassVar[type] = int
       ...    # Instance method annotated by this class variable.
       ...    def muh_method(self) -> muh_class_var: return 42

    Caveats
    ----------
    **This high-level getter requires the private low-level**
    :func:`sys._getframe` **getter.** If that getter is undefined, this getter
    unconditionally treats this callable as module-scoped by returning the
    empty dictionary rather than raising an exception. Since all standard
    Python implementations (e.g., CPython, PyPy) define that getter, this
    should typically *not* be a real-world concern.

    **This high-level getter is inefficient and should thus only be called if
    absolutely necessary.** Specifically, deciding the local scope for any
    callable is an ``O(k)`` operation for ``k`` the distance in call stack
    frames between the call to the current function and the call to the parent
    scope declaring that callable. Ergo, this decision problem should be
    deferred as long as feasible to minimize space and time consumption.

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
    Dict[str, Any]
        Local scope for this callable.

    Raises
    ----------
    exception_cls
        If the next non-ignored frame following the last ignored frame is *not*
        the parent callable or module directly declaring the passed callable.
    '''
    assert callable(func), f'{repr(func)} not callable.'
    # print(f'Capturing {func.__qualname__}() local scope...')

    # Avoid circular import dependencies.
    from beartype._util.func.utilfuncstack import get_func_stack_frame

    # If this callable is nested *AND* the active Python interpreter declares
    # the sys._getframe() getter...
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
    if is_func_nested(func) and get_func_stack_frame is not None:
        assert isinstance(func_stack_frames_ignore, int), (
            f'{func_stack_frames_ignore} not integer.')
        assert func_stack_frames_ignore >= 0, (
            f'{func_stack_frames_ignore} negative.')

        # print(f'Capturing nested {func.__qualname__}() local scope...')
        # ................{ LOCALS ~ func                     }................
        # Fully-qualified name of the module declaring this nested callable if
        # this nested callable was physically declared by an on-disk module
        # *OR* "None".
        func_module_name = func.__module__

        # Unqualified name of this nested callable.
        func_name = func.__name__

        # ................{ LOCALS ~ scope                    }................
        # Fully-qualified name of this callable.
        func_scopes = func.__qualname__

        # Unqualified name of the last lexical scope encapsulating this nested
        # callable.
        #
        # Note that:
        # * If this is a nested non-method callable, this name is the useless
        #   "<locals>" placeholder substring identifying the parent callable of
        #   this nested non-method callable: e.g.,
        #       # For a closure muh_closure() declared in a function muh_func()...
        #       >>> func.__qualname__
        #       'muh_func.<locals>.muh_closure'
        #       >>> func_scopes_name
        #       ['muh_func', '<locals>', 'muh_closure']
        # * The set of all callables embodied by the current runtime call stack
        #   is a (typically proper) superset of the set of all callables
        #   embodied by the lexical scopes encapsulating this nested callable.
        #   Ergo, some stack frames have no corresponding lexical scopes (e.g.,
        #   stack frames embodying callables defined by different modules) but
        #   *ALL* lexical scopes have a corresponding stack frame.
        # * Stack frames are only efficiently accessible relative to the
        #   initial stack frame embodying this nested callable, which resides
        #   at the end of the call stack. This implies we *MUST* iteratively
        #   search up:
        #   * The call stack for frames with relevant lexical scopes and ignore
        #     intervening frames with irrelevant lexical scopes, beginning at
        #     the end of that stack.
        #   * Lexical scopes for scopes with corresponding frames, beginning at
        #     the last lexical scope.
        func_scopes_name = func_scopes.rsplit(sep='.', maxsplit=3)

        # Assert this nested callable is encapsulated by at least two
        # lexical scopes identifying at least this nested callable and the
        # parent callable or class declaring this nested callable.
        assert len(func_scopes_name) >= 2, (
            f'{func_name}() not nested (i.e., fully-qualified name '
            f'"{func_scopes}" is unqualified name "{func_name}").')
        assert func_scopes_name[-1] == func_name, (
            f'{func_name}() fully-qualified name "{func_scopes}" invalid '
            f'(i.e., last lexical scope '
            f'"{func_scopes_name[-1]}" not unqualified name "{func_name}").')

        # Lexical scope encapsulating the parent callable directly containing
        # and thus declaring this nested callable -- which by the above
        # validation is guaranteed.to be the third-to-last string in this list
        # of lexical scopes.
        #
        # Note that that parent callable's local runtime scope transitively
        # contains *ALL* local variables accessible to this nested callable
        # (including the local variables directly contained in the body of that
        # parent callable as well as the local variables directly contained in
        # the bodies of all parent callables of that callable in the same
        # lexical scope). Since that parent callable's local runtime scope is
        # exactly the dictionary to be returned, iteration below searches up
        # the runtime call stack for a stack frame embodying that parent
        # callable and no further.
        func_scope_name = func_scopes_name[-2]

        # If this lexical scope is a placeholder substring specific to nested
        # non-method callables, ignore this placeholder by preferring the
        # actual lexical scope preceding this placeholder.
        if func_scope_name == '<locals>':
            assert len(func_scopes_name) >= 3, (
                f'{func_name}() fully-qualified name "{func_scopes}" invalid '
                f'(i.e., placeholder substring "<locals>" not preceded by '
                f'unqualified name of parent callable).')
            func_scope_name = func_scopes_name[-3]

        # ................{ LOCALS ~ frame                    }................
        # Next non-ignored frame following the last ignored frame, ignoring an
        # additional frame embodying the current call to this getter.
        func_frame = get_func_stack_frame(func_stack_frames_ignore + 1)

        # Code object underlying the parent callable associated with the
        # current stack frame if that callable is pure-Python *OR* "None".
        func_frame_codeobj: Optional[CodeType] = None

        # Fully-qualified name of that callable's module.
        func_frame_module_name = ''

        # Unqualified name of that callable.
        func_frame_name = ''

        # ................{ SEARCH                            }................
        # While at least one frame remains on the call stack, iteratively
        # search up the call stack for a stack frame embodying the parent
        # callable directly declaring this nested callable, whereupon that
        # parent callable's local runtime scope is returned as is.
        #
        # Note this also implicitly skips past all other decorators applied
        # *AFTER* (i.e., lexically above) @beartype to this nested callable:
        # e.g.,
        #     # This also skips past all decorators listed above @beartype.
        #     @the_way_of_kings
        #     @words_of_radiance
        #     @oathbringer
        #     @rhythm_of_war
        #     @beartype
        #     def the_stormlight_archive(bruh: str) -> str:
        #         return bruh
        while func_frame:
            # Code object underlying this frame's scope if that scope is
            # pure-Python *OR* "None" otherwise.
            func_frame_codeobj = get_func_codeobj_or_none(func_frame)

            # If that scope is pure-Python, that code object exists. In this
            # case...
            if func_frame_codeobj is not None:
                # Fully-qualified name of that scope's module.
                func_frame_module_name = func_frame.f_globals['__name__']

                # Unqualified name of that scope.
                func_frame_name = func_frame_codeobj.co_name
                # print(f'{func_frame_name}() locals: {repr(func_frame.f_locals)}')

                # If that scope is a module, this search has just crossed a
                # module boundary and is thus no longer searching within the
                # module declaring this nested callable and has thus failed to
                # find the lexical scope of the parent declaring this nested
                # callable. Why? Because that scope *MUST* necessarily be in
                # the same module as that of this nested callable. In this
                # case, immediately break and raise an exception.
                if func_frame_name == '<module>':
                    break
                # Else, that scope is *NOT* a module.
                #
                # If...
                elif (
                    # That callable's name is that of the current lexical scope
                    # to be found *AND*...
                    func_frame_name == func_scope_name and
                    # That callable's module is that of this nested callable's
                    # and thus resides in the same lexical scope...
                    func_frame_module_name == func_module_name
                ):
                # Then that callable embodies the lexical scope to be found. In
                # this case, that callable is the parent callable directly
                # declaring this nested callable.
                #
                # Note that this scope *CANNOT* be validated to declare this
                # nested callable. Why? Because this getter function is called
                # by the @beartype decorator when decorating this nested
                # callable, which has yet to be declared until @beartype
                # creates and returns a new wrapper function and is thus
                # unavailable from this scope: e.g.,
                #
                #     # This conditional *ALWAYS* raises an exception, because
                #     # this nested callable has yet to be declared.
                #     if func_name not in func_locals:
                #         raise exception_cls(
                #             f'{func_label} not declared by lexically scoped parent '
                #             f'callable(s) that declared local variables:\n{repr(func_locals)}'
                #         )
                #
                # Ergo, we have *NO* alternative but to blindly assume the
                # above algorithm correctly collected this scope, which we only
                # do because we have exhaustively tested this with *ALL*
                # possible edge cases.
                    # print(f'{func_scopes_name_curr}() locals: {repr(func_frame.f_locals)}')

                    # Return the local scope of this nested callable. Since
                    # this nested callable is directly declared in the body of
                    # this parent callable, the local scope of this nested
                    # callable is *EXACTLY* the local scope of the body of this
                    # parent callable. Well, isn't that special?
                    return func_frame.f_locals
                # Else, that callable does *NOT* embody the current lexical
                # scope to be found. In this case, silently ignore that
                # callable and proceed to the next frame in the call stack.
            # Else, that callable is C-based. In this case, silently ignore
            # that callable and proceed to the next frame in the call stack.

            # Iterate to the next frame on the call stack.
            func_frame = func_frame.f_back

        # Since the above iteration exhausted itself rather than returning,
        # that iteration failed to find the frame embodying the parent callable
        # declaring this nested callable. In this case, raise an exception.
        raise exception_cls(
            f'{get_object_scopes_name(func)}() parent lexical scope '
            f'"{func_scope_name}" not found on call stack.'
        )
    # Else, either this callable is unnested and thus module-scoped *OR* this
    # interpreter does *NOT* declare that getter. In either case, we
    # unconditionally treat this nested callable as module-scoped by preserving
    # "func_locals" as the empty dictionary.
    return {}
