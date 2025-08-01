#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype :pep:`563` **resolvers** (i.e., public high-level callables resolving
stringified :pep:`563`-compliant type hints implicitly postponed by the active
Python interpreter via a ``from __future__ import annotations`` statement at the
head of the external user-defined module currently being introspected).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ TODO                               }....................
#FIXME: Conditionally emit a non-fatal PEP 563-specific warning when the active
#Python interpreter targets Python >= 3.10 *AND* the passed callable is nested.
#FIXME: Actually, don't even bother. Instead, generalize the resolve_pep563()
#function defined below to emit a non-fatal deprecation warning when Python 3.13
#reaches its End-of-Life on October, 2029. At that point, PEP 563 will be
#officially deprecated. Two minor CPython releases after that happens, the
#entire "from __future__ import annotations" pragma and thus PEP 563 itself will
#be officially *REMOVED* from the language specification. At that point, any
#attempt by end users to use "from __future__ import annotations" will raise a
#fatal "SyntaxError" from CPython itself. \o/

#FIXME: [DOCOS] Officially document both this and the public "beartype.peps"
#submodule, please.

# ....................{ IMPORTS                            }....................
from beartype.roar import BeartypePep563Exception
from beartype._check.forward.fwdresolve import resolve_hint
from beartype._check.metadata.metadecor import (
    cull_beartype_call,
    make_beartype_call,
)
from beartype._conf.confcommon import BEARTYPE_CONF_DEFAULT
from beartype._conf.confmain import BeartypeConf
from beartype._data.typing.datatyping import TypeStack
from beartype._util.hint.pep.proposal.pep649 import (
    get_pep649_hintable_annotations,
    set_pep649_hintable_annotations,
)
from collections.abc import Callable

# ....................{ RESOLVERS                          }....................
def resolve_pep563(
    # Mandatory parameters.
    func: Callable,

    # Optional parameters.
    conf: BeartypeConf = BEARTYPE_CONF_DEFAULT,
    cls_stack: TypeStack = None,
) -> None:
    '''
    Resolve all :pep:`563`-based **postponed annotations** (i.e., strings that
    when dynamically evaluated as Python expressions yield actual annotations)
    on the passed callable to their **referents** (i.e., the actual annotations
    to which those postponed annotations evaluate) if :pep:`563` is active for
    that callable *or* silently reduce to a noop otherwise (i.e., if :pep:`563`
    is *not* active for that callable).

    :pep:`563` is active for that callable if the module declaring that callable
    explicitly enabled :pep:`563` support with a leading dunder importation of
    the form ``from __future__ import annotations``. If :pep:`563` is active for
    that callable, then for each type-hint annotating that callable:

    * If that hint is a string and thus postponed, this function:

      #. Dynamically evaluates that string within that callable's globals
         context (i.e., set of all global variables defined by the module
         declaring that callable).
      #. Replaces that hint's string value with the expression produced by this
         dynamic evaluation.

    * Else, this function preserves that hint as is (e.g., due to that hint
      that was previously postponed having already been evaluated by a prior
      decorator).

    Parameters
    ----------
    func : Callable
        Callable to resolve postponed annotations on.
    conf : BeartypeConf, optional
        Beartype configuration configuring :func:`beartype.beartype` uniquely
        specific to this callable. Defaults to :data`.BEARTYPE_CONF_DEFAULT`,
        the default beartype configuration.
    cls_stack : TypeStack
        Either:

        * If that callable is a method of a class, the **type stack** (i.e.,
          tuple of one or more lexically nested classes in descending order of
          top- to bottom-most lexically nested) such that:

          * The first item of this tuple is expected to be the **root class**
            (i.e., top-most class whose lexical scope encloses that callable,
            typically declared at module scope and thus global).
          * The last item of this tuple is expected to be the **current class**
            (i.e., possibly nested class directly containing that method).

        * Else, that callable is *not* a method of a class. In this case,
          :data:`None`.

        Defaults to :data:`None`.

        Note that this function requires *both* the root and current class to
        correctly resolve edge cases under :pep:`563`: e.g.,

        .. code-block:: python

           from __future__ import annotations
           from beartype import beartype

           @beartype
           class Outer(object):
               class Inner(object):
                   # At this time, the "Outer" class has been fully defined but
                   # is *NOT* yet accessible as a module-scoped attribute. Ergo,
                   # the *ONLY* means of exposing the "Outer" class to the
                   # recursive decoration of this get_outer() method is to
                   # explicitly pass the "Outer" class as the "cls_root"
                   # parameter to all decoration calls.
                   def get_outer(self) -> Outer:
                       return Outer()

        Note also that nested classes have *no* implicit access to either their
        parent classes *or* to class variables declared by those parent classes.
        Nested classes *only* have explicit access to module-scoped classes --
        exactly like any other arbitrary objects: e.g.,

        .. code-block:: python

           class Outer(object):
               my_str = str

               class Inner(object):
                   # This induces a fatal compile-time exception resembling:
                   #     NameError: name 'my_str' is not defined
                   def get_str(self) -> my_str:
                       return 'Oh, Gods.'

        Nonetheless, this tuple *must* contain all of those nested classes
        lexically containing the passed method. Why? Because this function
        resolves local attributes defined in the body of the callable on the
        current call stack lexically containing those nested classes (if any) by
        treating the length of this tuple as the total number of classes
        lexically nesting the current class. In short, just pass everything.

    Raises
    ------
    BeartypePep563Exception
        If either:

        * That callable is *not* a pure-Python callable (e.g., is C-based).
        * Evaluating a postponed annotation on that callable raises an exception
          (e.g., due to that annotation referring to local state inaccessible in
          this deferred context).
    '''

    # ..................{ NOOP                               }..................
    # Dictionary to be returned, mapping from the name of each annotated
    # parameter and return of the passed callable to the non-string type hint
    # resolved from the string type hint annotating that parameter or return --
    # raising an exception if that callable is *NOT* a pure-Python callable.
    func_annotations = get_pep649_hintable_annotations(
        hintable=func, exception_cls=BeartypePep563Exception)

    # If that callable is unannotated, silently reduce to a noop.
    if not func_annotations:
        return
    # Else, that callable is annotated by one or more type hints.

    # If that callable was *NOT* subject to PEP 563-compliant postponement of
    # type hints under the standard "from __future__ import annotations" import,
    # silently reduce to a noop.
    #
    # Note that there exist numerous means of detecting PEP 563. This approach:
    # * Is the least efficient, requiring O(n) iteration for n the number of
    #   type hints annotating that callable.
    # * Is the most reliable, detecting PEP 563 regardless of whether:
    #   * That callable was dynamically synthesized in-memory *OR* physically
    #     defined in an on-disk source module. In the latter case, this
    #     detection heuristic could statically analyze the on-disk source code
    #     underlying that callable for an import of the form:
    #         from __future__ import annotations
    #     In the former case, however, that analysis is infeasible.
    #   * The "__future__.annotations" singleton object is a global attribute of
    #     the module defining that callable. This simplistic test fails under
    #     numerous edge cases, including if:
    #     * That callable was dynamically synthesized in-memory, in which case
    #       that callable may have *NO* such module.
    #     * That callable was physically defined in an on-disk source module
    #       that enabled PEP 563 but which then maliciously deleted the
    #       "__future__.annotations" singleton object from module scope: e.g.,
    #           from __future__ import annotations
    #           del annotations
    #       Yes, that is valid Python. Yes, Python continues to enable PEP 563
    #       for that module despite that module deleting the "annotations"
    #       attribute from module scope. Yes, we're facepalming ourselves.
    #
    # Since reliability is *FAR* more important than efficiency, this function
    # adopts the detection heuristic that is the most inefficient and reliable.
    #
    # For the name of each annotated parameter and return of the passed callable
    # and the type hint annotating that parameter or return...
    for hint in func_annotations.values():
        # If this hint is *NOT* stringified, this hint was either:
        # * Never postponed under PEP 563 (i.e., the module defining that
        #   callable did *NOT* import "from __future__ import annotations").
        # * Previously postponed under PEP 563 (i.e., the module defining that
        #   callable imported "from __future__ import annotations") but has
        #   since been resolved into a non-string type hint by a competing
        #   runtime type-introspector, possibly including @beartype itself.
        #
        # In either case, PEP 563 is now disabled for this hint. But PEP 563 is
        # a module-scoped effect that universally applies to *ALL* type hints
        # annotating *ALL* callables of a module. If PEP 563 is disabled for one
        # hint of a callable, then PEP 563 must necessarily be disabled for all
        # hints of that same callable. In this case, reduce to a noop.
        if not isinstance(hint, str):
            return
        # Else, this hint is stringified. In this case, this hint was either:
        # * Postponed under PEP 563 (i.e., the module defining that callable
        #   imported "from __future__ import annotations").
        # * Never postponed under PEP 563 (i.e., the module defining that
        #   callable did *NOT* import "from __future__ import annotations") but
        #   was instead simply a PEP 484-compliant forward reference (e.g.,
        #   "def muh_func(muh_arg: 'MuhClass'): ...").
        #
        # Differentiating these two cases is infeasible! Python's standard
        # library failed to ship solutions to this or any other outstanding
        # runtime issues with PEP 563. Instead, we pretend everything will be
        # okay by silently ignoring the latter case. Doing so largely suffices
        # but can technically yield a false positive. This is why PEP 563 should
        # have failed Python's peer review process. Of course, it passed
        # instead. In short: "Trust me, bro."
    # All type hints annotating the passed callable are now guaranteed to have
    # been stringified. For simplicity, we assume these hints were stringified
    # automatically by PEP 563 rather than manually by user typing.

    # ..................{ LOCALS                             }..................
    # Beartype call metadata describing the passed callable.
    decor_meta = make_beartype_call(func=func, conf=conf, cls_stack=cls_stack)

    # Shallow copy of the dictionary to be returned. Why? Because the
    # "func.__annotations__" dictionary *CANNOT* be safely directly assigned to
    # below, as the loop performing that assignment below necessarily iterates
    # over that dictionary. As with most languages, Python containers cannot be
    # safely mutated while being iterated.
    func_annotations = func_annotations.copy()

    # ..................{ RESOLUTION                         }..................
    # For the name of each annotated parameter and return of the passed callable
    # and the stringified type hint annotating that parameter or return...
    #
    # Note that refactoring this iteration into a dictionary comprehension would
    # be both:
    # * Largely infeasible (e.g., due to the need to raise human-readable
    #   exceptions on evaluating invalid type hints).
    # * largely pointless (e.g., due to dictionary comprehensions being either
    #   no faster or even slower than explicit iteration for small dictionary
    #   sizes, as "func.__annotations__" usually is).
    for pith_name, hint in func_annotations.items():
        # Non-string hint to which this stringified hint refers
        hint = resolve_hint(
            hint=hint,
            decor_meta=decor_meta,
            exception_cls=BeartypePep563Exception,
        )

        # Safely set the hint annotating the parameter or return with the passed
        # name of the decorated callable to the passed hint in a portable manner
        # consistent with both PEP 649 and Python >= 3.14.
        decor_meta.set_func_pith_hint(pith_name=pith_name, hint=hint)

    # ..................{ RETURN                             }..................
    # Deinitialize this beartype call metadata.
    #
    # Note that this implicitly replaces that callable's postponed hints with
    # these resolved hints. While the @beartype decorator goes to great lengths
    # to preserve the originating "__annotations__" dictionary as is, PEP 563 is
    # sufficiently expensive, non-trivial, and general-purpose to support that
    # generically resolving postponed annotations for all downstream third-party
    # callers is justified. Everyone benefits from replacing useless postponed
    # annotations with useful real annotations; so, do so.
    cull_beartype_call(decor_meta)

    # print(
    #     f'{func.__name__}() PEP 563-postponed annotations resolved:'
    #     f'\n\t------[ POSTPONED ]------\n\t{func_hints_postponed}'
    #     f'\n\t------[ RESOLVED  ]------\n\t{func_hints_resolved}'
    # )

# ....................{ PRIVATE ~ resolvers                }....................
#FIXME: We currently no longer require this. See above for further commentary.
# from beartype.roar import BeartypeDecorHintPepException
# from beartype._util.cache.pool.utilcachepoollistfixed import FIXED_LIST_SIZE_MEDIUM
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
#     if hints_num >= FIXED_LIST_SIZE_MEDIUM:
#         raise BeartypeDecorHintPepException(
#             f'{pith_label} hint representation "{hint_repr}" '
#             f'contains {hints_num} subscripted arguments '
#             f'exceeding maximum limit {FIXED_LIST_SIZE_MEDIUM-1}.'
#         )
