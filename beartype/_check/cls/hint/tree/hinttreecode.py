#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype **type-checking type hint tree dataclasses** (i.e., low-level
subclasses storing metadata describing the breadth-first search (BFS)
dynamically generating pure-Python code snippets type-checking arbitrary objects
against the type hints annotating those objects).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.roar import BeartypeDecorHintRecursionException
from beartype._check.cls.call.callmetaabc import BeartypeCallDataABC
from beartype._check.cls.call.callmetaexternal import (
    BEARTYPE_CALL_EXTERNAL_META)
from beartype._check.cls.hint.data.hintdatacode import HintDataCode
from beartype._check.cls.hint.hintsane import HintSane
from beartype._check.cls.hint.tree.hinttreeabc import HintTreeABC
from beartype._check.convert.convmain import sanify_hint_child
from beartype._conf.confcommon import BEARTYPE_CONF_DEFAULT
from beartype._conf.confmain import BeartypeConf
from beartype._data.check.code.datacodeindent import INDENT_LEVEL_TO_CODE
from beartype._data.check.error.dataerrmagic import EXCEPTION_PLACEHOLDER
from beartype._data.typing.datatypingport import Hint
from beartype._data.typing.datatyping import (
    HintSignOrNoneOrSentinel,
    LexicalScope,
)
from beartype._data.kind.datakindiota import SENTINEL
from beartype._metaverse import URL_ISSUES
from beartype._util.cache.pool.utilcachepoollistfixed import (
    FIXED_LIST_SIZE_MEDIUM,
    FixedList,
)
from beartype._util.hint.pep.utilpepsign import get_hint_pep_sign_or_none
from typing import (
    TYPE_CHECKING,
    Optional,
)

# ....................{ SUBCLASSES                         }....................
#FIXME: Unit test us up, please.
class HintTreeCode(HintTreeABC):
    '''
    **Type hint tree type-checking metadata** (i.e., dataclass defining a
    low-level :attr:`._hint_queue` fixed list of metadata describing all
    visitable type hints currently discovered by the breadth-first search (BFS)
    dynamically generating pure-Python type-checking code snippets in the
    :func:`beartype._check.code.codemain.make_check_expr` factory).

    This metadata defines the :attr:`._hint_queue` instance variable to be a
    list acting as a standard First-In-First-Out (FIFO) queue, enabling that BFS
    to be implemented as an efficient imperative algorithm. Without
    :attr:`._hint_queue`, that BFS would instead have to be naively implemented
    as a recursive algorithm exhibiting both inefficiency and risk (due to
    unavoidable stack exhaustion and avoidable infinite recursion).

    Design
    ------
    Most of the following instance variables are only relevant when the
    currently visited hint is *not* the root hint. If the currently visited hint
    is the root hint, the current pith has already been localized to a local
    variable whose name is the value of the :data:`VAR_NAME_PITH_ROOT` string
    global and thus need *not* be relocalized to another local variable using an
    assignment expression.

    These variables enable a non-trivial runtime optimization eliminating
    repeated computations to obtain the child pith needed to type-check child
    hints. For example, if the current hint constrains the current pith to be
    a standard sequence, the child pith of that parent pith is a random item
    selected from this sequence; since obtaining this child pith is
    non-trivial, the computation required to do so is performed only once by
    assigning this child pith to a unique local variable during type-checking
    and then repeatedly type-checking that variable rather than the logic
    required to continually reacquire this child pith: e.g.,

    .. code-block:: python

       # Type-checking conditional for "List[List[str]]" under Python < 3.8.
       if not (
           isinstance(__beartype_pith_0, list) and
           (
               isinstance(__beartype_pith_0[__beartype_random_int % len(__beartype_pith_0)], list) and
               isinstance(__beartype_pith_0[__beartype_random_int % len(__beartype_pith_0)][__beartype_random_int % len(__beartype_pith_0[__beartype_random_int % len(__beartype_pith_0)])], str) if __beartype_pith_0[__beartype_random_int % len(__beartype_pith_0)] else True
           ) if __beartype_pith_0 else True
       ):

       # The same conditional under Python >= 3.8.
       if not (
           isinstance(__beartype_pith_0, list) and
           (
               isinstance(__beartype_pith_1 := __beartype_pith_0[__beartype_random_int % len(__beartype_pith_0)], list) and
               isinstance(__beartype_pith_1[__beartype_random_int % len(__beartype_pith_1)], str) if __beartype_pith_1 else True
           ) if __beartype_pith_0 else True
       ):

    Note that:

    * The random item selected from the root pith (i.e., ``__beartype_pith_1
      := __beartype_pith_0[__beartype_random_int % len(__beartype_pith_0)``)
      only occurs once under Python >= 3.8 but repeatedly under Python < 3.8.
      In both cases, the same semantic type-checking is performed regardless
      of optimization.
    * This optimization implicitly "bottoms out" when the currently visited hint
      is *not* subscripted by unignorable child hints. If all child hints of the
      currently visited hint are either ignorable (e.g., :class:`object`,
      :obj:`typing.Any`) *or* are unignorable isinstanceable types (e.g.,
      :class:`int`, :class:`str`), the currently visited hint has *no*
      meaningful child hints and is thus effectively a leaf node with respect to
      performing this optimization.

    Attributes
    ----------
    func_curr_code : Optional[str]
        Either:

        * If the currently visited hint is deeply type-checkable, the Python
          code snippet type-checking the current pith against this hint.
        * If the currently visited hint is only shallowly type-checkable,
          :data:`None`.
    func_wrapper_locals : LexicalScope
        **Local scope** (i.e., dictionary mapping from the name to value of each
        attribute referenced in the signature) of this wrapper function required
        by this Python code snippet.
    hint_curr: HintDataCode
        Metadata describing the currently visited hint, appended by the
        previously visited parent hint to this queue.
    hint_curr_expr : Optional[str]
        Either:

        * If the currently visited hint is deeply type-checkable, :data:`None`.
        * If the currently visited hint is only shallowly type-checkable, the
          Python expression evaluating to the origin type underlying this hint
          as a hidden :mod:`beartype`-specific parameter injected into the
          signature of the current wrapper function.
    indent_curr : str
        Python code snippet expanding to the current level of indentation
        appropriate for the currently visited hint.
    indent_child : str
        Python code snippet expanding to the current level of indentation
        appropriate for the currently iterated child hint of this parent hint.
    indent_level_child : int
        1-based indentation level describing the current level of indentation
        appropriate for the currently iterated child hint of this parent hint.
    index_last : int
        0-based index of metadata describing the last visitable hint in this
        list. For efficiency, this integer also uniquely identifies the current
        child type hint of the currently visited parent type hint.
    is_check_expr_cacheable : bool
        :data:`True` only if callers may safely cache (memoize) the pure-Python
        expression dynamically generated and returned by the low-level
        :func:`beartype._check.code.codemain.make_check_expr` code factory
        *after* visiting all type hints in this queue. This high-level boolean
        effectively composes (combines) each low-level
        :attr:`beartype._check.cls.hint.hintsane.HintSane.is_check_expr_cacheable`
        boolean across *all* child hints transitively subscripting the root hint
        of this queue. See also that instance variable for further details.
    is_var_random_int_needed : bool
        :data:`True` only if one or more child hints of the root hint of this
        queue require a pseudo-random integer. If :data:`True`, the body of this
        wrapper function will be prefixed with code generating this integer.
    pith_curr_assign_expr : str
        Assignment expression assigning this full Python expression to the
        unique local variable assigned the value of this expression.
    pith_curr_var_name : str
        Name of the current pith variable (i.e., local Python variable in the
        body of the wrapper function whose value is that of the current pith).
        This name is either:

        * Initially, the name of the currently type-checked parameter or return.
        * On subsequently type-checking nested items of the parameter or return,
          the name of the local variable uniquely assigned to by the assignment
          expression defined by :attr:`pith_curr_assign_expr` (i.e., the
          left-hand side (LHS) of that assignment expression).
    _hint_queue : FixedList
        **Type hint tree type-checking queue** (i.e., First-In-First-Out (FIFO)
        queue of :class:`.HintDataCode` objects describing all visitable type hints
        currently discovered by the breadth-first search (BFS) dynamically
        generating pure-Python type-checking code snippets in the
        :func:`beartype._check.code.codemain.make_check_expr` factory).
    '''

    # ..................{ CLASS VARIABLES                    }..................
    # Slot all instance variables defined on this object to minimize the time
    # complexity of both reading and writing variables across frequently
    # called @beartype decorations. Slotting has been shown to reduce read and
    # write costs by approximately ~10%, which is non-trivial.
    __slots__ = (
        'func_curr_code',
        'func_wrapper_locals',
        'hint_curr_expr',
        'indent_child',
        'indent_curr',
        'indent_level_child',
        'index_last',
        'is_check_expr_cacheable',
        'is_var_random_int_needed',
        'pith_curr_assign_expr',
        'pith_curr_var_name',
        '_hint_queue',
    )

    # Squelch false negatives from mypy. This is absurd. This is mypy. See:
    #     https://github.com/python/mypy/issues/5941
    if TYPE_CHECKING:
        func_curr_code: str
        func_wrapper_locals: LexicalScope
        hint_curr : HintDataCode
        hint_curr_expr : Optional[str]
        indent_curr: str
        indent_child: str
        indent_level_child: int
        index_last: int
        is_check_expr_cacheable: bool
        is_var_random_int_needed: bool
        pith_curr_assign_expr: str
        pith_curr_var_name: str
        _hint_queue : FixedList

    # ..................{ INITIALIZERS                       }..................
    def __init__(self) -> None:
        '''
        Initialize this type-checking metadata queue.
        '''

        # Initialize our superclass with defaults that technically satisfy the
        # superclass API but ultimately do little to nothing, as the deinit()
        # method called below overrides most of these with other defaults. UGH!
        super().__init__(
            exception_prefix=EXCEPTION_PLACEHOLDER,
            call_curr=BEARTYPE_CALL_EXTERNAL_META,
            conf=BEARTYPE_CONF_DEFAULT,
        )

        # Classify all instance variables that currently *NEVER* change across
        # all reinitializations of this queue.
        self._hint_queue = FixedList(size=FIXED_LIST_SIZE_MEDIUM)

        # Nullify all remaining instance variables for safety.
        self.deinit()


    def deinit(self) -> None:
        '''
        Deinitialize this type-checking metadata queue.
        '''

        # Nullify all instance variables for safety.
        self.call_curr = (  # type: ignore[assignment]
        self.conf) = (  # pyright: ignore
        self.func_curr_code) = (  # pyright: ignore
        self.func_wrapper_locals) = (  # pyright: ignore
        self.hint_curr) = (  # pyright: ignore
        self.hint_curr_expr) = (  # pyright: ignore
        self.indent_child) = (  # pyright: ignore
        self.indent_curr) = (  # pyright: ignore
        self.indent_level_child) = (  # pyright: ignore
        self.index_last) = (  # pyright: ignore
        self.is_check_expr_cacheable) = (  # pyright: ignore
        self.is_var_random_int_needed) = (  # pyright: ignore
        self.pith_curr_assign_expr) = (  # pyright: ignore
        self.pith_curr_var_name) = None  # type: ignore[assignment]


    def reinit(
        self,
        call_curr: BeartypeCallDataABC,
        conf: BeartypeConf,
        hint_sane: HintSane,
    ) -> None:
        '''
        Reinitialize this type-checking metadata queue.

        Parameters
        ----------
        call_curr : BeartypeCallDataABC
            **Beartype call metadata** (i.e., dataclass aggregating *all* common
            metadata encapsulating the user-defined callable, type, or statement
            currently being type-checked by the end user).
        conf : BeartypeConf
            **Beartype configuration** (i.e., self-caching dataclass
            encapsulating all settings configuring type-checking for this hint).
        hint_sane : HintSane
            **Sanified type hint metadata** (i.e., :data:`.HintSane` object)
            encapsulating the hint to be type-checked.
        '''
        assert isinstance(call_curr, BeartypeCallDataABC), (
            f'{repr(call_curr)} not beartype call metadata.')
        assert isinstance(conf, BeartypeConf), (
            f'{repr(conf)} not beartype configuration.')
        assert isinstance(hint_sane, HintSane), (
            f'{repr(hint_sane)} not sanified hint metadata.')

        # ..................{ PREAMBLE                       }..................
        # Deinitialize this type-checking metadata queue *BEFORE* overwriting
        # the initial defaults applied by this method.
        self.deinit()

        # ..................{ PARAMETERS                     }..................
        # Classify all passed parameters.
        self.call_curr = call_curr
        self.conf = conf

        # True only if the pure-Python expression dynamically generated by
        # the higher-level make_check_expr() code factory to type-check this
        # sanified hint is cacheable, defaulting to the same boolean set on this
        # sanified hint metadata.
        self.is_check_expr_cacheable = hint_sane.is_check_expr_cacheable

        # ..................{ DEFAULTS                       }..................
        # Restore instance variables to initial defaults.
        self.is_var_random_int_needed = False
        self.func_wrapper_locals = {}

        # 0-based index of metadata describing the last visitable hint in this
        # queue, initialized to "-1" to ensure that the initial incrementation
        # of this index by the enqueue_hint_child() method initializes index 0
        # of this queue.
        self.index_last = -1

        # 1-based indentation level describing the initial level of indentation
        # appropriate for the root hint.
        self.indent_level_child = 1

    # ..................{ SETTERS                            }..................
    def set_index_current(self, hint_index: int) -> None:
        '''
        Set the hint encapsulated by the metadata with the passed 0-based index
        as the currently visited hint of the breadth-first search (BFS) iterated
        by this queue.

        This setter updates instance variables of this queue to reflect that
        this hint is now the currently visited hint.

        Parameters
        ----------
        hint_index: int
            0-based index of the metadata describing the currently visited hint,
            appended by the previously visited parent hint to this queue.
        '''
        assert isinstance(hint_index, int), f'{repr(hint_index)} not integer.'
        assert 0 <= hint_index <= self.index_last, (
            f'{hint_index} not in [0, {self.index_last}].')

        # Metadata describing the currently visited hint.
        #
        # Note that this hint is guaranteed to have been enqueued by the prior
        # range validation. Ergo, this hint may be safely accessed here via a
        # slightly faster indexed lookup directly on the "_hint_queue" list
        # rather than slower call to the _make_hint_data() getter.
        self.hint_curr = self._hint_queue[hint_index]  # pyright: ignore

        # Update instance variables of this queue to reflect that this hint is
        # now the currently visited hint.
        self.indent_level_child = self.hint_curr.indent_level + 1
        self.indent_curr  = INDENT_LEVEL_TO_CODE[self.hint_curr.indent_level]
        self.indent_child = INDENT_LEVEL_TO_CODE[self.indent_level_child]

        #FIXME: Comment this sanity check out after we're sufficiently
        #convinced this algorithm behaves as expected. While useful, this check
        #requires a linear search over the entire code and is thus costly.
        # assert hint_curr_placeholder in func_wrapper_code, (
        #     '{} {!r} placeholder {} not found in wrapper body:\n{}'.format(
        #         hint_curr_exception_prefix, hint, hint_curr_placeholder, func_wrapper_code))

        # Code snippet type-checking the current pith against this hint.
        self.func_curr_code = None  # type: ignore[assignment]

        # Code expression evaluating to the origin type underlying this hint.
        self.hint_curr_expr = None

    # ..................{ SANIFIERS                          }..................
    #FIXME: DRY violation. This is extremely similar to the
    #HintTreeError.sanify_hint_child() implementation. Let's try to push up all
    #code shared in common to a new concrete HintTreeABC.sanify_hint_child()
    #implementation, please. *sigh*
    def sanify_hint_child(
        self,

        # Mandatory parameters.
        hint_child_insane: Hint,

        # Optional parameters.
        hint_parent_sane: Optional[HintSane] = None,
    ) -> HintSane:
        '''
        Metadata encapsulating the sanification (i.e., sanitization) of the
        passed **possibly insane child type hint** (i.e., possibly
        PEP-noncompliant hint transitively subscripting the root hint annotating
        a parameter or return of the currently decorated callable) if this hint
        is both reducible and unignorable, this hint unmodified if this hint is
        both irreducible and unignorable, or :obj:`.HINT_SANE_IGNORABLE` otherwise
        (i.e., if this hint is ignorable).

        This method is merely a convenience wrapper for the lower-level
        :func:`.sanify_hint_child` sanifier.

        Parameters
        ----------
        hint_child_insane : Hint
            Child type hint to be sanified.
        hint_parent_sane : Optional[HintSane], default: None
            **Sanified parent type hint metadata** (i.e., immutable and thus
            hashable object encapsulating *all* metadata previously returned by
            :mod:`beartype._check.convert.convmain` sanifiers after sanitizing
            the possibly PEP-noncompliant parent hint of this child hint into a
            fully PEP-compliant parent hint). Defaults to :data:`None`, in which
            case this parameter actually defaults to
            ``self.hint_curr.hint_sane``, the previously sanified metadata
            encapsulating a parent transitive hint of this child hint. Since
            this default suffices in the common case, callers should only pass
            this parameter when explicitly sanifying the parent hint of this
            child hint outside the current breadth-first search (BFS).

        Returns
        -------
        HintSane
            Either:

            * If this child hint is ignorable,
              :obj:`beartype._check.cls.hint.hintsane.HINT_SANE_IGNORABLE`.
            * Else if this unignorable child hint is reducible to another hint,
              metadata encapsulating this reduction.
            * Else, this unignorable child hint is irreducible. In this case,
              metadata encapsulating this child hint unmodified.
        '''

        # If the caller explicitly passed *NO* sanified parent hint metadata,
        # default this metadata to that of the currently visited parent hint.
        if hint_parent_sane is None:
            hint_parent_sane = self.hint_curr.hint_sane
        # Else, the caller explicitly passed sanified parent hint metadata.
        # Silently preserve this metadata as is.

        # Metadata encapsulating the sanification of this child hint.
        hint_child_sane = sanify_hint_child(
            call_curr=self.call_curr,
            conf=self.conf,
            hint=hint_child_insane,
            hint_parent_sane=hint_parent_sane,
            exception_prefix=self.exception_prefix,
        )

        # The type-checking expression currently being generated by the
        # higher-level make_check_expr() code factory is safely cacheable if and
        # only if both this root hint *AND* all previously type-checked child
        # hints transitively subscripting this root hint are also cacheable.
        # Semantically, this ensures that the uncacheability of even a single
        # child hint renders the entire tree uncacheable by propagating
        # uncacheability up the tree of hints visitable from this root hint.
        self.is_check_expr_cacheable &= hint_child_sane.is_check_expr_cacheable

        # Return this metadata.
        return hint_child_sane

    # ..................{ ENQUEUERS                          }..................
    def enqueue_hint_child_sane(
        self,

        # Mandatory parameters.
        hint_sane: HintSane,
        pith_expr: str,

        # Optional parameters.
        hint_sign: HintSignOrNoneOrSentinel = SENTINEL,
    ) -> str:
        '''
        **Enqueue** (i.e., append) to the end of this queue new **type-checking
        metadata** (i.e., :class:`.HintDataCode` object) describing the
        currently iterated child type hint with the passed metadata, enabling
        the ongoing breadth-first search (BFS) traversing over this queue to
        subsequently visit this child hint.

        Callers are expected to initialize this metadata by explicitly setting
        these instance variables on this object *before* calling this method:

        * :attr:`indent_level_child`, the 1-based indentation level describing
          the current level of indentation appropriate for this child hint.
        * :attr:`hint_curr.pith_var_name_index`, the integer suffixing the name
          of each local variable assigned the value of the current pith in a
          assignment expression, thus uniquifying this variable in the body of
          the current wrapper function.

        Parameters
        ----------
        hint_sane : HintSane
            **Sanified child type hint metadata** (i.e., immutable and thus
            hashable object encapsulating *all* metadata returned by
            :mod:`beartype._check.convert.convmain` sanifiers after sanitizing
            this possibly PEP-noncompliant hint into a fully PEP-compliant hint)
            describing this child hint.
        pith_expr : str
            **Pith expression** (i.e., Python code snippet evaluating to the
            value of) the current **pith** (i.e., possibly nested object of the
            passed parameter or return to be type-checked against this child
            hint).
        hint_sign : Union[Optional[HintSign], Iota], default: SENTINEL
            Either:

            * If this child hint is uniquely identified by a **non-default
              sign** (i.e., a singleton instance of the :class:`.HintSign` class
              *other* than the standard sign returned by the
              :func:`.get_hint_pep_sign_or_none` getter), this sign.
            * Else, the sentinel placeholder, in which case this parameter
              defaults to their **default sign** (i.e., the sign returned by the
              :func:`.get_hint_pep_sign_or_none` getter).

            Defaults to the sentinel placeholder. This parameter should
            typically *not* be passed. Almost all hints are uniquely identified
            by their default sign. A small subset of hints, however,
            concurrently satisfy the detection criteria for multiple signs and
            are thus identifiable with multiple signs. This parameter supports
            those hints by enabling callers to call this method multiple times
            with the same hint passed different signs.

            Prominent examples include:

            * :pep:`484`- and :pep:`585`-compliant unsubscripted generics --
              which, due to being user-defined types, may subclass another
              PEP-compliant :mod:`typing` superclass also identifiable by
              another sign. Prominent examples include:

              * **Generic typed dictionaries** identifiable as both the
                :data:`.HintSignPep484585GenericUnsubbed` sign *and* the
                :data:`HintSignTypedDict` sign for :pep:`589`-compliant typed
                dictionaries: e.g.,

                .. code-block:: python

                   from typing import Generic, TypedDict
                   class GenericTypedDict[T](TypedDict, Generic[T]):
                       generic_item: T

              * **Generic named tuples** identifiable as both the
                :data:`.HintSignPep484585GenericUnsubbed` sign *and* the
                :data:`HintSignNamedTuple` sign for :pep:`484`-compliant named
                tuples: e.g.,

                .. code-block:: python

                   from typing import Generic, NamedTuple
                   class GenericNamedTuple[T](NamedTuple, Generic[T]):
                       generic_item: T

        Returns
        -------
        str
            Placeholder string to be subsequently replaced by code type-checking
            this child pith against this child hint.

        Raises
        ------
        BeartypeDecorHintRecursionException
            If the number of child type hints internally visited by this
            breadth-first search (BFS) exceeds the length of this queue. This
            exception guards against accidental infinite recursion when
            dynamically generating code type-checking against this hint.
        '''
        assert isinstance(hint_sane, HintSane), (
            f'{repr(hint_sane)} not sanified hint metadata.')
        # print(f'Enqueing child hint {self.index_last+1} with {repr(kwargs)}...')

        # ..................{ LOCALS                         }..................
        # Child hint to be enqueued, localized mostly for readability.
        hint_child = hint_sane.hint

        # If the caller did *NOT* pass a non-default sign identifying this child
        # hint, default this sign to the default sign identifying this hint.
        if hint_sign is SENTINEL:
            hint_sign = get_hint_pep_sign_or_none(hint_child)
        # Else, the caller passed a non-default sign identifying this hint.
        # Preserve this sign as is.

        # ..................{ INDEX                          }..................
        # Increment the 0-based index of metadata describing the last visitable
        # hint in this list (which also serves as the unique identifier of the
        # currently iterated child hint) *BEFORE* overwriting the existing
        # metadata at this index.
        #
        # Note this index is guaranteed to *NOT* exceed the fixed length of this
        # list. By prior validation, "FIXED_LIST_SIZE_MEDIUM" is guaranteed to
        # be substantially larger than "hints_meta_index_last".
        self.index_last += 1

        #FIXME: Unit test this, please. No idea how yet. I sigh. *sigh*
        # If the current number of child type hints internally visited by this
        # breadth-first search (BFS) exceeds the length of this queue...
        #
        # Note that this should *NEVER* happen, but probably nonetheless will.
        if self.index_last >= FIXED_LIST_SIZE_MEDIUM:  # pragma: no cover
            # Metadata encapsulating the previously enqueued root hint.
            root_hint_meta = self._hint_queue[0]

            # This root hint.
            root_hint = root_hint_meta.hint_sane.hint

            # Raise an exception embedding this root hint.
            raise BeartypeDecorHintRecursionException(
                f'{self.exception_prefix}child type hint {repr(hint_child)} '
                f'non-type-checkable. '
                f'Recursion detected when generating code type-checking from '
                f'root type hint {repr(root_hint)} to this child type hint. '
                f'Please submit this exception traceback as a new issue '
                f'to our friendly issue tracker:\n'
                f'\t{URL_ISSUES}\n'
                f'Beartype thanks you for your tragic (yet ultimately noble) '
                f'sacrifice.'
            )
        # Else, the current number of child type hints internally visited by
        # this breadth-first search (BFS) is still less than the length of this
        # queue. In this case, continue.

        # ..................{ METADATA                       }..................
        #FIXME: The _make_hint_data() factory is overkill, obviously. Since we
        #only that method here, just inline that method here. Yay! \o/
        # Type hint type-checking metadata at this index.
        hint_next = self._make_hint_data(hint_index=self.index_last)

        # Replace prior fields of this metadata with the passed fields.
        hint_next.reinit(
            hint_sane=hint_sane,
            hint_sign=hint_sign,  # type: ignore[arg-type]
            indent_level=self.indent_level_child,
            pith_expr=pith_expr,

            #FIXME: Kinda awkward, honestly. This warrants a rethink. *sigh*
            # Pith variable name index, defined as either...
            pith_var_name_index=(
                # If this breadth-first search (BFS) has yet to visit *ANY*
                # hint, this metadata *MUST* encapsulate the root hint. In this
                # case, the first such index;
                0
                if self.hint_curr is None else
                # Else, this BFS has already visited at least one hint. In this
                # case, the same index as that associated with the currently
                # visited hint.
                self.hint_curr.pith_var_name_index
            ),
        )

        # Return the placeholder string to be subsequently replaced by code
        # type-checking this child pith against this child hint, produced by
        # enqueueing new type-checking metadata describing this child hint.
        return hint_next.hint_placeholder

    # ..................{ PRIVATE ~ factories                }..................
    def _make_hint_data(self, hint_index: int) -> HintDataCode:
        '''
        **Type hint type-checking metadata** (i.e., :class:`.HintDataCode`
        object describing the previously enqueued hint at the passed index
        currently being visited by the breadth-first search (BFS) in the parent
        :func:`beartype._check.code.codemain.make_check_expr` factory).

        For both efficiency and simplicity, this getter *always* returns
        a valid :class:`HintDataCode` object for all valid indices. This queue thus
        behaves similarly to the :class:`collections.defaultdict` container.
        Specifically:

        * If this is the first attempt to access metadata at this index from
          this queue (i.e., the value of the item at this index is
          :data:`None`), this dunder method (in order):

          #. Instantiates a new :class:`.HintDataCode` object with all fields
             initialized to sane values appropriate for this index.
          #. Replaces the value of the item at this index (which was previously
             :data:`None`) with this new :class:`.HintDataCode` object.
          #. Returns a new :class:`.HintDataCode` object.

        * Else, this is a subsequent access of metadata at this index from this
          queue (i.e., the value of the item at this index is an existing
          :class:`.HintDataCode` object). In this case, this getter simply
          returns that existing :class:`.HintDataCode` object as is.

        Parameters
        ----------
        hint_index : int
            0-based absolute index of the type hint type-checking metadata to be
            retrieved, where:

            * Index 0 yields the root type hint currently visited by that BFS.
            * Index 1 yields the first child type hint of that root type hint.
            * And so on.

        Returns
        -------
        HintDataCode
            Type hint type-checking metadata at this index.
        '''
        assert isinstance(hint_index, int), f'{repr(hint_index)} not integer.'
        assert 0 <= hint_index < FIXED_LIST_SIZE_MEDIUM, (
            f'{hint_index} not in [0, {FIXED_LIST_SIZE_MEDIUM}].')

        # Type hint type-checking metadata at this hint_index.
        hint_next = self._hint_queue[hint_index]

        # If this metadata has yet to be instantiated, instantiate a new
        # "HintDataCode" object initialized to values suitable for this index.
        if hint_next is None:
            hint_next = self._hint_queue[hint_index] = HintDataCode(
                hint_index=hint_index)
        # Else, this metadata has already been instantiated.

        # Return this metadata.
        return hint_next
