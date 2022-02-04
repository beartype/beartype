#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2022 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **callable creation** utilities.

This private submodule implements utility functions dynamically creating new
callables on-the-fly.

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                           }....................
from beartype.roar._roarexc import _BeartypeUtilCallableException
from beartype._util.func.utilfuncscope import CallableScope
from beartype._util.text.utiltextlabel import label_exception
from beartype._util.text.utiltextmunge import number_lines
from beartype._util.utilobject import get_object_name
from collections.abc import Callable
from functools import update_wrapper
from linecache import cache as linecache_cache  # type: ignore[attr-defined]
from typing import Optional, Type
from weakref import finalize

# See the "beartype.cave" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ MAKERS                            }....................
def make_func(
    # Mandatory arguments.
    func_name: str,
    func_code: str,

    # Optional arguments.
    func_globals: Optional[CallableScope] = None,
    func_locals:  Optional[CallableScope] = None,
    func_doc: Optional[str] = None,
    func_label:   Optional[str] = None,
    func_wrapped: Optional[Callable] = None,

    #FIXME: Unit test us up, please.
    is_debug: bool = False,
    exception_cls: Type[Exception] = _BeartypeUtilCallableException,
) -> Callable:
    '''
    Dynamically create and return a new function with the passed name declared
    by the passed code snippet and internally accessing the passed dictionaries
    of globally and locally scoped variables.

    Parameters
    ----------
    func_name : str
        Name of the function to be created.
    func_code : str
        Code snippet defining this function, including both this function's
        signature prefixed by zero or more decorations *and* body. **This
        snippet must be unindented.** If this snippet is indented, this factory
        raises a syntax error.
    func_globals : Dict[str, Any], optional
        Dictionary mapping from the name to value of each **globally scoped
        attribute** (i.e., internally referenced in the body of the function
        declared by this code snippet). Defaults to the empty dictionary.
    func_locals : Dict[str, Any], optional
        Dictionary mapping from the name to value of each **locally scoped
        attribute** (i.e., internally referenced either in the signature of
        the function declared by this code snippet *or* as decorators
        decorating that function). **Note that this factory necessarily
        modifies the contents of this dictionary.** Defaults to the empty
        dictionary.
    func_doc : str, optional
        Human-readable docstring documenting this function. Defaults to
        ``None``, in which case this function remains undocumented.
    func_label : str, optional
        Human-readable label describing this function for error-handling
        purposes. Defaults to ``{name}()``.
    func_wrapped : Callable, optional
        Callable wrapped by the function to be created. If non-``None``,
        special dunder attributes will be propagated (i.e., copied) from this
        wrapped callable into this created function; these include:

        * ``__name__``, this function's unqualified name.
        * ``__doc__``, this function's docstring.
        * ``__module__``, the fully-qualified name of this function's module.

        Defaults to ``None``.
    is_debug: bool, optional
        ``True`` only if this factory prints to standard output the definition
        (including signature and body) of this function. Defaults to ``False``.
    exception_cls : type, optional
        Type of exception to raise in the event of a fatal error. Defaults to
        :exc:`_BeartypeUtilCallableException`.

    Returns
    ----------
    Callable
        Function with this name declared by this snippet.

    Raises
    ----------
    exception_cls
        If either:

        * ``func_locals`` contains a key whose value is that of ``func_name``,
          implying the caller already declared a local attribute whose name
          collides with that of this function.
        * This code snippet is syntactically invalid.
        * This code snippet is syntactically valid but fails to declare a
          function with this name.
    '''
    assert isinstance(func_name, str), f'{repr(func_name)} not string.'
    assert isinstance(func_code, str), f'{repr(func_code)} not string.'
    assert isinstance(is_debug, bool), f'{repr(is_debug)} not bool.'
    assert func_name, 'Parameter "func_name" empty.'
    assert func_code, 'Parameter "func_code" empty.'

    # Default all unpassed parameters.
    if func_globals is None:
        func_globals = {}
    if func_locals is None:
        func_locals = {}
    if func_label is None:
        func_label = f'{func_name}()'
    assert isinstance(func_globals, dict), (
        f'{repr(func_globals)} not dictionary.')
    assert isinstance(func_locals, dict), (
        f'{repr(func_locals)} not dictionary.')
    assert isinstance(func_label, str), f'{repr(func_label)} not string.'

    # If that function's name is already in this local scope, the caller
    # already declared a local attribute whose name collides with that
    # function's. In this case, raise an exception for safety.
    if func_name in func_locals:
        raise exception_cls(
            f'{func_label} already defined by caller locals:\n'
            f'{repr(func_locals)}'
        )
    # Else, that function's name is *NOT* already in this local scope.

    # Code snippet defining this function, stripped of all leading and trailing
    # whitespace to improve both readability and disambiguity. Since this
    # whitespace is safely ignorable, the original snippet is safely
    # replaceable by this stripped snippet.
    func_code = func_code.strip()

    # If printing the definition of that function, do so.
    if is_debug:
        print(f'{number_lines(func_code)}')
    # Else, that definition is left obscured by voracious bitbuckets of time.

    # Attempt to...
    try:
        # Declare that function. For obscure and likely uninteresting reasons,
        # Python fails to capture that function (i.e., expose that function to
        # this function) when the locals() dictionary is passed; instead, a
        # unique local dictionary *MUST* be passed.

        # Make up a filename for compilation and possibly the linecache entry
        # (if we make one). A fully-qualified name and ID *should* be unique
        # for the life of the process.
        func_full_name = (
            get_object_name(func_wrapped)
            if func_wrapped else
            func_name
        )
        linecache_filename = (
            f'<@beartype({func_full_name}) at {id(func_wrapped):#x}>')

        # We use the more verbose and obfuscatory compile() builtin instead of
        # simply calling exec(func_code, func_globals, func_locals) because
        # exec does not provide a way to set the resulting function object's
        # .__code__.co_filename read-only attribute. We can use "single"
        # instead of "exec" if we are willing to accept that func_code is
        # constrained to a single statement. In casual testing, there is very
        # little performance difference (with an imperceptibly slight edge
        # going to "single").
        func_code_compiled = compile(
            func_code, linecache_filename, 'exec')
        assert func_name not in func_locals
        exec(func_code_compiled, func_globals, func_locals)
    # If doing so fails for any reason...
    except Exception as exception:
        # Raise an exception suffixed by that function's declaration such that
        # each line of that declaration is prefixed by that line's number. This
        # renders "SyntaxError" exceptions referencing arbitrary line numbers
        # human-readable: e.g.,
        #       File "<string>", line 56
        #         if not (
        #          ^
        #     SyntaxError: invalid syntax
        raise exception_cls(
            f'{func_label} unparseable, as @beartype generated '
            f'invalid code raising "{label_exception(exception)}":\n\n'
            f'{number_lines(func_code)}'
        ) from exception

    # If that function's name is *NOT* in this local scope, this code snippet
    # failed to declare that function. In this case, raise an exception.
    if func_name not in func_locals:
        raise exception_cls(
            f'{func_label} undefined by code snippet:\n\n'
            f'{number_lines(func_code)}'
        )
    # Else, that function's name is in this local scope.

    # Function declared by this code snippet.
    func: Callable = func_locals[func_name]  # type: ignore[assignment]

    # If that function is uncallable, raise an exception.
    if not callable(func):
        raise exception_cls(
            f'{func_label} defined by code snippet uncallable:\n\n'
            f'{number_lines(func_code)}'
        )
    # Else, that function is callable.

    # If that function is a wrapper wrapping a wrappee callable, propagate
    # dunder attributes from that wrappee onto this wrapper.
    if func_wrapped is not None:
        assert callable(func_wrapped), f'{repr(func_wrapped)} uncallable.'
        update_wrapper(wrapper=func, wrapped=func_wrapped)
    # Else, that function is *NOT* such a wrapper.

    # If that function is documented...
    #
    # Note that function is intentionally documented *AFTER* propagating dunder
    # attributes to enable callers to explicitly overwrite documentation
    # propagated from that wrappee onto this wrapper.
    if func_doc is not None:
        assert isinstance(func_doc, str), f'{repr(func_doc)} not string.'
        assert func_doc, '"func_doc" empty.'

        # Document that function.
        func.__doc__ = func_doc
    # Else, that function is undocumented.

    # Since we went through the trouble of printing its definition, we might
    # as well make its compiled version debuggable, too.
    if is_debug:
        linecache_cache[linecache_filename] = (  # type: ignore[assignment]
            len(func_code),  # type: ignore[assignment]  # Y u gotta b diff'rnt Python 3.7? WHY?!
            None,  # mtime, but should be None to avoid being discarded
            func_code.splitlines(keepends=True),
            linecache_filename,
        )

        # Define and register a cleanup callback for removing func's linecache
        # entry if func is ever garbage collected.
        def remove_linecache_entry_for_func():
            linecache_cache.pop(linecache_filename, None)
        finalize(func, remove_linecache_entry_for_func)

    # Return that function.
    return func

# ....................{ COPIERS                           }....................
#FIXME: Consider excising. Although awesome, this is no longer needed.
# from beartype._util.func.utilfunctest import die_unless_func_python
# from types import FunctionType
# def copy_func_shallow(
#     # Mandatory arguments.
#     func: Callable,
#
#     # Optional arguments.
#     exception_cls: Type[Exception] = _BeartypeUtilCallableException,
# ) -> Callable:
#     '''
#     Create and return a new shallow copy of the passed callable.
#
#     Specifically, this function creates and returns a new function sharing with
#     the passed callable the same:
#
#     * Underlying code object (i.e., ``func.__code__``).
#     * Unqualified and fully-qualified names (i.e., ``func.__name__`` and
#       ``func.__qualname__``).
#     * Docstring (i.e., ``func.__doc__``).
#     * Type hints (i.e., ``func.__annotations__``).
#     * Global scope (i.e., ``func.__globals__``).
#     * Fully-qualified module name (i.e., ``func.__module__``).
#     * Default values of optional parameters (i.e., ``f.__defaults__`` and
#       ``f.__kwdefaults__``).
#     * Closure-specific cell variables (i.e., ``f.__closure__``).
#     * Custom public and private attributes.
#
#     Parameters
#     ----------
#     func : Callable
#         Callable to be copied.
#     exception_cls : type, optional
#         Type of exception to raise in the event of a fatal error. Defaults to
#         :exc:`_BeartypeUtilCallableException`.
#
#     Returns
#     ----------
#     Callable
#         Function shallowly copied from the passed callable.
#
#     Raises
#     ----------
#     exception_cls
#         If the passed callable is *not* pure-Python.
#
#     See Also
#     ----------
#     https://stackoverflow.com/a/30714299/2809027
#         StackOverflow answer strongly inspiring this implementation.
#     '''
#
#     # If the passed callable is *NOT* pure-Python, raise an exception.
#     die_unless_func_python(func=func, exception_cls=exception_cls)
#
#     # Function shallowly copied from the passed callable.
#     #
#     # Note that *ALL* pure-Python callables are guaranteed to define the
#     # following dunder attributes.
#     func_copy = FunctionType(
#         func.__code__,
#         func.__globals__,  # type: ignore[attr-defined]
#         func.__name__,
#         func.__defaults__,  # type: ignore[attr-defined]
#         func.__closure__,  # type: ignore[attr-defined]
#     )
#
#     # Shallowly copy all remaining dunder attributes from the original callable
#     # onto this copy *NOT* already copied by the FunctionType.__init__() method
#     # called above.
#     #
#     # Note that *ALL* pure-Python callables are guaranteed to define the
#     # following dunder attributes.
#     func_copy.__annotations__ = func.__annotations__
#     func_copy.__doc__ = func.__doc__
#     func_copy.__kwdefaults__ = func.__kwdefaults__  # type: ignore[attr-defined]
#     func_copy.__module__ = func.__module__
#     func_copy.__qualname__ = func.__qualname__
#
#     # Shallowly copy all custom attributes (i.e., non-dunder attributes
#     # explicitly set by the caller) from the original callable onto this copy.
#     func_copy.__dict__.update(func.__dict__)
#     # print(f'func.__dict__: {func.__dict__}')
#     # print(f'func_copy.__dict__: {func_copy.__dict__}')
#
#     # Return this copy.
#     return func_copy
