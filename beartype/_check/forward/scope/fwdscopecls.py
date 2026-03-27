#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype **forward scope type hierarchy** (i.e., dictionary subclasses deferring
the resolutions of local and global scopes of types and callables decorated by
the :func:`beartype.beartype` decorator when dynamically evaluating
:pep:`484`-compliant forward references for those types and callables).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ TODO                               }....................
#FIXME: The BeartypeForwardScope.__init__() "scope_dict: LexicalScope" parameter
#should probably instead be typed as:
#from collections import ChainMap
#...
#    def __init__(self, scope_dict: ChainMap, scope_name: str) -> None:
#
#Why? Because "ChainMap" exists to literally solve this *EXACT* problem.
#Notably, the current approach effectively forces a "BeartypeForwardScope" to
#take a possibly desynchronized "snapshot" of a lexical scope at a certain point
#in time. If either the locals or globals of that scope are subsequently
#modified by an external caller, however, that "BeartypeForwardScope" will then
#be desynchronized from those locals and globals.
#
#A "ChainMap" trivially resolves this. How? Internally, a "ChainMap" only holds
#*REFERENCES* to external locals and globals dictionaries. External updates to
#those external dictionaries are thus *IMMEDIATELY* reflected inside the
#"ChainMap" itself, resolving any desynchronization woes. *facepalm*

# ....................{ IMPORTS                            }....................
from beartype.roar import BeartypeDecorHintForwardRefException
from beartype._cave._cavefast import WeakrefCallableType
from beartype._cave._cavemap import NoneTypeOr
from beartype._check.forward.reference._fwdrefabc import (
    BeartypeForwardRefSubbableABC)
from beartype._check.forward.reference.fwdrefproxy import (
    proxy_hint_pep484_ref_str_subbable)
from beartype._data.py.databuiltins import BUILTIN_NAME_TO_VALUE
from beartype._data.typing.datatyping import (
    FuncLocalParentCodeObjectWeakref,
    LexicalScope,
    SetStrs,
)
from beartype._data.typing.datatypingport import Hint
from beartype._util.func.utilfuncframe import (
    GET_FRAME_CALLER_PARENT_PARENT,
    get_frame_or_none,
    get_frame_module_name_or_none,
    is_frame_beartype,
    is_frame_eval,
    # iter_frames,
)
from beartype._util.kind.maplike.utilmapset import (
    remove_mapping_keys_except)
from beartype._util.text.utiltextidentifier import die_unless_identifier
from typing import (
    TYPE_CHECKING,
    Optional,
)

# ....................{ SUPERCLASSES                       }....................
class BeartypeForwardScope(LexicalScope):
    '''
    **Forward scope** (i.e., dictionary mapping from the name to value of each
    locally and globally accessible attribute in the local and global scope of a
    type or callable as well as deferring the resolution of each currently
    undeclared attribute in that scope by replacing that attribute with a
    forward reference proxy resolved only when that attribute is passed as the
    second parameter to an :func:`isinstance`- or :func:`issubclass`-based
    runtime type-check).

    This dictionary is principally employed to dynamically evaluate stringified
    type hints, including:

    * :pep:`484`-compliant forward reference type hints.
    * :pep:`563`-postponed type hints.

    This dictionary should composite both the local and global scopes (i.e.,
    dictionaries mapping from the name to value of each locally and globally
    accessible attribute in the local and global scope of some class or
    callable) underlying the desired lexical scope. This dictionary should *not*
    provide only the local or global scope; this dictionary should provide both.
    Why? Because this forward scope is principally intended to be passed as the
    second and last parameter to the :func:`eval` builtin, called by the
    :func:`beartype._check.forward.fwdresolve.resolve_hint_pep484_ref_str_decor_meta`
    function. For unknown reasons, :func:`eval` only calls the
    :meth:`__missing__` dunder method of this forward scope when passed only two
    parameters (i.e., when passed only a global scope); :func:`eval` does *not*
    call the :meth:`__missing__` dunder method of this forward scope when passed
    three parameters (i.e., when passed both a global and local scope).
    Presumably, this edge case pertains to the official :func:`eval` docstring
    -- which reads:

        The globals must be a dictionary and locals can be any mapping,
        defaulting to the current globals and locals.
        If only globals is given, locals defaults to it.

    Clearly, :func:`eval` treats globals and locals fundamentally differently
    (probably for efficiency or obscure C implementation details). Since
    :func:`eval` only supports a single unified globals dictionary for our use
    case, the caller *must* composite together the global and local scopes into
    this dictionary. Praise to Guido.

    Attributes
    ----------
    _exception_prefix : str
        Human-readable substring prefixing raised exception messages.
    _func_local_parent_codeobj_weakref : FuncLocalParentCodeObjectWeakref
        Proxy weakly referring to the code object underlying the lexical
        scope of the parent module, type, or callable whose body locally
        defines the locally decorated callable if this forward reference
        proxy subtype proxies a stringified forward reference annotating a
        locally decorated callable *or* :data:`None` otherwise. See also the
        :attr:`beartype._check.forward.reference._fwdrefabc.BeartypeForwardRefABC.__func_local_parent_codeobj_weakref_beartype__`
        class variable docstring for further details.
    _hint_names_destringified : set[str]
        Set of the relative (i.e., unqualified) or absolute (i.e.,
        fully-qualified) names of *all* :pep:`484`-compliant stringified type
        hints implicitly destringified into non-string type hints by external
        access of those hints as keys of this forward scope (e.g.,
        ``scope_forward['MuhUndefinedType]``). The :func:`eval` call in the
        :func:`beartype._check.forward.fwdresolve.resolve_hint_pep484_ref_str`
        function is typically responsible for this destringification. The
        :meth:`minify method subsequently truncates this forward scope to this
        minimal subset of key-value pairs required to resolve the
        specific stringified type hints annotating the decorated callable.
    _scope_name : Optional[str]
        Possibly undefined fully-qualified name of this forward scope. See the
        :meth:`__init__` method for details.
    '''

    # ..................{ CLASS VARIABLES                    }..................
    # Slot all instance variables defined on this object to minimize the time
    # complexity of both reading and writing variables across frequently
    # called @beartype decorations. Slotting has been shown to reduce read and
    # write costs by approximately ~10%, which is non-trivial.
    __slots__ = (
        '_exception_prefix',
        '_func_local_parent_codeobj_weakref',
        '_hint_names_destringified',
        '_scope_name',
    )

    # Squelch false negatives from mypy. This is absurd. This is mypy. See:
    #     https://github.com/python/mypy/issues/5941
    if TYPE_CHECKING:
        _exception_prefix: str
        _func_local_parent_codeobj_weakref: FuncLocalParentCodeObjectWeakref
        _hint_names_destringified: SetStrs
        _scope_name: Optional[str]

    # ..................{ INITIALIZERS                       }..................
    def __init__(
        self,

        # Mandatory parameters.
        scope_name: Optional[str],
        exception_prefix: str,

        # Optional parameters.
        func_local_parent_codeobj_weakref: FuncLocalParentCodeObjectWeakref = (
            None),
        is_beartype_test_beartype: bool = False,
        scope_dict: LexicalScope = BUILTIN_NAME_TO_VALUE,
    ) -> None:
        '''
        Initialize this forward scope to the immutable dictionary of all
        **builtin attributes** (e.g., :class:`str`, :class:`Exception`) by
        default.

        As detailed in the class docstring, callers typically use this forward
        scope to resolve a :pep:`484`-compliant stringified type hint by passing
        that hint and this scope as a single unified globals dictionary to the
        :func:`eval` builtin. In that context, :func:`eval` *does* implicitly
        evaluate that hint against all builtin attributes, but only *after*
        invoking the :meth:`__missing__` dunder method with each such builtin
        attribute referenced in this hint. Since handling that eccentricity
        would be less efficient and trivial than simply initializing this
        forward scope with all builtin attributes, we prefer the current
        (admittedly sus af) approach. Do not squint at this.

        Attributes
        ----------
        scope_name : Optional[str]
            Possibly undefined fully-qualified name of this forward scope. For
            example:

            * ``"some_package.some_module"`` for a module scope (e.g., to
              resolve a global class or callable against this scope).
            * ``"some_package.some_module.SomeClass"`` for a class scope (e.g.,
              to resolve a nested class or callable against this scope).
        exception_prefix : str
            Human-readable substring prefixing raised exception messages.
        func_local_parent_codeobj_weakref : FuncLocalParentCodeObjectWeakref, default: None
            Proxy weakly referring to the code object underlying the lexical
            scope of the parent module, type, or callable whose body locally
            defines the locally decorated callable if this forward reference
            proxy subtype proxies a stringified forward reference annotating a
            locally decorated callable *or* :data:`None` otherwise. See also the
            :attr:`beartype._check.forward.reference._fwdrefabc.BeartypeForwardRefABC.__func_local_parent_codeobj_weakref_beartype__`
            class variable for further details.
        scope_dict : LexicalScope, default: scope_builtins
            Initial dictionary from which to populate this forward scope.
            Defaults to the immutable dictionary of all **builtin attributes.**

        Raises
        ------
        BeartypeDecorHintForwardRefException
            If this scope name is *not* a valid Python attribute name.
        '''
        assert isinstance(scope_name, NoneTypeOr[str]), (
            f'{repr(scope_name)} neither string nor "None".')
        assert isinstance(exception_prefix, str), (
            f'{repr(exception_prefix)} not string.')
        assert isinstance(
            func_local_parent_codeobj_weakref,
            NoneTypeOr[WeakrefCallableType]
        ), (
            f'{repr(func_local_parent_codeobj_weakref)} neither weak reference '
            f'nor "None".'
        )
        assert isinstance(scope_dict, dict), (
            f'{repr(scope_dict)} not dictionary.')

        # Initialize our superclass with this lexical scope, efficiently
        # pre-populating this dictionary with all previously declared attributes
        # underlying this forward scope.
        super().__init__(scope_dict)

        # If this scope name is a syntactically invalid Python identifier, raise
        # an exception.
        if scope_name is not None:
            die_unless_identifier(
                text=scope_name,
                exception_cls=BeartypeDecorHintForwardRefException,
                exception_prefix=exception_prefix,
            )
        # Else, this scope name is either "None" *OR* a syntactically valid
        # Python identifier.

        # Classify all passed parameters.
        self._exception_prefix = exception_prefix
        self._func_local_parent_codeobj_weakref = (
            func_local_parent_codeobj_weakref)
        self._scope_name = scope_name

        # Default all remaining parameters to sane initial values.
        self._hint_names_destringified = set()

    # ..................{ DUNDERS                            }..................
    def __getitem__(self, hint_name: str) -> Hint:
        '''
        Dunder method implicitly called on each ``[``- and ``]``-delimited
        attempt to access a with the passed name against this forward scope.

        Parameters
        ----------
        hint_name : str
            Relative (i.e., unqualified) or absolute (i.e., fully-qualified)
            name of this unresolved type hint.

        Returns
        -------
        Hint:
            Either:

            * If this type hint already exists as an attribute in either the
              local or global scope aggregated by this forward scope, that hint.
            * Else, a **forward reference proxy** (i.e.,
              :class:`.BeartypeForwardRefSubbableABC` object) deferring the
              resolution of this unresolved type hint implicitly created and
              returned by the lower-level :meth:`__missing__` dunder method.

        Raises
        ------
        BeartypeDecorHintForwardRefException
            If this type hint name is *not* a valid Python identifier.
        '''

        # Non-string type hint destringified from this stringified forward
        # reference type hint, either explicitly against this dictionary by the
        # default superclass implementation *OR* implicitly as a forward
        # reference proxy by the __missing__() dunder method defined below).
        #
        # Note that doing so raises the expected
        # "BeartypeDecorHintForwardRefException" exception if this forward
        # reference type hint is *NOT* a valid Python identifier.
        hint = super().__getitem__(hint_name)

        # Record this stringified reference as having been destringified.
        self._hint_names_destringified.add(hint_name)

        # Return this non-string type hint
        return hint


    def __missing__(self, hint_name: str) -> (
        type[BeartypeForwardRefSubbableABC]):
        '''
        Dunder method explicitly called by the superclass
        :meth:`dict.__getitem__` method implicitly called on each ``[``- and
        ``]``-delimited attempt to access an **unresolved type hint** (i.e.,
        *not* currently defined in this scope) with the passed name.

        This dunder method transparently replaces this unresolved type hint with
        a **forward reference proxy** (i.e., concrete subclass of the private
        :class:`beartype._check.forward.reference._fwdrefabc.BeartypeForwardRefABC`
        abstract base class (ABC), which resolves this type hint on the first
        call to the :func:`isinstance` builtin whose second argument is that
        subclass).

        This dunder method assumes that:

        * This scope has only been partially initialized.
        * The passed type hint has yet to be declared in this scope.
        * The passed type hint will be declared in this scope by the later time
          that this dunder method is called.

        Caveats
        -------
        **This dunder method is susceptible to misuse by third-party frameworks
        that perform call stack inspection.** The higher-level
        :func:`beartype._check.forward.fwdresolve._resolve_hint_pep484_ref_str`
        function internally invokes this dunder method by calling the
        :func:`eval` builtin, which then adds a new frame to the call stack
        whose ``f_locals`` and ``f_globals`` attributes are this dictionary. If
        some third-party framework introspects the call stack containing this
        new frame, this dictionary's failure to conform to the behavior of a
        lexical scope could induce failure in that third-party framework. Does
        this edge case arise in real-world usage, though? It does.

        Consider :mod:`pytest`, which detects whether each frame on the call
        stack defines the ``pytest``-specific ``__tracebackhide__`` dunder
        attribute:

        .. code-block:: python

           def ishidden(self, excinfo: ExceptionInfo[BaseException] | None) -> bool:
               """Return True if the current frame has a var __tracebackhide__
               resolving to True.

               If __tracebackhide__ is a callable, it gets called with the
               ExceptionInfo instance and can decide whether to hide the traceback.

               Mostly for internal use.
               """
               tbh: bool | Callable[[ExceptionInfo[BaseException] | None], bool] = False
               for maybe_ns_dct in (self.frame.f_locals, self.frame.f_globals):
                   # in normal cases, f_locals and f_globals are dictionaries
                   # however via `exec(...)` / `eval(...)` they can be other types
                   # (even incorrect types!).
                   # as such, we suppress all exceptions while accessing __tracebackhide__
                   try:
                       tbh = maybe_ns_dct["__tracebackhide__"]
                   except Exception:
                       pass
                   else:
                       break
               if tbh and callable(tbh):
                   return tbh(excinfo)

        In obscure edge cases involving :mod:`beartype`, :mod:`pytest`, and
        :pep:`563`, one or both of the ``self.frame.f_locals`` and/or
        ``self.frame.f_globals`` dictionaries are instances of the
        :class:`beartype._check.forward.scope.fwdscopecls.BeartypeForwardScope`
        dictionary subclass. The ``tbh = maybe_ns_dct["__tracebackhide__"]``
        statement then implicitly invokes this dunder method, which then creates
        and returns a new forward reference proxy encapsulating the missing
        ``__tracebackhide__`` attribute: e.g.,

        .. code-block:: python

           tbh = <forwardref__tracebackhide__(
                     __hint_name_beartype__='__tracebackhide__',
                     __scope_name_beartype__='beartype_test.a00_unit.data.pep.pep563.pep695.data_pep563_pep695'
           )>

        Since forward reference proxies are types *and* since types are callable
        (in the sense that "calling" a type instantiates that type), forward
        reference proxies are callable. However, they're not. The
        :class:`beartype._check.forward.reference._fwdrefabc.BeartypeForwardRefABC`
        superclass prohibits instantiation by defining a ``__new__()`` dunder
        method that unconditionally raises exceptions, causing :mod:`pytest` to
        raise the same exceptions on attempting to ``return tbh(excinfo)``.

        This dunder method avoids that and all similar issues by:

        * Detecting whether this dunder method is called by a caller defined
          inside or outside the :mod:`beartype` codebase.
        * If this dunder method is called by a caller defined *inside* the
          :mod:`beartype` codebase, creating and returning a forward reference
          proxy.
        * If this dunder method is called by a caller defined *outside* the
          :mod:`beartype` codebase, raising a standard :class:`KeyError`.

        Parameters
        ----------
        hint_name : str
            Relative (i.e., unqualified) or absolute (i.e., fully-qualified)
            name of this unresolved type hint.

        Returns
        -------
        Type[BeartypeForwardRefSubbableABC]
            Forward reference proxy deferring the resolution of this unresolved
            type hint.

        Raises
        ------
        BeartypeDecorHintForwardRefException
            If this type hint name is *not* a valid Python identifier.
        '''
        # print(f'Missing type hint: {repr(hint_name)}')

        # If this type hint name is syntactically invalid, raise an exception.
        die_unless_identifier(
            text=hint_name,
            exception_cls=BeartypeDecorHintForwardRefException,
            exception_prefix=self._exception_prefix,
        )
        # Else, this type hint name is syntactically valid.

        #FIXME: Preserve to debug stack frame madness, which *ALWAYS* happens.
        # func_frames = iter_frames(
        #     ignore_frames=0,
        #     is_ignore_beartype_frames=False,
        #     is_ignore_nonpython_frames=False,
        #     is_ignore_unmoduled_frames=False,
        # )
        # print('[BeartypeForwardScope.__missing__()]:')
        # for func_frame_index, func_frame in enumerate(func_frames):
        #     print(f'func_frame {func_frame_index}: {repr(func_frame)}')
        # print('\n')
        # print(f'is beartype 1? {is_frame_caller_beartype(ignore_frames=1)}')
        # print(f'is beartype 2? {is_frame_caller_beartype(ignore_frames=2)}')

        # Stack frame of the caller directly calling this dunder method if this
        # method is called by a caller *OR* "None" otherwise (e.g., if this
        # method is called from an interactive REPL). Intentionally ignore the
        # call to the parent BeartypeForwardScope.__getitem__() dunder method,
        # which is *GUARANTEED* to be the only parent method of this child
        # method and thus safely ignorable.
        #
        # Note that, with respect to the body of the get_frame_or_none() getter:
        # * The 0-th stack frame is the call to that getter performed here.
        # * The 1-st stack frame is the call to this __missing__() method.
        # * The 2-nd stack frame is the call to the parent __getitem__() method.
        # * The 3-rd stack frame is the scope responsible for calling that
        #   parent __getitem__() method.
        #
        # Ergo, ignoring the first three stack frames on the current call stack
        # by passing "ignore_frames=2" yields the expected parent parent caller.
        frame_caller = get_frame_or_none(
            ignore_frames=GET_FRAME_CALLER_PARENT_PARENT)

        # If either...
        if (
            # *NO* caller directly called this dunder method (in which case this
            # method was probably called from an interactive REPL) *OR*...
            #
            # The caller that directly called this dunder method is neither...
            frame_caller is None or not (
                # A beartype module, type, or callable *NOR*...
                is_frame_beartype(frame_caller) or
                # A call to the eval() or exec() builtin.
                #
                # Note that calls to the eval() or exec() builtin that originate
                # from within the beartype codebase are difficult to distinguish
                # from calls to the eval() or exec() builtin that originate from
                # outside the beartype codebase. Technically, doing is is
                # feasible (e.g., by introspecting the caller of the caller if
                # this caller is a call to the eval() or exec() builtin).
                # Pragmatically, doing so would only needlessly consume scarce
                # space and time for no particularly good reason. Why? Because
                # this common edge cases arises when the parent
                # _resolve_hint_pep484_ref_str() function calls the eval()
                # builtin to dynamically evaluate the passed PEP 484-compliant
                # stringified forward reference type hint: e.g.,
                #     # This is the eval() call triggering this call.
                #     hint_resolved = eval(hint, scope_forward)
                is_frame_eval(frame_caller)
            )
            # Then the caller is a third-party. In this case, assume this
            # erroneous attempt to access a non-existent attribute of this scope
            # to *ACTUALLY* be an Easier to Ask for Permission than Forgiveness
            # (EAFP)-driven attempt to detect whether this forward scope defines
            # this attribute ala the hasattr() builtin. In this case, raise the
            # standard "KeyError" exception expected by callers. See also the
            # "Caveats" subsection of the docstring for commentary.
        ):
            # Exception message to be raised.
            exception_message = (
                f'{self._exception_prefix}'
                f'forward reference scope "{self._scope_name}" '
                f'attribute "{hint_name}" '
            )

            # Fully-qualified name of the module declaring the caller if any
            # *OR* "None" otherwise (e.g., if declared in an interactive REPL).
            frame_caller_module_name = (
                get_frame_module_name_or_none(frame_caller)
                if frame_caller is not None else
                None
            )

            # If the caller has a module, append the fully-qualified name of
            # that module to this exception message to improve debuggability.
            if frame_caller_module_name:
                exception_message += (
                    f'via third-party module "{frame_caller_module_name}" ')
            # Else, the caller has *NO* module.

            # Raise the expected exception.
            raise KeyError(f'{exception_message}not found.')
        # Else, the caller resides inside the "beartype" package and is thus
        # assumed to be trustworthy. Don't let us down, @beartype! Not again!

        # Forward reference proxy to be returned.
        #
        # Note that the decoration-time "exception_prefix" parameter is
        # intentionally *NOT* passed to this proxy factory. Why? Because that
        # parameter is usually memoized *ONLY* during decoration (e.g., as
        # "EXCEPTION_PLACEHOLDER"), which has *NO* relevance to the returned
        # proxy intended to be called *AFTER* decoration at wrapper call-time.
        # Logic elsewhere is expected to subsequently set the corresponding
        # "__exception_prefix_beartype__" class variable on this proxy to a
        # non-memoized string by calling the
        # set_beartype_ref_proxies_exception_prefix() setter.
        forwardref_subtype = proxy_hint_pep484_ref_str_subbable(
            scope_name=self._scope_name,  # type: ignore[arg-type]
            hint_name=hint_name,
            func_local_parent_codeobj_weakref=(
                self._func_local_parent_codeobj_weakref),
        )

        # Cache this proxy, preventing the "dict" superclass from re-calling
        # this __missing__() dunder method on the next attempt to access this.
        self[hint_name] = forwardref_subtype

        # Return this proxy.
        return forwardref_subtype

    # ..................{ OVERRIDES                          }..................
    def clear(self) -> None:
        '''
        Reduce this forward scope to the empty dictionary.
        '''

        # Defer to our superclass.
        super().clear()

        # Clear all subclass-specific instance variables as well.
        self._exception_prefix = ''
        self._func_local_parent_codeobj_weakref = None
        self._hint_names_destringified.clear()

    # ..................{ RESOLVERS                          }..................
    def resolve_pep484_hint_str(self, hint_name: str) -> Hint:
        '''
        Type hint referred to by the passed :pep:`484`-compliant stringified
        forward reference type hint.

        Caveats
        -------
        **Most callers should prefer resolving stringified forward references
        via dictionary lookups on this forward scope.** This method is *only*
        intended to be called from tests as a means of testing the otherwise
        obscured :meth:`__getitem__` and :meth:`__missing__` dunder methods,
        which conditionally modifies their behaviour depending on whether the
        caller resides inside the main :mod:`beartype` codebase or not. Tests
        reside outside :mod:`beartype` and thus have no direct means of testing
        both branches of that conditionality.

        Parameters
        ----------
        hint_name : str
            Relative (i.e., unqualified) or absolute (i.e., fully-qualified)
            name of this unresolved type hint.

        Returns
        -------
        Hint:
            Either:

            * If this type hint already exists as an attribute in either the
              local or global scope aggregated by this forward scope, that hint.
            * Else, a **forward reference proxy** (i.e.,
              :class:`.BeartypeForwardRefSubbableABC` object) deferring the
              resolution of this unresolved type hint implicitly created and
              returned by the lower-level :meth:`__missing__` dunder method.

        Raises
        ------
        BeartypeDecorHintForwardRefException
            If this type hint name is *not* a valid Python identifier.
        '''

        # Trivial one-liner, we invoke thee!
        return self[hint_name]

    # ..................{ MINIFIERS                          }..................
    def minify(self) -> LexicalScope:
        '''
        **Minimal lexical scope** (i.e., dictionary mapping from the name to
        value of each locally and globally accessible attribute in the local and
        global scope of a type or callable such that this dictionary is the
        minimal subset of key-value pairs needed to resolve *only* the specific
        :pep:`484`-compliant stringified forward reference type hints annotating
        the currently decorated callable).

        This minifier creates and returns the minimal dictionary required to
        type-check the callable currently being decorated by the
        :func:`beartype.beartype` decorator at the post-decoration time that
        callable is subsequently called. Since the type-checking code
        dynamically generated by that decorator is guaranteed to access *only*
        the key-value pairs contained in this minimal dictionary, this minimal
        dictionary is the minimal data structure that suffices to satisfy all
        post-decoration requirements for runtime type-checking of stringified
        forward references. This minimal dictionary is much safer than this
        forward scope. Why? Because:

        * Forward scopes are dictionaries aggregating the *entire* global and
          local scope of that decorated callable and thus consume excess space.
        * Moreover, these dictionaries preserve strong references to all
          attributes accessible from that local and global scope and thus
          inhibit garbage collection of those attributes.

        Forward scopes are intrinsically unsafe to indefinitely cache. By
        compare, the minimal dictionary created and returned by this minifier is
        comparatively safer to indefinitely cache.

        Returns
        -------
        LexicalScope
            Minimal dictionary minified from this maximal forward scope.
        '''

        # Minimal dictionary to be returned, initialized to a copy of this
        # maximal dictionary.
        scope_forward_min = self.copy()

        # Preserve *ONLY* the minimal subset of dictionary key-value pairs
        # required to resolve the specific stringified forward references type
        # hints annotating the currently decorated callable.
        remove_mapping_keys_except(
            mapping=scope_forward_min, keys=self._hint_names_destringified)

        # Return this minimal dictionary.
        return scope_forward_min
