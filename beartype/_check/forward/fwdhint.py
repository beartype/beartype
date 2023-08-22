#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
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
from beartype.roar import BeartypePep563Exception
from beartype.roar._roarexc import _BeartypeUtilCallableException
from beartype._check.checkcall import BeartypeCall
from beartype._data.hint.datahinttyping import (
    TypeException,
)
from beartype._data.kind.datakindset import FROZENSET_EMPTY
from beartype._util.func.utilfuncscope import get_func_locals

# ....................{ RESOLVERS                          }....................
#FIXME: Unit test us up, please.
#FIXME: Implement us up, please.
def resolve_hint(
    # Mandatory parameters.
    hint: str,
    bear_call: BeartypeCall,

    # Optional parameters.
    exception_cls: TypeException = _BeartypeUtilCallableException,
    exception_prefix: str = '',
) -> object:
    '''
    Resolve the passed **stringified type hint** (i.e., declared as a
    :pep:`484`- or :pep:`563`-compliant forward reference referring to an actual
    type hint that has yet to be declared in the local and global scopes
    declaring the currently decorated class or callable) to the non-string type
    hint to which this stringified type hint refers.

    This resolver is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator). Resolving both absolute *and* relative
    forward references assumes contextual context (e.g., the fully-qualified
    name of the object to which relative forward references are relative to)
    that *cannot* be safely and context-freely memoized away.

    Parameters
    ----------
    hint : str
        Stringified type hint to be resolved.
    bear_call : BeartypeCall
        Decorated callable annotated by this hint.
    exception_cls : Type[Exception], optional
        Type of exception to be raised in the event of a fatal error. Defaults
        to :class:`._BeartypeUtilCallableException`.
    exception_prefix : str
        Human-readable label prefixing the representation of this object in the
        exception message. Defaults to the empty string.

    Returns
    ----------
    object
        Either:

        * If this possibly PEP-noncompliant hint is coercible, a PEP-compliant
          type hint coerced from this hint.
        * Else, this hint as is unmodified.
    '''
    assert isinstance(hint, str), f'{repr(hint)} not stringified type hint.'
    assert isinstance(bear_call, BeartypeCall), (
        f'{repr(bear_call)} not @beartype call.')

    # ..................{ LOCALS                             }..................
    #FIXME: *SLOW*. Store this in the "bear_call" dataclass to avoid recomputing
    #this across calls, please.

    # Decorated callable, localized for negligible efficiency gains but *MOSTLY*
    # just to improve the readability of this algorithm.
    func = bear_call.func_wrappee_wrappee

    # If the frozen set of the unqualified names of all parent callables
    # lexically containing this possibly nested decorated callable has yet to be
    # decided...
    if bear_call.func_wrappee_scope_nested_names is None:
        # Classify this frozen set as either...
        bear_call.func_wrappee_scope_nested_names = (
            # If the decorated callable is nested, the non-empty frozen set of
            # the unqualified names of all parent callables lexically containing
            # this nested decorated callable (including this nested decorated
            # callable itself);
            frozenset(func.__qualname__.rsplit(sep='.'))
            if bear_call.func_wrappee_is_nested else
            # Else, the decorated callable is a global function. In that case,
            # the empty frozen set.
            FROZENSET_EMPTY
        )
    # Else, this frozen set has already been decided. Preserve this set as is.
    #
    # In either case, this set is now guaranteed to exist.

    # ..................{ RESOLVE                            }..................
    # If this hint is the unqualified name of a parent callable or class of the
    # decorated callable, then this hint is a relative forward reference to a
    # parent callable or class of the decorated callable that is currently being
    # defined but has yet to be defined in full. If PEP 563 postponed this type
    # hint under "from __future__ import annotations", this hint *MUST* have
    # been a locally or globally scoped attribute of the decorated callable
    # before being postponed by PEP 563 into a relative forward reference to
    # that attribute: e.g.,
    #     # If this loop is iterating over a postponed type hint annotating this
    #     # post-PEP 563 method signature...
    #     class MuhClass:
    #         @beartype
    #         def muh_method(self) -> 'MuhClass': ...
    #
    #     # ...then the original type hints prior to being postponed *MUST* have
    #     # annotated this pre-PEP 563 method signature.
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
    # This isn't simply an edge-case disambiguity, however. This exact situation
    # commonly arises whenever reloading modules containing @beartype-decorated
    # callables annotated with self-references (e.g., by passing those modules
    # to the standard importlib.reload() function). Why? Because module
    # reloading is ill-defined and mostly broken under Python. Since the
    # importlib.reload() function fails to delete any of the attributes of the
    # module to be reloaded before reloading that module, the parent callable or
    # class referred to by this hint will be briefly defined for the duration of
    # @beartype's decoration of the decorated callable as the prior version of
    # that parent callable or class!
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
    if hint in bear_call.func_wrappee_scope_nested_names:
        return hint
    # Else, this hint is *NOT* the unqualified name of a parent callable or
    # class of the decorated callable. In this case, resolve this hint.
    #
    # If the local scope of the decorated callable has yet to be decided...
    elif bear_call.func_wrappee_scope_nested_local is None:
        # Attempt to resolve this hint against *ONLY* the global scope defined
        # by the module declaring the decorated callable.
        #
        # Note that this first attempt intentionally does *NOT* attempt to
        # evaluate this hint against both the global and local scope of the
        # decorated callable. Why? Because:
        # * The majority of real-world hints are imported at module scope (e.g.,
        #   "collections.abc", "typing") and thus accessible as globals.
        # * Deciding the local scope of the decorated callable is an O(n**2)
        #   operation for an arbitrarily large integer n. Ergo, that decision
        #   should be deferred as long as feasible to minimize space and time
        #   costs of the @beartype decorator.
        try:
            hint = eval(hint, bear_call.func_wrappee_scope_global)

            # If doing so succeeded, return this resolved hint.
            return hint
        # If doing so failed, it probably did so due to requiring one or more
        # attributes available *ONLY* via the local scope for the decorated
        # callable. In this case...
        except Exception:
            # If the decorated callable is nested (rather than global) and thus
            # possibly has a non-empty local scope...
            if bear_call.func_wrappee_is_nested:
                # Local scope for the decorated callable.
                bear_call.func_wrappee_scope_nested_local = get_func_locals(
                    func=func,

                    # Ignore all lexical scopes in the fully-qualified name of
                    # the decorated callable corresponding to owner classes
                    # lexically nesting the current decorated class containing
                    # that callable (including the current decorated class).
                    # Why? Because these classes are *ALL* currently being
                    # decorated and thus have yet to be encapsulated by new
                    # stack frames on the call stack. If these lexical scopes
                    # are *NOT* ignored, this call to get_func_locals() will
                    # fail to find the parent lexical scope of the decorated
                    # callable and then raise an unexpected exception.
                    #
                    # Consider, for example, this nested class decoration of a
                    # fully-qualified "muh_package.Outer" class:
                    #     from beartype import beartype
                    #
                    #     @beartype
                    #     class Outer(object):
                    #         class Middle(object):
                    #             class Inner(object):
                    #                 def muh_method(self) -> str:
                    #                     return 'Painful API is painful.'
                    #
                    # When @beartype finally recurses into decorating the nested
                    # muh_package.Outer.Middle.Inner.muh_method() method, this
                    # call to get_func_locals() if *NOT* passed this parameter
                    # would naively assume that the parent lexical scope of the
                    # current muh_method() method on the call stack is named
                    # "Inner". Instead, the parent lexical scope of that method
                    # on the call stack is named "muh_package" -- the first
                    # lexical scope enclosing that method that exists on the
                    # call stack. Ergo, the non-existent "Outer", "Middle", and
                    # "Inner" lexical scopes must *ALL* be silently ignored.
                    func_scope_names_ignore=(
                        0
                        if bear_call.cls_stack is None
                        else len(bear_call.cls_stack)
                    ),

                    #FIXME: Consider dynamically calculating exactly how many
                    #additional @beartype-specific frames are ignorable on the
                    #first call to this function, caching that number, and then
                    #reusing that cached number on all subsequent calls to this
                    #function. The current approach employed below of naively
                    #hard-coding a number of frames to ignore was incredibly
                    #fragile and had to be effectively disabled, which hampers
                    #runtime efficiency.

                    # Ignore additional frames on the call stack embodying:
                    # * The current call to this function.
                    #
                    # Note that, for safety, we currently avoid ignoring
                    # additional frames that we could technically ignore. These
                    # include:
                    # * The call to the parent
                    #   beartype._check.checkcall.BeartypeCall.reinit() method.
                    # * The call to the parent @beartype.beartype() decorator.
                    #
                    # Why? Because the @beartype codebase has been sufficiently
                    # refactored so as to render any such attempts non-trivial,
                    # fragile, and frankly dangerous.
                    func_stack_frames_ignore=1,

                    #FIXME: *NON-IDEAL*. Raise a new type of exception specific
                    #to this submodule, please.
                    exception_cls=BeartypePep563Exception,
                )
                #FIXME: Pick up here tomorrow, please.

            # Else, the decorated callable is global and is thus guaranteed to
            # have an empty local scope. In this common case, avoid uselessly
            # and expensively deciding this empty local scope.

    # ..................{ RETURN                             }..................
    # Return this resolved hint.
    return hint
