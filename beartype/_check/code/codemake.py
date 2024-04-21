#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2024 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype **type-checking code factories** (i.e., low-level callables dynamically
generating pure-Python code snippets type-checking arbitrary objects against
PEP-compliant type hints).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ TODO                               }....................
# All "FIXME:" comments for this submodule reside in this package's "__init__"
# submodule to improve maintainability and readability here.

# ....................{ IMPORTS                            }....................
from beartype.roar import (
    BeartypeDecorHintPepException,
    BeartypeDecorHintPepUnsupportedException,
    BeartypeDecorHintPep593Exception,
)
from beartype.typing import Optional
from beartype._cave._cavefast import TestableTypes
from beartype._check.checkmagic import (
    ARG_NAME_CLS_STACK,
    ARG_NAME_GETRANDBITS,
    VAR_NAME_PITH_ROOT,
)
from beartype._check.code.codemagic import (
    EXCEPTION_PREFIX_FUNC_WRAPPER_LOCAL,
    EXCEPTION_PREFIX_HINT,
)
from beartype._check.code.codescope import (
    add_func_scope_type,
    add_func_scope_types,
    add_func_scope_type_or_types,
    express_func_scope_type_ref,
)
from beartype._check.code.snip.codesnipcls import PITH_INDEX_TO_VAR_NAME
from beartype._check.code.snip.codesnipstr import (
    CODE_HINT_CHILD_PLACEHOLDER_PREFIX,
    CODE_HINT_CHILD_PLACEHOLDER_SUFFIX,
    CODE_PEP484_INSTANCE_format,
    CODE_PEP484585_GENERIC_CHILD_format,
    CODE_PEP484585_GENERIC_PREFIX,
    CODE_PEP484585_GENERIC_SUFFIX,
    CODE_PEP484585_MAPPING_format,
    CODE_PEP484585_MAPPING_KEY_ONLY_format,
    CODE_PEP484585_MAPPING_KEY_VALUE_format,
    CODE_PEP484585_MAPPING_VALUE_ONLY_format,
    CODE_PEP484585_MAPPING_KEY_ONLY_PITH_CHILD_EXPR_format,
    CODE_PEP484585_MAPPING_VALUE_ONLY_PITH_CHILD_EXPR_format,
    CODE_PEP484585_MAPPING_KEY_VALUE_PITH_CHILD_EXPR_format,
    CODE_PEP484585_SEQUENCE_ARGS_1_format,
    CODE_PEP484585_SEQUENCE_ARGS_1_PITH_CHILD_EXPR_format,
    CODE_PEP484585_SUBCLASS_format,
    CODE_PEP484585_TUPLE_FIXED_EMPTY_format,
    CODE_PEP484585_TUPLE_FIXED_LEN_format,
    CODE_PEP484585_TUPLE_FIXED_NONEMPTY_CHILD_format,
    CODE_PEP484585_TUPLE_FIXED_NONEMPTY_PITH_CHILD_EXPR_format,
    CODE_PEP484585_TUPLE_FIXED_PREFIX,
    CODE_PEP484585_TUPLE_FIXED_SUFFIX,
    CODE_PEP484604_UNION_CHILD_PEP_format,
    CODE_PEP484604_UNION_CHILD_NONPEP_format,
    CODE_PEP484604_UNION_PREFIX,
    CODE_PEP484604_UNION_SUFFIX,
    CODE_PEP572_PITH_ASSIGN_EXPR_format,
    CODE_PEP586_LITERAL_format,
    CODE_PEP586_PREFIX_format,
    CODE_PEP586_SUFFIX,
    CODE_PEP593_VALIDATOR_IS_format,
    CODE_PEP593_VALIDATOR_METAHINT_format,
    CODE_PEP593_VALIDATOR_PREFIX,
    CODE_PEP593_VALIDATOR_SUFFIX_format,
)
from beartype._check.convert.convsanify import (
    sanify_hint_child_if_unignorable_or_none,
    sanify_hint_child,
)
from beartype._conf.confcls import BeartypeConf
from beartype._data.code.datacodeindent import INDENT_LEVEL_TO_CODE
from beartype._data.code.datacodemagic import (
    LINE_RSTRIP_INDEX_AND,
    LINE_RSTRIP_INDEX_OR,
)
from beartype._data.error.dataerrmagic import (
    EXCEPTION_PLACEHOLDER as EXCEPTION_PREFIX)
from beartype._data.hint.datahinttyping import (
    CodeGenerated,
    LexicalScope,
    TypeStack,
)
from beartype._data.hint.pep.sign.datapepsigns import (
    HintSignAnnotated,
    HintSignForwardRef,
    HintSignGeneric,
    HintSignLiteral,
    # HintSignNone,
    HintSignTuple,
    HintSignType,
)
from beartype._data.hint.pep.sign.datapepsignset import (
    HINT_SIGNS_MAPPING,
    HINT_SIGNS_ORIGIN_ISINSTANCEABLE,
    HINT_SIGNS_SEQUENCE_ARGS_1,
    HINT_SIGNS_SUPPORTED_DEEP,
    HINT_SIGNS_UNION,
)
from beartype._util.cache.utilcachecall import callable_cached
from beartype._util.cache.pool.utilcachepoollistfixed import (
    FIXED_LIST_SIZE_MEDIUM,
    acquire_fixed_list,
    release_fixed_list,
)
from beartype._util.cache.pool.utilcachepoolobjecttyped import (
    acquire_object_typed,
    release_object_typed,
)
from beartype._util.func.utilfuncscope import add_func_scope_attr
from beartype._util.hint.pep.proposal.pep484585.utilpep484585 import (
    is_hint_pep484585_tuple_empty)
from beartype._util.hint.pep.proposal.pep484585.utilpep484585 import (
    get_hint_pep484585_args)
from beartype._util.hint.pep.proposal.pep484585.utilpep484585generic import (
    get_hint_pep484585_generic_type,
    iter_hint_pep484585_generic_bases_unerased_tree,
)
from beartype._util.hint.pep.proposal.pep484585.utilpep484585type import (
    get_hint_pep484585_type_superclass)
from beartype._util.hint.pep.proposal.utilpep586 import (
    get_hint_pep586_literals)
from beartype._util.hint.pep.proposal.utilpep593 import (
    get_hint_pep593_metadata,
    get_hint_pep593_metahint,
)
from beartype._util.hint.pep.utilpepget import (
    get_hint_pep_args,
    get_hint_pep_sign,
    get_hint_pep_sign_or_none,
    get_hint_pep_origin_type_isinstanceable,
)
from beartype._util.hint.pep.utilpeptest import (
    die_if_hint_pep_unsupported,
    is_hint_pep,
    is_hint_pep_args,
)
from beartype._util.hint.utilhinttest import is_hint_ignorable
from beartype._util.kind.map.utilmapset import update_mapping
from beartype._util.text.utiltextmunge import replace_str_substrs
from beartype._util.text.utiltextrepr import represent_object
from random import getrandbits

# ....................{ MAKERS                             }....................
@callable_cached
def make_check_expr(
    # ..................{ ARGS ~ mandatory                   }..................
    hint: object,
    conf: BeartypeConf,

    # ..................{ ARGS ~ optional                    }..................
    cls_stack: TypeStack = None,
) -> CodeGenerated:
    '''
    **Type-checking expression factory** (i.e., low-level callable dynamically
    generating a pure-Python boolean expression type-checking an arbitrary
    object against the passed PEP-compliant type hint).

    This code factory performs a breadth-first search (BFS) over the abstract
    graph of nested type hints reachable from the subscripted arguments of the
    passed root type hint. For each such (possibly nested) hint, this factory
    embeds one or more boolean subexpressions validating a (possibly nested
    sub)object of an arbitrary object against that hint into the full boolean
    expression created and returned by this factory. In short, this factory is
    the beating heart of :mod:`beartype`. We applaud you for your perseverance.
    You finally found the essence of the Great Bear. You did it!! Now, we clap.

    This code factory is memoized for efficiency.

    Caveats
    -------
    **This factory intentionally accepts no** ``exception_prefix``
    **parameter.** Why? Since that parameter is typically specific to the
    context-sensitive use case of the caller, accepting that parameter would
    prevent this factory from memoizing the passed hint with the returned code,
    which would rather defeat the point. Instead, this factory only:

    * Returns generic non-working code containing the placeholder
      :data:`VAR_NAME_PITH_ROOT` substring that the caller is required to
      globally replace by either the name of the current parameter *or*
      ``return`` for return values (e.g., by calling the builtin
      :meth:`str.replace` method) to generate the desired non-generic working
      code type-checking that parameter or return value.
    * Raises generic non-human-readable exceptions containing the placeholder
      :attr:`beartype._util.error.utilerrraise.EXCEPTION_PLACEHOLDER` substring
      that the caller is required to explicitly catch and raise non-generic
      human-readable exceptions from by calling the
      :func:`beartype._util.error.utilerrraise.reraise_exception_placeholder`
      function.

    Parameters
    ----------
    hint : object
        PEP-compliant type hint to be type-checked.
    conf : BeartypeConf
        **Beartype configuration** (i.e., self-caching dataclass encapsulating
        all settings configuring type-checking for the passed object).
    cls_stack : TypeStack, optional
        **Type stack** (i.e., either a tuple of the one or more
        :func:`beartype.beartype`-decorated classes lexically containing the
        class variable or method annotated by this hint *or* :data:`None`).
        Defaults to :data:`None`.

    Returns
    -------
    CodeGenerated
        Tuple containing the Python code snippet dynamically generated by this
        code generator and metadata describing that code. See the
        :attr:`beartype._data.hint.datahinttyping.CodeGenerated` type hint for details.

    Raises
    ------
    BeartypeDecorHintPepException
        If this object is *not* a PEP-compliant type hint.
    BeartypeDecorHintPepUnsupportedException
        If this object is a PEP-compliant type hint currently unsupported by
        the :func:`beartype.beartype` decorator.
    BeartypeDecorHintPep484Exception
        If one or more PEP-compliant type hints visitable from this object are
        nested :attr:`typing.NoReturn` child hints, since
        :attr:`typing.NoReturn` is valid *only* as a non-nested return hint.
    BeartypeDecorHintPep593Exception
        If one or more PEP-compliant type hints visitable from this object
        subscript the :pep:`593`-compliant :class:`typing.Annotated` class such
        that:

        * The second argument subscripting that class is an instance of the
          :class:`beartype.vale.Is` class.
        * One or more further arguments subscripting that class are *not*
          instances of the :class:`beartype.vale.Is` class.

    Warns
    -----
    BeartypeDecorHintPep585DeprecationWarning
        If one or more :pep:`484`-compliant type hints visitable from this
        object have been deprecated by :pep:`585`.
    '''

    # ..................{ LOCALS ~ hint : root               }..................
    # Top-level hint relocalized for disambiguity.
    hint_root = hint

    # Delete the passed parameter whose name is ambiguous within the context of
    # this function for similar disambiguity.
    del hint

    # ..................{ LOCALS ~ hint : current            }..................
    # Currently visited hint.
    hint_curr = None

    # Current unsubscripted typing attribute associated with this hint (e.g.,
    # "Union" if "hint_curr == Union[int, str]").
    hint_curr_sign = None

    # Python expression evaluating to an isinstanceable type (e.g., origin type)
    # associated with the currently visited type hint if any.
    hint_curr_expr = None

    # Placeholder string to be globally replaced in the Python code snippet to
    # be returned (i.e., "func_wrapper_code") by a Python code snippet
    # type-checking the current pith expression (i.e.,
    # "pith_curr_var_name") against the currently visited hint (i.e.,
    # "hint_curr").
    hint_curr_placeholder = None

    # Full Python expression evaluating to the value of the current pith (i.e.,
    # possibly nested object of the passed parameter or return value to be
    # type-checked against the currently visited hint).
    #
    # Note that this is intentionally *NOT* an assignment expression but rather
    # the original inefficient expression provided by the parent type hint of
    # the currently visited hint.
    pith_curr_expr = None

    # Name of the current pith variable (i.e., local Python variable in the
    # body of the wrapper function whose value is that of the current pith).
    # This name is either:
    # * Initially, the name of the currently type-checked parameter or return.
    # * On subsequently type-checking nested items of the parameter or return,
    #   the name of the local variable uniquely assigned to by the assignment
    #   expression defined by "pith_curr_assign_expr" (i.e., the left-hand side
    #   (LHS) of that assignment expression).
    pith_curr_var_name = VAR_NAME_PITH_ROOT

    # ..................{ LOCALS ~ hint : child              }..................
    # Currently iterated PEP-compliant child hint subscripting the currently
    # visited hint, initialized to the root hint to enable the subsequently
    # called _enqueue_hint_child() function to enqueue the root hint.
    hint_child = hint_root

    # Current unsubscripted typing attribute associated with this child hint
    # (e.g., "Union" if "hint_child == Union[int, str]").
    hint_child_sign = None

    # ..................{ LOCALS ~ hint : childs             }..................
    # Current tuple of all child hints subscripting the currently visited hint
    # (e.g., "(int, str)" if "hint_curr == Union[int, str]").
    hint_childs: tuple = None  # type: ignore[assignment]

    # Current list of all output child hints to replace the Current tuple of all
    # input child hints subscripting the currently visited hint with.
    hint_childs_new: list = None  # type: ignore[assignment]

    # Number of child hints subscripting the currently visited hint.
    hint_childs_len: int = None  # type: ignore[assignment]

    # 0-based index of the currently iterated child hint of the "hint_childs"
    # tuple.
    hint_childs_index: int = None  # type: ignore[assignment]

    # Current tuple of all child child hints subscripting the currently visited
    # child hint (e.g., "(int, str)" if "hint_child == Union[int, str]").
    hint_child_childs: tuple = None  # type: ignore[assignment]

    # ..................{ LOCALS ~ hint : metadata           }..................
    # Tuple of metadata describing the currently visited hint, appended by
    # the previously visited parent hint to the "hints_meta" stack.
    hint_curr_meta: tuple = None  # type: ignore[assignment]

    # Fixed list of all metadata describing all visitable hints currently
    # discovered by the breadth-first search (BFS) below. This list acts as a
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
    # integer maintained by this BFS is strictly less than
    # "FIXED_LIST_SIZE_MEDIUM", as this constraint is already guaranteed to be
    # the case.
    hints_meta = acquire_fixed_list(FIXED_LIST_SIZE_MEDIUM)

    # 0-based index of metadata describing the currently visited hint in the
    # "hints_meta" list.
    hints_meta_index_curr = 0

    # 0-based index of metadata describing the last visitable hint in the
    # "hints_meta" list, initialized to "-1" to ensure that the initial
    # incrementation of this index by the _enqueue_hint_child() directly called
    # below initializes index 0 of the "hints_meta" fixed list.
    #
    # For efficiency, this integer also uniquely identifies the currently
    # iterated child type hint of the currently visited parent type hint.
    hints_meta_index_last = -1

    # ..................{ LOCALS ~ func : code               }..................
    # Python code snippet type-checking the current pith against the currently
    # visited hint (to be appended to the "func_wrapper_code" string).
    func_curr_code: str = None  # type: ignore[assignment]

    # ..................{ LOCALS ~ func : code : locals      }..................
    # Local scope (i.e., dictionary mapping from the name to value of each
    # attribute referenced in the signature) of this wrapper function required
    # by this Python code snippet.
    func_wrapper_scope: LexicalScope = {}

    # True only if one or more PEP-compliant type hints visitable from this
    # root hint require a pseudo-random integer. If true, the higher-level
    # beartype._decor.wrap.wrapmain.generate_code() function prefixes the body
    # of this wrapper function with code generating such an integer.
    is_var_random_int_needed = False

    # ..................{ LOCALS ~ indentation               }..................
    # Python code snippet expanding to the current level of indentation
    # appropriate for the currently visited hint.
    indent_curr: str = None  # type: ignore[assignment]

    # 1-based indentation level describing the current level of indentation
    # appropriate for the currently visited hint.
    indent_level_curr = 2

    # 1-based indentation level describing the current level of indentation
    # appropriate for the currently iterated child hint, initialized to the
    # root hint indentation level to enable the subsequently called
    # _enqueue_hint_child() function to enqueue the root hint.
    indent_level_child = indent_level_curr

    # ..................{ LOCALS ~ pep : 484                 }..................
    # Set of the unqualified classnames referred to by all relative forward
    # references visitable from this root hint if any *OR* "None" otherwise
    # (i.e., if no such forward references are visitable).
    hint_refs_type_basename: Optional[set] = None

    # ..................{ LOCALS ~ pep : 572                 }..................
    # The following local variables isolated to this subsection are only
    # relevant when the currently visited hint is *NOT* the root hint (i.e.,
    # "hint_root"). If the currently visited hint is the root hint, the current
    # pith has already been localized to a local variable whose name is the
    # value of the "VAR_NAME_PITH_ROOT" string global and thus need *NOT* be
    # relocalized to another local variable using an assignment expression.
    #
    # These variables enable a non-trivial runtime optimization eliminating
    # repeated computations to obtain the child pith needed to type-check child
    # hints. For example, if the current hint constrains the current pith to be
    # a standard sequence, the child pith of that parent pith is a random item
    # selected from this sequence; since obtaining this child pith is
    # non-trivial, the computation required to do so is performed only once by
    # assigning this child pith to a unique local variable during type-checking
    # and then repeatedly type-checking that variable rather than the logic
    # required to continually reacquire this child pith: e.g.,
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
    #     # The same conditional under Python >= 3.8.
    #     if not (
    #         isinstance(__beartype_pith_0, list) and
    #         (
    #             isinstance(__beartype_pith_1 := __beartype_pith_0[__beartype_random_int % len(__beartype_pith_0)], list) and
    #             isinstance(__beartype_pith_1[__beartype_random_int % len(__beartype_pith_1)], str) if __beartype_pith_1 else True
    #         ) if __beartype_pith_0 else True
    #     ):
    #
    # Note that:
    # * The random item selected from the root pith (i.e., "__beartype_pith_1
    #   := __beartype_pith_0[__beartype_random_int % len(__beartype_pith_0)")
    #   only occurs once under Python >= 3.8 but repeatedly under Python < 3.8.
    #   In both cases, the same semantic type-checking is performed regardless
    #   of optimization.
    # * This optimization implicitly "bottoms out" when the currently visited
    #   hint is *NOT* subscripted by unignorable child hints. If all child hints
    #   of the currently visited hint are either ignorable (e.g., "object",
    #   "Any") *OR* are unignorable isinstanceable types (e.g., "int", "str"),
    #   the currently visited hint has *NO* meaningful child hints and is thus
    #   effectively a leaf node with respect to performing this optimization.

    # Integer suffixing the name of each local variable assigned the value of
    # the current pith in a assignment expression, thus uniquifying this
    # variable in the body of the current wrapper function.
    #
    # Note that this integer is intentionally incremented as an efficient
    # low-level scalar rather than as an inefficient high-level
    # "itertools.Counter" object. Since both are equally thread-safe in the
    # internal context of this function body, the former is preferable.
    pith_curr_var_name_index = 0

    # Assignment expression assigning this full Python expression to the unique
    # local variable assigned the value of this expression.
    pith_curr_assign_expr: str = None  # type: ignore[assignment]

    # ..................{ CLOSURES                           }..................
    # Closures centralizing frequently repeated logic, addressing Don't Repeat
    # Yourself (DRY) concerns during the breadth-first search (BFS) below.

    def _enqueue_hint_child(pith_child_expr: str) -> str:
        '''
        **Enqueue** (i.e., append) a new tuple of metadata describing the
        currently iterated child type hint to the end of the ``hints_meta``
        queue, enabling this hint to be visited by the ongoing breadth-first
        search (BFS) traversing over this queue.

        Parameters
        ----------
        pith_child_expr : str
            Python code snippet evaluating to the child pith to be type-checked
            against the currently iterated child type hint.

        This closure also implicitly expects the following local variables of
        the outer scope to be set to relevant values:

        hint_child : object
            Currently iterated child type hint subscripting the currently
            visited type hint.

        Returns
        -------
        str
            Placeholder string to be subsequently replaced by code type-checking
            this child pith against this child type hint.
        '''
        # print(f'pith_child_expr: {pith_child_expr}')

        # Allow these local variables of the outer scope to be modified below.
        nonlocal hints_meta_index_last

        # Increment both the 0-based index of metadata describing the last
        # visitable hint in the "hints_meta" list and the unique identifier of
        # the currently iterated child hint *BEFORE* overwriting the existing
        # metadata at this index.
        #
        # Note this index is guaranteed to *NOT* exceed the fixed length of
        # this list, by prior validation.
        hints_meta_index_last += 1

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
        #   and undebuggable Python code.
        hint_child_placeholder = (
            f'{CODE_HINT_CHILD_PLACEHOLDER_PREFIX}'
            f'{str(hints_meta_index_last)}'
            f'{CODE_HINT_CHILD_PLACEHOLDER_SUFFIX}'
        )

        # Create and insert a new tuple of metadata describing this child hint
        # at this index of this list.
        #
        # Note that this assignment is guaranteed to be safe, as
        # "FIXED_LIST_SIZE_MEDIUM" is guaranteed to be substantially larger than
        # "hints_meta_index_last".
        hints_meta[hints_meta_index_last] = (
            hint_child,
            hint_child_placeholder,
            pith_child_expr,
            pith_curr_var_name_index,
            indent_level_child,
        )

        # Return this placeholder string.
        return hint_child_placeholder

    # ..................{ LOCALS ~ closure                   }..................
    # Local variables calling one or more closures declared above and thus
    # deferred until after declaring those closures.

    # Placeholder string to be globally replaced in the Python code snippet to
    # be returned (i.e., "func_wrapper_code") by a Python code snippet
    # type-checking the child pith expression (i.e., "pith_child_expr") against
    # the currently iterated child hint (i.e., "hint_child"), initialized to a
    # placeholder describing the root hint.
    hint_child_placeholder = _enqueue_hint_child(VAR_NAME_PITH_ROOT)

    # Python code snippet type-checking the root pith against the root hint,
    # localized separately from the "func_wrapper_code" snippet to enable this
    # function to validate this code to be valid *BEFORE* returning this code.
    func_root_code = hint_child_placeholder

    # Python code snippet to be returned, seeded with a placeholder to be
    # replaced on the first iteration of the breadth-first search performed
    # below with a snippet type-checking the root pith against the root hint.
    func_wrapper_code = func_root_code

    # ..................{ SEARCH                             }..................
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
            f'index {hints_meta_index_curr} not tuple.'
        )

        #FIXME: ...heh. It's time, people. Sadly, it turns out that redefining
        #the _enqueue_hint() closure on *EVERY* call to this function is a huge
        #time sink -- far huger than anything else, actually. Therefore:
        #* Define a new "HintMeta" dataclass defining one slotted field for each
        #  of these metadata.
        #* Refactor the _enqueue_hint() closure into a HintMeta.enqueue_hint()
        #  method.
        #* Replace all calls to the _enqueue_hint() closure with calls to the
        #  HintMeta.enqueue_hint() method.
        #* Remove the _enqueue_hint() closure.
        #* Remove all of the following locals from this function in favour of
        #  the "HintMeta" slotted fields of the same names:
        #  * hint_curr.
        #  * hint_curr_placeholder.
        #  * pith_curr_expr.
        #  * pith_curr_var_name_index.
        #  * indent_level_curr.

        # Localize metadata for both efficiency and f-string purposes.
        #
        # Note that list unpacking is substantially more efficient than
        # manually indexing list items; the former requires only a single Python
        # statement, whereas the latter requires "n" Python statements.
        (
            hint_curr,
            hint_curr_placeholder,
            pith_curr_expr,
            pith_curr_var_name_index,
            indent_level_curr,
        ) = hint_curr_meta
        # print(f'Visiting type hint {repr(hint_curr)}...')

        #FIXME: Comment this sanity check out after we're sufficiently
        #convinced this algorithm behaves as expected. While useful, this check
        #requires a linear search over the entire code and is thus costly.
        # assert hint_curr_placeholder in func_wrapper_code, (
        #     '{} {!r} placeholder {} not found in wrapper body:\n{}'.format(
        #         hint_curr_exception_prefix, hint, hint_curr_placeholder, func_wrapper_code))

        # ................{ PEP                                }................
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
            #        hint=hint_curr, exception_prefix=hint_curr_exception_prefix)
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
                hint=hint_curr, exception_prefix=EXCEPTION_PREFIX)
            # Else, this hint is supported.

            # Assert that this hint is unignorable. Iteration below generating
            # code for child hints of the current parent hint is *REQUIRED* to
            # explicitly ignore ignorable child hints. Since the caller has
            # explicitly ignored ignorable root hints, these two guarantees
            # together ensure that all hints visited by this breadth-first
            # search *SHOULD* be unignorable. Naturally, we validate that here.
            assert not is_hint_ignorable(hint_curr), (
                f'{EXCEPTION_PREFIX}ignorable type hint '
                f'{repr(hint_curr)} not ignored.'
            )

            # Sign uniquely identifying this hint.
            hint_curr_sign = get_hint_pep_sign(hint_curr)
            # print(f'Visiting PEP type hint {repr(hint_curr)} sign {repr(hint_curr_sign)}...')

            #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            # NOTE: Whenever adding support for (i.e., when generating code
            # type-checking) a new "typing" attribute below, similar support
            # for that attribute *MUST* also be added to the parallel:
            # * "beartype._check.error" subpackage, which raises exceptions on
            #   the current pith failing this check.
            # * "beartype._data.hint.pep.sign.datapepsignset.HINT_SIGNS_SUPPORTED_DEEP"
            #   frozen set of all signs for which this function generates deeply
            #   type-checking code.
            #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

            #FIXME: Python 3.10 provides proper syntactic support for "case"
            #statements, which should allow us to dramatically optimize this
            #"if" logic into equivalent "case" logic *AFTER* we drop support
            #for Python 3.9. Of course, that will be basically never, so we'll
            #have to preserve this for basically forever. What you gonna do?
            #FIXME: Actually, we should probably just leverage a hypothetical
            #"beartype.vale.IsInline[...]" validator to coerce this slow O(n)
            #procedural logic into fast O(1) object-oriented logic. Of course,
            #object-oriented logic is itself slow -- so we only do this if we
            #can sufficiently memoize that logic. Consideration!

            # Switch on (as in, pretend Python provides a "case" statement)
            # the sign identifying this hint to decide which type of code to
            # generate to type-check the current pith against the current hint.
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
            #
            # ..............{ SHALLOW                            }..............
            # Perform shallow type-checking logic (i.e., logic that does *NOT*
            # recurse and thus "bottoms out" at this hint) *BEFORE* deep
            # type-checking logic. The latter needs additional setup (e.g.,
            # generation of assignment expressions) *NOT* needed by the former,
            # whose requirements are more understandably minimalist. Note that:
            # * Shallow type-checking code should access this pith via
            #   "pith_curr_expr". Since this code does *NOT* recurse,
            #   "pith_curr_expr" accesses this pith optimally efficiently
            # * Deep type-checking code should access this pith via
            #   "pith_assign_expr". Since that code *DOES* recurse, only
            #   "pith_assign_expr" accesses this pith optimally efficiently;
            #   "pith_curr_expr" accesses this pith extremely inefficiently.
            #
            # ..............{ ORIGIN                             }..............
            # If this hint both...
            if (
                # Originates from an origin type and may thus be shallowly
                # type-checked against that type *AND is either...
                hint_curr_sign in HINT_SIGNS_ORIGIN_ISINSTANCEABLE and (
                    # Unsubscripted *OR*...
                    not is_hint_pep_args(hint_curr) or
                    #FIXME: Remove this branch *AFTER* deeply supporting all
                    #hints.
                    # Currently unsupported with deep type-checking...
                    hint_curr_sign not in HINT_SIGNS_SUPPORTED_DEEP
                )
            ):
            # Then generate trivial code shallowly type-checking the current
            # pith as an instance of the origin type originating this sign
            # (e.g., "list" for the hint "typing.List[int]").
                # Code type-checking the current pith against this origin type.
                func_curr_code = CODE_PEP484_INSTANCE_format(
                    pith_curr_expr=pith_curr_expr,
                    # Python expression evaluating to this origin type.
                    hint_curr_expr=add_func_scope_type(
                        # Origin type of this hint if any *OR* raise an
                        # exception -- which should *NEVER* happen, as this hint
                        # was validated above to be supported.
                        cls=get_hint_pep_origin_type_isinstanceable(hint_curr),
                        func_scope=func_wrapper_scope,
                        exception_prefix=EXCEPTION_PREFIX_FUNC_WRAPPER_LOCAL,
                    ),
                )
            # Else, this hint is either subscripted, not shallowly
            # type-checkable, *OR* deeply type-checkable.
            #
            # ..............{ FORWARDREF                         }..............
            # If this hint is a forward reference...
            elif hint_curr_sign is HintSignForwardRef:
                # Render this forward reference accessible to the body of this
                # wrapper function by populating:
                # * A Python expression evaluating to the class referred to by
                #   this forward reference when accessed via the private
                #   "__beartypistry" parameter.
                # * A set of the unqualified classnames referred to by all
                #   relative forward references, including this reference if
                #   relative. If this set was previously uninstantiated (i.e.,
                #   "None"), this assignment initializes this local to the new
                #   set instantiated by this call; else, this assignment
                #   preserves this local set as is.
                hint_curr_expr, hint_refs_type_basename = (
                    express_func_scope_type_ref(
                        forwardref=hint_curr,
                        forwardrefs_class_basename=hint_refs_type_basename,
                        func_scope=func_wrapper_scope,
                        exception_prefix=EXCEPTION_PREFIX,
                    ))

                # Code type-checking the current pith against this class.
                func_curr_code = CODE_PEP484_INSTANCE_format(
                    pith_curr_expr=pith_curr_expr,
                    hint_curr_expr=hint_curr_expr,
                )
            # Else, this hint is *NOT* a forward reference.
            #
            # Since this hint is *NOT* shallowly type-checkable, this hint
            # *MUST* be deeply type-checkable. So, we do so now.
            #
            # ..............{ DEEP                               }..............
            # Perform deep type-checking logic (i.e., logic that is guaranteed
            # to recurse and thus *NOT* "bottom out" at this hint).
            else:
                # Tuple of all arguments subscripting this hint if any *OR* the
                # empty tuple otherwise (e.g., if this hint is its own
                # unsubscripted "typing" attribute).
                #
                # Note that the "__args__" dunder attribute is *NOT* guaranteed
                # to exist for arbitrary PEP-compliant type hints. Ergo, we
                # obtain this attribute via a higher-level utility getter
                # instead.
                hint_childs = get_hint_pep_args(hint_curr)
                hint_childs_len = len(hint_childs)

                # Python code snippet expanding to the current level of
                # indentation appropriate for the current hint.
                indent_curr = INDENT_LEVEL_TO_CODE[indent_level_curr]

                # 1-based indentation level describing the current level of
                # indentation appropriate for the currently iterated child hint.
                indent_level_child = indent_level_curr + 1

                # ............{ DEEP ~ expression                  }............
                #FIXME: Unit test that this is behaving as expected. Doing so
                #will require further generalizations, including:
                #* In the "beartype._decor.decormain" submodule:
                #  * Detect when running under tests.
                #  * When running under tests, define a new
                #    "func_wrapper.__beartype_wrapper_code" attribute added to
                #    decorated callables to be the "func_wrapper_code" string
                #    rather than True. Note that this obviously isn't the right way
                #    to do source code association. Ideally, we'd at least
                #    interface with the stdlib "linecache" module (e.g., by calling
                #    the linecache.lazycache() function intended to be used to
                #    cache the source code for non-file-based modules) and possibly
                #    even go so far as to define a PEP 302-compatible beartype
                #    module loader. That's out of scope, so this suffices for now.
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
                #* In the "beartype._decor.decormain" submodule:
                #  * Do... something? Oh, boy. Why didn't we finish this comment?

                # If the expression yielding the current pith is neither...
                if not (
                    # The root pith *NOR*...
                    #
                    # Note that this is merely a negligible optimization for the
                    # common case in which the current pith is the root pith
                    # (i.e., this is the first iteration of the outermost loop).
                    # The subsequent call to the str.isidentifier() method is
                    # *MUCH* more expensive than this object identity test.
                    pith_curr_expr is VAR_NAME_PITH_ROOT or
                    # A simple Python identifier *NOR*...
                    pith_curr_expr.isidentifier() or
                    # A complex Python expression already containing the
                    # assignment expression-specific "walrus" operator ":=".
                    # Since this implies this expression to already be an
                    # assignment expression, needlessly reassigning the local
                    # variable to which this assignment expression was
                    # previously assigned to yet another redundant local
                    # variable only harms efficiency for *NO* tangible gain
                    # (e.g., expanding the efficient assignment expression
                    # "__beartype_pith_1 := next(iter(__beartype_pith_0))" to
                    # the inefficient assignment expression
                    # "__beartype_pith_2 := __beartype_pith_1 :=
                    # next(iter(__beartype_pith_0))").
                    #
                    # Note that this edge case is induced by closure calls
                    # performed below of the form:
                    #    _enqueue_hint_child(pith_curr_assign_expr)
                    #
                    # As of this writing, the only such edge case is a PEP 484-
                    # or 604-compliant union containing *ONLY* two or more
                    # PEP-compliant type hints (e.g., "list[str] | set[bytes]").
                    ':=' in pith_curr_expr
                ):
                    # Then the current pith is safely assignable to a unique
                    # local variable via an assignment expression.
                    #
                    # Note that we explicitly test against piths rather than
                    # seemingly equivalent metadata to account for edge cases.
                    # Notably, child hints of unions (and possibly other
                    # "typing" objects) do *NOT* narrow the current pith and are
                    # *NOT* the root hint. Ergo, a seemingly equivalent test
                    # like "hints_meta_index_curr != 0" would generate false
                    # positives and thus unnecessarily inefficient code.

                    # Increment the integer suffixing the name of this variable
                    # *BEFORE* defining this variable.
                    pith_curr_var_name_index += 1

                    # Name of this local variable.
                    pith_curr_var_name = PITH_INDEX_TO_VAR_NAME[
                        pith_curr_var_name_index]

                    # Assignment expression assigning this full expression to
                    # this local variable.
                    pith_curr_assign_expr = CODE_PEP572_PITH_ASSIGN_EXPR_format(
                        pith_curr_var_name=pith_curr_var_name,
                        pith_curr_expr=pith_curr_expr,
                    )
                # Else, the current pith is *NOT* safely assignable to a unique
                # local variable via an assignment expression. Since the
                # expression yielding the current pith is a simple Python
                # identifier, there is *NO* benefit to assigning that to another
                # local variable via another assignment expression, which would
                # just be an alias of the existing local variable assigned via
                # the existing assignment expression. Moreover, whereas chained
                # assignments are syntactically valid, chained assignment
                # expressions are syntactically invalid unless explicitly
                # protected by parens: e.g.,
                #     >>> a = b =    'Mother*Teacher*Destroyer'  # <-- fine
                #     >>> (a :=      "Mother's Abomination")     # <-- fine
                #     >>> (a :=
                #     ... (b := "Mother's Illumination"))        # <-- fine
                #     >>> (a := b := "Mother's Illumination")    # <-- not fine
                #     SyntaxError: invalid syntax
                #
                # In this case...
                else:
                    # Name of this local variable.
                    pith_curr_var_name = PITH_INDEX_TO_VAR_NAME[
                        pith_curr_var_name_index]

                    # Preserve the Python code snippet evaluating to the value
                    # of the current pith as is.
                    pith_curr_assign_expr = pith_curr_expr

                # ............{ UNION                              }............
                # If this hint is a union (e.g., "typing.Union[bool, str]",
                # typing.Optional[float]")...
                #
                # Note that unions are non-physical abstractions of physical
                # types and thus *NOT* themselves subject to type-checking;
                # only the subscripted arguments of unions are type-checked.
                # This differs from "typing" pseudo-containers like
                # "List[int]", in which both the parent "List" and child "int"
                # types represent physical types to be type-checked. Ergo,
                # unions themselves impose no narrowing of the current pith
                # expression and thus *CANNOT* by definition benefit from
                # assignment expressions. This differs from "typing"
                # pseudo-containers, which narrow the current pith expression
                # and thus do benefit from assignment expressions.
                if hint_curr_sign in HINT_SIGNS_UNION:
                    # Assert this union to be subscripted by one or more child
                    # hints. Note this should *ALWAYS* be the case, as:
                    # * The unsubscripted "typing.Union" object is explicitly
                    #   listed in the "HINTS_REPR_IGNORABLE_SHALLOW" set and
                    #   should thus have already been ignored when present.
                    # * The "typing" module explicitly prohibits empty union
                    #   subscription: e.g.,
                    #       >>> typing.Union[]
                    #       SyntaxError: invalid syntax
                    #       >>> typing.Union[()]
                    #       TypeError: Cannot take a Union of no types.
                    assert hint_childs, (
                        f'{EXCEPTION_PREFIX}union type hint '
                        f'{repr(hint_curr)} unsubscripted.'
                    )
                    # Else, this union is subscripted by two or more arguments.
                    # Why two rather than one? Because the "typing" module
                    # reduces unions of one argument to that argument: e.g.,
                    #     >>> import typing
                    #     >>> typing.Union[int]
                    #     int

                    # 0-based index of the currently iterated child hint.
                    hint_childs_index = 0

                    # For efficiency, reuse a previously created list of all
                    # new child hints of this parent union.
                    hint_childs_new = acquire_object_typed(list)
                    hint_childs_new.clear()

                    # For each subscripted argument of this union...
                    #
                    # Note that this preliminary iteration:
                    # * Modifies the "hint_childs" container being iterated over
                    #   and is thus intentionally implemented as a cumbersome
                    #   "while" loop rather than a convenient "for" loop.
                    # * Exists for the sole purpose of explicitly flattening
                    #   *ALL* child unions nested in this parent union. This
                    #   iteration *CANNOT* be efficiently combined with the
                    #   iteration performed below for that reason.
                    # * Does *NOT* recursively flatten arbitrarily nested
                    #   child unions regardless of nesting depth in this parent
                    #   union. Doing so is non-trivial and currently *NOT*
                    #   required by any existing edge cases. "Huzzah!"
                    while hint_childs_index < hint_childs_len:
                        # Current child hint of this union.
                        hint_child = hint_childs[hint_childs_index]

                        # This child hint sanified (i.e., sanitized) from this
                        # child hint if this child hint is reducible *OR*
                        # preserved as is otherwise (i.e., if this child hint is
                        # irreducible).
                        #
                        # Note that:
                        # * This sanification is intentionally performed
                        #   *BEFORE* this child hint is tested as being either
                        #   PEP-compliant or -noncompliant. Why? Because a small
                        #   subset of low-level reduction routines performed by
                        #   this high-level sanification actually expand a
                        #   PEP-noncompliant type into a PEP-compliant type
                        #   hint. This includes:
                        #   * The PEP-noncompliant "float' and "complex" types,
                        #     implicitly expanded to the PEP 484-compliant
                        #     "float | int" and "complex | float | int" type
                        #     hints (respectively) when the non-default
                        #     "conf.is_pep484_tower=True" parameter is enabled.
                        # * This sanification intentionally calls the
                        #   lower-level sanify_hint_child() rather than the
                        #   higher-level
                        #   sanify_hint_child_if_unignorable_or_none() sanifier.
                        #   Technically, the latter would suffice as well.
                        #   Pragmatically, both are semantically equivalent here
                        #   but the former is faster. Why? By definition, this
                        #   union is unignorable. If this union were ignorable,
                        #   the parent hint containing this union would already
                        #   have ignored this union. Moreover, *ALL* child
                        #   hints subscripting an unignorable union are
                        #   necessarily also unignorable. It follows that this
                        #   child hint need *NOT* be tested for ignorability.
                        # print(f'Sanifying union child hint {repr(hint_child)} under {repr(conf)}...')
                        hint_child = sanify_hint_child(
                            hint=hint_child,
                            conf=conf,
                            cls_stack=cls_stack,
                            exception_prefix=EXCEPTION_PREFIX,
                        )
                        # print(f'Sanified union child hint to {repr(hint_child)}...')

                        # Sign of this sanified child hint if this hint is
                        # PEP-compliant *OR* "None" otherwise (i.e., if this
                        # hint is PEP-noncompliant).
                        hint_child_sign = get_hint_pep_sign_or_none(hint_child)

                        # If this child hint is itself a child union nested in
                        # this parent union, explicitly flatten this nested
                        # union by appending *ALL* child child hints
                        # subscripting this child union onto this parent union.
                        #
                        # Note that this edge case currently *ONLY* arises when
                        # this child hint has been expanded by the above call to
                        # the sanify_hint_child() function from a non-union (e.g.,
                        # "float") into a union (e.g., "float | int"). The
                        # standard PEP 484-compliant "typing.Union" factory
                        # already implicitly flattens nested unions: e.g.,
                        #     >>> from typing import Union
                        #     >>> Union[float, Union[int, str]]
                        #     typing.Union[float, int, str]
                        if hint_child_sign in HINT_SIGNS_UNION:
                            # Tuple of all child child type hints subscripting
                            # this child union.
                            hint_child_childs = get_hint_pep_args(hint_child)
                            # print(f'Expanding union {repr(hint_curr)} with child union {repr(hint_child_childs)}...')

                            # Append these child child type hints to this parent
                            # union.
                            hint_childs_new.extend(hint_child_childs)
                        # Else, this child hint is *NOT* itself a union. In this
                        # case, append this child hint to this parent union.
                        else:
                            hint_childs_new.append(hint_child)

                        # Increment the 0-based index of the currently iterated
                        # child hint.
                        hint_childs_index += 1

                    # Freeze this temporary list back to this permanent tuple,
                    # replacing the prior unflattened contents of this tuple.
                    hint_childs = tuple(hint_childs_new)

                    # Release this list back to its respective pool.
                    release_object_typed(hint_childs_new)
                    # print(f'Flattened union to {repr(hint_childs)}...')

                    # For efficiency, reuse previously created sets of the
                    # following (when available):
                    # * "hint_childs_nonpep", the set of all PEP-noncompliant
                    #   child hints subscripting this union.
                    # * "hint_childs_pep", the set of all PEP-compliant child
                    #   hints subscripting this union.
                    #
                    # Since these child hints require fundamentally different
                    # forms of type-checking, prefiltering child hints into
                    # these sets *BEFORE* generating code type-checking these
                    # child hints improves both efficiency and maintainability.
                    hint_childs_nonpep = acquire_object_typed(set)
                    hint_childs_pep = acquire_object_typed(set)

                    # Clear these sets prior to use below.
                    hint_childs_nonpep.clear()
                    hint_childs_pep.clear()

                    # For each subscripted argument of this union...
                    for hint_child in hint_childs:
                        #FIXME: Uncomment as desired for debugging. This test is
                        #currently a bit too costly to warrant uncommenting.
                        # Assert that this child hint is *NOT* shallowly ignorable.
                        # Why? Because any union containing one or more shallowly
                        # ignorable child hints is deeply ignorable and should thus
                        # have already been ignored after a call to the
                        # is_hint_ignorable() tester passed this union on handling
                        # the parent hint of this union.
                        # assert (
                        #     repr(hint_curr) not in HINTS_REPR_IGNORABLE_SHALLOW), (
                        #     f'{hint_curr_exception_prefix} {repr(hint_curr)} child '
                        #     f'{repr(hint_child)} ignorable but not ignored.')

                        # If this child hint is PEP-compliant...
                        if is_hint_pep(hint_child):
                            # Filter this child hint into the set of
                            # PEP-compliant child hints.
                            #
                            # Note that this PEP-compliant child hint *CANNOT*
                            # also be filtered into the set of PEP-noncompliant
                            # child hints, even if this child hint originates
                            # from a non-"typing" type (e.g., "List[int]" from
                            # "list"). Why? Because that would then induce
                            # false positives when the current pith shallowly
                            # satisfies this non-"typing" type but does *NOT*
                            # deeply satisfy this child hint.
                            hint_childs_pep.add(hint_child)
                        # Else, this child hint is PEP-noncompliant. In this
                        # case, filter this child hint into the list of
                        # PEP-noncompliant arguments.
                        else:
                            hint_childs_nonpep.add(hint_child)

                    # Initialize the code type-checking the current pith against
                    # these arguments to the substring prefixing all such code.
                    func_curr_code = CODE_PEP484604_UNION_PREFIX

                    # If this union is subscripted by one or more
                    # PEP-noncompliant child hints, generate and append
                    # efficient code type-checking these child hints *BEFORE*
                    # less efficient code type-checking any PEP-compliant child
                    # hints subscripting this union.
                    if hint_childs_nonpep:
                        func_curr_code += (
                            CODE_PEP484604_UNION_CHILD_NONPEP_format(
                                # Python expression yielding the value of the
                                # current pith. Specifically...
                                pith_curr_expr=(
                                    # If this union is also subscripted by one
                                    # or more PEP-compliant child hints, prefer
                                    # the expression assigning this value to a
                                    # local variable efficiently reused by
                                    # subsequent code generated for those
                                    # PEP-compliant child hints.
                                    pith_curr_assign_expr
                                    if hint_childs_pep else
                                    # Else, this union is subscripted by *NO*
                                    # PEP-compliant child hints. Since this is
                                    # the first and only test generated for this
                                    # union, prefer the expression yielding the
                                    # value of the current pith *WITHOUT*
                                    # assigning this value to a local variable,
                                    # which would needlessly go unused.
                                    pith_curr_expr
                                ),
                                # Python expression evaluating to a tuple of
                                # these arguments.
                                #
                                # Note that we would ideally avoid coercing this
                                # set into a tuple when this set only contains
                                # one type by passing that type directly to the
                                # _add_func_wrapper_local_type() function.
                                # Sadly, the "set" class defines no convenient
                                # or efficient means of retrieving the only item
                                # of a 1-set. Indeed, the most efficient means
                                # of doing so is to iterate over that set and
                                # immediately halt iteration:
                                #     for first_item in muh_set: break
                                #
                                # While we *COULD* technically leverage that
                                # approach here, doing so would also mandate
                                # adding multiple intermediate tests, mitigating
                                # any performance gains. Ultimately, we avoid
                                # doing so by falling back to the usual
                                # approach. See also this relevant
                                # self-StackOverflow post:
                                #       https://stackoverflow.com/a/40054478/2809027
                                hint_curr_expr=add_func_scope_types(
                                    types=hint_childs_nonpep,
                                    func_scope=func_wrapper_scope,
                                    exception_prefix=(
                                        EXCEPTION_PREFIX_FUNC_WRAPPER_LOCAL),
                                ),
                            ))

                    # For the 0-based index and each child hint of this union...
                    for hint_child_index, hint_child in enumerate(
                        hint_childs_pep):
                        # Code deeply type-checking this child hint.
                        func_curr_code += CODE_PEP484604_UNION_CHILD_PEP_format(
                            # Expression yielding the value of this pith.
                            hint_child_placeholder=_enqueue_hint_child(
                                # If either...
                                #
                                # Then prefer the expression efficiently reusing
                                # the value previously assigned to a local
                                # variable by either the above conditional or
                                # prior iteration of the current conditional.
                                pith_curr_var_name
                                if (
                                    # This union is also subscripted by one or
                                    # more PEP-noncompliant child hints *OR*...
                                    hint_childs_nonpep or
                                    # This is any PEP-compliant child hint
                                    # *EXCEPT* the first...
                                    hint_child_index
                                ) else
                                # Then this union is not subscripted by any
                                # PEP-noncompliant child hints *AND* this is the
                                # first PEP-compliant child hint. In this case,
                                # preface this code with an expression assigning
                                # this value to a local variable efficiently
                                # reused by code generated by subsequent
                                # iteration.
                                #
                                # Note this child hint is guaranteed to be
                                # followed by at least one more child hint. Why?
                                # Because the "typing" module forces unions to
                                # be subscripted by two or more child hints. By
                                # deduction, those child hints *MUST* be
                                # PEP-compliant. Ergo, we need *NOT* explicitly
                                # validate that constraint here.
                                pith_curr_assign_expr
                            ))

                    # If this code is *NOT* its initial value, this union is
                    # subscripted by one or more unignorable child hints and
                    # the above logic generated code type-checking these child
                    # hints. In this case...
                    if func_curr_code is not CODE_PEP484604_UNION_PREFIX:
                        # Munge this code to...
                        func_curr_code = (
                            # Strip the erroneous " or" suffix appended by the
                            # last child hint from this code.
                            f'{func_curr_code[:LINE_RSTRIP_INDEX_OR]}'
                            # Suffix this code by the substring suffixing all
                            # such code.
                            f'{CODE_PEP484604_UNION_SUFFIX}'
                        # Format the "indent_curr" prefix into this code,
                        # deferred above for efficiency.
                        ).format(indent_curr=indent_curr)
                    # Else, this snippet is its initial value and thus
                    # ignorable.

                    # Release this pair of sets back to their respective pools.
                    release_object_typed(hint_childs_nonpep)
                    release_object_typed(hint_childs_pep)
                # Else, this hint is *NOT* a union.
                #
                # ..........{ SEQUENCES ~ variadic                 }............
                # If this hint is either...
                elif (
                    # A standard sequence (e.g., "typing.List[int]") *OR*...
                    hint_curr_sign in HINT_SIGNS_SEQUENCE_ARGS_1 or (
                        # A tuple *AND*...
                        hint_curr_sign is HintSignTuple and
                        # This tuple is subscripted by exactly two child hints
                        # *AND*...
                        hint_childs_len == 2 and
                        # The second child hint is just an unquoted ellipsis...
                        hint_childs[1] is Ellipsis
                    )
                    # Then this hint is of the form "Tuple[{typename}, ...]",
                    # typing a tuple accepting a variadic number of items all
                    # satisfying the "{typename}" child hint. Since this case
                    # is semantically equivalent to that of standard sequences,
                    # we transparently handle both here for maintainability.
                    #
                    # See below for logic handling fixed-length tuples.
                # Then this hint is either a single-argument sequence *OR* a
                # similar hint semantically resembling a single-argument
                # sequence subscripted by one argument and one or more
                # ignorable arguments. In this case...
                ):
                    # Python expression evaluating to the origin type of this
                    # sequence hint.
                    hint_curr_expr = add_func_scope_type(
                        # Origin type of this sequence hint.
                        cls=get_hint_pep_origin_type_isinstanceable(hint_curr),
                        func_scope=func_wrapper_scope,
                        exception_prefix=EXCEPTION_PREFIX_FUNC_WRAPPER_LOCAL,
                    )

                    # print(f'Sequence type hint {hint_curr} origin type scoped: {hint_curr_expr}')

                    # Possibly ignorable insane child hint subscripting this
                    # sequence hint, defined as either...
                    hint_child = (
                        # If this hint is a variadic tuple, the parent "if"
                        # statement above has already validated the contents of
                        # this tuple. In this case, efficiently get the lone
                        # child hint of this parent hint *WITHOUT* validation.
                        hint_childs[0]
                        if hint_curr_sign is HintSignTuple else
                        # Else, this hint is a single-argument sequence, in
                        # which case the contents of this sequence have yet to
                        # be validated. In this case, inefficiently get the lone
                        # child hint of this parent hint *WITH* validation.
                        get_hint_pep484585_args(
                            hint=hint_curr,
                            args_len=1,
                            exception_prefix=EXCEPTION_PREFIX,
                        )
                    )

                    # Unignorable sane child hint sanified from this possibly
                    # ignorable insane child hint *OR* "None" otherwise (i.e.,
                    # if this child hint is ignorable).
                    hint_child = sanify_hint_child_if_unignorable_or_none(
                        hint=hint_child,
                        conf=conf,
                        cls_stack=cls_stack,
                        exception_prefix=EXCEPTION_PREFIX,
                    )

                    # If this child hint is unignorable, deeply type-check both
                    # the type of the current pith *AND* a randomly indexed item
                    # of this pith. Specifically...
                    if hint_child is not None:
                        # Record that a pseudo-random integer is now required.
                        is_var_random_int_needed = True

                        # Code type-checking this pith against this type.
                        func_curr_code = CODE_PEP484585_SEQUENCE_ARGS_1_format(
                            indent_curr=indent_curr,
                            pith_curr_assign_expr=pith_curr_assign_expr,
                            pith_curr_var_name=pith_curr_var_name,
                            hint_curr_expr=hint_curr_expr,
                            hint_child_placeholder=_enqueue_hint_child(
                                # Python expression yielding the value of a
                                # randomly indexed item of the current pith
                                # (i.e., standard sequence) to be
                                # type-checked against this child hint.
                                CODE_PEP484585_SEQUENCE_ARGS_1_PITH_CHILD_EXPR_format(
                                    pith_curr_var_name=pith_curr_var_name)),
                        )
                    # Else, this child hint is ignorable. In this case, fallback
                    # to trivial code shallowly type-checking this pith as an
                    # instance of this origin type.
                    else:
                        func_curr_code = CODE_PEP484_INSTANCE_format(
                            pith_curr_expr=pith_curr_expr,
                            hint_curr_expr=hint_curr_expr,
                        )
                # Else, this hint is neither a standard sequence *NOR* variadic
                # tuple.
                #
                # ............{ SEQUENCES ~ tuple : fixed          }............
                # If this hint is a tuple, this tuple is *NOT* of the variadic
                # form and *MUST* thus be of the fixed-length form.
                #
                # Note that if this hint is a:
                # * PEP 484-compliant "typing.Tuple"-based hint, this hint is
                #   guaranteed to contain one or more child hints. Moreover, if
                #   this hint contains exactly one child hint that is the empty
                #   tuple, this hint is the empty fixed-length form
                #   "typing.Tuple[()]".
                # * PEP 585-compliant "tuple"-based hint, this hint is *NOT*
                #   guaranteed to contain one or more child hints. If this hint
                #   contains *NO* child hints, this hint is equivalent to the
                #   empty fixed-length PEP 484-compliant form
                #   "typing.Tuple[()]". Yes, PEP 585 even managed to violate
                #   PEP 484-compliance. UUUURGH!
                #
                # While tuples are sequences, the "typing.Tuple" singleton that
                # types tuples violates the syntactic norms established for
                # other standard sequences by concurrently supporting two
                # different syntaxes with equally different semantics:
                # * "typing.Tuple[{typename}, ...]", typing a tuple whose items
                #   all satisfy the "{typename}" child hint. Note that the
                #   "..." substring here is a literal ellipses.
                # * "typing.Tuple[{typename1}, {typename2}, ..., {typenameN}]",
                #   typing a tuple whose:
                #   * First item satisfies the "{typename1}" child hint.
                #   * Second item satisfies the "{typename2}" child hint.
                #   * Last item satisfies the "{typenameN}" child hint.
                #   Note that the "..." substring here is *NOT* a literal
                #   ellipses.
                #
                # This is what happens when unreadable APIs are promoted.
                elif hint_curr_sign is HintSignTuple:
                    # Assert this tuple is *NOT* of the syntactic form
                    # "typing.Tuple[{typename}, ...]" handled by prior logic.
                    assert (
                        hint_childs_len <= 1 or
                        hint_childs[1] is not Ellipsis
                    ), (f'{EXCEPTION_PREFIX}variadic tuple type hint '
                        f'{repr(hint_curr)} unhandled.')

                    # Initialize the code type-checking this pith against this
                    # tuple to the substring prefixing all such code.
                    func_curr_code = CODE_PEP484585_TUPLE_FIXED_PREFIX

                    # If this hint is the empty fixed-length tuple, generate
                    # and append code type-checking the current pith to be the
                    # empty tuple. This edge case constitutes a code smell.
                    if is_hint_pep484585_tuple_empty(hint_curr):
                        func_curr_code += (
                            CODE_PEP484585_TUPLE_FIXED_EMPTY_format(
                                pith_curr_var_name=pith_curr_var_name))
                    # Else, that ridiculous edge case does *NOT* apply. In this
                    # case...
                    else:
                        # Append code type-checking the length of this pith.
                        func_curr_code += (
                            CODE_PEP484585_TUPLE_FIXED_LEN_format(
                                pith_curr_var_name=pith_curr_var_name,
                                hint_childs_len=hint_childs_len,
                            ))

                        # For each possibly ignorable insane child hint of this
                        # parent tuple...
                        for hint_child_index, hint_child in enumerate(
                            hint_childs):
                            # Unignorable sane child hint sanified from this
                            # possibly ignorable insane child hint *OR* "None"
                            # otherwise (i.e., if this child hint is ignorable).
                            hint_child = (
                                sanify_hint_child_if_unignorable_or_none(
                                    hint=hint_child,
                                    conf=conf,
                                    cls_stack=cls_stack,
                                    exception_prefix=EXCEPTION_PREFIX,
                                ))

                            # If this child hint is unignorable, deeply
                            # type-check this child pith.
                            if hint_child is not None:
                                func_curr_code += CODE_PEP484585_TUPLE_FIXED_NONEMPTY_CHILD_format(
                                    hint_child_placeholder=_enqueue_hint_child(
                                        # Python expression yielding the value
                                        # of the currently indexed item of this
                                        # tuple to be type-checked against this
                                        # child hint.
                                        CODE_PEP484585_TUPLE_FIXED_NONEMPTY_PITH_CHILD_EXPR_format(
                                            pith_curr_var_name=pith_curr_var_name,
                                            pith_child_index=hint_child_index,
                                        )
                                    ),
                                )
                            # Else, this child hint is ignorable.

                    # Munge this code to...
                    func_curr_code = (
                        # Strip the erroneous " and" suffix appended by the
                        # last child hint from this code.
                        f'{func_curr_code[:LINE_RSTRIP_INDEX_AND]}'
                        # Suffix this code by the substring suffixing all such
                        # code.
                        f'{CODE_PEP484585_TUPLE_FIXED_SUFFIX}'
                    # Format...
                    ).format(
                        indent_curr=indent_curr,
                        pith_curr_assign_expr=pith_curr_assign_expr,
                    )
                # Else, this hint is *NOT* a tuple.
                #
                # ..........{ MAPPINGS                             }............
                # If this hint is a standard mapping (e.g., "dict[str, int]")...
                elif hint_curr_sign in HINT_SIGNS_MAPPING:
                    # Python expression evaluating to the origin type of this
                    # mapping hint.
                    hint_curr_expr = add_func_scope_type(
                        # Origin type of this sequence.
                        cls=get_hint_pep_origin_type_isinstanceable(hint_curr),
                        func_scope=func_wrapper_scope,
                        exception_prefix=EXCEPTION_PREFIX_FUNC_WRAPPER_LOCAL,
                    )

                    # 2-tuple of the possibly ignorable insane child key and
                    # value hints subscripting this mapping hint.
                    hint_childs = get_hint_pep484585_args(  # type: ignore[assignment]
                        hint=hint_curr,
                        args_len=2,
                        exception_prefix=EXCEPTION_PREFIX,
                    )

                    #FIXME: Consider also contextually considering child key
                    #hints that reduce to "Hashable" to be ignorable. This
                    #includes complex type hints like "Union[Hashable, str]",
                    #which reduces to "Hashable". We can't particularly be
                    #bothered at the moment. This is a microoptimization and
                    #will probably require a non-trivial amount of work. *sigh*
                    # Unignorable sane child key and value hints sanified from
                    # these possibly ignorable insane child key and value hints
                    # *OR* "None" otherwise (i.e., if ignorable).
                    hint_child_key = sanify_hint_child_if_unignorable_or_none(
                        hint=hint_childs[0],
                        conf=conf,
                        cls_stack=cls_stack,
                        exception_prefix=EXCEPTION_PREFIX,
                    )
                    hint_child_value = sanify_hint_child_if_unignorable_or_none(
                        hint=hint_childs[1],  # type: ignore[has-type]
                        conf=conf,
                        cls_stack=cls_stack,
                        exception_prefix=EXCEPTION_PREFIX,
                    )

                    # If at least one of these child hints are unignorable...
                    if hint_child_key or hint_child_value:
                        # If this child key hint is unignorable...
                        if hint_child_key:
                            # If this child value hint is also unignorable...
                            if hint_child_value:
                                # Increase the indentation level of code
                                # type-checking this child value pith.
                                indent_level_child += 1

                                # Increment the integer suffixing the name of a
                                # unique local variable storing the value of
                                # this child key pith *BEFORE* defining this
                                # variable.
                                pith_curr_var_name_index += 1

                                # Name of this local variable.
                                pith_curr_key_var_name = PITH_INDEX_TO_VAR_NAME[
                                    pith_curr_var_name_index]

                                # Expose this hint to the subsequent call to the
                                # _enqueue_hint_child() closure.
                                hint_child = hint_child_key

                                # Placeholder string to be subsequently replaced
                                # by code type-checking this child key pith
                                # against this hint.
                                hint_key_placeholder = _enqueue_hint_child(
                                    pith_curr_key_var_name)

                                # Expose this hint to the subsequent call to the
                                # _enqueue_hint_child() closure.
                                hint_child = hint_child_value

                                # Placeholder string to be subsequently replaced
                                # by code type-checking this child value pith
                                # against this hint.
                                hint_value_placeholder = _enqueue_hint_child(
                                    CODE_PEP484585_MAPPING_KEY_VALUE_PITH_CHILD_EXPR_format(
                                        pith_curr_var_name=pith_curr_var_name,
                                        pith_curr_key_var_name=pith_curr_key_var_name,
                                    ))

                                # Code deeply type-checking these child key and
                                # value piths against these hints.
                                func_curr_code_key_value = (
                                    CODE_PEP484585_MAPPING_KEY_VALUE_format(
                                        indent_curr=indent_curr,
                                        pith_curr_key_var_name=(  # pyright: ignore
                                            pith_curr_key_var_name),
                                        pith_curr_var_name=pith_curr_var_name,
                                        hint_key_placeholder=(
                                            hint_key_placeholder),
                                        hint_value_placeholder=(
                                            hint_value_placeholder),
                                    ))
                            # Else, this child value hint is ignorable. In this
                            # case...
                            else:
                                # Expose this child key hint to the subsequent
                                # call to the _enqueue_hint_child() closure.
                                hint_child = hint_child_key

                                # Code deeply type-checking only this child key
                                # pith against this hint.
                                func_curr_code_key_value = (
                                    CODE_PEP484585_MAPPING_KEY_ONLY_format(
                                        indent_curr=indent_curr,
                                        # Placeholder string to be subsequently
                                        # replaced by code type-checking this
                                        # child key pith against this hint.
                                        hint_key_placeholder=_enqueue_hint_child(
                                            CODE_PEP484585_MAPPING_KEY_ONLY_PITH_CHILD_EXPR_format(
                                                pith_curr_var_name=(
                                                    pith_curr_var_name))),
                                    ))
                        # Else, this child key hint is ignorable. By process
                        # of elimination, this child value hint *MUST* be
                        # unignorable. In this case...
                        else:
                            # Expose this child value hint to the subsequent
                            # call to the _enqueue_hint_child() closure.
                            hint_child = hint_child_value

                            # Code deeply type-checking only this child value
                            # pith against this hint.
                            func_curr_code_key_value = (
                                CODE_PEP484585_MAPPING_VALUE_ONLY_format(
                                    indent_curr=indent_curr,
                                    # Placeholder string to be subsequently
                                    # replaced by code type-checking this
                                    # child value pith against this hint.
                                    hint_value_placeholder=_enqueue_hint_child(
                                        CODE_PEP484585_MAPPING_VALUE_ONLY_PITH_CHILD_EXPR_format(
                                            pith_curr_var_name=(
                                                pith_curr_var_name))),
                                ))

                        # Code deeply type-checking this pith as well as at
                        # least one of these child key and value piths.
                        func_curr_code = CODE_PEP484585_MAPPING_format(
                            indent_curr=indent_curr,
                            pith_curr_assign_expr=pith_curr_assign_expr,
                            pith_curr_var_name=pith_curr_var_name,
                            hint_curr_expr=hint_curr_expr,
                            func_curr_code_key_value=func_curr_code_key_value,
                        )
                    # Else, these child key *AND* value hints are both
                    # ignorable. In this case, fallback to trivial code
                    # shallowly type-checking this pith as an instance of this
                    # origin type.
                    else:
                        func_curr_code = CODE_PEP484_INSTANCE_format(
                            pith_curr_expr=pith_curr_expr,
                            hint_curr_expr=hint_curr_expr,
                        )
                # Else, this hint is *NOT* a mapping.
                #
                # ............{ ANNOTATED                          }............
                # If this hint is a PEP 593-compliant type metahint, this
                # metahint is guaranteed by the reduction performed above to be
                # beartype-specific (i.e., metahint whose second argument is a
                # beartype validator produced by subscripting a beartype
                # validator factory). In this case...
                elif hint_curr_sign is HintSignAnnotated:
                    # Defer heavyweight imports.
                    from beartype.vale._core._valecore import BeartypeValidator

                    # Initialize the code type-checking this pith against this
                    # metahint to the substring prefixing all such code.
                    func_curr_code = CODE_PEP593_VALIDATOR_PREFIX

                    # Unignorable sane metahint annotating this parent hint
                    # sanified from this possibly ignorable insane metahint *OR*
                    # "None" otherwise (i.e., if this metahint is ignorable).
                    hint_child = sanify_hint_child_if_unignorable_or_none(
                        hint=get_hint_pep593_metahint(hint_curr),
                        conf=conf,
                        cls_stack=cls_stack,
                        exception_prefix=EXCEPTION_PREFIX,
                    )

                    # Python expression yielding the value of the current pith,
                    # defaulting to the name of the local variable assigned to
                    # by the assignment expression performed below.
                    hint_curr_expr = pith_curr_var_name

                    # Tuple of the one or more beartype validators annotating
                    # this metahint.
                    hints_child = get_hint_pep593_metadata(hint_curr)
                    # print(f'hints_child: {repr(hints_child)}')

                    # If this metahint is ignorable...
                    if hint_child is None:
                        # If this metahint is annotated by only one beartype
                        # validator, the most efficient expression yielding the
                        # value of the current pith is simply the full Python
                        # expression *WITHOUT* assigning that value to a
                        # reusable local variable in an assignment expression.
                        # *NO* assignment expression is needed in this case.
                        #
                        # Why? Because beartype validators are *NEVER* recursed
                        # into. Each beartype validator is guaranteed to be the
                        # leaf of a type-checking subtree, guaranteeing this
                        # pith to be evaluated only once.
                        if len(hints_child) == 1:
                            hint_curr_expr = pith_curr_expr
                        # Else, this metahint is annotated by two or more
                        # beartype validators. In this case, the most efficient
                        # expression yielding the value of the current pith is
                        # the assignment expression assigning this value to a
                        # reusable local variable.
                        else:
                            hint_curr_expr = pith_curr_assign_expr
                    # Else, this metahint is unignorable. In this case...
                    else:
                        # Code deeply type-checking this metahint.
                        func_curr_code += CODE_PEP593_VALIDATOR_METAHINT_format(
                            indent_curr=indent_curr,
                            # Python expression yielding the value of the
                            # current pith assigned to a local variable
                            # efficiently reused by code generated by the
                            # following iteration.
                            #
                            # Note this child hint is guaranteed to be followed
                            # by at least one more test expression referencing
                            # this local variable. Why? Because the "typing"
                            # module forces metahints to be subscripted by one
                            # child hint and one or more arbitrary objects.
                            # Ergo, we need *NOT* explicitly validate that here.
                            hint_child_placeholder=_enqueue_hint_child(
                                pith_curr_assign_expr),
                        )
                    # Else, this metahint is ignorable.

                    # For the 0-based index and each beartype validator
                    # annotating this metahint...
                    for hint_child_index, hint_child in enumerate(hints_child):
                        # print(f'Type-checking PEP 593 type hint {repr(hint_curr)} argument {repr(hint_child)}...')
                        # If this is *NOT* a beartype validator, raise an
                        # exception.
                        #
                        # Note that the previously called sanify_hint_child()
                        # function validated only the first such to be a
                        # beartype validator. All remaining arguments have yet
                        # to be validated, so we do so now for consistency and
                        # safety.
                        if not isinstance(hint_child, BeartypeValidator):
                            raise BeartypeDecorHintPep593Exception(
                                f'{EXCEPTION_PREFIX}PEP 593 type hint '
                                f'{repr(hint_curr)} subscripted by both '
                                f'@beartype-specific and -agnostic metadata '
                                f'(i.e., {represent_object(hint_child)} not '
                                f'beartype validator).'
                            )
                        # Else, this argument is beartype-specific.
                        #
                        # If this is any beartype validator *EXCEPT* the first,
                        # set the Python expression yielding the value of the
                        # current pith to the name of the local variable
                        # assigned to by the prior assignment expression. By
                        # deduction, it *MUST* be the case now that either:
                        # * This metahint was unignorable, in which case this
                        #   assignment uselessly reduplicates the exact same
                        #   assignment performed above. While non-ideal, this
                        #   assignment is sufficiently efficient to make any
                        #   optimizations here effectively worthless.
                        # * This metahint was ignorable, in which case this
                        #   expression was set above to the assignment
                        #   expression assigning this pith for the first
                        #   beartype validator. Since this iteration has already
                        #   processed the first beartype validator, this
                        #   assignment expression has already been performed.
                        #   Avoid inefficiently re-performing this assignment
                        #   expression for each additional beartype validator by
                        #   efficiently reusing the previously assigned local.
                        elif hint_child_index:
                            hint_curr_expr = pith_curr_var_name
                        # Else, this is the first beartype validator. See above.

                        # Code deeply type-checking this validator.
                        func_curr_code += CODE_PEP593_VALIDATOR_IS_format(
                            indent_curr=indent_curr,
                            # Python expression formatting the current pith into
                            # the "{obj}" format substring previously embedded
                            # by this validator into this code string.
                            hint_child_expr=hint_child._is_valid_code.format(
                                # Indentation unique to this child hint.
                                indent=INDENT_LEVEL_TO_CODE[indent_level_child],
                                obj=hint_curr_expr,
                            ),
                        )

                        # Generate locals safely merging the locals required by
                        # both this validator code *AND* the current code
                        # type-checking this entire root hint.
                        update_mapping(
                            mapping_trg=func_wrapper_scope,
                            mapping_src=hint_child._is_valid_code_locals,
                        )

                    # Munge this code to...
                    func_curr_code = (
                        # Strip the erroneous " and" suffix appended by the
                        # last child hint from this code.
                        f'{func_curr_code[:LINE_RSTRIP_INDEX_AND]}'
                        # Suffix this code by the substring suffixing all such
                        # code.
                        f'{CODE_PEP593_VALIDATOR_SUFFIX_format(indent_curr=indent_curr)}'
                    )
                # Else, this hint is *NOT* a metahint.
                #
                # ............{ SUBCLASS                           }............
                # If this hint is either a PEP 484- or 585-compliant subclass
                # type hint...
                elif hint_curr_sign is HintSignType:
                    #FIXME: Optimization: if the superclass is an ignorable
                    #class (e.g., "object", "Protocol"), this type hint is
                    #ignorable (e.g., "Type[object]", "type[Protocol]"). We'll
                    #thus want to:
                    #* Add that detection logic to one or more
                    #  is_hint_*_ignorable() testers elsewhere.
                    #* Call is_hint_ignorable() below.
                    #* Unit test such type hints to indeed be ignorable.

                    # Superclass this pith is required to be a subclass of.
                    hint_child = get_hint_pep484585_type_superclass(
                        hint=hint_curr,
                        exception_prefix=EXCEPTION_PREFIX,
                    )

                    # If this superclass is either a class *OR* tuple of
                    # classes...
                    if isinstance(hint_child, TestableTypes):
                        # Python expression evaluating to this superclass.
                        hint_curr_expr = add_func_scope_type_or_types(
                            type_or_types=hint_child,  # type: ignore[arg-type]
                            func_scope=func_wrapper_scope,
                            exception_prefix=(
                                EXCEPTION_PREFIX_FUNC_WRAPPER_LOCAL),
                        )
                    # Else, this superclass is *NOT* actually a class. By
                    # process of elimination and the validation already
                    # performed above by the
                    # get_hint_pep484585_type_superclass() getter, this
                    # superclass *MUST* be a forward reference to a class.
                    else:
                        # Render this forward reference accessible to the body
                        # of this wrapper function. See above for commentary.
                        hint_curr_expr, hint_refs_type_basename = (
                            express_func_scope_type_ref(
                                forwardref=hint_child,  # type: ignore[arg-type]
                                forwardrefs_class_basename=(
                                    hint_refs_type_basename),
                                func_scope=func_wrapper_scope,
                                exception_prefix=EXCEPTION_PREFIX,
                            ))

                    # Code type-checking this pith against this superclass.
                    func_curr_code = CODE_PEP484585_SUBCLASS_format(
                        pith_curr_assign_expr=pith_curr_assign_expr,
                        pith_curr_var_name=pith_curr_var_name,
                        hint_curr_expr=hint_curr_expr,
                        indent_curr=indent_curr,
                    )
                # Else, this hint is neither a PEP 484- nor 585-compliant
                # subclass type hint.
                #
                # ............{ GENERIC or PROTOCOL                }............
                # If this hint is either a:
                # * PEP 484-compliant generic (i.e., user-defined class
                #   subclassing a combination of one or more of the
                #   "typing.Generic" superclass and other "typing" non-class
                #   pseudo-superclasses) *OR*...
                # * PEP 544-compliant protocol (i.e., class subclassing a
                #   combination of one or more of the "typing.Protocol"
                #   superclass and other "typing" non-class
                #   pseudo-superclasses) *OR*...
                # * PEP 585-compliant generic (i.e., user-defined class
                #   subclassing at least one non-class PEP 585-compliant
                #   pseudo-superclasses) *OR*...
                #
                # ...then this hint is a PEP-compliant generic. In this case...
                elif hint_curr_sign is HintSignGeneric:
                    #FIXME: *THIS IS NON-IDEAL.* Ideally, we should propagate
                    #*ALL* child type hints subscripting a generic up to *ALL*
                    #pseudo-superclasses of that generic (e.g., the "int" child
                    #hint subscripting a parent hint "MuhGeneric[int]" of type
                    #"class MuhGeneric(list[T]): pass" up to its "list[T]"
                    #pseudo-superclass).
                    #
                    #For now, we just strip *ALL* child type hints subscripting
                    #a generic with the following call. This suffices, because
                    #we just need this to work. So it goes, uneasy code
                    #bedfellows.

                    # Reduce this hint to the object originating this generic
                    # (if any) by stripping all child type hints subscripting
                    # this hint from this hint. Why? Because these child type
                    # hints convey *NO* meaningful semantics and are thus safely
                    # ignorable. Consider this simple example, in which the
                    # subscription "[int]" not only conveys *NO* meaningful
                    # semantics but actually conveys paradoxically conflicting
                    # semantics contradicting the original generic declaration:
                    #     class ListOfListsOfStrs(list[list[str]]): pass
                    #     ListOfListsOfStrs[int]  # <-- *THIS MEANS NOTHING*
                    #
                    # Specifically:
                    # * If this hint is an unsubscripted generic (e.g.,
                    #   "typing.IO"), preserve this hint as is. In this case,
                    #   this hint is a standard isinstanceable class.
                    # * If this hint is a subscripted generic (e.g.,
                    #   "typing.IO[str]"), reduce this hint to the object
                    #   originating this generic (e.g., "typing.IO").
                    hint_curr = get_hint_pep484585_generic_type(
                        hint=hint_curr, exception_prefix=EXCEPTION_PREFIX)
                    # print(f'Visiting generic type {repr(hint_curr)}...')

                    # Initialize the code type-checking this pith against this
                    # generic to the substring prefixing all such code.
                    func_curr_code = CODE_PEP484585_GENERIC_PREFIX

                    # For each unignorable unerased transitive pseudo-superclass
                    # originally declared as a superclass of this generic...
                    for hint_child in (
                        iter_hint_pep484585_generic_bases_unerased_tree(
                            hint=hint_curr,
                            conf=conf,
                            exception_prefix=EXCEPTION_PREFIX,
                    )):
                        # print(f'Visiting generic type hint {repr(hint_curr)} unerased base {repr(hint_child)}...')

                        # Generate and append code type-checking this pith
                        # against this superclass.
                        func_curr_code += CODE_PEP484585_GENERIC_CHILD_format(
                            hint_child_placeholder=_enqueue_hint_child(
                                # Python expression efficiently reusing the
                                # value of this pith previously assigned to a
                                # local variable by the prior expression.
                                pith_curr_var_name))

                    # Munge this code to...
                    func_curr_code = (
                        # Strip the erroneous " and" suffix appended by the
                        # last child hint from this code.
                        f'{func_curr_code[:LINE_RSTRIP_INDEX_AND]}'
                        # Suffix this code by the substring suffixing all such
                        # code.
                        f'{CODE_PEP484585_GENERIC_SUFFIX}'
                    # Format...
                    ).format(
                        # Indentation deferred above for efficiency.
                        indent_curr=indent_curr,
                        pith_curr_assign_expr=pith_curr_assign_expr,
                        # Python expression evaluating to this generic type.
                        hint_curr_expr=add_func_scope_type(
                            cls=hint_curr,
                            func_scope=func_wrapper_scope,
                            exception_prefix=(
                                EXCEPTION_PREFIX_FUNC_WRAPPER_LOCAL),
                        ),
                    )
                    # print(f'{hint_curr_exception_prefix} PEP generic {repr(hint)} handled.')
                # Else, this hint is *NOT* a generic.
                #
                # ............{ LITERAL                            }............
                # If this hint is a PEP 586-compliant type hint (i.e., the
                # "typing.Literal" singleton subscripted by one or more literal
                # objects), this hint is largely useless and thus intentionally
                # detected last. Why? Because "typing.Literal" is subscriptable
                # by objects that are instances of only *SIX* possible types,
                # which is sufficiently limiting as to render this singleton
                # patently absurd and a farce that we weep to even implement.
                # In this case...
                elif hint_curr_sign is HintSignLiteral:
                    # Tuple of zero or more literal objects subscripting this
                    # hint, intentionally replacing the current such tuple due
                    # to the non-standard implementation of the third-party
                    # "typing_extensions.Literal" type hint factory.
                    hint_childs = get_hint_pep586_literals(
                        hint=hint_curr, exception_prefix=EXCEPTION_PREFIX)

                    # Initialize the code type-checking this pith against this
                    # hint to the substring prefixing all such code.
                    func_curr_code = CODE_PEP586_PREFIX_format(
                        pith_curr_assign_expr=pith_curr_assign_expr,

                        #FIXME: If "typing.Literal" is ever extended to support
                        #substantially more types (and thus actually becomes
                        #useful), optimize the construction of the "types" set
                        #below to instead leverage a similar
                        #"acquire_object_typed(set)" caching solution as that
                        #currently employed for unions. For now, we only shrug.

                        # Python expression evaluating to a tuple of the unique
                        # types of all literal objects subscripting this hint.
                        hint_child_types_expr=add_func_scope_types(
                            # Set comprehension of all unique literal objects
                            # subscripting this hint, implicitly discarding all
                            # duplicate such objects.
                            types={
                                type(hint_child)
                                for hint_child in hint_childs
                            },
                            func_scope=func_wrapper_scope,
                            exception_prefix=(
                                EXCEPTION_PREFIX_FUNC_WRAPPER_LOCAL),
                        ),
                    )

                    # For each literal object subscripting this hint...
                    for hint_child in hint_childs:
                        # Generate and append efficient code type-checking
                        # this data validator by embedding this code as is.
                        func_curr_code += CODE_PEP586_LITERAL_format(
                            pith_curr_var_name=pith_curr_var_name,
                            # Python expression evaluating to this object.
                            hint_child_expr=add_func_scope_attr(
                                attr=hint_child,
                                func_scope=func_wrapper_scope,
                                exception_prefix=(
                                    EXCEPTION_PREFIX_FUNC_WRAPPER_LOCAL),
                            ),
                        )

                    # Munge this code to...
                    func_curr_code = (
                        # Strip the erroneous " or" suffix appended by the last
                        # child hint from this code.
                        f'{func_curr_code[:LINE_RSTRIP_INDEX_OR]}'
                        # Suffix this code by the appropriate substring.
                        f'{CODE_PEP586_SUFFIX}'
                    ).format(indent_curr=indent_curr)
                # Else, this hint is *NOT* a PEP 586-compliant type hint.

                # ............{ UNSUPPORTED                        }............
                # Else, this hint is neither shallowly nor deeply supported and
                # is thus unsupported. Since an exception should have already
                # been raised above in this case, this conditional branch
                # *NEVER* be triggered. Nonetheless, raise an exception.
                else:
                    raise BeartypeDecorHintPepUnsupportedException(
                        f'{EXCEPTION_PREFIX_HINT}'
                        f'{repr(hint_curr)} unsupported but '
                        f'erroneously detected as supported with '
                        f'beartype sign {hint_curr_sign}.'
                    )

        # ................{ NON-PEP                            }................
        # Else, this hint is *NOT* PEP-compliant.
        #
        # ................{ NON-PEP ~ type                     }................
        # If this hint is a non-"typing" class...
        #
        # Note that:
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
            # Code type-checking the current pith against this type.
            func_curr_code = CODE_PEP484_INSTANCE_format(
                pith_curr_expr=pith_curr_expr,
                # Python expression evaluating to this type.
                hint_curr_expr=add_func_scope_type(
                    cls=hint_curr,
                    func_scope=func_wrapper_scope,
                    exception_prefix=EXCEPTION_PREFIX_HINT,
                ),
            )
        # ................{ NON-PEP ~ bad                      }................
        # Else, this hint is neither PEP-compliant *NOR* a class. In this case,
        # raise an exception. Note that:
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
                f'{EXCEPTION_PREFIX_HINT}{repr(hint_curr)} '
                f'not PEP-compliant.'
            )

        # ................{ CLEANUP                            }................
        # Inject this code into the body of this wrapper.
        func_wrapper_code = replace_str_substrs(
            text=func_wrapper_code,
            old=hint_curr_placeholder,
            new=func_curr_code,
        )

        # Nullify the metadata describing the previously visited hint in this
        # list for safety.
        hints_meta[hints_meta_index_curr] = None

        # Increment the 0-based index of metadata describing the next visited
        # hint in the "hints_meta" list *BEFORE* visiting that hint but *AFTER*
        # performing all other logic for the currently visited hint.
        hints_meta_index_curr += 1

    # ..................{ CLEANUP                            }..................
    # Release the fixed list of all such metadata.
    release_fixed_list(hints_meta)

    # If the Python code snippet to be returned remains unchanged from its
    # initial value, the breadth-first search above failed to generate code. In
    # this case, raise an exception.
    #
    # Note that this test is inexpensive, as the third character of the
    # "func_root_code" code snippet is guaranteed to differ from that of
    # "func_wrapper_code" code snippet if this function behaved as expected,
    # which it should have... but may not have, which is why we're testing.
    if func_wrapper_code == func_root_code:
        raise BeartypeDecorHintPepException(
            f'{EXCEPTION_PREFIX_HINT}{repr(hint_root)} unchecked.')
    # Else, the breadth-first search above successfully generated code.

    # ..................{ CODE ~ scope                       }..................
    # If type-checking for the root pith requires the type stack, pass a hidden
    # parameter to this wrapper function exposing this stack.
    if cls_stack:
        func_wrapper_scope[ARG_NAME_CLS_STACK] = cls_stack
    # Else, type-checking for the root pith requires *NO* type stack.

    # If type-checking for the root pith requires a pseudo-random integer, pass
    # a hidden parameter to this wrapper function exposing the
    # random.getrandbits() function required to generate this integer.
    if is_var_random_int_needed:
        func_wrapper_scope[ARG_NAME_GETRANDBITS] = getrandbits
    # Else, type-checking for the root pith requires *NO* pseudo-random integer.

    # ..................{ CODE ~ suffix                      }..................
    # Tuple of the unqualified classnames referred to by all relative forward
    # references visitable from this hint converted from that set to reduce
    # space consumption after memoization by @callable_cached, defined as...
    hint_refs_type_basename_tuple = (
        # If *NO* relative forward references are visitable from this root
        # hint, the empty tuple;
        ()
        if hint_refs_type_basename is None else
        # Else, that set converted into a tuple.
        tuple(hint_refs_type_basename)
    )

    # Return all metadata required by higher-level callers.
    return (
        func_wrapper_code,
        func_wrapper_scope,
        hint_refs_type_basename_tuple,
    )
