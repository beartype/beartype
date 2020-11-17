#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2020 Cecil Curry.
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
#then define a new beartype._decor._typistry.register_hashable() function
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

# ....................{ IMPORTS                           }....................
from beartype.roar import (
    BeartypeDecorHintPepException,
    BeartypeDecorHintPepUnsupportedException,
    BeartypeDecorHintPep484Exception,
)
from beartype._decor._typistry import (
    register_typistry_forwardref,
    register_typistry_type,
    register_typistry_tuple,
)
from beartype._decor._code._codesnip import CODE_INDENT_1, CODE_INDENT_2
from beartype._decor._code._pep._pepsnip import (
    PEP_CODE_CHECK_HINT_ROOT,
    PEP_CODE_CHECK_HINT_TUPLE_FIXED_PREFIX,
    PEP_CODE_CHECK_HINT_TUPLE_FIXED_SUFFIX,
    PEP_CODE_HINT_CHILD_PLACEHOLDER_PREFIX,
    PEP_CODE_HINT_CHILD_PLACEHOLDER_SUFFIX,
    PEP_CODE_HINT_FORWARDREF_UNQUALIFIED_PLACEHOLDER_PREFIX,
    PEP_CODE_HINT_FORWARDREF_UNQUALIFIED_PLACEHOLDER_SUFFIX,
    PEP_CODE_PITH_NAME_PREFIX,
    PEP_CODE_PITH_ROOT_NAME,
    PEP484_CODE_CHECK_HINT_GENERIC_PREFIX,
    PEP484_CODE_CHECK_HINT_GENERIC_SUFFIX,
    PEP484_CODE_CHECK_HINT_UNION_PREFIX,
    PEP484_CODE_CHECK_HINT_UNION_SUFFIX,

    # Bound format methods.
    PEP_CODE_CHECK_HINT_NONPEP_TYPE_format,
    PEP_CODE_CHECK_HINT_SEQUENCE_STANDARD_format,
    PEP_CODE_CHECK_HINT_SEQUENCE_STANDARD_PITH_CHILD_EXPR_format,
    PEP_CODE_CHECK_HINT_TUPLE_FIXED_EMPTY_format,
    PEP_CODE_CHECK_HINT_TUPLE_FIXED_LEN_format,
    PEP_CODE_CHECK_HINT_TUPLE_FIXED_NONEMPTY_CHILD_format,
    PEP_CODE_CHECK_HINT_TUPLE_FIXED_NONEMPTY_PITH_CHILD_EXPR_format,
    PEP_CODE_PITH_ASSIGN_EXPR_format,
    PEP484_CODE_CHECK_HINT_GENERIC_CHILD_format,
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
)
from beartype._util.hint.data.pep.proposal.utilhintdatapep484 import (
    HINT_PEP484_BASE_FORWARDREF,
    HINT_PEP484_SIGNS_UNION,
)
from beartype._util.hint.data.utilhintdata import HINTS_IGNORABLE_SHALLOW
from beartype._util.hint.utilhintget import get_hint_forwardref_classname
from beartype._util.hint.pep.proposal.utilhintpep484 import (
    get_hint_pep484_generic_base_erased_from_unerased,
    get_hint_pep484_generic_bases_unerased_or_none,
    get_hint_pep484_newtype_class,
    is_hint_pep484_newtype,
)
from beartype._util.hint.pep.proposal.utilhintpep544 import (
    get_hint_pep544_io_protocol_from_generic,
    is_hint_pep544_io_generic,
)
from beartype._util.hint.pep.proposal.utilhintpep593 import (
    get_hint_pep593_hint,
    is_hint_pep593,
)
from beartype._util.hint.pep.utilhintpepget import (
    get_hint_pep_args,
    get_hint_pep_sign,
    get_hint_pep_type_origin,
)
from beartype._util.hint.pep.utilhintpeptest import (
    die_if_hint_pep_unsupported,
    die_if_hint_pep_sign_unsupported,
    is_hint_pep,
    is_hint_pep_typing,
)
from beartype._util.hint.utilhinttest import is_hint_ignorable
from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_8
from itertools import count
from typing import Generic, NewType, NoReturn, Tuple

# See the "beartype.__init__" submodule for further commentary.
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
def pep_code_check_hint(hint: object) -> (
    'Tuple[str, bool, Optional[Set[str]]'):
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
    Tuple[str, bool, Optional[Tuple[str]]
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
        * ``hints_forwardref_class_basename`` is the tuple of the unqualified
          classnames of PEP 484-compliant relative forward references visitable
          from this root hint (e.g., ``('MuhClass', 'YoClass')`` given the root
          hint ``Union['MuhClass', List['YoClass']]``).

    Raises
    ----------
    BeartypeDecorHintPepException
        If this object is *not* a PEP-compliant type hint.
    BeartypeDecorHintPepUnsupportedException
        If this object is a PEP-compliant type hint currently unsupported by
        the :func:`beartype.beartype` decorator.
    '''

    # ..................{ HINT ~ root                       }..................
    # Top-level hint relocalized for disambiguity. For the same reason, delete
    # the passed parameter whose name is ambiguous within the context of this
    # code generator.
    hint_root = hint
    del hint

    # Human-readable label describing the root hint in exception messages.
    hint_root_label = f'{EXCEPTION_CACHED_PLACEHOLDER} {repr(hint_root)}'

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

    # Human-readable label prefixing the representations of child hints of this
    # root hint in exception messages.
    #
    # Note that this label intentionally only describes the root and currently
    # iterated child hints rather than the root hint, the currently iterated
    # child hint, and all interim child hints leading from the former to the
    # latter. The latter approach would be non-human-readable and insane.
    hint_child_label = hint_root_label + ' child'

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

    # Origin type (i.e., non-"typing" superclass suitable for shallowly
    # type-checking the current pith against the currently visited hint by
    # passing both to the isinstance() builtin) of the currently iterated child
    # hint of the currently visited parent hint.
    hint_child_type_origin = None

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
    hint_childs = None

    # Number of PEP-compliant child hints subscripting the currently visited
    # hint.
    hint_childs_len = None

    # Set of all PEP-noncompliant child hints subscripting the currently
    # visited hint.
    hint_childs_nonpep = None

    # Set of all PEP-compliant child hints subscripting the currently visited
    # hint.
    hint_childs_pep = None

    # ..................{ HINT ~ pep 484 : forwardref       }..................
    # Set of the unqualified classnames referred to by all relative forward
    # references visitable from this root hint if any *OR* "None" otherwise
    # (i.e., if no such forward references are visitable).
    hints_forwardref_class_basename = None

    # Possibly unqualified classname referred to by the currently visited
    # forward reference type hint.
    hint_curr_forwardref_classname = None

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
    pith_curr_assign_expr = None

    # Name of the local variable uniquely assigned to by
    # "pith_curr_assign_expr". Equivalently, this is the left-hand side (LHS)
    # of that assignment expression.
    pith_curr_assigned_expr = None

    # ..................{ METADATA                          }..................
    # Tuple of metadata describing the currently visited hint, appended by
    # the previously visited parent hint to the "hints_meta" stack.
    hint_curr_meta = None

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
    func_root_code = PEP_CODE_CHECK_HINT_ROOT.format(
        hint_child_placeholder=hint_child_placeholder)

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

        # ................{ REDUCTION                         }................
        #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        # CAVEATS: Synchronize changes here with the corresponding block of the
        # beartype._decor._code._pep._error._peperrorsleuth.CauseSleuth__init__()
        # method.
        #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        # This logic reduces the currently visited hint to an arbitrary object
        # associated with this hint when this hint conditionally satisfies any
        # of various conditions.
        #
        # ................{ REDUCTION ~ pep 484               }................
        # If this is a PEP 484-compliant new type hint, reduce this hint to the
        # user-defined class aliased by this hint. Although this logic could
        # also be performed below, doing so here simplifies matters.
        if is_hint_pep484_newtype(hint_curr):
            hint_curr = get_hint_pep484_newtype_class(hint_curr)
        # ................{ REDUCTION ~ pep 544               }................
        # If this is a PEP 484-compliant IO generic base class *AND* the active
        # Python interpreter targets at least Python >= 3.8 and thus supports
        # PEP 544-compliant protocols, reduce this functionally useless hint to
        # the corresponding functionally useful beartype-specific PEP
        # 544-compliant protocol implementing this hint.
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
        #         hint_child_label, hint, hint_curr_placeholder, func_code))

        # ................{ PEP                               }................
        # If this hint is PEP-compliant...
        if is_hint_pep(hint_curr):
            #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            # CAVEATS: Synchronize changes here with "ANNOTATED" below.
            #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

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
            #        hint=hint_curr, hint_label=hint_child_label)
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
                hint=hint_curr, hint_label=hint_child_label)
            # Else, this hint is supported.

            # Assert that this hint is unignorable. Iteration below generating
            # code for child hints of the current parent hint is *REQUIRED* to
            # explicitly ignore ignorable child hints. Since the caller has
            # explicitly ignored ignorable root hints, these two guarantees
            # together ensure that all hints visited by this breadth-first
            # search *SHOULD* be unignorable. Naturally, we validate that here.
            assert not is_hint_ignorable(hint_curr), (
                f'{hint_child_label} PEP type hint '
                f'{repr(hint_curr)} ignorable.')

            # Unsubscripted "typing" attribute uniquely identifying this hint.
            hint_curr_sign = get_hint_pep_sign(hint_curr)

            # If this attribute is currently unsupported, raise an exception.
            #
            # Note the human-readable label prefixing the representations of
            # child PEP-compliant type hints is unconditionally passed. Since
            # the root hint has already been validated to be supported by the
            # above call to the die_if_hint_pep_unsupported() function, this
            # call is guaranteed to *NEVER* raise exceptions for the root hint.
            die_if_hint_pep_sign_unsupported(
                hint=hint_curr_sign, hint_label=hint_child_label)
            # Else, this attribute is supported.

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
            #* In the "beartype_test.unit.data._data_hint_pep" submodule:
            #  * Add a new "_PepHintMetadata.code_str_match_regexes" field,
            #    defined as an iterable of regular expressions matching
            #    substrings of the "func_wrapper.__beartype_wrapper_code"
            #    attribute that are expected to exist.
            #  * For most "HINT_PEP_TO_META" entries, default this field to
            #    merely the empty tuple.
            #  * For deeply nested "HINT_PEP_TO_META" entries, define this
            #    field as follows:
            #        code_str_match_regexes=(r'\s+:=\s+',)
            #* In the "beartype_test.unit.pep.p484.test_p484" submodule:
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
                    f'{hint_child_label} PEP union '
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
                        f'{hint_child_label} ignorable PEP union '
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
                            # Note that we would ideally avoid coercing this
                            # set into a tuple when this set only contains one
                            # type by passing that type directly to the
                            # register_typistry_type() function. Sadly, the
                            # "set" class defines no convenient or efficient
                            # means of retrieving the only item of a 1-set.
                            # Indeed, the most efficient means of doing so is
                            # to iterate over that set and immediately break:
                            #     for first_item in muh_set: break
                            #
                            # While we *COULD* technically leverage that
                            # approach here, doing so would also mandate adding
                            # a number of intermediate tests, which would
                            # certainly reduce any performance gains.
                            # Ultimately, we avoid doing so by falling back to
                            # the standard approach. See also this relevant
                            # self-StackOverflow post:
                            #     https://stackoverflow.com/a/40054478/2809027
                            hint_curr_expr=register_typistry_tuple(
                                hint=tuple(hint_childs_nonpep),
                                # Inform this function it needn't attempt to
                                # uselessly omit duplicates, since the "typing"
                                # module already does so for all "Union"
                                # arguments. Well, that's nice.
                                is_types_unique=True,
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
            elif hint_curr_sign is Generic:
                # Assert this hint is a class.
                assert isinstance(hint_curr, type), (
                    f'{hint_child_label} PEP generic '
                    f'{repr(hint_curr)} not class.')

                # Tuple of the one or more unerased pseudo-superclasses (i.e.,
                # "typing" objects originally listed as superclasses prior to
                # their implicit type erasure by the "typing" module)
                # subclassed by this generic.
                hint_childs = get_hint_pep484_generic_bases_unerased_or_none(hint_curr)

                # Assert this generic subclassed at least one
                # pseudo-superclass. Note that the "typing" module should have
                # already guaranteed this on our behalf. Trust is for the fool.
                assert hint_childs, (
                    f'{hint_child_label} PEP generic '
                    f'{repr(hint_curr)} subclasses no superclasses.')

                # Initialize the code type-checking the current pith against
                # this generic to the substring prefixing all such code.
                func_curr_code = PEP484_CODE_CHECK_HINT_GENERIC_PREFIX

                # For each pseudo-superclass subclassed by this generic...
                for hint_child in hint_childs:
                    # print(f'hint_child: {repr(hint_child)} {is_hint_pep_class_typing(hint_child)}')

                    # If this pseudo-superclass is an actual class, this class
                    # is effectively ignorable. Why? Because the
                    # "PEP484_CODE_CHECK_HINT_GENERIC_PREFIX" snippet leveraged
                    # above already type-checks this pith against the generic
                    # subclassing this superclass and thus this superclass as
                    # well with a trivial isinstance() call. In this case, skip
                    # to the next pseudo-superclass.
                    if isinstance(hint_child, type):
                        continue
                    # Else, this pseudo-superclass is *NOT* an actual class.
                    #
                    # If this pseudo-superclass is *NOT* defined by the
                    # "typing" module (and is thus user-defined), reduce this
                    # pseudo-superclass to a real superclass originating this
                    # pseudo-superclass.
                    #
                    # Note that this edge case arises *ONLY* for user-defined
                    # generics and protocols subclassing another user-defined
                    # generic or protocol superclass subscripted by one or more
                    # type variables: e.g.,
                    #
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
                    elif not is_hint_pep_typing(hint_child):
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
                        PEP484_CODE_CHECK_HINT_GENERIC_CHILD_format(
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
                    PEP484_CODE_CHECK_HINT_GENERIC_SUFFIX
                # Format the "indent_curr" prefix into this code deferred
                # above for efficiency.
                ).format(
                    indent_curr=indent_curr,
                    pith_curr_assign_expr=pith_curr_assign_expr,
                    # Python expression evaluating to the builtin "tuple" type
                    # when accessed via the private "__beartypistry" parameter.
                    hint_curr_expr=register_typistry_type(hint_curr),
                )
                # print(f'{hint_child_label} PEP generic {repr(hint)} handled.')
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
                    f'{hint_child_label} PEP type hint '
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
                # Is deeply supported by this function but is its own
                # unsubscripted "typing" attribute (e.g., "typing.List" rather
                # than "typing.List[str]") and is thus subscripted by *NO*
                # child hints...
                hint_curr is hint_curr_sign
            ):
            # Then generate trivial code shallowly type-checking the current
            # pith as an instance of the non-"typing" origin class originating
            # this unsubscripted "typing" attribute (e.g., "list" for attribute
            # "typing.List" identifying hint "typing.List[int]").

                # Code type-checking the current pith against this class.
                func_curr_code = PEP_CODE_CHECK_HINT_NONPEP_TYPE_format(
                    pith_curr_expr=pith_curr_expr,
                    # Python expression evaluating to this class when accessed
                    # via the private "__beartypistry" parameter.
                    hint_curr_expr=register_typistry_type(
                        # Origin type of this attribute if any *OR* raise an
                        # exception -- which should *NEVER* happen, as this
                        # attribute was validated above to be supported.
                        get_hint_pep_type_origin(hint_curr_sign)),
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
                    hint_curr_sign is Tuple and
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
                    get_hint_pep_type_origin(hint_curr_sign))

                # Assert this sequence is either subscripted by exactly one
                # argument *OR* a non-standard sequence (e.g., "typing.Tuple").
                # Note that the "typing" module should have already guaranteed
                # this on our behalf. Still, we trust nothing and no one:
                #     >>> import typing as t
                #     >>> t.List[int, str]
                #     TypeError: Too many parameters for typing.List; actual 2, expected 1
                assert hint_childs_len == 1 or hint_curr_sign is Tuple, (
                    f'{hint_child_label} PEP sequence {repr(hint_curr)} '
                    f'subscripted by multiple arguments.')

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
            elif hint_curr_sign is Tuple:
                # Assert this tuple was subscripted by at least one argument.
                # Note that the "typing" module should have already guaranteed
                # this on our behalf. Trust is for the weak.
                assert hint_childs, (
                    f'{hint_child_label} PEP fixed-length tuple '
                    f'{repr(hint_curr)} empty.')

                # Assert this tuple is *NOT* of the syntactic form
                # "typing.Tuple[{typename}, ...]" handled by prior logic.
                assert (
                    hint_childs_len == 1 or
                    hint_childs[1] is not Ellipsis
                ), (
                    f'{hint_child_label} PEP variadic tuple '
                    f'{repr(hint_curr)} unhandled.')

                # Initialize the code type-checking the current pith against
                # this tuple to the substring prefixing all such code.
                func_curr_code = PEP_CODE_CHECK_HINT_TUPLE_FIXED_PREFIX

                # If this hint is subscripted by exactly one child hint *AND*
                # this child hint is the empty tuple, generate and append code
                # type-checking the current pith to also be the empty tuple.
                # Yes, this is a ridiculous edge case. Welcome to PEP 484.
                if hint_childs_len == 1 and hint_childs[0] == ():
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
                    f'{hint_child_label} PEP type hint '
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
                f'{hint_child_label} hint {repr(hint_curr)} not PEP-compliant '
                f'(e.g., neither "typing" object nor non-"typing" class).'
            )

        # ................{ CLEANUP                           }................
        # Inject this code into the body of this wrapper.
        func_code = func_code.replace(hint_curr_placeholder, func_curr_code)

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
            f'{hint_root_label} not type-checked.')
    # Else, the breadth-first search above successfully generated code.

    # Tuple of the unqualified classnames referred to by all relative forward
    # references visitable from this root hint converted from this set to
    # reduce space consumption after memoization by @callable_cached.
    hints_forwardref_class_basename = (
        # If *NO* relative forward references are visitable from this root
        # hint, the empty tuple.
        ()
        if hints_forwardref_class_basename is None else
        # Else, this set converted into a tuple.
        tuple(hints_forwardref_class_basename)
    )

    # Return all metadata required by higher-level callers.
    return (
        func_code,
        is_func_code_needs_random_int,
        hints_forwardref_class_basename,
    )
