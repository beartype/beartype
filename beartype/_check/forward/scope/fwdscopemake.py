#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype **forward scope type factories** (i.e., low-level callables creating
and returning dictionary subclasses deferring the resolutions of local and
global scopes of types and callables decorated by the :func:`beartype.beartype`
decorator when dynamically evaluating :pep:`484`-compliant forward references
for those types and callables).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.roar import BeartypeDecorHintForwardRefException
from beartype.roar._roarexc import _BeartypeUtilCallableScopeNotFoundException
from beartype._check.forward.scope.fwdscopecls import BeartypeForwardScope
from beartype._check.metadata.call.callmetadecormin import (
    BeartypeCallDecorMinimalMeta)
from beartype._data.kind.datakindiota import SENTINEL
from beartype._data.kind.datakindmap import FROZENDICT_EMPTY
from beartype._data.typing.datatyping import TypeException
from beartype._data.typing.datatypingport import HintOrSentinel
from beartype._util.cls.utilclsget import get_type_locals
from beartype._util.func.utilfuncframe import (
    find_frame_caller_external,
    get_frame_globals,
    get_frame_locals,
    get_frame_module_name_or_none,
)
from beartype._util.func.utilfuncscope import (
    get_func_globals,
    get_func_locals,
)
from beartype._util.hint.pep.proposal.pep695 import resolve_func_scope_pep695
from beartype._util.module.utilmodget import get_object_module_name_or_none
from beartype._util.text.utiltextlabel import label_callable
from beartype._util.utilobject import get_object_name

# ....................{ FACTORIES ~ caller                 }....................
#FIXME: Unit test us up, please.
def make_scope_forward_caller_external(
    # Optional parameters.
    hint: HintOrSentinel = SENTINEL,
    exception_cls: TypeException = BeartypeDecorHintForwardRefException,
    exception_prefix: str = '',
) -> BeartypeForwardScope:
    '''
    Create and return a new **forward scope** (i.e., dictionary mapping from the
    name to value of each locally and globally accessible attribute in the local
    and global scope of the currently decorated callable as well as deferring
    the resolution of each currently undeclared attribute in that scope by
    replacing that attribute with a forward reference proxy resolved only when
    that attribute is passed as the second parameter to an :func:`isinstance`-
    or :func:`issubclass`-based runtime type-check) relative to the first
    **external lexical scope** on the call stack (i.e., originating from any
    module or package *except* those residing in the :mod:`beartype` package).

    This factory is internally memoized into the
    :attr:`decor_meta.func_wrappee_scope_forward` instance variable of the
    passed metadata.

    Parameters
    ----------
    hint : HintOrSentinel, default: SENTINEL
        :pep:`484`-compliant forward reference type hint requiring this forward
        scope if any *or* the sentinel placeholder. This factory embeds this
        hint in exception messages for readability. Defaults to the sentinel
        placeholder.
    exception_cls : Type[Exception], default: BeartypeDecorHintForwardRefException
        Type of exception to be raised in the event of a fatal error. Defaults
        to :exc:`.BeartypeDecorHintForwardRefException`.
    exception_prefix : str, default: ''
        Human-readable substring prefixing raised exception messages. Defaults
        to the empty string.

    Returns
    -------
    BeartypeForwardScope
        Forward scope relative to the currently decorated callable.
    '''

    # ....................{ CALLER                         }....................
    # Stack frame encapsulating the external caller.
    caller_frame = find_frame_caller_external(
        # Additionally ignore the current frame on the call stack
        # encapsulating the current call to this factory function.
        ignore_frames=1,
        exception_cls=exception_cls,
        exception_prefix=exception_prefix,
    )

    # Fully-qualified name of the module declaring this external caller if that
    # caller defines the "__module__" dunder attribute *OR* "None" (i.e., if
    # that caller fails to define that attribute).
    caller_module_name = get_frame_module_name_or_none(caller_frame)

    # Global and local scopes directly accessible to this external caller.
    caller_globals = get_frame_globals(caller_frame)
    caller_locals = get_frame_locals(caller_frame)

    # ....................{ SCOPE                          }....................
    # Forward scope compositing this global and local scope of the external
    # caller as well as dynamically replacing each unresolved attribute of
    # each stringified type hint with a forward reference proxy resolving that
    # attribute on the first attempt to pass that attribute as the second
    # parameter to an isinstance()- or issubclass()based runtime type-check.
    caller_scope = BeartypeForwardScope(scope_name=caller_module_name)  # type: ignore[arg-type]

    # Composite this global and local scope into this forward scope (in that
    # order), implicitly overwriting first each builtin attribute and then
    # each global attribute previously copied into this forward scope with
    # each global and then local attribute of the same name. Since locals
    # *ALWAYS* assume precedence over globals *ALWAYS* assume precedence
    # over builtins, order of operation is *EXTREMELY* significant here.
    caller_scope.update(caller_globals)
    caller_scope.update(caller_locals)
    # print(f'Forward scope: {decor_meta.func_wrappee_scope_forward}')

    # ....................{ RETURN                         }....................
    # Return this forward scope for orthogonality with the sibling
    # make_scope_forward_caller_external() factory.
    return caller_scope

# ....................{ FACTORIES ~ decorated              }....................
#FIXME: Unit test us up, please.
def make_scope_forward_decor_meta(
    # Mandatory parameters.
    decor_meta: BeartypeCallDecorMinimalMeta,

    # Optional parameters.
    hint: HintOrSentinel = SENTINEL,
    exception_cls: TypeException = BeartypeDecorHintForwardRefException,
    exception_prefix: str = '',
) -> BeartypeForwardScope:
    '''
    Create and return a new **forward scope** (i.e., dictionary mapping from the
    name to value of each locally and globally accessible attribute in the local
    and global scope of the currently decorated callable as well as deferring
    the resolution of each currently undeclared attribute in that scope by
    replacing that attribute with a forward reference proxy resolved only when
    that attribute is passed as the second parameter to an :func:`isinstance`-
    or :func:`issubclass`-based runtime type-check) relative to the currently
    decorated callable described by the passed metadata.

    This factory is internally memoized into the
    :attr:`decor_meta.func_wrappee_scope_forward` instance variable of the
    passed metadata.

    Parameters
    ----------
    decor_meta : BeartypeCallDecorMinimalMeta
        **Beartype decorator call minimal metadata** (i.e., dataclass
        encapsulating the minimal metadata required to type-check the currently
        decorated callable at the time that callable is subsequently called).
    hint : HintOrSentinel, default: SENTINEL
        :pep:`484`-compliant forward reference type hint requiring this forward
        scope if any *or* the sentinel placeholder. This factory embeds this
        hint in exception messages for readability. Defaults to the sentinel
        placeholder.
    exception_cls : Type[Exception], default: BeartypeDecorHintForwardRefException
        Type of exception to be raised in the event of a fatal error. Defaults
        to :exc:`.BeartypeDecorHintForwardRefException`.
    exception_prefix : str, default: ''
        Human-readable substring prefixing raised exception messages. Defaults
        to the empty string.

    Returns
    -------
    BeartypeForwardScope
        Forward scope relative to the currently decorated callable.
    '''
    assert isinstance(decor_meta, BeartypeCallDecorMinimalMeta), (
        f'{repr(decor_meta)} not beartype decorator call metadata.')

    # ....................{ PREAMBLE                       }....................
    # If the forward scope of the decorated callable has already been decided,
    # immediately return this scope as is.
    if decor_meta.func_wrappee_scope_forward is not None:
        return decor_meta.func_wrappee_scope_forward
    # Else, this forward scope has yet to be decided.

    # ....................{ LOCALS                         }....................
    # Decorated callable and metadata associated with that callable, localized
    # to improve both readability and negligible efficiency when accessed below.
    func = decor_meta.func
    cls_stack = decor_meta.cls_stack

    # Global scope of the decorated callable.
    func_globals = get_func_globals(func=func, exception_cls=exception_cls)

    # Fully-qualified name of the module declaring the decorated callable if
    # that callable defines the "__module__" dunder attribute *OR* "None"
    # (i.e., if that callable fails to define that attribute).
    func_module_name = get_object_module_name_or_none(func)

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
        assert isinstance(exception_prefix, str), (
            f'{repr(exception_prefix)} not string.')
        assert isinstance(exception_cls, type), (
            f'{repr(exception_cls)} not exception type.')

        # Fully-qualified name of the currently decorated callable.
        func_name = get_object_name(func)

        # Human-readable label describing that callable.
        func_label = label_callable(func)

        # If the caller passed a PEP 484-compliant forward reference hint,
        # prefix this exception message by this hint for readability.
        if hint is not SENTINEL:
            exception_prefix += (
                f'PEP 484 forward reference type hint "{repr(hint)}" '
                f'unresolvable, as '
            )
        # Else, the caller passed *NO* such hint.

        # Raise this exception.
        raise exception_cls(
            f'{exception_prefix}'
            f'callable "{func_name}.__module__" dunder attribute undefined '
            f'(e.g., as {func_label} defined dynamically in-memory). '
            f'So much bad stuff is happening here all at once that '
            f'@beartype can no longer cope with the explosion in badness.'
        )
    # Else, the decorated callable defines that attribute.

    # ..................{ NESTED                             }..................
    #FIXME: Shift this entire "if: ... else: ..." construct into a new private
    #_get_decor_meta_scope_forward_locals() getter for maintainability, please.
    # If the decorated callable is nested (rather than global) and thus *MAY*
    # have a non-empty local nested scope...
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
                ignore_func_scope_names=(
                    0 if cls_stack is None else len(cls_stack)),

                #FIXME: Consider dynamically calculating exactly how many
                #additional @beartype-specific frames are ignorable on the first
                #call to this function, caching that number, and then reusing
                #that cached number on all subsequent calls to this function.
                #The current approach employed below of naively hard-coding a
                #number of frames to ignore was incredibly fragile and had to be
                #effectively disabled, which hampers runtime efficiency.

                # Additionally ignore the current frame on the call stack
                # encapsulating the current call to this factory function.
                #
                # Note that, for safety, we currently avoid ignoring additional
                # frames that we could technically ignore. These include:
                # * The call to the parent
                #   beartype._check.metadata.call.callmetadecor.BeartypeCallDecorMeta.reinit()
                #   method.
                # * The call to the parent @beartype.beartype() decorator.
                #
                # Why? Because the @beartype codebase has been sufficiently
                # refactored so as to render any such attempts non-trivial,
                # fragile, and frankly dangerous.
                ignore_frames=1,
                exception_cls=exception_cls,
            )
        # If this local scope cannot be found (i.e., if this getter found the
        # lexical scope of the module declaring the decorated callable *BEFORE*
        # that of the parent callable or class declaring that callable), then
        # this factory function was called *AFTER* rather than *DURING* the
        # declaration of the decorated callable. This implies that that callable
        # is not, in fact, currently being decorated. Instead, that callable was
        # *NEVER* decorated by @beartype but has instead subsequently been
        # passed to this function after its initial declaration -- typically due
        # to an external caller passing that callable to our public
        # beartype.peps.resolve_pep563() function.
        #
        # In this case, the call stack frame providing this local scope has
        # (almost certainly) already been deleted and is no longer accessible.
        # We have no recourse but to default to the empty frozen dictionary.
        except _BeartypeUtilCallableScopeNotFoundException:
            func_locals = FROZENDICT_EMPTY

        # If the decorated callable is a method transitively defined by a root
        # decorated class, add a pair of local attributes exposing:
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
            # Root and current decorated types.
            cls_root = cls_stack[0]
            cls_curr = cls_stack[-1]

            # If this local scope is the empty frozen dictionary, mutate this
            # local scope into a new mutable dictionary to enable new locals to
            # be added to this scope below.
            if func_locals is FROZENDICT_EMPTY:
                func_locals = {}
            # Else, this local scope is *NOT* the empty frozen dictionary.
            # Presumably, this implies this scope to be a mutable dictionary.

            # Add new locals exposing these types to type hints, overwriting any
            # locals of the same names in the higher-level local scope for any
            # closure declaring this type if any. These types are currently
            # being decorated and thus guaranteed to be the most recent
            # declarations of these attributes.
            #
            # Note that the current type assumes lexical precedence over the
            # root type and is thus intentionally added *AFTER* the latter.
            func_locals[cls_root.__name__] = cls_root
            func_locals[cls_curr.__name__] = cls_curr

            # Type scope (i.e., lexical scope for the type directly defining
            # this method, providing all class variables directly defined in the
            # body of this type).
            #
            # Note that callables *ONLY* have direct access to attributes
            # declared by the types directly defining those callables. Ergo, the
            # lexical scopes for parent types of this type (including the root
            # decorated type) are *ALL* irrelevant.
            type_locals = get_type_locals(
                cls=cls_curr, exception_cls=exception_cls)

            # Forcefully merge this type scope into the current local scope,
            # implicitly overwriting any locals of the same name. Class
            # variables necessarily assume lexical precedence over:
            # * These types themselves.
            # * Class variables defined by higher-level parent types.
            # * Local variables defined by higher-level parent closures defining
            #   these types.
            func_locals.update(type_locals)
        # Else, the decorated callable is *NOT* a method transitively declared
        # by a root decorated type.
    # Else, the decorated callable is global and thus guaranteed to have an
    # empty local scope. In this case, default to the empty frozen dictionary.
    else:
        func_locals = FROZENDICT_EMPTY

    # ..................{ SCOPE                              }..................
    # Forward scope compositing this global and local scope of the decorated
    # callable as well as dynamically replacing each unresolved attribute of
    # each stringified type hint with a forward reference proxy resolving that
    # attribute on the first attempt to pass that attribute as the second
    # parameter to an isinstance()- or issubclass()based runtime type-check:
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
    func_scope = decor_meta.func_wrappee_scope_forward = BeartypeForwardScope(
        scope_name=func_module_name)  # type: ignore[arg-type]

    # Composite this global and local scope into this forward scope (in that
    # order), implicitly overwriting first each builtin attribute and then
    # each global attribute previously copied into this forward scope with
    # each global and then local attribute of the same name. Since locals
    # *ALWAYS* assume precedence over globals *ALWAYS* assume precedence
    # over builtins, order of operation is *EXTREMELY* significant here.
    func_scope.update(func_globals)
    func_scope.update(func_locals)
    # print(f'Forward scope: {decor_meta.func_wrappee_scope_forward}')

    # ..................{ PEP 695                            }..................
    # If the decorated callable resides in one or more PEP 695-compliant type
    # parameter scopes, composite these scopes into this forward scope *AFTER*
    # compositing all local and global attributes into this scope above. Doing
    # so properly overrides these attributes with type parameters of the same
    # name, vaguely replicating the scoping rules established by PEP 695:
    #     https://peps.python.org/pep-0695/#type-parameter-scopes
    resolve_func_scope_pep695(
        func=func,
        func_scope=func_scope,
        cls_stack=cls_stack,
        exception_prefix=exception_prefix,
    )

    # ....................{ RETURN                         }....................
    # Return this forward scope for orthogonality with the sibling
    # make_scope_forward_caller_external() factory.
    return func_scope
