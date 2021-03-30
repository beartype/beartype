#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2021 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype decorator** `PEP 563`_ **support.**

This private submodule this submodule implements `PEP 563`_ (i.e., "Postponed
Evaluation of Annotations") support on behalf of the :func:`beartype.beartype`
decorator.

This private submodule is *not* intended for importation by downstream callers.

.. _PEP 563:
   https://www.python.org/dev/peps/pep-0563
'''

# ....................{ IMPORTS                           }....................
import __future__
from beartype.roar import BeartypeDecorHintPep563Exception
from beartype._decor._data import BeartypeData
from beartype._util.func.utilfuncscope import (
    get_func_globals,
    get_func_locals,
)
from beartype._util.py.utilpyversion import (
    IS_PYTHON_AT_LEAST_3_10,
    IS_PYTHON_AT_LEAST_3_7,
)
from beartype._util.text.utiltextlabel import label_callable_decorated_pith
from sys import modules as sys_modules

# See the "beartype.cave" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ RESOLVERS                         }....................
def resolve_hints_postponed_if_needed(data: BeartypeData) -> None:
    '''
    Resolve all `PEP 563`_-based **postponed annotations** (i.e., strings that
    when dynamically evaluated as Python expressions yield actual annotations)
    on the currently decorated callable to their **referents** (i.e., the
    actual annotations to which those postponed annotations evaluate) if `PEP
    563`_ is active for this callable *or* silently reduce to a noop otherwise
    (i.e., if `PEP 563`_ is *not* active for this callable).

    `PEP 563`_ is active for this callable if the active Python interpreter
    targets:

    * Python >= 3.10, where `PEP 563`_ is globally, unconditionally enabled.
    * Python >= 3.7 < 3.10 *and* the module declaring this callable explicitly
      enables `PEP 563`_ support with a leading dunder importation of the form
      ``from __future__ import annotations``.

    If `PEP 563`_ is active for this callable, then for each type-hint
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
    :meth:`beartype._decor._data.BeartypeData.reinit` **method**, due to
    unavoidably introspecting the current call stack and making fixed
    assumptions about the structure and height of that stack.

    Parameters
    ----------
    data : BeartypeData
        Decorated callable to be resolved.

    Raises
    ----------
    BeartypeDecorHintPep563Exception
        If evaluating a postponed annotation on this callable raises an
        exception (e.g., due to that annotation referring to local state
        inaccessible in this deferred context).

    .. _PEP 563:
       https://www.python.org/dev/peps/pep-0563
    '''
    assert data.__class__ is BeartypeData, f'{repr(data)} not @beartype data.'

    # Localize attributes of this metadata for negligible efficiency gains.
    func = data.func

    # If neither...
    if not (
        # The active Python interpreter targets Python >= 3.10 *NOR*...
        #
        # If this interpreter targets Python >= 3.10, PEP 563 is
        # unconditionally active. In this case, *ALL* annotations including
        # this callable's annotations are necessarily postponed.
        IS_PYTHON_AT_LEAST_3_10 or
        (
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
        )
    # Then this callable's annotations are *NOT* postponed under PEP 563. In
    # this case, silently reduce to a noop.
    ):
        return
    # Else, this callable's annotations are postponed under PEP 563. In this
    # case, resolve these annotations to their referents.

    # Global scope for this callable.
    func_globals = get_func_globals(
        func=func, exception_cls=BeartypeDecorHintPep563Exception)

    # Dictionary mapping from parameter name to resolved annotation for each
    # annotated parameter and return value of this callable.
    func_hints = {}

    # For the parameter name (or "return" for the return value) and
    # corresponding annotation of each of this callable's type hints...
    #
    # Note that refactoring this iteration into a dictionary comprehension
    # would be largely infeasible (e.g., due to the need to raise
    # human-readable exceptions on evaluating unevaluatable type hints) as well
    # as largely pointless (e.g., due to dictionary comprehensions being either
    # no faster or even slower than explicit iteration for small dictionary
    # sizes, as "func.__annotations__" usually is).
    for pith_name, pith_hint in func.__annotations__.items():
        # If...
        if (
            # This hint is a string *AND*...
            isinstance(pith_hint, str) and
            # This string is non-empty...
            pith_hint
        ):
        # Then this hint is a PEP 563-compliant postponed hint.  Note that:
        # * This test could technically yield a false positive in the unlikely
        #   edge case that this annotation was previously postponed but has
        #   since been replaced in-place with its referent, which is itself a
        #   string matching the PEP 563 format without actually being a
        #   PEP 563-formatted postponed string. Since there's nothing we can do
        #   about this, we choose to silently pretend everything will be okay.
        # * Any local variables referenced by this annotation are now
        #   inaccessible and *MUST* be ignored, thus raising an exception here
        #   on attempting to evaluate this annotation against a
        #   non-inaccessible local. Yes, this is absurd. But what can you do?
        #   To quote PEP 563:
        #
        #   "When running eval(), the value of globals can be gathered in the
        #    following way:
        #    * function objects hold a reference to their respective globals in
        #      an attribute called __globals__;
        #    ...
        #    The value of localns cannot be reliably retrieved for functions
        #    because in all likelihood the stack frame at the time of the call no
        #    longer exists."

            #FIXME: Since CPython appears to currently be incapable of even
            #defining a deeply nested annotation that would violate this limit,
            #we avoid performing this test for the moment. Nonetheless, it's
            #likely that CPython will permit such annotations to be defined at
            #under some *VERY* distant major version. Ergo, we preserve this.
            # If this string internally exceeds the child limit (i.e., maximum
            # number of nested child type hints listed as subscripted arguments
            # of the parent PEP-compliant type hint produced by evaluating this
            # string) permitted by the @beartype decorator, raise an exception.
            #_die_if_hint_repr_exceeds_child_limit(
            #    hint_repr=pith_hint, pith_label=pith_label)

            # First, attempt to evaluate this postponed hint against the global
            # scope defined by the module declaring the decorated callable.
            #
            # Note that this first attempt intentionally does *NOT* attempt to
            # evaluate this postponed hint against both the global and local
            # scope of the decorated callable. Why? Because:
            # * The overwhelming majority of real-world type hints are imported
            #   at module scope (e.g., from "collections.abc" and "typing") and
            #   thus accessible as global attributes.
            # * Deciding the local scope of the decorated callable is an O(k)
            #   operation for k the distance in call stack frames between the
            #   call to the current function and the call to the parent
            #   callable or class declaring the decorated callable. Ergo, this
            #   decision problem should be deferred until as long as possible
            #   to minimize space and time costs of the @beartype decorator.
            try:
                func_hints[pith_name] = eval(pith_hint, func_globals)
            # If this fails (as it occasionally does)...
            except Exception as exception:
                # Local scope for this callable.
                func_locals = get_func_locals(
                    func=func,
                    # Ignore additional frames on the call stack embodying:
                    # * The current call to this function.
                    # * The call to the parent
                    #   beartype._decor._data.BeartypeData.reinit() method.
                    # * The call to the parent @beartype.beartype() decorator.
                    func_stack_frames_ignore=3,
                    exception_cls=BeartypeDecorHintPep563Exception,
                )

                try:
                    # Last, attempt to evaluate this postponed hint against
                    # both the global and local scopes for the decorated
                    # callable.
                    func_hints[pith_name] = eval(
                        pith_hint, func_globals, func_locals)
                # If this also fails...
                except Exception as exception:
                    # Human-readable label describing this pith.
                    pith_label = label_callable_decorated_pith(
                        func=func, pith_name=pith_name)

                    # Wrap this low-level non-human-readable exception with a
                    # high-level human-readable beartype-specific exception.
                    raise BeartypeDecorHintPep563Exception(
                        f'{pith_label} postponed hint '
                        f'{repr(pith_hint)} syntactically invalid '
                        f'(i.e., "{str(exception)}") under:\n'
                        f'~~~~[ GLOBAL SCOPE ]~~~~\n{repr(func_globals)}\n'
                        f'~~~~[ LOCAL SCOPE  ]~~~~\n{repr(func_locals)}'
                    ) from exception
        # Else, this annotation is *NOT* a PEP 563-formatted postponed string.
        # Since PEP 563 is active for this callable, this implies this
        # annotation *MUST* have been previously postponed but has since been
        # replaced in-place with its referent -- typically due to this callable
        # being chain-decorated by both @beartype and one or more other
        # annotation-based decorations.
        #
        # In this case, silently preserve this annotation as is. Since PEP 563
        # provides no means of distinguishing expected from unexpected
        # evaluation of postponed annotations, either emitting a non-fatal
        # warning *OR* raising a fatal exception here would be overly violent.
        # Instead, we conservatively assume that this annotation was previously
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
        #   * Detecting postponed annotations on arbitrary objects.
        #   * Resolving those annotations.
        # * Dramatically reduces the efficiency of annotation-based decorators
        #   for no particularly good reason.
        # * Non-orthogonally prohibits annotations from accessing local state.
        #
        # Because we should probably mention those complaints here.
        else:
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

            # Silently preserve this annotation as is.
            func_hints[pith_name] = pith_hint

    # Atomically (i.e., all-at-once) replace this callable's postponed
    # annotations with these resolved annotations for safety and efficiency.
    #
    # While the @beartype decorator goes to great lengths to preserve the
    # originating "__annotations__" dictionary as is, PEP 563 is sufficiently
    # expensive, non-trivial, and general-purpose to implement that generally
    # resolving postponed annotations for downstream third-party callers is
    # justified. Everyone benefits from replacing useless postponed annotations
    # with useful real annotations; so, we do so.
    func.__annotations__ = func_hints

    #FIXME: We currently no longer require this, but nonetheless preserve this
    #for both posterity and the unknowable future to come.
    # Else, this callable's annotations are *NOT* postponed under PEP 563. In
    # this case, shallowly copy the originating annotations dictionary to a
    # beartype-specific annotations dictionary to enable other functions
    # elsewhere to safely modify these annotations.
    # else:
    #     data.func_hints = data.func.__annotations__.copy()

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
#     :mod:`beartype_test.a00_unit.data.data_pep563` submodule for appalling details.
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
#         necessarily as a `PEP 563`_-formatted postponed string.
#     pith_label : str
#         Human-readable label describing the callable parameter or return value
#         annotated by this string.
#
#     Raises
#     ----------
#     BeartypeDecorHintPepException
#         If this representation internally exceeds this limit.
#
#     .. _PEP 563:
#        https://www.python.org/dev/peps/pep-0563
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
