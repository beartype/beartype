#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype **stringified type hint utilities** (i.e., low-level callables handling
**stringified type hints** (i.e., declared as :pep:`484`- or
:pep:`563`-compliant forward references referring to actual type hints that have
yet to be declared in the local and global scopes declaring a callable or
class)).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.roar import BeartypeDecorHintForwardRefException
from beartype._check.forward.reference.fwdrefmake import (
    make_forwardref_subbable_subtype)
from beartype._check.forward.scope.fwdscopecls import BeartypeForwardScope
from beartype._check.forward.scope.fwdscopemake import (
    make_scope_forward_decor_meta)
from beartype._check.metadata.call.callmetadecormin import (
    BeartypeCallDecorMinimalMeta)
from beartype._conf.confmain import BeartypeConf
from beartype._data.typing.datatyping import TypeException
from beartype._data.typing.datatypingport import Hint
from beartype._util.func.utilfunctest import is_func_nested
from beartype._util.module.utilmodget import get_object_module_name_or_none
from beartype._util.text.utiltextansi import color_hint
from beartype._util.text.utiltextlabel import label_callable
from beartype._util.utilobject import (
    get_object_basename_scoped,
    get_object_name,
)
from traceback import format_exc

# ....................{ RESOLVERS                          }....................
#FIXME: Unit test us up, please.
def resolve_hint_pep484_ref_str(
    # Mandatory parameters.
    hint: str,
    conf: BeartypeConf,
    scope_forward: BeartypeForwardScope,

    # Optional parameters.
    exception_cls: TypeException = BeartypeDecorHintForwardRefException,
    exception_prefix: str = '',
) -> Hint:
    '''
    Resolve the passed :pep:`484`-compliant **stringified forward reference type
    hint** (i.e., string referring to an actual type hint that typically has yet
    to be defined in the local or global scopes of a type-checking call) to that
    actual hint relative to those scopes.

    This resolver is intentionally *not* memoized (e.g., by the
    ``@callable_cached`` decorator). Resolving both absolute *and* relative
    forward references assumes contextual context (e.g., the fully-qualified
    name of the object to which relative forward references are relative to)
    that *cannot* be safely and context-freely memoized away.

    Parameters
    ----------
    hint : str
        Stringified forward reference type hint to be resolved.
    conf : BeartypeConf
        **Beartype configuration** (i.e., self-caching dataclass encapsulating
        all flags, options, settings, and other metadata configuring that
        that type-checking call).
    scope_forward : BeartypeForwardScope
        **Forward scope** (i.e., dictionary mapping from the names to values of
        all attributes accessible to the lexical scope of the passed decorated
        callable where this scope comprises both the global scope and all local
        lexical scopes enclosing that type-checking call) of that call.
    exception_cls : Type[Exception], default: BeartypeDecorHintForwardRefException
        Type of exception to be raised in the event of a fatal error. Defaults
        to :exc:`.BeartypeDecorHintForwardRefException`.
    exception_prefix : str, default: ''
        Human-readable substring prefixing raised exception messages. Defaults
        to the empty string.

    Returns
    -------
    Hint
        Non-string type hint to which this reference refers.

    Raises
    ------
    exception_cls
        If attempting to dynamically evaluate this reference against both the
        global and local scopes of the decorated callable raises an exception,
        typically due to this reference being syntactically invalid as Python.
    '''
    assert isinstance(hint, str), (
        f'{repr(hint)} not PEP 484 stringified forward reference type hint.')
    assert isinstance(conf, BeartypeConf), (
        f'{repr(conf)} not beartype configuration.')
    assert isinstance(scope_forward, BeartypeForwardScope), (
        f'{repr(scope_forward)} not forward scope.')

    # Attempt to resolve this stringified type hint into a non-string type hint
    # against both the global and local scopes of the decorated callable.
    try:
        hint_resolved = eval(hint, scope_forward)
        # print(f'Resolved stringified type hint {repr(hint)} to {repr(hint_resolved)}...')
    # If doing so failed for *ANY* reason whatsoever...
    except Exception as exception:
        assert isinstance(exception_cls, type), (
            f'{repr(exception_cls)} not exception class.')
        assert isinstance(exception_prefix, str), (
            f'{repr(exception_prefix)} not string.')

        # Human-readable message to be raised.
        exception_message = (
            f'{exception_prefix}'
            f'PEP 484 stringified forward reference type hint '
            f'{color_hint(text=repr(hint), is_color=conf.is_color)} '
            f'invalid, as attempting to dynamically import '
            f'the target type (hint) referred to by '
            f'this source reference raises:\n'
            f'{format_exc()}'
        )

        # If the beartype configuration associated with the decorated
        # callable enabled debugging, append debug-specific metadata to this
        # message.
        # if True:
        if conf.is_debug:
            exception_message += (
                f'\nComposite global and local scope enclosing this hint:\n\n'
                f'{repr(scope_forward)}'
            )
        # Else, the beartype configuration associated with the decorated
        # callable disabled debugging. In this case, avoid appending
        # debug-specific metadata to this message.

        # Raise a human-readable exception wrapping the typically
        # non-human-readable exception raised above.
        raise exception_cls(exception_message) from exception

    # Return this resolved hint.
    return hint_resolved

# ....................{ RESOLVERS ~ metadata               }....................
#FIXME: Unit test us up, please.
def resolve_hint_pep484_ref_str_caller_external(
    # Mandatory parameters.
    hint: str,
    conf: BeartypeConf,

    # Optional parameters.
    exception_cls: TypeException = BeartypeDecorHintForwardRefException,
    exception_prefix: str = '',
) -> Hint:
    '''
    Resolve the passed :pep:`484`-compliant **stringified forward reference type
    hint** (i.e., string referring to an actual type hint that typically has yet
    to be defined in the local or global scopes of the currently decorated
    callable) to that actual hint relative to the first external lexical scope
    on the call stack originating from any third-party module or package.

    This resolver is intentionally *not* memoized (e.g., by the
    ``@callable_cached`` decorator). Resolving both absolute *and* relative
    forward references assumes contextual context (e.g., the fully-qualified
    name of the object to which relative forward references are relative to)
    that *cannot* be safely and context-freely memoized away.

    Parameters
    ----------
    hint : str
        Stringified forward reference type hint to be resolved.
    conf : BeartypeConf
        **Beartype configuration** (i.e., dataclass encapsulating all flags,
        options, settings, and other metadata configuring this resolution).
    exception_cls : Type[Exception], default: BeartypeDecorHintForwardRefException
        Type of exception to be raised in the event of a fatal error. Defaults
        to :exc:`.BeartypeDecorHintForwardRefException`.
    exception_prefix : str, default: ''
        Human-readable substring prefixing raised exception messages. Defaults
        to the empty string.

    Returns
    -------
    Hint
        Non-string type hint to which this reference refers.

    Raises
    ------
    exception_cls
        If attempting to dynamically evaluate this reference against both the
        global and local scopes of the decorated callable raises an exception,
        typically due to this reference being syntactically invalid as Python.
    '''
    assert isinstance(hint, str), (
        f'{repr(hint)} not PEP 484 stringified forward reference type hint.')
    # print(f'Resolving caller-time stringified type hint {repr(hint)}...')

    # Avoid circular import dependencies.
    from beartype._check.forward.scope.fwdscopemake import (
        make_scope_forward_caller_external)

    # Forward scope relative to the first external scope on the call stack,
    # encapsulating a call to a public beartype callable by an external
    # callable originating from a third-party package or module.
    scope_forward = make_scope_forward_caller_external(
        exception_cls=exception_cls,
        exception_prefix=exception_prefix,
    )

    # Defer to this low-level resolver.
    return resolve_hint_pep484_ref_str(
        hint=hint,
        conf=conf,
        scope_forward=scope_forward,
        exception_cls=exception_cls,
        exception_prefix=exception_prefix,
    )


#FIXME: Unit test us up, please.
def resolve_hint_pep484_ref_str_decor_meta(
    # Mandatory parameters.
    decor_meta: BeartypeCallDecorMinimalMeta,
    hint: str,

    # Optional parameters.
    exception_cls: TypeException = BeartypeDecorHintForwardRefException,
    exception_prefix: str = '',
) -> Hint:
    '''
    Resolve the passed :pep:`484`-compliant **stringified forward reference type
    hint** (i.e., string referring to an actual type hint that typically has yet
    to be defined in the local or global scopes of the currently decorated
    callable) to that actual hint relative to that callable.

    This resolver is intentionally *not* memoized (e.g., by the
    ``@callable_cached`` decorator). Resolving both absolute *and* relative
    forward references assumes contextual context (e.g., the fully-qualified
    name of the object to which relative forward references are relative to)
    that *cannot* be safely and context-freely memoized away.

    Parameters
    ----------
    decor_meta : BeartypeCallDecorMinimalMeta
        **Beartype decorator call minimal metadata** (i.e., dataclass
        encapsulating the minimal metadata required to type-check the currently
        decorated callable at the time that callable is subsequently called).
    hint : str
        Stringified forward reference type hint to be resolved.
    exception_cls : Type[Exception], default: BeartypeDecorHintForwardRefException
        Type of exception to be raised in the event of a fatal error. Defaults
        to :exc:`.BeartypeDecorHintForwardRefException`.
    exception_prefix : str, default: ''
        Human-readable substring prefixing raised exception messages. Defaults
        to the empty string.

    Returns
    -------
    Hint
        Non-string type hint to which this reference refers.

    Raises
    ------
    exception_cls
        If attempting to dynamically evaluate this reference against both the
        global and local scopes of the decorated callable raises an exception,
        typically due to this reference being syntactically invalid as Python.
    '''
    assert isinstance(decor_meta, BeartypeCallDecorMinimalMeta), (
        f'{repr(decor_meta)} not beartype decorator call metadata.')
    assert isinstance(hint, str), (
        f'{repr(hint)} not PEP 484 stringified forward reference type hint.')
    # print(f'Resolving decorator-time stringified type hint {repr(hint)}...')

    # ..................{ LOCALS                             }..................
    # Decorated callable and metadata associated with that callable, localized
    # to improve both readability and negligible efficiency when accessed below.
    func = decor_meta.func
    cls_stack = decor_meta.cls_stack

    # True only if that callable is nested. As a minor efficiency gain, we avoid
    # the slightly expensive call to is_func_nested() by noting that:
    # * If the class stack is non-empty, then this wrappee callable is
    #   necessarily nested in one or more classes.
    # * Else, defer to the is_func_nested() tester.
    func_is_nested = bool(cls_stack) or is_func_nested(func)

    # Fully-qualified name of the module declaring the decorated callable if
    # that callable defines the "__module__" dunder attribute *OR* "None"
    # otherwise (i.e., if that callable fails to define that attribute).
    func_module_name = get_object_module_name_or_none(func)

    # If the decorated callable fails to define the "__module__" dunder
    # attribute, there exists *NO* known module against which to resolve this
    # stringified type hint. Since this implies that this hint *CANNOT* be
    # reliably resolved, raise an exception.
    #
    # Note that this is an uncommon edge case that nonetheless occurs frequently
    # enough to warrant explicit handling by raising a more human-readable
    # exception than would otherwise be raised (e.g., if the lower-level
    # get_object_module_name() getter were called instead above). Notably, the
    # third-party "markdown-exec" package behaved like this -- and possibly
    # still does. See also:
    #     https://github.com/beartype/beartype/issues/381
    if not func_module_name:
        assert isinstance(exception_prefix, str), (
            f'{repr(exception_prefix)} not string.')
        assert isinstance(exception_cls, type), (
            f'{repr(exception_cls)} not exception type.')

        # Fully-qualified name of the currently decorated callable.
        func_name = get_object_name(func)

        # Human-readable label describing that callable.
        func_label = label_callable(func)

        # Raise this exception.
        raise exception_cls(
            f'{exception_prefix}'
            f'PEP 484 forward reference type hint "{repr(hint)}" '
            f'unresolvable, as '
            f'callable "{func_name}.__module__" dunder attribute undefined '
            f'(e.g., as {func_label} defined dynamically in-memory). '
            f'So much bad stuff is happening here all at once that '
            f'@beartype can no longer cope with the explosion in badness.'
        )
    # Else, the decorated callable defines that attribute.

    # ..................{ AMBIGUITY                          }..................
    # If...
    if (
        # That callable is directly decorated by the @beartype decorator (rather
        # than that callable being a method only transitively decorated by the
        # type declaring that method being directly decorated by the @beartype
        # decorator) *AND*...
        cls_stack is None and
        # That callable is nested (i.e., declared in the body of another
        # pure-Python callable or type)...
        func_is_nested
    ):
        # Non-empty frozen set of the unqualified basenames of all parent
        # callables and types lexically containing this nested decorated
        # callable (including this nested decorated callable itself).
        #
        # Note that this set *COULD* be cached across repeated calls to this
        # resolver passed the same decorated callable metadata by simply storing
        # this set as additional metadata. Indeed, we once did exactly that.
        # Although doing so yet again would be trivial, doing so:
        # * Would also increase beartype space consumption by requiring an
        #   additional slot be stored in each "BeartypeCallDecorMinimalMeta"
        #   instance associated with each type-checking wrapper function.
        # * Would be mostly pointless. This set is *ONLY* required for the edge
        #   case in which a forward reference annotates a nested callable
        #   directly decorated by @beartype, which rarely even occurs anymore.
        #   Why? Because if a callable is nested, that callable is probably a
        #   method. That method's high-level class (rather that low-level
        #   method itself) should have been decorated by @beartype. Decorating
        #   methods directly by @beartype is heavily frowned upon.
        func_basenames_scoped = frozenset(
            get_object_basename_scoped(func).rsplit(sep='.'))

        # If this hint is the unqualified basename of a parent callable or type
        # of the decorated callable, this hint is a relative forward reference
        # to a parent callable or type of the decorated callable that is
        # currently being defined but has yet to be defined in full. If PEP 563
        # postponed this type hint under "from __future__ import annotations",
        # this hint *MUST* have been a locally or globally scoped attribute of
        # the decorated callable before being postponed by PEP 563 into a
        # relative forward reference to that attribute: e.g.,
        #     from __future__ import annotations
        #
        #     # If this is a PEP 563-postponed type hint...
        #     class MuhClass:
        #         @beartype
        #         def muh_method(self) -> 'MuhClass': ...
        #
        #     # ...then the original type hints prior to being postponed *MUST*
        #     # have annotated this pre-PEP 563 method signature.
        #     class MuhClass:
        #         @beartype
        #         def muh_method(self) -> MuhClass: ...
        #
        # In this case, avoid attempting to resolve this forward reference. Why?
        # Disambiguity. Although the "MuhClass" class has yet to be defined at
        # the time @beartype decorates the muh_method() method, an attribute of
        # the same name may already have been defined at that time: e.g.,
        #     # While bad form, PEP 563 postpones this valid logic...
        #     MuhClass = "Just kidding! Had you going there, didn't I?"
        #     class MuhClass:
        #         @beartype
        #         def muh_method(self) -> MuhClass: ...
        #
        #     # ...into this relative forward reference.
        #     MuhClass = "Just kidding! Had you going there, didn't I?"
        #     class MuhClass:
        #         @beartype
        #         def muh_method(self) -> 'MuhClass': ...
        #
        # Naively resolving this forward reference would erroneously replace
        # this hint with the previously declared attribute rather than the class
        # currently being declared: e.g.,
        #     # Naive PEP 563 resolution would replace the above by this!
        #     MuhClass = "Just kidding! Had you going there, didn't I?"
        #     class MuhClass:
        #         @beartype
        #         def muh_method(self) -> (
        #             "Just kidding! Had you going there, didn't I?"): ...
        #
        # This isn't just an edge-case disambiguity, though. This situation
        # commonly arises when reloading modules containing @beartype-decorated
        # callables annotated with self-references (e.g., by passing those
        # modules to the standard importlib.reload() function). Why? Because
        # module reloading is ill-defined and mostly broken in Python. Since the
        # importlib.reload() function fails to delete any of the attributes of
        # the module to be reloaded before reloading that module, the parent
        # callable or type referred to by this hint will be briefly defined for
        # the duration of @beartype's decoration of the decorated callable as
        # the prior version of that parent callable or type!
        #
        # Resolving this hint would thus superficially succeed, while actually
        # erroneously replacing this hint with the prior rather than current
        # version of that parent callable or type. @beartype would then wrap
        # the decorated callable with a wrapper expecting the prior rather than
        # current version of that parent callable or type. All subsequent calls
        # to that wrapper would then fail. Since this actually happened, we
        # ensure it never does again.
        #
        # Lastly, note that this edge case *ONLY* supports top-level relative
        # forward references (i.e., syntactically valid Python identifier names
        # subscripting *NO* parent type hints). Child relative forward
        # references will continue to raise exceptions. As resolving PEP
        # 563-postponed type hints effectively reduces to a single "all or
        # nothing" call of the low-level eval() builtin accepting *NO*
        # meaningful configuration, there exists *NO* means of only partially
        # resolving parent type hints while preserving relative forward
        # references subscripting those hints. The solution in those cases is
        # for end users to either:
        # * Decorate classes rather than methods: e.g.,
        #     # Users should replace this method decoration, which will fail at
        #     # runtime...
        #     class MuhClass:
        #         @beartype
        #         def muh_method(self) -> list[MuhClass]: ...
        #
        #     # ...with this class decoration, which will work.
        #     @beartype
        #     class MuhClass:
        #         def muh_method(self) -> list[MuhClass]: ...
        # * Replace implicit with explicit forward references: e.g.,
        #     # Users should replace this implicit forward reference, which will
        #     # fail at runtime...
        #     class MuhClass:
        #         @beartype
        #         def muh_method(self) -> list[MuhClass]: ...
        #
        #     # ...with this explicit forward reference, which will work.
        #     class MuhClass:
        #         @beartype
        #         def muh_method(self) -> list['MuhClass']: ...
        #
        # Indeed, the *ONLY* reasons we support this common edge case are:
        # * This edge case is indeed common.
        # * This edge case is both trivial and efficient to support.
        #
        # tl;dr: Preserve this hint for disambiguity by reducing to a noop.

        #FIXME: This trivial test is *BUGGED.* It *DOES* efficiently detect
        #unqualified basenames of non-nested types (e.g., "Outer", "Inner") but
        #fails to detect partially-qualified basenames of nested types (e.g.,
        #"Outer.Inner"). Resolve this once somebody actually complains. Ugh!
        if hint in func_basenames_scoped:
            # print(f'Proxying nested hint {repr(hint)}...')

            # Beartype-specific forward reference proxy deferring the detection
            # of this type until required by a runtime type-check performed
            # during some subsequent call to the currently decorated callable.
            hint_resolved = make_forwardref_subbable_subtype(
                scope_name=func_module_name, hint_name=hint)

            # Resolve this stringified forward reference to this proxy.
            return hint_resolved
        # Else, this hint is *NOT* the unqualified basename of a parent callable
        # or type of the decorated callable. In this case, this hint *COULD*
        # require dynamic evaluation under the eval() builtin. Why? Because this
        # hint could simply be the stringified basename of a PEP 563-postponed
        # unsubscripted "typing" non-type type hint imported at module scope.
        # While valid as a type hint, this attribute is *NOT* a type. Returning
        # this stringified hint as is would erroneously instruct our code
        # generation algorithm to treat this stringified hint as a relative
        # forward reference to a type. Instead, evaluate this stringified hint
        # into its referent below: e.g.,
        #     from __future__ import annotations
        #     from typing import Hashable
        #
        #     # PEP 563 postpones this into:
        #     #     def muh_func() -> 'Hashable':
        #     def muh_func() -> Hashable:
        #         return 'This is hashable, yo.'
    # Else, either:
    # * "cls_stack is not None". Ergo, that callable is a method only
    #   transitively decorated by the type declaring that method being directly
    #   decorated by the @beartype decorator. In this case, the
    #   make_scope_forward_decor_meta() factory defined below already guarantees
    #   this hint to be locally unambiguous via the following logic:
    #       # Add new locals exposing these types to type hints, overwriting any
    #       # locals of the same names in the higher-level local scope for any
    #       # closure declaring this type if any. These types are currently
    #       # being decorated and thus guaranteed to be the most recent
    #       # declarations of these attributes.
    #       #
    #       # Note that the current type assumes lexical precedence over the
    #       # root type and is thus intentionally added *AFTER* the latter.
    #       func_locals[cls_root.__name__] = cls_root
    #       func_locals[cls_curr.__name__] = cls_curr
    # * "not decor_meta.func_wrappee_is_nested". That callable is *NOT* nested
    #   and *MUST* thus be a global function, implying this hint to already be
    #   globally unambiguous.

    # ..................{ SCOPE                              }..................
    # Decide the forward scope of the decorated callable.
    func_scope_forward = make_scope_forward_decor_meta(
        decor_meta=decor_meta,
        func_is_nested=func_is_nested,
        exception_cls=exception_cls,
        exception_prefix=exception_prefix,
    )
    # print(f'Resolving {repr(decor_meta)} string hint {repr(hint)} to forward reference proxy...')
    # print(f'Resolving string hint {repr(hint)} against {repr(decor_metafunc_wrappee_wrappee_scope_forward)}...')

    # ..................{ RESOLVE                            }..................
    # Non-string type hint resolved from this stringified type hint. against
    # both the global and local scopes of the decorated callable.
    hint_resolved = resolve_hint_pep484_ref_str(
        hint=hint,
        conf=decor_meta.conf,
        scope_forward=func_scope_forward,  # type: ignore[arg-type]
        exception_cls=exception_cls,
        exception_prefix=exception_prefix,
    )

    # Return this resolved hint.
    return hint_resolved
