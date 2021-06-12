#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2021 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype dataclass** (i.e., class aggregating *all* metadata for the callable
currently being decorated by the :func:`beartype.beartype` decorator).**

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ TODO                              }....................
#FIXME: Optimize away the call to the inspect.signature() function by
#reimplementing this function to assign to instance variables of the current
#"BeartypeData" object rather than instantiating a new "Signature" object and
#then one new "Parameter" object for each parameter of the decorated callable.
#Note, for example, that we don't need to replicate that function's copying of
#parameter and return value annotations already trivially accessible via the
#"self.func.__annotations__" dunder attribute. Indeed, we only require these
#new "BeartypeData" instance variables:
#
#* "func_param_names", a tuple of all parameter names.
#* "func_param_name_to_kind", a dictionary mapping from each parameter name
#  (including the 'return' pseudo-parameter signifying the return value) to
#  that parameter's kind (e.g., keyword-only, variadic positional). Naturally,
#  parameter kinds should probably be defined as enumeration members of a
#  global public "Enum" class defined in this submodule and accessed elsewhere.
#
#Doing so will be non-trivial but entirely feasible and absolutely worthwhile,
#as the inspect.signature() function is *GUARANTEED* to be a performance
#bottleneck for us. This is low-priority for the moment and may actually never
#happen... but it really should.
#FIXME: Bwaha! We actually did this and even more space- and time-efficiently
#than the above scheme. See the new
#beartype.util.func.utilfuncargs.iter_func_args() generator, called like so:
#    for arg_name, arg_kind, _ in iter_func_args(func): ...
#*AWESOME.* Note we simply ignore the third item of each 3-tuple yielded by
#that generator, as we currently have *NO* need for default values. We will
#elsewhere certainly, but not quite yet. *shrug*

# ....................{ IMPORTS                           }....................
import inspect
from beartype._decor._code.codesnip import (
    ARG_NAME_FUNC,
    ARG_NAME_RAISE_EXCEPTION,
)
from beartype._decor._error.errormain import raise_pep_call_exception
from beartype._util.func.utilfuncscope import CallableScope
from collections.abc import Callable
from inspect import Signature

# See the "beartype.cave" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ CLASSES                           }....................
class BeartypeData(object):
    '''
    **Beartype data** (i.e., object aggregating *all* metadata for the callable
    currently being decorated by the :func:`beartype.beartype` decorator).**

    Design
    ----------
    This the *only* object instantiated by that decorator for that callable,
    substantially reducing both space and time costs. That decorator then
    passes this object to most lower-level functions, which then:

    #. Access read-only instance variables of this object as input.
    #. Modify writable instance variables of this object as output. In
       particular, these lower-level functions typically accumulate pure-Python
       code comprising the generated wrapper function type-checking the
       decorated callable by setting various instance variables of this object.

    Caveats
    ----------
    **This object cannot be used to communicate state between low-level
    memoized callables** (e.g.,
    :func:`beartype._decor._code._pep._pephint.pep_code_check_hint`) **and
    higher-level callables** (e.g.,
    :func:`beartype._decor._code.codemain.generate_code`). Instead, memoized
    callables *must* return that state as additional return values up the call
    stack to those higher-level callables. By definition, memoized callables
    are *not* recalled on subsequent calls passed the same parameters. Since
    only the first call to those callables passed those parameters would set
    the appropriate state on this object intended to be communicated to
    higher-level callables, *all* subsequent calls would subtly fail with
    difficult-to-diagnose issues. See also `<issue #5_>`__, which exhibited
    this very complaint.

    .. _issue #5:
       https://github.com/beartype/beartype/issues/5

    Attributes
    ----------
    func : Optional[Callable]
        **Decorated callable** (i.e., callable currently being decorated by the
        :func:`beartype.beartype` decorator) if the :meth:`reinit` method has
        been called *or* ``None`` otherwise.
    func_codeobj : Optional[CallableCodeObjectType]
        **Code object** (i.e., instance of the :class:`CodeType` type)
        underlying the decorated callable if the :meth:`reinit` method has been
        called *or* ``None`` otherwise.
    func_sig : Optional[inspect.Signature]
        :class:`inspect.Signature` object describing this signature if the
        :meth:`reinit` method has been called *or* ``None`` otherwise.
    func_wrapper_locals : CallableScope
        **Local scope** (i.e., dictionary mapping from the name to value of
        each attribute referenced in the signature) of this wrapper function
        required by this code snippet.
    func_wrapper_name : Optional[str]
        Machine-readable name of the wrapper function to be generated and
        returned by this decorator if the :meth:`reinit` method has been called
        *or* ``None`` otherwise. To efficiently (albeit imperfectly) avoid
        clashes with existing attributes of the module defining that function,
        this name is obfuscated while still preserving human-readability.

    .. _PEP 563:
        https://www.python.org/dev/peps/pep-0563
    '''

    # ..................{ CLASS VARIABLES                   }..................
    # Slot all instance variables defined on this object to minimize the time
    # complexity of both reading and writing variables across frequently
    # called @beartype decorations. Slotting has been shown to reduce read and
    # write costs by approximately ~10%, which is non-trivial.
    __slots__ = (
        'func',
        #FIXME: Uncomment if needed.
        # 'func_codeobj',
        'func_sig',
        'func_wrapper_locals',
        'func_wrapper_name',
    )

    # Coerce instances of this class to be unhashable, preventing spurious
    # issues when accidentally passing these instances to memoized callables by
    # implicitly raising an "TypeError" exceptions on the first call to such a
    # callable. There exists no tangible benefit to permitting these instances
    # to be hashed (and thus also cached), since these instances are:
    # * Specific to the decorated callable and thus *NOT* safely cacheable
    #   across functions applying to different decorated callables.
    # * Already cached via the acquire_object_typed() function called by the
    #   "beartype._decor.main" submodule.
    #
    # See also:
    #     https://docs.python.org/3/reference/datamodel.html#object.__hash__
    __hash__ = None  # type: ignore[assignment]

    # ..................{ INITIALIZERS                      }..................
    def __init__(self) -> None:
        '''
        Initialize this metadata by nullifying all instance variables.

        Caveats
        ----------
        **This class is not intended to be explicitly instantiated.** Instead,
        callers are expected to (in order):

        #. Acquire cached instances of this class via the
           :mod:`beartype._util.cache.pool.utilcachepoolobjecttyped` submodule.
        #. Call the :meth:`reinit` method on these instances to properly
           initialize these instances.
        '''

        # Nullify all remaining instance variables.
        self.func: Callable = None  # type: ignore[assignment]
        #FIXME: Uncomment if needed.
        # self.func_codeobj: CallableCodeObjectType = None  # type: ignore[assignment]
        self.func_sig: Signature = None  # type: ignore[assignment]
        self.func_wrapper_locals: CallableScope = {}
        self.func_wrapper_name: str = None  # type: ignore[assignment]


    def reinit(self, func: Callable) -> None:
        '''
        Reinitialize this metadata from the passed callable, typically after
        acquisition of a previously cached instance of this class from the
        :mod:`beartype._util.cache.pool.utilcachepoolobject` submodule.

        If `PEP 563`_ is conditionally active for this callable, this function
        additionally resolves all postponed annotations on this callable to
        their referents (i.e., the intended annotations to which those
        postponed annotations refer).

        Parameters
        ----------
        func : Callable
            Callable currently being decorated by :func:`beartype.beartype`.

        Raises
        ----------
        BeartypeDecorHintPep563Exception
            If evaluating a postponed annotation on this callable raises an
            exception (e.g., due to that annotation referring to local state no
            longer accessible from this deferred evaluation).
        BeartypeDecorWrappeeException
            If this callable is neither a pure-Python function *nor* method;
            equivalently, if this callable is either C-based *or* a class or
            object defining the ``__call__()`` dunder method.

        .. _PEP 563:
           https://www.python.org/dev/peps/pep-0563
        '''
        assert callable(func), f'{repr(func)} uncallable.'

        # Avoid circular import dependencies.
        from beartype._decor._pep563 import resolve_hints_pep563_if_active

        # Callable currently being decorated.
        self.func = func

        #FIXME: Uncomment if needed.
        # Code object underlying that callable unwrapped if that callable is
        # pure-Python *OR* raise an exception otherwise.
        # self.func_codeobj = get_func_unwrapped_codeobj(
        #     func=func, exception_cls=BeartypeDecorWrappeeException)

        # Efficiently Reduce this local scope back to the dictionary of all
        # parameters unconditionally required by *ALL* wrapper functions.
        self.func_wrapper_locals.clear()
        self.func_wrapper_locals[ARG_NAME_FUNC] = func
        self.func_wrapper_locals[ARG_NAME_RAISE_EXCEPTION] = (
            raise_pep_call_exception)

        # Machine-readable name of the wrapper function to be generated.
        self.func_wrapper_name = func.__name__

        # Nullify all remaining attributes for safety *BEFORE* passing this
        # object to any functions (e.g., resolve_hints_pep563_if_active()).
        self.func_sig = None  # type: ignore[assignment]

        # Resolve all postponed hints on this callable if any *BEFORE* parsing
        # the actual hints these postponed hints refer to.
        resolve_hints_pep563_if_active(self)

        # "Signature" instance encapsulating this callable's signature,
        # dynamically parsed by the stdlib "inspect" module from this callable.
        self.func_sig = inspect.signature(func)
