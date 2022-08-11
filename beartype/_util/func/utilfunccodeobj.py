#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2022 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **callable code object utilities** (i.e., callables introspecting
**code objects** (i.e., instances of the :class:`CodeType` type) underlying all
pure-Python callables).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.roar._roarexc import _BeartypeUtilCallableException
from beartype.typing import (
    Any,
    Optional,
)
from beartype._util.func.utilfuncwrap import unwrap_func
from beartype._data.datatyping import (
    Codeobjable,
    TypeException,
)
from types import (
    CodeType,
    FrameType,
    FunctionType,
    GeneratorType,
    MethodType,
)

# ....................{ CONSTANTS                          }....................
#FIXME: Unit test us up, please.
FUNC_CODEOBJ_NAME_MODULE = '<module>'
'''
String constant unconditionally assigned to the ``co_name`` instance variables
of the code objects of all pure-Python modules.
'''

# ....................{ GETTERS                            }....................
def get_func_codeobj(
    # Mandatory parameters.
    func: Codeobjable,

    # Optional parameters.
    is_unwrapping: bool = False,
    exception_cls: TypeException = _BeartypeUtilCallableException,
) -> CodeType:
    '''
    **Code object** (i.e., instance of the :class:`CodeType` type) underlying
    the passed **codeobjable** (i.e., pure-Python object directly associated
    with a code object) if this object is codeobjable *or* raise an exception
    otherwise (e.g., if this object is *not* codeobjable).

    For convenience, this getter also accepts a code object, in which case that
    code object is simply returned as is.

    Code objects have a docstring under CPython resembling:

    .. code-block:: python

       Code objects provide these attributes:
           co_argcount         number of arguments (not including *, ** args
                               or keyword only arguments)
           co_code             string of raw compiled bytecode
           co_cellvars         tuple of names of cell variables
           co_consts           tuple of constants used in the bytecode
           co_filename         name of file in which this code object was
                               created
           co_firstlineno      number of first line in Python source code
           co_flags            bitmap: 1=optimized | 2=newlocals | 4=*arg |
                               8=**arg | 16=nested | 32=generator | 64=nofree |
                               128=coroutine | 256=iterable_coroutine |
                               512=async_generator
           co_freevars         tuple of names of free variables
           co_posonlyargcount  number of positional only arguments
           co_kwonlyargcount   number of keyword only arguments (not including
                               ** arg)
           co_lnotab           encoded mapping of line numbers to bytecode
                               indices
           co_name             name with which this code object was defined
           co_names            tuple of names of local variables
           co_nlocals          number of local variables
           co_stacksize        virtual machine stack space required
           co_varnames         tuple of names of arguments and local variables

    Parameters
    ----------
    func : Codeobjable
        Codeobjable to be inspected.
    is_unwrapping: bool, optional
        ``True`` only if this getter implicitly calls the :func:`unwrap_func`
        function to unwrap this possibly higher-level wrapper into a possibly
        lower-level wrappee *before* returning the code object of that wrappee.
        Note that doing so incurs worst-case time complexity ``O(n)`` for ``n``
        the number of lower-level wrappees wrapped by this wrapper. Defaults to
        ``False`` for efficiency.
    exception_cls : type, optional
        Type of exception in the event of a fatal error. Defaults to
        :class:`_BeartypeUtilCallableException`.

    Returns
    ----------
    CodeType
        Code object underlying this callable.

    Raises
    ----------
    exception_cls
         If this callable has *no* code object and is thus *not* pure-Python.
    '''

    # Code object underlying this callable if this callable is pure-Python *OR*
    # "None" otherwise.
    func_codeobj = get_func_codeobj_or_none(
        func=func, is_unwrapping=is_unwrapping)

    # If this callable is *NOT* pure-Python...
    if func_codeobj is None:
        # Avoid circular import dependencies.
        from beartype._util.func.utilfunctest import die_unless_func_python

        # Raise an exception.
        die_unless_func_python(func=func, exception_cls=exception_cls)
    # Else, this callable is pure-Python and this code object exists.

    # Return this code object.
    return func_codeobj  # type: ignore[return-value]


def get_func_codeobj_or_none(
    # Mandatory parameters.
    func: Any,

    # Optional parameters.
    is_unwrapping: bool = False,
) -> Optional[CodeType]:
    '''
    **Code object** (i.e., instance of the :class:`CodeType` type) underlying
    the passed **codeobjable** (i.e., pure-Python object directly associated
    with a code object) if this object is codeobjable *or* ``None`` otherwise
    (e.g., if this object is *not* codeobjable).

    Specifically, if the passed object is a:

    * Pure-Python function, this getter returns the code object of that
      function (i.e., ``func.__code__``).
    * Pure-Python bound method wrapping a pure-Python unbound function, this
      getter returns the code object of the latter (i.e.,
      ``func.__func__.__code__``).
    * Pure-Python call stack frame, this getter returns the code object of the
      pure-Python callable encapsulated by that frame (i.e., ``func.f_code``).
    * Pure-Python generator, this getter returns the code object of that
      generator (i.e., ``func.gi_code``).
    * Code object, this getter returns that code object as is.
    * Any other object, this getter raises an exception.

    Caveats
    -------
    If ``is_unwrapping``, **this callable has worst-case time complexity**
    ``O(n)`` **for** ``n`` **the number of lower-level wrappees wrapped by this
    higher-level wrapper.** That parameter should thus be disabled in
    time-critical code paths; instead, the lowest-level wrappee returned by the
    :func:``beartype._util.func.utilfuncwrap.unwrap_func` function should be
    temporarily stored and then repeatedly passed.

    Parameters
    ----------
    func : Codeobjable
        Codeobjable to be inspected.
    is_unwrapping: bool, optional
        ``True`` only if this getter implicitly calls the :func:`unwrap_func`
        function to unwrap this possibly higher-level wrapper into a possibly
        lower-level wrappee *before* returning the code object of that wrappee.
        Note that doing so incurs worst-case time complexity ``O(n)`` for ``n``
        the number of lower-level wrappees wrapped by this wrapper. Defaults to
        ``False`` for efficiency.

    Returns
    ----------
    Optional[CodeType]
        Either:

        * If the passed callable is pure-Python, that callable's code object.
        * Else, ``None``.

    See Also
    ----------
    :func:`get_func_codeobj`
        Further details.
    '''
    assert is_unwrapping.__class__ is bool, f'{is_unwrapping} not boolean.'

    # Note that:
    # * For efficiency, tests are intentionally ordered in decreasing
    #   likelihood of a successful match.
    # * An equivalent algorithm could also technically be written as a chain of
    #   "getattr(func, '__code__', None)" calls, but that doing so would both
    #   be less efficient *AND* render this getter less robust. Why? Because
    #   the getattr() builtin internally calls the __getattr__() and
    #   __getattribute__() dunder methods (either of which could raise
    #   arbitrary exceptions) and is thus considerably less safe.
    #
    # If this object is already a code object, return this object as is.
    if isinstance(func, CodeType):
        return func
    # Else, this object is *NOT* already a code object.
    #
    # If this object is a pure-Python function...
    #
    # Note that this test intentionally leverages the standard
    # "types.FunctionType" class rather than our equivalent
    # "beartype.cave.FunctionType" class to avoid circular import issues.
    elif isinstance(func, FunctionType):
        #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        # CAUTION: Synchronize this with the same test below (for methods).
        #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        # Return the code object of either:
        # * If unwrapping this function, the lowest-level wrappee wrapped by
        #   this function.
        # * Else, this function as is.
        return (unwrap_func(func) if is_unwrapping else func).__code__  # type: ignore[attr-defined]
    # Else, this object is *NOT* a pure-Python function.
    #
    # If this callable is a bound method, return this method's code object.
    #
    # Note this test intentionally tests the standard "types.MethodType" class
    # rather than our equivalent "beartype.cave.MethodBoundInstanceOrClassType"
    # class to avoid circular import issues.
    elif isinstance(func, MethodType):
        # Unbound function underlying this bound method.
        func = func.__func__

        #FIXME: Can "MethodType" objects actually bind lower-level C-based
        #rather than pure-Python functions? We kinda doubt it -- but maybe they
        #can. If they can't, then this test is superfluous and should be
        #removed with all haste.

        # If this unbound function is pure-Python...
        if isinstance(func, FunctionType):
            #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            # CAUTION: Synchronize this with the same test above.
            #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            # Return the code object of either:
            # * If unwrapping this function, the lowest-level wrappee wrapped
            #   by this function.
            # * Else, this function as is.
            return (unwrap_func(func) if is_unwrapping else func).__code__  # type: ignore[attr-defined]
    # Else, this callable is *NOT* a pure-Python bound method.
    #
    # If this object is a pure-Python generator, return this generator's code
    # object.
    elif isinstance(func, GeneratorType):
        return func.gi_code
    # Else, this object is *NOT* a pure-Python generator.
    #
    # If this object is a call stack frame, return this frame's code object.
    elif isinstance(func, FrameType):
        #FIXME: *SUS AF.* This is likely to behave as expected *ONLY* for
        #frames encapsulating pure-Python callables. For frames encapsulating
        #C-based callables, this is likely to fail with an "AttributeError"
        #exception. That said, we have *NO* idea how to test this short of
        #defining our own C-based callable accepting a pure-Python callable as
        #a callback parameter and calling that callback. Are there even C-based
        #callables like that in the wild?
        return func.f_code
    # Else, this object is *NOT* a call stack frame. Since none of the above
    # tests matched, this object *MUST* be a C-based callable.

    # Fallback to returning "None".
    return None
