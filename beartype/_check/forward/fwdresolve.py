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
from beartype._check.forward.scope.fwdscopemake import (
    make_decor_meta_scope_forward)
from beartype._check.metadata.metadecor import BeartypeDecorMeta
from beartype._data.typing.datatypingport import Hint
from beartype._data.typing.datatyping import TypeException
from beartype._data.kind.datakindset import FROZENSET_EMPTY
from beartype._util.text.utiltextansi import color_hint
from beartype._util.utilobject import (
    get_object_basename_scoped,
)
from builtins import __dict__ as func_builtins  # type: ignore[attr-defined]
from traceback import format_exc

# ....................{ RESOLVERS                          }....................
#FIXME: Unit test us up, please.
def resolve_hint_pep484_ref_str(
    # Mandatory parameters.
    hint: str,
    decor_meta: BeartypeDecorMeta,

    # Optional parameters.
    exception_cls: TypeException = BeartypeDecorHintForwardRefException,
    exception_prefix: str = '',
) -> Hint:
    '''
    Resolve the passed :pep:`484`-compliant **stringified forward reference**
    (i.e., hint referring to an actual hint that has yet to be declared in the
    local or global scopes declaring the currently decorated type or callable)
    to the non-string hint to which this reference refers.

    This resolver is intentionally *not* memoized (e.g., by the
    ``@callable_cached`` decorator). Resolving both absolute *and* relative
    forward references assumes contextual context (e.g., the fully-qualified
    name of the object to which relative forward references are relative to)
    that *cannot* be safely and context-freely memoized away.

    Parameters
    ----------
    hint : str
        Stringified type hint to be resolved.
    decor_meta : BeartypeDecorMeta
        Decorated callable annotated by this hint.
    exception_cls : Type[Exception], default: BeartypeDecorHintForwardRefException
        Type of exception to be raised in the event of a fatal error. Defaults
        to :exc:`.BeartypeDecorHintForwardRefException`.
    exception_prefix : str, default: ''
        Human-readable substring prefixing raised exception messages. Defaults
        to the empty string.

    Returns
    -------
    Hint
        Non-string type hint resolved from this stringified type hint.

    Raises
    ------
    exception_cls
        If attempting to dynamically evaluate this stringified type hint into a
        non-string type hint against both the global and local scopes of the
        decorated callable raises an exception, typically due to this
        stringified type hint being syntactically invalid.
    '''
    assert isinstance(hint, str), f'{repr(hint)} not stringified type hint.'
    assert isinstance(decor_meta, BeartypeDecorMeta), (
        f'{repr(decor_meta)} not @beartype call.')
    # print(f'Resolving stringified type hint {repr(hint)}...')

    # ..................{ LOCALS                             }..................
    # Currently decorated callable, localized to improve both readability and
    # negligible efficiency when accessed below.
    func = decor_meta.func_wrappee_wrappee

    # If the frozen set of the unqualified names of all parent callables
    # lexically containing this decorated callable has yet to be decided...
    if decor_meta.func_wrappee_scope_nested_names is None:
        # Decide this frozen set as either...
        decor_meta.func_wrappee_scope_nested_names = (
            # If the decorated callable is nested, the non-empty frozen set of
            # the unqualified names of all parent callables lexically containing
            # this nested decorated callable (including this nested decorated
            # callable itself);
            frozenset(get_object_basename_scoped(func).rsplit(sep='.'))
            if decor_meta.func_wrappee_is_nested else
            # Else, the decorated callable is a global function. In this case,
            # the empty frozen set.
            FROZENSET_EMPTY
        )
    # Else, this frozen set has already been decided.
    #
    # In either case, this frozen set is now decided. I choose you!

    # If this hint is the unqualified name of a parent callable or class of the
    # decorated callable, then this hint is a relative forward reference to a
    # parent callable or class of the decorated callable that is currently being
    # defined but has yet to be defined in full. If PEP 563 postponed this type
    # hint under "from __future__ import annotations", this hint *MUST* have
    # been a locally or globally scoped attribute of the decorated callable
    # before being postponed by PEP 563 into a relative forward reference to
    # that attribute: e.g.,
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
    # Disambiguity. Although the "MuhClass" class has yet to be defined at the
    # time @beartype decorates the muh_method() method, an attribute of the same
    # name may already have been defined at that time: e.g.,
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
    # Naively resolving this forward reference would erroneously replace this
    # hint with the previously declared attribute rather than the class
    # currently being declared: e.g.,
    #     # Naive PEP 563 resolution would replace the above by this!
    #     MuhClass = "Just kidding! Had you going there, didn't I?"
    #     class MuhClass:
    #         @beartype
    #         def muh_method(self) -> (
    #             "Just kidding! Had you going there, didn't I?"): ...
    #
    # This isn't just an edge-case disambiguity, though. This situation commonly
    # arises when reloading modules containing @beartype-decorated callables
    # annotated with self-references (e.g., by passing those modules to the
    # standard importlib.reload() function). Why? Because module reloading is
    # ill-defined and mostly broken in Python. Since the importlib.reload()
    # function fails to delete any of the attributes of the module to be
    # reloaded before reloading that module, the parent callable or type
    # referred to by this hint will be briefly defined for the duration of
    # @beartype's decoration of the decorated callable as the prior version of
    # that parent callable or type!
    #
    # Resolving this hint would thus superficially succeed, while actually
    # erroneously replacing this hint with the prior rather than current version
    # of that parent callable or class. @beartype would then wrap the decorated
    # callable with a wrapper expecting the prior rather than current version of
    # that parent callable or class. All subsequent calls to that wrapper would
    # then fail. Since this actually happened, we ensure it never does again.
    #
    # Lastly, note that this edge case *ONLY* supports top-level relative
    # forward references (i.e., syntactically valid Python identifier names
    # subscripting *NO* parent type hints). Child relative forward references
    # will continue to raise exceptions. As resolving PEP 563-postponed type
    # hints effectively reduces to a single "all or nothing" call of the
    # low-level eval() builtin accepting *NO* meaningful configuration, there
    # exists *NO* means of only partially resolving parent type hints while
    # preserving relative forward references subscripting those hints. The
    # solution in those cases is for end users to either:
    #
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
    if hint in decor_meta.func_wrappee_scope_nested_names:  # type: ignore[operator]
        # print(f'Preserving string hint {repr(hint)}...')
        return hint  # pyright: ignore
    # Else, this hint is *NOT* the unqualified name of a parent callable or
    # class of the decorated callable. In this case, this hint *COULD* require
    # dynamic evaluation under the eval() builtin. Why? Because this hint could
    # simply be the stringified name of a PEP 563-postponed unsubscripted
    # "typing" non-class attribute imported at module scope. While valid as a
    # type hint, this attribute is *NOT* a class. Returning this stringified
    # hint as is would erroneously instruct our code generation algorithm to
    # treat this stringified hint as a relative forward reference to a class.
    # Instead, evaluate this stringified hint into its referent below: e.g.,
    #     from __future__ import annotations
    #     from typing import Hashable
    #
    #     # PEP 563 postpones this into:
    #     #     def muh_func() -> 'Hashable':
    #     def muh_func() -> Hashable:
    #         return 'This is hashable, yo.'

    # ..................{ RESOLVE                            }..................
    # Decide the forward scope of the decorated callable.
    make_decor_meta_scope_forward(
        decor_meta=decor_meta,
        exception_cls=exception_cls,
        exception_prefix=exception_prefix,
    )
    # print(f'Resolving {repr(decor_meta)} string hint {repr(hint)} to forward reference proxy...')

    # Return a non-string type hint resolved from this stringified type hint.
    return _resolve_func_scope_forward_hint(
        hint=hint,
        decor_meta=decor_meta,
        exception_cls=exception_cls,
        exception_prefix=exception_prefix,
    )

# ....................{ PRIVATE ~ resolvers                }....................
def _resolve_func_scope_forward_hint(
    hint: str,
    decor_meta: BeartypeDecorMeta,
    exception_cls: TypeException,
    exception_prefix: str,
) -> Hint:
    '''
    Resolve the passed stringified type hint into a non-string type hint against
    the **forward scope** (i.e., dictionary mapping from the names to values of
    all attributes accessible to the lexical scope of the passed decorated
    callable where this scope comprises both the global scope and all local
    lexical scopes enclosing that callable) of that callable.

    This resolver is intentionally *not* memoized (e.g., by the
    ``@callable_cached`` decorator). Resolving both absolute *and* relative
    forward references assumes contextual context (e.g., the fully-qualified
    name of the object to which relative forward references are relative to)
    that *cannot* be safely and context-freely memoized away.

    Parameters
    ----------
    hint : str
        Stringified type hint to be resolved.
    decor_meta : BeartypeDecorMeta
        Decorated callable to resolve the forward scope of
    exception_cls : Type[Exception]
        Type of exception to be raised in the event of a fatal error.
    exception_prefix : str
        Human-readable substring prefixing raised exception messages.

    Returns
    -------
    Hint
        Non-string type hint resolved from this stringified type hint.

    Raises
    ------
    exception_cls
        If attempting to dynamically evaluate this stringified type hint into a
        non-string type hint against both the global and local scopes of the
        decorated callable raises an exception, typically due to this
        stringified type hint being syntactically invalid.
    BeartypeDecorHintPep604Exception
        If the active Python interpreter is Python <= 3.9 and this stringified
        type hint is a :pep:`604`-compliant new-style union, which requires
        Python >= 3.10.
    '''
    # print(f'Resolving string hint {repr(hint)} against {repr(decor_meta.func_wrappee_scope_forward)}...')

    # Attempt to resolve this stringified type hint into a non-string type hint
    # against both the global and local scopes of the decorated callable.
    try:
        hint_resolved = eval(hint, decor_meta.func_wrappee_scope_forward)
        # print(f'Resolved stringified type hint {repr(hint)} to {repr(hint_resolved)}...')
    # If doing so failed for *ANY* reason whatsoever...
    except Exception as exception:
        assert isinstance(exception_cls, type), (
            f'{repr(exception_cls)} not exception class.')
        assert isinstance(exception_prefix, str), (
            f'{repr(exception_prefix)} not string.')

        # Human-readable message to be raised.
        exception_message = (
            f'{exception_prefix}stringified type hint '
            f'{color_hint(text=repr(hint), is_color=decor_meta.conf.is_color)} '
            f'invalid, as attempting to dynamically import '
            f'the attribute referred to by this hint raises:\n'
            f'{format_exc()}'
        )

        # If the beartype configuration associated with the decorated
        # callable enabled debugging, append debug-specific metadata to this
        # message.
        # if True:
        if decor_meta.conf.is_debug:
            exception_message += (
                f'\nComposite global and local scope enclosing this hint:\n\n'
                f'{repr(decor_meta.func_wrappee_scope_forward)}'
            )
        # Else, the beartype configuration associated with the decorated
        # callable disabled debugging. In this case, avoid appending
        # debug-specific metadata to this message.

        # Raise a human-readable exception wrapping the typically
        # non-human-readable exception raised above.
        raise exception_cls(exception_message) from exception

    # Return this resolved hint.
    return hint_resolved
