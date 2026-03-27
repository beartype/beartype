#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype **forward reference factories** (i.e.,  low-level callables creating
and returning forward reference proxy subclasses deferring the resolution of a
stringified type hint referencing an attribute that has yet to be defined and
annotating a class or callable decorated by the :func:`beartype.beartype`
decorator).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.roar import BeartypeDecorHintForwardRefException
from beartype._cave._cavefast import (
    HintPep484749RefObjectType,
    WeakrefCallableType,
)
from beartype._cave._cavemap import NoneTypeOr
from beartype._check.forward.reference._fwdrefabc import (
    BeartypeForwardRefSubbableABC,
    BeartypeForwardRefSubbableABC_BASES,
    BeartypeForwardRefSubbedABC,
    BeartypeForwardRefSubbedABC_BASES,
)
from beartype._check.forward.reference.fwdreftyping import BeartypeForwardRef
from beartype._data.typing.datatyping import (
    FuncLocalParentCodeObjectWeakref,
    LexicalScope,
    TupleTypes,
)
from beartype._util.cls.utilclsmake import make_type
from beartype._util.hint.pep.proposal.pep749.pep484749forwardref import (
    get_hint_pep484749_ref_names)
from beartype._util.text.utiltextidentifier import die_unless_identifier
from typing import Optional

# ....................{ PROXIERS ~ pep : 484               }....................
def proxy_hint_pep484_ref_str_subbable(
    # Mandatory parameters.
    hint_name: str,
    scope_name: str,

    # Optional parameters.
    func_local_parent_codeobj_weakref: FuncLocalParentCodeObjectWeakref = None,
    exception_prefix: Optional[str] = None,
) -> type[BeartypeForwardRefSubbableABC]:
    '''
    Create and return a new **subscripted forward reference proxy** (i.e.,
    concrete subclass of the :class:`.BeartypeForwardRefSubbedABC` abstract
    base class (ABC)) deferring the resolution of the referent target type hint
    with the passed :pep:`484`-compliant stringified module and hint names in a
    permissive manner permitting this hint to be subscripted by any arbitrary
    child type hints).

    This getter is intentionally *not* memoized (e.g., by the
    ``@callable_cached`` decorator). Why? Because callers typically subsequently
    overwrite the ``__exception_prefix_beartype__`` class variable of returned
    proxies with strings contextually depending on the currently decorated
    callable, effectively prohibiting memoization.

    Parameters
    ----------
    scope_name : str
        Possibly ignored fully-qualified name of the lexical scope in which this
        unresolved type hint was originally declared. For example:

        * ``"some_package.some_module"`` for a module scope (e.g., to
          resolve a global class or callable against this scope).
        * ``"some_package.some_module.SomeClass"`` for a class scope (e.g.,
          to resolve a nested class or callable against this scope).
    hint_name : str
        Relative (i.e., unqualified) or absolute (i.e., fully-qualified) name of
        this unresolved type hint to be proxied.
    func_local_parent_codeobj_weakref : FuncLocalParentCodeObjectWeakref, default: None
        Proxy weakly referring to the code object underlying the lexical scope
        of the parent module, type, or callable whose body locally defines the
        locally decorated callable if this forward reference proxy subtype
        proxies a stringified forward reference annotating a locally decorated
        callable *or* :data:`None` otherwise. See also the
        :attr:`beartype._check.forward.reference._fwdrefabc.BeartypeForwardRefABC.__func_local_parent_codeobj_weakref_beartype__`
        class variable docstring for further details.
    exception_prefix : Optional[str], default: None
        Human-readable substring prefixing raised exception messages if any *or*
        :data:`None` otherwise, in which case the returned proxy preserves its
        default non-empty exception prefix.

    Returns
    -------
    type[BeartypeForwardRefSubbableABC]
        Subscriptable forward reference proxy subclass proxying this type hint.

    Raises
    ------
    BeartypeDecorHintForwardRefException
        If either ``hint_name`` or ``scope_name`` are *not* syntactically valid
        ``"."``-delimited Python identifiers.
    '''

    # Create and return a new subscriptable forward reference proxy proxying the
    # passed referent target module and hint names.
    return _proxy_hint_ref(  # type: ignore[return-value]
        type_bases=BeartypeForwardRefSubbableABC_BASES,
        scope_name=scope_name,
        hint_name=hint_name,
        exception_prefix=exception_prefix,
        func_local_parent_codeobj_weakref=func_local_parent_codeobj_weakref,
    )


def proxy_hint_pep484_ref_str_subbed(
    scope_name: str,
    hint_name: str,

    # Note that this (and *ONLY* this) factory intentionally accepts a mandatory
    # "exception_prefix" parameter, whose value derives from the parent proxy's
    # "__exception_prefix_beartype__" class variable -- which is guaranteed to
    # both exist and be a non-empty string.
    func_local_parent_codeobj_weakref: FuncLocalParentCodeObjectWeakref,
    exception_prefix: str,
    args: tuple,
    kwargs: LexicalScope,
) -> type[BeartypeForwardRefSubbedABC]:
    '''
    Create and return a new **subscripted forward reference proxy** (i.e.,
    concrete subclass of the :class:`.BeartypeForwardRefSubbedABC` abstract
    base class (ABC)) deferring the resolution of the referent target type hint
    with the passed :pep:`484`-compliant stringified module and hint names in a
    strict manner prohibiting this hint from being re-subscripted by any further
    child type hints).

    This getter is intentionally *not* memoized (e.g., by the
    ``@callable_cached`` decorator). Why? Because callers typically subsequently
    overwrite the ``__exception_prefix_beartype__`` class variable of returned
    proxies with strings contextually depending on the currently decorated
    callable, effectively prohibiting memoization.

    Parameters
    ----------
    scope_name : str
        Possibly ignored fully-qualified name of the lexical scope in which this
        unresolved type hint was originally declared. See also
        :func:`.proxy_hint_pep484_ref_str_subbable` docstring for further details.
    hint_name : str
        Relative (i.e., unqualified) or absolute (i.e., fully-qualified) name of
        this unresolved type hint to be proxied.
    func_local_parent_codeobj_weakref : FuncLocalParentCodeObjectWeakref
        Proxy weakly referring to the code object underlying the lexical scope
        of the parent module, type, or callable whose body locally defines the
        locally decorated callable if this forward reference proxy subtype
        proxies a stringified forward reference annotating a locally decorated
        callable *or* :data:`None` otherwise. See also the
        :attr:`beartype._check.forward.reference._fwdrefabc.BeartypeForwardRefABC.__func_local_parent_codeobj_weakref_beartype__`
        class variable docstring for further details.
    exception_prefix : str
        Human-readable substring prefixing raised exception messages.
    args : tuple
        Tuple of all positional arguments subscripting this forward reference.
    kwargs: LexicalScope,
        Dictionary of all keyword arguments subscripting this forward reference.

    Returns
    -------
    type[BeartypeForwardRefSubbedABC]
        Subscripted forward reference proxy subclass proxying this type hint.

    Raises
    ------
    BeartypeDecorHintForwardRefException
        If either ``hint_name`` or ``scope_name`` are *not* syntactically valid
        ``"."``-delimited Python identifiers.
    '''
    assert isinstance(args, tuple), f'{repr(args)} not tuple.'
    assert isinstance(kwargs, dict), f'{repr(kwargs)} not dictionary.'

    # Subscripted forward reference proxy to be returned.
    ref_proxy: type[BeartypeForwardRefSubbedABC] = _proxy_hint_ref(  # type: ignore[assignment]
        type_bases=BeartypeForwardRefSubbedABC_BASES,
        scope_name=scope_name,
        hint_name=hint_name,
        func_local_parent_codeobj_weakref=func_local_parent_codeobj_weakref,
        exception_prefix=exception_prefix,
    )

    # Classify passed parameters with this proxy.
    ref_proxy.__args_beartype__ = args  # pyright: ignore
    ref_proxy.__kwargs_beartype__ = kwargs  # pyright: ignore

    # Return this proxy.
    return ref_proxy

# ....................{ PROXIERS ~ pep : 749               }....................
def proxy_hint_pep749_ref_object(
    # Mandatory parameters.
    hint: HintPep484749RefObjectType,

    # Optional parameters.
    exception_prefix: Optional[str] = None,
) -> type[BeartypeForwardRefSubbedABC]:
    '''
    Create and return a new **forward reference proxy** (i.e.,
    concrete subclass of the :class:`.BeartypeForwardRefSubbableABC` abstract
    base class (ABC)) deferring the resolution of the referent target type hint
    encapsulated by the passed **object-oriented forward reference
    type hint** (i.e., :class:`annotationlib.ForwardRef` object encapsulating
    all metadata required to dynamically resolve at runtime a reference to a
    referent target type hint that typically has yet to be defined in the
    current lexical scope).

    This getter is intentionally *not* memoized (e.g., by the
    ``@callable_cached`` decorator). Why? Because callers typically subsequently
    overwrite the ``__exception_prefix_beartype__`` class variable of returned
    proxies with strings contextually depending on the currently decorated
    callable, effectively prohibiting memoization.

    Parameters
    ----------
    hint : HintPep484749RefObjectType
        Object-oriented forward reference type hint to be proxied.
    exception_prefix : Optional[str], default: None
        Human-readable substring prefixing raised exception messages if any *or*
        :data:`None` otherwise, in which case the returned proxy preserves its
        default non-empty exception prefix.

    Returns
    -------
    type[BeartypeForwardRefSubbedABC]
        Unsubscriptable forward reference proxy subclass proxying this hint.
    '''
    assert isinstance(hint, HintPep484749RefObjectType), (
        f'{repr(hint)} not "annotationlib.ForwardRef" object.')

    # Possibly undefined fully-qualified module name and possibly unqualified
    # classname referred to by this forward reference.
    hint_module_name, hint_type_name = get_hint_pep484749_ref_names(hint)

    # Forward reference proxy proxying this PEP 749-compliant object-oriented
    # forward reference type hint (i.e., "annotationlib.ForwardRef" object).
    ref_proxy: type[BeartypeForwardRefSubbedABC] = _proxy_hint_ref(  # type: ignore[assignment]
        #FIXME: The "BeartypeForwardRefSubbedABC" superclass *DEFINITELY* isn't
        #quite right here, but (possibly) suffices for now. We'll take it! \o/
        type_bases=BeartypeForwardRefSubbedABC_BASES,
        scope_name=hint_module_name,
        hint_name=hint_type_name,
        exception_prefix=exception_prefix,
    )

    # Classify passed parameters with this proxy.
    ref_proxy.__hint_pep749_ref_beartype__ = hint

    # Return this proxy.
    return ref_proxy

# ....................{ PRIVATE ~ factories                }....................
def _proxy_hint_ref(
    # Mandatory parameters.
    type_bases: TupleTypes,
    scope_name: Optional[str],
    hint_name: str,

    # Optional parameters.
    func_local_parent_codeobj_weakref: FuncLocalParentCodeObjectWeakref = None,
    exception_prefix: Optional[str] = None,
) -> BeartypeForwardRef:
    '''
    Create and return a new **forward reference subclass** (i.e., concrete
    subclass of the passed abstract base class (ABC) transparently deferring the
    resolution of the type hint with the passed name).

    This getter is intentionally *not* memoized (e.g., by the
    ``@callable_cached`` decorator). Why? Because callers typically subsequently
    overwrite the ``__exception_prefix_beartype__`` class variable of returned
    proxies with strings contextually depending on the currently decorated
    callable, effectively prohibiting memoization.

    Caveats
    -------
    **There is an unresolvable syntactic disambiguity between the following two
    competing use cases:**

    * When ``hint_name`` is an absolute forward reference (e.g.,
      ``"muh_package.muh_submodule.MuhType"``). In this case, the
      ``type_module_name`` local variable internally defined in the body of
      this factory is a valid module name.
    * When ``hint_name`` is a relative forward reference to a nested type (e.g.,
      ``"MuhOuterType.MuhInnerType"``). In this case, ``type_module_name`` is
      non-empty but *not* a valid module name.

      Thankfully, nested types are entirely useless in Python and thus
      *extremely* uncommon in real-world code. The latter use case is thus
      largely ignorable (but still regrettable).

      In theory, these two cases could be disambiguated in the body of this
      factory by calling the :func:`.is_module` tester below like so:

      .. code-block:: python

         if not (
             type_module_name and
             is_module(type_module_name)
         ):

      In practice, doing so would be ill-advised. The whole point of forward
      references is to defer module importation until *after* this early
      decoration time. Importing arbitrary third-party modules at this early
      decoration time would increase the likelihood of real-world issues in
      production code *far* more severe than this syntactic ambiguity.

      Lastly, note that third-party downstream consumers do have options here.
      To avoid this syntactic ambiguity, users intending to create forward
      references to nested types should either prefer unquoted forward
      references under Python >= 3.14 *or* instantiate
      :class:`.typing.ForwardRef` objects passed the ``module`` parameter: e.g.,

      .. code-block:: python

         # Instead of this ambiguous awfulness...
         is_bearable(['ok'], list['MuhInnerType.MuhOuterType'])

         # ...users should do this under Python >= 3.14:
         from typing import ForwardRef
         is_bearable(['ok'], list[MuhInnerType.MuhOuterType])

         # ...or this under Python <= 3.14:
         from typing import ForwardRef
         is_bearable(['ok'], list[ForwardRef(
             'MuhInnerType.MuhOuterType', module=__name__])

    Parameters
    ----------
    type_bases : Tuple[type, ...]
        Tuple of all base classes to be inherited by this forward reference
        subclass. For simplicity, this *must* be a 1-tuple ``(type_base,)``
        where ``type_base`` is a :class:`.BeartypeForwardRefSubbableABC`
        subclass.
    scope_name : Optional[str]
        Possibly ignored fully-qualified name of the lexical scope in which this
        unresolved type hint was originally declared. See also the
        :func:`.proxy_hint_pep484_ref_str_subbable` docstring for further details.
    hint_name : str
        Absolute (i.e., fully-qualified) or relative (i.e., unqualified) name of
        this unresolved type hint to be proxied.
    func_local_parent_codeobj_weakref : FuncLocalParentCodeObjectWeakref, default: None
        Proxy weakly referring to the code object underlying the lexical scope
        of the parent module, type, or callable whose body locally defines the
        locally decorated callable if this forward reference proxy subtype
        proxies a stringified forward reference annotating a locally decorated
        callable *or* :data:`None` otherwise. See also the
        :attr:`beartype._check.forward.reference._fwdrefabc.BeartypeForwardRefABC.__func_local_parent_codeobj_weakref_beartype__`
        class variable docstring for further details. Defaults to :data:`None`.
    exception_prefix : Optional[str], default: None
        Human-readable substring prefixing raised exception messages if any *or*
        :data:`None` otherwise, in which case the returned proxy preserves its
        default non-empty exception prefix.

    Returns
    -------
    BeartypeForwardRef
        Forward reference proxy subclass proxying this type hint.

    Raises
    ------
    BeartypeDecorHintForwardRefException
        If either ``hint_name`` or ``scope_name`` are *not* syntactically valid
        ``"."``-delimited Python identifiers.
    '''

    # ....................{ VALIDATE                       }....................
    assert isinstance(type_bases, tuple), f'{repr(type_bases)} not tuple.'
    assert len(type_bases) == 1, (
        f'{repr(type_bases)} not 1-tuple of one superclass.')
    assert isinstance(scope_name, str), f'{repr(scope_name)} not string.'
    assert isinstance(hint_name, str), f'{repr(hint_name)} not string.'
    assert isinstance(exception_prefix, NoneTypeOr[str]), (
        f'{repr(exception_prefix)} neither string nor "None".')
    assert isinstance(
        func_local_parent_codeobj_weakref, NoneTypeOr[WeakrefCallableType]), (
        f'{repr(func_local_parent_codeobj_weakref)} neither weak reference '
        f'nor "None".'
    )

    # If passed *NO* exception prefix, default this prefix to something sane.
    if not exception_prefix:
        exception_prefix = 'Forward reference '
    # Else, an exception prefix was passed.

    # If this attribute name is *NOT* a syntactically valid Python identifier,
    # raise an exception.
    die_unless_identifier(
        text=hint_name,
        exception_cls=BeartypeDecorHintForwardRefException,
        exception_prefix=exception_prefix,
    )
    # Else, this attribute name is a syntactically valid Python identifier.

    # ....................{ LOCALS                         }....................
    # Possibly empty fully-qualified module name and unqualified basename of the
    # unresolved hint referred to by this forward reference.
    type_module_name, _, type_name = hint_name.rpartition('.')

    # If this module name is empty, fallback to the passed module name if any.
    if not type_module_name:
        type_module_name = scope_name
    # Else, this module name is non-empty.

    # ....................{ PROXY                          }....................
    # Forward reference proxy to be returned.
    ref_proxy: BeartypeForwardRef = make_type(
        type_name=type_name,
        type_module_name=type_module_name,
        type_bases=type_bases,
        exception_cls=BeartypeDecorHintForwardRefException,
        exception_prefix=exception_prefix,
    )

    # Classify all remaining passed parameters with this proxy.
    ref_proxy.__scope_name_beartype__ = scope_name
    ref_proxy.__hint_name_beartype__ = hint_name
    ref_proxy.__exception_prefix_beartype__ = exception_prefix
    ref_proxy.__func_local_parent_codeobj_weakref_beartype__ = (
        func_local_parent_codeobj_weakref)

    # Return this proxy.
    return ref_proxy
