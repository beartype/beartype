#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **call stack frame utilities** (i.e., callables introspecting the
current stack of frame objects, encapsulating the linear chain of calls to
external callables underlying the call to the current callable).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
import sys
from beartype.roar._roarexc import _BeartypeUtilCallFrameException
from beartype._cave._cavefast import CallableFrameType
from beartype._data.typing.datatyping import (
    LexicalScope,
    MappingStrToAny,
    TypeException,
)
from collections.abc import (
    Callable,
    Iterable,
    Mapping,
)
from typing import Optional

# ....................{ TESTERS                            }....................
#FIXME: Unit test us up, please.
def is_frame_caller_beartype(
    # Optional parameters.
    ignore_frames: int = 1,
    is_beartype_test: bool = False,
    exception_cls: TypeException = _BeartypeUtilCallFrameException,
) -> bool:
    '''
    :data:`True` only if the **caller** (i.e., callable directly calling this
    getter) resides inside the :mod:`beartype` codebase.

    This tester implicitly ignores the current call to this getter by
    unconditionally adding ``1`` to the passed number of stack frames.

    Parameters
    ----------
    ignore_frames : int, optional
        Number of stack frames on the current call stack to ignore (excluding
        the stack frame encapsulating the call to this getter). Defaults to 1,
        signifying the stack frame of the **caller** directly calling this
        getter.
    is_beartype_test : bool, optional
        :data:`True` only if this tester additionally returns :data:`True` when
        the caller resides inside the related :mod:`beartype_test` codebase.
        Defaults to :data:`False`; thus, this tester returns :data:`False` when
        the caller resides inside the related :mod:`beartype_test` codebase by
        default and treats :mod:`beartype_test` as an external third-party.
    exception_cls : TypeException, optional
        Type of exception to be raised in the event of a fatal error. Defaults
        to :class:`._BeartypeUtilCallFrameException`.

    Returns
    -------
    bool
        :data:`True` only if the caller is in the :mod:`beartype` codebase.
    '''
    assert isinstance(ignore_frames, int), f'{repr(ignore_frames)} not integer.'
    assert isinstance(is_beartype_test, bool), (
        f'{repr(is_beartype_test)} not bool.')

    # Fully-qualified name of the (sub)module declaring the caller (i.e.,
    # callable directly calling this dunder method) if that callable has a
    # (sub)module *or* "None" otherwise (e.g., if that callable resides outside
    # a module, usually due to being declared in an interactive REPL).
    frame_caller_module_name = get_frame_caller_module_name_or_none(
        ignore_frames=ignore_frames + 1, exception_cls=exception_cls)

    # Return true only if
    return (
        # The caller resides inside a module structure *AND*...
        frame_caller_module_name is not None and
        # Either...
        (
            # The caller resides inside the "beartype" package *OR*...
            frame_caller_module_name.startswith('beartype.') or
            (
                # The caller requests that the "beartype_test" package be
                # conflated with the "beartype" package *AND*...
                is_beartype_test and
                # The caller resides inside the "beartype_test" package...
                frame_caller_module_name.startswith('beartype_test.')
            )
        )
    )

# ....................{ GETTERS                            }....................
def get_frame_or_none(
    # Optional parameters.
    ignore_frames: int = 1,
    exception_cls: TypeException = _BeartypeUtilCallFrameException,
) -> Optional[CallableFrameType]:
    '''
    **Stack frame** (i.e., :class:`.CallableFrameType` object) on the current
    call stack *after* ignoring the passed number of stack frames.

    This getter implicitly ignores the current call to this getter by
    unconditionally adding ``1`` to the passed number of stack frames, implying
    this semantic interpretation of the passed number:

    * If ``ignore_frames == 0``, this getter returns the stack frame of the
      **caller** directly calling this getter. Since callers already know
      their own syntactic and semantic context, this is generally useless.
      Instead, callers typically want to ensure that ``ignore_frames >= 1``.
    * If ``ignore_frames == 1``, this getter returns the stack frame of the
      **parent caller** calling the caller directly calling this getter.
      Unsurprisingly, this is the standard use case and thus the default.
    * If ``ignore_frames == 2``, this getter returns the stack frame of the
      **parent parent caller** calling the parent caller calling the caller
      directly calling this getter.

    Caveats
    -------
    **This higher-level getter should typically be called in lieu of the
    lower-level** :func:`.get_frame` **getter.** The former handles edge cases
    and validates the passed input, whereas the latter is lower-level and thus
    more fragile with respect to both edge cases and input.

    Parameters
    ----------
    ignore_frames : int
        Number of stack frames on the current call stack to ignore (excluding
        the stack frame encapsulating the call to this getter). Defaults to 1,
        signifying the stack frame of the **parent caller** calling the caller
        directly calling this getter.
    exception_cls : TypeException, default: _BeartypeUtilCallFrameException
        Type of exception to be raised in the event of a fatal error. Defaults
        to :class:`._BeartypeUtilCallFrameException`.

    Returns
    -------
    Optional[CallableFrameType]
        Either:

        * If the active Python interpreter defines the private low-level
          :func:`sys._getframe` getter *and*...

          * If a stack frame exists on the current call stack *after* ignoring
            the passed number of stack frames, that frame.
          * Else, the requested frame exceeds the **frame height** (i.e., total
            number of stack frames) of the current call stack. In this case,
            :data:`None`.

        * Else, :data:`None`.

    Raises
    ------
    exception_cls
        If either:

        * ``ignore_frames`` is *not* an integer.
        * ``ignore_frames`` is a negative integer.
    '''

    # If the passed number of stack frames to ignore is *NOT* a non-negative
    # integer, raise an exception.
    if not isinstance(ignore_frames, int):
        raise exception_cls(f'{repr(ignore_frames)} not integer.')
    if ignore_frames < 0:
        raise exception_cls(f'{repr(ignore_frames)} not non-negative integer.')

    # If the active Python interpreter defines the private low-level
    # sys._getframe() getter...
    if get_frame is not None:
        # Attempt to return the stack frame on the current call stack *AFTER*
        # ignoring the passed number of stack frames (as well as the current
        # call to this getter).
        try:
            return get_frame(ignore_frames + 1)
        # If the above call to sys._getframe() raised a "ValueError" exception,
        # then "ignore_frames + 1 >= frame_height" where "frame_height" is the
        # total number of stack frames on the current call stack. In this case,
        # return "None" instead.
        except ValueError:
            pass
        # If the above call to sys._getframe() raised an "OverflowError"
        # exception, then "ignore_frames + 1 >= frame_height" is almost
        # certainly the case. This case thus reduces to the prior case. Ergo,
        # return "None" instead. This exception message resembles:
        #     OverflowError: Python int too large to convert to C int
        except OverflowError:
            pass
    # Else, this interpreter fails to define that getter. In this case, return
    # "None" instead.

    # Return "None" as a latch-ditch fallback.
    return None


#FIXME: Mypy insists the sys._getframe() getter can return "None" in certain
#edge cases. But... what are those? Official documentation is seemingly silent
#on the issue. *sigh*
get_frame: Optional[Callable[[int], Optional[CallableFrameType]]] = getattr(
    sys, '_getframe', None)
'''
Private low-level :func:`sys._getframe` getter if the active Python interpreter
declares this getter *or* :data:`None` otherwise (i.e., if this interpreter does
*not* declare this getter).

All standard Python interpreters supported by this package including both
CPython *and* PyPy declare this getter. Ergo, this attribute should *always* be
a valid callable rather than :data:`None`.

If this getter is *not* :data:`None`, this getter's signature and docstring
under CPython resembles:

::

    _getframe([depth]) -> frameobject

    Return a frame object from the call stack.  If optional integer depth is
    given, return the frame object that many calls below the top of the
    stack. If that is deeper than the call stack, ValueError is raised. The
    default for depth is zero, returning the frame at the top of the call
    stack.

    Frame objects provide these attributes:
        f_back          next outer frame object (this frame's caller)
        f_builtins      built-in namespace seen by this frame
        f_code          code object being executed in this frame
        f_globals       global namespace seen by this frame
        f_lasti         index of last attempted instruction in bytecode
        f_lineno        current line number in Python source code
        f_locals        local namespace seen by this frame
        f_trace         tracing function for this frame, or None

Caveats
-------
**The higher-level** :func:`.get_frame_or_none` **getter should typically be
called in lieu of this lower-level getter.** The former handles edge cases and
validates the passed input, whereas the latter is lower-level and thus more
fragile with respect to both edge cases and input.

Parameters
----------
depth : int
    0-based index of the stack frame on the current call stack to be returned.
    Defaults to 0, signifying the stack frame encapsulating the lexical scope
    directly calling this getter.

Returns
-------
CallableFrameType
    Stack frame with the passed index on the current call stack.

Raises
------
ValueError
    If this index exceeds the **height** (i.e., total number of stack frames)
    of the current call stack.
'''

# ....................{ GETTERS ~ attr                     }....................
#FIXME: Unit test up, please. *sigh*
def get_frame_globals(frame: CallableFrameType) -> LexicalScope:
    '''
    **Global scope** encapsulated by the passed **stack frame** (i.e.,
    :class:`.CallableFrameType` instance encapsulating all metadata describing a
    single call on the current call stack).

    Parameters
    ----------
    frame : CallableFrameType
        Stack frame to be inspected.

    Returns
    -------
    LexicalScope
        **Global scope** encapsulated by this frame.
    '''
    assert isinstance(frame, CallableFrameType), (
        f'{repr(frame)} not stack frame.')

    # Local scope of this frame to be yielded to the caller, possibly coerced
    # from a non-dictionary into a dictionary.
    frame_globals = _coerce_mapping_to_scope(frame.f_globals)

    # Return this global scope.
    return frame_globals


#FIXME: Unit test up, please. *sigh*
def get_frame_locals(frame: CallableFrameType) -> LexicalScope:
    '''
    **Local scope** encapsulated by the passed **stack frame** (i.e.,
    :class:`.CallableFrameType` instance encapsulating all metadata describing a
    single call on the current call stack).

    Parameters
    ----------
    frame : CallableFrameType
        Stack frame to be inspected.

    Returns
    -------
    LexicalScope
        **Local scope** encapsulated by this frame.
    '''
    assert isinstance(frame, CallableFrameType), (
        f'{repr(frame)} not stack frame.')

    # Local scope of this frame to be yielded to the caller, possibly coerced
    # from a non-dictionary into a dictionary.
    frame_locals = _coerce_mapping_to_scope(frame.f_locals)

    # Return this local scope.
    return frame_locals

# ....................{ GETTERS ~ name : package           }....................
#FIXME: Unit test us up, please.
def get_frame_package_name_or_none(frame: CallableFrameType) -> Optional[str]:
    '''
    Fully-qualified name of the (sub)package of the (sub)module declaring the
    callable whose code object is that of the passed **stack frame** (i.e.,
    :class:`.CallableFrameType` instance encapsulating all metadata describing a
    single call on the current call stack) if that (sub)module has a
    (sub)package *or* :data:`None` otherwise (e.g., if that (sub)module is
    either a top-level module or script residing outside any package structure).

    Parameters
    ----------
    frame : CallableFrameType
        Stack frame to be inspected.

    Returns
    -------
    Optional[str]
        Either:

        * If the callable described by this frame resides in a package, the
          fully-qualified name of that package.
        * Else, :data:`None`.

    Raises
    ------
    exception_cls
         If that callable has *no* code object and is thus *not* pure-Python.

    See Also
    --------
    :func:`beartype._util.func.utilfunccodeobj.get_func_codeobj_basename`
        Related getter getting the unqualified basename of that callable.
    '''
    assert isinstance(frame, CallableFrameType), (
        f'{repr(frame)} not stack frame.')

    # Fully-qualified name of the parent package of the child module declaring
    # the callable whose code object is that of this stack frame's if that
    # module declares its name *OR* the empty string otherwise (e.g., if that
    # module is either a top-level module or script residing outside any parent
    # package structure).
    frame_package_name = frame.f_globals.get('__package__')

    # Return the name of this parent package.
    return frame_package_name

# ....................{ GETTERS ~ name : module            }....................
#FIXME: Unit test us up, please.
def get_frame_caller_module_name_or_none(
    # Optional parameters.
    ignore_frames: int = 1,
    exception_cls: TypeException = _BeartypeUtilCallFrameException,
) -> Optional[str]:
    '''
    Fully-qualified name of the (sub)module declaring the **caller** (i.e.,
    callable directly calling this getter) if that callable has a (sub)module
    *or* :data:`None` (e.g., if that callable resides outside any module
    structure, typically due to being declared directly in an interactive REPL).

    This getter implicitly ignores the current call to this getter by
    unconditionally adding ``1`` to the passed number of stack frames.

    Parameters
    ----------
    ignore_frames : int
        Number of stack frames on the current call stack to ignore (excluding
        the stack frame encapsulating the call to this getter). Defaults to 1,
        signifying the stack frame of the **caller** directly calling this
        getter.
    exception_cls : TypeException, optional
        Type of exception to be raised in the event of a fatal error. Defaults
        to :class:`._BeartypeUtilCallFrameException`.

    Returns
    -------
    Optional[str]
        Either:

        * If the callable described by this frame resides in a module, the
          fully-qualified name of that module.
        * Else, :data:`None`.

    See Also
    --------
    :func:`beartype._util.func.utilfunccodeobj.get_func_codeobj_basename`
        Related getter getting the unqualified basename of that callable.
    '''

    # Stack frame of the caller directly calling this getter, obtained by
    # ignoring the stack frame of the current call to this getter.
    frame_caller = get_frame_or_none(
        ignore_frames=ignore_frames + 1, exception_cls=exception_cls)

    # Return either...
    return (
        # If this stack frame exists, return either the fully-qualified name of
        # the module defining the caller if the caller resides in a module *OR*
        # "None" otherwise (e.g., if the caller was defined in a REPL).
        get_frame_module_name_or_none(frame_caller)
        if frame_caller is not None else
        # Else, *NO* such stack frame exists, implying this getter was probably
        # directly called from an interactive REPL (e.g., "ipython"). In this
        # case, return "None".
        None
    )


#FIXME: Unit test us up, please.
def get_frame_module_name_or_none(frame: CallableFrameType) -> Optional[str]:
    '''
    Fully-qualified name of the (sub)module declaring the callable whose code
    object is that of the passed **stack frame** (i.e.,
    :class:`.CallableFrameType` instance encapsulating all metadata describing a
    single call on the current call stack) if that callable has a (sub)module
    *or* :data:`None` otherwise (e.g., if that callable resides outside any
    module structure, typically due to being declared directly in an interactive
    REPL).

    Parameters
    ----------
    frame : CallableFrameType
        Stack frame to be inspected.
    exception_cls : TypeException
        Type of exception to be raised in = _BeartypeUtilCallFrameException,

    Returns
    -------
    Optional[str]
        Either:

        * If the callable described by this frame resides in a module, the
          fully-qualified name of that module.
        * Else, :data:`None`.

    See Also
    --------
    :func:`beartype._util.func.utilfunccodeobj.get_func_codeobj_basename`
        Related getter getting the unqualified basename of that callable.
    '''
    assert isinstance(frame, CallableFrameType), (
        f'{repr(frame)} not stack frame.')

    # Fully-qualified name of the module declaring the callable described by
    # this frame.
    frame_module_name = frame.f_globals.get('__name__')

    # Return this name.
    return frame_module_name


#FIXME: Preserved for posterity. Currently unused, but potentially useful.
# from beartype._data.func.datafunccodeobj import FUNC_CODEOBJ_NAME_MODULE
# #FIXME: Unit test us up, please.
# def get_frame_name(
#     # Mandatory parameters.
#     frame: CallableFrameType,
#
#     # Optional parameters.
#     exception_cls: TypeException = _BeartypeUtilCallFrameException,
# ) -> str:
#     '''
#     Fully-qualified name of the callable whose code object is that of the passed
#     **stack frame** (i.e., :class:`types.CallableFrameType` instance
#     encapsulating all metadata describing a single call on the current call
#     stack).
#
#     Parameters
#     ----------
#     frame : CallableFrameType
#         Stack frame to be inspected.
#
#     Returns
#     -------
#     str
#         Fully-qualified name of the callable described by this frame.
#     '''
#
#     # Avoid circular import dependencies.
#     from beartype._util.func.utilfunccodeobj import get_func_codeobj_basename
#
#     # Fully-qualified name of the module declaring the callable described by
#     # this frame.
#     frame_module_name = get_frame_module_name_or_none(
#         frame=frame, exception_cls=exception_cls)
#
#     # Unqualified basename of that callable.
#     frame_basename = get_func_codeobj_basename(
#         func=frame, exception_cls=exception_cls)
#
#     # Possibly fully-qualified name of that callable, defined as either...
#     frame_name = (
#         # If that callable is *NOT* actually a callable but instead the
#         # top-level lexical scope of a module, omit the prefixing module name
#         # (which is, in any case, the meaningless magic string "<module>");
#         frame_basename
#         if frame_module_name == FUNC_CODEOBJ_NAME_MODULE else
#         # Else, that callable is actually a callable. In this case, prefix the
#         # unqualified basename of that callable by the fully-qualified name of
#         # the module declaring that callable.
#         f'{frame_module_name}.{frame_basename}'
#     )
#
#     # Return this name.
#     return frame_name

# ....................{ FINDERS                            }....................
def find_frame_caller_external(
    # Optional parameters.
    ignore_frames: int = 0,
    exception_cls: TypeException = _BeartypeUtilCallFrameException,
    exception_prefix: str = '',
    **kwargs
) -> CallableFrameType:
    '''
    First **external caller stack frame** (i.e., :class:`.CallableFrameType`
    object originating from any module or package *except* those residing in the
    :mod:`beartype` package itself) on the current call stack *after* ignoring
    the passed number of stack frames.

    This finder returns the stack frame originating from the third-party package
    or module that most recently directly called some public :mod:`beartype`
    function. Typically, that function is either of the statement-level
    :func:`beartype.door.die_if_unbearable` or :func:`beartype.door.is_bearable`
    type-checkers, which conditionally defer to this finder to resolve
    :pep:`484`-compliant relative forward references against the local and
    global lexical scopes of that external caller.

    Parameters
    ----------
    ignore_frames : int, default: 0
        Number of frames on the call stack to be ignored (i.e., silently
        incremented past), such that the next non-ignored frame following the
        last ignored frame is the parent callable or module directly declaring
        the passed callable. Defaults to 0.
    exception_cls : Type[Exception], default: _BeartypeUtilCallFrameException
        Type of exception to be raised in the event of a fatal error. Defaults
        to :class:`._BeartypeUtilCallFrameException`.
    exception_prefix : str, default: ''
        Human-readable substring prefixing raised exception messages. Defaults
        to the empty string.

    All remaining keyword parameters are passed as is to the lower-level
    :func:`.iter_frames` generator.

    Returns
    -------
    CallableFrameType
        Stack frame originating from the first external caller on the current
        call stack.

    Raises
    ------
    exception_cls
        If the call stack contains either:

        * *Only* the stack frame encapsulating the current call to this getter.
          Although an extreme edge case, this could technically occur if the
          caller called this getter from a REPL.
        * *Only* two or more ignorable stack frames.

    See Also
    --------
    :func:`.iter_frames`
        Further details.
    '''
    assert isinstance(ignore_frames, int), f'{ignore_frames} not integer.'
    assert ignore_frames >= 0, f'{ignore_frames} negative.'

    # ..................{ LOCALS                             }..................
    # Stack frame originating from the first external caller on the current
    # call stack.
    frame_caller_external: CallableFrameType = None  # type: ignore[assignment]

    # ..................{ SEARCH                             }..................
    # While at least one frame remains on the call stack, iteratively search up
    # the call stack for the first unignorable frame, whereupon that frame's
    # local runtime scope is returned as is.
    #
    # Note that exactly what "unignorable" means depends on whether the caller
    # passed additional keyword arguments. By default, this getter ignores *ALL*
    # scopes that either:
    # * Do *NOT* derive from a pure-Python object.
    # * Originate inside the "beartype" package.
    # * Originate outside a module.
    for frame_caller_external in iter_frames(
        # 0-based index of the first non-ignored frame following the last
        # ignored frame, ignoring an additional frame embodying the current call
        # to this getter.
        ignore_frames=ignore_frames + 1,
        **kwargs
    ):
    # Then this frame is the first unignorable frame to yield the local runtime
    # scope of to the caller. Why? Because the iter_frames() generator yielded
    # (rather than ignored) this frame. Assuming the caller passed *NO*
    # additional keyword parameters, this *MUST* be a frame encapsulating a
    # scope that:
    # * Derives from a pure-Python object.
    # * Originate outside the "beartype" package.
    # * Originate inside a module.
        # Halt iteration.
        break
    # If the above "break" statement was *NOT* performed, the above call to the
    # iter_frames() generator failed to yield even a single unignorable frame.
    # Ergo, that generator either:
    # * Yielded one or more ignorable frames. This is the common case.
    # * Yielded *NO* frames. Although an extreme edge case, this could
    #   technically occur if the caller called this getter from a REPL.
    #
    # In either case...
    else:  # pragma: no cover
        assert isinstance(exception_cls, type), (
            f'{repr(exception_cls)} not exception type.')
        assert isinstance(exception_prefix, str), (
            f'{repr(exception_prefix)} not string.')

        # Raise an exception.
        raise exception_cls(
            f'{exception_prefix}call stack either '
            f'empty or contains only ignorable stack frames.'
        )

    # Return this frame. By the above logic, this frame is guaranteed to exist.
    return frame_caller_external

# ....................{ ITERATORS                          }....................
#FIXME: Generalize with a new "is_module_boundary_stop: bool = True" optional
#parameter. If true, this generator implicitly halts at a "<module>" boundary.
def iter_frames(
    # Optional parameters.
    ignore_frames: int = 0,
    is_ignore_beartype_frames: bool = True,
    is_ignore_nonpython_frames: bool = True,
    is_ignore_unmoduled_frames: bool = True,
) -> Iterable[CallableFrameType]:
    '''
    Generator yielding one **frame** (i.e., :class:`types.CallableFrameType`
    instance) for each call on the current **call stack** (i.e., stack of frame
    objects, encapsulating the linear chain of calls to external callables
    underlying the current call to this callable).

    Notably, for each:

    * **C-based callable call** (i.e., call of a C-based rather than
      pure-Python callable), this generator yields one frame encapsulating *no*
      code object. Only pure-Python frame objects have code objects.
    * **Class-scoped callable call** (i.e., call of an arbitrary callable
      occurring at class scope rather than from within the body of a callable
      or class, typically due to a method being decorated), this generator
      yields one frame ``func_frame`` for that class ``cls`` such that
      ``func_frame.f_code.co_name == cls.__name__`` (i.e., the name of the code
      object encapsulated by that frame is the unqualified name of the class
      encapsulating the lexical scope of this call). Actually, we just made all
      of that up. That is *probably* (but *not* necessarily) the case. Research
      is warranted.
    * **Module-scoped callable call** (i.e., call of an arbitrary callable
      occurring at module scope rather than from within the body of a callable
      or class, typically due to a function or class being decorated), this
      generator yields one frame ``func_frame`` such that
      ``func_frame.f_code.co_name == '<module>'`` (i.e., the name of the code
      object encapsulated by that frame is the placeholder string assigned by
      the active Python interpreter to all scopes encapsulating the top-most
      lexical scope of a module in the current call stack).

    The above constraints imply that frames yielded by this generator *cannot*
    be assumed to encapsulate code objects. See the "Examples" subsection for
    standard logic handling this edge case.

    Caveats
    -------
    **This high-level iterator requires the private low-level**
    :func:`sys._getframe` **getter.** If that getter is undefined, this iterator
    reduces to the empty generator yielding nothing rather than raising an
    exception. Since all standard Python implementations (e.g., CPython, PyPy)
    define that getter, this should typically *not* be a real-world concern.

    Parameters
    ----------
    ignore_frames : int, default: 0
        Number of frames on the call stack to be ignored (i.e., silently
        incremented past). Defaults to 0.
    is_ignore_beartype_frames : bool, default: True
        :data:`True` only if yielding *only* frames encapsulating lexical scopes
        originating from objects (e.g., modules, types, callables) defined
        outside the :mod:`beartype` package. Equivalently, :data:`True` only if
        ignoring (i.e., silently incrementing past) all frames *other* than
        those encapsulating such scopes. Defaults to :data:`True` for both
        safety and usability. This is almost certainly what both everyone wants.
    is_ignore_nonpython_frames : bool, default: True
        :data:`True` only if yielding *only* frames encapsulating lexical scopes
        originating from pure-Python objects (e.g., modules, types, callables).
        Equivalently, :data:`True` only if ignoring (i.e., silently incrementing
        past) all frames *other* than those encapsulating such scopes. Defaults
        to :data:`True` for both safety and usability. This is almost certainly
        what everyone wants.
    is_ignore_unmoduled_frames : bool, default: True
        :data:`True` only if yielding *only* frames encapsulating lexical scopes
        originating from either modules *or* objects residing inside modules
        (e.g., types, callables). Equivalently, :data:`True` only if ignoring
        (i.e., silently incrementing past) all frames *other* than those
        encapsulating such scopes. Note that most real-world objects of interest
        are either themselves modules *or* reside inside modules; exceptions
        include objects that are both dynamically defined in-memory *and*
        assigned no parent module. Defaults to :data:`True` for both safety and
        usability. This is almost certainly what both everyone wants.

    Returns
    -------
    Iterable[CallableFrameType]
        Generator yielding one frame for each call on the current call stack.

    See Also
    --------
    :func:`.get_frame_or_none`
        Further details on the ``ignore_frames`` parameter.
    :func:`.get_frame`
        Further details on stack frame objects.

    Examples
    --------
    :: code-block:: python

       from beartype._util.func.utilfunccodeobj import (
           get_func_codeobj_or_none)
       from beartype._util.func.utilfuncframe import iter_frames

       # For each pure-Python stack frame on the call stack...
       for func_frame in iter_frames():
           # Fully-qualified name of this scope's module.
           func_frame_module_name = func_frame.f_globals['__name__']

           # Unqualified name of this scope.
           func_frame_name = func_frame_codeobj.co_name

           # Print the fully-qualified name of this scope.
           print(f'On {func_frame_module_name}.{func_frame_name}()!')
    '''
    assert isinstance(ignore_frames, int), f'{repr(ignore_frames)} not integer.'
    assert ignore_frames >= 0, f'{ignore_frames} negative.'
    assert isinstance(is_ignore_beartype_frames, bool), (
        f'{repr(is_ignore_beartype_frames)} not boolean.')
    assert isinstance(is_ignore_nonpython_frames, bool), (
        f'{repr(is_ignore_nonpython_frames)} not boolean.')
    assert isinstance(is_ignore_unmoduled_frames, bool), (
        f'{repr(is_ignore_unmoduled_frames)} not boolean.')

    # ..................{ IMPORTS                            }..................
    # Avoid circular import dependencies.
    from beartype._util.func.utilfunccodeobj import get_func_codeobj_or_none

    # ....................{ PREAMBLE                       }....................
    # If the active Python interpreter fails to declare the private
    # sys._getframe() getter, reduce to the empty generator (i.e., noop).
    if get_frame is None:  # pragma: no cover
        return (yield from ())
    # Else, the active Python interpreter declares the sys._getframe() getter.

    # Attempt to obtain the next non-ignored frame after the last ignored frame,
    # ignoring an additional frame embodying the current call to this iterator.
    try:
        func_frame = get_frame(ignore_frames + 1)  # type: ignore[misc]
    # If doing so raises a "ValueError" exception...
    except ValueError as value_error:
        # Whose message matches this standard boilerplate, the caller requested
        # that this generator ignore more stack frames than currently exist on
        # the call stack. Permitting this exception to unwind the call stack
        # would only needlessly increase the fragility of this already fragile
        # mission-critical generator. Instead, swallow this exception and
        # silently reduce to the empty generator (i.e., noop).
        if str(value_error) == 'call stack is not deep enough':
            yield from ()
            return
        # Whose message does *NOT* match this standard boilerplate, an
        # unexpected exception occurred. In this case, re-raise this exception.

        raise
    # Else, doing so raised *NO* "ValueError" exception.
    # print(f'start frame: {repr(func_frame)}')

    # ....................{ ITERATE                        }....................
    # While at least one frame remains on the call stack...
    while func_frame:
        # print(f'current frame: {repr(func_frame)}')

        # Code object underlying this frame's scope if this scope is pure-Python
        # *OR* "None" otherwise.
        func_frame_codeobj = get_func_codeobj_or_none(func_frame)

        # Fully-qualified name of the module defining this scope if any *OR*
        # "None" otherwise (i.e., if this scope is defined outside a module).
        func_frame_module_name = get_frame_module_name_or_none(func_frame)

        # If neither...
        if not (
            (
                # Ignoring frames encapsulating lexical scopes *NOT* originating
                # from pure-Python objects (e.g., modules, types, callables)
                # *AND*...
                is_ignore_nonpython_frames and
                # This code object does *NOT* exist (implying this scope to
                # *NOT* be pure-Python)...
                func_frame_codeobj is None
            # *NOR*...
            ) or (
                # Ignoring frames encapsulating lexical scopes originating
                # outside modules *AND*...
                is_ignore_unmoduled_frames and
                # This scope is defined outside a module...
                func_frame_module_name is None
            # *NOR*...
            ) or (
                # Ignoring frames encapsulating lexical scopes originating
                # outside the "beartype" package *AND*...
                is_ignore_beartype_frames and
                # This scope is defined inside a module *AND either...
                func_frame_module_name and (
                    # This scope is directly defined by the root "beartype"
                    # package *OR*...
                    func_frame_module_name == 'beartype' or
                    # This scope is transitively defined by a "beartype"
                    # subpackage...
                    func_frame_module_name.startswith('beartype.')
                )
            )
        ):
        # Then this frame is of interest to the caller. Yield this frame! \o/
            yield func_frame
        # Else, silently ignore this scope.
        # else:
        #     print(f'Ignoring {func_frame} in module "{func_frame_module_name}"...')

        # Iterate to the next frame on the call stack.
        func_frame = func_frame.f_back

# ....................{ PRIVATE ~ coercers                 }....................
#FIXME: Unit test us up, please. *sigh*
def _coerce_mapping_to_scope(scopelike: MappingStrToAny) -> LexicalScope:
    '''
    **Lexical scope** (i.e., dictionary mapping from strings to arbitrary
    objects) converted if necessary from the passed **lexical scope-like
    mapping** (i.e., possibly immutable mapping from strings to arbitrary
    objects).

    Parameters
    ----------
    scopelike : Mapping[str, object]
        Lexical scope-like mapping to be converted into a lexical scope.

    Returns
    ----------
    dict[str, object]
        Lexical scope converted from this lexical scope-like mapping.
    '''
    assert isinstance(scopelike, Mapping), f'{repr(scopelike)} not mapping.'

    # If this scope-like is *NOT* a "dict" instance, coerce this scope-like
    # into a "dict" instance. Why? Several justifiable reasons:
    # * Higher-level callers calling this lower-level coercer are typically
    #   annotated as returning a "LexicalScope", which is currently just a
    #   readable alias for "DictStrToAny", which is itself an efficiency alias
    #   for "Dict[Str, object]". Ergo, static type-checkers expect this getter
    #   to return "dict" instances.
    # * Under Python <= 3.11, the "CallerFrameType.f_locals" instance variable
    #   actually is a "dict" instance.
    # * Under Python >= 3.12, the "CallerFrameType.f_locals" instance variable
    #   actually is instead a "mappingproxy" instance. Although interchangeable
    #   for most purposes, "dict" and "mappingproxy" instances are *NOT*
    #   perfectly interchangeable. In particular, callers of this function
    #   frequently pass this local scope to the dict.update() method -- which
    #   expects the passed mapping to also be a "dict" instance: e.g.,
    #       cls_curr_locals = get_type_locals(
    #           cls=cls_curr, exception_cls=exception_cls)
    #   >   func_locals.update(cls_curr_locals)
    #   E   TypeError: update() argument must be dict or another FrameLocalsProxy
    #
    #   Why? No idea. Ideally, the dict.update() method would accept arbitrary
    #   mappings -- but it doesn't. Since it doesn't, we have *NO* recourse but
    #   to preserve forward compatibility with future Python versions by
    #   coercing non-"dict" to "dict" instances here on behalf of the caller. It
    #   is what it is. We sigh! *sigh*
    return scopelike if isinstance(scopelike, dict) else dict(scopelike)
    # Else, this local scope is already a "dict" instance.
