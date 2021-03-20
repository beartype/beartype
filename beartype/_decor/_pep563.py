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
from beartype.roar import (
    BeartypeDecorHintPep563Exception,
    BeartypeDecorHintPepException,
)
from beartype._decor._data import BeartypeData
from beartype._util.cache.pool.utilcachepoollistfixed import SIZE_BIG
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

    Conditions
    ----------
    `PEP 563`_ is active for this callable if the active Python interpreter
    targets:

    * Python >= 3.10, where `PEP 563`_ is globally, unconditionally enabled.
    * Python >= 3.7 < 3.10 *and* the module declaring this callable explicitly
      enables `PEP 563`_ support with a leading dunder importation of the form
      ``from __future__ import annotations``.

    Resolution
    ----------
    If the above conditions applies, then for each annotation on this callable:

    * If this annotation is postponed (i.e., is a string), this function:

      #. Dynamically evaluates that string within this callable's globals
         context (i.e., set of all global variables defined by the module
         declaring this callable).
      #. Replaces this annotation's string value with the expression produced
         by this dynamic evaluation.

    * Else, this function preserves this annotation as is.

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

    # If this callable's annotations are postponed under PEP 563, resolve these
    # annotations to their referents.
    if _is_hints_postponed(data):
        _resolve_hints_postponed(data)

    #FIXME: We currently no longer require this, but nonetheless preserve this
    #for both posterity and the unknowable future to come.
    # Else, this callable's annotations are *NOT* postponed under PEP 563. In
    # this case, shallowly copy the originating annotations dictionary to a
    # beartype-specific annotations dictionary to enable other functions
    # elsewhere to safely modify these annotations.
    # else:
    #     data.func_hints = data.func.__annotations__.copy()

# ....................{ PRIVATE ~ resolvers               }....................
def _is_hints_postponed(data: BeartypeData) -> bool:
    '''
    ``True`` only if `PEP 563`_ is active for the currently decorated callable.

    Parameters
    ----------
    data : BeartypeData
        Decorated callable to be inspected.

    Returns
    ----------
    bool
        ``True`` only if `PEP 563`_ is active for this callable.

    .. _PEP 563:
       https://www.python.org/dev/peps/pep-0563
    '''
    assert data.__class__ is BeartypeData, f'{repr(data)} not @beartype data.'

    # True only if PEP 563 is active for this callable.
    #
    # If the active Python interpreter targets Python >= 3.10, PEP 563 is
    # unconditionally active. Ergo, *ALL* annotations including this callable's
    # annotations are necessarily postponed.
    is_hints_postponed = IS_PYTHON_AT_LEAST_3_10

    # If the active Python interpreter targets at least Python 3.7.x, PEP 563
    # is conditionally active only if...
    if not is_hints_postponed and IS_PYTHON_AT_LEAST_3_7:
        # Module declaring this callable.
        func_module = sys_modules[data.func.__module__]

        # "annotations" attribute declared by this module if any *OR* None.
        func_module_annotations_attr = getattr(
            func_module, 'annotations', None)

        # If this attribute is the "__future__.annotations" object, then the
        # module declaring this callable *MUST* necessarily have enabled PEP
        # 563 support with a leading statement resembling:
        #     from __future__ import annotations
        is_hints_postponed = (
             func_module_annotations_attr is __future__.annotations)

    # Return true only if PEP 563 is active for this callable.
    return is_hints_postponed


def _resolve_hints_postponed(data: BeartypeData) -> None:
    '''
    Resolve all `PEP 563`_-based postponed annotations on the currently
    decorated callable to their referents.

    Parameters
    ----------
    data : BeartypeData
        Decorated callable to be resolved.

    Raises
    ----------
    BeartypeDecorHintPep563Exception
        If evaluating a postponed annotation on this callable raises an
        exception (e.g., due to that annotation referring to local state no
        longer accessible from this deferred evaluation).

    .. _PEP 563:
       https://www.python.org/dev/peps/pep-0563
    '''
    assert data.__class__ is BeartypeData, f'{repr(data)} not @beartype data.'
    # print('annotations: {!r}'.format(func.__annotations__))

    # Localize attributes of this metadata for negligible efficiency gains.
    func = data.func
    func_globals = func.__globals__  # type: ignore[attr-defined]

    # Dictionary mapping from parameter name to resolved annotation for each
    # annotated parameter and return value of this callable.
    func_hints = {}

    # For the parameter name (or "return" for the return value) and
    # corresponding annotation of each of this callable's annotations...
    #
    # Note that refactoring this iteration into a dictionary comprehension
    # would be largely infeasible (e.g., due to the need to raise
    # human-readable exceptions on evaluating unevaluatable annotations) as
    # well as largely pointless (e.g., due to dictionary comprehensions being
    # either no faster or even slower than explicit iteration for small
    # dictionary sizes, as "func.__annotations__" usually is).
    for pith_name, pith_hint in func.__annotations__.items():
        # Human-readable label describing this pith.
        pith_label = label_callable_decorated_pith(
            func=func, pith_name=pith_name)

        # If...
        if (
            # This annotation is a string *AND*...
            isinstance(pith_hint, str) and
            # This string is non-empty...
            pith_hint
        ):
        # Then this annotation is a PEP 563-formatted postponed string. In this
        # case, resolve this annotation to its referent against the global
        # variables (if any) defined by the module defining this callable.
        #
        # Note that:
        #
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

            # If this string internally exceeds the child limit (i.e., maximum
            # number of nested child type hints listed as subscripted arguments
            # of the parent PEP-compliant type hint produced by evaluating this
            # string) permitted by the @beartype decorator, raise an exception.
            _die_if_hint_repr_exceeds_child_limit(
                hint_repr=pith_hint, pith_label=pith_label)

            #FIXME: Insufficient. We also need to dynamically obtain
            #"func_locals" by either:
            #* If "func" is actually a @beartype-decorated class, then PEP 563
            #  itself provides the algorithm for retrieving this:
            #      For classes, localns can be composed by chaining vars of the
            #      given class and its base classes (in the method resolution
            #      order). Since slots can only be filled after the class was
            #      defined, we don't need to consult them for this purpose.
            #  That seems... pretty intense. We're fairly certain typing.
            #* If "func" is instead a @beartype-decorated callable, then PEP
            #  563 is sadly useless, because it uselessly intones:
            #      The value of localns cannot be reliably retrieved for
            #      functions because in all likelihood the stack frame at the
            #      time of the call no longer exists.
            #  This is obviously untrue for decorators, whose parent callable
            #  (if any) absolutely does provide the desired stack frame. This
            #  suggests:
            #  * The top-level @beartype() function itself needs to decide
            #    whether or not it is being called at module scope (the common
            #    case) *OR* at function scope (the edge case). We intuitively
            #    suspect that the "func.__qualname__" dunder attribute provides
            #    the easiest means of doing so, because the value of that
            #    attribute for closures should contain a substring resembling
            #    "<locals>" or something. Maybe. Let's investigate. Actually:
            #    * Don't closures have cell variables? *AH, YES.* That's it.
            #      Closures have a "__closure__" dunder attribute listing all
            #      cell variables of that closure. Obviously, only closures
            #      define that attribute. Ergo, the mere existence of that
            #      attribute suffices to inform us that @bearype() is called
            #      at function scope (to decorate a closure). Phew!
            #  * If @beartype() is called at module scope, nothing further need
            #    be done, as "func_globals == func_locals".
            #  * If @beartype() is called at function scope, we now need to
            #    roll up our sleeves. Specifically, it would seem that the
            #    following expression yields the desired dictionary:
            #        from inspect import currentframe
            #        func_locals = currentframe().f_back.f_locals
            #    Yes, the currentframe() call is likely to be inefficient. It's
            #    also likely to be portable. Moreover, we *ONLY* require this
            #    when @beartype() is used to decorate function-local callables,
            #    which is an unlikely edge case we basically only hit in our
            #    test suite. We need it there, but this does *NOT* need to be
            #    highly performant. This just needs to work.
            #    * *WAIT.* Fascinatingly, it turns out that we can also
            #      construct the same "func_locals" dictionary ourselves by
            #      combining the "func.__code__.co_freevars" tuple of the names
            #      of all locals defined by the parent function referenced by
            #      this closure. In theory, type hints annotating this closure
            #      but defined by the parent function should *ABSOLUTELY* be
            #      listed in this tuple. We'll need to investigate that,
            #      obviously. If true, though, we can probably do this much
            #      more efficiently without "inspect" by black magic ala:
            #        # Wrap this in a new utility method, please.
            #        func_locals = dict(zip(
            #            func.__code__.co_freevars,
            #            (cell.cell_contents for cell in func.__closure__)
            #        ))
            #      *YES.* It's a bit gnarly, but it'll work -- maybe. It'll also be
            #      significantly more reliable than the currentframe()
            #      approach, which will almost certainly fail in edge cases,
            #      because its implementation is super-dark-magic:
            #          def currentframe():
            #              """Return the frame of the caller or None if this is not possible."""
            #              return sys._getframe(1) if hasattr(sys, "_getframe") else None
            #      Yeah. currentframe() fails if the active Python interpreter
            #      fails to conditionally define a private "sys" attribute.
            #      We're definitely not going there, folks. Ergo, closures.
            #   * *UGH!* Unfortunately, we have no choice but to go there. Why?
            #     Because Python fails to record closure annotations bound to
            #     function scope as free variables, which means we literally
            #     have *NO* other access to those annotations except to inspect
            #     the call stack:
            #     >>> def muh():
            #     ...     ugh = int
            #     ...     def agh(huh: ugh): pass
            #     ...     print(f'agh.__code__.co_freevars: {agh.__code__.co_freevars}')
            #     >>> muh()
            #     agh.__code__.co_freevars: ()
            #     This sucks, which means we're going to need to explicitly
            #     call currentframe() instead and handle a "None" return value
            #     *BY DOING ABSOLUTELY NOTHING.* That is, if currentframe()
            #     returns "None", then we silently avoid trying to construct
            #     "func_locals" at all. Just don't.
            #FIXME: How does this intersect with class and instance methods? Do
            #we actually exercise @beartype against class and instance methods
            #in our test suite anywhere? We suspect... not. Obviously, we need
            #to begin doing that. *sigh*
            #FIXME: We also need to handle recursively wrapped callables to
            #obtain the root "__globals__". For example, this is what
            #typing.get_type_hints() does to obtain this metadata:
            #    # Find globalns for the unwrapped object.
            #    while hasattr(func, '__wrapped__'):
            #        func = func.__wrapped__
            #    func_globals = func.__globals__
            #So, we probably want similar logic above. Naturally, we might mant
            #to refactor that "while" loop out into a proper utility function
            #-- or maybe the whole thing, really: e.g.,
            #    from inspect import currentframe
            #
            #    # Declared somewhere else.
            #    def get_func_globals_locals(func: Callable) -> Tuple[
            #        Dict[str, Any], Optional[Dict[str, Any]]]:
            #        assert callable(func), f'{repr(func)} not callable.'
            #
            #        # Find globalns for the unwrapped object.
            #        while hasattr(func, '__wrapped__'):
            #            func = func.__wrapped__
            #        func_globals = func.__globals__
            #
            #        func_locals = None
            #
            #        if hasattr(func, '__closure__'):
            #            call_stack = currentframe()
            #
            #            if call_stack:
            #                #FIXME: Yikes. Two "f_back" references? *shrug*
            #                func_locals = call_stack.f_back.f_back.f_locals
            #
            #                #FIXME: Actually, raise an exception instead. This
            #                #is critical and fragile stuff, guys.
            #                # Assert this local dictionary declares this
            #                # closure for sanity.
            #                assert func.__name__ in func_locals, (
            #                   f'Closure {func.__name__} not declared by '
            #                   f'parent callable scope {func_locals}.)
            #
            #        return func_globals, func_locals
            #Note:
            #* We need to call that utility function from @beartype() directly
            #  to ensure proper "f_back" referencing.
            #* For the same reason, the docstring for that utility function
            #  should *ABSOLUTELY* note that that function should be called
            #  directly by the function possibly receiving a closure to ensure
            #  that the parent scope of that closure is properly retrieved.
            #  Failure to do so *WILL RESULT IN A RAISED EXCEPTION.*
            #FIXME: Actually, it's a bit worse than described above, because
            #the decorated callable could be decorated by multiple decorators,
            #which means it has *NO* reliable location in the call stack.
            #Instead, we *MUST* iteratively search up the call stack until
            #finding a parent callable satisfying the constraints:
            #    func_name = func.__name__
            #    (
            #        func_name in func_locals and
            #
            #        #FIXME: *OH.* Wait. If the decorated callable is decorated
            #        #by multiple decorators, then this constraint wouldn't
            #        #hold. Even if did, we doubt this callable is actually
            #        #available in "func_locals" at this point. Maybe it is?
            #        #Maybe closures are declared... *sigh*
            #        func_locals[func_name] == func
            #    )
            #
            #Okay. So, the above test probably doesn't work. The only sane
            #alternative we can think of is to:
            #* Parse "__qualname__" either with "str.[r]split('.')" or a
            #  compiled regex. Probably a compiled regex, because we don't just
            #  need to split; we need to get the Python identifier preceding
            #  the last ".<locals>" in "__qualname__". Right? Compiled regex.
            #* Get the Python identifier preceding the last ".<locals>" in
            #  "__qualname__". That will give us the name of the parent
            #  callable whose *LEXICAL* scope declares this closure.
            #* Given that, we can then iteratively search up the current call
            #  stack to find that parent callable. Fortunately, we shouldn't
            #  have to search far; the parent callable's frame should be *VERY*
            #  close to the current frame. Nonetheless, this is still O(n) for
            #  n the call stack height in the worst case. *sigh*
            #FIXME: Actually, it still might be a bit worse than described
            #above, because closures can be nested in closures *AND INNER
            #CLOSURES CAN BE ANNOTATED BY TYPE HINTS DECLARED IN THE OUTERMOST
            #SCOPE.* We have verified this. This means we now need to
            #iteratively synthesize "func_locals" by generalizing the above
            #algorithm. Specifically:
            #
            #* Initialize "func_locals: Dict[str, Any] = {}".
            #* For each ".<locals>" in "func.__qualname__":
            #  * Iteratively search up the current call stack for the parent
            #    callable whose unqualified name (i.e., "__name__") precedes
            #    that ".<locals>".
            #  * Extend "func_locals" by the "f_locals" dictionary in the call
            #    stack for that parent function.
            #
            #Note that we actually need to perform this iteration in the
            #reverse direction (i.e., starting at the outermost scope and
            #proceeding inwards) to ensure that inner variables occlude outer
            #variables. This suggests we should probably implement this as a
            #two-pass algorithm as follows:
            #* Define a new "frames_parent = []".
            #* In the first pass, we populate "frames_parent" with the call
            #  frames of all such parent callables as discovered above (i.e.,
            #  by parsing "func.__qualname__" and iterating up the call stack).
            #* In the second pass, we iterate "frames_parent" *IN THE REVERSE
            #  DIRECTION* (i.e., starting at the end). On each iteration, we
            #  extend "func_locals" by the "f_locals" dictionary in the current
            #  stack frame being iterated.
            #
            #Pretty intense stuff. This will work, but it's *NOT* going to be
            #trivial, efficient, or easy. It *SHOULD* be robust for at least
            #CPython and PyPy, which are the primary use cases. *SHOULD*.
            #FIXME: Actually, it still might be a bit worse than described
            #above, because (nested) classes also interact with (nested)
            #closures. Fortunately, note that decorators can non-trivially
            #decide whether they're currently decorating an unbound method
            #(which tests as a function from the perspective of isinstance) or
            #a non-class function. How? By inspecting the call stack yet again.
            #From an exceptionally useful StackOverflow post:
            #    Take a look at the output of inspect.stack() when you wrap a
            #    method. When your decorator's execution is underway, the
            #    current stack frame is the function call to your decorator;
            #    the next stack frame down is the @ wrapping action that is
            #    being applied to the new method; and the third frame will be
            #    the class definition itself, which merits a separate stack
            #    frame because the class definition is its own namespace (that
            #    is wrapped up to create a class when it is done executing).
            #See also:
            #    https://stackoverflow.com/a/8793684/2809027
            #
            #Our intuitive analysis of the situation suggests that, for our
            #purposes, (nested) classes and closures should effectively be
            #solvable by the exact same algorithm with *NO* special handling
            #required for (nested) classes, since (nested) class declarations
            #are simply additional frames on the call stack. Nice! Two birds
            #with one stone to go.
            #FIXME: Exercise this edge case with a unit test:
            #* Declaring a closure decorated by both @beartype and another
            #  decorator (probably just the identity decorator for simplicity).
            #* Declaring a closure decorated by both @beartype and another
            #  decorator (probably just the identity decorator for simplicity)
            #  nested inside of another closure such that the inner closure is
            #  annotated by type hints defined by the outer scope declaring the
            #  outer closure.
            #* Declaring an instance method decorated by both @beartype and
            #  another decorator (probably just the identity decorator for
            #  simplicity) declared in a class declared in a function.
            #* Declaring an instance method decorated by both @beartype and
            #  another decorator (probably just the identity decorator for
            #  simplicity) declared in a class declared in a closure nested
            #  inside of function such that the instance method is annotated by
            #  type hints defined by the function declaring the closure.
            #This is incredibly fragile, so tests.

            # Attempt to resolve this postponed annotation to its referent.
            try:
                func_hints[pith_name] = eval(pith_hint, func_globals)
            # If this fails (as it commonly does), wrap the low-level (and
            # usually non-human-readable) exception raised by eval() with a
            # higher-level human-readable beartype-specific exception.
            except Exception as exception:
                raise BeartypeDecorHintPep563Exception(
                    f'{pith_label} postponed hint '
                    f'"{pith_hint}" not evaluable.'
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
            _die_if_hint_repr_exceeds_child_limit(
                hint_repr=repr(pith_hint),
                pith_label=pith_label)

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


# ....................{ PRIVATE ~ resolvers               }....................
def _die_if_hint_repr_exceeds_child_limit(
    hint_repr: str, pith_label: str) -> None:
    '''
    Raise an exception if the passed machine-readable representation of an
    arbitrary annotation internally exceeds the **child limit** (i.e., maximum
    number of nested child type hints listed as subscripted arguments of
    PEP-compliant type hints) permitted by the :func:`beartype.beartype`
    decorator.

    The :mod:`beartype` decorator internally traverses over these nested child
    types of the parent PEP-compliant type hint produced by evaluating this
    string representation to its referent with a breadth-first search (BFS).
    For efficiency, this search is iteratively implemented with a cached
    **fixed list** (i.e.,
    :class:`beartype._util.cache.pool.utilcachepoollistfixed.FixedList`
    instance) rather than recursively implemented with traditional recursion.
    Since the size of this list is sufficiently large to handle all uncommon
    *and* uncommon edge cases, this list suffices for *all* PEP-compliant type
    hints of real-world interest.

    Nonetheless, safety demands that we guarantee this by explicitly raising an
    exception when the internal structure of this string suggests that the
    resulting PEP-compliant type hint will subsequently violate this limit.
    This has the convenient side effect of optimizing that BFS, which may now
    unconditionally insert child hints into arbitrary indices of that cached
    fixed list without having to explicitly test whether each index exceeds the
    fixed length of that list.

    Caveats
    ----------
    **This function is currently irrelevant.** Why? Because all existing
    implementations of the :mod:`typing` module are sufficiently
    space-consumptive that they already implicitly prohibit deep nesting of
    PEP-compliant type hints. See commentary in the
    :mod:`beartype_test.a00_unit.data.data_pep563` submodule for appalling details.
    Ergo, this validator could technically be disabled. Indeed, if this
    validator actually incurred any measurable costs, it *would* be disabled.
    Since it doesn't, this validator has preserved purely for forward
    compatibility with some future revision of the :mod:`typing` module that
    hopefully improves that module's horrid space consumption.

    Parameters
    ----------
    hint_repr : str
        Machine-readable representation of this annotation, typically but *not*
        necessarily as a `PEP 563`_-formatted postponed string.
    pith_label : str
        Human-readable label describing the callable parameter or return value
        annotated by this string.

    Raises
    ----------
    BeartypeDecorHintPepException
        If this representation internally exceeds this limit.

    .. _PEP 563:
       https://www.python.org/dev/peps/pep-0563
    '''
    assert isinstance(hint_repr, str), f'{repr(hint_repr)} not string.'

    # Total number of hints transitively encapsulated in this hint (i.e., the
    # total number of all child hints of this hint as well as this hint
    # itself), defined as the summation of...
    hints_num = (
        # Number of parent PEP-compliant type hints nested in this hint,
        # including this hint itself *AND*...
        hint_repr.count('[') +
        # Number of child type hints (both PEP-compliant type hints and
        # non-"typing" types) nested in this hint, excluding the last child
        # hint subscripting each parent PEP-compliant type hint *AND*...
        hint_repr.count(',') +
        # Number of last child hints subscripting all parent PEP-compliant type
        # hints.
        hint_repr.count(']')
    )

    # If this number exceeds the fixed length of the cached fixed list with
    # which the @beartype decorator traverses this hint, raise an exception.
    if hints_num >= SIZE_BIG:
        raise BeartypeDecorHintPepException(
            f'{pith_label} hint representation "{hint_repr}" '
            f'contains {hints_num} subscripted arguments '
            f'exceeding maximum limit {SIZE_BIG-1}.'
        )
