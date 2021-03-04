#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2021 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype decorator PEP-compliant type-checking graph-based code generator.**

This private submodule dynamically generates pure-Python code type-checking
arbitrary **PEP-compliant type hints** (i.e., :mod:`beartype`-agnostic
annotations compliant with annotation-centric PEPs) of the decorated callable
with a breadth-first search over the abstract graph of nested objects reachable
from the subscripted arguments of these hints.

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ TODO                              }....................
#FIXME: Byte string values aren't displayed properly in messages: e.g.,
#    ...as value "b"What? Haven't you ever seen a byte-string separator
#    before?"" not str.

#FIXME: Resurrect memoization support. To do so, we'll probably need to
#abandon the @callable_cached decorator employed below in favour of a manually
#implemented dictionary cache resembling:
#
#    _PEP_HINT_REPR_TO_CODE_CHECK = {}
#    '''
#    Dictionary mapping from the machine-readable representation of each
#    PEP-compliant type hint previously passed to a call of the
#    :func:`pep_code_check_hint` function to the tuple returned from that call.
#    '''
#
#Why? Because PEP 585 fails to internally cache PEP 585-compliant type hints,
#unlike *MOST* PEP 484-compliant type hints: e.g.,
#
#     >>> import typing as t
#     >>> list[int] is list[int]
#     False
#     >>> t.List[int] is t.List[int]
#     True
#
#This means that brute-force memoization fails. Happily, the __repr__() dunder
#method still exists to uniquely identify type hints. While calling that
#method will impose a non-negligible runtime cost, that cost will absolutely be
#*MUCH* smaller than that imposed by the pep_code_check_hint().
#
#The pep_code_check_hint() function will then need to be refactored as follows:
#* Drop the @callable_cached decorator.
#* Before doing *ANYTHING* else in the body of that function:
#  1. Get the passed hint's repr().
#  2. If that repr() is a key of "_PEP_HINT_REPR_TO_CODE_CHECK",
#     immediately return the corresponding value of that dictionary.
#  3. Else, continue as normal.
#* At the very end of that function, cache that repr() and the generated
#  code as a new key-value pair of that dictionary.
#
#Note that this can probably be optimized a bit by noting that *SOME* (but
#probably not *ALL*) "typing" hints are cached. That means we can directly
#cache the id() rather than repr() for those hints, which is substantially
#faster to compute. The issue, of course, is deciding the subset of "typing"
#hints that are reliably cached. To compound matters, we need to do this across
#all supported Python versions.
#
#Under Python 3.9, this appears to be trivially decidable. Since the private
#@typing._tp_cache decorator performs this caching, we only need to find all
#methods decorated by this decorator and then work backward to the public
#"typing" hints bound to those methods.
#
#Actually, for simplicity, let's just assume for now that all type hints
#*OTHER* than PEP 585-compliant type hints are internally cached. This is
#probably a close enough approximation to the truth to suffice for now.
#FIXME: If one considers it, the situation actually a bit worse than that
#described above. *ALL* memoized functions accepting type hints currently
#suffer the same issue, which means that manually correcting the
#pep_code_check_hint() function alone fails to generalize. Instead, we need to:
#
#* Refactor the existing @callable_cached decorator to *STOP* supporting
#  keyword arguments. There's absolutely *NO* reason to emit non-fatal warnings
#  as we currently do. Instead, just drop keyword argument support entirely.
#  For robustness, this decorator should be augmented to internally perform the
#  following additional operation:
#  * In the outer decorator:
#    * If the decorated callable accepts a parameter named "hint", raise an
#      exception.
#* Define a new @callable_cached_hintable decorator copied from the existing
#  @callable_cached. For efficiency, this decorator *MUST* be augmented to
#  internally perform the following additional operations:
#  * In the outer decorator:
#    * If the decorated callable does *NOT* accept a mandatory parameter named
#      "hint", raise an exception. Note the emphasis on *MANDATORY.* We believe
#      that all "hint" parameters are mandatory, which simplifies things.
#    * Since this decorator will only accept positional arguments, the 0-based
#      index of the "hint" parameter will be known at decoration time in the
#      outer decorator. Localize this index as a closure constant accessible to
#      the inner wrapper function returned by the outer decorator.
#  * In the inner wrapper function:
#    * Test whether the passed mandatory "hint" parameter (trivially accessible
#      via this closure constant providing its 0-based index in "*args") is an
#      instance of "beartype.cave.HintGenericSubscriptedType". Do *NOT* bother calling the
#      higher-level is_hint_pep585_builtin() tester. Speed is of the essence here.
#    * If so, replace this parameter in the "*args" tuple with the repr() for
#      this parameter. Naturally, this (probably) requires inefficiently
#      reconstructing the entire "*args" tuple. What can you do? Note that this
#      has the significant advantage of making unhashable hints hashable.
#    * Else, behave as normal.
#* Hmmm. Actually, the prior note brings up a salient point: using the repr()
#  for hints rather than actual hints trivially resolves hashability concerns.
#  Rather than the current conditional approach, it might actually be faster to
#  refactor the @callable_cached_hintable decorator to:
#  * Drop all support for unhashable parameters.
#  * Unconditionally replace the value of the passed mandatory "hint" parameter
#    in "*args" with its repr() for purposes of memoization. Obviously, the
#    actual value should still be passed to the decorated callable.
#* Grep the codebase for all existing uses of the @callable_cached decorator.
#* For use such use, if the decorated callable accepts a "hint" parameter,
#  refactor that callable to use @callable_cached_hintable instead.
#FIXME: *YIKES!* We are incredibly thankful we didn't actually do any of the
#above, but everything above is absolutely the *WRONG* approach. Yes, it would
#technically work, but it would be considerably slower, more fragile, and
#require considerably more work across the codebase than the preferable
#approach delineated below -- which is to say, everything above is bad.
#
#So, how do we do this the right way? *SIMPLE.* We "patch up" PEP 585-compliant
#type hints directly in the "func.__annotations__" dictionary once and only
#once sufficiently early in @beartype decoration that we don't actually need to
#do anything else, where "patch up" means:
#* If passed a callable decorated by a PEP 585-compliant type hint whose
#  repr() is something that we've already seen, we *REPLACE* that hint in that
#  callable's "func.__annotations__" dictionary with the hint we already saw.
#
#To do so, we should probably:
#* In the "beartype._decor._cache.cachehint" submodule:
#  * Any hint that appears in that cache should be *REPLACED* where it appears
#    in the "func.__annotations__" dictionary with its cached value. Sweeeeeet.
#* Cache deferred annotations in the "beartype._decor._pep563" submodule. To do
#  so, we probably want to define a new cache_hint_pep563() function in the new
#  "beartype._decor._cache.cachehint" submodule. Note this function should
#  internally defer to the new cache_hint_nonpep563() function detailed below
#  (e.g., to ensure tuple unions are cached as typing unions).
#* Cache PEP 563 annotations in the "beartype._decor._code.codemain" or
#  possibly "beartype._decor._code._pep.pepcode" submodule. *AHAH!* Yes. Here's
#  what we want to do:
#  * Shift the existing beartype._decor._code.pepcode.coerce_hint_pep()
#    function into the new "beartype._decor._cache.cachehint" submodule as a
#    new cache_hint_nonpep563() function. Note that if the passed hint was
#    previously deferred and thus cached by a prior call to the
#    cache_hint_pep563() function, then the current call to the
#    cache_hint_nonpep563() function should just reduce to a noop.
#FIXME: *UNIT TEST THIS CACHE AND MAKE SURE IT ACTUALLY WORKS* for both PEP
#585- and 563-compliant hints, which are the principle use cases.

#FIXME: *WOOPS.* The "LRUDuffleCacheStrong" class designed below assumes that
#calculating the semantic height of a type hint (e.g., 3 for the complex hint
#Optional[int, dict[Union[bool, tuple[int, ...], Sequence[set]], list[str]])
#is largely trivial. It isn't -- at all. Computing that without a context-free
#recursion-esque algorithm of some sort is literally infeasible. We absolutely
#*MUST* get that height right, since we'll be exponentiating that height to
#estimate space consumption of arbitrary objects. Off-by-one errors are
#unacceptable when the difference between a height of 2 and a height of 3 means
#tens of thousands in additional estimated space consumption.
#
#So. How do we do this, then? *SIMPLE.* Okay, not simple -- but absolutely
#beneficial for a medley of unrelated pragmatic reasons and thus something we
#need to pursue anyway regardless of the above concerns.
#
#The solution is to make the breadth-first search (BFS) internally performed
#by the pep_code_check_hint() function below more recursion-esque. We will
#*NOT* be refactoring that function to leverage:
#
#* Recursion rather than iteration for all of the obvious reasons.
#* A stack-like depth-first search (DFS) approach. While implementing a DFS
#  with iteration can technically be done, doing so imposes non-trivial
#  technical constraints because you then need to store interim results (which
#  in a proper recursive function would simply be local variables) as you
#  iteratively complete each non-leaf node. That's horrifying. So, we'll be
#  preserving our breadth-first search (BFS) approach. The reason why a BFS is
#  often avoided in the real world are space concerns: a BFS consumes
#  significantly more space than a comparable DFS, because:
#  * The BFS constructs the entire tree before operating on that tree.
#  * The DFS only constructs a vertical slice of the entire tree before
#    operating only on that slice.
#  In our case, however, space consumption of a BFS versus DFS is irrelevant.
#  Why? Because type hints *CANNOT* be deeply nested without raising recursion
#  limit errors from deep within the CPython interpreter, as we well know.
#  Ergo, a BFS will only consume slightly more temporary space than a DFS. This
#  means a "FixedList" of the same size trivially supports both.
#
#First, let's recap what we're currently doing:
#
#* In a single "while ...:" loop, we simultaneously construct the BFS tree
#  (stored in a "FixedList" of tuples) *AND* output results from that tree as
#  we are dynamically constructing it.
#
#The "simultaneously" is the problem there. We're disappointed we didn't
#realize it sooner, but our attempt to do *EVERYTHING* in a single pass is why
#we had such extraordinary difficulties correctly situating code generated by
#child type hints into the code generated for parent type hints. We
#circumvented the issue by repeatedly performing a global search-and-replace on
#the code being generated, which is horrifyingly inefficient *AND* error-prone.
#We should have known then that something was wrong. Sadly, we proceeded.
#
#Fortunately, this is the perfect moment to correct our wrongs -- before we
#proceed any deeper into a harmful path dependency. How? By splitting our
#current monolithic BFS algorithm into two disparate BFS phases -- each
#mirroring the behaviour of a recursive algorithm:
#
#1. In the first phase, a "while ...:" loop constructs the BFS tree by
#   beginning at the root hint, iteratively visiting all child hints, and
#   inserting metadata describing those hints into our "hints_meta" list as we
#   currently do. That's it. That's all. But that's enough. This construction
#   then gives us efficient random access over the entire type hinting
#   landscape, which then permits us to implement the next phase -- which does
#   the bulk of the work. To do so, we'll add additional metadata to our
#   current "hint_meta" tuple: e.g.,
#   * "_HINT_META_INDEX_CHILD_FIRST_INDEX", the 0-based index into the
#     "hints_meta" FixedList of the first child hint of the current hint if any
#     *OR* "None" otherwise. Since this is a BFS, that child hint could appear
#     at any 0-based index following the current hint; finding that child hint
#     during the second phase thus requires persisting the index of that hint.
#     Note that the corresponding index of the last child hint of the current
#     hint need *NOT* be stored, as adding the length of the argument list of
#     the current hint to the index of the first child hint trivially gives the
#     index of the last child hint.
#   * "_HINT_META_INDEX_CODE", the Python code snippet type-checking the
#     current hint to be generated by the second phase.
#   * "_HINT_META_INDEX_HEIGHT", the 1-based height of the current hint in this
#     BFS tree. Leaf nodes have a height of 1. All non-leaf nodes have a height
#     greater than 1. This height *CANNOT* be defined during the first phase
#     but *MUST* instead be deferred to the second phase.
#   * ...probably loads more stuff, but that's fine.
#2. In the second phase, another "while ...:" loop generates a Python code
#   snippet type-checking the root hint and all child hints visitable from that
#   hint in full by beginning *AT THE LAST CHILD HINT ADDED TO THE*
#   "hints_meta" FixedList, generating code type-checking that hint,
#   iteratively visiting all hints *IN THE REVERSE DIRECTION BACK UP THE TREE*,
#   and so on.
#
#That's insanely swag. It shames us that we only thought of it now. *sigh*
#FIXME: Note that this new approach will probably (hopefully only slightly)
#reduce decoration efficiency. This means that we should revert to optimizing
#the common case of PEP-noncompliant classes. Currently, we uselessly iterate
#over these classes with the same BFS below as we do PEP-compliant classes --
#which is extreme overkill. This will be trivial (albeit irksome) to revert,
#but it really is fairly crucial. *sigh*
#FIXME: Now that we actually have an audience (yay!), we *REALLY* need to avoid
#breaking anything. But implementing the above refactoring would absolutely
#break everything for an indeterminate period of time. So how do we do this?
#*SIMPLE*. We leave this submodule as is *UNTIL* our refactoring passes tests.
#In the meanwhile, we safely isolate our refactoring work to the following new
#submodules:
#* "_pephinttree.py", implementing the first phase detailed above.
#* "_pephintgene.py", implementing the second phase detailed above.
#
#To test, we locally change a simple "import" statement in the parent
#"_pepcode" submodule and then revert that import before committing. Rinse
#until tests pass, which will presumably take several weeks at least.
#FIXME: Note that there exists a significant optimization that we *ABSOLUTELY*
#should add to these new modules. Currently, the "hints_meta" data structure is
#represented as a FixedList of size j, each item of which is a k-length tuple.
#If you briefly consider it, however, that structure could equivalently be
#represented as a FixedList of size j * k, where we simply store the items
#previously stored in each k-length tuple directly in that FixedList itself.
#
#Iterating forward and backward by single hints over that FixedList is still
#trivial. Rather than incrementing or decrementing an index by 1, we instead
#increment or decrement an index by k.
#
#The resulting structure is guaranteed to be considerably more space-efficient,
#due to being both contiguous in memory and requiring only a single object
#(and thus object dictionary) to maintain. Cue painless forehead slap.

#FIXME: Add support for "PEP 586 -- Literal Types". Sadly, doing so will be
#surprisingly non-trivial.
#
#First, note that the user-defined literal object defined by a "typing.Literal"
#hint is available as "hint.__args__[0]". That is, such hints *ALWAYS* have
#exactly one child hint which is the user-defined literal object.
#
#Second, note that mutable objects are *NOT* hashable. So, registering these
#objects with the "beartypistry" is *NOT* a valid generic solution. That said,
#we *COULD* technically still do so for the subset of literal objects that are
#hashable -- which will probably be most of them, actually. To do so, we would
#then define a new beartype._decor._cache.cachetype.register_hashable() function
#registering a generic hashable. This would then necessitate a new prefix
#unique to hashables (e.g., "h"). In short, this actually entails quite a bit
#of work and fails in the general case. So, we might simply avoid this for now.
#
#Third, note that one approach would be to augment the breadth-first search
#performed below to record the "hint_path" used to access the currently visited
#and possibly nested hint from the universally accessible
#"__beartype_func.__annotations__[{param_name}]". This is obviously *NOT* the
#optimally efficient approach, as this will entail multiple dictionary lookups
#to type-check each literal object. Nonetheless, this is absolutely the
#simplest approach and thus probably the one we should at least initially
#pursue. Why? Because literal objects are unlikely to be used much (if at all)
#in practical real-world applications. We certainly can't think of a single
#valid use case ourselves. Literal objects are an obvious "code smell." If your
#callable unconditionally accepts or returns an object, why even go to the
#trouble of accepting or returning that object in the first place, right? So,
#efficiency is *ABSOLUTELY* not a concern here.
#
#The issue, of course, is that we currently do *NOT* record the "hint_path"
#used to access the currently visited and possibly nested hint from the
#universally accessible "__beartype_func.__annotations__[{param_name}]". Doing
#so will probably prove annoying and possibly non-trivial. Since we might need
#to refactor quite a bit to do that and would increase the space complexity of
#this algorithm by a little bit as well, we might consider alternatives.
#
#The obvious alternative is to refactor the pep_code_check_hint() function to
#instead return the 3-tuple "Tuple[str, bool, Tuple[object]]" rather than the
#2-tuple "Tuple[str, bool]" as we currently do. The new third item of that
#3-tuple "Tuple[object]" is, of course, the tuple listing all user-defined
#literal objects (i.e., "hint.__args__[0]" objects) such that the 0-based index
#in this list of each such object is the breadth-first visitation order in
#which this submodule discovers that object. Consider the callable with
#signature:
#      def muh_func(muh_param: Union[
#          Literal[True],
#          Tuple[str, List[Literal['ok']]],
#          Sequence[Literal[5]],
#      ]) -> Literal[23.35]: pass
#
#The third item of the tuple returned by the pep_code_check_hint() function
#would then be the following tuple:
#      (True, 5, 'ok',)
#
#Note the unexpected breadth-first ordering and omission of the "23.35" return
#value literal. In any case, parent functions would then be responsible for
#aggregating all literal object tuples returned by all calls to the
#pep_code_check_hint() function for the decorated callable into a new
#"data.func.__beartype_param_name_to_literals" dictionary mapping from the
#name of each passed parameter as well as "return" for the return value to the
#tuple returned by the pep_code_check_hint() function for that parameter.
#
#Given that, the pep_code_check_hint() function may then safely and reasonably
#efficiently access each parameter-specific literal in breadth-first visitation
#order with a placeholder expression resembling:
#
#    PEP586_CODE_PARAM_LITERAL_EXPR = (
#        '''__beartype_func.__beartype_param_name_to_literals[PEP_CODE_PITH_ROOT_PARAM_NAME_PLACEHOLDER][{literal_curr_index}]''')
#    '''
#    `PEP 586`_-compliant Python expression yielding the literal object subscripting
#    a possibly nested :attr:`typing.Literal` type hint annotated by the current
#    parameter or return value.
#
#    .. _PEP 586:
#       https://www.python.org/dev/peps/pep-0586
#    '''
#
#This works, because "PEP_CODE_PITH_ROOT_PARAM_NAME_PLACEHOLDER" will be
#globally replaced by the caller with the code-safe name of this parameter or
#return value. Pretty sweet, yah? There's basically *NO* other way to
#reasonably render literal objects accessible. This is sufficiently efficient
#for these bizarre edge-case objects that this will suffice for all time.
#FIXME: Oh, boy. So, we were *REALLY* overthinking things above -- all of which
#should simply be ignored. Adding "typing.Literal" is actually trivial. Why?
#Because object identifiers are both unique and trivially hashable. This means
#the hashability of literal objects themselves is irrelevant. We only need to
#map the object identifiers for literal objects to those objects. That's it.
#Now, there are numerous valid ways to go about that, including:
#* Registering literal objects with the beartypistry, presumably in a format
#  resembling f'l{literal_id}'. Technically, this works. But it's also
#  suboptimal, because it requires:
#  * Polluting the beartypistry with even less relevant keys, which impacts
#    runtime performance for other unrelated objects accessed via the
#    beartypistry.
#  * At least one more dictionary lookup than necessary.
#* One new default parameter passed to the decorated callable for each literal
#  object annotating that callable with name formatted for uniqueness ala
#  f'__beartype_literal_{literal_id}'. This is, of course, feasible. Note,
#  however, that we'd eventually like to entirely obsolete *ALL* usage of
#  beartype-specific default parameters. Why? Because:
#  * They're incompatible with parameter-preservation. We'd eventually like the
#    function wrappers generated by @beartype to perfectly masquerade as their
#    decorated callables, which mostly means perfectly replicating the original
#    signature of those decorated callables.
#  * They obstruct runtime introspection. Imagine attempting to dynamically
#    call function wrappers generated by @beartype with clever automation.
#    Currently, that basically can't happen. That's bad. Quite bad, actually.
#  * They enable callers to maliciously override beartype-specific default
#    parameters. Of course, it's unclear why anyone would want to do that --
#    but the mere fact that they can should be enough to make anyone
#    uncomfortable with the current approach.
#  * They possibly impose a non-negligible space and time cost. Currently, we
#    only pass two default parameters; that's probably negligible. But as soon
#    as we start scaling that up to an arbitrary number of default parameters,
#    it becomes likely that non-negligible space and time costs will appear.
#* One new global variable defined in the global scope specific to the
#  decorated callable for each literal object annotating that callable with
#  name formatted for uniqueness ala f'__beartype_literal_{literal_id}'. *THIS
#  IS THE WAY FORWARD.* In fact, this is the way forward for literally (pun!)
#  everything, including:
#  * The decorated callable. We currently pass the decorated callable as the
#    "__beartype_func" default parameter. Instead, that callable be should be
#    declared as a "__beartype_func" global variable.
#  * The beartypistry itself, for identical reasons. This declaration should be
#    made conditional on whether the function wrapper actually requires the
#    beartypistry. Callables annotated only by builtin types (e.g., int, str),
#    do *NOT* require the beartypistry, for example.
#  * Types and tuples of types currently registered with the beartypistry.
#    Eventually, the only remaining use for the beartypistry will be forward
#    references. There's really no other reasonable way to support forward
#    references, which is fine. It would sadden us to kill off the beartypistry
#    entirely, given the effort we've invested in it. Note that:
#    * Types should be declared as "__beartype_type_{class_id}" global
#      variables, where "{class_id}" is the object id of that class. Note this
#      trivially circumvents ambiguity issues with fully-qualified classnames
#      that would otherwise clash (e.g., "org.MuhType" versus "org_MuhType").
#    * Tuples of types should pursue a hybrid approach and:
#      * Continue to be *REGISTERED* (basically, cached) at decoration time
#        with the beartypistry as they currently are. The reason for this, of
#        course, is to minimize space consumption for tuples auto-coerced from
#        the same "Union" type hints nested at different nesting levels. No
#        such issue exists for classes, of course.
#      * Declared and accessed at call time as "__beartype_tuple_{tuple_id}"
#        global variables, where "{tuple_id}" is the object id of that tuple.
#        This maximizes call time efficiency by avoiding dictionary lookups.
#  Implementing this will require refactoring not only this function but the
#  entire tree of function calls leading to this function. Why? Because we'll
#  need to percolate up the tree the following additional metadata as
#  additional return values:
#      global_var_name_to_value: Dict[str, object]
#
#  Obviously, that is a dictionary mapping from the unique name to value of
#  each callable-specific global variable that should be declared by the
#  top-level @beartype() decorator function generating the wrapper function.
#  Specifically:
#
#  * The pep_code_check_hint() function below should be refactored to:
#    * Locally declare a new "global_var_name_to_value" local dictionary,
#      initialized to the empty dictionary. Although this local *COULD* also be
#      initialized to "None", that would be a bit silly and complicate
#      everything in the common case, as most calls to this function will be
#      adding one or more globals to this dictionary. Oh, wait... perhaps it
#      should be initialized to "None" after all, to minimize space consumption
#      due to memoization. Sure. Whatevahs! In that case, we want to also
#      define:
#      * A new local _register_type() closure resembling the current
#        _typistry.register_type() function.
#      * A new local _register_tuple() closure resembling the current
#        _typistry.register_tuple() function. Tuples of types are particularly
#        complicated, thanks to continued caching under the beartypistry.
#    * Return this dictionary as yet another return value.
#  * The beartype._decor.main.beartype() function should be refactored to:
#    * Define these new local variables:
#      * "global_attrs", the dictionary mapping from the names to values of all
#        global variables required by the decorated callable. Initialized to
#        either "None" or the empty dictionary.
#      * "global_attrs_func", the dictionary mapping from the names to values
#        of all global variables conditionally required by this decorated
#        callable specifically. Note that it is explicitly permissible for this
#        dictionary to be empty (e.g., when type hints annotating the decorated
#        callable are all builtin types).
#    * Set "global_attrs_func" to the "global_var_name_to_value" value returned
#      by the generate_code() function.
#    * Set "global_attrs" to the dynamic merger of the "_GLOBAL_ATTRS" global
#      dictionary constant with the "global_attrs_func" dictionary local. We
#      probably want to code this mildly carefully. Efficiency is slightly less
#      critical here than robustness, as this is decoration time. In
#      particular, we'll want to ensure that:
#      * The "_GLOBAL_ATTRS" and "global_attrs_func" dictionaries do *NOT*
#        collide (i.e., have no keys in common). An exception should be raised
#        when this is the case, as that would indicate a critical low-level
#        @beartype issue.
#      * The "__beartype_func" global variable be added to either the
#        "global_attrs_func" *OR* "global_attrs" dictionaries. It doesn't
#        particularly matter which, so whichever is easier and faster is it.
#    * Pass "global_attrs" rather than "_GLOBAL_ATTRS" to the exec() call.
#
#That's it! We'll be hitting two birds with one stone here, so that makes this
#a fairly fun step forwards -- even if "typing.Literal" itself is rather
#inconsequential in the grand scheme of things. Yum.

#FIXME: Significant optimizations still remain... when we have sufficient time.
#Notably, we can replace most existing usage of the generic private
#"__beartypistry" parameter unconditionally passed to all wrapper functions
#with specific private "__beartype_hint_{beartypistry_key}" parameters
#conditionally passed to each individual wrapper function, where:
#* "{beartypistry_key}" signifies an existing string key of the "bear_typistry"
#  singleton dictionary munged so as to produce a valid Python identifier.
#  Notably:
#  * Rather than use the fully-qualified names of types as we currently do,
#    we'll instead need to use their hashes. Why? Because Python identifiers
#    accept a sufficiently small set of permissible characters that there is
#    *NO* character we could possibly globally replace all "." characters in a
#    fully-qualified classname with to produce a disambiguous Python
#    identifier. Consider, for example, the two distinct classnames
#    "muh_package.muh_module.MuhClass" and
#    "muh_package_muh_module.MuhClass". Replacing "." characters with "_"
#    characters in both would produce the same munged Python identifier
#    "muh_package_muh_module_MuhClass" -- an ambiguous collision. Ergo, hashes.
#  * Hashes appear to be both negative and positive. So, we'll probably need to
#    replace "-" substrings prefixing "str(hash(hint))" output with something
#    sane complying with Python identifiers -- say, the "n" character. *shrug*
#* "__beartype_hint_{beartypistry_key}" signifies a parameter name whose value
#  defaults to either a type or tuple of types required by this wrapper
#  function.
#
#For example, if a function internally requires a "muh_package.MuhClass" class,
#we would then generate wrapper functions resembling:
#
#    def muh_wrapper(
#        *args,
#        __beartype_func=__beartype_func,
#        __beartype_hint_24234234240=__beartype_hint_24234234240,
#    )
#
#...where "__beartype_hint_24234234240" would need to be defined within the
#locals() dictionary passed to the exec() builtin by the "beartype._decor.main"
#submodule to refer to the "muh_package.MuhClass" class: e.g.,
#
#    # In "beartype._decor.main":
#    local_vars = {
#        __beartype_hint_24234234240: muh_package.MuhClass,
#    }
#
#Why is this so much more efficient than the current approach? Because lookups
#into large dictionaries inevitably have non-negligible constants, whereas
#exploiting default function parameters *IS LITERALLY INSTANTEOUS.* Why?
#Because Python actually stores function defaults in a tuple at function
#declaration time, thus minimizing both space and time costs: e.g.,
#    # It doesn't get faster than this, folks.
#    >>> def defjam(hmm, yum='Yum!', oko='Kek!'): pass
#    >>> defjam.__defaults__
#    ('Yum!', 'Kek!')
#
#Clearly, we'll need to carefully consider how we might efficiently percolate
#that metadata up from this breadth-first traversal to that top-level module.
#Presumably, we'll want to add a new data structure to the "BeartypeData"
#object -- say, a new "BeartypeData.param_name_to_value" dictionary mapping
#private parameter names to values to be passed to the current wrapper.
#
#Note that we should still cache at least tuples in the "bear_typistry"
#singleton dictionary to reduce space consumption for different tuple objects
#containing the same types, but that we should no longer look those tuples up
#in that dictionary at runtime from within wrapper functions.
#FIXME: Most of the prior "FIXME:" is now obsolete. See the "typing.Literal"
#discussion for the real optimal approach: callable-specific global variables.

#FIXME: Note that there exist four possible approaches to random item selection
#for arbitrary containers depending on container type. Either the actual pith
#object (in descending order of desirability):
#* Satisfies "collections.abc.Sequence" (*NOTE: NOT* "typing.Sequence", as we
#  don't particularly care how the pith is type-hinted for this purpose), in
#  which case the above approach trivially applies.
#* Else is *NOT* a one-shot container (e.g., generator and... are there any
#  other one-shot container types?) and is *NOT* slotted (i.e., has no
#  "__slots__" attribute), then generalize the mapping-specific
#  _get_dict_nonempty_random_key() approach delineated below.
#* Else is *NOT* a one-shot container (e.g., generator and... are there any
#  other one-shot container types?) but is slotted (i.e., has a "__slots__"
#  attribute), then the best we can do is the trivial O(1) approach by
#  calling "{hint_child_pith} := next({hint_curr_pith})" to unconditionally
#  check the first item of this container. What you goin' do? *shrug* (Note
#  that we could try getting around this with a global cache of weak references
#  to iterators mapped on object ID, but... ain't nobody got time or interest
#  for that. Also, prolly plenty dangerous.)
#* Else is a one-shot container, in which case *DO ABSOLUTELY NUTHIN'.*
#FIXME: We should ultimately make this user-configurable (e.g., as a global
#configuration setting). Some users might simply prefer to *ALWAYS* look up a
#fixed 0-based index (e.g., "0", "-1"). For the moment, however, the above
#probably makes the most sense as a reasonably general-purpose default.

#FIXME: Note that randomly checking mapping (e.g., "dict") keys and/or values
#will be non-trivial, as there exists no out-of-the-box O(1) approach in either
#the general case or the specific case of a "dict". Actually, there does -- but
#we'll need to either internally or externally maintain one dict.items()
#iterator for each passed mapping. We should probably investigate the space
#costs of that *BEFORE* doing so. Assuming minimal costs, one solution under
#Python >= 3.8 might resemble:
#* Define a new _get_dict_random_key() function resembling:
#      def _get_dict_nonempty_random_key(mapping: MappingType) -> object:
#          '''
#          Caveats
#          ----------
#          **This mapping is assumed to be non-empty.** If this is *not* the
#          case, this function raises a :class:`StopIteration` exception.
#          '''
#          items_iter = getattr(mapping, '__beartype_items_iter', None)
#          if items_iter is None:
#              #FIXME: This should probably be a weak reference to prevent
#              #unwanted reference cycles and hence memory leaks.
#              #FIXME: We need to protect this both here and below with a
#              #"try: ... except Exception: ..." block, where the body of the
#              #"except Exception:" condition should probably just return
#              #"beartype._util.utilobject.SENTINEL", as the only type hints
#              #that would ever satisfy are type hints *ALL* objects satisfy
#              #(e.g., "Any", "object").
#              mapping.__beartype_items_iter = iter(mapping.items())
#          try:
#              return next(mapping.__beartype_items_iter)
#          # If we get to the end (i.e., the prior call to next() raises a
#          # "StopIteration" exception) *OR* anything else happens (i.e., the
#          # prior call to next() raises a "RuntimeError" exception due to the
#          # underlying mapping having since been externally mutated), just
#          # start over. :p
#          except Exception:
#              mapping.__beartype_items_iter = None
#
#              # We could also recursively call ourselves: e.g.,
#              #     return _get_dict_random_key(mapping)
#              # However, that would be both inefficient and dangerous.
#              mapping.__beartype_items_iter = iter(mapping.items())
#              return next(mapping.__beartype_items_iter)
#* In "beartype._decor._main":
#     import _get_dict_nonempty_random_key as __beartype_get_dict_nonempty_random_key
#* In code generated by this submodule, internally call that helper when
#  checking keys of non-empty mappings *THAT ARE UNSLOTTED* (for obvious
#  reasons) ala:
#  (
#     {hint_curr_pith} and
#     not hasattr({hint_curr_pith}, '__slots__') and
#     {!INSERT_CHILD_TEST_HERE@?(
#         {hint_child_pith} := __beartype_get_dict_nonempty_random_key({hint_curr_pith}))
#  )
#  Obviously not quite right, but gives one the general gist of the thing.
#
#We could get around the slots limitation by using an external LRU cache
#mapping from "dict" object ID to items iterator, and maybe that *IS* what we
#should do. Actually... *NO.* We absolutely should *NOT* do that sort of thing
#anywhere in the codebase, as doing so would guaranteeably induce memory leaks
#by preventing "dict" objects cached in that LRU from being garbage collected.
#
#Note that we basically can't do this under Python < 3.8, due to the lack of
#assignment expressions there. Since _get_dict_nonempty_random_key() returns a
#new random key each call, we can't repeatedly call that for each child pith
#and expect the same random key to be returned. So, Python >= 3.8 only. *shrug*
#
#Note that the above applies to both immutable mappings (i.e., objects
#satisfying "Mapping" but *NOT* "MutableMapping"), which is basically none of
#them, and mutable mappings. Why? Because we don't particularly care if the
#caller externally modifies the underlying mapping between type-checks, even
#though the result is the above call to "next(mapping.__beartype_items_iter)"
#raising a "RuntimeError". Who cares? Whenever an exception occurs, we just
#restart iteration over from the beginning and carry on. *GOOD 'NUFF.*
#FIXME: *YIKES.* So, as expected, the above approach fundamentally fails on
#builtin dicts and sets. Why? Because *ALL* builtin types prohibit
#monkey-patching, which the above technically is. Instead, we need a
#fundamentally different approach.
#
#That approach is to globally (but thread-safely, obviously) cache *STRONG*
#references to iterators over dictionary "ItemsView" objects. Note that we
#can't cache weak references, as the garbage collector would almost certainly
#immediately dispose of them, entirely defeating the point. Of course, these
#references implicitly prevent garbage collection of the underlying
#dictionaries, which means we *ALSO* need a means of routinely removing these
#references from our global cache when these references are the only remaining
#references to the underlying dictionaries. Can we do any of this? We can.
#
#First, note that we can trivially obtain the number of live references to any
#arbitrary object by calling "sys.getrefcount(obj)". Note, however, that the
#count returned by this function is mildly non-deterministic. In particular,
#off-by-one issues are not merely edge cases but commonplace. Ergo:
#
#    from sys import getrefcount
#
#    def is_obj_nearly_dead(obj: object) -> bool:
#        '''
#        ``True`` only if there only exists one external strong reference to
#        the passed object.
#        '''
#
#        # Note that the integer returned by this getter is intentionally *NOT*
#        # tested for equality with "1". Why? Because:
#        # * The "obj" parameter passed to this tester is an ignorable strong
#        #   reference to this object.
#        # * The "obj" parameter passed to the getrefcount() getter is yet
#        #   another strong reference to this object.
#        return getrefcount(obj) <= 3
#
#Second, note that neither the iterator API nor the "ItemsView" API provide a
#public means of obtaining a strong reference to the underlying dictionary.
#This means we *MUST* necessarily maintain for each dictionary a 2-tuple
#"(mapping, mapping_iter)", where:
#* "mapping" is a strong reference to that dictionary.
#* "mapping_iter" is an iterator over that dictionary's "ItemsView" object.
#
#This implies that we want to:
#* Define a new "beartype._util.cache.utilcachemapiter" submodule.
#* In that submodule:
#  * Define a new global variable resembling:
#      # Note that this is unbounded. There's probably no reasonable reason to
#      # use an LRU-style bounded cache here... or maybe there is for safety to
#      # avoid exhausting memory. Right.
#      #
#      # So, this should obviously be LRU-bounded at some point. Since Python's
#      # standard @lru decorator is inefficient, we'll need to build that our
#      # ourselves, which means this is *NOT* an immediate priority.
#      _MAP_ITER_CACHE = {}
#      '''
#      Mapping from mapping identifiers to 2-tuples
#      ``(mapping: Mapping, mapping_iter: Iterator)``,
#      where ``mapping`` is a strong reference to the mapping whose key is that
#      mapping's identifier and ``mapping_iter`` is an iterator over that
#      mapping's ``ItemsView`` object.
#      '''
#  * Define a new asynchronous cleanup_cache() function. See the
#    cleanup_beartype() function defined below for inspiration.
#* Extensively unit test that submodule.
#
#Third, note that this means the above is_obj_nearly_dead() fails to apply to
#this edge case. In our case, a cached dictionary is nearly dead if and only if
#the following condition applies:
#
#    def is_cached_mapping_nearly_dead(mapping: Mapping) -> bool:
#        '''
#        ``True`` only if there only exists one external strong reference to
#        the passed mapping internally cached by the :mod:`beartype.beartype`
#        decorator.
#        '''
#
#        # Note that the integer returned by this getter is intentionally *NOT*
#        # tested for equality with "1". Why? Because ignorable strong
#        # references to this mapping include:
#        # * The "mapping" parameter passed to this tester.
#        # * The "mapping" parameter passed to the getrefcount() getter.
#        # * This mapping cached by the beartype-specific global container
#        #   caching these mappings.
#        # * The iterator over this mapping cached by the same container.
#        return getrefcount(mapping) <= 5   # <--- yikes!
#
#Fourth, note that there are many different means of routinely removing these
#stale references from our global cache (i.e., references that are the only
#remaining references to the underlying dictionaries). For example, we could
#routinely iterate over our entire cache, find all stale references, and remove
#them. This is the brute-force approach. Of course, this approach is both slow
#and invites needlessly repeated work across repeated routine iterations. Ergo,
#rather than routinely iterating *ALL* cache entries, we instead only want to
#routinely inspect a single *RANDOM* cache entry on each scheduled callback of
#our cleanup routine. This is the O(1) beartype approach and still eventually
#gets us where we want to go (i.e., complete cleanup of all stale references)
#with minimal costs. A random walk wins yet again.
#
#Fifth, note that there are many different means of routinely scheduling work.
#We ignore the existence of the GIL throughout the following discussion, both
#because we have no choice *AND* because the randomized cleanup we need to
#perform on each scheduled callback is an O(1) operation with negligible
#constant factors and thus effectively instantaneous rather than CPU- or
#IO-bound. The antiquated approach is "threading.Timer". The issue with the
#entire "threading" module is that it is implemented with OS-level threads,
#which are ludicrously expensive and thus fail to scale. Our usage of the
#"threading" module in beartype would impose undue costs on downstream apps by
#needlessly consuming a precious thread, preventing apps from doing so. That's
#bad. Instead, we *MUST* use coroutines, which are implemented in Python itself
#rather than exposed to the OS and thus suffer no such scalability concerns,
#declared as either:
#* Old-school coroutines via the @asyncio.coroutine decorator. Yielding under
#  this approach is trivial (and possibly more efficient): e.g.,
#       yield
#* New-school coroutines via the builtin "async def" syntax. Yielding under
#  this approach is non-trivial (and possibly less efficient): e.g.,
#       await asyncio.sleep_ms(0)
#
#In general, the "async def" approach is strongly favoured by the community.
#Note that yielding control in the "async def" approach is somewhat more
#cumbersome and possibly less efficient than simply performing a "yield".
#Clearly, a bit of research here is warranted. Note this online commentary:
#    In performance-critical code yield does offer a small advantage. There are
#    other tricks such as yielding an integer (number of milliseconds to
#    pause). In the great majority of cases code clarity trumps the small
#    performance gain achieved by these hacks. In my opinion, of course.
#
#In either case, we declare an asynchronous coroutine. We then need to schedule
#that coroutine with the global event loop (if any). The canonical way of doing
#this is to:
#* Pass our "async def" function to the asyncio.create_task() function.
#  Although alternatives exist (e.g., futures), this function is officially
#  documented as being the preferred approach:
#    create_task() (added in Python 3.7) is the preferable way for spawning new
#    tasks.
#  Of course, note this requires Python >= 3.7. We could care less. *shrug*
#* Pass that task to the asyncio.run() function... or something, something.
#  Clearly, we still need to research how to routinely schedule that task with
#  "asyncio" rather than running it only once. In theory, that'll be trivial.
#
#Here's a simple example:
#
#    async def cleanup_beartype(event_loop):
#        # Disregard how simple this is, it's just for example
#        s = await asyncio.create_subprocess_exec("ls", loop=event_loop)
#
#    def schedule_beartype_cleanup():
#        event_loop = asyncio.get_event_loop()
#        event_loop.run_until_complete(asyncio.wait_for(
#            cleanup_beartype(event_loop), 1000))
#
#The above example was culled from this StackOverflow post:
#    https://stackoverflow.com/questions/45010178/how-to-use-asyncio-event-loop-in-library-function
#Unlike the asyncio.create_task() approach, that works on Python >= 3.6.
#Anyway, extensive research is warranted here.
#
#Sixthly, note that the schedule_beartype_cleanup() function should be called
#only *ONCE* per active Python process by the first call to the @beartype
#decorator passed a callable annotated by one or more "dict" or
#"typing.Mapping" type hints. We don't pay these costs unless we have to. In
#particular, do *NOT* unconditionally call the schedule_beartype_cleanup()
#function on the first importation of the "beartype" package.
#
#Lastly, note there technically exists a trivial alternative to the above
#asynchronous approach: the "gc.callbacks" list, which allows us to schedule
#arbitrary user-defined standard non-asynchronous callback functions routinely
#called by the garbage collector either immediately before or after each
#collection. So what's the issue? Simple: end users are free to either
#explicitly disable the garbage collector *OR* compile or interpreter their
#apps under a non-CPython executable that does not perform garbage collection.
#Ergo, this alternative fails to generalize and is thus largely useless.
#FIXME: Actually... let's not do the "asyncio" approach -- at least not
#initially. Why? The simplest reason is that absolutely no one expects a
#low-level decorator to start adding scheduled asynchronous tasks to the global
#event loop. The less simple reason is that doing so would probably have
#negative side effects to at least one downstream consumer, the likes of which
#we could never possibly predict.
#
#So, what can we do instead? Simple. We do this by:
#* If garbage collection is enabled, registering a new cleanup callback with
#  "gc.callbacks".
#* Else, we get creative. First, note that garbage collection is really only
#  ever disabled in the real world when compiling Python to a lower-level
#  language (typically, C). Ergo, efficiency isn't nearly as much of a concern
#  in this currently uncommon edge case. So, here's what we do:
#  * After the first call to the @beartype decorator passed a callable
#    annotated by one or more mapping or set type hints, globally set a private
#    "beartype" boolean -- say, "WAS_HINT_CLEANABLE" -- noting this to have
#    been the case.
#  * In the _code_check_params() function generating code type-checking *ALL*
#    annotated non-ignorable parameters:
#    * If "WAS_HINT_CLEANABLE" is True, conditionally append code calling our
#      cleanup routine *AFTER* code type-checking these parameters. While
#      mildly inefficient, function calls incur considerably less overhead
#      when compiled away from interpreted Python bytecode.
#FIXME: Note that the above scheme by definition *REQUIRES* assignment
#expressions and thus Python >= 3.8 for general-purpose O(1) type-checking of
#arbitrarily nested dictionaries and sets. Why? Because each time we iterate an
#iterator over those data structures we lose access to the previously iterated
#value, which means there is *NO* sane means of type-checking nested
#dictionaries or sets without assignment expressions. But that's unavoidable
#and Python <= 3.7 is the past, so that's largely fine.
#
#What we can do under Python <= 3.7, however, is the following:
#* If the (possibly nested) type hint is of the form
#  "{checkable}[...,{dict_or_set}[{class},{class}],...]" where
#  "{checkable}" is an arbitrary parent type hint safely checkable under Python
#  <= 3.7 (e.g., lists, unions), "{dict_or_set}" is (wait for it) either "dict"
#  or "set", and "{class}" is an arbitrary type, then that hint *IS* safely
#  checkable under Python <= 3.7. Note that items (i.e., keys and values) can
#  both be checked in O(1) time under Python <= 3.7 by just validating the key
#  and value of a different key-value pair (e.g., by iterating once for the key
#  and then again for the value). That does have the disadvantage of then
#  requiring O(n) iteration to raise a human-readable exception if a dictionary
#  value fails a type-check, but we're largely okay with that. Again, this only
#  applies to an edge case under obsolete Python versions, so... *shrug*
#* Else, a non-fatal warning should be emitted and the portion of that type
#  hint that *CANNOT* be safely checked under Python <= 3.7 should be ignored.

#FIXME: *WOOPS.* The "LRUCacheStrong" class is absolutely awesome and we'll
#absolutely be reusing that for various supplementary purposes across the
#codebase (e.g., for perfect O(1) tuple type-checking below). However, this
#class sadly doesn't get us where we need to be for full O(1) dictionary and
#set type-checking. Why? Two main reasons:
#* *ITERATIVE ACCESS.* Our routinely scheduled cleanup function needs to
#  iteratively or randomly access arbitrary cache items for inspection to
#  decide whether they need to be harvested or not.
#* *VARIABLE OBJECT SIZES.* We gradually realized, given the plethora of
#  related "FIXME:" comments below, that we'll eventually want to cache a
#  variety of possible types of objects across different caches -- each cache
#  caching a unique type of object. This makes less and less sense the more one
#  considers, however. For example, why have an LRU cache of default size 256
#  specific to iterators for a downstream consumer that only passes one
#  iterator to a single @beartype-decorated callable?
#
#The solution to both is simple, but not: we define a new derivative
#"LRUDuffleCacheStrong" class. The motivation for using the term "duffle" is
#that, just like a duffle bag, a duffle cache:
#* Provides random access.
#* Elegantly stretches to contains a variable number of arbitrary objects of
#  variable size.
#
#The "LRUDuffleCacheStrong" class satisfies both concerns by caching to a
#maximum *OBJECT SIZE CAPACITY* rather than merely to an *OBJECT NUMBER
#CAPACITY.* Whereas the "LRUCacheStrong" class treats all cached objects as
#having a uniform size of 1, the "LRUDuffleCacheStrong" class instead assigns
#each cached object an estimated abstract size (EAS) as a strictly positive
#integer intended to reflect its actual transitive in-memory size -- where a
#cached object of EAS 1 is likely to be the smallest object in that cache.
#While estimating EAS will depend on object type, the following should apply:
#* EAS estimators *MUST* run in O(1) time. That is, estimating the abstract
#  size of an object *MUST* be implementable in constant time with negligible
#  constant factors. This means that the standard approach of recursively
#  inspecting the physical in-memory sizes of all objects visitable from the
#  target object should *NOT* be employed.
#* For containers:
#  * Note that type hints provide us the expected height
#    "sizeable_height" of any data structure, where "sizeable_height" is
#    defined as the number of "[" braces in a type hint ignoring those that do
#    *NOT* connote semantic depth (e.g., "Optional", "Union", "Annotated"). So:
#    * The "sizeable_height" for a type hint "list[list[list[int]]]" is 3.
#    * Since any unsubscripted type hint (e.g., "list") is implicitly
#      subscripted by "[Any]", the "sizeable_height" for the type hints "list"
#      and "list[int]" is both 1.
#  * Note also that most containers satisfy the "collections.abc.Sizeable" ABC.
#  * Given that, we can trivially estimate the EAS "sizeable_bigo_size" of any
#    type-hinted sizeable object "sizeable" as follows:
#      sizeable_bigo_size = len(sizeable) ** sizeable_height
#  Ergo, a list of length 100 type-hinted as "list[list[int]]" has a size of:
#      sizeable_bigo_size = 100 ** 2 = 10,000
#* For dictionaries, the "sizeable_bigo_size" provided by the equation above
#  should be multiplied by two to account for the increased space consumption
#  due to storing key-value pairs.
#
#Here's then how the "LRUDuffleCacheStrong" class is implemented:
#* The "LRUDuffleCacheStrong" class should *NOT* subclass the
#  "LRUCacheStrong" class but copy-and-paste from the latter into the former.
#  This is both for efficiency and maintainability; it's likely their
#  implementations will mildly diverge.
#* The LRUDuffleCacheStrong.__init__() method should be implemented like this:
#      def __init__(
#          self,
#          bigo_size_max: int,
#          value_metadata_len: 'Optional[int]' = 0,
#      )
#          assert bigo_size_max > 0
#          assert value_metadata_len >= 0
#
#          # Classify all passed parameters as instance variables.
#          self._EAS_MAX = bigo_size_max
#          self._FIXED_LIST_SIZE = value_metadata_len + 2
#
#          # Initialize all remaining instance variables.
#          self._bigo_size_cur = 0
#          self._iter = None
#* Note the above assignment of these new instance variables:
#  * "_EAS_MAX", the maximum capacity of this LRU cache in EAS units. Note that
#    this capacity should ideally default to something that *DYNAMICALLY SCALES
#    WITH THE RAM OF THE LOCAL MACHINE.* Ergo, "_bigo_size_max" should be
#    significantly larger in a standard desktop system with 32GB RAM than it is
#    on a Raspberry Pi 2 with 1GB RAM: specifically, 32 times larger.
#  * "_bigo_size_cur", the current capacity of this LRU cache in EAS units.
#  * "_FIXED_LIST_SIZE", the number of additional supplementary objects to
#    be cached with each associated value of this LRU cache. The idea here is
#    that each key-value pair of this cache is an arbitrary hashable object
#    (the key) mapping to a "FixedList(size=self._FIXED_LIST_SIZE)"
#    (the value) whose 0-based indices provide (in order):
#    1. The EAS of that object. For completeness, we should also add to the
#       "sizeable_bigo_size" estimate given above the additional estimated cost
#       of this "FixedList". Since the length of this "FixedList" is guaranteed
#       to be exactly "self._value_metadata_len + 2", this then gives a final
#       EAS of that object as:
#         sizeable_bigo_size = (
#             self._value_metadata_len + 2 + len(sizeable) ** sizeable_height)
#    2. A strong reference to the primary object being cached under this key.
#       For dictionaries and sets, this is an iterator over those dictionaries
#       and sets.
#    3...self._value_metadata_len + 2: Additional supplementary objects to be
#       cached along with that object. For dictionaries and sets, exactly one
#       supplementary object must be cached, so this is:
#       3. The underlying dictionary or set being iterated over, so we can
#          lookup the number of existing strong references to that dictionary
#          or set during cleanup and decide whether to uncache that or not.
#  * "_iter", an iterator over this dictionary. Yes, we *COULD* implement
#    random access (e.g., with a linked list or list), but doing so introduces
#    extreme complications and inefficiencies in both space and time. Instead,
#    persisting a simple iterator over this dictionary suffices.
#* Allow any "LRUDuffleCacheStrong" instance to be trivially incremented
#  (e.g., during garbage collection cleanup) as an iterator by also defining:
#      def get_pair_next_or_none(
#          self,
#          __dict_len = dict.__len__,
#      ) -> 'Optional[Tuple[Hashable, FixedList]]':
#          '''
#          Next most recently used key-value pair of this cache if this cache
#          is non-empty *or* ``None`` otherwise (i.e., if this cache is empty).
#
#          The first call to this method returns the least recently used
#          key-value pair of this cache. Each successive call returns the next
#          least recently used key-value pair of this cache until finally
#          returning the most recently used key-value pair of this cache, at
#          which time the call following that call rewinds time by again
#          returning the least recently used key-value pair of this cache.
#          '''
#
#          #FIXME: Probably nest this in a "with self._thread_lock:" block.
#
#          # If this cache is empty, return None.
#          if not __dict_len(self):
#              return None
#          # Else, this cache is non-empty.
#
#          # Attempt to...
#          try:
#              # Return the next recent key-value pair of this cache.
#              return self._iter.__next__()
#          # If doing so raises *ANY* exception, this iterator has become
#          # desynchronized from this cache. In this case...
#          #
#          # Note this implicitly handles the initial edge case in which this
#          # cache has yet to be iterated (i.e., "self._iter == None"). Since
#          # this is *ONLY* the case for the first call to this method for the
#          # entire lifetime of the active Python process, the negligible
#          # overhead of handling this exception is preferable to violating DRY
#          # by duplicating this logic with an explicit
#          # "if self._iter == None:" block.
#          except:
#              # Reinitialize this iterator.
#              self._iter = self.items()
#
#              # Return the least recent such pair.
#              return self._iter.__next__()
#* Refactor the __setitem__() method. Specifically, when caching a new
#  key-value pair with EAS "bigo_size_item" such that:
#      while bigo_size_item + self._bigo_size_cur > self._bigo_size_max:
#  ...we need to iteratively remove the least recently used key-value pair of
#  this cache (which, yes, technically has O(n) worst-case time, which is
#  non-ideal, which may be why nobody does this, but that's sort-of okay here,
#  since we're doing something monstrously productive each iteration by freeing
#  up critical space and avoiding memory leaks, which seems more than worth the
#  cost of iteration, especially as we expect O(1) average-case time) until
#  this cache can fit that pair into itself. Once it does, we:
#      # Bump the current EAS of this cache by the EAS of this pair.
#      self._bigo_size_cur += bigo_size_item
#  Oh, and there's an obvious edge case here: if "bigo_size_item >
#  self._bigo_size_max", we do *NOT* attempt to do anything with that object.
#  We don't cache it or an iterator over it. It's too bid. Instead, we just
#  type-check the first item of that object in O(1) time. *shrug*
#
#Seems sweet to us. We can store arbitrarily large nested containers in our
#duffle cache without exhausting memory, which is actually more than the
#brute-force LRU cache can say. We get trivial iteration persistence. We also
#avoid a proliferation of different LRU caches, because a single
#"LRUDuffleCacheStrong" instance can flexibly store heterogeneous types.
#FIXME: *RIGHT.* So, "LRUDuffleCacheStrong" is mostly awesome as defined above.
#We'd just like to make a few minor tweaks for improved robustness:
#
#* Drop the "value_metadata_len" parameter from the
#  LRUDuffleCacheStrong.__init__() method. We'd prefer to have that parameter
#  individually passed to each cache_item() call (see below) rather than
#  globally, as the former enables different types of cached objects to have a
#  different quantity of metadata cached with those objects.
#* Drop the __setitem__() implementation borrow from "LRUCacheStrong". Instead,
#  defer to the existing dict.__setitem__() implementation. Why? Because we
#  need to pass additional cache-specific parameters to our own
#  __setitem__()-like non-dunder method, which __setitem__() doesn't support.
#* Define a new cache_obj() method resembling LRUCacheStrong.__setitem__() but
#  even more virile and awesome with signature resembling:
#      def cache_value(
#          self,
#
#          # Mandatory parameters.
#          key: 'Hashable',
#          value: object,
#          *metadata: object,
#
#          # Optional parameters.
#          value_height: 'Optional[int]' = 1,
#      ) -> None:

#FIXME: Here's a reasonably clever idea for perfect O(1) tuple type-checking
#guaranteed to check all n items of an arbitrary tuple in exactly n calls, with
#each subsequent call performing *NO* type-checking by reducing to a noop. How?
#Simple! We:
#* Augment our existing "LRUCacheStrong" data structure to optionally accept a
#  new initialization-time "value_maker" factory function defaulting to "None".
#  If non-"None", "LRUCacheStrong" will implicitly call that function on each
#  attempt to access a missing key by assigning the object returned by that
#  call as the key of a new key-value pair -- or, in other words, by behaving
#  exactly like "collections.defaultdict".
#* Globally define a new "_LRU_CACHE_TUPLE_TO_COUNTER" cache somewhere as an
#  instance of "LRUCacheStrong" whose "value_maker" factory function is
#  initialized to a lambda function simply returning a new
#  "collections.Counter" object that starts counting at 0. Since tuples
#  themselves are hashable and thus permissible for direct use as dictionary
#  keys, this cache maps from tuples (recently passed to or returned from
#  @beartype-decorated callables) to either:
#  * If that tuple has been type-checked to completion, "True" or any other
#    arbitrary sentinel placeholder, really. "True" is simpler, however,
#    because the resulting object needs to be accessible from dynamically
#    generated wrapper functions.
#  * Else, a counter such that the non-negative integer returned by
#    "next(counter)" is the 0-based index of the next item of that tuple to be
#    type-checked.
#
#Given that low-level infrastructure, the pep_code_check_hint() function below
#then generates code perfectly type-checking arbitrary tuples in O(1) time that
#should ideally resemble (where "__beartype_pith_j" is the current pith
#referring to this tuple):
#    (
#        _LRU_CACHE_TUPLE_TO_COUNTER[__beartype_pith_j] is True or
#        {INSERT_CHILD_TYPE_CHECK_HERE}(
#            __beartype_pith_k := __beartype_pith_j[
#                next(_LRU_CACHE_TUPLE_TO_COUNTER[__beartype_pith_j])]
#        )
#    )
#
#Awesome, eh? The same concept trivially generalizes to immutable sequences
#(i.e., "Sequence" type hints that are *NOT* "MutableSequence" type hints).
#Sadly, since many users use "Sequence" to interchangeably denote both
#immutable and mutable sequences, we probably have no means of reliably
#distinguishing the two. So it goes! So, just tuples then in practice. *sigh*

#FIXME: Huzzah! We finally invented a reasonably clever means of (more or less)
#safely type-checking one-shot iterables like generators and iterators in O(1)
#time without destroying those iterables. Yes, doing so requires proxying those
#iterables with iterables of our own. Yes, this is non-ideal but not nearly as
#bad as you might think. Why? Because *NO ONE CARES ABOUT ONE-SHOT ITERABLES.*
#They're one-shot. By definition, you can't really care about them, because
#they don't last long enough. You certainly can't cache them or stash them in
#data structures or really do anything with them beside pass or return them
#between callables until they inevitably get exhausted.
#
#This means that proxying one-shot iterables is almost always safe. Moreover,
#we devised a clever means of proxying that introduces negligible overhead
#while preserving our O(1) guarantee. First, let's examine the standard
#brute-force approach to proxying one-shot iterables:
#
#    class BeartypeIteratorProxy(object):
#        def __init__(self, iterator: 'Iterator') -> None:
#            self._iterator = iterator
#
#        def __next__(self) -> object:
#            item_next = next(self._iterator)
#
#            if not {INSERT_TYPE_CHECKS_HERE}(item_next):
#                raise SomeBeartypeException(f'Iterator {item_next} bad!')
#
#            return item_next
#
#That's bad, because that's an O(n) type-check run on every single iteration.
#Instead, we do this:
#
#    class BeartypeIteratorProxy(object):
#        def __init__(self, iterator: 'Iterator') -> None:
#            self._iterator = iterator
#
#        def __next__(self) -> object:
#            # Here is where the magic happens, folks.
#            self.__next__ = self._iterator.__next__
#
#            item_next = self.__next__(self._iterator)
#
#            if not {INSERT_TYPE_CHECKS_HERE}(item_next):
#                raise SomeBeartypeException(f'Iterator {item_next} bad!')
#
#            return item_next
#
#See what we did there? We dynamically monkey-patch away the
#BeartypeIteratorProxy.__next__() method by replacing that method with the
#underlying __next__() method of the proxied iterator immediately after
#type-checking one and only one item of that iterator.
#
#The devil, of course, is in that details. Assuming a method can monkey-patch
#itself away (we're pretty sure it can, as that's the basis of most efficient
#decorators that cache property method results, *BUT WE SHOULD ABSOLUTELY
#VERIFY THAT THIS IS THE CASE), the trick is then to gracefully handle
#reentrancy. That is to say, although we have technically monkey-patched away
#the BeartypeIteratorProxy.__next__() method, that object is still a live
#object that *WILL BE RECREATED ON EACH CALL TO THE SAME* @beartype-decorated
#callable. Yikes! So, clearly we yet again cache with an "LRUCacheStrong" cache
#specific to iterators... or perhaps something like "LRUCacheStrong" that
#provides a callback mechanism to enable arbitrary objects to remove themselves
#from the cache. Yes! Perhaps just augment our existing "LRUCacheStrong" strong
#with some sort of callback or hook support?
#
#In any case, the idea here is that the "BeartypeIteratorProxy" class defined
#above should internally:
#* Store a weak rather than strong reference to the underlying iterator.
#* Register a callback with that weak reference such that:
#  * When the underlying iterator is garbage-collected, the wrapping
#    "BeartypeIteratorProxy" proxy removes itself from its "LRUCacheStrong"
#    proxy.
#
#Of course, we're still not quite done yet. Why? Because we want to avoid
#unnecessarily wrapping "BeartypeIteratorProxy" instances in
#"BeartypeIteratorProxy" instances. This will happen whenever such an instance
#is passed to a @beartype-decorated callable annotated as accepting or
#returning an iterator. How can we avoid that? Simple. Whenever we detect that
#an iterator to be type-checked is already a "BeartypeIteratorProxy" instance,
#we just efficiently restore the __next__() method of that instance to its
#pre-monkey-patched version: e.g.,
#    (
#        isinstance(__beartype_pith_n, BeartypeIteratorProxy) and
#        # Unsure if this sort of assignment expression hack actually works.
#        # It probably doesn't. So, this may need to be sealed away into a
#        # utility function performing the same operation. *shrug*
#        __beartype_pith_n.__next__ = BeartypeIteratorProxy.__next__
#    )

#FIXME: Huzzah! The prior commentary on type-checking iterators in O(1) time
#also generalizes to most of the other non-trivial objects we had no idea how
#to type-check -- notably, callables. How? Simple. *WE PROXY CALLABLES WITH
#OBJECTS WHOSE* __call__() methods:
#* Type-check parameters to be passed to the underlying callable.
#* Call the underlying callable.
#* Type-check the return value.
#* Monkey-patch themselves away by replacing themselves (i.e., the __call__()
#  methods of that object) with the underlying callable. The only issue here,
#  and it might be a deal-breaker, is whether or not a bound method can simply
#  be replaced with either an unbound function *OR* a bound method of another
#  object entirely. Maybe it can? We suspect it can in both cases, but research
#  will certainly be required here.
#
#Again, cache such objects to avoid reentrancy issues. That said, there is a
#significant complication here that one-shot iterables do *NOT* suffer:
#proxying. Unlike one-shot iterables, callables are often expected to retain
#their object identities. Proxying disrupts that. I still believe that we
#should enable proxying across the board by default despite that, because less
#than 1% of our users will manually enable an option enabling proxying, simply
#because they'll never think to go look for it and when they do find it will be
#understandably hesitant to enable it when everything else is working. Users
#(including myself) typically only enable options when they encounter issues
#requiring they do so. Ergo, proxy by default. But we *ABSOLUTELY* need to
#allow users to conditionally disable proxying on a per-decoration basis --
#especially when proxying callables.
#
#So we propose adding a new optional "is_proxying" parameter to the @beartype
#decorator. Unfortunately, doing so in an efficient manner will prove highly
#non-trivial. Why? Because the standard approach of doing so is *PROBABLY*
#extremely inefficient. We need to test that hypothesis, of course, but the
#standard approach to adding optional parameters to decorators is to nest a
#closure in a closure in a function. We don't need the innermost closure, of
#course, because we dynamically generate it at runtime. We would need the
#outermost closure, though, to support optional decorator parameters under the
#standard approach. That seems outrageously expensive, because each call to the
#@beartype decorator would then internally generate and return a new closure!
#Yikes. We can avoid that by instead, on each @beartype call:
#* Create a new functools.partial()-based wrapper decorator passed our
#  @beartype decorator and all options passed to the current @beartype call.
#* Cache that wrapper decorator into a new private "LRUCacheStrong" instance.
#* Return that decorator.
#* Return the previously cached wrapper decorator on the next @beartype call
#  passed the same options (rather than recreating that decorator).
#
#Naturally, this requires these options to be hashable. Certainly, booleans
#are, so this smart approach supports a new optional "is_proxying" parameter.
#FIXME: Note that the above approach should only be employed as a last-ditch
#fallback in the event that the passed callable both:
#* Lacks a non-None "__annotations__" dictionary.
#* Is *not* annotated by the third-party optional "typeshed" dependency.
#
#If the passed callable satisfies either of those two constraints, the existing
#type hints annotating that callable should be trivially inspected instead in
#O(1) time (e.g., by just performing a brute-force dictionary comparison from
#that callable's "__annotations__" dictionary to a dictionary that we
#internally construct and cache based on the type hints annotating the
#currently decorated callable, except that doesn't quite work because the
#"__annotations__" dictionary maps from parameter and return names whereas the
#"typing.Callable" and "collections.abc.Callable" syntax omits those names,
#which begs the question of how the latter syntax handles positional versus
#keyword arguments anyway)... *OR SOMETHING.*
#
#Fascinatingly, "Callable" syntax supports *NO* distinction between mandatory,
#optional, positional, or keyword arguments, because PEP 484 gonna PEP 484:
#    "There is no syntax to indicate optional or keyword arguments; such
#     function types are rarely used as callback types."
#
#Note that mapping from the return type hint given by "typing.Callable" syntax
#into the "__annotations__" dictionary is trivial, because the return is always
#unconditionally named "return" in that dictionary. So, we then just have to
#resolve how to ignore parameter names. Actually, handling mandatory positional
#parameters (i.e., positional parameters lacking defaults) on the passed
#callable should also be trivial, because they *MUST* strictly correspond to
#the first n child type hints of the first argument of the expected parent
#"typing.Callable" type hint. It's optional positional parameters and keyword
#arguments that are the rub. *shrug*
#
#Obviously, we'll want to dynamically generate the full test based on the
#expected parent "typing.Callable" type hint. For sanity, do this iteratively
#by generating code testing arbitrary "__annotations__" against a "Callable"
#type hint (in increasing order of complexity):
#* Passed *NO* parameters and returning something typed.
#* Passed *ONE* parameter and returning something typed.
#* Passed *TWO* parameters and returning something typed.
#* Passed an arbitrary number of parameters and returning something typed.
#
#Note that test should ideally avoid iteration. We're fairly certain we can do
#that by mapping various attributes from the code object of the passed callable
#into something that enables us to produce a tuple of type hints matching the
#first argument of the expected parent "Callable" type hint.
#
#*BINGO!* The value of the "func.__code__.co_varnames" attribute is a tuple of
#both parameter names *AND* local variables. Fortunately, the parameter names
#come first. Unfortunately, there are two types: standard and keyword-only.
#Altogether, an expression yielding a tuple of the names of all parameters
#(excluding local variables) is given by:
#    func_codeobj = get_func_codeobj(func)
#
#    # Tuple of the names of all parameters accepted by this callable.
#    func_param_names = func_codeobj.co_varnames[
#        :func_codeobj.co_argcount + func_codeobj.co_kwonlyargcount]
#
#Note that "func_param_names" probably excludes variadic positional and keyword
#argument names, but that's probably fine, because "Callable" type hint syntax
#doesn't appear to explicitly support that sort of thing anyway. I mean, how
#would it? Probably using the "..." singleton ellipse object, I'm sure. But
#that's completely undefined, so it seems doubtful anyone's actually doing it.
#
#We then need to use that tuple to slice "func.__annotations__". Of course, you
#can't slice a dictionary in Python, because Python dictionaries are much less
#useful than they should be. See also:
#    https://stackoverflow.com/questions/29216889/slicing-a-dictionary
#
#The simplest and fastest approach we can currently think of is given by:
#    func_param_name_to_hint = func.__annotations__
#
#    # Generator comprehension producing type hints for this callable's
#    # parameters in the same order expected by the first argument of the
#    # "Callable" type hint.
#    func_param_hints = (
#        func_param_name_to_hint[func_param_name]
#        for func_param_name in func_param_names
#    )
#
#Note that because we know the exact number of expected parameters up front
#(i.e., as the len() of the first argument of the "Callable" type hint), we can
#generate optimal code *WITHOUT* a generator or other comprehension and thus
#*WITHOUT* iteration. Yes, this is literally loop unrolling in Python, which is
#both hilarious and exactly what CPython developers get for failing to support
#generally useful operations on dictionaries and sets: e.g.,
#
#    callable_type_hint = ... # Give this a name for reference below.
#
#    # Number of non-variadic parameters expected to be accepted by this
#    # caller-passed callable.
#    FUNC_PARAM_LEN_EXPECTED = len(callable_type_hint[0])
#
#    # Generator comprehension producing type hints for this callable's
#    # parameters in the same order expected by the first argument of the
#    # "Callable" type hint.
#    func_param_hints = (
#        func_param_name_to_hint[func_param_names[0]],
#        func_param_name_to_hint[func_param_names[1]],
#        ...
#        func_param_name_to_hint[func_param_names[FUNC_PARAM_LEN_EXPECTED]],
#    )
#
#Clearly, there's *LOADS* of additional preliminary validation that needs to
#happen here as well. Since "Callable" type hint syntax *REQUIRES* a return
#type hint to be specified (yes, this is absolutely non-optional), we also need
#to ensure that "func_param_name_to_hint" contains the 'return' key.
#
#Given all that, the final test would then resemble something like:
#
#    (
#        __beartype_pith_n_func_param_name_to_hint := (
#            func.__annotations__ or LOOKUP_IN_TYPESHED_SOMEHOW) and
#        'return' in __beartype_pith_n_func_param_name_to_hint and
#        __beartype_pith_n_func_codeobj := getattr(
#            __beartype_pith_n, '__code__', None) and
#        # Just ignore C-based callables and assume they're valid. Unsure what
#        # else we can do with them. Okay, we could also proxy them here, but
#        # that seems a bit lame. Just accept them as is for now, perhaps?
#        __beartype_pith_n_func_codeobj is None or (
#            __beartype_pith_n_func_param_names := (
#                __beartype_pith_n_func_codeobj.co_varnames) and
#            len(__beartype_pith_n_func_param_names) == {FUNC_PARAM_LEN_EXPECTED} and
#            (
#                __beartype_pith_n_func_param_name_to_hint[__beartype_pith_n_func_param_names[0]],
#                __beartype_pith_n_func_param_name_to_hint[__beartype_pith_n_func_param_names[1]],
#                ...
#                __beartype_pith_n_func_param_name_to_hint[__beartype_pith_n_func_param_names[FUNC_PARAM_LEN_EXPECTED]],
#                __beartype_pith_n_func_param_name_to_hint['return']
#            ) == {callable_type_hint}
#        )
#    )
#
#*YUP.* That's super hot, that is. We're sweating.
#
#Note this test is effectively O(1) but really O(FUNC_PARAM_LEN_EXPECTED) where
#FUNC_PARAM_LEN_EXPECTED is sufficiently small that it's basically O(1). That
#said, the constant factors are non-negligible. Fortunately, callables *NEVER*
#change once declared. You should now be thinking what we're thinking:
#*CACHING*. That's right. Just stuff the results of the above test (i.e., a
#boolean) into our duffel LRU cache keyed on the fully-qualified name of that
#callable. We only want to pay the above price once per callable, if we can
#help it, which we absolutely can, so let's do that please.
#
#*NOTE THAT ASSIGNMENT EXPRESSIONS ARE EFFECTIVELY MANDATORY.* I mean, there's
#basically no way we can avoid them, so let's just require them. By the time we
#get here anyway, Python 3.6 will be obsolete, which just leaves Python 3.7. We
#could just emit warnings when decorating callables annotated by "Callable"
#type hints under Python 3.7. </insert_shrug>
#
#*NOTE THAT BUILTINS DO NOT HAVE CODE OBJECTS,* complicating matters. At this
#point, we could care less, but we'll have to care sometime that is not now.
#FIXME: *OH.* Note that things are slightly less trivial than detailed above.
#It's not enough for a callable to be annotated, of course; that callable also
#needs to be annotated *AND* type-checked by a runtime type checker like
#@beartype or @typeguard. The same, of course, does *NOT* apply to "typeshed"
#annotations, because we generally expect stdlib callables to do exactly what
#they say and nothing more or less. This means the above approach should only
#be employed as a last-ditch fallback in the event that the passed callable
#does *NOT* satisfy any of the following:
#* Is decorated by a runtime type checker *AND* has a non-None
#  "__annotations__" dictionary.
#* Is annotated by the third-party optional "typeshed" dependency.
#
#Trivial, but worth noting.
#FIXME: Lastly, note that everywhere we say "typeshed" above, we *REALLY* mean
#a PEP 561-compliant search for stub files annotating that callable.
#Unsurprisingly, the search algorithm is non-trivial, which will impact the
#performance gains associated with type-checking annotations in the first
#place. Ergo, we might consider omitting aspects of this search that are both
#highly inefficient *AND* unlikely to yield positive hits. See also:
#    https://www.python.org/dev/peps/pep-0561/

#FIXME: *IT'S CONFIGURATION TIME.* So, let's talk about how we efficiently
#handle @beartype configuration like the "is_proxying" boolean introduced
#above. It's worth getting this right the first time. Happily, we got this
#right the first time with a balls-crazy scheme that gives us O(1)
#configurability that supports global defaults that can be both trivially
#changed globally *AND* overridden by passed optional @beartype parameters.
#
#Note this scheme does *NOT* require us to litter the codebase with cumbersome
#and inefficient logic like:
#    muh_setting = (
#        beartype_params.muh_setting if beartype_params.muh_setting is not None else
#        beartype._global_config.muh_setting)
#
#What is this magic we speak of? *SIMPLE.* We twist class variable MRO lookup
#in our favour. Since CPython already efficiently implements such lookup with a
#fast C implementation, we can hijack that implementation for our own sordid
#purposes to do something completely different. Note that only *CLASS* variable
#MRO lookup suffices. Since classes are global singletons, all subclasses will
#implicitly perform efficient lookups for undefined class variables in their
#superclass -- which is exactly what we want and need here.
#
#Specifically:
#* Define a new private "beartype._config" submodule.
#* In that submodule:
#  * Define a new public "BeartypeConfigGlobal" class declaring all
#    configuration settings as class variables defaulting to their desired
#    arbitrary global defaults: e.g.,
#        class BeartypeConfigGlobal(object):
#            '''
#            **Global beartype configuration.**
#            '''
#
#            is_proxying = True
#            ...
#* Publicly expose that class to external users as a new public
#  "beartype.config" *PSEUDO-MODULE.* In reality, that object will simply be an
#  alias of "beartype._config.BeartypeConfigGlobal". But users shouldn't know
#  that. They should just treat that object as if it was a module. To effect
#  this, just establish this alias in the "beartype.__init__" submodule: e.g.,
#      from beartype._config import BeartypeConfigGlobal
#
#      # It really is that simple, folks. Maybe. Gods, let it be that simple.
#      config = BeartypeConfigGlobal
#* Privatize the existing public "beartype._decor.main" submodule to a new
#  "beartype._decor._template" submodule.
#* In that submodule:
#  * Rename the existing @beartype decorator to beartype_template(). That
#    function will now only be called internally rather than externally.
#* Define a new private "beartype._decor._cache.cachedecor" submodule.
#* In that submodule:
#  * Define a new "BEARTYPE_PARAMS_TO_DECOR" dictionary mapping from a *TUPLE*
#    of positional arguments listed in the exact same order as the optional
#    parameters accepted by the new @beartype decorator discussed below to
#    subclasses to dynamically generated @beartype decorators configured by
#    those subclasses. This tuple should just literally be the argument tuple
#    passed to the @beartype decorator, which is probably easiest to achieve if
#    we force @beartype parameters to be passed as keyword-only arguments:
#
#        # Keyword-only arguments require Python >= 3.8. Under older Pythons,
#        # just drop the "*". Under older Pythons, let's just *NOT ALLOW
#        # CONFIGURATION AT ALL.* So, this gives us:
#        if IS_PYTHON_AT_LEAST_3_8:
#            def beartype(*, is_proxying: bool = None, ...) -> Callable:
#                BEARTYPE_PARAMS = (is_proxying, ...)
#
#                beartype_decor = BEARTYPE_PARAMS_TO_DECOR.get(BEARTYPE_PARAMS)
#                if beartype_decor:
#                    return beartype_decor
#
#                # Else, we need to make a new @beartype decorator passed
#                # these parameters, cache that decorator in
#                # "BEARTYPE_PARAMS_TO_DECOR", and return that decorator.
#        else:
#            # Probably not quite right, but close enough.
#            beartype = beartype_template
#
#    We need a hashable tuple for lookup purposes. That's *ABSOLUTELY* the
#    fastest way, given that we expect keyword arguments. So, we're moving on.
#    Also, do *NOT* bother with LRU caching here, as the expected size of that
#    dictionary will almost certainly always be less than 10 and surely 100.
#* Define a new private "beartype._decor.main" submodule.
#* In that submodule:
#  * Define a new @beartype decorator accepting *ALL* of the *EXACT* same
#    class variables declared by the "BeartypeConfigGlobal" class as optional
#    parameters of the same name but *UNCONDITIONALLY* defaulting to "None".
#    That last bit is critical. Do *NOT* default them to what the
#    "BeartypeConfigGlobal" superclass defaults them to, as that would obstruct
#    our purposes, which is to have lookups punted upward to the
#    "BeartypeConfigGlobal" superclass only when undefined in a subclass.
#  * The purpose of this new @beartype decorator is to (in order):
#    * First lookup the passed parameters to get an existing decorator passed
#      those parameters, as already implemented above. (This is trivial.)
#    * If we need to make a new decorator, this is also mostly trivial. Just:
#      * Define a new local dictionary "BEARTYPE_PARAM_NAME_TO_VALUE" bundling
#        these optional parameters for efficient lookup: e.g.,
#            BEARTYPE_PARAM_NAME_TO_VALUE = {
#                'is_proxying': is_proxying,
#                ...
#            }
#      * Dynamically create a new "BeartypeConfigGlobal" subclass *SETTING THE
#        DESIRED CLASS VARIABLES* based on all of the passed optional
#        parameters whose values are *NOT* "None". For example, if the only
#        passed non-"None" optional parameter was "is_proxying", this would be:
#            class _BeartypeConfigDecor{ARBITRARY_NUMBER}(BeartypeConfigGlobal):
#                is_proxying = False
#        This will probably require a bit of iteration to filter out all
#        non-"None" optional parameters. Note that the simplest way to
#        implement this would probably be to just dynamically declare an empty
#        subclass and then monkey-patch that subclass' dictionary with the
#        desired non-"None" optional parameters: e.g.,
#            # Pseudo-code, but close enough.
#            BeartypeConfigDecor = eval(
#                f'''class _BeartypeConfigDecor{ARBITRARY_NUMBER}(BeartypeConfigGlobal): pass''')
#
#            # Yes, this is a bit lame, but it suffices for now. Remember,
#            # we're caching this class, so the logic constructing this class
#            # doesn't need to be lightning fast. It's *FAR* more critical that
#            # the logic looking up this class in this class be lightning fast.
#            #
#            # Do *NOT* try to embed this logic into the above evaluation
#            # (e.g., as f-expressions). Yes, that sort of hackery is trivial
#            # with booleans but rapidly gets hairy with containers. So, I
#            # *GUESS* we could do that for booleans. Just remember that that
#            # doesn't generalize to the general case. Actually, don't bother.
#            # The following suffices and doesn't violate DRY, which is the
#            # only important thing here.
#            BeartypeConfigDecor.__dict__.update({
#                param_name: param_value
#                param_name, param_value in BEARTYPE_PARAM_NAME_TO_VALUE.items()
#                if param_value is not None
#            })
#      * Dynamically *COPY* the beartype_template() function into a new
#        function specific to that subclass, which means that function is
#        actually just a template. We'll never actually the original function
#        itself; we just use that function as the basis for dynamically
#        generating new decorators on-the-fly. Heh! Fortunately, we only need
#        a shallow function copy. That is to say, we want the code objects to
#        remain the same. Note that the most efficient means of implementing
#        this is given directly be this StackOverflow answer:
#            https://stackoverflow.com/a/13503277/2809027
#        Note that that answer can be slightly improved to resemble:
#            WRAPPER_ASSIGNMENTS = functools.WRAPPER_ASSIGNMENTS + ('__kwdefaults__',)
#            def copy_func(f):
#                g = types.FunctionType(f.__code__, f.__globals__, name=f.__name__,
#                                       argdefs=f.__defaults__,
#                                       closure=f.__closure__)
#                g = functools.update_wrapper(g, f, WRAPPER_ASSIGNMENTS)
#                return g
#        That's the most general form. Of course, we don't particularly care
#        about copying metadata, since we don't expect anyone to care about
#        these dynamically generated decorators. That means we can reduce the
#        above to simply:
#            def copy_func(f):
#                return types.FunctionType(
#                    f.__code__,
#                    f.__globals__,
#                    name=f.__name__,
#                    argdefs=f.__defaults__,
#                    closure=f.__closure__,
#                )
#      * Monkey-patch the new decorator returned by
#        "copy_func(beartype_template)" with the new subclass: e.g.,
#            beartype_decor = copy_func(beartype_template)
#            beartype_decor.__beartype_config = BeartypeConfigDecor
#        *HMMM.* Minor snag. That doesn't work, but the beartype_template()
#        template won't have access to that "__beartype_config". Instead, we'll
#        need to:
#        * Augment the signature of the beartype_template() template to accept
#          a new optional "config" parameter default to "None": e.g.,.
#          def beartype_template(
#              func: Callable, config: BeartypeConfigGlobal = None) -> Callable:
#        * Either refactor the copy_func() function defined above to accept a
#          caller-defined "argdefs" parameter *OR* (more reasonably) just
#          inline the body of that function in @beartype as:
#            beartype_decor = types.FunctionType(
#                f.__code__,
#                f.__globals__,
#                name=f.__name__,
#                # Yup. In theory, that should do it, if we recall the internal
#                # data structure of this parameter correctly.
#                argdefs=(BeartypeConfigDecor,),
#                closure=f.__closure__,
#            )
#      * Cache and return that decorator:
#            BEARTYPE_PARAMS_TO_DECOR[BEARTYPE_PARAMS] = beartype_decor
#            return beartype_decor
#
#Pretty trivial, honestly. We've basically already implemented all of the hard
#stuff above, which is nice.
#
#Note that the beartype_template() function will now accept an optional
#"config" parameter -- which will, of course, *ALWAYS* be non-"None" by the
#logic above. Assert this, of course. We can then trivially expose that
#"config" to lower-level beartype functions by just stuffing it into the
#existing "BeartypeData" class: e.g.,
#    # Welp, that was trivial.
#    func_data.config = config
#
#Since we pass "func_data" everywhere, we get configuration for free. Muhaha!

#FIXME: Propagate generic subscriptions both to *AND* from pseudo-superclasses.
#First, consider the simpler case of propagating a generic subscription to
#pseudo-superclasses: e.g.,
#    from typing import List
#    class MuhList(List): pass
#
#    @beartype
#    def muh_lister(muh_list: MuhList[int]) -> None: pass
#
#During internal type hint visitation, @beartype should propagate the "int"
#child type hint subscripting the "MuhList" type hint up to the "List"
#pseudo-superclass under Python >= 3.9. Under older Python versions, leaving
#"List" unsubscripted appears to raise exceptions at parse time. *shrug*
#
#Of the two cases, this first case is *SIGNIFICANTLY* more important than the
#second case documented below. Why? Because mypy (probably) supports this first
#but *NOT* second case, for  which mypy explicitly raises an "error". Since
#mypy has effectively defined the standard interpretation of type hints,
#there's little profit in contravening that ad-hoc standard by supporting
#something unsupported under mypy -- especially because doing so would then
#expose end user codebases to mypy errors. Sure, that's "not our problem, man,"
#but it kind of is, because community standards exist for a reason -- even if
#they're ad-hoc community standards we politely disagree with.
#
#Nonetheless, here's the second case. Consider the reverse case of propagating
#a generic subscription from a pseudo-superclass down to its unsubscripted
#generic: e.g.,
#    from typing import Generic, TypeVar
#
#    T = TypeVar('T')
#    class MuhGeneric(Generic[T]):
#        def __init__(self, muh_param: T): pass
#
#    @beartype
#    def muh_genericizer(generic: MuhGeneric, T) -> None: pass
#
#During internal type hint visitation, @beartype should propagate the "T"
#child type hint subscripting the "Generic" pseudo-superclass down to the
#"MuhGeneric" type hint under Python >= 3.9 and possibly older versions. Doing
#so would reduce DRY violations, because there's no tangible reason why users
#should have to perpetually subscript "MuhGeneric" when its pseudo-superclass
#already has been. Of course, mypy doesn't see it that way. *shrug*

#FIXME: When time permits, we can augment the pretty lame approach by
#publishing our own "BeartypeDict" class that supports efficient random access
#of both keys and values. Note that:
#* The existing third-party "randomdict" package provides baseline logic that
#  *MIGHT* be useful in getting "BeartypeDict" off the ground. The issue with
#  "randomdict", however, is that it internally leverages a "list", which
#  probably then constrains key-value pair deletions on the exterior
#  "randomdict" object to an O(n) rather than O(1) operation, which is
#  absolutely unacceptable.
#* StackOverflow questions provide a number of solutions that appear to be
#  entirely O(1), but which require maintaining considerably more internal data
#  structures, which is also unacceptable (albeit less so), due to increased
#  space consumption that probably grows unacceptable fast and thus fails to
#  generally scale.
#* Since we don't control "typing", we'll also need to augment "BeartypeDict"
#  with a "__class_getitem__" dunder method (or whatever that is called) to
#  enable that class to be subscripted with "typing"-style types ala:
#     def muh_func(muh_mapping: BeartypeDict[str, int]) -> None: pass
#In short, we'll need to conduct considerably more research here.
#FIXME: Actually, none of the above is necessary or desirable. Rather than
#designing a random access "BeartypeDict" class, it would be *FAR* more useful
#to design a series of beartype-specific container types in a new external
#"beartypes" package, each of which performs O(1) type-checking *ON INSERTION
#OF EACH CONTAINER ITEM.* This should be stupidly fast under standard use
#cases, because we typically expect an item to be inserted only once but
#accessed many, many times. By just checking on insertion, we avoid *ALL* of
#the complications of trying to type-check after the fact during sequential
#non-random iteration over items.
#
#Indeed, there appears to be a number of similar projects with the same idea,
#with the caveat that these projects *ALL* leverage package-specific constructs
#rather than PEP-compliant type hints -- a significant negative. The most
#interesting of these are:
#* "typed_python", a fascinating package with a variety of novel ideas at play.
#  In addition to providing package-specific container types that perform
#  PEP-noncompliant type-checking on item insertion *IMPLEMENTED THAT AT THE C
#  LEVEL* rather than in pure Python (which is both horrible and fascinating,
#  mainly because... why bother? I mean, PyPy, Nuitka, and Cython already
#  exist, so why go to all that trouble to work in C rather than Python?),
#  this package also offers:
#  * "typed_python.Entrypoint", which looks balls-cray-cray. This is probably
#    the most interesting aspect of this package, presuming it actually behaves
#    as advertised, which it almost certainly doesn't. Nonetheless, it appears
#    to be a bit of a cross between Nuitka and beartype. To quote:
#    "Simply stick the @typed_python.Entrypoint decorator around any function
#     that uses "typed_python" primitives to get a fast version of it:
#     @Entrypoint
#     def sum(someList, zero):
#         for x in someList:
#             zero += x
#         return x
#     ...will generate specialized code for different data types
#     ("ListOf(int)", say, or "ListOf(float)", or even "Dict(int)") that's not
#     only many times faster than the python equivalent, but that can operate
#     using multiple processors. Compilation occurs each time you call the
#     method with a new combination of types." The "that can operate using
#     multiple processors" part is particularly novel, as it implies
#     circumvention of the GIL. "typed_python" appears to implement this magic
#     by leveraging LLVM to compile Python down to C. Again, we strongly doubt
#     any of this actually works under real-world industrial constraints, but
#     it's still a fascinating thought experiment.
#  * "type_python.Class", a generic-style class one subclasses to generate
#    "strongly typed class with a packed memory layout." The "strongly typed"
#    part isn't terribly interesting, as it's PEP-noncompliant. The "packed
#    memory layout" part, however, *IS* interesting. Reducing space consumption
#    by presumably compiling to C is intriguing, if tangential to our concerns.

# ....................{ IMPORTS                           }....................
from beartype.cave import NoneType
from beartype.roar import (
    BeartypeDecorHintPepException,
    BeartypeDecorHintPepUnsupportedException,
    BeartypeDecorHintPep484Exception,
)
from beartype._decor._cache.cachetype import (
    register_typistry_forwardref,
    register_typistry_type,
    register_typistry_tuple,
)
from beartype._decor._code.codesnip import CODE_INDENT_1, CODE_INDENT_2
from beartype._decor._code._pep._pepsnip import (
    PEP_CODE_CHECK_HINT_GENERIC_PREFIX,
    PEP_CODE_CHECK_HINT_GENERIC_SUFFIX,
    PEP_CODE_CHECK_HINT_ROOT_PREFIX,
    PEP_CODE_CHECK_HINT_TUPLE_FIXED_PREFIX,
    PEP_CODE_CHECK_HINT_TUPLE_FIXED_SUFFIX,
    PEP_CODE_HINT_CHILD_PLACEHOLDER_PREFIX,
    PEP_CODE_HINT_CHILD_PLACEHOLDER_SUFFIX,
    PEP_CODE_HINT_FORWARDREF_UNQUALIFIED_PLACEHOLDER_PREFIX,
    PEP_CODE_HINT_FORWARDREF_UNQUALIFIED_PLACEHOLDER_SUFFIX,
    PEP_CODE_PITH_NAME_PREFIX,
    PEP_CODE_PITH_ROOT_NAME,
    PEP_CODE_RAISE_PEP_CALL_EXCEPTION_RANDOM_INT,
    PEP484_CODE_CHECK_HINT_UNION_PREFIX,
    PEP484_CODE_CHECK_HINT_UNION_SUFFIX,

    # Bound format methods.
    PEP_CODE_CHECK_HINT_NONPEP_TYPE_format,
    PEP_CODE_CHECK_HINT_ROOT_SUFFIX_format,
    PEP_CODE_CHECK_HINT_SEQUENCE_STANDARD_format,
    PEP_CODE_CHECK_HINT_SEQUENCE_STANDARD_PITH_CHILD_EXPR_format,
    PEP_CODE_CHECK_HINT_TUPLE_FIXED_EMPTY_format,
    PEP_CODE_CHECK_HINT_TUPLE_FIXED_LEN_format,
    PEP_CODE_CHECK_HINT_TUPLE_FIXED_NONEMPTY_CHILD_format,
    PEP_CODE_CHECK_HINT_TUPLE_FIXED_NONEMPTY_PITH_CHILD_EXPR_format,
    PEP_CODE_CHECK_HINT_GENERIC_CHILD_format,
    PEP_CODE_PITH_ASSIGN_EXPR_format,
    PEP484_CODE_CHECK_HINT_UNION_CHILD_PEP_format,
    PEP484_CODE_CHECK_HINT_UNION_CHILD_NONPEP_format,
)
from beartype._util.cache.utilcachecall import callable_cached
from beartype._util.cache.pool.utilcachepoollistfixed import (
    SIZE_BIG,
    acquire_fixed_list,
    release_fixed_list,
)
from beartype._util.cache.pool.utilcachepoolobjecttyped import (
    acquire_object_typed,
    release_object_typed,
)
from beartype._util.cache.utilcacheerror import (
    EXCEPTION_CACHED_PLACEHOLDER)
from beartype._util.hint.data.pep.utilhintdatapep import (
    HINT_PEP_SIGNS_SUPPORTED_DEEP,
    HINT_PEP_SIGNS_SEQUENCE_STANDARD,
    HINT_PEP_SIGNS_TUPLE,
)
from beartype._util.hint.data.pep.proposal.utilhintdatapep484 import (
    HINT_PEP484_BASE_FORWARDREF,
    HINT_PEP484_SIGNS_UNION,
)
from beartype._util.hint.data.utilhintdata import HINTS_IGNORABLE_SHALLOW
from beartype._util.hint.utilhintget import get_hint_forwardref_classname
from beartype._util.hint.utilhinttest import is_hint_ignorable
from beartype._util.hint.pep.proposal.utilhintpep484 import (
    get_hint_pep484_generic_base_erased_from_unerased,
    get_hint_pep484_newtype_class,
    is_hint_pep484_newtype,
)
from beartype._util.hint.pep.proposal.utilhintpep544 import (
    get_hint_pep544_io_protocol_from_generic,
    is_hint_pep544_io_generic,
)
from beartype._util.hint.pep.proposal.utilhintpep585 import is_hint_pep585_builtin
from beartype._util.hint.pep.proposal.utilhintpep593 import (
    get_hint_pep593_hint,
    is_hint_pep593,
)
from beartype._util.hint.pep.utilhintpepget import (
    get_hint_pep_args,
    get_hint_pep_generic_bases_unerased,
    get_hint_pep_sign,
    get_hint_pep_stdlib_type,
    get_hint_pep_generic_type_or_none,
)
from beartype._util.hint.pep.utilhintpeptest import (
    die_if_hint_pep_unsupported,
    die_if_hint_pep_sign_unsupported,
    is_hint_pep,
    is_hint_pep_tuple_empty,
    is_hint_pep_typing,
    warn_if_hint_pep_sign_deprecated,
)
from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_8
from beartype._util.text.utiltextmunge import replace_str_substrs
from itertools import count
from typing import Generic, Tuple, NoReturn

# See the "beartype.cave" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ CONSTANTS ~ hint : meta           }....................
# Iterator yielding the next integer incrementation starting at 0, to be safely
# deleted *AFTER* defining the following 0-based indices via this iterator.
__hint_meta_index_counter = count(start=0, step=1)


_HINT_META_INDEX_HINT = next(__hint_meta_index_counter)
'''
0-based index into each tuple of hint metadata providing the currently
visited hint.

For both space and time efficiency, this metadata is intentionally stored as
0-based integer indices of an unnamed tuple rather than:

* Human-readable fields of a named tuple, which incurs space and time costs we
  would rather *not* pay.
* 0-based integer indices of a tiny fixed list. Previously, this metadata was
  actually stored as a fixed list. However, exhaustive profiling demonstrated
  that reinitializing each such list by slice-assigning that list's items from
  a tuple to be faster than individually assigning these items:

  .. code-block:: shell-session

     $ echo 'Slice w/ tuple:' && command python3 -m timeit -s \
          'muh_list = ["a", "b", "c", "d",]' \
          'muh_list[:] = ("e", "f", "g", "h",)'
     Slice w/ tuple:
     2000000 loops, best of 5: 131 nsec per loop
     $ echo 'Slice w/o tuple:' && command python3 -m timeit -s \
          'muh_list = ["a", "b", "c", "d",]' \
          'muh_list[:] = "e", "f", "g", "h"'
     Slice w/o tuple:
     2000000 loops, best of 5: 138 nsec per loop
     $ echo 'Separate:' && command python3 -m timeit -s \
          'muh_list = ["a", "b", "c", "d",]' \
          'muh_list[0] = "e"
     muh_list[1] = "f"
     muh_list[2] = "g"
     muh_list[3] = "h"'
     Separate:
     2000000 loops, best of 5: 199 nsec per loop

  So, not only does there exist no performance benefit to smaller fixed lists,
  there exists demonstrable performance costs.
'''


_HINT_META_INDEX_PLACEHOLDER = next(__hint_meta_index_counter)
'''
0-based index into each tuple of hint metadata providing the **current
placeholder type-checking substring** (i.e., placeholder to be globally
replaced by a Python code snippet type-checking the current pith expression
against the hint described by this metadata on visiting that hint).

This substring provides indirection enabling the currently visited parent hint
to defer and delegate the generation of code type-checking each child argument
of that hint to the later time at which that child argument is visited.

Example
----------
For example, the :func:`pep_code_check_hint` function might generate
intermediary code resembling the following on visiting the :data:`Union` parent
of a ``Union[int, str]`` object *before* visiting either the :class:`int` or
:class:`str` children of that object:

    if not (
        @{0}! or
        @{1}!
    ):
        raise __beartype_raise_pep_call_exception(
            func=__beartype_func,
            pith_name=$%PITH_ROOT_NAME/~,
            pith_value=__beartype_pith_root,
        )

Note the unique substrings "@{0}!" and "@{1}!" in that code, which that
function iteratively replaces with code type-checking each of the child
arguments of that :data:`Union` parent (i.e., :class:`int`, :class:`str`). The
final code memoized by that function might then resemble:

    if not (
        isinstance(__beartype_pith_root, int) or
        isinstance(__beartype_pith_root, str)
    ):
        raise __beartype_raise_pep_call_exception(
            func=__beartype_func,
            pith_name=$%PITH_ROOT_NAME/~,
            pith_value=__beartype_pith_root,
        )
'''


_HINT_META_INDEX_PITH_EXPR = next(__hint_meta_index_counter)
'''
0-based index into each tuple of hint metadata providing the **current
pith expression** (i.e., Python code snippet evaluating to the current possibly
nested object of the passed parameter or return value to be type-checked
against the currently visited hint).
'''


_HINT_META_INDEX_INDENT = next(__hint_meta_index_counter)
'''
0-based index into each tuple of hint metadata providing **current
indentation** (i.e., Python code snippet expanding to the current level of
indentation appropriate for the currently visited hint).
'''

# Delete the above counter for safety and sanity in equal measure.
del __hint_meta_index_counter

# ....................{ CONSTANTS ~ operator              }....................
_OPERATOR_SUFFIX_LEN_AND = len(' and')
'''
Length of the builtin ``and`` operator when suffixing Python code snippets
generated by the :func:`pep_code_check_hint` function.
'''


_OPERATOR_SUFFIX_LEN_OR = len(' or')
'''
Length of the builtin ``or`` operator when suffixing Python code snippets
generated by the :func:`pep_code_check_hint` function.
'''

# ....................{ CODERS                            }....................
@callable_cached
def pep_code_check_hint(hint: object) -> Tuple[str, bool, Tuple[str, ...]]:
    '''
    Python code type-checking the previously localized parameter or return
    value annotated by the passed PEP-compliant type hint against this hint of
    the decorated callable.

    This code generator is memoized for efficiency.

    Caveats
    ----------
    **This function intentionally accepts no** ``hint_label`` **parameter.**
    Why? Since that parameter is typically specific to the caller, accepting
    that parameter would effectively prevent this code generator from memoizing
    the passed hint with the returned code, which would rather defeat the
    point. Instead, this function only:

    * Returns generic non-working code containing the placeholder
      :attr:`beartype._decor._code._pep.pepcode.PITH_ROOT_NAME_PLACEHOLDER_STR`
      substring that the caller is required to globally replace by the name of
      the current parameter *or* ``return`` for return values (e.g., by calling
      the builtin :meth:`str.replace` method) to generate the desired
      non-generic working code type-checking that parameter or return value.
    * Raises generic non-human-readable exceptions containing the placeholder
      :attr:`beartype._util.cache.utilcacheerror.EXCEPTION_CACHED_PLACEHOLDER`
      substring that the caller is required to explicitly catch and raise
      non-generic human-readable exceptions from by calling the
      :func:`beartype._util.cache.utilcacheerror.reraise_exception_cached`
      function.

    Parameters
    ----------
    hint : object
        PEP-compliant type hint to be type-checked.

    Returns
    ----------
    Tuple[str, bool, Tuple[str, ...]]
        3-tuple ``(func_code, is_func_code_needs_random_int,
        hints_forwardref_class_basename)``, where:

        * ``func_code`` is Python code type-checking the previously localized
          parameter or return value against this hint.
        * ``is_func_code_needs_random_int`` is a boolean that is ``True`` only
          if one or more PEP-compliant type hints transitively visitable from
          this root hint (including this root hint) require a pseudo-random
          integer. If true, the higher-level
          :func:`beartype._decor._code.codemain.generate_code` function
          prefixes the body of this wrapper function with code generating such
          an integer.
        * ``hints_forwardref_class_basename`` is a tuple of the unqualified
          classnames of `PEP 484`_-compliant relative forward references
          visitable from this root hint (e.g., ``('MuhClass', 'YoClass')``
          given the root hint ``Union['MuhClass', List['YoClass']]``).

    Raises
    ----------
    BeartypeDecorHintPepException
        If this object is *not* a PEP-compliant type hint.
    BeartypeDecorHintPepUnsupportedException
        If this object is a PEP-compliant type hint currently unsupported by
        the :func:`beartype.beartype` decorator.

    Raises
    ----------
    BeartypeDecorHintPepDeprecatedWarning
        If one or more PEP-compliant type hints annotating the currently
        decorated callable are deprecated.

    .. _PEP 484:
       https://www.python.org/dev/peps/pep-0484
    '''

    # ..................{ HINT ~ root                       }..................
    # Top-level hint relocalized for disambiguity. For the same reason, delete
    # the passed parameter whose name is ambiguous within the context of this
    # code generator.
    hint_root = hint
    del hint

    # Python code snippet evaluating to the current passed parameter or return
    # value to be type-checked against the root hint.
    pith_root_expr = PEP_CODE_PITH_ROOT_NAME

    # ..................{ HINT ~ current                    }..................
    # Currently visited hint.
    hint_curr = None

    # Current unsubscripted typing attribute associated with this hint (e.g.,
    # "Union" if "hint_curr == Union[int, str]").
    hint_curr_sign = None

    # Python expression evaluating to an isinstance()-able class (e.g., origin
    # type) associated with the currently visited type hint if any.
    hint_curr_expr = None

    #FIXME: Excise us up.
    # Origin type (i.e., non-"typing" superclass suitable for shallowly
    # type-checking the current pith against the currently visited hint by
    # passing both to the isinstance() builtin) of this hint if this hint
    # originates from such a superclass.
    # hint_curr_type_origin = None

    # Placeholder string to be globally replaced in the Python code snippet to
    # be returned (i.e., "func_code") by a Python code snippet type-checking
    # the current pith expression (i.e., "pith_curr_assigned_expr") against the
    # currently visited hint (i.e., "hint_curr").
    hint_curr_placeholder = None

    # Full Python expression evaluating to the value of the current pith (i.e.,
    # possibly nested object of the passed parameter or return value to be
    # type-checked against the currently visited hint).
    #
    # Note that this is *NOT* a Python >= 3.8-specific assignment expression
    # but rather the original inefficient expression provided by the parent
    # PEP-compliant type hint of the currently visited hint.
    pith_curr_expr = None

    # Python code snippet expanding to the current level of indentation
    # appropriate for the currently visited hint.
    indent_curr = CODE_INDENT_2

    # ..................{ HINT ~ child                      }..................
    #FIXME: Excise us up.
    # True only if this hint is subscripted by multiple child hints.
    # is_hint_childs_multiple = None

    # Currently iterated PEP-compliant child hint subscripting the currently
    # visited hint, initialized to the root hint to enable the subsequently
    # called _enqueue_hint_child() function to enqueue the root hint.
    hint_child = hint_root

    #FIXME: Excise us up.
    # Current unsubscripted typing attribute associated with this hint (e.g.,
    # "Union" if "hint_child == Union[int, str]").
    # hint_child_sign = None

    # Placeholder string to be globally replaced in the Python code snippet to
    # be returned (i.e., "func_code") by a Python code snippet type-checking
    # the child pith expression (i.e., "pith_child_expr") against the currently
    # iterated child hint (i.e., "hint_child").
    hint_child_placeholder = None

    # Integer identifying the currently iterated child PEP-compliant type
    # hint of the currently visited parent PEP-compliant type hint.
    #
    # Note this ID is intentionally initialized to -1 rather than 0. Since
    # the get_next_pep_hint_child_str() method increments *BEFORE*
    # stringifying this ID, initializing this ID to -1 ensures that method
    # returns a string containing only non-negative substrings starting at
    # 0 rather than both negative and positive substrings starting at -1.
    hint_child_placeholder_id = -1

    #FIXME: Excise us up.
    # Python expression evaluating to the value of the currently iterated child
    # hint of the currently visited parent hint.
    # hint_child_expr = None

    #FIXME: Excise us up.
    # Origin type (i.e., non-"typing" superclass suitable for shallowly
    # type-checking the current pith against the currently visited hint by
    # passing both to the isinstance() builtin) of the currently iterated child
    # hint of the currently visited parent hint.
    # hint_child_type_origin = None

    #FIXME: Excise us up.
    # Python code snippet evaluating to the current (possibly nested) object of
    # the passed parameter or return value to be type-checked against the
    # currently iterated child hint.
    #pith_child_expr = None

    # Python code snippet expanding to the current level of indentation
    # appropriate for the currently iterated child hint, initialized to the
    # root hint indentation to enable the subsequently called
    # _enqueue_hint_child() function to enqueue the root hint.
    indent_child = indent_curr

    # ..................{ HINT ~ childs                     }..................
    # Current tuple of all PEP-compliant child hints subscripting the currently
    # visited hint (e.g., "(int, str)" if "hint_curr == Union[int, str]").
    hint_childs: tuple = None  # type: ignore[assignment]

    # Number of PEP-compliant child hints subscripting the currently visited
    # hint.
    hint_childs_len: int = None  # type: ignore[assignment]

    # Set of all PEP-noncompliant child hints subscripting the currently
    # visited hint.
    hint_childs_nonpep: set = None  # type: ignore[assignment]

    # Set of all PEP-compliant child hints subscripting the currently visited
    # hint.
    hint_childs_pep: set = None  # type: ignore[assignment]

    # ..................{ HINT ~ pep 484 : forwardref       }..................
    # Set of the unqualified classnames referred to by all relative forward
    # references visitable from this root hint if any *OR* "None" otherwise
    # (i.e., if no such forward references are visitable).
    hints_forwardref_class_basename: set = None  # type: ignore[assignment]

    # Possibly unqualified classname referred to by the currently visited
    # forward reference type hint.
    hint_curr_forwardref_classname: str = None  # type: ignore[assignment]

    # ..................{ HINT ~ pep 572                    }..................
    # The following local variables isolated to this subsection are only
    # relevant when these conditions hold:
    #
    # * The active Python interpreter targets at least Python 3.8, the first
    #   major Python version to introduce support for "PEP 572 -- Assignment
    #   Expressions."
    # * The currently visited hint is *NOT* the root hint (i.e., "hint_root").
    #   If the currently visited hint is the root hint, the current pith has
    #   already been localized to a local variable whose name is the value of
    #   the "PEP_CODE_PITH_ROOT_NAME" string global and thus need *NOT* be
    #   relocalized to another local variable using an assignment expression.
    #
    # This is a necessary and sufficient condition for deciding whether a
    # Python >= 3.8-specific assignment expression localizing the current pith
    # should be embedded in the code generated to type-check this pith against
    # this hint. This is a non-trivial runtime optimization eliminating
    # repeated computations to obtain this pith from PEP-compliant child hints.
    # For example, if this hint constrains this pith to be a standard sequence,
    # the child pith of this parent pith is a random item selected from this
    # sequence; since obtaining this child pith is non-trivial, the computation
    # required to do so is performed only once by assigning this child pith to
    # a unique local variable during runtime type-checking and then repeatedly
    # type-checking that variable rather than the computation required to
    # continually reacquire this child pith: e.g.,
    #
    #     # Type-checking conditional for "List[List[str]]" under Python < 3.8.
    #     if not (
    #         isinstance(__beartype_pith_0, list) and
    #         (
    #             isinstance(__beartype_pith_0[__beartype_random_int % len(__beartype_pith_0)], list) and
    #             isinstance(__beartype_pith_0[__beartype_random_int % len(__beartype_pith_0)][__beartype_random_int % len(__beartype_pith_0[__beartype_random_int % len(__beartype_pith_0)])], str) if __beartype_pith_0[__beartype_random_int % len(__beartype_pith_0)] else True
    #         ) if __beartype_pith_0 else True
    #     ):
    #
    #     # The same conditional under Python < 3.8.
    #     if not (
    #         isinstance(__beartype_pith_0, list) and
    #         (
    #             isinstance(__beartype_pith_1 := __beartype_pith_0[__beartype_random_int % len(__beartype_pith_0)], list) and
    #             isinstance(__beartype_pith_1[__beartype_random_int % len(__beartype_pith_1)], str) if __beartype_pith_1 else True
    #         ) if __beartype_pith_0 else True
    #     ):
    #
    # Note the localization of the random item selection from the root pith
    # (i.e., "__beartype_pith_1 := __beartype_pith_0[__beartype_random_int %
    # len(__beartype_pith_0)"), which only occurs once in the latter case
    # rather than repeatedly as in the former case. In both cases, the same
    # semantic type-checking is performed regardless of optimization.
    #
    # Note this optimization implicitly "bottoms out" when the currently
    # visited hint is *NOT* subscripted by one or more non-ignorable
    # PEP-compliant child hint arguments, as desired. If all child hints of the
    # currently visited hint are either ignorable (e.g., "object", "Any") *OR*
    # are non-ignorable non-"typing" types (e.g., "int", "str"), the currently
    # visited hint has *NO* meaningful PEP-compliant child hints and is thus
    # effectively a leaf node with respect to performing this optimization.
    # is_pith_curr_assign_expr = None

    # Integer suffixing the name of each local variable assigned the value of
    # the current pith in a Python >= 3.8-specific assignment expression, thus
    # uniquifying this variable in the body of the current wrapper function.
    #
    # Note that this integer is intentionally incremented as an efficient
    # low-level scalar rather than an inefficient high-level
    # "itertools.counter" object. Since both are equally thread-safe in the
    # internal context of this function body, the former is preferable.
    pith_curr_assign_expr_name_counter = 0

    # Python >= 3.8-specific assignment expression assigning this full Python
    # expression to the local variable assigned the value of this expression.
    pith_curr_assign_expr: str = None  # type: ignore[assignment]

    # Name of the local variable uniquely assigned to by
    # "pith_curr_assign_expr". Equivalently, this is the left-hand side (LHS)
    # of that assignment expression.
    pith_curr_assigned_expr: str = None  # type: ignore[assignment]

    # ..................{ HINT ~ label                      }..................
    # Human-readable label describing the root hint in exception messages.
    #
    # Note that the "hint_curr_label" should almost *ALWAYS* be used instead.
    HINT_ROOT_LABEL = EXCEPTION_CACHED_PLACEHOLDER

    # Human-readable label prefixing the machine-readable representation of the
    # currently visited type hint if this hint is nested (i.e., any hint
    # *except* the root type hint) in exception and warning messages.
    #
    # Note that the "hint_curr_label" should almost *ALWAYS* be used instead.
    HINT_CHILD_LABEL = f'{HINT_ROOT_LABEL} {repr(hint_root)} child'

    # Human-readable label prefixing the machine-readable representation of the
    # currently visited type hint in exception and warning messages.
    hint_curr_label = None

    # ..................{ METADATA                          }..................
    # Tuple of metadata describing the currently visited hint, appended by
    # the previously visited parent hint to the "hints_meta" stack.
    hint_curr_meta: tuple = None  # type: ignore[assignment]

    # Fixed list of all metadata describing all visitable hints currently
    # discovered by the breadth-first search (BFS) below. This lists acts as a
    # standard First In First Out (FILO) queue, enabling this BFS to be
    # implemented as an efficient imperative algorithm rather than an
    # inefficient (and dangerous, due to both unavoidable stack exhaustion and
    # avoidable infinite recursion) recursive algorithm.
    #
    # Note that this list is guaranteed by the previously called
    # _die_if_hint_repr_exceeds_child_limit() function to be larger than the
    # number of hints transitively visitable from this root hint. Ergo, *ALL*
    # indexation into this list performed by this BFS is guaranteed to be safe.
    # Ergo, avoid explicitly testing below that the "hints_meta_index_last"
    # integer maintained by this BFS is strictly less than "SIZE_BIG", as this
    # constraint is already guaranteed to be the case.
    hints_meta = acquire_fixed_list(SIZE_BIG)

    # 0-based index of metadata describing the currently visited hint in the
    # "hints_meta" list.
    hints_meta_index_curr = 0

    # 0-based index of metadata describing the last visitable hint in the
    # "hints_meta" list, initialized to "-1" to ensure that the initial
    # incrementation of this index by the _enqueue_hint_child() directly called
    # below initializes index 0 of the "hints_meta" fixed list.
    hints_meta_index_last = -1

    # ..................{ CLOSURES ~ hint : child           }..................
    # Closures centralizing frequently repeated logic and thus addressing any
    # Don't Repeat Yourself (DRY) concerns during the breadth-first search
    # (BFS) performed below.

    def _enqueue_hint_child(pith_child_expr: str) -> str:
        '''
        **Enqueue** (i.e., append) a new tuple of metadata describing the
        currently iterated child hint to the end of the ``hints_meta`` queue,
        enabling this hint to be visited by the ongoing breadth-first search
        (BFS) traversing over this queue.

        Parameters
        ----------
        pith_child_expr : str
            Python code snippet evaluating to the child pith to be
            type-checked against the currently iterated child hint.

        This closure also implicitly expects the following local variables of
        the outer scope to be set to relevant values:

        hint_child : object
            Currently iterated PEP-compliant child hint subscripting the
            currently visited hint.

        Returns
        ----------
        str
            Placeholder string to be subsequently replaced by code
            type-checking this child pith against this child hint.
        '''

        # Allow these local variables of the outer scope to be modified below.
        nonlocal \
            hint_child_placeholder_id, \
            hints_meta_index_last

        # Increment the 0-based index of metadata describing the last visitable
        # hint in the "hints_meta" list *BEFORE* overwriting the existing
        # metadata at this index.
        #
        # Note this index is guaranteed to *NOT* exceed the fixed length of
        # this list, by prior validation.
        hints_meta_index_last += 1

        # Increment the unique identifier of the currently iterated child hint.
        hint_child_placeholder_id += 1

        # Placeholder string to be globally replaced by code type-checking the
        # child pith against this child hint, intentionally prefixed and
        # suffixed by characters that:
        #
        # * Are intentionally invalid as Python code, guaranteeing that the
        #   top-level call to the exec() builtin performed by the @beartype
        #   decorator will raise a "SyntaxError" exception if the caller fails
        #   to replace all placeholder substrings generated by this method.
        # * Protect the identifier embedded in this substring against ambiguous
        #   global replacements of larger identifiers containing this
        #   identifier. If this identifier were *NOT* protected in this manner,
        #   then the first substring "0" generated by this method would
        #   ambiguously overlap with the subsequent substring "10" generated by
        #   this method, which would then produce catastrophically erroneous
        #   and non-trivial to debug Python code.
        hint_child_placeholder = (
            f'{PEP_CODE_HINT_CHILD_PLACEHOLDER_PREFIX}'
            f'{str(hint_child_placeholder_id)}'
            f'{PEP_CODE_HINT_CHILD_PLACEHOLDER_SUFFIX}'
        )

        # Create and insert a new tuple of metadata describing this child hint
        # at this index of this list.
        #
        # Note that this assignment is guaranteed to be safe, as "SIZE_BIG" is
        # guaranteed to be substantially larger than "hints_meta_index_last".
        hints_meta[hints_meta_index_last] = (
            hint_child,
            hint_child_placeholder,
            pith_child_expr,
            indent_child,
        )

        # Return this placeholder string.
        return hint_child_placeholder

    # Seed this list with metadata describing the root hint.
    hint_child_placeholder = _enqueue_hint_child(pith_root_expr)

    # ..................{ FUNC ~ code                       }..................
    # Python code snippet type-checking the current pith against the currently
    # visited hint (to be appended to the "func_code" string).
    func_curr_code = None

    # Python code snippet type-checking the root pith against the root hint,
    # localized separately from the "func_code" snippet to enable this function
    # to validate this code to be valid *BEFORE* returning this code.
    func_root_code = (
        f'{PEP_CODE_CHECK_HINT_ROOT_PREFIX}{hint_child_placeholder}')

    # Python code snippet to be returned, seeded with a placeholder to be
    # subsequently replaced on the first iteration of the breadth-first search
    # performed below with a snippet type-checking the root pith against the
    # root hint.
    func_code = func_root_code

    # True only if one or more PEP-compliant type hints visitable from this
    # root hint require a pseudo-random integer. If true, the higher-level
    # beartype._decor._code.codemain.generate_code() function prefixes the body
    # of this wrapper function with code generating such an integer.
    is_func_code_needs_random_int = False

    # ..................{ SEARCH                            }..................
    # While the 0-based index of metadata describing the next visited hint in
    # the "hints_meta" list does *NOT* exceed that describing the last
    # visitable hint in this list, there remains at least one hint to be
    # visited in the breadth-first search performed by this iteration.
    while hints_meta_index_curr <= hints_meta_index_last:
        # Metadata describing the currently visited hint.
        hint_curr_meta = hints_meta[hints_meta_index_curr]

        # Assert this metadata is a tuple as expected. This enables us to
        # distinguish between proper access of used items and improper access
        # of unused items of the parent fixed list containing this tuple, since
        # an unused item of this list is initialized to "None" by default.
        assert hint_curr_meta.__class__ is tuple, (
            f'Current hint metadata {repr(hint_curr_meta)} at '
            f'index {hints_meta_index_curr} not tuple.')

        # Localize metadatum for both efficiency and f-string purposes.
        hint_curr             = hint_curr_meta[_HINT_META_INDEX_HINT]
        hint_curr_placeholder = hint_curr_meta[_HINT_META_INDEX_PLACEHOLDER]
        pith_curr_expr        = hint_curr_meta[_HINT_META_INDEX_PITH_EXPR]
        indent_curr           = hint_curr_meta[_HINT_META_INDEX_INDENT]

        #FIXME: This test can be trivially avoided by:
        #* Initializing "hint_curr_label = HINT_ROOT_LABEL" above.
        #* Unconditionally setting "hint_curr_label = HINT_CHILD_LABEL"
        #  below at the end of each iteration of this loop.
        #
        #Since we're going to be fundamentally refactoring this entire
        #algorithm into a two-phase algorithm, let's hold off on that until the
        #radioactive dust settles, shall we?

        # Human-readable label prefixing the machine-readable representation of
        # the currently visited type hint in exception and warning messages.
        #
        # Note that this label intentionally only describes the root and
        # currently iterated child hints rather than the root hint, the
        # currently iterated child hint, and all interim child hints leading
        # from the former to the latter. The latter approach would be
        # non-human-readable and insane.
        hint_curr_label = (
            HINT_ROOT_LABEL
            if hints_meta_index_curr == 0 else
            HINT_CHILD_LABEL
        )

        # ................{ REDUCTION                         }................
        #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        # CAVEATS: Synchronize changes here with the corresponding block of the
        # beartype._decor._code._pep._error._peperrorsleuth.CauseSleuth.__init__()
        # method.
        #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        #
        # This logic reduces the currently visited hint to an arbitrary object
        # associated with this hint when this hint conditionally satisfies any
        # of various conditions.
        #
        # ................{ REDUCTION ~ pep 484               }................
        # If this is the PEP 484-compliant "None" singleton, reduce this hint
        # to the type of that singleton. While not explicitly defined by the
        # "typing" module, PEP 484 explicitly supports this singleton:
        #     When used in a type hint, the expression None is considered
        #     equivalent to type(None).
        if hint_curr is None:
            hint_curr = NoneType
        # If this is a PEP 484-compliant new type hint, reduce this hint to the
        # user-defined class aliased by this hint. Although this logic could
        # also be performed below, doing so here simplifies matters.
        elif is_hint_pep484_newtype(hint_curr):
            hint_curr = get_hint_pep484_newtype_class(hint_curr)
        # ................{ REDUCTION ~ pep 544               }................
        # If this is a PEP 484-compliant IO generic base class *AND* the active
        # Python interpreter targets at least Python >= 3.8 and thus supports
        # PEP 544-compliant protocols, reduce this functionally useless hint to
        # the corresponding functionally useful beartype-specific PEP
        # 544-compliant protocol implementing this hint.
        #
        # Note that PEP 484-compliant IO generic base classes are technically
        # usable under Python < 3.8 (e.g., by explicitly subclassing those
        # classes from third-party classes). Ergo, we can neither safely emit
        # warnings nor raise exceptions on visiting these classes under *ANY*
        # Python version.
        elif is_hint_pep544_io_generic(hint_curr):
            hint_curr = get_hint_pep544_io_protocol_from_generic(hint_curr)
        # ................{ REDUCTION ~ pep 593               }................
        # If this is a PEP 593-compliant type metahint, ignore all annotations
        # on this hint (i.e., "hint_curr.__metadata__" tuple) by reducing this
        # hint to its origin (e.g., "str" in "Annotated[str, 50, False]").
        elif is_hint_pep593(hint_curr):
            hint_curr = get_hint_pep593_hint(hint_curr)
        # ................{ REDUCTION ~ end                   }................

        #FIXME: Comment this sanity check out after we're sufficiently
        #convinced this algorithm behaves as expected. While useful, this check
        #requires a linear search over the entire code and is thus costly.
        # assert hint_curr_placeholder in func_code, (
        #     '{} {!r} placeholder {} not found in wrapper body:\n{}'.format(
        #         hint_curr_label, hint, hint_curr_placeholder, func_code))

        # ................{ PEP                               }................
        # If this hint is PEP-compliant...
        if is_hint_pep(hint_curr):
            #FIXME: Refactor to call warn_if_hint_pep_unsupported() instead.
            #Actually...wait. This is probably still a valid test here. We'll
            #need to instead augment the is_hint_ignorable() function to
            #additionally test whether the passed hint is unsupported, in which
            #case that function should return false as well as emit a non-fatal
            #warning ala the new warn_if_hint_pep_unsupported() function --
            #which should probably simply be removed now. *sigh*
            #FIXME: Actually, in that case, we can simply reduce the following
            #two calls to simply:
            #    die_if_hint_pep_ignorable(
            #        hint=hint_curr, hint_label=hint_curr_label)
            #Of course, this implies we want to refactor the
            #die_if_hint_pep_unsupported() function into
            #die_if_hint_pep_ignorable()... probably.

            # If this hint is currently unsupported, raise an exception.
            #
            # Note the human-readable label prefixing the representations of
            # child PEP-compliant type hints is unconditionally passed. Since
            # the root hint has already been validated to be supported by
            # the above call to the same function, this call is guaranteed to
            # *NEVER* raise an exception for that hint.
            die_if_hint_pep_unsupported(
                hint=hint_curr, hint_label=hint_curr_label)
            # Else, this hint is supported.

            # Assert that this hint is unignorable. Iteration below generating
            # code for child hints of the current parent hint is *REQUIRED* to
            # explicitly ignore ignorable child hints. Since the caller has
            # explicitly ignored ignorable root hints, these two guarantees
            # together ensure that all hints visited by this breadth-first
            # search *SHOULD* be unignorable. Naturally, we validate that here.
            assert not is_hint_ignorable(hint_curr), (
                f'{hint_curr_label} PEP type hint '
                f'{repr(hint_curr)} ignorable.')

            # Sign uniquely identifying this hint.
            hint_curr_sign = get_hint_pep_sign(hint_curr)

            # If this sign is currently unsupported, raise an exception.
            #
            # Note the human-readable label prefixing the representations of
            # child PEP-compliant type hints is unconditionally passed. Since
            # the root hint has already been validated to be supported by the
            # above call to the die_if_hint_pep_unsupported() function, this
            # call is guaranteed to *NEVER* raise exceptions for the root hint.
            die_if_hint_pep_sign_unsupported(
                hint_sign=hint_curr_sign, hint_label=hint_curr_label)
            # Else, this attribute is supported.

            # If this sign and thus this hint is deprecated, emit a non-fatal
            # warning warning users of this deprecation.
            # print(f'Testing {hint_curr_label} hint {repr(hint_curr)} for deprecation...')
            warn_if_hint_pep_sign_deprecated(
                hint=hint_curr,
                hint_sign=hint_curr_sign,
                hint_label=hint_curr_label,
            )

            # Tuple of all arguments subscripting this hint if any *OR* the
            # empty tuple otherwise (e.g., if this hint is its own unsubscripted
            # "typing" attribute).
            #
            # Note that the "__args__" dunder attribute is *NOT* guaranteed to
            # exist for arbitrary PEP-compliant type hints. Ergo, we obtain
            # this attribute via a higher-level utility getter instead.
            hint_childs = get_hint_pep_args(hint_curr)
            hint_childs_len = len(hint_childs)

            # Python code snippet expanding to the current level of indentation
            # appropriate for the currently iterated child hint.
            #
            # Note that this is almost always but technically *NOT* always
            # required below by logic generating code type-checking the
            # currently visited parent hint. Naturally, unconditionally setting
            # this string here trivially optimizes the common case.
            indent_child = indent_curr + CODE_INDENT_1

            #FIXME: Unit test that this is behaving as expected. Doing so will
            #require further generalizations, including:
            #* In the "beartype._decor.main" submodule:
            #  * Detect when running under tests.
            #  * When running under tests, define a new
            #    "func_wrapper.__beartype_wrapper_code" attribute added to
            #    decorated callables to be the "func_code" string rather than
            #    True. Note that this obviously isn't the right way to do
            #    source code association. Ideally, we'd at least interface with
            #    the stdlib "linecache" module (e.g., by calling the
            #    linecache.lazycache() function intended to be used to cache
            #    the source code for non-file-based modules) and possibly even
            #    go so far as to define a PEP 302-compatible beartype module
            #    loader. Clearly, that's out of scope. For now, this suffices.
            #* In the "beartype_test.a00_unit.data._data_hint_pep" submodule:
            #  * Add a new "_PepHintMetadata.code_str_match_regexes" field,
            #    defined as an iterable of regular expressions matching
            #    substrings of the "func_wrapper.__beartype_wrapper_code"
            #    attribute that are expected to exist.
            #  * For most "HINTS_PEP_META" entries, default this field to
            #    merely the empty tuple.
            #  * For deeply nested "HINTS_PEP_META" entries, define this
            #    field as follows:
            #        code_str_match_regexes=(r'\s+:=\s+',)
            #* In the "beartype_test.a00_unit.pep.p484.test_p484" submodule:
            #  * Match the "pep_hinted.__beartype_wrapper_code" string against
            #    all regular expressions in the "code_str_match_regexes"
            #    iterable for the currently iterated "pep_hint_meta".
            #
            #This is fairly important, as we have no other reusable means of
            #ascertaining whether this is actually being applied in general.
            #FIXME: That's all great, except for the
            #"func_wrapper.__beartype_wrapper_code" part. Don't do that,
            #please. We really do just want to do this right the first time. As
            #expected, the key to doing so is the linecache.lazycache()
            #function, whose implementation under Python 3.7 reads:
            #
            #    def lazycache(filename, module_globals):
            #        """Seed the cache for filename with module_globals.
            #
            #        The module loader will be asked for the source only when getlines is
            #        called, not immediately.
            #
            #        If there is an entry in the cache already, it is not altered.
            #
            #        :return: True if a lazy load is registered in the cache,
            #            otherwise False. To register such a load a module loader with a
            #            get_source method must be found, the filename must be a cachable
            #            filename, and the filename must not be already cached.
            #        """
            #        if filename in cache:
            #            if len(cache[filename]) == 1:
            #                return True
            #            else:
            #                return False
            #        if not filename or (filename.startswith('<') and filename.endswith('>')):
            #            return False
            #        # Try for a __loader__, if available
            #        if module_globals and '__loader__' in module_globals:
            #            name = module_globals.get('__name__')
            #            loader = module_globals['__loader__']
            #            get_source = getattr(loader, 'get_source', None)
            #
            #            if name and get_source:
            #                get_lines = functools.partial(get_source, name)
            #                cache[filename] = (get_lines,)
            #                return True
            #        return False
            #
            #Given that, what we need to do is:
            #* Define a new "beartype._decor._pep302" submodule implementing a
            #  PEP 302-compatible loader for @beartype-generated wrapper
            #  functions, enabling external callers (including the stdlib
            #  "linecache" module) to obtain the source for these functions.
            #  For space efficiency, this submodule should internally store
            #  code in a compressed format -- which probably means "gzip" for
            #  maximal portability. This submodule should at least define these
            #  attributes:
            #  * "_FUNC_WRAPPER_MODULE_NAME_TO_CODE", a dictionary mapping from
            #    the unique fake module names assigned to @beartype-generated
            #    wrapper functions by the @beartype decorator to the compressed
            #    source strings for those fake modules.
            #  * get_source(), a function accepting one unique fake module name
            #    assigned to an arbitrary @beartype-generated wrapper function
            #    by the @beartype decorator and returning the uncompressed
            #    source string for that fake module. Clearly, this function
            #    should internally access the
            #    "_FUNC_WRAPPER_MODULE_NAME_TO_CODE" dictionary and either:
            #    * If the passed module name has *NOT* already been registered
            #      to that dictionary, raise an exception.
            #    * Else, uncompress the compressed source string previously
            #      registered under that module name with that dictionary and
            #      return that uncompressed string. Don't worry about caching
            #      uncompressed strings here; that's exactly what the stdlib
            #      "linecache" module already does on our behalf.
            #    Ergo, this function should have signature resembling:
            #        def get_source(func_wrapper_module_name: str) -> str:
            #  * set_source(), a function accepting one unique fake module name
            #    assigned to an arbitrary @beartype-generated wrapper function
            #    by the @beartype decorator as well as as the uncompressed
            #    source string for that fake module. Clearly, this function
            #    should internally
            #    "_FUNC_WRAPPER_MODULE_NAME_TO_CODE" dictionary and either:
            #    * If the passed module name has already been registered to
            #      that dictionary, raise an exception.
            #    * Else, compress the passed uncompressed source string and
            #      register that compressed string under that module name with
            #      that dictionary.
            #* In the "beartype._decor.main" submodule:
            #  *

            # If...
            if (
                # The active Python interpreter targets Python >= 3.8 *AND*...
                IS_PYTHON_AT_LEAST_3_8 and
                # The current pith is *NOT* the root pith...
                #
                # Note that we explicitly test against piths rather than
                # seemingly equivalent metadata to account for edge cases.
                # Notably, child hints of unions (and possibly other "typing"
                # objects) do *NOT* narrow the current pith and are *NOT* the
                # root hint. Ergo, a seemingly equivalent test like
                # "hints_meta_index_curr != 0" would generate false positives
                # and thus unnecessarily inefficient code.
                pith_curr_expr != pith_root_expr
            ):
            # Then all conditions needed to assign the current pith to a unique
            # local variable via a Python >= 3.8-specific assignment expression
            # are satisfied. In this case...

                # Increment the integer suffixing the name of this variable
                # *BEFORE* defining this local variable.
                pith_curr_assign_expr_name_counter += 1

                # Reduce the current pith expression to the name of this local
                # variable.
                pith_curr_assigned_expr = (
                    PEP_CODE_PITH_NAME_PREFIX +
                    str(pith_curr_assign_expr_name_counter))

                # Python >= 3.8-specific assignment expression assigning this
                # full expression to this variable.
                pith_curr_assign_expr = (
                    PEP_CODE_PITH_ASSIGN_EXPR_format(
                        pith_curr_assigned_expr=pith_curr_assigned_expr,
                        pith_curr_expr=pith_curr_expr,
                    ))
            # Else, one or more of these conditions have *NOT* been satisfied.
            # In this case, preserve the Python code snippet evaluating to the
            # current pith as is.
            else:
                pith_curr_assign_expr = pith_curr_assigned_expr = (
                    pith_curr_expr)

            #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            # NOTE: Whenever adding support for (i.e., when generating code
            # type-checking) a new "typing" attribute below, similar support
            # for that attribute *MUST* also be added to the parallel:
            # * "beartype._util.hint.pep.peperror" submodule, which
            #   raises exceptions on the current pith failing this check.
            # * "beartype._util.hint.data.pep.utilhintdatapep.HINT_PEP_SIGNS_SUPPORTED_DEEP"
            #   frozen set of all supported unsubscripted "typing" attributes
            #   for which this function generates deeply type-checking code.
            #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

            # Switch on (as in, pretend Python provides a "switch" statement)
            # this attribute to decide which type of code to generate to
            # type-check the current pith against the current hint.
            #
            # This decision is intentionally implemented as a linear series of
            # tests ordered in descending likelihood for efficiency. While
            # alternative implementations (that are more readily readable and
            # maintainable) do exist, these alternatives all appear to be
            # substantially less efficient.
            #
            # Consider the standard alternative of sequestering the body of
            # each test implemented below into either:
            #
            # * A discrete private function called by this function. This
            #   approach requires maintaining a global private dictionary
            #   mapping from each support unsubscripted typing attribute to
            #   the function generating code for that attribute: e.g.,
            #      def pep_code_check_union(...): ...
            #      _HINT_TYPING_ATTR_ARGLESS_TO_CODER = {
            #          typing.Union: pep_code_check_union,
            #      }
            #   Each iteration of this loop then looks up the function
            #   generating code for the current attribute from this dictionary
            #   and calls that function to do so. Function calls come with
            #   substantial overhead in Python, impacting performance more
            #   than the comparable linear series of tests implemented below.
            #   Additionally, these functions *MUST* mutate local variables of
            #   this function by some arcane means -- either:
            #   * Passing these locals to each such function, returning these
            #     locals from each such function, and assigning these return
            #     values to these locals in this function after each such call.
            #   * Passing a single composite fixed list of these locals to each
            #     such function, which then mutates these locals in-place,
            #     which then necessitates this function permanently store these
            #     locals in such a list rather than as local variables.
            # * A discrete closure of this function, which adequately resolves
            #   the aforementioned locality issue via the "nonlocal" keyword at
            #   a substantial up-front performance cost of redeclaring these
            #   closures on each invocation of this function.

            # ..............{ UNIONS                            }..............
            # If this hint is a union (e.g., "typing.Union[bool, str]",
            # typing.Optional[float]")...
            #
            # Note that unions are non-physical abstractions of physical types
            # and are thus *NOT* type-checked; only the subscripted arguments
            # of unions are type-checked. This differs from "typing"
            # pseudo-containers like "List[int]", in which both the parent
            # "List" and child "int" types represent physical types to be
            # type-checked. Ergo, unions themselves impose no narrowing of the
            # current pith expression and thus *CANNOT* by definition benefit
            # from Python >= 3.8-specific assignment expressions -- unlike
            # standard sequences, for example, which typically narrow the
            # current pith expression and thus do benefit from these
            # expressions.
            if hint_curr_sign in HINT_PEP484_SIGNS_UNION:
                # Assert this union is subscripted by one or more child hints.
                # Note this should *ALWAYS* be the case, as:
                #
                # * The unsubscripted "typing.Union" object is explicitly
                #   listed in the "HINTS_IGNORABLE_SHALLOW" set and should thus
                #   have already been ignored when present.
                # * The "typing" module explicitly prohibits empty
                #   subscription: e.g.,
                #       >>> typing.Union[]
                #       SyntaxError: invalid syntax
                #       >>> typing.Union[()]
                #       TypeError: Cannot take a Union of no types.
                assert hint_childs, (
                    f'{hint_curr_label} PEP union type hint '
                    f'{repr(hint_curr)} unsubscripted.')
                # Else, this union is subscripted by two or more arguments. Why
                # two rather than one? Because the "typing" module reduces
                # unions of one argument to that argument: e.g.,
                #     >>> import typing
                #     >>> typing.Union[int]
                #     int

                # Acquire a pair of sets for use in prefiltering child hints
                # into the subset of all PEP-noncompliant and -compliant child
                # hints subscripting this union. For efficiency, reuse
                # previously created sets if available.
                #
                # Since these child hints require fundamentally different forms
                # of type-checking, prefiltering child hints into these sets
                # *BEFORE* generating code type-checking these child hints
                # improves both efficiency and maintainability below.
                hint_childs_nonpep = acquire_object_typed(set)
                hint_childs_pep = acquire_object_typed(set)

                # Clear these sets prior to use below.
                hint_childs_nonpep.clear()
                hint_childs_pep.clear()

                # For each subscripted argument of this union...
                for hint_child in hint_childs:
                    # Assert that this child hint is *NOT* shallowly ignorable.
                    # Why? Because any union containing one or more shallowly
                    # ignorable child hints is deeply ignorable and should thus
                    # have already been ignored after a call to the
                    # is_hint_ignorable() tester passed this union on handling
                    # the parent hint of this union.
                    assert hint_child not in HINTS_IGNORABLE_SHALLOW, (
                        f'{hint_curr_label} ignorable PEP union type hint '
                        f'{repr(hint_curr)} not ignored.')

                    # If this child hint is PEP-compliant...
                    if is_hint_pep(hint_child):
                        # Filter this child hint into the set of PEP-compliant
                        # child hints.
                        #
                        # Note that this PEP-compliant child hint *CANNOT* also
                        # be filtered into the set of PEP-noncompliant child
                        # hints, even if this child hint originates from a
                        # non-"typing" type (e.g., "List[int]" from "list").
                        # Why? Because that would then induce false positives
                        # when the current pith shallowly satisfies this
                        # non-"typing" type but does *NOT* deeply satisfy this
                        # child hint.
                        hint_childs_pep.add(hint_child)
                    # Else, this child hint is PEP-noncompliant. In this case,
                    # filter this child hint into the list of PEP-noncompliant
                    # arguments.
                    else:
                        hint_childs_nonpep.add(hint_child)

                # Initialize the code type-checking the current pith against
                # these arguments to the substring prefixing all such code.
                func_curr_code = PEP484_CODE_CHECK_HINT_UNION_PREFIX

                # If this union is subscripted by one or more PEP-noncompliant
                # child hints, generate and append efficient code type-checking
                # these child hints *BEFORE* less efficient code type-checking
                # any PEP-compliant child hints subscripting this union.
                if hint_childs_nonpep:
                    func_curr_code += (
                        PEP484_CODE_CHECK_HINT_UNION_CHILD_NONPEP_format(
                            # Python expression yielding the value of the
                            # current pith. Specifically...
                            pith_curr_expr=(
                                # If this union is subscripted by one or more
                                # PEP-compliant child hints, prefer the
                                # expression assigning this value to a local
                                # variable efficiently reused by subsequent
                                # code generated for PEP-compliant child hints.
                                pith_curr_assign_expr if hint_childs_pep else
                                # Else, this union is *NOT* subscripted by one
                                # or more PEP-compliant child hints. Since this
                                # is the first and only test generated for this
                                # union, prefer the expression yielding the
                                # value of the current pith *WITHOUT* assigning
                                # this value to a local variable, which would
                                # otherwise pointlessly go unused.
                                pith_curr_expr
                            ),
                            # Python expression evaluating to a tuple of these
                            # arguments when accessed via the private
                            # "__beartypistry" parameter.
                            #
                            # Note that:
                            # * We would ideally avoid coercing this set into a
                            #   tuple when this set only contains one type by
                            #   passing that type directly to the
                            #   register_typistry_type() function. Sadly, the
                            #   "set" class defines no convenient or efficient
                            #   means of retrieving the only item of a 1-set.
                            #   Indeed, the most efficient means of doing so is
                            #   to iterate over that set and immediately break:
                            #     for first_item in muh_set: break
                            #   While we *COULD* technically leverage that
                            #   approach here, doing so would also mandate
                            #   adding a number of intermediate tests, which
                            #   would certainly reduce any performance gains.
                            #   Ultimately, we avoid doing so by falling back
                            #   to the standard approach. See also this
                            #   relevant self-StackOverflow post:
                            #       https://stackoverflow.com/a/40054478/2809027
                            # * These parameters are intentionally passed as
                            #   positional rather than keyword arguments for
                            #   optimal memoization efficiency.
                            hint_curr_expr=register_typistry_tuple(
                                tuple(hint_childs_nonpep),
                                # Inform this function it needn't attempt to
                                # uselessly omit duplicates, since the "typing"
                                # module already does so for all "Union"
                                # arguments. Well, that's nice.
                                True,
                            )
                        ))

                # For each PEP-compliant child hint of this union, generate and
                # append code type-checking this child hint.
                for hint_child_index, hint_child in enumerate(hint_childs_pep):
                    func_curr_code += (
                        PEP484_CODE_CHECK_HINT_UNION_CHILD_PEP_format(
                            # Python expression yielding the value of the
                            # current pith.
                            hint_child_placeholder=_enqueue_hint_child(
                                # If this union is subscripted by either...
                                #
                                # Then prefer the expression efficiently
                                # reusing the value previously assigned to a
                                # local variable by either the above
                                # conditional or prior iteration of the current
                                # conditional.
                                pith_curr_assigned_expr
                                if (
                                    # One or more PEP-noncompliant child hints
                                    # *OR*...
                                    hint_childs_nonpep or
                                    # This is any PEP-compliant child hint but
                                    # the first...
                                    hint_child_index > 1
                                ) else
                                # Else, this union is both subscripted by no
                                # PEP-noncompliant child hints *AND* this is
                                # the first PEP-compliant child hint, prefer
                                # the expression assigning this value to a
                                # local variable efficiently reused by code
                                # generated by the following "else" condition
                                # under subsequent iteration.
                                #
                                # Note this child hint is guaranteed to be at
                                # least one more child hint. Why? Because the
                                # "typing" module forces unions to be
                                # subscripted by two or more child hints. By
                                # deduction, this union must thus be
                                # subscripted by two or more PEP-compliant
                                # child hints. Ergo, we needn't explicitly
                                # validate that constraint here.
                                pith_curr_assign_expr
                            )))

                # If this code is *NOT* its initial value, this union is
                # subscripted by one or more unignorable child hints and the
                # above logic generated code type-checking these child hints.
                # In this case...
                if func_curr_code is not PEP484_CODE_CHECK_HINT_UNION_PREFIX:
                    # Munge this code to...
                    func_curr_code = (
                        # Strip the erroneous " or" suffix appended by the
                        # last child hint from this code.
                        func_curr_code[:-_OPERATOR_SUFFIX_LEN_OR] +
                        # Suffix this code by the substring suffixing all such
                        # code.
                        PEP484_CODE_CHECK_HINT_UNION_SUFFIX
                    # Format the "indent_curr" prefix into this code deferred
                    # above for efficiency.
                    ).format(indent_curr=indent_curr)
                # Else, this snippet is its initial value and thus ignorable.

                # Release this pair of sets back to their respective pools.
                release_object_typed(hint_childs_nonpep)
                release_object_typed(hint_childs_pep)
            # Else, this hint is *NOT* a union.

            # ..............{ GENERIC or PROTOCOL               }..............
            # If this hint is either a:
            # * PEP 484-compliant generic (i.e., user-defined class subclassing
            #   a combination of one or more of the "typing.Generic" superclass
            #   and other "typing" non-class pseudo-superclasses).
            # * PEP 544-compliant protocol (i.e., class subclassing a
            #   combination of one or more of the "typing.Protocol" superclass
            #   and other "typing" non-class pseudo-superclasses).
            # * PEP 585-compliant generic (i.e., user-defined class subclassing
            #   at least one non-class PEP 585-compliant pseudo-superclasses).
            # Then this hint is a PEP-compliant generic. In this case...
            elif hint_curr_sign is Generic:
                #FIXME: *THIS IS NON-IDEAL.* Ideally, we should propagate *ALL*
                #child type hints subscripting a generic up to *ALL*
                #pseudo-superclasses of that generic (e.g., the "int" child
                #hint subscripting a parent hint "MuhGeneric[int]" of type
                #"class MuhGeneric(list[T]): pass" up to its "list[T]"
                #pseudo-superclass).
                #
                #For now, we just strip *ALL* child type hints subscripting a
                #generic with the following call. This suffices, because we
                #just need this to work. So it goes, uneasy code bedfellows.

                # If this hint is *NOT* a class, this hint is *NOT* an
                # unsubscripted generic but could still be a generic
                # subscripted by one or more PEP-compliant child type hints.
                #
                # To decide, reduce this hint to the object originating this
                # hint if any, enabling the subsequent assertion to assert
                # whether this origin object is an unsubscripted generic, which
                # would then imply this hint to be a subscripted generic. If
                # this strikes you as insane, you're not alone.
                hint_curr = get_hint_pep_generic_type_or_none(hint_curr)

                # Assert this hint to be a class.
                assert isinstance(hint_curr, type), (
                    f'{hint_curr_label} PEP generic type hint '
                    f'{repr(hint_curr)} not class.')

                # Tuple of the one or more unerased pseudo-superclasses
                # originally listed as superclasses prior to their type erasure
                # subclassed by this generic.
                hint_childs = get_hint_pep_generic_bases_unerased(hint_curr)

                # Initialize the code type-checking the current pith against
                # this generic to the substring prefixing all such code.
                func_curr_code = PEP_CODE_CHECK_HINT_GENERIC_PREFIX

                # For each pseudo-superclass subclassed by this generic...
                for hint_child in hint_childs:
                    # print(f'hint_child: {repr(hint_child)} {is_hint_pep_type_typing(hint_child)}')

                    # If this pseudo-superclass is an actual class, this class
                    # is effectively ignorable. Why? Because the
                    # "PEP_CODE_CHECK_HINT_GENERIC_PREFIX" snippet leveraged
                    # above already type-checks this pith against the generic
                    # subclassing this superclass and thus this superclass as
                    # well with a trivial isinstance() call. In this case, skip
                    # to the next pseudo-superclass.
                    if isinstance(hint_child, type):
                        continue
                    # Else, this pseudo-superclass is *NOT* an actual class.
                    #
                    # If this pseudo-superclass is neither a PEP 585-compliant
                    # type hint *NOR* a PEP-compliant type hint defined by the
                    # "typing" module, this pseudo-superclass *MUST* be a PEP
                    # 585-noncompliant user-defined pseudo-superclass. In this
                    # case, reduce this pseudo-superclass to the corresponding
                    # actual superclass originating this pseudo-superclass.
                    #
                    # Note that:
                    # * This horrible, irrational, and unintuitive edge case
                    #   arises *ONLY* for user-defined PEP 484-compliant
                    #   generics and PEP 544-compliant protocols subclassing
                    #   another user-defined generic or protocol superclass
                    #   subscripted by one or more type variables: e.g.,
                    #     >>> import typing as t
                    #     >>> class UserProtocol(t.Protocol[t.AnyStr]): pass
                    #     >>> class UserSubprotocol(UserProtocol[str], t.Protocol): pass
                    #     >>> UserSubprotocol.__orig_bases__
                    #     (UserProtocol[bytes], typing.Protocol)
                    #     >>> UserProtocolUnerased = UserSubprotocol.__orig_bases__[0]
                    #     >>> UserProtocolUnerased is UserProtocol
                    #     False
                    #     >>> isinstance(UserProtocolUnerased, type)
                    #     False
                    # * PEP 585-compliant generics suffer no such issues:
                    #     >>> from beartype._util.hint.pep.proposal.utilhintpep585 import is_hint_pep585_builtin
                    #     >>> class UserGeneric(list[int]): pass
                    #     >>> class UserSubgeneric(UserGeneric[int]): pass
                    #     >>> UserSubgeneric.__orig_bases__
                    #     (UserGeneric[int],)
                    #     >>> UserGenericUnerased = UserSubgeneric.__orig_bases__[0]
                    #     >>> isinstance(UserGenericUnerased, type)
                    #     True
                    #     >>> UserGenericUnerased.__mro__
                    #     (UserGeneric, list, object)
                    #     >>> is_hint_pep585_builtin(UserGenericUnerased)
                    #     True
                    #
                    # Walking up the unerased inheritance hierarchy for this
                    # generic or protocol iteratively visits the user-defined
                    # generic or protocol pseudo-superclass subscripted by one
                    # or more type variable. Due to poorly defined obscurities
                    # in the "typing" implementation, this pseudo-superclass is
                    # *NOT* actually a class but rather an instance of a
                    # private "typing" class (e.g., "typing._SpecialForm").
                    #
                    # Ergo, this pseudo-superclass will be subsequently
                    # detected as neither a generic nor "typing" object and
                    # thus raise exceptions. Our only recourse is to silently
                    # reduce this hint into the erased superclass to which the
                    # "typing" module previously transformed this hint (e.g.,
                    # "UserProtocol" above). This is slightly non-ideal, as
                    # this erased superclass is an actual class that should
                    # ideally be ignored rather than redundantly tested against
                    # the current pith again. Nonetheless, there exists no
                    # other means of recursing into the possibly relevant
                    # superclasses of this erased superclass.
                    #
                    # Note that, in theory, we could deeply refactor this
                    # algorithm to support the notion of child hints that
                    # should be ignored for purposes of type-checking but
                    # nonetheless recursed into. In practice, the current
                    # approach only introduces mild runtime inefficiencies
                    # while preserving sanity throughout this algorithm.
                    #
                    # Specifically, perform this awful reduction *ONLY* if
                    # this child hint is a PEP 484- or 544-compliant
                    # user-defined pseudo-superclass that is neither...
                    elif not (
                        # A PEP 585-compliant pseudo-superclass *NOR*...
                        is_hint_pep585_builtin(hint_child) and
                        # A PEP 484- or 544-compliant pseudo-superclass defined
                        # by the "typing" module.
                        is_hint_pep_typing(hint_child)
                    ):
                        hint_child = (
                            get_hint_pep484_generic_base_erased_from_unerased(
                                hint_child))
                    # Else, this pseudo-superclass is defined by the "typing"
                    # module.

                    # If this superclass is ignorable, do so.
                    if is_hint_ignorable(hint_child):
                        continue
                    # Else, this superclass is unignorable.

                    # Generate and append code type-checking this pith against
                    # this superclass.
                    func_curr_code += (
                        PEP_CODE_CHECK_HINT_GENERIC_CHILD_format(
                            hint_child_placeholder=_enqueue_hint_child(
                                # Python expression efficiently reusing the
                                # value of this pith previously assigned to a
                                # local variable by the prior prefix.
                                pith_curr_assigned_expr),
                        ))

                # Munge this code to...
                func_curr_code = (
                    # Strip the erroneous " and" suffix appended by the last
                    # child hint from this code.
                    func_curr_code[:-_OPERATOR_SUFFIX_LEN_AND] +
                    # Suffix this code by the substring suffixing all such
                    # code.
                    PEP_CODE_CHECK_HINT_GENERIC_SUFFIX
                # Format...
                ).format(
                    # Indentation deferred above for efficiency.
                    indent_curr=indent_curr,
                    pith_curr_assign_expr=pith_curr_assign_expr,
                    # Python expression evaluating to this user-defined type
                    # when accessed via the private "__beartypistry" parameter.
                    hint_curr_expr=register_typistry_type(hint_curr),
                )
                # print(f'{hint_curr_label} PEP generic {repr(hint)} handled.')
            # Else, this hint is *NOT* a generic.

            # ..............{ FORWARDREF                        }..............
            # If this hint is a forward reference...
            elif hint_curr_sign is HINT_PEP484_BASE_FORWARDREF:
                # Possibly unqualified classname referred to by this hint.
                hint_curr_forwardref_classname = get_hint_forwardref_classname(
                    hint_curr)

                # If this classname contains one or more "." characters, this
                # classname is fully-qualified. In this case...
                if '.' in hint_curr_forwardref_classname:
                    # Python expression evaluating to this class when accessed
                    # via the private "__beartypistry" parameter.
                    hint_curr_expr = register_typistry_forwardref(
                        hint_curr_forwardref_classname)
                # Else, this classname is unqualified. In this case...
                else:
                    # If the set of unqualified classnames referred to by all
                    # relative forward references has yet to be instantiated,
                    # do so.
                    if hints_forwardref_class_basename is None:
                        hints_forwardref_class_basename = set()
                    # In any case, this set now exists.

                    # Add this unqualified classname to this set.
                    hints_forwardref_class_basename.add(
                        hint_curr_forwardref_classname)

                    # Placeholder substring to be replaced by the caller with a
                    # Python expression evaluating to this unqualified
                    # classname canonicalized relative to the module declaring
                    # the currently decorated callable when accessed via the
                    # private "__beartypistry" parameter.
                    hint_curr_expr = (
                        f'{PEP_CODE_HINT_FORWARDREF_UNQUALIFIED_PLACEHOLDER_PREFIX}'
                        f'{hint_curr_forwardref_classname}'
                        f'{PEP_CODE_HINT_FORWARDREF_UNQUALIFIED_PLACEHOLDER_SUFFIX}'
                    )

                # Code type-checking the current pith against this class.
                func_curr_code = PEP_CODE_CHECK_HINT_NONPEP_TYPE_format(
                    pith_curr_expr=pith_curr_expr,
                    hint_curr_expr=hint_curr_expr,
                )
            # Else, this hint is *NOT* a forward reference.

            # ..............{ NORETURN                          }..............
            # If this hint is the PEP 484-compliant "NoReturn" singleton valid
            # *ONLY* as the non-nested return annotation of a callable, raise
            # an exception. This singleton is invalid when subscripting *ANY*
            # PEP-compliant type hint (e.g., "typing.List[typing.NoReturn]"),
            # which is guaranteed to be the case if this conditional is true.
            # Why? Because the previously called higher-level
            # pep_code_check_return() function has already handled the single
            # edge case in which this singleton is contextually valid, implying
            # this singleton to be invalid here.
            elif hint_curr is NoReturn:
                raise BeartypeDecorHintPep484Exception(
                    f'{hint_curr_label} PEP type hint '
                    f'{repr(hint_curr)} nesting "typing.NoReturn" invalid '
                    f'(i.e., as "typing.NoReturn" valid only as a '
                    f'non-nested return annotation).'
                )
            # Else, this hint is *NOT* "NoReturn".

            # ..............{ SHALLOW or ARGUMENTLESS           }..............
            # If this hint either...
            elif (
                # Is not yet deeply supported by this function *OR*...
                hint_curr_sign not in HINT_PEP_SIGNS_SUPPORTED_DEEP or
                # Is deeply supported by this function but is its own sign
                # (e.g., "typing.List" rather than "typing.List[str]") and is
                # thus subscripted by *NO* child hints...
                hint_curr is hint_curr_sign
            ):
            # Then generate trivial code shallowly type-checking the current
            # pith as an instance of the non-"typing" origin type originating
            # this sign (e.g., "list" for the sign "typing.List" identifying
            # hint "typing.List[int]").

                # Code type-checking the current pith against this origin type.
                func_curr_code = PEP_CODE_CHECK_HINT_NONPEP_TYPE_format(
                    pith_curr_expr=pith_curr_expr,
                    # Python expression evaluating to this origin type when
                    # accessed via the private "__beartypistry" parameter.
                    hint_curr_expr=register_typistry_type(
                        # Origin type of this hint if any *OR* raise an
                        # exception -- which should *NEVER* happen, as this
                        # hint was validated above to be supported.
                        get_hint_pep_stdlib_type(hint_curr)),
                )
            # Else, this hint is *NOT* its own unsubscripted "typing" attribute
            # (e.g., "typing.List") and is thus subscripted by one or more
            # child hints.

            # ............{ SEQUENCES ~ standard OR tuple vari. }..............
            # If this hint is either...
            elif (
                # A standard sequence (e.g., "typing.List[int]") *OR*...
                hint_curr_sign in HINT_PEP_SIGNS_SEQUENCE_STANDARD or (
                    # A tuple *AND*...
                    hint_curr_sign in HINT_PEP_SIGNS_TUPLE and
                    # This tuple is subscripted by exactly two child hints
                    # *AND*...
                    hint_childs_len == 2 and
                    # The second child hint is just an unquoted ellipsis...
                    hint_childs[1] is Ellipsis
                )
                # Then this hint is of the form "Tuple[{typename}, ...]",
                # typing a tuple accepting a variadic number of items all
                # satisfying the "{typename}" child hint. Since this case is
                # semantically equivalent to that of standard sequences, we
                # transparently handle both here for maintainability.
                #
                # See below for logic handling the fixed-length "Tuple" form.
            ):
            # Then this hint is either a standard sequence *OR* a similar hint
            # semantically resembling a standard sequence, subscripted by one
            # or more child hints.

                # Python expression evaluating to this origin type when
                # accessed with the private "__beartypistry" parameter.
                hint_curr_expr = register_typistry_type(
                    # Origin type of this attribute if any *OR* raise an
                    # exception -- which should *NEVER* happen, as all standard
                    # sequences originate from an origin type.
                    get_hint_pep_stdlib_type(hint_curr))

                # Assert this sequence is either subscripted by exactly one
                # argument *OR* a non-standard sequence (e.g., "typing.Tuple").
                # Note that the "typing" module should have already guaranteed
                # this on our behalf. Still, we trust nothing and no one:
                #     >>> import typing as t
                #     >>> t.List[int, str]
                #     TypeError: Too many parameters for typing.List; actual 2, expected 1
                assert (
                    hint_childs_len == 1 or
                    hint_curr_sign in HINT_PEP_SIGNS_TUPLE
                ), (
                    f'{hint_curr_label} PEP sequence type hint '
                    f'{repr(hint_curr)} subscripted by multiple arguments.')

                # Lone child hint of this parent hint.
                hint_child = hint_childs[0]

                # If this child hint is *NOT* ignorable, deeply type-check both
                # the type of the current pith *AND* a randomly indexed item of
                # this pith. Specifically...
                if not is_hint_ignorable(hint_child):
                    # Record that a pseudo-random integer is now required.
                    is_func_code_needs_random_int = True

                    # Code type-checking the current pith against this type.
                    func_curr_code = (
                        PEP_CODE_CHECK_HINT_SEQUENCE_STANDARD_format(
                            indent_curr=indent_curr,
                            pith_curr_assign_expr=pith_curr_assign_expr,
                            pith_curr_assigned_expr=pith_curr_assigned_expr,
                            hint_curr_expr=hint_curr_expr,
                            hint_child_placeholder=_enqueue_hint_child(
                                # Python expression yielding the value of a
                                # randomly indexed item of the current pith
                                # (i.e., standard sequence) to be type-checked
                                # against this child hint.
                                PEP_CODE_CHECK_HINT_SEQUENCE_STANDARD_PITH_CHILD_EXPR_format(
                                    pith_curr_assigned_expr=(
                                        pith_curr_assigned_expr))),
                        ))
                # Else, this child hint is ignorable. In this case,
                # fallback to generating trivial code shallowly
                # type-checking the current pith as an instance of this
                # origin type.
                else:
                    func_curr_code = PEP_CODE_CHECK_HINT_NONPEP_TYPE_format(
                        pith_curr_expr=pith_curr_expr,
                        hint_curr_expr=hint_curr_expr,
                    )
            # Else, this hint is neither a standard sequence *NOR* variadic
            # tuple.

            # ..............{ SEQUENCES ~ tuple : fixed         }..............
            # If this hint is a tuple, this tuple is *NOT* of the variadic form
            # and *MUST* thus be of the fixed-length form.
            #
            # Note that if this hint is a:
            # * PEP 484-compliant "typing.Tuple"-based hint, this hint is
            #   guaranteed to contain one or more child hints. Moreover, if
            #   this hint contains exactly one child hint that is the empty
            #   tuple, this hint is the empty fixed-length form
            #   "typing.Tuple[()]".
            # * PEP 585-compliant "tuple"-based hint, this hint is *NOT*
            #   guaranteed to contain one or more child hints. If this hint
            #   contains *NO* child hints, this hint is equivalent to the empty
            #   fixed-length PEP 484-compliant form "typing.Tuple[()]". Yes,
            #   PEP 585 even managed to violate PEP 484-compliance. UUUURGH!
            #
            # While tuples are sequences, the "typing.Tuple" singleton that
            # types tuples violates the syntactic norms established for other
            # standard sequences by concurrently supporting two different
            # syntaxes with equally different semantics:
            # * "typing.Tuple[{typename}, ...]", typing a tuple whose items all
            #   satisfy the "{typename}" child hint. Note that the "..."
            #   substring here is a literal ellipses.
            # * "typing.Tuple[{typename1}, {typename2}, ..., {typenameN}]",
            #   typing a tuple whose:
            #   * First item satisfies the "{typename1}" child hint.
            #   * Second item satisfies the "{typename2}" child hint.
            #   * Last item satisfies the "{typenameN}" child hint.
            #   Note that the "..." substring here is *NOT* a literal ellipses.
            #
            # This is what happens when non-human-readable APIs are promoted.
            elif hint_curr_sign in HINT_PEP_SIGNS_TUPLE:
                # Assert this tuple was subscripted by at least one child hint
                # if this tuple is PEP 484-compliant. Note that the "typing"
                # module should have already guaranteed this on our behalf.
                # Trust is for the weak. See above for further commentary.
                assert hint_curr_sign is tuple or hint_childs, (
                    f'{hint_curr_label} PEP 484 fixed-length tuple type hint '
                    f'{repr(hint_curr)} empty.')

                # Assert this tuple is *NOT* of the syntactic form
                # "typing.Tuple[{typename}, ...]" handled by prior logic.
                assert (
                    hint_childs_len <= 1 or
                    hint_childs[1] is not Ellipsis
                ), (
                    f'{hint_curr_label} PEP variadic tuple type hint '
                    f'{repr(hint_curr)} unhandled.')

                # Initialize the code type-checking the current pith against
                # this tuple to the substring prefixing all such code.
                func_curr_code = PEP_CODE_CHECK_HINT_TUPLE_FIXED_PREFIX

                # If this hint is the empty fixed-length tuple, generate and
                # append code type-checking the current pith to be the empty
                # tuple. Yes, this edge case constitutes a code smell.
                if is_hint_pep_tuple_empty(hint_curr):
                    func_curr_code += (
                        PEP_CODE_CHECK_HINT_TUPLE_FIXED_EMPTY_format(
                            pith_curr_assigned_expr=pith_curr_assigned_expr))
                # Else, that ridiculous edge case does *NOT* apply. In this
                # case...
                else:
                    # Append code type-checking the length of this pith.
                    func_curr_code += (
                        PEP_CODE_CHECK_HINT_TUPLE_FIXED_LEN_format(
                            pith_curr_assigned_expr=pith_curr_assigned_expr,
                            hint_childs_len=hint_childs_len,
                        ))

                    # For each child hint of this tuple...
                    for hint_child_index, hint_child in enumerate(hint_childs):
                        # If this child hint is ignorable, skip to the next.
                        if is_hint_ignorable(hint_child):
                            continue
                        # Else, this child hint is unignorable.

                        # Append code type-checking this child pith.
                        func_curr_code += (
                            PEP_CODE_CHECK_HINT_TUPLE_FIXED_NONEMPTY_CHILD_format(
                                hint_child_placeholder=_enqueue_hint_child(
                                    # Python expression yielding the value of
                                    # the currently indexed item of this tuple to
                                    # be type-checked against this child hint.
                                    PEP_CODE_CHECK_HINT_TUPLE_FIXED_NONEMPTY_PITH_CHILD_EXPR_format(
                                        pith_curr_assigned_expr=(
                                            pith_curr_assigned_expr),
                                        pith_child_index=hint_child_index)),
                            ))

                # Munge this code to...
                func_curr_code = (
                    # Strip the erroneous " and" suffix appended by the
                    # last child hint from this code.
                    func_curr_code[:-_OPERATOR_SUFFIX_LEN_AND] +
                    # Suffix this code by the substring suffixing all such
                    # code.
                    PEP_CODE_CHECK_HINT_TUPLE_FIXED_SUFFIX
                # Format the "indent_curr" prefix into this code deferred
                # above for efficiency.
                ).format(
                    indent_curr=indent_curr,
                    pith_curr_assign_expr=pith_curr_assign_expr,
                    # Python expression evaluating to the builtin "tuple" type
                    # when accessed via the private "__beartypistry" parameter.
                    hint_curr_expr=register_typistry_type(tuple),
                )
            # Else, this hint is *NOT* a tuple.

            # ..............{ UNSUPPORTED                       }..............
            # Else, this hint is neither shallowly nor deeply supported and is
            # thus unsupported. Since an exception should have already been
            # raised above in this case, this conditional branch *NEVER* be
            # triggered. Nonetheless, raise an exception for safety.
            else:
                raise BeartypeDecorHintPepUnsupportedException(
                    f'{hint_curr_label} PEP type hint '
                    f'{repr(hint_curr)} unsupported but '
                    f'erroneously detected as supported.'
                )

        # ................{ NON-PEP                           }................
        # Else, this hint is *NOT* PEP-compliant.
        #
        # ................{ CLASSES                           }................
        # If this hint is a non-"typing" class...
        #
        # Note that:
        #
        # * This test is intentionally performed *AFTER* that testing whether
        #   this hint is PEP-compliant, thus guaranteeing this hint to be a
        #   PEP-noncompliant non-"typing" class rather than a PEP-compliant
        #   type hint originating from such a class. Since many hints are both
        #   PEP-compliant *AND* originate from such a class (e.g., the "List"
        #   in "List[int]", PEP-compliant but originating from the
        #   PEP-noncompliant builtin class "list"), testing these hints first
        #   for PEP-compliance ensures we generate non-trivial code deeply
        #   type-checking these hints instead of trivial code only shallowly
        #   type-checking the non-"typing" classes from which they originate.
        # * This class is guaranteed to be a subscripted argument of a
        #   PEP-compliant type hint (e.g., the "int" in "Union[Dict[str, str],
        #   int]") rather than the root type hint. Why? Because if this class
        #   were the root type hint, it would have already been passed into a
        #   faster submodule generating PEP-noncompliant code instead.
        elif isinstance(hint_curr, type):
            #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            # CAVEATS: Synchronize changes here with similar logic above.
            #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

            # Code type-checking the current pith against this class.
            func_curr_code = PEP_CODE_CHECK_HINT_NONPEP_TYPE_format(
                pith_curr_expr=pith_curr_expr,
                # Python expression evaluating to this class when accessed via
                # the private "__beartypistry" parameter.
                hint_curr_expr=register_typistry_type(hint_curr),
            )

        # Else, this hint is neither PEP-compliant *NOR* a class. In this
        # case, raise an exception. Note that:
        #
        # * This should *NEVER* happen, as the "typing" module goes to great
        #   lengths to validate the integrity of PEP-compliant types at
        #   declaration time.
        # * The higher-level die_unless_hint_nonpep() validator is
        #   intentionally *NOT* called here, as doing so would permit both:
        #   * PEP-noncompliant forward references, which could admittedly be
        #     disabled by passing "is_str_valid=False" to that call.
        #   * PEP-noncompliant tuple unions, which currently *CANNOT* be
        #     disabled by passing such an option to that call.
        else:
            raise BeartypeDecorHintPepException(
                f'{hint_curr_label} hint {repr(hint_curr)} not PEP-compliant '
                f'(e.g., neither "typing" object nor non-"typing" class).'
            )

        # ................{ CLEANUP                           }................
        # Inject this code into the body of this wrapper.
        func_code = replace_str_substrs(
            text=func_code, old=hint_curr_placeholder, new=func_curr_code)

        # Nullify the metadata describing the previously visited hint in this
        # list for safety.
        hints_meta[hints_meta_index_curr] = None

        # Increment the 0-based index of metadata describing the next visited
        # hint in the "hints_meta" list *BEFORE* visiting this hint but *AFTER*
        # performing all other logic for the currently visited hint, implying
        # this should be the last statement of this iteration.
        hints_meta_index_curr += 1

    # ..................{ CLEANUP                           }..................
    # Release the fixed list of all such metadata.
    release_fixed_list(hints_meta)

    # If the Python code snippet to be returned remains unchanged from its
    # initial value, the breadth-first search above failed to generate code. In
    # this case, raise an exception.
    #
    # Note that this test is inexpensive, as the third character of the
    # "func_root_code" code snippet is guaranteed to differ from that of
    # "func_code" code snippet if this function behaved as expected, which it
    # absolutely should have... but may not have, which is why we're testing.
    if func_code == func_root_code:
        raise BeartypeDecorHintPepException(
            f'{HINT_ROOT_LABEL} {repr(hint_root)} not type-checked.')
    # Else, the breadth-first search above successfully generated code.

    # Suffix this code by a Python code snippet raising a human-readable
    # exception when the root pith violates the root type hint.
    func_code += PEP_CODE_CHECK_HINT_ROOT_SUFFIX_format(
        random_int_if_any=(
            # If type-checking the root pith requires a pseudo-random integer,
            # pass this integer to the function raising this exception.
            PEP_CODE_RAISE_PEP_CALL_EXCEPTION_RANDOM_INT
            if is_func_code_needs_random_int else
            # Else, call that function *WITHOUT* passing that integer.
            ''
        ),
    )

    # Return all metadata required by higher-level callers.
    return (
        func_code,
        is_func_code_needs_random_int,
        # Tuple of the unqualified classnames referred to by all relative
        # forward references visitable from this hint converted from this set
        # to reduce space consumption after memoization by @callable_cached.
        (
            # If *NO* relative forward references are visitable from this root
            # hint, the empty tuple.
            ()
            if hints_forwardref_class_basename is None else
            # Else, this set converted into a tuple.
            tuple(hints_forwardref_class_basename)
        ),
    )
