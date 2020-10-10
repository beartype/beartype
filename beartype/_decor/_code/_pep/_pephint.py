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

#FIXME: Type-check instances of user-defined subclasses subclassing multiple
#"typing" pseudo-superclasses. While we currently do iterate over these
#superclasses properly in the breadth-first search implemented below, we
#currently do *NOT* generate sane code type-checking such instances against
#these superclasses and thus raise exceptions on detecting such subclasses.
#See the related "FIXME:" comment preceding this test below.:
#           elif len(hint_curr_attrs_to_args) > 2:

#FIXME: Type-check instances of types subclassing the "typing.Protocol"
#superclass decorated by the @runtime_checkable decorator, detectable at
#runtime by the existence of both "typing.Protocol" in their "__mro__" dunder
#attribute *AND* the protocol-specific private "_is_runtime_protocol" instance
#variable set to True.
#
#Specifically, refactor the codebase as follows to support protocols:
#
#* Define a new utilhintpeptest.is_hint_pep_protocol() tester returning True if
#  the passed object is a @runtime_checkable-decorated Protocol. See below for
#  the logic necessary to do so. This is non-trivial, as "Protocol" was only
#  introduced under Python >= 3.8 *BUT* various "typing" subclasses of a
#  private "_Protocol" superclass have been available since Python >= 3.5.
#* Define a new utilhinttest.is_hint_isinstanceable() tester returning True if
#  the passed object is a type that either:
#  * Is a non-"typing" type.
#  * Is a @runtime_checkable-decorated Protocol subclass.
#* Call the is_hint_isinstanceable() tester *BEFORE* the is_hint_pep() tester
#  everywhere in this codebase. Notably:
#  * Revise:
#    # ...this test...
#    elif isinstance(hint_curr, type):
#    # ...into this test.
#    elif is_hint_isinstanceable(hint_curr):
#  * Shift that test before the "if is_hint_pep(hint_curr):"
#    test above.
#  * Revise the above union-specific tests from:
#    # ...this logic...
#         # If this argument is PEP-compliant...
#         if is_hint_pep(hint_child):
#             # Filter this argument into the list of
#             # PEP-compliant arguments.
#             hint_childs_pep.append(hint_child)
#
#         # Else, this argument is PEP-noncompliant. In this
#         # case, filter this argument into the list of
#         # PEP-noncompliant arguments.
#         else:
#             hint_childs_nonpep.append(hint_child)
#
#    # ...into this logic.
#         # If this argument is an isinstance()-compatible
#         # type, filter this argument into the list of these
#         # types.
#         if is_hint_isinstanceable(hint_child):
#             hint_childs_nonpep.append(hint_child)
#         # Else, this argument is *NOT* an
#         # isinstance()-compatible type. In this case...
#         else:
#             # If this argument is *NOT* a PEP-compliant
#             # type hint, raise an exception.
#             die_unless_hint_pep(
#                 hint=hint_child, hint_label=???)
#             # Else, this argument is a PEP-compliant
#             # type hint.
#
#             # Filter this argument into the list of
#             # PEP-compliant arguments.
#             hint_childs_pep.append(hint_child)
#
#Note lastly that support for protocols conditionally depends on the current
#Python version. Besically:
#
#* Under Python < 3.8, the following abstract base classes (ABCs) are standard
#  ABCs and thus trivially support isinstance() as is:
#  * typing.SupportsInt
#  * typing.SupportsFloat
#  * typing.SupportsComplex
#  * typing.SupportsBytes
#  * typing.SupportsAbs
#  * typing.SupportsRound
#  Note that "typing.Protocol" does *NOT* exist here. Ergo, the
#  is_hint_pep_protocol() tester should return True under Python < 3.8 only if
#  the passed hint is an instance of one of these six ABCs. This is essential,
#  as these instances would otherwise be treated as PEP-compliant type hints --
#  which they're not, really.
#* Under Python >= 3.8, the "typing.Protocol" superclass appears and all of the
#  above ABCs both subclass that *AND* are decorated by @runtime_checkable.
#  Lastly, a new "typing.SupportsIndex" ABC is introduced as well. So, we need
#  to check that the protocol-specific private "_is_runtime_protocol" instance
#  variable is set to True
#  for "Protocol" subclasses.
#FIXME: Note that the ProtocolMeta.__subclasshook__() dunder method
#implementation is insanely inefficient in a way that only "typing" authors
#could have written. Ideally, rather than naively calling isinstance() on
#instances of core "typing.Protocol" subclasses defined by the "typing" module
#itself (e.g., "typing.SupportsInt"), we would instead generate efficient code
#directly type-checking that those instances define the requisite attributes.
#Note, however, that the typing.Protocol.__init_subclass__._proto_hook()
#implementing structural subtyping checks is sufficiently non-trivial that we
#*REALLY* don't want to get into that for now.

#FIXME: Type-check "typing.NoReturn", too. Note that whether a callable returns
#"None" or not is *NOT* a sufficient condition to positively declare a function
#to return no value for hopefully obvious reasons. Rather, we instead need to
#validate this condition entirely at decoration time by either:
#* Disassembling the decorated callable with the "dis" module and parsing the
#  returned bytecode assembly for the first "return" statement if any.
#* Constructing the abstract syntax tree (AST) for the decorated callable with
#  the "ast" module and parsing the returned AST for the first node marked as a
#  "return" statement if any.


#FIXME: Resolve PEP-compliant forward references as well. Note that doing so is
#highly non-trivial -- sufficiently so, in fact, that we probably want to do so
#elsewhere as cleverly documented in the "_pep563" submodule.

# ....................{ IMPORTS                           }....................
from beartype.roar import BeartypeDecorHintPepException
from beartype._decor._data import BeartypeData
from beartype._decor._typistry import (
    register_typistry_type,
    register_typistry_tuple,
)
from beartype._decor._code._codesnip import CODE_INDENT_1, CODE_INDENT_2
from beartype._decor._code._pep._pepsnip import (
    PEP_CODE_CHECK_HINT_ROOT,
    PEP_CODE_CHECK_HINT_NONPEP_TYPE_format,
    PEP_CODE_CHECK_HINT_SEQUENCE_STANDARD_format,
    PEP_CODE_CHECK_HINT_SEQUENCE_STANDARD_PITH_CHILD_EXPR_format,
    PEP_CODE_CHECK_HINT_UNION_PREFIX,
    PEP_CODE_CHECK_HINT_UNION_SUFFIX,
    PEP_CODE_CHECK_HINT_UNION_ARG_NONPEP_format,
    PEP_CODE_CHECK_HINT_UNION_ARG_PEP_format,
    PEP_CODE_PITH_ASSIGN_EXPR_format,
    PEP_CODE_PITH_NAME_PREFIX,
    PEP_CODE_PITH_ROOT_NAME,
)
from beartype._util.cache.utilcachecall import callable_cached
from beartype._util.cache.pool.utilcachepoollistfixed import (
    SIZE_BIG, FixedList, acquire_fixed_list, release_fixed_list)
from beartype._util.cache.utilcacheerror import (
    EXCEPTION_CACHED_PLACEHOLDER)
from beartype._util.hint.utilhintdata import HINTS_SHALLOW_IGNORABLE
from beartype._util.hint.utilhintget import get_hint_type_origin
from beartype._util.hint.utilhinttest import is_hint_ignorable
from beartype._util.hint.pep.utilhintpepdata import (
    TYPING_ATTR_TO_TYPE_ORIGIN,
    TYPING_ATTRS_SEQUENCE_STANDARD,
    TYPING_ATTRS_UNION,
)
from beartype._util.hint.pep.utilhintpepget import get_hint_pep_typing_attr
from beartype._util.hint.pep.utilhintpeptest import (
    die_unless_hint_pep_supported,
    die_unless_hint_pep_typing_attr_supported,
    is_hint_pep,
)
from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_8
from itertools import count
# from typing import

# See the "beartype.__init__" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ CONSTANTS ~ hint : meta           }....................
# Iterator yielding the next integer incrementation starting at 0, to be safely
# deleted *AFTER* defining the following 0-based indices via this iterator.
__hint_meta_index_counter = count(start=0, step=1)


_HINT_META_INDEX_HINT = next(__hint_meta_index_counter)
'''
0-based index into each fixed list of hint metadata providing the currently
visited hint.
'''


_HINT_META_INDEX_PLACEHOLDER = next(__hint_meta_index_counter)
'''
0-based index into each fixed list of hint metadata providing the **current
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
0-based index into each fixed list of hint metadata providing the **current
pith expression** (i.e., Python code snippet evaluating to the current possibly
nested object of the passed parameter or return value to be type-checked
against the currently visited hint).
'''


_HINT_META_INDEX_INDENT = next(__hint_meta_index_counter)
'''
0-based index into each fixed list of hint metadata providing **current
indentation** (i.e., Python code snippet expanding to the current level of
indentation appropriate for the currently visited hint).
'''


_HINT_META_SIZE = next(__hint_meta_index_counter)
'''
Length to constrain **hint metadata** (i.e., fixed lists efficiently
masquerading as tuples of metadata describing the currently visited hint,
defined by the previously visited parent hint as a means of efficiently sharing
metadata common to all children of that hint) to.
'''

# Delete the above counter for safety and sanity in equal measure.
del __hint_meta_index_counter

# ....................{ CODERS                            }....................
@callable_cached
def pep_code_check_hint(data: BeartypeData, hint: object) -> (
    'Tuple[str, bool]'):
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
    data : BeartypeData
        Decorated callable to be type-checked.
    hint : object
        PEP-compliant type hint to be type-checked.

    Returns
    ----------
    Tuple[str, bool]
        2-tuple ``(func_code, is_func_code_needs_random_int)``, where:

        * ``func_code`` is Python code type-checking the previously localized
          parameter or return value against this hint.
        * ``is_func_code_needs_random_int`` is a boolean that is ``True`` only
          if one or more PEP-compliant type hints transitively visitable from
          this root hint (including this root hint) require a pseudo-random
          integer. If true, the higher-level
          :func:`beartype._decor._code.codemain.generate_code` function
          prefixes the body of this wrapper function with code generating such
          an integer.

    Raises
    ----------
    BeartypeDecorHintPepException
        If this object is *not* a PEP-compliant type hint.
    BeartypeDecorHintPepUnsupportedException
        If this object is a PEP-compliant type hint but is currently
        unsupported by the :func:`beartype.beartype` decorator.
    '''
    # Note this hint need *NOT* be validated as a PEP-compliant type hint
    # (e.g., by explicitly calling the die_unless_hint_pep_supported()
    # function). By design, the caller already guarantees this to be the case.
    assert data.__class__ is BeartypeData, (
        '{!r} not @beartype data.'.format(data))
    # print('Type-checking hint {!r} for {}...'.format(hint, data.func_name))

    # ..................{ ATTRIBUTES                        }..................
    # Localize attributes of this dataclass for negligible efficiency gains.
    # Notably, alias:
    #
    # * The generic "data.set_a" set as the readable "hint_childs_nonpep",
    #   accessed below as the set of all PEP-noncompliant types listed by the
    #   currently visited hint.
    # * The generic "data.set_b" set as the readable "hint_childs_pep",
    #   accessed below as the set of all PEP-compliant types listed by the
    #   currently visited hint.
    get_next_pep_hint_placeholder = data.get_next_pep_hint_placeholder
    hint_childs_nonpep = data.set_a
    hint_childs_pep    = data.set_b
    hint_childs_nonpep_add = hint_childs_nonpep.add
    hint_childs_pep_add    = hint_childs_pep.add

    # ..................{ HINT ~ root                       }..................
    # Top-level hint relocalized for disambiguity. For the same reason, delete
    # the passed parameter whose name is ambiguous within the context of this
    # code generator.
    hint_root = hint
    del hint

    #FIXME: Refactor to leverage f-strings after dropping Python 3.5 support,
    #which are the optimal means of performing string formatting.

    # Human-readable label describing the root hint in exception messages.
    hint_root_label = EXCEPTION_CACHED_PLACEHOLDER + ' ' + repr(hint_root)

    # Python code snippet evaluating to the current passed parameter or return
    # value to be type-checked against the root hint.
    pith_root_expr = PEP_CODE_PITH_ROOT_NAME

    # ..................{ HINT ~ current                    }..................
    # Currently visited hint.
    hint_curr = None

    # Current argumentless typing attribute associated with this hint (e.g.,
    # "Union" if "hint_curr == Union[int, str]").
    hint_curr_attr = None

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
    # the current pith expression (i.e., "pith_curr_expr") against the
    # currently visited hint (i.e., "hint_curr").
    hint_curr_placeholder = None

    # Python code snippet evaluating to the current (possibly nested) object of
    # the passed parameter or return value to be type-checked against the
    # currently visited hint.
    pith_curr_expr = None

    # Python code snippet expanding to the current level of indentation
    # appropriate for the currently visited hint.
    indent_curr = CODE_INDENT_2

    # ..................{ HINT ~ child                      }..................
    # Current tuple of all subscripted arguments defined on this hint (e.g.,
    # "(int, str)" if "hint_curr == Union[int, str]").
    hint_childs = None

    # Currently iterated subscripted argument defined on this hint.
    hint_child = None

    #FIXME: Excise us up.
    # Current argumentless typing attribute associated with this hint (e.g.,
    # "Union" if "hint_child == Union[int, str]").
    # hint_child_attr = None

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
    hint_child_placeholder = get_next_pep_hint_placeholder()

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
    # appropriate for the currently iterated child hint.
    indent_child = None

    # ..................{ HINT ~ pep 572                    }..................
    # True only if:
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
    is_pith_curr_assign_expr = None

    # Integer suffixing the name of each local variable assigned the value of
    # the current pith in a Python >= 3.8-specific assignment expression, thus
    # uniquifying this variable in the body of the current wrapper function.
    #
    # Note that this integer is intentionally incremented as an efficient
    # low-level scalar rather than an inefficient high-level
    # "itertools.counter" object. Since both are equally thread-safe in the
    # internal context of this function body, the former is preferable.
    pith_curr_assign_expr_name_counter = 0

    # Full Python expression yielding the value of the current pith.
    #
    # Note that this is *NOT* a Python >= 3.8-specific assignment expression
    # but rather the original inefficient expression provided by the parent
    # PEP-compliant type hint of the currently visited hint.
    pith_curr_full_expr = None

    # Python >= 3.8-specific assignment expression assigning this full Python
    # expression to the local variable assigned the value of this expression.
    pith_curr_assign_expr = None

    # ..................{ METADATA                          }..................
    # Fixed list of metadata describing the root hint.
    hint_root_meta = acquire_fixed_list(_HINT_META_SIZE)
    hint_root_meta[_HINT_META_INDEX_HINT] = hint_root
    hint_root_meta[_HINT_META_INDEX_PLACEHOLDER] = hint_child_placeholder
    hint_root_meta[_HINT_META_INDEX_PITH_EXPR] = pith_root_expr
    hint_root_meta[_HINT_META_INDEX_INDENT] = indent_curr

    # Fixed list of metadata describing the currently visited hint, appended by
    # the previously visited parent hint to the "hints_meta" stack.
    hint_curr_meta = None

    # Fixed list of metadata describing a child hint to be subsequently
    # visited, appended by the currently visited parent hint to that stack.
    hint_child_meta = None

    # Fixed list of all metadata describing all visitable hints currently
    # discovered by the breadth-first search (BFS) below.
    #
    # Note that this list is guaranteed by the previously called
    # _die_if_hint_repr_exceeds_child_limit() function to be larger than the
    # number of hints transitively visitable from this root hint. Ergo, *ALL*
    # indexation into this list performed by this BFS is guaranteed to be safe.
    # Ergo, avoid explicitly testing below that the "hints_meta_index_last"
    # integer maintained by this BFS is strictly less than "SIZE_BIG", as this
    # constraint is already guaranteed to be the case.
    hints_meta = acquire_fixed_list(SIZE_BIG)

    # Seed this list with metadata describing the root hint.
    #
    # Note that this assignment is guaranteed to be safe, as "SIZE_BIG" is
    # guaranteed to be substantially larger than 1.
    hints_meta[0] = hint_root_meta

    # 0-based index of metadata describing the currently visited hint in the
    # "hints_meta" list.
    hints_meta_index_curr = 0

    # 0-based index of metadata describing the last visitable hint in the
    # "hints_meta" list.
    hints_meta_index_last = 0

    # ..................{ FUNC ~ code                       }..................
    #FIXME: Refactor to leverage f-strings after dropping Python 3.5 support,
    #which are the optimal means of performing string formatting.

    # Python code snippet type-checking the root pith against the root hint,
    # localized separately from the "func_code" snippet to enable this function
    # to validate this code to be valid *BEFORE* returning this code.
    func_root_code = PEP_CODE_CHECK_HINT_ROOT.format(
        hint_child_placeholder=hint_child_placeholder)

    # Python code snippet type-checking the current pith against the currently
    # visited hint (to be appended to the "func_code" string).
    func_curr_code = None

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
        assert hint_curr_meta.__class__ is FixedList, (
            'Current hint metadata {!r} at index {!r} '
            'not a fixed list.'.format(hint_curr_meta, hints_meta_index_curr))

        # Localize metadatum for both efficiency and f-string purposes.
        hint_curr             = hint_curr_meta[_HINT_META_INDEX_HINT]
        hint_curr_placeholder = hint_curr_meta[_HINT_META_INDEX_PLACEHOLDER]
        pith_curr_expr        = hint_curr_meta[_HINT_META_INDEX_PITH_EXPR]
        indent_curr           = hint_curr_meta[_HINT_META_INDEX_INDENT]

        #FIXME: Comment this sanity check out after we're sufficiently
        #convinced this algorithm behaves as expected. While useful, this check
        #requires a linear search over the entire code and is thus costly.
        # assert hint_curr_placeholder in func_code, (
        #     '{} {!r} placeholder {} not found in wrapper body:\n{}'.format(
        #         hint_child_label, hint, hint_curr_placeholder, func_code))

        # If this hint is PEP-compliant...
        if is_hint_pep(hint_curr):
            # If this hint is currently unsupported, raise an exception.
            #
            # Note the human-readable label prefixing the representations of
            # child PEP-compliant type hints is unconditionally passed. Since
            # the root hint has already been validated to be supported by
            # the above call to the same function, this call is guaranteed to
            # *NEVER* raise an exception for that hint.
            die_unless_hint_pep_supported(
                hint=hint_curr, hint_label=hint_child_label)
            # Else, this hint is supported.

            # Assert that this hint is unignorable. Iteration below generating
            # code for child hints of the current parent hint is *REQUIRED* to
            # explicitly ignore ignorable child hints. Since the caller has
            # explicitly ignored ignorable root hints, these two guarantees
            # together ensure that all hints visited by this breadth-first
            # search *SHOULD* be unignorable. Naturally, we validate that here.
            assert not is_hint_ignorable(hint_curr), (
                '{} {!r} ignorable.'.format(hint_child_label, hint_curr))

            # Argumentless "typing" attribute uniquely identifying this hint.
            hint_curr_attr = get_hint_pep_typing_attr(hint_curr)

            # If this attribute is currently unsupported, raise an exception.
            #
            # Note the human-readable label prefixing the representations of
            # child PEP-compliant type hints is unconditionally passed. Since
            # the root hint has already been validated to be supported by the
            # above call to the die_unless_hint_pep_supported() function, this
            # call is guaranteed to *NEVER* raise exceptions for the root hint.
            die_unless_hint_pep_typing_attr_supported(
                hint=hint_curr_attr, hint_label=hint_child_label)
            # Else, this attribute is supported.

            # Python code snippet expanding to the current level of indentation
            # appropriate for the currently iterated child hint.
            #
            # Note that this is almost always but technically *NOT* always
            # required below by logic generating code type-checking the
            # currently visited parent hint. Naturally, unconditionally setting
            # this string here trivially optimizes the common case.
            indent_child = indent_curr + CODE_INDENT_1

            # True only if...
            is_pith_curr_assign_expr = (
                # The active Python interpreter targets Python >= 3.8 *AND*...
                IS_PYTHON_AT_LEAST_3_8 and
                # The current pith is *NOT* the root pith.
                #
                # Note that we explicitly test against piths rather than
                # seemingly equivalent metadata to account for edge cases.
                # Notably, child hints of unions (and possibly other "typing"
                # objects) do *NOT* narrow the current pith and are *NOT* the
                # root hint; ergo, a seemingly equivalent test like
                # "hints_meta_index_curr != 0" would generate false positives
                # and thus unnecessarily inefficient code.
                pith_curr_expr != pith_root_expr
            )

            #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            # NOTE: Whenever adding support for (i.e., when generating code
            # type-checking) a new "typing" attribute below, similar support
            # for that attribute *MUST* also be added to the parallel:
            # * "beartype._util.hint.pep.utilhintpeperror" submodule (i.e.,
            #   raising exceptions when the current pith fails this check).
            # * "beartype._util.hint.pep.utilhintpepdata.TYPING_ATTRS_SUPPORTED"
            #   frozen set of all supported argumentless "typing" attributes.
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
            #   mapping from each support argumentless typing attribute to
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
            if hint_curr_attr in TYPING_ATTRS_UNION:
                # Tuple of all subscripted arguments defining this union,
                # localized for both minor efficiency and major readability.
                #
                # Note that the "__args__" dunder attribute is *NOT* generally
                # guaranteed to exist for arbitrary PEP-compliant type hints
                # but is guaranteed to exist for all unions other than the
                # shallowly ignorable argumentless "typing.Optional" and
                # "typing.Union" attributes. Ergo, this attribute is guaranteed
                # to exist here.
                hint_childs = hint_curr.__args__

                # Assert this union is subscripted by one or more child hints.
                # Note this should *ALWAYS* be the case, as:
                #
                # * The unsubscripted "typing.Union" object is explicitly
                #   listed in the "HINTS_SHALLOW_IGNORABLE" set and should thus
                #   have already been ignored when present.
                # * The "typing" module explicitly prohibits empty
                #   subscription: e.g.,
                #       >>> typing.Union[]
                #       SyntaxError: invalid syntax
                #       >>> typing.Union[()]
                #       TypeError: Cannot take a Union of no types.
                assert hint_childs, (
                    '{} {!r} unsubscripted.'.format(hint_child_label, hint))
                # Else, this union is subscripted by two or more arguments. Why
                # two rather than one? Because the "typing" module reduces
                # unions of one argument to that argument: e.g.,
                #     >>> import typing
                #     >>> typing.Union[int]
                #     int

                # Clear the sets of all PEP-compliant and -noncompliant types
                # listed as subscripted arguments of this union. Since these
                # types require fundamentally different forms of type-checking,
                # prefiltering arguments into these sets *BEFORE* generating
                # code type-checking these arguments improves both efficiency
                # and maintainability below.
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
                    assert hint_child not in HINTS_SHALLOW_IGNORABLE, (
                        '{} ignorable PEP union {!r} not ignored.'.format(
                            hint_child_label, hint_curr))

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
                        hint_childs_pep_add(hint_child)
                    # Else, this child hint is PEP-noncompliant. In this case,
                    # filter this child hint into the list of PEP-noncompliant
                    # arguments.
                    else:
                        hint_childs_nonpep_add(hint_child)
                # All subscripted arguments of this union are now prefiltered
                # into the list of PEP-compliant or -noncompliant arguments.

                # Initialize the code type-checking the current pith against
                # these arguments to the substring prefixing all such code.
                func_curr_code = PEP_CODE_CHECK_HINT_UNION_PREFIX

                # If this union is subscripted by one or more PEP-noncompliant
                # arguments, generate efficient code type-checking these
                # arguments before less efficient code type-checking any
                # PEP-compliant arguments subscripting this union.
                if hint_childs_nonpep:
                    #FIXME: Refactor to leverage f-strings after dropping
                    #Python 3.5 support, which are the optimal means of
                    #performing string formatting.

                    # Append code type-checking these arguments.
                    #
                    # Defer formatting the "indent_curr" prefix into this code
                    # until below for efficiency.
                    func_curr_code += (
                        PEP_CODE_CHECK_HINT_UNION_ARG_NONPEP_format(
                            pith_curr_expr=pith_curr_expr,
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

                # If this union is also subscripted by one or more
                # PEP-compliant arguments, generate less efficient code
                # type-checking these arguments.
                if hint_childs_pep:
                    # For each PEP-compliant child hint listed as a subscripted
                    # argument of this union...
                    for hint_child in hint_childs_pep:
                        # Placeholder string to be globally replaced by code
                        # type-checking the child pith against this child hint.
                        hint_child_placeholder = (
                            get_next_pep_hint_placeholder())

                        #FIXME: *WOOPS!* Premature optimization alert. Given
                        #that the fastest way to initialize a small fixed list
                        #is by slice-assigning from the equivalent tuple, we'd
                        #might as well dispense entirely with this fixed list
                        #and just use the tuple as is. Maybe? Let's profile.
                        #
                        #If faster, we can probably at least dispense with
                        #"_HINT_META_SIZE" above.

                        # List of metadata describing this child hint.
                        #
                        # Note that exhaustive profiling has demonstrated
                        # slice-assigning this list's items to be mildly
                        # faster than individually assigning these items:
                        #      $ command python3 -m timeit -s \
                        #      .     'muh_list = ["a", "b", "c", "d",]' \
                        #      .     'muh_list[:] = "e", "f", "g", "h"'
                        #      2000000 loops, best of 5: 131 nsec per loop
                        #      $ command python3 -m timeit -s \
                        #      .     'muh_list = ["a", "b", "c", "d",]' \
                        #      .     'muh_list[0] = "e"
                        #      . muh_list[1] = "f"
                        #      . muh_list[2] = "g"
                        #      . muh_list[3] = "h"'
                        #      2000000 loops, best of 5: 199 nsec per loop
                        hint_child_meta = acquire_fixed_list(_HINT_META_SIZE)
                        hint_child_meta[:] = (
                            hint_child,
                            hint_child_placeholder,
                            pith_curr_expr,
                            indent_child,
                        )

                        # Increment the 0-based index of metadata describing
                        # the last visitable hint in the "hints_meta" list
                        # *BEFORE* overwriting the existing metadata at this
                        # index.
                        #
                        # Note that this index is guaranteed to *NOT* exceed
                        # the fixed length of this list, by prior validation.
                        hints_meta_index_last += 1

                        # Inject this metadata at this index of this list.
                        hints_meta[hints_meta_index_last] = hint_child_meta

                        # Append code type-checking this argument.
                        #
                        # Defer formatting the "indent_curr" prefix into this
                        # code until below for efficiency.
                        func_curr_code += (
                            PEP_CODE_CHECK_HINT_UNION_ARG_PEP_format(
                                hint_child_placeholder=hint_child_placeholder))

                # If this code is *NOT* its initial value, this union is
                # subscripted by one or more unignorable arguments and the
                # above logic generated code type-checking these arguments. In
                # this case...
                if func_curr_code is not PEP_CODE_CHECK_HINT_UNION_PREFIX:
                    # Munge this code to...
                    func_curr_code = (
                        # Strip the erroneous " or" suffix appended by the
                        # last child hint from this code.
                        func_curr_code[:-3] +
                        # Suffix this code by the substring suffixing all such
                        # code.
                        PEP_CODE_CHECK_HINT_UNION_SUFFIX
                    # Format the "indent_curr" prefix into this code deferred
                    # above for efficiency.
                    ).format(indent_curr=indent_curr)
                # Else, this snippet is its initial value and thus ignorable.

            # ..............{ SEQUENCES                         }..............
            # If this hint...
            elif (
                # Is a standard sequence (e.g., "typing.List[int]") *AND*...
                hint_curr_attr in TYPING_ATTRS_SEQUENCE_STANDARD and
                # Is *NOT* its own argumentless "typing" attribute (e.g.,
                # "typing.List")...
                hint_curr is not hint_curr_attr
            # Then this hint is subscripted by one or more arguments.
            ):
                # Assert this attribute is isinstance()-able.
                assert hint_curr_attr in TYPING_ATTR_TO_TYPE_ORIGIN, (
                    '{} argumentless "typing" attribute {!r} '
                    'not isinstance()-able.'.format(
                        hint_child_label, hint_curr_attr))

                # Python expression evaluating to this origin type when
                # accessed via the private "__beartypistry" parameter.
                hint_curr_expr = register_typistry_type(
                    # Origin type of this attribute if any *OR* raise an
                    # exception -- which should *NEVER* happen, as all standard
                    # sequences originate from an origin type.
                    get_hint_type_origin(hint_curr_attr))

                # Tuple of all subscripted arguments defining this sequence,
                # localized for both minor efficiency and major readability.
                #
                # Note that the "__args__" dunder attribute is *NOT* generally
                # guaranteed to exist for arbitrary PEP-compliant type hints
                # but is specifically guaranteed to exist for all standard
                # sequences including the argumentless "typing.List",
                # "typing.MutableSequence", and "typing.Sequence" attributes.
                # Ergo, this attribute is guaranteed to exist here.
                hint_childs = hint_curr.__args__

                # Assert this sequence was subscripted by exactly one argument.
                # Note that the "typing" module should have already guaranteed
                # this on our behalf. Still, we trust nothing and no one:
                #     >>> import typing as t
                #     >>> t.List[int, str]
                #     TypeError: Too many parameters for typing.List; actual 2, expected 1
                assert len(hint_childs) == 1, (
                    '{} sequence {!r} subscripted by '
                    'multiple arguments.'.format(hint_child_label, hint_curr))

                # Lone child hint of this parent hint.
                hint_child = hint_childs[0]

                #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                # CAVEATS: Synchronize changes here with logic below.
                #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

                # If this child hint is *NOT* ignorable, deeply type-check both
                # the type of the current pith *AND* a randomly indexed item of
                # this pith. Specifically...
                if not is_hint_ignorable(hint_child):
                    # Record that a pseudo-random integer is now required.
                    is_func_code_needs_random_int = True

                    # If the active Python interpreter targets at least Python
                    # 3.8 *AND* this parent hint is not the root hint, then all
                    #   conditions needed to assign the current pith to a
                    #   unique local variable via a Python >= 3.8-specific
                    #   assignment expression are satisfied. In this case...
                    if is_pith_curr_assign_expr:
                        # Full Python expression yielding the value of the
                        # current pith *BEFORE* reducing the current pith
                        # expression to the name of this local variable.
                        pith_curr_full_expr = pith_curr_expr

                        # Increment the integer suffixing the name of this
                        # variable *BEFORE* defining this local variable.
                        pith_curr_assign_expr_name_counter += 1

                        # Reduce the current pith expression to the name of
                        # this local variable.
                        pith_curr_expr = (
                            PEP_CODE_PITH_NAME_PREFIX +
                            str(pith_curr_assign_expr_name_counter))

                        # Python >= 3.8-specific assignment expression
                        # assigning this full expression to this variable.
                        pith_curr_assign_expr = (
                            PEP_CODE_PITH_ASSIGN_EXPR_format(
                                pith_curr_expr=pith_curr_expr,
                                pith_curr_full_expr=pith_curr_full_expr,
                            ))
                    # Else, one or more of these conditions have *NOT* been
                    # satisfied. In this case, preserve the Python code snippet
                    # evaluating to the current pith as is.
                    else:
                        pith_curr_assign_expr = pith_curr_expr

                    # Placeholder string to be globally replaced by code
                    # type-checking the child pith against this child hint.
                    hint_child_placeholder = get_next_pep_hint_placeholder()

                    # List of metadata describing this child hint. (See above.)
                    hint_child_meta = acquire_fixed_list(_HINT_META_SIZE)
                    hint_child_meta[:] = (
                        hint_child,
                        hint_child_placeholder,
                        # Python code snippet evaluating to a randomly indexed
                        # item of the current pith (i.e., standard sequence) to
                        # be type-checked against this child hint.
                        PEP_CODE_CHECK_HINT_SEQUENCE_STANDARD_PITH_CHILD_EXPR_format(
                            pith_curr_expr=pith_curr_expr),
                        indent_child,
                    )

                    # Increment the 0-based index of metadata describing the
                    # last visitable hint in the "hints_meta" list *BEFORE*
                    # overwriting the existing metadata at this index.
                    #
                    # Note that this index is guaranteed to *NOT* exceed the
                    # fixed length of this list, by prior validation.
                    hints_meta_index_last += 1

                    # Inject this metadata at this index of this list.
                    hints_meta[hints_meta_index_last] = hint_child_meta

                    #FIXME: Refactor to leverage f-strings after dropping
                    #Python 3.5 support, which are the optimal means of
                    #performing string formatting.

                    # Code type-checking the current pith against this type.
                    func_curr_code = (
                        PEP_CODE_CHECK_HINT_SEQUENCE_STANDARD_format(
                            indent_curr=indent_curr,
                            pith_curr_assign_expr=pith_curr_assign_expr,
                            pith_curr_expr=pith_curr_expr,
                            hint_curr_expr=hint_curr_expr,
                            hint_child_placeholder=hint_child_placeholder,
                        ))
                # Else, this child hint is ignorable. In this case, fallback to
                # generating trivial code shallowly type-checking the current
                # pith as an instance of this origin type.
                else:
                    #FIXME: Refactor to leverage f-strings after dropping
                    #Python 3.5 support, which are the optimal means of
                    #performing string formatting.

                    # Code type-checking the current pith against this type.
                    func_curr_code = PEP_CODE_CHECK_HINT_NONPEP_TYPE_format(
                        pith_curr_expr=pith_curr_expr,
                        hint_curr_expr=hint_curr_expr,
                    )

            # ..............{ GENERICS                          }..............
            #FIXME: Implement support for generics (i.e., user-defined
            #subclasses) here similarly to how we currently handle "Union".
            #To do so, we'll want to call:
            #* The newly defined get_hint_pep_generic_bases() getter to form
            #  the set of all base classes to generate code intersected
            #  with " and ", much like "Union" hints united with " or ".
            #  When doing so, we'll want to assert that the returned tuple
            #  is non-empty. This doesn't warrant an exception, as the
            #  is_hint_pep_custom() tester will have already ensured this
            #  tuple to be non-empty.
            #* The existing get_hint_pep_args() getter to iterate the set
            #  of all concrete arguments parametrizing superclass type
            #  variables. This doesn't apply to us at the moment, of
            #  course, but we'll still want to note this somewhere.
            #* To treat the multiple inheritance case as analogous to the
            #  "Union" case. If one considers it, their structure should be
            #  nearly identical -- the sole difference being the usage of
            #  " and " rather than " or " as the boolean operator connecting
            #  the code generated for each child. In this respect, we could
            #  then consider each superclass of a user-defined subclass to be a
            #  "child hint" of that subclass.
            #* Add a new "elif hint_curr_attr is Generic:" test below, whose
            #  code would basically be identical to the existing "if
            #  hint_curr_attr is Union:" test above. Indeed, we should inspect
            #  that existing test and if, by inspection, we believe the two can
            #  indeed be fully unified, we should do so as follows:
            #  * Define above:
            #      HINT_ATTR_BOOL_TO_OPERATOR = {
            #          Generic: 'and',
            #          Union:   'or',
            #      )
            #  * Replace the hardcoded 'or' in both
            #    "PEP_CODE_CHECK_HINT_UNION_ARG_PEP" and
            #    "PEP_CODE_CHECK_HINT_UNION_ARG_NONPEP" with a
            #    "{hint_curr_attr_bool_operator}" format variable.
            #  * Rename the "PEP_CODE_CHECK_HINT_UNION_*" suite of globals to
            #    "PEP_CODE_CHECK_HINT_BOOL_*" instead.
            #  * Refactor above:
            #      # Refactor this...
            #      if hint_curr_attr is Union:
            #
            #      # ...into this:
            #      hint_curr_attr_bool_operator = HINT_ATTR_BOOL_TO_OPERATOR.get(
            #          hint_curr_attr, None)
            #      if hint_curr_attr_bool_operator is not None:
            #
            #Welp, that's pretty brilliant. Nearly instantaneous support for
            #multiple inheritance in a generically orthogonal manner.

            # If this is a generic (i.e., user-defined class subclassing one or
            # more "typing" pseudo-superclasses)...
            # # elif hint_curr_attr is Generic:
            # #     pass

            # ..............{ FALLBACK                          }..............
            # Else, fallback to generating trivial code shallowly type-checking
            # the current pith as an instance of the PEP-noncompliant
            # non-"typing" origin class originating this argumentless "typing"
            # attribute (e.g., "list" for the attribute "List" associated with
            # the hint "List[int]").
            #
            # This fallback implements nominal implicit support for
            # argumentless "typing" attributes currently *NOT* explicitly
            # supported above.
            #
            # Note that this fallback already perfectly type-checks the proper
            # subset of argumentless typing attributes originating from origin
            # types that accept *NO* subscripted arguments, including:
            # * "typing.ByteString", which accepts *NO* subscripted arguments.
            #   "typing.ByteString" is simply an alias for the
            #   "collections.abc.ByteString" abstract base class (ABC) and thus
            #   already perfectly handled by this fallback logic.
            # * "typing.Hashable", which accepts *NO* subscripted arguments.
            #   "typing.Hashable" is simply an alias for the
            #   "collections.abc.Hashable" abstract base class (ABC) and thus
            #   already perfectly handled by this fallback logic.
            #
            # Ergo, this fallback *MUST* thus be preserved in perpetuity --
            # even after deeply type-checking all other argumentless typing
            # attributes originating from origin types above.
            else:
                # Assert this attribute is isinstance()-able.
                assert hint_curr_attr in TYPING_ATTR_TO_TYPE_ORIGIN, (
                    '{} argumentless "typing" attribute {!r} '
                    'not isinstance()-able.'.format(
                        hint_child_label, hint_curr_attr))

                #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                # CAVEATS: Synchronize changes here with logic below.
                #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

                #FIXME: Refactor to leverage f-strings after dropping
                #Python 3.5 support, which are the optimal means of
                #performing string formatting.

                # Code type-checking the current pith against this class.
                func_curr_code = PEP_CODE_CHECK_HINT_NONPEP_TYPE_format(
                    pith_curr_expr=pith_curr_expr,
                    # Python expression evaluating to this class when accessed
                    # via the private "__beartypistry" parameter.
                    hint_curr_expr=register_typistry_type(
                        # Origin type of this attribute if any *OR* raise an
                        # exception -- which should *NEVER* happen, as this
                        # attribute was validated above to be supported.
                        get_hint_type_origin(hint_curr_attr)
                    ),
                )
        # Else, this hint is *NOT* PEP-compliant.

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

            #FIXME: Refactor to leverage f-strings after dropping Python 3.5
            #support, which are the optimal means of performing string
            #formatting.

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
                '{} {!r} not PEP-compliant (i.e., '
                'neither "typing" object nor non-"typing" class).'.format(
                    hint_child_label, hint_curr))

        # ................{ CLEANUP                           }................
        # Inject this code into the body of this wrapper.
        func_code = func_code.replace(
            hint_curr_placeholder, func_curr_code)

        # Release the metadata describing the previously visited hint and
        # nullify this metadata in its list for safety.
        release_fixed_list(hint_curr_meta)
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
            '{} not type-checked.'.format(hint_root_label))
    # Else, the breadth-first search above successfully generated code.

    # Return all metadata required by higher-level callers.
    return (func_code, is_func_code_needs_random_int)
