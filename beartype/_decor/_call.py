#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2022 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype dataclass** (i.e., class aggregating *all* metadata for the callable
currently being decorated by the :func:`beartype.beartype` decorator).**

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                           }....................
from beartype.roar import BeartypeDecorWrappeeException
from beartype._decor.conf import BeartypeConf
from beartype._decor._code.codemagic import (
    ARG_NAME_FUNC,
    ARG_NAME_RAISE_EXCEPTION,
)
from beartype._decor._error.errormain import raise_pep_call_exception
from beartype._util.func.utilfunccodeobj import get_func_codeobj
from beartype._util.func.utilfuncscope import CallableScope
from beartype._util.func.utilfunctest import is_func_async_coroutine
from beartype._util.func.utilfuncwrap import unwrap_func
from types import CodeType
from typing import Callable, Dict

# See the "beartype.cave" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ CLASSES                           }....................
class BeartypeCall(object):
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
    func_arg_name_to_hint : dict[str, object]
        Dictionary mapping from the name of each annotated parameter accepted
        by the decorated callable to the type hint annotating that parameter.
    func_arg_name_to_hint_get : Callable[[str, object], object]
        :meth:`dict.get` method bound to the :attr:`func_arg_name_to_hint`
        dictionary, localized as a negligible microoptimization. Blame Guido.
    func_conf : BeartypeConf
        **Beartype configuration** (i.e., self-caching dataclass encapsulating
        all flags, options, settings, and other metadata configuring the
        current decoration of the decorated callable).
    func_wrappee : Optional[Callable]
        Possibly wrapped **decorated callable** (i.e., high-level callable
        currently being decorated by the :func:`beartype.beartype` decorator)
        if the :meth:`reinit` method has been called *or* ``None`` otherwise.
        Note the lower-level :attr:`func_wrappee_wrappee` callable should
        *usually* be accessed instead; although higher-level, this callable may
        only be a wrapper function and hence yield inaccurate or even erroneous
        metadata (especially the code object) for the callable being wrapped.
    func_wrappee_codeobj : CodeType
        Possibly wrapped **decorated callable wrappee code object** (i.e.,
        code object underlying the high-level :attr:`func_wrappee` callable
        currently being decorated by the :func:`beartype.beartype` decorator).
        For efficiency, this code object should *always* be accessed in lieu of
        inefficiently calling the comparatively slower
        :func:`beartype._util.func.utilfunccodeobj.get_func_codeobj` getter.
    func_wrappee_wrappee : Optional[Callable]
        Possibly unwrapped **decorated callable wrappee** (i.e., low-level
        callable wrapped by the high-level :attr:`func_wrappee` callable
        currently being decorated by the :func:`beartype.beartype` decorator)
        if the :meth:`reinit` method has been called *or* ``None`` otherwise.
        If the higher-level :attr:`func_wrappee` callable does *not* actually
        wrap another callable, this callable is identical to that callable.
    func_wrappee_wrappee_codeobj : CodeType
        Possibly unwrapped **decorated callable wrappee code object** (i.e.,
        code object underlying the low-level :attr:`func_wrappee_wrappee`
        callable wrapped by the high-level :attr:`func_wrappee` callable
        currently being decorated by the :func:`beartype.beartype` decorator).
        For efficiency, this code object should *always* be accessed in lieu of
        inefficiently calling the comparatively slower
        :func:`beartype._util.func.utilfunccodeobj.get_func_codeobj` getter.
    func_wrapper_code_call_prefix : Optional[str]
        Code snippet prefixing all calls to the decorated callable in the body
        of the wrapper function wrapping that callable with type checking if
        the :meth:`reinit` method has been called *or* ``None`` otherwise. If
        non-``None``, this string is guaranteed to be either:

        * If the decorated callable is synchronous (i.e., neither a coroutine
          nor asynchronous generator), the empty string.
        * If the decorated callable is asynchronous (i.e., either a coroutine
          nor asynchronous generator), the ``"await "`` keyword.
    func_wrapper_code_signature_prefix : Optional[str]
        Code snippet prefixing the signature declaring the wrapper function
        wrapping the decorated callable with type checking if the
        :meth:`reinit` method has been called *or* ``None`` otherwise. If
        non-``None``, this string is guaranteed to be either:

        * If the decorated callable is synchronous (i.e., neither a coroutine
          nor asynchronous generator), the empty string.
        * If the decorated callable is asynchronous (i.e., either a coroutine
          nor asynchronous generator), the ``"async "`` keyword.
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
    '''

    # ..................{ CLASS VARIABLES                   }..................
    # Slot all instance variables defined on this object to minimize the time
    # complexity of both reading and writing variables across frequently
    # called @beartype decorations. Slotting has been shown to reduce read and
    # write costs by approximately ~10%, which is non-trivial.
    __slots__ = (
        'func_arg_name_to_hint',
        'func_arg_name_to_hint_get',
        'func_conf',
        'func_wrappee_codeobj',
        'func_wrappee_wrappee_codeobj',
        'func_wrappee',
        'func_wrappee_wrappee',
        'func_wrapper_code_call_prefix',
        'func_wrapper_code_signature_prefix',
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
        self.func_arg_name_to_hint: Dict[str, object] = None  # type: ignore[assignment]
        self.func_arg_name_to_hint_get: Callable[[str, object], object] = None  # type: ignore[assignment]
        self.func_conf: BeartypeConf = None  # type: ignore[assignment]
        self.func_wrappee: Callable = None  # type: ignore[assignment]
        self.func_wrappee_codeobj: CodeType = None  # type: ignore[assignment]
        self.func_wrappee_wrappee: Callable = None  # type: ignore[assignment]
        self.func_wrappee_wrappee_codeobj: CodeType = None  # type: ignore[assignment]
        self.func_wrapper_code_call_prefix: str = None  # type: ignore[assignment]
        self.func_wrapper_code_signature_prefix: str = None  # type: ignore[assignment]
        self.func_wrapper_locals: CallableScope = {}
        self.func_wrapper_name: str = None  # type: ignore[assignment]


    def reinit(self, func: Callable, conf: BeartypeConf) -> None:
        '''
        Reinitialize this metadata from the passed callable, typically after
        acquisition of a previously cached instance of this class from the
        :mod:`beartype._util.cache.pool.utilcachepoolobject` submodule.

        If :pep:`563` is conditionally active for this callable, this function
        additionally resolves all postponed annotations on this callable to
        their referents (i.e., the intended annotations to which those
        postponed annotations refer).

        Parameters
        ----------
        func : Callable
            Callable currently being decorated by :func:`beartype.beartype`.
        conf : BeartypeConf
            Beartype configuration configuring :func:`beartype.beartype`
            specific to this callable.

        Raises
        ----------
        :exc:`BeartypeDecorHintPep563Exception`
            If evaluating a postponed annotation on this callable raises an
            exception (e.g., due to that annotation referring to local state no
            longer accessible from this deferred evaluation).
        :exc:`BeartypeDecorWrappeeException`
            If either:

            * This callable is uncallable.
            * This callable is neither a pure-Python function *nor* method;
              equivalently, if this callable is either C-based *or* a class or
              object defining the ``__call__()`` dunder method.
            * This configuration is *not* actually a configuration.
        '''

        # Avoid circular import dependencies.
        from beartype._decor._pep.pep563 import resolve_hints_pep563_if_active

        # If this callable is uncallable, raise an exception.
        if not callable(func):
            raise BeartypeDecorWrappeeException(f'{repr(func)} uncallable.')
        # Else, this callable is callable.
        #
        # If this configuration is *NOT* a configuration, raise an exception.
        elif not isinstance(conf, BeartypeConf):
            raise BeartypeDecorWrappeeException(
                f'{repr(conf)} not beartype configuration.')
        # Else, this configuration is a configuration.

        # Classify this configuration as is.
        self.func_conf = conf

        # Possibly wrapped callable currently being decorated.
        self.func_wrappee = func

        # Possibly unwrapped callable unwrapped from that callable.
        self.func_wrappee_wrappee = unwrap_func(func)

        # Possibly wrapped callable code object.
        self.func_wrappee_codeobj = get_func_codeobj(
            func=func, exception_cls=BeartypeDecorWrappeeException)

        # Possibly unwrapped callable code object.
        self.func_wrappee_wrappee_codeobj = get_func_codeobj(
            func=self.func_wrappee_wrappee,
            exception_cls=BeartypeDecorWrappeeException,
        )

        # Efficiently reduce this local scope back to the dictionary of all
        # parameters unconditionally required by *ALL* wrapper functions.
        self.func_wrapper_locals.clear()
        self.func_wrapper_locals[ARG_NAME_FUNC] = func
        self.func_wrapper_locals[ARG_NAME_RAISE_EXCEPTION] = (
            raise_pep_call_exception)

        # Machine-readable name of the wrapper function to be generated.
        self.func_wrapper_name = func.__name__

        # Resolve all postponed hints on this callable if any *BEFORE* parsing
        # the actual hints these postponed hints refer to.
        resolve_hints_pep563_if_active(self)

        #FIXME: Globally replace all references to "__annotations__" throughout
        #the "beartype._decor" subpackage with references to this instead.
        #Since doing so is a negligible optimization, this is fine... for now.

        # Annotations dictionary *AFTER* resolving all postponed hints.
        #
        # The functools.update_wrapper() function underlying the
        # @functools.wrap decorator underlying all sane decorators propagates
        # this dictionary by default from lower-level wrappees to higher-level
        # wrappers. We intentionally classify the annotations dictionary of
        # this higher-level wrapper, which *SHOULD* be the superset of that of
        # this lower-level wrappee (and thus more reflective of reality).
        self.func_arg_name_to_hint = func.__annotations__

        # dict.get() method bound to this dictionary.
        self.func_arg_name_to_hint_get = self.func_arg_name_to_hint.get

        # If this callable is an asynchronous coroutine callable (i.e.,
        # callable declared with "async def" rather than merely "def" keywords
        # containing *NO* "yield" expressions)...
        #
        # Note that:
        # * The code object of the higher-level wrapper rather than lower-level
        #   wrappee is passed. Why? Because @beartype directly decorates *ONLY*
        #   the former, whose asynchronicity has *NO* relation to that of the
        #   latter. Notably, it is both feasible and (relatively) commonplace
        #   for third-party decorators to enable:
        #   * Synchronous callables to be called asynchronously by wrapping
        #     synchronous callables with asynchronous closures.
        #   * Asynchronous callables to be called synchronously by wrapping
        #     asynchronous callables with synchronous closures. Indeed, our
        #     top-level "conftest.py" pytest plugin does exactly this --
        #     enabling asynchronous tests to be safely called by pytest's
        #     currently synchronous framework.
        # * The higher-level is_func_async() tester is intentionally *NOT*
        #   called here, as doing so would also implicitly prefix all calls to
        #   asynchronous generator callables (i.e., callables also declared
        #   with the "async def" rather than merely "def" keywords but
        #   containing one or more "yield" expressions) with the "await"
        #   keyword. Whereas asynchronous coroutine objects implicitly returned
        #   by all asynchronous coroutine callables return a single awaitable
        #   value, asynchronous generator objects implicitly returned by all
        #   asynchronous generator callables *NEVER* return any awaitable
        #   value; they instead yield one or more values to external "async
        #   for" loops.
        if is_func_async_coroutine(self.func_wrappee_codeobj):
            # Code snippet prefixing all calls to this callable.
            self.func_wrapper_code_call_prefix = 'await '

            # Code snippet prefixing the declaration of the wrapper function
            # wrapping this callable with type-checking.
            self.func_wrapper_code_signature_prefix = 'async '
        # Else, this callable is synchronous (i.e., callable declared with
        # "def" rather than "async def"). In this case, reduce these code
        # snippets to the empty string.
        else:
            self.func_wrapper_code_call_prefix = ''
            self.func_wrapper_code_signature_prefix = ''
