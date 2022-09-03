#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2022 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **text label** (i.e., human-readable strings describing prominent
objects or types, typically interpolated into error messages) utilities.

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.typing import Optional
from beartype._util.text.utiltextcolour import user_value_colour
from beartype._util.utilobject import (
    get_object_name,
    get_object_type_name,
)
from collections.abc import Callable

# ....................{ LABELLERS ~ callable               }....................
def label_callable(
    # Mandatory parameters.
    func: Callable,

    # Optional parameters.
    is_contextualized: Optional[bool] = None,
) -> str:
    '''
    Human-readable label describing the passed **callable** (e.g., function,
    method, property).

    Parameters
    ----------
    func : Callable
        Callable to be labelled.
    is_contextualized : Optional[bool] = None
        Either:

        * ``True``, in which case this label is suffixed by additional metadata
          contextually disambiguating that callable, including:

          * The line number of the first line declaring that callable in its
            underlying source code module file.
          * The absolute filename of that file.

        * ``False``, in which case this label is *not* suffixed by such
          metadata.
        * ``None``, in which case this label is conditionally suffixed by such
          metadata only if that callable is a lambda function and thus
          ambiguously lacks any semblance of an innate context.

        Defaults to ``None``.

    Returns
    ----------
    str
        Human-readable label describing this callable.
    '''
    assert callable(func), f'{repr(func)} uncallable.'

    # Avoid circular import dependencies.
    from beartype._util.func.arg.utilfuncargget import (
        get_func_args_len_flexible)
    from beartype._util.func.utilfuncfile import get_func_filename_or_none
    from beartype._util.func.utilfunccodeobj import get_func_codeobj
    from beartype._util.func.utilfunctest import (
        is_func_lambda,
        is_func_coro,
        is_func_async_generator,
        is_func_sync_generator,
    )
    from beartype._util.mod.utilmodget import (
        get_object_module_line_number_begin)

    # Substring prefixing the string to be returned, typically identifying the
    # specialized type of that callable if that callable has a specialized type.
    func_label_prefix = ''

    # Substring suffixing the string to be returned, typically contextualizing
    # that callable with respect to its on-disk code module file.
    func_label_suffix = ''

    # If the passed callable is a pure-Python lambda function, that callable
    # has *NO* unique fully-qualified name. In this case, return a string
    # uniquely identifying this lambda from various code object metadata.
    if is_func_lambda(func):
        # Code object underlying this lambda.
        func_codeobj = get_func_codeobj(func)

        # Substring preceding the string to be returned.
        func_label_prefix = (
            f'lambda function of '
            f'{get_func_args_len_flexible(func_codeobj)} argument(s)'
        )

        # If the caller failed to request an explicit contextualization, default
        # to contextualizing this lambda function.
        if is_contextualized is None:
            is_contextualized = True
        # Else, the caller requested an explicit contextualization. In this
        # case, preserve that contextualization as is.
    # Else, the passed callable is *NOT* a pure-Python lambda function and thus
    # has a unique fully-qualified name.
    else:
        # If that callable is a synchronous generator, return this string
        # prefixed by a substring emphasizing that fact.
        if is_func_sync_generator(func):
            func_label_prefix = 'generator '
        # Else, that callable is *NOT* a synchronous generator.
        #
        # If that callable is an asynchronous coroutine, return this string
        # prefixed by a substring emphasizing that fact.
        elif is_func_coro(func):
            func_label_prefix = 'coroutine '
        # Else, that callable is *NOT* an asynchronous coroutine.
        #
        # If that callable is an asynchronous generator, return this string
        # prefixed by a substring emphasizing that fact.
        elif is_func_async_generator(func):
            func_label_prefix = 'asynchronous generator '
        # Else, that callable is *NOT* an asynchronous generator.

    # If contextualizing that callable...
    if is_contextualized:
        # Absolute filename of the source module file defining that callable if
        # that callable was defined on-disk *OR* "None" otherwise (i.e., if that
        # callable was defined in-memory).
        func_filename = get_func_filename_or_none(func)

        # Line number of the first line declaring that callable in that file.
        func_lineno = get_object_module_line_number_begin(func)

        # If that callable was defined on-disk, describe the location of that
        # callable in that file.
        if func_filename:
            func_label_suffix += (
                f' declared on line {func_lineno} of file "{func_filename}" ')
        # Else, that callable was defined in-memory. In this case, avoid
        # attempting to uselessly contextualize that callable.

    # Return that prefix followed by the fully-qualified name of that callable.
    return f'{func_label_prefix}{get_object_name(func)}(){func_label_suffix}'

# ....................{ LABELLERS ~ type                   }....................
def label_obj_type(obj: object) -> str:
    '''
    Human-readable label describing the class of the passed object.

    Parameters
    ----------
    obj : object
        Object whose class is to be labelled.

    Returns
    ----------
    str
        Human-readable label describing the class of this object.
    '''

    # Tell me why, why, why I curse the sky! ...no, srsly.
    return label_type(type(obj))


def label_type(cls: type) -> str:
    '''
    Human-readable label describing the passed class.

    Parameters
    ----------
    cls : type
        Class to be labelled.

    Returns
    ----------
    str
        Human-readable label describing this class.
    '''
    assert isinstance(cls, type), f'{repr(cls)} not class.'

    # Avoid circular import dependencies.
    from beartype._util.cls.utilclstest import is_type_builtin
    from beartype._util.hint.pep.proposal.utilpep544 import (
        is_hint_pep544_protocol)

    # Label to be returned, initialized to this class' fully-qualified name.
    classname = get_object_type_name(cls)
    # print(f'cls {cls} classname: {classname}')

    # If this name contains *NO* periods, this class is actually a builtin type
    # (e.g., "list"). Since builtin types are well-known and thus
    # self-explanatory, this name requires no additional labelling. In this
    # case, return this name as is.
    if '.' not in classname:
        pass
    # Else, this name contains one or more periods but could still be a
    # builtin indirectly accessed via the standard "builtins" module.
    #
    # If this name is that of a builtin type uselessly prefixed by the name of
    # the module declaring all builtin types (e.g., "builtins.list"), reduce
    # this name to the unqualified basename of this type (e.g., "list").
    elif is_type_builtin(cls):
        classname = cls.__name__
    # Else, this is a non-builtin class. Non-builtin classes are *NOT*
    # well-known and thus benefit from additional labelling.
    #
    # If this class is a PEP 544-compliant protocol supporting structural
    # subtyping, label this protocol.
    elif is_hint_pep544_protocol(cls):
        # print(f'cls {cls} is protocol!')
        classname = f'<protocol "{classname}">'
    # Else if this class is a standard abstract base class (ABC) defined by a
    # stdlib submodule also known to support structural subtyping (e.g.,
    # "collections.abc.Hashable", "contextlib.AbstractContextManager"),
    # label this ABC as a protocol.
    #
    # Note that user-defined ABCs do *NOT* generally support structural
    # subtyping. Doing so requires esoteric knowledge of undocumented and
    # mostly private "abc.ABCMeta" metaclass internals unlikely to be
    # implemented by third-party developers. Thanks to the lack of both
    # publicity and standardization, there exists *NO* general-purpose means of
    # detecting whether an arbitrary class supports structural subtyping.
    elif (
        classname.startswith('collections.abc.') or
        classname.startswith('contextlib.')
    ):
        classname = f'<protocol ABC "{classname}">'
    # Else, this is a standard class. In this case, label this class as such.
    else:
        classname = f'<class "{classname}">'

    # Return this labelled classname.
    return classname

# ....................{ LABELLERS ~ exception              }....................
def label_exception(exception: Exception) -> str:
    '''
    Human-readable label describing the passed exception.

    Caveats
    ----------
    **The label returned by this function does not describe the traceback
    originating this exception.** To do so, consider calling the standard
    :func:`traceback.format_exc` function instead.

    Parameters
    ----------
    exception : Exception
        Exception to be labelled.

    Returns
    ----------
    str
        Human-readable label describing this exception.
    '''
    assert isinstance(exception, Exception), (
        f'{repr(exception)} not exception.')

    # Return this exception's label.
    return f'{exception.__class__.__qualname__}: {str(exception)}'

# ....................{ PREFIXERS ~ callable               }....................
def prefix_callable(func: Callable) -> str:
    '''
    Human-readable label describing the passed **callable** (e.g., function,
    method, property) suffixed by delimiting whitespace.

    Parameters
    ----------
    func : Callable
        Callable to be labelled.

    Returns
    ----------
    str
        Human-readable label describing this callable.
    '''
    assert callable(func), f'{repr(func)} uncallable.'

    # Testify, beartype!
    return f'{label_callable(func)} '


def prefix_callable_decorated(func: Callable) -> str:
    '''
    Human-readable label describing the passed **decorated callable** (i.e.,
    callable wrapped by the :func:`beartype.beartype` decorator with a wrapper
    function type-checking that callable) suffixed by delimiting whitespace.

    Parameters
    ----------
    func : Callable
        Decorated callable to be labelled.

    Returns
    ----------
    str
        Human-readable label describing this decorated callable.
    '''

    # Create and return this label.
    return f'@beartyped {prefix_callable(func)}'


def prefix_callable_decorated_pith(
    func: Callable, pith_name: str) -> str:
    '''
    Human-readable label describing either the parameter with the passed name
    *or* return value if this name is ``return`` of the passed **decorated
    callable** (i.e., callable wrapped by the :func:`beartype.beartype`
    decorator with a wrapper function type-checking that callable) suffixed by
    delimiting whitespace.

    Parameters
    ----------
    func : Callable
        Decorated callable to be labelled.
    pith_name : str
        Name of the parameter or return value of this callable to be labelled.

    Returns
    ----------
    str
        Human-readable label describing either the name of this parameter *or*
        this return value.
    '''
    assert isinstance(pith_name, str), f'{repr(pith_name)} not string.'

    # Return a human-readable label describing either...
    return (
        # If this name is "return", the return value of this callable.
        prefix_callable_decorated_return(func)
        if pith_name == 'return' else
        # Else, the parameter with this name of this callable.
        prefix_callable_decorated_arg(func=func, arg_name=pith_name)
    )

# ....................{ PREFIXERS ~ callable : param       }....................
def prefix_callable_decorated_arg(
    func: Callable, arg_name: str) -> str:
    '''
    Human-readable label describing the parameter with the passed name of the
    passed **decorated callable** (i.e., callable wrapped by the
    :func:`beartype.beartype` decorator with a wrapper function type-checking
    that callable) suffixed by delimiting whitespace.

    Parameters
    ----------
    func : Callable
        Decorated callable to be labelled.
    arg_name : str
        Name of the parameter of this callable to be labelled.

    Returns
    ----------
    str
        Human-readable label describing this parameter's name.
    '''
    assert isinstance(arg_name, str), f'{repr(arg_name)} not string.'

    # Create and return this label.
    return f'{prefix_callable_decorated(func)}parameter "{arg_name}" '


def prefix_callable_decorated_arg_value(
    func: Callable, arg_name: str, arg_value: object) -> str:
    '''
    Human-readable label describing the parameter with the passed name and
    trimmed value of the passed **decorated callable** (i.e., callable wrapped
    by the :func:`beartype.beartype` decorator with a wrapper function
    type-checking that callable) suffixed by delimiting whitespace.

    Parameters
    ----------
    func : Callable
        Decorated callable to be labelled.
    arg_name : str
        Name of the parameter of this callable to be labelled.
    arg_value : object
        Value of the parameter of this callable to be labelled.

    Returns
    ----------
    str
        Human-readable label describing this parameter's name and value.
    '''
    assert isinstance(arg_name, str), f'{repr(arg_name)} not string.'

    # Avoid circular import dependencies.
    from beartype._util.text.utiltextrepr import represent_object

    coloured_arg = user_value_colour(f'{arg_name}={represent_object(arg_value)}')
    # Create and return this label.
    return (
        f'{prefix_callable_decorated(func)}parameter '
        f'{coloured_arg} '
    )

# ....................{ PREFIXERS ~ callable : return      }....................
def prefix_callable_decorated_return(func: Callable) -> str:
    '''
    Human-readable label describing the return of the passed **decorated
    callable** (i.e., callable wrapped by the :func:`beartype.beartype`
    decorator with a wrapper function type-checking that callable) suffixed by
    delimiting whitespace.

    Parameters
    ----------
    func : Callable
        Decorated callable to be labelled.

    Returns
    ----------
    str
        Human-readable label describing this return.
    '''

    # Create and return this label.
    return f'{prefix_callable_decorated(func)}return '


def prefix_callable_decorated_return_value(
    func: Callable, return_value: object) -> str:
    '''
    Human-readable label describing the passed trimmed return value of the
    passed **decorated callable** (i.e., callable wrapped by the
    :func:`beartype.beartype` decorator with a wrapper function type-checking
    that callable) suffixed by delimiting whitespace.

    Parameters
    ----------
    func : Callable
        Decorated callable to be labelled.
    return_value : object
        Value returned by this callable to be labelled.

    Returns
    ----------
    str
        Human-readable label describing this return value.
    '''

    # Avoid circular import dependencies.
    from beartype._util.text.utiltextrepr import represent_object

    # Create and return this label.
    return (
        f'{prefix_callable_decorated_return(func)}'
        f'{user_value_colour(represent_object(return_value))} '
    )
