#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2022 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **callable scope** utilities (i.e., functions handling the
possibly nested lexical scopes enclosing arbitrary callables).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                           }....................
from beartype.roar._roarexc import _BeartypeUtilCallableException
from beartype._util.utilobject import get_object_basename_scoped
from beartype._data.datatyping import TypeException
from collections.abc import Callable
from types import CodeType
from typing import Any, Dict, Optional

# See the "beartype.cave" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

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
#     # attribute whose value is either:
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
    exception_cls: TypeException = _BeartypeUtilCallableException,
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
    exception_cls : Type[Exception], optional
        Type of exception to be raised in the event of a fatal error. Defaults
        to :class:`_BeartypeUtilCallableException`.

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
    from beartype._util.func.utilfunctest import die_unless_func_python
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


def get_func_locals(
    # Mandatory parameters.
    func: Callable,

    # Optional parameters.
    func_stack_frames_ignore: int = 0,
    exception_cls: TypeException = _BeartypeUtilCallableException,
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
    frames from the call to the current function to the call to the top-most
    parent scope transitively declaring the passed callable in its submodule.
    Ergo, this decision problem should be deferred as long as feasible to
    minimize space and time consumption.

    Parameters
    ----------
    func : Callable
        Callable to be inspected.
    func_stack_frames_ignore : int, optional
        Number of frames on the call stack to be ignored (i.e., silently
        incremented past), such that the next non-ignored frame following the
        last ignored frame is the parent callable or module directly declaring
        the passed callable. Defaults to 0.
    exception_cls : Type[Exception], optional
        Type of exception to be raised in the event of a fatal error. Defaults
        to :class:`_BeartypeUtilCallableException`.

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
    assert isinstance(func_stack_frames_ignore, int), (
        f'{func_stack_frames_ignore} not integer.')
    assert func_stack_frames_ignore >= 0, (
        f'{func_stack_frames_ignore} negative.')
    # print(f'\n--------- Capturing nested {func.__qualname__}() local scope...')

    # ..................{ IMPORTS                           }..................
    # Avoid circular import dependencies.
    from beartype._util.func.utilfunccodeobj import get_func_codeobj_or_none
    from beartype._util.func.utilfuncstack import iter_func_stack_frames

    # ..................{ NOOP                              }..................
    # Fully-qualified name of the module declaring the passed callable if that
    # callable was physically declared by an on-disk module *OR* "None"
    # otherwise (i.e., if that callable was dynamically declared in-memory).
    func_module_name = func.__module__

    # Note that we intentionally return the local scope for this wrapper rather
    # than wrappee callable, as local scope can *ONLY* be obtained by
    # dynamically inspecting local attributes bound to call frames on the
    # current call stack. However, this wrapper was called at a higher call
    # frame than this wrappee. All local attributes declared within the body of
    # this wrapper callable are irrelevant to this wrappee callable, as Python
    # syntactically parsed the latter at a later time than the former. If we
    # returned the local scope for this wrappee rather than wrapper callable,
    # we would erroneously return local attributes that this wrappee callable
    # originally had no lexical access to. That's bad. So, we don't do that.
    #
    # If either...
    if (
        # The passed callable is dynamically declared in-memory...
        func_module_name is None or
        # The passed callable is unnested *OR*...
        not is_func_nested(func)
    ):
        # Then silently reduce to a noop by treating this nested callable as
        # module-scoped by preserving "func_locals" as the empty dictionary.
        return {}
    # Else, all of the following constraints hold:
    # * The passed callable is physically declared on-disk.
    # * The passed callable is nested.

    # ..................{ LOCALS ~ scope                    }..................
    # Local scope of the passed callable to be returned.
    func_scope: CallableScope = {}

    # ..................{ LOCALS ~ scope : name             }..................
    # Unqualified name of this nested callable.
    func_name_unqualified = func.__name__

    # Fully-qualified name of this nested callable. If this nested callable is
    # a non-method, this name contains one or more meaningless placeholders
    # "<locals>" -- each identifying one parent callable lexically containing
    # this nested callable: e.g.,
    #     >>> def muh_func():
    #     ...     def muh_closure(): pass
    #     ...     return muh_closure()
    #     >>> muh_func().__qualname__
    #     'muh_func.<locals>.muh_closure'
    func_name_qualified = func.__qualname__

    # Non-empty list of the unqualified names of all parent callables lexically
    # containing this nested callable (including this nested callable itself).
    #
    # Note that:
    # * The set of all callables embodied by the current runtime call stack is
    #   a (usually proper) superset of the set of all callables embodied by the
    #   lexical scopes encapsulating this nested callable. Ergo:
    #   * Some stack frames have no corresponding lexical scopes (e.g., stack
    #     frames embodying callables defined by different modules).
    #   * *ALL* lexical scopes have a corresponding stack frame.
    # * Stack frames are only efficiently accessible relative to the initial
    #   stack frame embodying this nested callable, which resides at the end of
    #   the call stack. This implies we *MUST* iteratively search up the call
    #   stack for frames with relevant lexical scopes and ignore intervening
    #   frames with irrelevant lexical scopes, starting at the stack top (end).
    func_scope_names = func_name_qualified.rsplit(sep='.')

    # Assert this nested callable is encapsulated by at least two lexical
    # scopes identifying at least this nested callable and the parent callable
    # or class declaring this nested callable.
    assert len(func_scope_names) >= 2, (
        f'{func_name_unqualified}() not nested (i.e., fully-qualified name '
        f'"{func_name_qualified}" == unqualified name '
        f'"{func_name_unqualified}").')

    # If the unqualified name of the last parent callable lexically containing
    # the passed callable is *NOT* that callable itself, the caller maliciously
    # renamed one but *NOT* both of the dunder attributes of that callable
    # uniquely identifying that callable. In this case, raise an exception.
    if func_scope_names[-1] != func_name_unqualified:
        raise exception_cls(
            f'{func_name_unqualified}() fully-qualified name '
            f'{func_name_qualified}() invalid (i.e., last lexical scope '
            f'"{func_scope_names[-1]}" != unqualified name '
            f'"{func_name_unqualified}").'
        )

    # Unqualified name of the parent callable directly lexically containing
    # (and thus declaring) the passed callable -- which by the above validation
    # is guaranteed to be the second-to-last string in this list of names.
    #
    # Note that that the parent callable's local runtime scope transitively
    # contains *ALL* local variables accessible to this nested callable
    # (including the local variables directly contained in the body of that
    # parent callable as well as the local variables directly contained in the
    # bodies of all parent callables of that callable in the same lexical
    # scope). Since that parent callable's local runtime scope is exactly the
    # dictionary to be returned, iteration below searches up the runtime call
    # stack for a stack frame embodying that parent callable and no further.
    func_scope_name = func_scope_names[-2]

    # If this name is the placeholder substring specific to nested callables...
    if func_scope_name == '<locals>':
        # If this list contains less than three names, this list *MUST* contain
        # exactly two names, since this list is neither empty *NOR* contains
        # exactly one name. In this case, this name *MUST* by deduction have
        # been the first in this list.
        #
        # But this placeholder substring *MUST* be preceded by the name of a
        # parent callable. Since this is *NOT* the case, the caller maliciously
        # renamed the "__qualname__" dunder attributes of the passed callable
        # to be prefixed by "<locals>". In this case, raise an exception.
        if len(func_scope_names) < 3:
            raise exception_cls(
                f'{func_name_unqualified}() fully-qualified name '
                f'{func_name_qualified}() invalid (i.e., placeholder '
                f'substring "<locals>" not preceded by parent callable name).'
            )

        # Skip over this placeholder to the unqualified name of the parent
        # callable lexically containing the passed callable.
        func_scope_name = func_scope_names[-3]
    # print(f'Searching for parent {func_scope_name}() local scope...')

    # ..................{ LOCALS ~ frame                    }..................
    # Code object underlying the parent callable associated with the current
    # stack frame if that callable is pure-Python *OR* "None".
    func_frame_codeobj: Optional[CodeType] = None

    # Fully-qualified name of that callable's module.
    func_frame_module_name = ''

    # Unqualified name of that callable.
    func_frame_name = ''

    # ..................{ SEARCH                            }..................
    # While at least one frame remains on the call stack, iteratively search up
    # the call stack for a stack frame embodying the parent callable directly
    # declaring this nested callable, whereupon that parent callable's local
    # runtime scope is returned as is.
    #
    # Note this also implicitly skips past all other decorators applied *AFTER*
    # @beartype (and thus residing lexically above @beartype) in caller code to
    # this nested callable: e.g.,
    #     @the_way_of_kings   <--- skipped past
    #     @words_of_radiance  <--- skipped past
    #     @oathbringer        <--- skipped past
    #     @rhythm_of_war      <--- skipped past
    #     @beartype
    #     def the_stormlight_archive(bruh: str) -> str:
    #         return bruh
    for func_frame in iter_func_stack_frames(
        # 0-based index of the first non-ignored frame following the last
        # ignored frame, ignoring an additional frame embodying the current
        # call to this getter.
        func_stack_frames_ignore=func_stack_frames_ignore + 1,
    ):
        # Code object underlying this frame's scope if that scope is
        # pure-Python *OR* "None" otherwise.
        func_frame_codeobj = get_func_codeobj_or_none(func_frame)

        # If this code object does *NOT* exist, this scope is C-based. In this
        # case, silently ignore this scope and proceed to the next frame.
        if func_frame_codeobj is None:
            continue
        # Else, this code object exists, implying this scope is pure-Python.

        # Fully-qualified name of that scope's module.
        func_frame_module_name = func_frame.f_globals['__name__']

        # Unqualified name of that scope.
        func_frame_name = func_frame_codeobj.co_name
        # print(f'{func_frame_name}() locals: {repr(func_frame.f_locals)}')

        # If that scope is the placeholder string assigned by the active Python
        # interpreter to all scopes encapsulating the top-most lexical scope of
        # a module in the current call stack, this search has just crossed a
        # module boundary and is thus no longer searching within the module
        # declaring this nested callable and has thus failed to find the
        # lexical scope of the parent declaring this nested callable. Why?
        # Because that scope *MUST* necessarily be in the same module as that
        # of this nested callable. In this case, raise an exception.
        if func_frame_name == '<module>':
            raise exception_cls(
                f'{get_object_basename_scoped(func)}() parent lexical scope '
                f'{func_scope_name}() not found on call stack.'
            )
        # Else, that scope is *NOT* a module.
        #
        # If...
        elif (
            # That callable's name is that of the current lexical scope to be
            # found *AND*...
            func_frame_name == func_scope_name and
            # That callable's module is that of this nested callable's and thus
            # resides in the same lexical scope...
            func_frame_module_name == func_module_name
        ):
        # Then that callable embodies the lexical scope to be found. In this
        # case, that callable is the parent callable directly declaring this
        # nested callable.
        #
        # Note that this scope *CANNOT* be validated to declare this nested
        # callable. Why? Because this getter function is called by the
        # @beartype decorator when decorating this nested callable, which has
        # yet to be declared until @beartype creates and returns a new wrapper
        # function and is thus unavailable from this scope: e.g.,
        #     # This conditional *ALWAYS* raises an exception, because this
        #     # nested callable has yet to be declared.
        #     if func_name not in func_locals:
        #         raise exception_cls(
        #             f'{func_label} not declared by lexically scoped parent '
        #             f'callable(s) that declared local variables:\n{repr(func_locals)}'
        #         )
        #
        # Ergo, we have *NO* alternative but to blindly assume the above
        # algorithm correctly collected this scope, which we only do because we
        # have exhaustively tested this with *ALL* edge cases.
            # print(f'{func_frame_name}() locals: {repr(func_frame.f_locals)}')

            # Local scope of the passed callable. Since this nested callable is
            # directly declared in the body of this parent callable, the local
            # scope of this nested callable is *EXACTLY* the local scope of the
            # body of this parent callable. Well, isn't that special?
            func_scope = func_frame.f_locals

            # Halt iteration.
            break
        # Else, that callable does *NOT* embody the current lexical scope to be
        # found. In this case, silently ignore that callable and proceed to the
        # next frame in the call stack.

    # Return the local scope of the passed callable.
    return func_scope

# ....................{ ADDERS                            }....................
def add_func_scope_attr(
    # Mandatory parameters.
    attr: Any,
    func_scope: CallableScope,

    # Optional parameters.
    exception_prefix: str = 'Globally or locally scoped attribute ',
) -> str:
    '''
    Add a new **scoped attribute** (i.e., new key-value pair of the passed
    dictionary mapping from the name to value of each globally or locally
    scoped attribute externally accessed elsewhere, whose key is a
    machine-readable name internally generated by this function to uniquely
    refer to the passed object and whose value is that object) to the passed
    scope *and* return that name.

    Parameters
    ----------
    attr : Any
        Arbitrary object to be added to this scope.
    func_scope : CallableScope
        Local or global scope to add this object to.
    exception_prefix : str, optional
        Human-readable label prefixing the representation of this object in the
        exception message. Defaults to the empty string.

    Returns
    ----------
    str
        Name of the passed object in this scope generated by this function.

    Raises
    ----------
    :exc:`_BeartypeUtilCallableException`
        If an attribute with the same name as that internally generated by
        this adder but having a different value already exists in this scope.
        This adder uniquifies names by object identifier and should thus
        *never* generate name collisions. This exception is thus intentionally
        raised as a private rather than public exception.
    '''
    assert isinstance(func_scope, dict), f'{repr(func_scope)} not dictionary.'
    assert isinstance(exception_prefix, str), (
        f'{repr(exception_prefix)} not string.')

    # Name of the new attribute referring to this object in this scope, mildly
    # obfuscated so as to avoid name collisions.
    attr_name = f'__beartype_object_{id(attr)}'

    # If an attribute with the same name but differing value already exists in
    # this scope, raise an exception.
    if func_scope.get(attr_name, attr) is not attr:
        raise _BeartypeUtilCallableException(
            f'{exception_prefix}"{attr_name}" already exists with differing value:\n'
            f'~~~~[ NEW VALUE ]~~~~\n{repr(attr)}\n'
            f'~~~~[ OLD VALUE ]~~~~\n{repr(func_scope[attr_name])}'
        )
    # Else, either no attribute with this name exists in this scope *OR* an
    # attribute with this name and value already exists in this scope.

    # Refer to the passed object in this scope with this name.
    func_scope[attr_name] = attr

    # Return this name.
    return attr_name
