#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **text label utilities** (i.e., low-level callables creating and
returning human-readable strings describing prominent objects or types, intended
to be embedded in human-readable error messages).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.typing import Optional
from beartype._data.datatyping import (
    BeartypeableT,
    TypeStack,
)
from beartype._util.utilobject import (
    get_object_name,
    get_object_type_name,
)
from collections.abc import Callable

# ....................{ LABELLERS ~ beartypeable           }....................
def label_beartypeable_kind(
    # Mandatory parameters.
    obj: BeartypeableT,  # pyright: ignore[reportInvalidTypeVarUse]

    # Optional parameters.
    cls_stack: TypeStack = None,
) -> str:
    '''
    Human-readable label describing the **kind** (i.e.,
    single concise noun synopsizing the category of) the passed **beartypeable**
    (i.e., object that is currently being or has already been decorated by the
    :func:`beartype.beartype` decorator).

    Parameters
    ----------
    obj : BeartypeableT
        Beartypeable to describe the kind of.
    cls_stack : TypeStack
        **Type stack** (i.e., tuple of zero or more arbitrary types describing
        the chain of classes lexically containing this beartypeable if any *or*
        :data:`None`). Defaults to :data:`None`. See also the
        :func:`beartype._decor.decorcore.beartype_object` decorator.

    Returns
    ----------
    str
        Human-readable label describing the kind of this beartypeable.
    '''

    # Avoid circular import dependencies.
    from beartype._util.func.utilfunctest import is_func_python

    # Return either...
    return (
        # If this object is a pure-Python class, an appropriate string;
        'class' if isinstance(obj, type) else
        # If this object is either a pure-Python function *OR* method, an
        # appropriate string;
        (
            'function' if cls_stack is None else 'method'
        ) if is_func_python(obj) else
        # Else, this object is neither a pure-Python class, function, *NOR*
        # method. In this case, fallback to a sane placeholder.
        'object'
    )

# ....................{ LABELLERS ~ callable               }....................
#FIXME: Unit test up the "is_contex" parameter, which is currently untested.
def label_callable(
    # Mandatory parameters.
    func: Callable,

    # Optional parameters.
    is_context: Optional[bool] = None,
) -> str:
    '''
    Human-readable label describing the passed **callable** (e.g., function,
    method, property).

    Parameters
    ----------
    func : Callable
        Callable to be labelled.
    is_context : Optional[bool] = None
        Either:

        * :data:`True`, in which case this label is suffixed by additional
          metadata contextually disambiguating that callable, including:

          * The line number of the first line declaring that callable in its
            underlying source code module file.
          * The absolute filename of that file.

        * :data:`False`, in which case this label is *not* suffixed by such
          metadata.
        * :data:`None`, in which case this label is conditionally suffixed by
          such metadata only if that callable is a lambda function and thus
          ambiguously lacks any semblance of an innate context.

        Defaults to :data:`None`.

    Returns
    ----------
    str
        Human-readable label describing this callable.
    '''
    assert callable(func), f'{repr(func)} uncallable.'

    # Avoid circular import dependencies.
    from beartype._util.func.arg.utilfuncargget import (
        get_func_args_len_flexible)
    from beartype._util.func.utilfunccodeobj import get_func_codeobj
    from beartype._util.func.utilfuncfile import get_func_filename_or_none
    from beartype._util.func.utilfunctest import (
        is_func_async_generator,
        is_func_coro,
        is_func_lambda,
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
        if is_context is None:
            is_context = True
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
    if is_context:
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

# ....................{ LABELLERS ~ type                   }....................
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
    # standard submodule also known to support structural subtyping (e.g.,
    # "collections.abc.Hashable", "contextlib.AbstractContextManager"), label
    # this ABC as a protocol.
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


def label_object_type(obj: object) -> str:
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
