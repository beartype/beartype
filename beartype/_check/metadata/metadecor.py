#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype decorator call metadata dataclass** (i.e., class aggregating *all*
metadata for the callable currently being decorated by the
:func:`beartype.beartype` decorator).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.roar import BeartypeDecorWrappeeException
from beartype.typing import (
    TYPE_CHECKING,
    Callable,
    # Dict,
    FrozenSet,
    Optional,
)
from beartype._cave._cavefast import CallableCodeObjectType
from beartype._cave._cavemap import NoneTypeOr
from beartype._check.forward.fwdscope import BeartypeForwardScope
from beartype._conf.confmain import BeartypeConf
from beartype._data.hint.datahintpep import DictStrToHint
from beartype._data.hint.datahinttyping import (
    LexicalScope,
    TypeStack,
)
from beartype._util.cache.pool.utilcachepoolinstance import (
    acquire_instance,
    release_instance,
)
from beartype._util.func.utilfunccodeobj import (
    get_func_codeobj,
    get_func_codeobj_or_none,
)
from beartype._util.func.utilfuncget import get_func_annotations
from beartype._util.func.utilfunctest import (
    is_func_coro,
    is_func_nested,
)
from beartype._util.func.utilfuncwrap import unwrap_func_all_isomorphic

# ....................{ CLASSES                            }....................
class BeartypeDecorMeta(object):
    '''
    **Beartype decorator call metadata** (i.e., object encapsulating *all*
    metadata for the callable currently being decorated by the
    :func:`beartype.beartype` decorator).

    Design
    ------
    This the *only* object instantiated by that decorator for that callable,
    substantially reducing both space and time costs. That decorator then
    passes this object to most lower-level functions, which then:

    #. Access read-only instance variables of this object as input.
    #. Modify writable instance variables of this object as output. In
       particular, these lower-level functions typically accumulate pure-Python
       code comprising the generated wrapper function type-checking the
       decorated callable by setting various instance variables of this object.

    Caveats
    -------
    **This object cannot be used to communicate state between low-level
    memoized callables** (e.g.,
    :func:`beartype._check.code.codemake.make_func_pith_code`) **and
    high-level unmemoized callables** (e.g.,
    :func:`beartype._decor.wrap.wrapmain.generate_code`). Instead, low-level
    memoized callables *must* return that state as additional return values up
    the call stack to those high-level unmemoized callables. By definition,
    memoized callables are *not* recalled on subsequent calls passed the same
    parameters. Since only the first call to those callables passed those
    parameters would set the appropriate state on this object intended to be
    communicated to unmemoized callables, *all* subsequent calls would subtly
    fail with difficult-to-diagnose issues. See also `<issue #5_>`__, which
    exhibited this very complaint.

    .. _issue #5:
       https://github.com/beartype/beartype/issues/5

    Attributes
    ----------
    cls_stack : TypeStack
        **Type stack** (i.e., either tuple of zero or more arbitrary types *or*
        :data:`None`). See also the parameter of the same name accepted by the
        :func:`beartype._decor.decorcore.beartype_object` function for details.
    conf : BeartypeConf
        **Beartype configuration** (i.e., self-caching dataclass encapsulating
        all flags, options, settings, and other metadata configuring the
        current decoration of the decorated callable).
    func_arg_name_to_hint : dict[str, Hint]
        **Type hint dictionary** (i.e., mapping from the name of each annotated
        parameter accepted by the decorated callable to the type hint annotating
        that parameter).
    func_arg_name_to_hint_get : Callable[[str, object], object]
        :meth:`dict.get` method bound to the :attr:`func_arg_name_to_hint`
        dictionary, localized as a negligible microoptimization. Blame Guido.
    func_wrappee : Optional[Callable]
        Possibly wrapping **decorated callable** (i.e., high-level callable
        currently being decorated by the :func:`beartype.beartype` decorator).
        Note the lower-level :attr:`func_wrappee_wrappee` callable should
        *usually* be accessed instead; although higher-level, this callable may
        only be a wrapper function and hence yield inaccurate or even erroneous
        metadata (especially the code object) for the callable being wrapped.
    func_wrappee_is_nested : bool
        Either:

        * If this wrappee callable is **nested** (i.e., declared in the body of
          another pure-Python callable or class), :data:`True`.
        * If this wrappee callable is **global** (i.e., declared at module scope
          in its submodule), :data:`False`.
    func_wrappee_scope_forward : Optional[BeartypeForwardScope]
        Either:

        * If this wrappee callable is annotated by at least one **stringified
          type hint** (i.e., declared as a :pep:`484`- or :pep:`563`-compliant
          forward reference referring to an actual type hint that has yet to be
          declared in the local and global scopes declaring this callable) that
          :mod:`beartype` has already resolved to its referent, this wrappee
          callable's **forward scope** (i.e., dictionary mapping from the name
          to value of each locally and globally accessible attribute in the
          local and global scope of this wrappee callable as well as deferring
          the resolution of each currently undeclared attribute in that scope by
          replacing that attribute with a forward reference proxy resolved only
          when that attribute is passed as the second parameter to an
          :func:`isinstance`-based runtime type-check).
        * Else, :data:`None`.

        Note that:

        * The reconstruction of this scope is computationally expensive and thus
          deferred until needed to resolve the first stringified type hint
          annotating this wrappee callable.
        * All callables have local scopes *except* global functions, whose local
          scopes are by definition the empty dictionary.
    func_wrappee_scope_nested_names : Optional[frozenset[str]]
        Either:

        * If this wrappee callable is annotated by at least one stringified type
          hint that :mod:`beartype` has already resolved to its referent,
          either:

          * If this wrappee callable is **nested** (i.e., declared in the body
            of another pure-Python callable or class), the non-empty frozen set
            of the unqualified names of all parent callables lexically
            containing this nested wrappee callable (including this nested
            wrappee callable itself).
          * Else, this wrappee callable is declared at global scope in its
            submodule. In this case, the empty frozen set.

        * Else, :data:`None`.
    func_wrappee_wrappee : Optional[Callable]
        Possibly unwrapped **decorated callable wrappee** (i.e., low-level
        callable wrapped by the high-level :attr:`func_wrappee` callable
        currently being decorated by the :func:`beartype.beartype` decorator).
        If the higher-level :attr:`func_wrappee` callable does *not* actually
        wrap another callable, this callable is identical to that callable.
    func_wrappee_wrappee_codeobj : CallableCodeObjectType
        Possibly unwrapped **decorated callable wrappee code object** (i.e.,
        code object underlying the low-level :attr:`func_wrappee_wrappee`
        callable wrapped by the high-level :attr:`func_wrappee` callable
        currently being decorated by the :func:`beartype.beartype` decorator).
        For efficiency, this code object should *always* be accessed in lieu of
        inefficiently calling the comparatively slower
        :func:`beartype._util.func.utilfunccodeobj.get_func_codeobj` getter.
    func_wrapper_code_call_prefix : Optional[str]
        Code snippet prefixing all calls to the decorated callable in the body
        of the wrapper function wrapping that callable with type checking. This
        string is guaranteed to be either:

        * If the decorated callable is synchronous (i.e., neither a coroutine
          nor asynchronous generator), the empty string.
        * If the decorated callable is asynchronous (i.e., either a coroutine
          nor asynchronous generator), the ``"await "`` keyword.
    func_wrapper_code_signature_prefix : Optional[str]
        Code snippet prefixing the signature declaring the wrapper function
        wrapping the decorated callable with type checking. This string is
        guaranteed to be either:

        * If the decorated callable is synchronous (i.e., neither a coroutine
          nor asynchronous generator), the empty string.
        * If the decorated callable is asynchronous (i.e., either a coroutine
          or asynchronous generator), the ``"async "`` keyword.
    func_wrapper_scope : LexicalScope
        **Local scope** (i.e., dictionary mapping from the name to value of
        each attribute referenced in the signature) of this wrapper function.
    func_wrapper_name : Optional[str]
        Unqualified basename of the type-checking wrapper function to be
        generated and returned by the current invocation of the
        :func:`beartype.beartype` decorator.
    '''

    # ..................{ CLASS VARIABLES                    }..................
    # Slot all instance variables defined on this object to minimize the time
    # complexity of both reading and writing variables across frequently
    # called @beartype decorations. Slotting has been shown to reduce read and
    # write costs by approximately ~10%, which is non-trivial.
    __slots__ = (
        'cls_stack',
        'conf',
        'func_arg_name_to_hint',
        'func_arg_name_to_hint_get',
        'func_wrappee',
        'func_wrappee_is_nested',
        'func_wrappee_scope_forward',
        'func_wrappee_scope_nested_names',
        'func_wrappee_wrappee',
        'func_wrappee_wrappee_codeobj',
        'func_wrapper_code_call_prefix',
        'func_wrapper_code_signature_prefix',
        'func_wrapper_scope',
        'func_wrapper_name',
    )

    # Squelch false negatives from mypy. This is absurd. This is mypy. See:
    #     https://github.com/python/mypy/issues/5941
    if TYPE_CHECKING:
        cls_stack: TypeStack
        conf: BeartypeConf
        func_arg_name_to_hint: DictStrToHint
        func_arg_name_to_hint_get: Callable[[str, object], object]
        func_wrappee: Callable
        func_wrappee_is_nested: bool
        func_wrappee_scope_forward: Optional[BeartypeForwardScope]
        func_wrappee_scope_nested_names: Optional[FrozenSet[str]]
        func_wrappee_wrappee: Callable
        func_wrappee_wrappee_codeobj: CallableCodeObjectType
        func_wrapper_code_call_prefix: str
        func_wrapper_code_signature_prefix: str
        func_wrapper_scope: LexicalScope
        func_wrapper_name: str

    # Coerce instances of this class to be unhashable, preventing spurious
    # issues when accidentally passing these instances to memoized callables by
    # implicitly raising a "TypeError" exception on the first call to those
    # callables. There exists no tangible benefit to permitting these instances
    # to be hashed (and thus also cached), since these instances are:
    # * Specific to the decorated callable and thus *NOT* safely cacheable
    #   across functions applying to different decorated callables.
    # * Already cached via the acquire_instance() function called by the
    #   "beartype._decor.decormain" submodule.
    #
    # See also:
    #     https://docs.python.org/3/reference/datamodel.html#object.__hash__
    __hash__ = None  # type: ignore[assignment]

    # ..................{ INITIALIZERS                       }..................
    def __init__(self) -> None:
        '''
        Initialize this metadata by nullifying all instance variables.

        Caveats
        -------
        **This class is not intended to be explicitly instantiated.** Instead,
        callers are expected to (in order):

        #. Acquire cached instances of this class via the
           :mod:`beartype._util.cache.pool.utilcachepoolinstance` submodule.
        #. Call the :meth:`reinit` method on these instances to properly
           initialize these instances.
        '''

        # Nullify instance variables for safety.
        self.deinit()


    def deinit(self) -> None:
        '''
        Deassociate this metadata from the callable passed to the most recent
        call of the :meth:`reinit` method, typically before releasing this
        instance of this class back to the
        :mod:`beartype._util.cache.pool.utilcachepoolobject` submodule.

        This method prevents a minor (albeit still undesirable, of course)
        memory leak in which this instance would continue to remain accidentally
        associated with that callable despite this instance being released back
        to its object pool, which would then prevent that callable from being
        garbage-collected on the finalization of the last external reference to
        that callable.
        '''

        # Nullify instance variables for safety.
        self.func_wrapper_scope: LexicalScope = {}
        self.cls_stack = (  # type: ignore[assignment]
        self.conf) = (  # type: ignore[assignment]
        self.func_arg_name_to_hint) = (  # type: ignore[assignment]
        self.func_arg_name_to_hint_get) = (  # type: ignore[assignment]
        self.func_wrappee) = (  # type: ignore[assignment]
        self.func_wrappee_is_nested) = (  # type: ignore[assignment]
        self.func_wrappee_scope_forward) = (  # type: ignore[assignment]
        self.func_wrappee_scope_nested_names) = (  # type: ignore[assignment]
        self.func_wrappee_wrappee) = (  # type: ignore[assignment]
        self.func_wrappee_wrappee_codeobj) = (  # type: ignore[assignment]
        self.func_wrapper_code_call_prefix) = (  # type: ignore[assignment]
        self.func_wrapper_code_signature_prefix) = (  # type: ignore[assignment]
        self.func_wrapper_name) = None  # type: ignore[assignment]


    def reinit(
        self,

        # Mandatory parameters.
        func: Callable,
        conf: BeartypeConf,

        # Optional parameters.
        cls_stack: TypeStack = None,
        wrapper: Optional[Callable] = None,
    ) -> None:
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
        cls_stack : TypeStack
            **Type stack** (i.e., either tuple of zero or more arbitrary types
            *or* :data:`None`). See also the parameter of the same name accepted
            by the :func:`beartype._decor.decorcore.beartype_object` function.
        wrapper : Optional[Callable]
            Wrapper callable to be unwrapped in the event that the callable
            currently being decorated by :func:`beartype.beartype` differs from
            the callable to be unwrapped. Typically, these two callables are the
            same. Edge cases in which these two callables differ include:

            * When ``wrapper`` is a **pseudo-callable** (i.e., otherwise
              uncallable object whose type renders that object callable by
              defining the ``__call__()`` dunder method) *and* ``func`` is that
              ``__call__()`` dunder method. If that pseudo-callable wraps a
              lower-level callable, then that pseudo-callable (rather than
              ``__call__()`` dunder method) defines the ``__wrapped__`` instance
              variable providing that callable.

            Defaults to :data:`None`, in which case this parameter *actually*
            defaults to ``func``.

        Raises
        ------
        BeartypePep563Exception
            If evaluating a postponed annotation on this callable raises an
            exception (e.g., due to that annotation referring to local state no
            longer accessible from this deferred evaluation).
        BeartypeDecorWrappeeException
            If either:

            * This callable is uncallable.
            * This callable is neither a pure-Python function *nor* method;
              equivalently, if this callable is either C-based *or* a class or
              object defining the ``__call__()`` dunder method.
            * This configuration is *not* actually a configuration.
            * ``cls_owner`` is neither a class *nor* :data:`None`.
        '''

        #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        # CAUTION: Note this method intentionally avoids creating and passing an
        # "exception_prefix" substring to callables called below. Why? Because
        # exhaustive profiling has shown that creating that substring consumes a
        # non-trivial slice of decoration time. In other words, efficiency.
        #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

        # If the caller failed to pass a callable to be unwrapped, default that
        # to the callable to be type-checked.
        if wrapper is None:
            wrapper = func
        # Else, the caller passed a callable to be unwrapped. Preserve it up!
        # print(f'Beartyping func {repr(func)} + wrapper {repr(wrapper)}...')

        # If the callable to be type-checked is uncallable, raise an exception.
        if not callable(func):
            raise BeartypeDecorWrappeeException(f'{repr(func)} uncallable.')
        # Else, that callable is callable.
        #
        # If the callable to be unwrapped is uncallable, raise an exception.
        elif not callable(wrapper):
            raise BeartypeDecorWrappeeException(f'{repr(wrapper)} uncallable.')
        # Else, that callable is callable.
        #
        # If this configuration is *NOT* a configuration, raise an exception.
        elif not isinstance(conf, BeartypeConf):
            raise BeartypeDecorWrappeeException(
                f'"conf" {repr(conf)} not beartype configuration.')
        # Else, this configuration is a configuration.
        #
        # If this class stack is neither a tuple *NOR* "None", raise an
        # exception.
        elif not isinstance(cls_stack, NoneTypeOr[tuple]):
            raise BeartypeDecorWrappeeException(
                f'"cls_stack" {repr(cls_stack)} neither tuple nor "None".')
        # Else, this class stack is either a tuple *OR* "None".

        # If the caller passed a non-empty class stack...
        if cls_stack:
            # For each item of this class stack...
            for cls_stack_item in cls_stack:
                # If this item is *NOT* a type, raise an exception.
                if not isinstance(cls_stack_item, type):
                    raise BeartypeDecorWrappeeException(
                        f'"cls_stack" item {repr(cls_stack_item)} not type.')
                # Else, this item is a type.
        # Else, the caller either passed no class stack *OR* an empty class
        # stack. In either case, ignore this parameter.

        # Classify all passed parameters.
        self.conf = conf
        self.cls_stack = cls_stack

        # Wrappee callable currently being decorated.
        self.func_wrappee = func

        # Possibly unwrapped callable unwrapped from this wrappee callable.
        self.func_wrappee_wrappee = unwrap_func_all_isomorphic(
            func=func, wrapper=wrapper)
        # print(f'func_wrappee: {self.func_wrappee}')
        # print(f'func_wrappee_wrappee: {self.func_wrappee_wrappee}')
        # print(f'{dir(self.func_wrappee_wrappee)}')

        # True only if this wrappee callable is nested. As a minor efficiency
        # gain, we can avoid the slightly expensive call to is_func_nested() by
        # noting that:
        # * If the class stack is non-empty, then this wrappee callable is
        #   necessarily nested in one or more classes.
        # * Else, defer to the is_func_nested() tester.
        self.func_wrappee_is_nested = bool(cls_stack) or is_func_nested(func)

        # Defer the resolution of both global and local scopes for this wrappee
        # callable until needed to subsequently resolve stringified type hints.
        self.func_wrappee_scope_forward = None
        self.func_wrappee_scope_nested_names = None

        # Possibly wrapped callable wrappee code object (i.e., code object
        # underlying the callable currently being type-checked by the
        # @beartype.beartype decorator) if this wrappee is pure-Python *OR*
        # "None" otherwise.
        #
        # Note that only the possibly unwrapped callable (i.e.,
        # "self.func_wrappee_wrappee") need actually be pure-Python. Whereas the
        # latter is required to have a code object, the "self.func_wrappee" is
        # permitted to be C-based and thus *NOT* have a code object.
        func_wrappee_codeobj = get_func_codeobj_or_none(func)

        # Possibly unwrapped callable code object.
        self.func_wrappee_wrappee_codeobj = get_func_codeobj(
            func=self.func_wrappee_wrappee,
            exception_cls=BeartypeDecorWrappeeException,
        )

        # Efficiently reduce this local scope back to the dictionary of all
        # parameters unconditionally required by *ALL* wrapper functions.
        self.func_wrapper_scope.clear()

        # Machine-readable name of the wrapper function to be generated.
        self.func_wrapper_name = func.__name__

        #FIXME: Globally replace all references to "__annotations__" throughout
        #the "beartype._decor" subpackage with references to this instead.
        #Since doing so is a negligible optimization, this is fine... for now.
        #FIXME: *WOOPS.* Due to PEP 649, we absolutely need to get out ahead of
        #this before Python 3.13 and catastrophe strike. Notably:
        #* Define a new "beartype._data.hint.datahinttyping.Hintable" type hint
        #  resembling:
        #      from beartype._cave._cavefast import (
        #          FunctionType,
        #          MethodBoundInstanceOrClassType,
        #      )
        #
        #      Hintable = Union[
        #          FunctionType,                    # <-- pure-Python function
        #          MethodBoundInstanceOrClassType,  # <-- pure-Python method
        #          ModuleType,  # <-- C-based *OR* pure-Python module
        #          type,        # <-- C-based *OR* pure-Python class
        #      ]
        #      '''
        #      PEP-compliant type hint matching any **hintable** (i.e., ideally
        #      pure-Python object defining the ``__annotations__`` dunder
        #      attribute as well as the ``__annotate__`` dunder callable if the
        #      active Python interpreter targets Python >= 3.13).
        #      '''
        #* Define a new "beartype._data.cls.datacls.HintableTypes" tuple union
        #  resembling:
        #      from beartype._cave._cavefast import (
        #          FunctionType,
        #          MethodBoundInstanceOrClassType,
        #      )
        #
        #      HintableTypes = (
        #          FunctionType,                    # <-- pure-Python function
        #          MethodBoundInstanceOrClassType,  # <-- pure-Python method
        #          ModuleType,  # <-- C-based *OR* pure-Python module
        #          type,        # <-- C-based *OR* pure-Python class
        #      )
        #* Rename "HintAnnotations" to "HintableAnnotations" in that same
        #  submodule.
        #* Define a new "beartype._util.hintable" subpackage.
        #* Define a new "beartype._util.hintable.utilhintableget" submodule.
        #* Define a new get_hintable_hint_name_to_hint() getter in that
        #  submodule whose signature resembles:
        #      from beartype._data.hint.datahinttyping import (
        #          Hintable,
        #          HintableAnnotations,
        #      )
        #
        #      def get_hintable_hint_name_to_hint(hintable: Hintable) -> (
        #          HintableAnnotations):
        #* Define a new "BeartypePep649Exception" exception type, please.
        #* Implement this getter conditionally depending on the active Python
        #  interpreter as follows:
        #      from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_13
        #
        #      # If the active Python interpreter targets Python >= 3.13, defer
        #      # to the PEP 649-compliant __annotate__() dunder callable rather
        #      # than the PEP 484-compliant __annotations__() dunder attribute.
        #      # Why? Because the latter simply reduces to calling
        #      # "self.__annotate__(inspect.VALUE)", which raises a "NameError"
        #      # exception if the passed hintable is annotated by one or more
        #      # unquoted forward references. Unacceptable!
        #      #
        #      # Note that this getter is memoized *ONLY* under Python >= 3.13.
        #      # Why? Because __annotate__() *ONLY* memoizes the annotations
        #      # dictionary it creates and returns when passed "inspect.VALUE".
        #      # When passed *ANY* other "format" value, __annotate__() avoids
        #      # avoids caching its return value. Creating this return value is
        #      # algorithmically non-trivial and computationally expensive. So,
        #      # we are effectively required to memoize this return value here.
        #      if IS_PYTHON_AT_LEAST_3_13:
        #          # Defer version-specific imports.
        #          from inspect import FORWARDREF
        #          from beartype.roar import BeartypePep649Exception
        #          from beartype._data.cls.datacls import HintableTypes
        #
        #          @callable_cached
        #          def get_hintable_hint_name_to_hint(hintable: Hintable) -> (
        #              HintableAnnotations):
        #
        #              if not isinstance(hintable, HintableTypes):
        #                  raise BeartypePep649(
        #                      f'Object {repr(hintable)} not hintable '
        #                      f'(i.e., defines no PEP 649 __annotate__() '
        #                      f'data descriptor).'
        #                  )
        #              # Note that this will probably become a shockingly common
        #              # occurrence. PEP 649 openly encourages users to destroy
        #              # the "__annotate__" dunder method by setting that method
        #              # to "None": e.g.,
        #              #     Failing that, it’s best to overwrite the object’s
        #              #     __annotate__ method with None to prevent
        #              #     inspect.get_annotations from generating stale
        #              #     results for SOURCE and FORWARDREF formats.
        #              elif hintable.__annotate__ is None:
        #                  raise BeartypePep649(
        #                      f'Object {repr(hintable)} annotations destroyed '
        #                      f'(i.e., PEP 649 __annotate__() data descriptor '
        #                      f'externally set to "None").'
        #                  )
        #
        #              # Return the annotations dictionary for this hintable,
        #              # implicitly replacing all unquoted forward references to
        #              # undefined attributes in type hints described by this
        #              # dictionary with "typing.ForwardRef" proxies.
        #              return hintable.__annotate__(FORWARDREF)
        #      else:
        #          def get_hintable_hint_name_to_hint(hintable: Hintable) -> (
        #              HintableAnnotations):
        #              return hintable.__annotations__
        #* Grep the codebase for all references to "__annotations__". All such
        #  references *MUST* immediately be refactored as calls to
        #  get_hintable_hint_name_to_hint().
        #FIXME: *SUPERB.* However, note that even the following might not
        #suffice for Python >= 3.13. Why? Because, to quote PEP 649:
        #    Initially, inspect.get_annotations will call the object’s
        #    __annotate__ method requesting the desired format. If that raises
        #    NotImplementedError, inspect.get_annotations will construct a “fake
        #    globals” environment, then call the object’s __annotate__ method.
        #    inspect.get_annotations produces FORWARDREF format by creating a
        #    new empty “fake globals” dict, pre-populating it with the current
        #    contents of the __annotate__ method’s globals dict, binding the
        #    “fake globals” dict to the object’s __annotate__ method, calling
        #    that requesting VALUE format, and returning the result.
        #
        #...heh. So, our get_hintable_hint_name_to_hint() implementation needs
        #to either:
        #* Just defer to inspect.get_annotations(). I'm *NOT* particularly keen
        #  on that. That implementation is likely to be suboptimal and, more
        #  importantly, outside our control. Moreover, there's really *NO* need
        #  to defer to somebody else's implementation. Why? Because we basically
        #  already implemented the entirety of inspect.get_annotations() without
        #  knowing it as our "beartype._check.forward" subpackage. Ergo...
        #* Derive mild inspiration from inspect.get_annotations(), but otherwise
        #  substitute stock CPython stuff like "typing.ForwardRef" with
        #  equivalent functionality from our own "beartype._check.forward"
        #  subpackage.
        #
        #Control is pivotal here. We can iterate on underlying issues
        #significantly faster than CPython. We can also optimize and
        #microoptimize this as we see fit to generate even better yields.
        #
        #Note, however, that PEP 649-compliant stringizers are pretty
        #phenomenal. It's unlikely that @beartype could or even should implement
        #a better internal alternative. Ideally, our
        #"beartype._check.forward.reference" API could be mildly refactored to
        #internally support PEP 649-compliant stringizers under Python >= 3.13.
        #Is that even feasible? Who knows. But... it's certainly desirable.
        #FIXME: Actually... let's just defer to inspect.get_annotations(). Look.
        #I know. I know. It's a shame. We threw a veritable ton of volunteer
        #hours at "beartype._check.forward". But inspect.get_annotations() is
        #strictly better than anything we've done or could reasonably do.
        #Seriously. That train is moving on. Honestly, reproducing
        #inspect.get_annotations() in @beartype is probably *NOT* feasible.
        #inspect.get_annotations() does all sorts of intense and crazy stuff:
        #    The “fake globals” environment will also have to create a fake
        #    “closure”, a tuple of ForwardRef objects pre-created with the names
        #    of the free variables referenced by the __annotate__ method.
        #
        #There's just no way we're dynamically constructing fake closures. So,
        #inspect.get_annotations() is it -- at least, initially. I mean, if
        #significant issues end up arising from our usage of
        #inspect.get_annotations()... well, that's fine. At that point, we'd
        #obviously begin deriving our alternative heavily inspired by
        #inspect.get_annotations(). Until then, we genuinely do need to assume
        #that CPython devs know what they are talking about. Call that getter.

        # Dictionary mapping from the name of each annotated parameter accepted
        # by the unwrapped callable to the type hint annotating that parameter
        # *AFTER* resolving all postponed type hints elsewhere.
        #
        # Note that:
        # * The functools.update_wrapper() function underlying the
        #   @functools.wrap decorator underlying all sane decorators propagates
        #   this dictionary from lower-level wrappees to higher-level wrappers
        #   by default. We intentionally classify the annotations dictionary of
        #   this higher-level wrapper, which *SHOULD* be the superset of that of
        #   this lower-level wrappee (and thus more reflective of reality).
        # * The type hints annotating the callable to be unwrapped (i.e.,
        #   "wrapper)" are preferred to those annotating the callable to be
        #   type-checked (i.e., "func"). Why? Because the callable to be
        #   unwrapped is either the original pure-Python function or method
        #   defined by the user *OR* a pseudo-callable object transitively
        #   wrapping that function or method; in either case, the type hints
        #   annotating that callable are guaranteed to be authoritative.
        #   However, the callable to be type-checked is in this case typically
        #   only a thin isomorphic wrapper deferring to the callable to be
        #   unwrapped.
        #
        # Consider the typical use case invoking this conditional logic:
        #     from functools import update_wrapper, wraps
        #
        #     def probably_lies(lies: str, more_lies: str) -> str:
        #         return lies + more_lies
        #
        #     class LyingClass(object):
        #         def __call__(self, *args, **kwargs):
        #             return probably_lies(*args, **kwargs)
        #
        #     cheating_object = LyingClass()
        #     update_wrapper(wrapper=cheating_object, wrapped=probably_lies)
        #     print(cheating_object.__annotations__)
        #
        # ...which would print:
        #     {'lies': <class 'str'>, 'more_lies': <class 'str'>, 'return':
        #     <class 'str'>}
        #
        # We thus see that this use case successfully propagated the
        # "__annotations__" dunder dictionary from the probably_lies()
        # function onto the pseudo-callable "cheating_object" object.
        #
        # In this case, the caller would have called this method as:
        #     decor_meta.reinit(
        #         func=cheating_object.__call__, wrapper=cheating_object)
        #
        # Note that "func" (i.e., the callable to be type-checked) is only a
        # thin isomorphic wrapper deferring to "wrapper" (i.e., the callable to
        # be unwrapped). Even if "func" were annotated with type hints, those
        # type hints would be useless for most intents and purposes.
        self.func_arg_name_to_hint = get_func_annotations(wrapper)
        # print(f'Beartyping func {repr(func)} + wrapper {repr(wrapper)} w/ annotations {self.func_arg_name_to_hint}...')

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
        if func_wrappee_codeobj and is_func_coro(func_wrappee_codeobj):
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

    # ..................{ DUNDERS                            }..................
    def __repr__(self) -> str:
        '''
        Machine-readable representation of this metadata.
        '''

        # Represent this metadata with just the minimal subset of metadata
        # needed to reasonably describe this metadata.
        return (
            f'{self.__class__.__name__}('
            f'func={repr(self.func_wrappee)}, '
            f'conf={repr(self.conf)}'
            f')'
        )

    # ..................{ LABELLERS                          }..................
    def label_func_wrapper(self) -> str:
        '''
        Human-readable label describing the type-checking wrapper function to be
        generated and returned by the current invocation of the
        :func:`beartype.beartype` decorator.

        This method is a non-negligible optimization. Since string munging is
        *extremely* slow and this method necessarily munges strings, external
        callers delay this string munging as late as possible by delaying all
        calls to this method as late as possible (e.g., until an exception
        message requiring this label is actually required).
        '''

        # One-liner of Ultimate Beauty: we invoke thee in this line!
        return f'@beartyped {self.func_wrapper_name}() wrapper'

# ....................{ FACTORIES                          }....................
#FIXME: Unit test us up, please.
def make_beartype_call(**kwargs) -> BeartypeDecorMeta:
    '''
    **Beartype call metadata** (i.e., object encapsulating *all* metadata for
    the passed user-defined callable, typically currently being decorated by the
    :func:`beartype.beartype` decorator).

    Caveats
    -------
    **This higher-level factory function should always be called in lieu of
    instantiating the** :class:`.BeartypeDecorMeta` **class directly.** Why?
    Brute-force efficiency. This factory efficiently reuses previously
    instantiated :class:`.BeartypeDecorMeta` objects rather than inefficiently
    instantiating new :class:`.BeartypeDecorMeta` objects.

    **The caller must pass the metadata returned by this factory back to the**
    :func:`beartype._util.cache.pool.utilcachepoolinstance.release_instance`
    **function.** If accidentally omitted, this metadata will simply be
    garbage-collected rather than available for efficient reuse by this factory.
    Although hardly a worst-case outcome, omitting that explicit call largely
    defeats the purpose of calling this factory in the first place.

    Parameters
    ----------
    All keyword parameters are passed as is to the :meth:`.BeartypeDecorMeta.reinit`
    method.

    Returns
    -------
    BeartypeDecorMeta
        Beartype call metadata describing this callable.
    '''

    # Acquire previously cached beartype call metadata from its object pool.
    decor_meta = acquire_instance(BeartypeDecorMeta)

    # Reinitialize this metadata with the passed keyword parameters.
    decor_meta.reinit(**kwargs)

    # Return this metadata.
    return decor_meta


#FIXME: Unit test us up, please.
def cull_beartype_call(decor_meta: BeartypeDecorMeta) -> None:
    '''
    Deinitialize the passed **beartype call metadata** (i.e., object
    encapsulating *all* metadata for the passed user-defined callable, typically
    currently being decorated by the :func:`beartype.beartype` decorator).

    Parameters
    ----------
    decor_meta : BeartypeDecorMeta
        Beartype call metadata to be deinitialized.
    '''

    # Deinitialize this beartype call metadata.
    decor_meta.deinit()

    # Release this beartype call metadata back to its object pool.
    release_instance(decor_meta)
