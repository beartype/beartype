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
from __future__ import annotations
from beartype.roar import (
    BeartypeDecorHintForwardRefException,
    BeartypeDecorHintPep604Exception,
)
from beartype.roar._roarexc import _BeartypeUtilCallableScopeNotFoundException
from beartype.typing import Optional
from beartype._cave._cavefast import FunctionType
from beartype._check.metadata.metadecor import BeartypeDecorMeta
from beartype._check.forward.fwdscope import BeartypeForwardScope
from beartype._data.hint.datahintpep import Hint
from beartype._data.hint.datahinttyping import (
    LexicalScope,
    TypeException,
)
from beartype._data.kind.datakindmap import FROZENDICT_EMPTY
from beartype._data.kind.datakindset import FROZENSET_EMPTY
from beartype._util.cache.pool.utilcachepoolinstance import (
    acquire_instance,
    release_instance,
)
from beartype._util.cls.utilclsget import get_type_locals
from beartype._util.func.utilfuncscope import (
    get_func_globals,
    get_func_locals,
)
from beartype._util.hint.pep.proposal.pep695 import (
    add_func_scope_hint_pep695_parameterizable_typeparams)
from beartype._util.module.utilmodget import get_object_module_name_or_none
from beartype._util.py.utilpyversion import (
    IS_PYTHON_AT_MOST_3_11,
    IS_PYTHON_AT_MOST_3_9,
)
from beartype._util.text.utiltextansi import color_hint
from beartype._util.utilobject import (
    # SENTINEL,
    get_object_name,
)
from builtins import __dict__ as func_builtins  # type: ignore[attr-defined]
from traceback import format_exc

# ....................{ RESOLVERS                          }....................
#FIXME: Unit test us up, please.
def resolve_hint(
    # Mandatory parameters.
    hint: str,
    decor_meta: BeartypeDecorMeta,

    # Optional parameters.
    exception_cls: TypeException = BeartypeDecorHintForwardRefException,
    exception_prefix: str = '',
) -> Hint:
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
    decor_meta : BeartypeDecorMeta
        Decorated callable annotated by this hint.
    exception_cls : Type[Exception], optional
        Type of exception to be raised in the event of a fatal error. Defaults
        to :exc:`.BeartypeDecorHintForwardRefException`.
    exception_prefix : str, optional
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
    BeartypeDecorHintPep604Exception
        If the active Python interpreter is Python <= 3.9 and this stringified
        type hint is a :pep:`604`-compliant new-style union, which requires
        Python >= 3.10.
    '''
    assert isinstance(hint, str), f'{repr(hint)} not stringified type hint.'
    assert isinstance(decor_meta, BeartypeDecorMeta), (
        f'{repr(decor_meta)} not @beartype call.')
    # print(f'Resolving stringified type hint {repr(hint)}...')

    # ..................{ LOCALS                             }..................
    # Decorated callable and metadata associated with that callable, localized
    # to improve both readability and negligible efficiency when accessed below.
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
            frozenset(func.__qualname__.rsplit(sep='.'))
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
    # This isn't just an edge-case disambiguity, however. This situation
    # commonly arises when reloading modules containing @beartype-decorated
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
    if hint in decor_meta.func_wrappee_scope_nested_names:  # type: ignore[operator]
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

    # ..................{ SCOPE                              }..................
    # If the forward scope of the decorated callable has yet to be decided...
    if decor_meta.func_wrappee_scope_forward is None:
        # Fully-qualified name of the module declaring the decorated callable if
        # that callable defines the "__module__" dunder attribute *OR* "None"
        # (i.e., if that callable fails to define that attribute).
        func_module_name = get_object_module_name_or_none(func)  # type: ignore[operator]

        # If the decorated callable fails to define the "__module__" dunder
        # attribute, there exists *NO* known module against which to resolve
        # this stringified type hint. Since this implies that this hint *CANNOT*
        # be reliably resolved, raise an exception.
        #
        # Note that this is an uncommon edge case that nonetheless occurs
        # frequently enough to warrant explicit handling by raising a more
        # human-readable exception than would otherwise be raised (e.g., if the
        # lower-level get_object_module_name() getter were called instead
        # above). Notably, the third-party "markdown-exec" package behaved like
        # this -- and possibly still does. See also:
        #     https://github.com/beartype/beartype/issues/381
        if not func_module_name:
            raise exception_cls(
                f'{exception_prefix}forward reference type hint "{hint}" '
                f'unresolvable, as '
                f'"{get_object_name(func)}.__module__" dunder attribute '
                f'undefined (e.g., due to {repr(func)} being defined only '
                f'dynamically in-memory). '
                f'So much bad stuff is happening here all at once that '
                f'@beartype can no longer cope with the explosion in badness.'
            )
        # Else, the decorated callable defines that attribute.

        # Resolve the forward scope of the decorated callable, which requires
        # the decorated callable to define that attribute.
        _resolve_func_scope_forward(
            decor_meta=decor_meta,
            exception_cls=exception_cls,
            exception_prefix=exception_prefix,
        )
    # Else, this forward scope has already been decided.
    #
    # In either case, this forward scope should now all have been decided.

    # ..................{ RESOLVE                            }..................
    # Return a non-string type hint resolved from this stringified type hint.
    return _resolve_func_scope_forward_hint(
        hint=hint,
        decor_meta=decor_meta,
        exception_cls=exception_cls,
        exception_prefix=exception_prefix,
    )

# ....................{ PRIVATE ~ resolvers                }....................
def _resolve_func_scope_forward(
    decor_meta: BeartypeDecorMeta,
    exception_cls: TypeException,
    exception_prefix: str,
) -> None:
    '''
    Resolve the **forward scope** (i.e., dictionary mapping from the names to
    values of all attributes accessible to the lexical scope of the passed
    decorated callable where this scope comprises both the global scope and all
    local lexical scopes enclosing that callable) for that callable.

    This resolver is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator). Resolving both absolute *and* relative
    forward references assumes contextual context (e.g., the fully-qualified
    name of the object to which relative forward references are relative to)
    that *cannot* be safely and context-freely memoized away.

    Parameters
    ----------
    decor_meta : BeartypeDecorMeta
        Decorated callable to resolve the forward scope of
    exception_cls : Type[Exception]
        Type of exception to be raised in the event of a fatal error.
    exception_prefix : str
        Human-readable substring prefixing raised exception messages.
    '''

    # ..................{ LOCALS                             }..................
    # Decorated callable and metadata associated with that callable, localized
    # to improve both readability and negligible efficiency when accessed below.
    func = decor_meta.func_wrappee_wrappee
    cls_stack = decor_meta.cls_stack

    # ..................{ NESTED                             }..................
    # If the decorated callable is nested (rather than global) and thus
    # *MAY* have a non-empty local nested scope...
    if decor_meta.func_wrappee_is_nested:
        # Attempt to...
        try:
            # Local scope of the decorated callable, localized to improve
            # readability and negligible efficiency when accessed below.
            func_locals = get_func_locals(
                func=func,

                # Ignore all lexical scopes in the fully-qualified name of the
                # decorated callable corresponding to parent classes lexically
                # nesting the current decorated class containing that callable
                # (including that class). Why? Because these classes are *ALL*
                # currently being decorated and thus have yet to be encapsulated
                # by new stack frames on the call stack. If these lexical scopes
                # are *NOT* ignored, this call to get_func_locals() will fail to
                # find the parent lexical scope of the decorated callable and
                # then raise an unexpected exception.
                #
                # Consider, for example, this nested class decoration of a
                # fully-qualified "muh_package.Outer" class:
                #     @beartype
                #     class Outer(object):
                #         class Middle(object):
                #             class Inner(object):
                #                 def muh_method(self) -> str:
                #                     return 'Painful API is painful.'
                #
                # When @beartype finally recurses into decorating the nested
                # muh_package.Outer.Middle.Inner.muh_method() method, this call
                # to get_func_locals() if *NOT* passed this parameter would
                # naively assume that the parent lexical scope of the current
                # muh_method() method on the call stack is named "Inner".
                # Instead, the parent lexical scope of that method on the call
                # stack is named "muh_package" -- the first lexical scope
                # enclosing that method that exists on the call stack. The
                # non-existent "Outer", "Middle", and "Inner" lexical scopes
                # must *ALL* be silently ignored.
                func_scope_names_ignore=(
                    0 if cls_stack is None else len(cls_stack)),

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
                # Note that, for safety, we currently avoid ignoring additional
                # frames that we could technically ignore. These include:
                # * The call to the parent
                #   beartype._check.metadata.metadecor.BeartypeDecorMeta.reinit() method.
                # * The call to the parent @beartype.beartype() decorator.
                #
                # Why? Because the @beartype codebase has been sufficiently
                # refactored so as to render any such attempts non-trivial,
                # fragile, and frankly dangerous.
                func_stack_frames_ignore=1,
                exception_cls=exception_cls,
            )
        # If this local scope cannot be found (i.e., if this getter found the
        # lexical scope of the module declaring the decorated callable *BEFORE*
        # that of the parent callable or class declaring that callable), then
        # this resolve_hint() function was called *AFTER* rather than *DURING*
        # the declaration of the decorated callable. This implies that that
        # callable is not, in fact, currently being decorated. Instead, that
        # callable was *NEVER* decorated by @beartype but has instead
        # subsequently been passed to this resolve_hint() function after its
        # initial declaration -- typically due to an external caller passing
        # that callable to our public beartype.peps.resolve_pep563() function.
        #
        # In this case, the call stack frame providing this local scope has
        # (almost certainly) already been deleted and is no longer accessible.
        # We have no recourse but to default to the empty frozen dictionary.
        except _BeartypeUtilCallableScopeNotFoundException:
            func_locals = FROZENDICT_EMPTY

        # If the decorated callable is a method transitively defined by a root
        # decorated class, add a pair of local attributes exposing:
        #
        # * The unqualified basename of the root decorated class. Why? Because
        #   this class may be recursively referenced in postponed type hints and
        #   *MUST* thus be exposed to *ALL* postponed type hints. However, this
        #   class is currently being decorated and thus has yet to be defined in
        #   either:
        #   * If this class is module-scoped, the global attribute dictionary of
        #     that module and thus the "func_globals" dictionary.
        #   * If this class is closure-scoped, the local attribute dictionary of
        #     that closure and thus the "func_locals" dictionary.
        # * The unqualified basename of the current decorated class. Why? For
        #   similar reasons. Since the current decorated class may be lexically
        #   nested in the root decorated class, the current decorated class is
        #   *NOT* already accessible as either a global or local. Exposing the
        #   current decorated class to a stringified
        #   type hint referencing that class thus requires adding a local
        #   attribute exposing that class.
        #
        # Note that:
        # * *ALL* intermediary classes (i.e., excluding the root decorated
        #   class) lexically nesting the current decorated class are irrelevant.
        #   Intermediary classes are neither module-scoped nor closure-scoped
        #   and thus inaccessible as either globals or locals in the nested
        #   lexical scope of the current decorated class: e.g.,
        #     # This raises a parser error and is thus *NOT* fine:
        #     #     NameError: name 'muh_type' is not defined
        #     class Outer(object):
        #         class Middle(object):
        #             muh_type = str
        #
        #             class Inner(object):
        #                 def muh_method(self) -> muh_type:
        #                     return 'Dumpster fires are all I see.'
        # * This implicitly overrides any previously declared locals of the same
        #   name. Although non-ideal, this constitutes syntactically valid
        #   Python and is thus *NOT* worth emitting even a non-fatal warning
        #   over: e.g.,
        #     # This is fine... technically.
        #     from beartype import beartype
        #     def muh_closure() -> None:
        #         MuhClass = 'This is horrible, yet fine.'
        #
        #         @beartype
        #         class MuhClass(object):
        #             def muh_method(self) -> str:
        #                 return 'Look away and cringe, everyone!'
        if cls_stack:
            # Root and current decorated classes.
            cls_root = cls_stack[0]
            cls_curr = cls_stack[-1]

            # If this local scope is the empty frozen dictionary, mutate this
            # local scope into a new mutable dictionary to enable new locals to
            # be added to this scope below.
            if func_locals is FROZENDICT_EMPTY:
                func_locals = {}
            # Else, this local scope is *NOT* the empty frozen dictionary.
            # Presumably, this implies this scope to be a mutable dictionary.

            # Add new locals exposing these classes to type hints, overwriting
            # any locals of the same names in the higher-level local scope for
            # any closure declaring this class if any. These classes are
            # currently being decorated and thus guaranteed to be the most
            # recent declarations of these attributes.
            #
            # Note that the current class assumes lexical precedence over the
            # root class and is thus added *AFTER* the latter.
            func_locals[cls_root.__name__] = cls_root
            func_locals[cls_curr.__name__] = cls_curr

            # Local scope for the class directly defining this method.
            #
            # Note that callables *ONLY* have direct access to attributes
            # declared by the classes directly defining those callables. Ergo,
            # the local scopes for parent classes of this class (including the
            # root decorated class) are irrelevant.
            cls_curr_locals = get_type_locals(
                cls=cls_curr, exception_cls=exception_cls)

            # Forcefully merge this local scope into the current local
            # scope, implicitly overwriting any locals of the same name.
            # Class locals necessarily assume lexical precedence over:
            # * These classes themselves.
            # * Locals defined by higher-level parent classes.
            # * Locals defined by closures defining these classes.
            func_locals.update(cls_curr_locals)
        # Else, the decorated callable is *NOT* a method transitively
        # declared by a root decorated class.
    # Else, the decorated callable is global and thus guaranteed to have an
    # empty local scope. In this case, default to the empty frozen dictionary.
    else:
        func_locals = FROZENDICT_EMPTY

    # ..................{ SCOPE                              }..................
    # Fully-qualified name of the module declaring the decorated callable if
    # that callable defines the "__module__" dunder attribute *OR* "None"
    # (i.e., if that callable fails to define that attribute).
    func_module_name = get_object_module_name_or_none(func)  # type: ignore[operator]

    # Global scope of the decorated callable.
    func_globals = get_func_globals(func=func, exception_cls=exception_cls)

    # Forward scope compositing this global and local scope of the decorated
    # callable as well as dynamically replacing each unresolved attribute of
    # this stringified type hint with a forward reference proxy resolving
    # this attribute on the first attempt to pass this attribute as the
    # second parameter to an isinstance()-based runtime type-check: e.g.,
    #     from beartype import beartype
    #     from beartype.typing import Dict, Generic, TypeVar
    #
    #     T = TypeVar('T')
    #
    #     # @beartype resolves this stringified type hint as follows:
    #     # * The "Dict", "str", and "int" attributes are globals and thus
    #     #   trivially resolved to those objects via the "func_globals"
    #     #   scope decided above.
    #     # * The "MuhGeneric" attribute is neither a global nor local and
    #     #   thus remains unresolved. This forward scope replaces this
    #     #   unresolved attribute with a forward reference proxy.
    #     @beartype
    #     def muh_func(muh_arg: 'Dict[str, MuhGeneric[int]]') -> None: ...
    #
    #     class MuhGeneric(Generic[T]): ...
    #
    # Initialize this forward scope to the set of all builtin attributes
    # (e.g., "str", "Exception"). Although the eval() builtin does, of
    # course, implicitly evaluate this stringified type hint against all
    # builtin attributes, it does so only *AFTER* invoking the
    # BeartypeForwardScope.__missing__() dunder method with each such
    # builtin attribute referenced in this hint. Since handling that
    # eccentricity would be less efficient and trivial than simply
    # initializing this forward scope with all builtin attributes, we prefer
    # the current (admittedly sus af) approach. Do not squint at this.

    #FIXME: [SPEED] Optimize away the repeated access to the
    #"decor_meta.func_wrappee_scope_forward" instance variable above, here,
    #and below with a local variable, please. *sigh*
    decor_meta.func_wrappee_scope_forward = BeartypeForwardScope(
        scope_dict=func_builtins, scope_name=func_module_name)  # type: ignore[arg-type]

    # Composite this global and local scope into this forward scope (in that
    # order), implicitly overwriting first each builtin attribute and then
    # each global attribute previously copied into this forward scope with
    # each global and then local attribute of the same name. Since locals
    # *ALWAYS* assume precedence over globals *ALWAYS* assume precedence
    # over builtins, order of operations is *EXTREMELY* significant here.
    decor_meta.func_wrappee_scope_forward.update(func_globals)
    decor_meta.func_wrappee_scope_forward.update(func_locals)
    # print(f'Forward scope: {decor_meta.func_wrappee_scope_forward}')

    # ..................{ PEP 695                            }..................
    # If the decorated callable resides in one or more PEP 695-compliant type
    # parameter scopes, composite these scopes into this forward scope *AFTER*
    # compositing all local and global attributes into this scope above. Doing
    # so properly overrides these attributes with type parameters of the same
    # name, vaguely replicating the scoping rules established by PEP 695:
    #     https://peps.python.org/pep-0695/#type-parameter-scopes
    _resolve_func_scope_pep695(
        decor_meta=decor_meta, exception_prefix=exception_prefix)


#FIXME: Unit test us up, please.
def _resolve_func_scope_pep695(
    decor_meta: BeartypeDecorMeta, exception_prefix) -> None:
    '''
    Composite all **type parameter scopes** (i.e., lexical scopes induced by
    parametrizing the decorated callable *and* all lexical parent classes of
    that callable with :pep:`695`-compliant implicitly instantiated **type
    parameters** (i.e., :pep:`484`-compliant type variables, pep:`612`-compliant
    parameter specifications, and :pep:`646`-compliant type variable tuples))
    of the decorated callable into the **forward scope** (i.e., dictionary
    mapping from the names to values of all attributes accessible to the lexical
    scope of the passed decorated callable where this scope comprises both the
    global scope and all local lexical scopes enclosing that callable).

    Note that this function implicitly overwrites each global and local
    attribute previously composited into this forward scope with each type
    parameter of the same name, vaguely replicating the scoping rules dictated
    by :pep:`695`.

    Parameters
    ----------
    decor_meta : BeartypeDecorMeta
        Decorated callable to resolve the forward scope of
    exception_prefix : str
        Human-readable substring prefixing raised exception messages.
    '''

    # If the active Python interpreter targets Python <= 3.11, this interpreter
    # fails to support PEP 695. In this case, silently reduce to a noop.
    if IS_PYTHON_AT_MOST_3_11:
        return
    # Else, this interpreter targets Python >= 3.12. In this case, this
    # interpreter supports PEP 695.

    # PEP 695-specific lexical scope. Ideally, we'd simply reuse the existing
    # "decor_meta.func_wrappee_scope_forward" scope rather than instantiate a
    # PEP 695-specific lexical scope. Although both trivial and efficient, such
    # reuse would violate PEP 695. PEP 695 mandates that type-checkers:
    # * Raise errors when PEP 695-compliant type parameters parametrizing parent
    #   classes share the same names as those parametrizing either nested
    #   classes or the decorated callable.
    # * Silently allow PEP 695-compliant type parameters parametrizing either
    #   nested classes or the decorated callable to shadow (i.e., override)
    #   *ALL* other attributes in parent lexical scopes.
    #
    # Ergo, this resolver *MUST* differentiate between type parameters and
    # non-type parameters. The only means of doing so sanely is to isolate type
    # parameters resolved by this function to this unique dictionary. See also:
    #     https://peps.python.org/pep-0695/#type-parameter-scopes
    scope_pep695: LexicalScope = acquire_instance(dict)

    # If one or more parent classes lexically enclose the decorated callable...
    if decor_meta.cls_stack:
        # For each parent class lexically enclosing the decorated callable (in
        # descending order from outermost to innermost class)...
        for cls_parent in decor_meta.cls_stack:
            # Composite all PEP 695-compliant type parameters parametrizing this
            # class into this forward scope. Since this class lexically encloses
            # that callable, this class is guaranteed to be pure-Python and thus
            # support PEP 695-compliant type parametrization.
            add_func_scope_hint_pep695_parameterizable_typeparams(
                func_scope=scope_pep695,
                parameterizable=cls_parent,
                exception_prefix=exception_prefix,
            )
    # Else, *NO* parent classes lexically enclose the decorated callable.

    # Decorated callable, localized for negligible efficiency and readability.
    func = decor_meta.func_wrappee_wrappee

    # If the decorated callable is a pure-Python function, this function
    # supports PEP 695-compliant type parametrization. In this case...
    if isinstance(func, FunctionType):
        # Composite all PEP 695-compliant type parameters parametrizing the
        # decorated callable into this forward scope.
        add_func_scope_hint_pep695_parameterizable_typeparams(
            func_scope=scope_pep695,
            parameterizable=func,
            exception_prefix=exception_prefix,
        )
    # Else, the decorated callable is *NOT* a pure-Python function. In this
    # case, that callable does *NOT* support PEP 695-compliant type
    # parametrization. Silently ignore that callable, whatever it is.

    # Composite all type parameters parametrizing the decorated callable and all
    # lexical parent classes of that callable into this forward scope.
    decor_meta.func_wrappee_scope_forward.update(scope_pep695)  # type: ignore[union-attr]

    # Release this PEP 695-specific lexical scope.
    release_instance(scope_pep695)


def _resolve_func_scope_forward_hint(
    hint: str,
    decor_meta: BeartypeDecorMeta,
    exception_cls: TypeException,
    exception_prefix: str,
) -> Hint:
    '''
    Resolve the passed stringified type hint into a non-string type hint
    against the **forward scope** (i.e., dictionary mapping from the names to
    values of all attributes accessible to the lexical scope of the passed
    decorated callable where this scope comprises both the global scope and all
    local lexical scopes enclosing that callable) of that callable.

    This resolver is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator). Resolving both absolute *and* relative
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

        # Human-readable message to be raised if this message has been defined
        # *OR* "None" otherwise (i.e., if this message has yet to be defined).
        exception_message: Optional[str] = None

        # If the following conditions all hold:
        # * The active Python interpreter targets Python < 3.10 *AND*...
        # * The external module defining this stringified type hint was prefixed
        #   by the "from __future__ import annotations" pragma enabling PEP 563
        #   *AND*...
        # * This hint contains one or more PEP 604-compliant new unions (e.g.,
        #   "int | str")...
        #
        # ...then this interpreter fails to syntactically support this hint at
        # runtime (because only Python >= 3.10 supports PEP 604) but nonetheless
        # superficially appears to do so under PEP 563 by simply stringifying
        # this otherwise unsupported hint into a string. Indeed, PEP 563
        # superficially appears to support a countably infinite set of
        # syntactically and semantically invalid type hints -- including but
        # certainly not limited to PEP 604 under Python < 3.10: e.g.,
        #     from __future__ import annotations  # <-- enable PEP 563
        #     def bad() -> int | str: # <-- invalid under Python < 3.10, but
        #         pass                #     silently ignored by PEP 563
        #     def BAD() -> int ** str:  # <-- invalid under all Python versions,
        #         pass                  #     but silently ignored by PEP 563
        #
        # Clearly, exponentiating one type by another is both syntactically and
        # semantically invalid -- but PEP 563 blindly accepts and stringifies
        # that invalid type hint into the string "int ** str". This is nonsense.
        #
        # This branch detects this discrepancy between PEP 563 and 604 and, when
        # detected, raises a human-readable exception advising the caller with
        # recommendations of how to resolve this. Although we could also simply
        # do nothing, doing nothing results in non-human-readable exceptions
        # resembling the following, which only generates confusion: e.g.,
        #     $ python3.9
        #     >>> int | str
        #     Traceback (most recent call last):
        #       File "<stdin>", line 1, in <module>
        #     TypeError: unsupported operand type(s) for |: 'type' and 'type'
        #
        # Specifically, if...
        if (
            # The active Python interpreter targets Python <= 3.9 *AND*...
            IS_PYTHON_AT_MOST_3_9 and
            # Evaluating this stringified type hint raised a "TypeError"...
            isinstance(exception, TypeError)
        ):
            # If the exception message raised by this "TypeError" is prefixed by
            # a well-known substring implying this exception to have been
            # produced by a discrepancy between PEP 563 and 604...
            if str(exception).startswith(
                'unsupported operand type(s) for |: '):
                # PEP 604-specific exception type, forcefully overriding the
                # passed exception type (for disambiguity).
                exception_cls = BeartypeDecorHintPep604Exception

                # Human-readable message providing various recommendations.
                exception_message = (
                    f'{exception_prefix}stringified PEP 604 type hint '
                    f'{repr(hint)} syntactically invalid under Python < 3.10 '
                    f'(i.e., {repr(exception)}). Consider either:\n'
                    f'* Requiring Python >= 3.10. Abandon Python < 3.10 all '
                    f'ye who code here.\n'
                    f'* Refactoring PEP 604 type hints into '
                    f'equivalent PEP 484 type hints: e.g.,\n'
                    f'    # Instead of this...\n'
                    f'    from __future__ import annotations\n'
                    f'    def bad_func() -> int | str: ...\n'
                    f'\n'
                    f'    # Do this. Ugly, yet it works. Worky >>>> pretty.\n'
                    f'    from typing import Union\n'
                    f'    def bad_func() -> Union[int, str]: ...'
                )
            # Else, this another kind of "TypeError" entirely. In this case,
            # defer to the default message defined below.
        # Else, either the active Python interpreter targets Python >= 3.10 *OR*
        # another type of exception was raised. In either case, defer to the
        # default message defined below.

        # If a human-readable message has yet to be defined, fallback to a
        # default message generically applicable to *ALL* stringified hints.
        if exception_message is None:
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
        # Else, a human-readable message has already been defined.

        # Raise a human-readable exception wrapping the typically
        # non-human-readable exception raised above.
        raise exception_cls(exception_message) from exception

    # Return this resolved hint.
    return hint_resolved
