#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2022 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype decorator** :pep:`563` **support.**

This private submodule this submodule implements :pep:`563` (i.e., "Postponed
Evaluation of Annotations") support on behalf of the :func:`beartype.beartype`
decorator.

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                           }....................
import __future__
from beartype.roar import BeartypeDecorHintPep563Exception
from beartype._decor._call import BeartypeCall
from beartype._util.func.utilfuncscope import (
    CallableScope,
    get_func_globals,
    get_func_locals,
    is_func_nested,
)
from beartype._util.text.utiltextident import is_identifier
from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_7
from beartype._util.text.utiltextlabel import prefix_callable_decorated_pith
from sys import modules as sys_modules
from typing import Any, FrozenSet, Optional

# See the "beartype.cave" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ CONSTANTS                         }....................
_FROZEN_SET_EMPTY: FrozenSet[Any] = frozenset()
'''
Empty frozen set, globalized as a mild optimization for the body of the
:func:`resolve_hints_pep563_if_active` resolver.
'''

# ....................{ RESOLVERS                         }....................
def resolve_hints_pep563_if_active(bear_call: BeartypeCall) -> None:
    '''
    Resolve all :pep:`563`-based **postponed annotations** (i.e., strings that
    when dynamically evaluated as Python expressions yield actual annotations)
    on the currently decorated callable to their **referents** (i.e., the
    actual annotations to which those postponed annotations evaluate) if `PEP
    563`_ is active for this callable *or* silently reduce to a noop otherwise
    (i.e., if :pep:`563` is *not* active for this callable).

    :pep:`563` is active for this callable if the active Python interpreter
    targets either:

    * Python >= 3.7 *and* the module declaring this callable explicitly enables
      :pep:`563` support with a leading dunder importation of the form ``from
      __future__ import annotations``.
    * Python >= ?.?.?, where :pep:`563` is unconditionally globally enabled.

    If :pep:`563` is active for this callable, then for each type-hint
    annotating this callable:

    * If that hint is a string and thus postponed, this function:

      #. Dynamically evaluates that string within this callable's globals
         context (i.e., set of all global variables defined by the module
         declaring this callable).
      #. Replaces that hint's string value with the expression produced by this
         dynamic evaluation.

    * Else, this function preserves that hint as is (e.g., due to that hint
      that was previously postponed having already been evaluated by a prior
      decorator).

    Caveats
    ----------
    **This function must be called only directly by the**
    :meth:`beartype._decor._call.BeartypeCall.reinit` **method**, due to
    unavoidably introspecting the current call stack and making fixed
    assumptions about the structure and height of that stack.

    Parameters
    ----------
    bear_call : BeartypeCall
        Decorated callable to be resolved.

    Raises
    ----------
    BeartypeDecorHintPep563Exception
        If evaluating a postponed annotation on this callable raises an
        exception (e.g., due to that annotation referring to local state
        inaccessible in this deferred context).
    '''
    assert bear_call.__class__ is BeartypeCall, (
        f'{repr(bear_call)} not @beartype call.')

    # ..................{ DETECTION                         }..................
    # Localize attributes of this metadata for negligible efficiency gains.
    func = bear_call.func_wrappee

    # If it is *NOT* the case that...
    if not (
        # The active Python interpreter targets Python >= 3.7 *AND*...
        IS_PYTHON_AT_LEAST_3_7 and
        # This callable was declared by on on-disk module *AND*...
        func.__module__ is not None and
        # This callable's module defined an "annotations" attribute to be
        # the "__future__.annotations" object. In this case, that module
        # enabled PEP 563 support with a leading statement resembling:
        #     from __future__ import annotations
        getattr(sys_modules[func.__module__], 'annotations', None) is (
            __future__.annotations)
    ):
    # Then this callable's hints are *NOT* postponed under PEP 563. In this
    # case, silently reduce to a noop.
        return
    # Else, these hints are postponed under PEP 563. In this case, resolve
    # these hints to their referents.

    # ..................{ LOCALS                            }..................
    # Global scope for the decorated callable.
    func_globals = get_func_globals(
        func=func, exception_cls=BeartypeDecorHintPep563Exception)

    # Dictionary mapping from parameter name to postponed hint for each
    # annotated parameter and return value of this callable.
    func_hints_postponed = func.__annotations__

    # Dictionary mapping from parameter name to resolved hint for each
    # annotated parameter and return value of this callable, initialized to a
    # shallow copy of the postponed dictionary.
    #
    # Note that the "func.__annotations__" dictionary *CANNOT* be safely
    # directly assigned to below, as the loop performing that assignment below
    # necessarily iterates over that dictionary. As with most languages, Python
    # containers cannot be safely mutated while being iterated.
    func_hints_resolved = func_hints_postponed.copy()

    # Local scope for the decorated callable. Since calculating this scope is
    # O(n**2) for an arbitrary large integer n, defer doing so until we must
    # (i.e., when that callable's postponed annotations are *NOT* resolvable
    # given only the global scope of that callable).
    func_locals: Optional[CallableScope] = None

    # Non-empty frozen set of the unqualified names of all parent callables
    # lexically containing this nested callable (including this nested
    # callable itself) if this callable is nested *OR* the empty frozen set
    # otherwise (i.e., if this callable is declared at global scope in its
    # submodule).
    func_scope_names = (
        frozenset(func.__qualname__.rsplit(sep='.'))
        if is_func_nested(func) else
        _FROZEN_SET_EMPTY
    )

    # ..................{ RESOLUTION                        }..................
    # For the parameter name (or "return" for the return value) and
    # corresponding annotation of each of this callable's type hints...
    #
    # Note that refactoring this iteration into a dictionary comprehension
    # would be largely infeasible (e.g., due to the need to raise
    # human-readable exceptions on evaluating unevaluatable type hints) as well
    # as largely pointless (e.g., due to dictionary comprehensions being either
    # no faster or even slower than explicit iteration for small dictionary
    # sizes, as "func.__annotations__" usually is).
    for pith_name, pith_hint in func_hints_postponed.items():
        # If...
        if (
            # This hint is a string *AND*...
            isinstance(pith_hint, str) and
            # This string is non-empty...
            pith_hint
        ):
        # Then this hint is a PEP 563-compliant postponed hint. Note that this
        # test could technically yield a false positive in the unlikely edge
        # case that this annotation was previously postponed but has since been
        # replaced in-place with its referent, which is itself a string
        # matching the PEP 563 format without actually being a PEP
        # 563-formatted postponed string. Since there's nothing we can do about
        # that, we choose to just silently pretend everything will be okay.
            # print(f'Resolving postponed hint {repr(pith_hint)}...')

            #FIXME: Since CPython appears to currently be incapable of even
            #defining a deeply nested annotation that would violate this limit,
            #we avoid performing this test for the moment. Nonetheless, it's
            #likely that CPython will permit such annotations to be defined
            #under some *VERY* distant major version. Ergo, we preserve this.
            # If this string internally exceeds the child limit (i.e., maximum
            # number of nested child type hints listed as subscripted arguments
            # of the parent PEP-compliant type hint produced by evaluating this
            # string) permitted by the @beartype decorator, raise an exception.
            #_die_if_hint_repr_exceeds_child_limit(
            #    hint_repr=pith_hint, pith_label=pith_label)

            # If this hint is the unqualified name of one or more parent
            # callables or classes of this callable, then this hint is a
            # relative forward reference to a parent callable or class of this
            # callable that is currently being defined but has yet to be
            # defined in full. By deduction, we can infer this hint *MUST* have
            # been a locally or globally scoped attribute of this callable
            # before being postponed by PEP 563 into a relative forward
            # reference to that attribute: e.g.,
            #     # If this loop is iterating over a postponed type hint
            #     # annotating this post-PEP 563 method signature...
            #     class MuhClass:
            #         @beartype
            #         def muh_method(self) -> 'MuhClass': ...
            #
            #     # ...then the original type hints prior to being postponed
            #     # *MUST* have annotated this pre-PEP 563 method signature.
            #     class MuhClass:
            #         @beartype
            #         def muh_method(self) -> MuhClass: ...
            #
            # In this case, we absolutely *MUST* avoid attempting to resolve
            # this forward reference. Why? Disambiguity. Although the
            # "MuhClass" class has yet to be defined at the time @beartype
            # decorates the muh_method() method, an attribute of the same name
            # may already have been defined at that time: e.g.,
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
            # Naively resolving this forward reference would erroneously
            # replace this hint with the previously declared attribute rather
            # than the class currently being declared: e.g.,
            #     # Naive PEP 563 resolution would replace the above by this!
            #     MuhClass = "Just kidding! Had you going there, didn't I?"
            #     class MuhClass:
            #         @beartype
            #         def muh_method(self) -> (
            #             "Just kidding! Had you going there, didn't I?"): ...
            #
            # This isn't simply an edge-case disambiguity, however. This exact
            # situation commonly arises whenever reloading modules containing
            # @beartype-decorated callables annotated with self-references
            # (e.g., by passing those modules to the standard
            # importlib.reload() function). Why? Because module reloading is
            # ill-defined and mostly broken under Python. Since the
            # importlib.reload() function fails to delete any of the attributes
            # of the module to be reloaded before reloading that module, the
            # parent callable or class referred to by this hint will be briefly
            # defined for the duration of @beartype's decoration of this
            # callable as the prior version of that parent callable or class!
            #
            # Resolving this hint would thus superficially succeed, while
            # actually erroneously replacing this hint with the prior rather
            # than current version of that parent callable or class. @beartype
            # would then wrap the decorated callable with a wrapper expecting
            # the prior rather than current version of that parent callable or
            # class. All subsequent calls to that wrapper would then fail.
            # Since this actually happened, we ensure it never does again.
            #
            # Lastly, note that this edge case *ONLY* supports top-level
            # relative forward references (i.e., syntactically valid Python
            # identifier names subscripting *NO* parent type hints). Child
            # relative forward references will continue to raise exceptions. As
            # resolving PEP 563-postponed type hints effectively reduces to a
            # single "all or nothing" call of the low-level eval() builtin
            # accepting *NO* meaningful configuration, there exists *NO* means
            # of only partially resolving parent type hints while preserving
            # relative forward references subscripting those hints. The
            # solution in those cases is for end users to replace implicit with
            # explicit forward references: e.g.,
            #     # Users should replace this implicit forward reference, which
            #     # will fail at runtime...
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
            # tl;dr: Preserve this hint for disambiguity and skip to the next.
            if pith_hint in func_scope_names:
                continue

            # If the local scope of the decorated callable has yet to be
            # decided...
            if func_locals is None:
                # Attempt to resolve this hint against the global scope defined
                # by the module declaring the decorated callable.
                #
                # Note that this first attempt intentionally does *NOT* attempt
                # to evaluate this postponed hint against both the global and
                # local scope of the decorated callable. Why? Because:
                # * The overwhelming majority of real-world type hints are
                #   imported at module scope (e.g., from "collections.abc" and
                #   "typing") and thus accessible as global attributes.
                # * Deciding the local scope of the decorated callable is an
                #   O(n**2) operation for an arbitrarily large integer n. Ergo,
                #   that decision should be deferred as long as feasible to
                #   minimize space and time costs of the @beartype decorator.
                try:
                    func_hints_resolved[pith_name] = eval(
                        pith_hint, func_globals)

                    # If that succeeded, continue to the next postponed hint.
                    continue
                # If that resolution failed, it probably did so due to
                # requiring one or more attributes available only in the local
                # scope for the decorated callable. In this case...
                except Exception:
                    # Decide the local scope for the decorated callable.
                    func_locals = get_func_locals(
                        func=func,
                        # Ignore additional frames on the call stack embodying:
                        # * The current call to this function.
                        # * The call to the parent
                        #   beartype._decor._call.BeartypeCall.reinit() method.
                        # * The call to the parent @beartype.beartype()
                        #   decorator.
                        func_stack_frames_ignore=3,
                        exception_cls=BeartypeDecorHintPep563Exception,
                    )
            # In either case, the local scope of the decorated callable has now
            # been decided. (Validate this to be the case.)
            assert func_locals is not None, (
                f'{func.__qualname__}() local scope undecided.')

            # Attempt to resolve this hint against both the global and local
            # scopes for the decorated callable.
            try:
                func_hints_resolved[pith_name] = eval(
                    pith_hint, func_globals, func_locals)
            # If that resolution also fails...
            except Exception as exception:
                # If...
                if (
                    # That resolution fails with a "NameError" *AND*...
                    isinstance(exception, NameError) and
                    # This hint is a valid Python identifier...
                    is_identifier(pith_hint)
                ):
                    # This hint is *PROBABLY* a forward reference hinted as a
                    # string. In this case, defer validation of this string as
                    # a valid forward reference to a class (that presumably has
                    # yet to be declared) until call time of the decorated
                    # callable by preserving this string as is.
                    #
                    # Insanely, PEP 563 fails to enable runtime type checkers
                    # to distinguish between forward references hinted as
                    # strings and non-forward references postponed under PEP
                    # 563 as strings. Ideally, PEP 563 would postpone the
                    # former as machine-readable string representations (e.g.,
                    # converting "muh.class.name" to "'muh.class.name'"). It
                    # doesn't. Instead, it simply preserves forward references
                    # hinted as strings! Who approved this appalling
                    # abomination that breaks CPython itself?
                    # print(f'Deferring postponed forward reference hint {repr(pith_hint)}...')
                    continue
                # Else, this hint is *PROBABLY NOT* a forward reference hinted
                # as a string.

                # Human-readable label describing this pith.
                exception_prefix = prefix_callable_decorated_pith(
                    func=func, pith_name=pith_name)

                # Wrap this low-level non-human-readable exception with a
                # high-level human-readable beartype-specific exception.
                raise BeartypeDecorHintPep563Exception(
                    f'{exception_prefix}PEP 563-postponed type hint '
                    f'{repr(pith_hint)} syntactically invalid '
                    f'(i.e., "{str(exception)}") under:\n'
                    f'~~~~[ GLOBAL SCOPE ]~~~~\n{repr(func_globals)}\n'
                    f'~~~~[ LOCAL SCOPE  ]~~~~\n{repr(func_locals)}'
                ) from exception
        # Else, this hint is *NOT* a PEP 563-formatted postponed string. Since
        # PEP 563 is active for this callable, this implies this hint *MUST*
        # have been previously postponed but has since been replaced in-place
        # with its referent -- typically due to this callable being decorated
        # by @beartype and one or more other hint-based decorators.
        #
        # In this case, silently preserve this hint as is. Since PEP 563
        # provides no means of distinguishing expected from unexpected
        # evaluation of postponed hint, either emitting a non-fatal
        # warning *OR* raising a fatal exception here would be overly violent.
        # Instead, we conservatively assume this hint was previously
        # postponed but has already been properly resolved to its referent by
        # external logic elsewhere (e.g., yet another runtime type checker).
        #
        # Did we mention that PEP 563 is a shambolic cesspit of inelegant
        # language design and thus an indictment of Guido himself, who approved
        # this festering mess that:
        #
        # * Critically breaks backward compatibility throughout the
        #   well-established Python 3 ecosystem.
        # * Unhelpfully provides no general-purpose API for either:
        #   * Detecting postponed hints on arbitrary objects.
        #   * Resolving those hints.
        # * Dramatically reduces the efficiency of hint-based decorators
        #   for no particularly good reason.
        # * Non-orthogonally prohibits hints from accessing local state.
        #
        # Because we should probably mention those complaints here.
        # else:
            #FIXME: See above.
            # If the machine-readable representation of this annotation (which
            # internally encapsulates the same structural metadata as the
            # PEP 563-formatted postponed string representation of this
            # annotation) internally exceeds the child limit as tested above,
            # again raise an exception.
            #
            # Note that obtaining the machine-readable representation of this
            # annotation incurs a minor performance penalty. However, since
            # effectively *ALL* annotations will be PEP 563-formatted postponed
            # strings once the next major Python version officially instates
            # PEP 563 as a mandatory backward compatibility-breaking change,
            # this penalty will effectively cease to existence for the
            # overwhelming majority of real-world annotations. *shrug*
            #_die_if_hint_repr_exceeds_child_limit(
            #    hint_repr=repr(pith_hint),
            #    pith_label=pith_label)

    # Assert the above resolution resolved the expected number of type hints.
    assert len(func_hints_resolved) == len(func_hints_postponed), (
        f'{func.__qualname__}() PEP 563-postponed type hint resolution mismatch: '
        f'{len(func_hints_resolved)} resolved hints != '
        f'{len(func_hints_postponed)} postponed hints.')

    # Atomically (i.e., all-at-once) replace this callable's postponed
    # annotations with these resolved annotations for safety and efficiency.
    #
    # While the @beartype decorator goes to great lengths to preserve the
    # originating "__annotations__" dictionary as is, PEP 563 is sufficiently
    # expensive, non-trivial, and general-purpose to implement that generally
    # resolving postponed annotations for downstream third-party callers is
    # justified. Everyone benefits from replacing useless postponed annotations
    # with useful real annotations; so, we do so.
    # print(
    #     f'{func.__name__}() PEP 563-postponed annotations resolved:'
    #     f'\n\t------[ POSTPONED ]------\n\t{func_hints_postponed}'
    #     f'\n\t------[ RESOLVED  ]------\n\t{func_hints_resolved}'
    # )
    func.__annotations__ = func_hints_resolved

# ....................{ PRIVATE ~ resolvers               }....................
#FIXME: We currently no longer require this. See above for further commentary.
# from beartype.roar import BeartypeDecorHintPepException
# from beartype._util.cache.pool.utilcachepoollistfixed import SIZE_BIG
#
# def _die_if_hint_repr_exceeds_child_limit(
#     hint_repr: str, pith_label: str) -> None:
#     '''
#     Raise an exception if the passed machine-readable representation of an
#     arbitrary annotation internally exceeds the **child limit** (i.e., maximum
#     number of nested child type hints listed as subscripted arguments of
#     PEP-compliant type hints) permitted by the :func:`beartype.beartype`
#     decorator.
#
#     The :mod:`beartype` decorator internally traverses over these nested child
#     types of the parent PEP-compliant type hint produced by evaluating this
#     string representation to its referent with a breadth-first search (BFS).
#     For efficiency, this search is iteratively implemented with a cached
#     **fixed list** (i.e.,
#     :class:`beartype._util.cache.pool.utilcachepoollistfixed.FixedList`
#     instance) rather than recursively implemented with traditional recursion.
#     Since the size of this list is sufficiently large to handle all uncommon
#     *and* uncommon edge cases, this list suffices for *all* PEP-compliant type
#     hints of real-world interest.
#
#     Nonetheless, safety demands that we guarantee this by explicitly raising an
#     exception when the internal structure of this string suggests that the
#     resulting PEP-compliant type hint will subsequently violate this limit.
#     This has the convenient side effect of optimizing that BFS, which may now
#     unconditionally insert child hints into arbitrary indices of that cached
#     fixed list without having to explicitly test whether each index exceeds the
#     fixed length of that list.
#
#     Caveats
#     ----------
#     **This function is currently irrelevant.** Why? Because all existing
#     implementations of the :mod:`typing` module are sufficiently
#     space-consumptive that they already implicitly prohibit deep nesting of
#     PEP-compliant type hints. See commentary in the
#     :mod:`beartype_test.a00_unit.data.pep.pep563.data_pep563_poem` submodule for appalling details.
#     Ergo, this validator could technically be disabled. Indeed, if this
#     validator actually incurred any measurable costs, it *would* be disabled.
#     Since it doesn't, this validator has preserved purely for forward
#     compatibility with some future revision of the :mod:`typing` module that
#     hopefully improves that module's horrid space consumption.
#
#     Parameters
#     ----------
#     hint_repr : str
#         Machine-readable representation of this annotation, typically but *not*
#         necessarily as a :pep:`563`-formatted postponed string.
#     pith_label : str
#         Human-readable label describing the callable parameter or return value
#         annotated by this string.
#
#     Raises
#     ----------
#     BeartypeDecorHintPepException
#         If this representation internally exceeds this limit.
#     '''
#     assert isinstance(hint_repr, str), f'{repr(hint_repr)} not string.'
#
#     # Total number of hints transitively encapsulated in this hint (i.e., the
#     # total number of all child hints of this hint as well as this hint
#     # itself), defined as the summation of...
#     hints_num = (
#         # Number of parent PEP-compliant type hints nested in this hint,
#         # including this hint itself *AND*...
#         hint_repr.count('[') +
#         # Number of child type hints (both PEP-compliant type hints and
#         # non-"typing" types) nested in this hint, excluding the last child
#         # hint subscripting each parent PEP-compliant type hint *AND*...
#         hint_repr.count(',') +
#         # Number of last child hints subscripting all parent PEP-compliant type
#         # hints.
#         hint_repr.count(']')
#     )
#
#     # If this number exceeds the fixed length of the cached fixed list with
#     # which the @beartype decorator traverses this hint, raise an exception.
#     if hints_num >= SIZE_BIG:
#         raise BeartypeDecorHintPepException(
#             f'{pith_label} hint representation "{hint_repr}" '
#             f'contains {hints_num} subscripted arguments '
#             f'exceeding maximum limit {SIZE_BIG-1}.'
#         )
