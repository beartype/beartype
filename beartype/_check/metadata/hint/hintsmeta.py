#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2024 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype **type-checking code container classes** (i.e., low-level classes
storing metadata describing the breadth-first search (BFS) dynamically
generating pure-Python code snippets type-checking arbitrary objects against
PEP-compliant type hints).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.typing import (
    TYPE_CHECKING,
    Optional,
)
from beartype._check.code.codemagic import (
    EXCEPTION_PREFIX_FUNC_WRAPPER_LOCAL)
from beartype._check.code.codescope import add_func_scope_type_or_types
from beartype._check.code.snip.codesnipcls import (
    PITH_INDEX_TO_VAR_NAME)
from beartype._check.metadata.hint.hintmeta import HintMeta
from beartype._check.metadata.metasane import (
    HintOrHintSanifiedData,
    unpack_hint_or_sane,
)
from beartype._conf.confcls import BeartypeConf
from beartype._conf.confcommon import BEARTYPE_CONF_DEFAULT
from beartype._data.code.datacodeindent import INDENT_LEVEL_TO_CODE
from beartype._data.error.dataerrmagic import (
    EXCEPTION_PLACEHOLDER as EXCEPTION_PREFIX)
from beartype._data.hint.datahinttyping import (
    LexicalScope,
    TypeStack,
    TypeOrSetOrTupleTypes,
)
from beartype._util.cache.pool.utilcachepoollistfixed import (
    FIXED_LIST_SIZE_MEDIUM,
    FixedList,
)

# ....................{ SUBCLASSES                         }....................
#FIXME: Unit test us up, please.
class HintsMeta(FixedList):
    '''
    **Type hint type-checking metadata queue** (i.e., low-level fixed list of
    metadata describing all visitable type hints currently discovered by the
    breadth-first search (BFS) dynamically generating pure-Python type-checking
    code snippets in the :func:`beartype._check.code.codemake.make_check_expr`
    factory).

    This list acts as a standard First In First Out (FILO) queue, enabling that
    BFS to be implemented as an efficient imperative algorithm rather than an
    inefficient -- and dangerous, due to both unavoidable stack exhaustion and
    avoidable infinite recursion -- recursive algorithm.

    Note that this list is guaranteed by the previously called
    ``_die_if_hint_repr_exceeds_child_limit()`` function to be larger than the
    number of hints transitively visitable from this root hint. Ergo, *all*
    indexation into this list performed by this BFS is guaranteed to be safe.

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
    cls_stack : TypeStack
        **Type stack** (i.e., either a tuple of the one or more
        :func:`beartype.beartype`-decorated classes lexically containing the
        class variable or method annotated by this hint *or* :data:`None`).
    conf : BeartypeConf
        **Beartype configuration** (i.e., self-caching dataclass encapsulating
        all settings configuring type-checking for the passed object).
    exception_prefix : str
        Human-readable substring prefixing the representation of this object in
        the exception message.
    func_curr_code : Optional[str]
        Either:

        * If the currently visited hint is deeply type-checkable, the Python
          code snippet type-checking the current pith against this hint.
        * If the currently visited hint is only shallowly type-checkable,
          :data:`None`.
    func_wrapper_scope : LexicalScope
        **Local scope** (i.e., dictionary mapping from the name to value of each
        attribute referenced in the signature) of this wrapper function required
        by this Python code snippet.
    hint_curr_expr : Optional[str]
        Either:

        * If the currently visited hint is deeply type-checkable, :data:`None`.
        * If the currently visited hint is only shallowly type-checkable, the
          Python expression evaluating to the origin type underlying this hint
          as a hidden :mod:`beartype`-specific parameter injected into the
          signature of the current wrapper function.
    hint_curr_meta: HintMeta
        Metadata describing the currently visited hint, appended by the
        previously visited parent hint to this queue.
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
    is_var_random_int_needed : bool
        :data:`True` only if one or more child hints of the root hint of this
        queue require a pseudo-random integer. If :data:`True`, the body of this
        wrapper function will be prefixed with code generating this integer.
    pith_curr_expr : str
        Full Python expression evaluating to the value of the **current pith**
        (i.e., possibly nested object of the current parameter or return value
        to be type-checked against this union type hint).

        Note that this is intentionally *not* an assignment expression but
        rather the original inefficient expression provided by the parent type
        hint of the currently visited hint.
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
    pith_curr_var_name_index : int
        Integer suffixing the name of each local variable assigned the value of
        the current pith in a assignment expression, thus uniquifying this
        variable in the body of the current wrapper function.

        Note that this integer is intentionally incremented as an efficient
        low-level scalar rather than as an inefficient high-level
        "itertools.Counter" object. Since both are equally thread-safe in the
        internal context of this function body, the former is preferable.
    '''

    # ..................{ CLASS VARIABLES                    }..................
    # Slot all instance variables defined on this object to minimize the time
    # complexity of both reading and writing variables across frequently
    # called @beartype decorations. Slotting has been shown to reduce read and
    # write costs by approximately ~10%, which is non-trivial.
    __slots__ = (
        'cls_stack',
        'conf',
        'exception_prefix',
        'func_curr_code',
        'func_wrapper_scope',
        'hint_curr_expr',
        'hint_curr_meta',
        'indent_curr',
        'indent_child',
        'indent_level_child',
        'index_last',
        'is_var_random_int_needed',
        'pith_curr_expr',
        'pith_curr_assign_expr',
        'pith_curr_var_name',
        'pith_curr_var_name_index',
    )

    # Squelch false negatives from mypy. This is absurd. This is mypy. See:
    #     https://github.com/python/mypy/issues/5941
    if TYPE_CHECKING:
        cls_stack: TypeStack
        conf: BeartypeConf
        exception_prefix: str
        func_curr_code: str
        func_wrapper_scope: LexicalScope
        hint_curr_expr : Optional[str]
        hint_curr_meta : HintMeta
        indent_curr: str
        indent_child: str
        indent_level_child: int
        index_last: int
        is_var_random_int_needed: bool
        pith_curr_expr: str
        pith_curr_assign_expr: str
        pith_curr_var_name: str
        pith_curr_var_name_index: int

    # ..................{ INITIALIZERS                       }..................
    def __init__(self) -> None:
        '''
        Initialize this type-checking metadata list.
        '''

        # Initialize our superclass.
        super().__init__(size=FIXED_LIST_SIZE_MEDIUM)

        # Initialize this type-checking metadata queue.
        self.reinit()


    def reinit(
        self,

        # Optional parameters. Note that these parameters are optional *ONLY* to
        # allow the __init__() method to be trivially defined. In all *OTHER*
        # calls to this method, these parameters should always be passed. Ugh!
        cls_stack: TypeStack = None,
        conf: BeartypeConf = BEARTYPE_CONF_DEFAULT,
    ) -> None:
        '''
        Reinitialize this type-checking metadata queue.

        Parameters
        ----------
        See the class docstring for further details on passed parameters.
        '''

        # Classify all passed parameters.
        self.conf = conf
        self.cls_stack = cls_stack

        # 0-based index of metadata describing the last visitable hint in this
        # queue, initialized to "-1" to ensure that the initial incrementation
        # of this index by the enqueue_hint_child() method initializes index 0
        # of this queue.
        self.index_last = -1

        # Nullify all remaining passed parameters.
        self.exception_prefix = EXCEPTION_PREFIX
        self.func_curr_code = None  # type: ignore[assignment]
        self.func_wrapper_scope = {}
        self.hint_curr_expr = None
        self.hint_curr_meta = None  # type: ignore[assignment]
        self.indent_curr = None  # type: ignore[assignment]
        self.indent_child = None  # type: ignore[assignment]
        self.indent_level_child: int = None  # type: ignore[assignment]
        self.is_var_random_int_needed = False
        self.pith_curr_expr = None  # type: ignore[assignment]
        self.pith_curr_assign_expr = None  # type: ignore[assignment]
        self.pith_curr_var_name = None  # type: ignore[assignment]
        self.pith_curr_var_name_index = 0

    # ..................{ DUNDERS                            }..................
    def __getitem__(self, hint_index: int) -> HintMeta:  # type: ignore[override]
        '''
        **Type hint type-checking metadata** (i.e., :class:`.HintMeta` object)
        describing the currently visited type hint at the passed index by the
        breadth-first search (BFS) in the
        :func:`beartype._check.code.codemake.make_check_expr` factory.

        For both efficiency and simplicity, this dunder method *always* returns
        a valid :class:`HintMeta` object for all valid indices. This list thus
        behaves similarly to the :class:`collections.defaultdict` container.
        Specifically:

        * If this is the first attempt to access metadata at this index from
          this list (i.e., the value of the item at this index is :data:`None`),
          this dunder method (in order):

          #. Instantiates a new :class:`.HintMeta` object with all fields
             initialized to sane values appropriate for this index.
          #. Replaces the value of the item at this index (which was previously
             :data:`None`) with this new :class:`.HintMeta` object.
          #. Returns new :class:`.HintMeta` object.

        * Else, this is a subsequent access of metadata at this index from this
          list (i.e., the value of the item at this index is an existing
          :class:`.HintMeta` object). In this case, this dunder method simply
          returns that existing :class:`.HintMeta` object as is.

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
        HintMeta
            Type hint type-checking metadata at this index.
        '''
        assert isinstance(hint_index, int), f'{repr(hint_index)} not integer.'
        assert 0 <= hint_index <= len(self), (
            f'{hint_index} not in [0, {len(self)}].')

        # Type hint type-checking metadata at this hint_index.
        hint_curr_meta = super().__getitem__(hint_index)  # type: ignore[call-overload]

        # If this metadata has yet to be instantiated...
        if hint_curr_meta is None:
            # Instantiate a new "HintMeta" object with all fields initialized
            # to sane values appropriate for this index.
            hint_curr_meta = self[hint_index] = HintMeta(hint_index=hint_index)
        # Else, this metadata has already been instantiated.

        # Return this metadata.
        return hint_curr_meta

    # ..................{ SETTERS                            }..................
    def set_hint_curr_meta(self, hint_curr_meta: HintMeta) -> None:
        '''
        Set the hint encapsulated by the passed metadata as the currently
        visited hint of the breadth-first search (BFS) iterated by this queue.

        This setter updates instance variables of this queue to reflect that
        this hint is now the currently visited hint.

        Parameters
        ----------
        hint_curr_meta: HintMeta
            Metadata describing the currently visited hint, appended by the
            previously visited parent hint to this queue.
        '''
        assert isinstance(hint_curr_meta, HintMeta), (
            f'{repr(hint_curr_meta)} not "HintMeta" object.')

        # Current level of indentation appropriate for this hint.
        indent_level_curr = hint_curr_meta.indent_level

        # Update instance variables of this queue to reflect that this hint is
        # now the currently visited hint.
        self.hint_curr_meta = hint_curr_meta
        self.indent_level_child = indent_level_curr + 1
        self.indent_curr  = INDENT_LEVEL_TO_CODE[indent_level_curr]
        self.indent_child = INDENT_LEVEL_TO_CODE[self.indent_level_child]
        self.pith_curr_expr = hint_curr_meta.pith_expr
        self.pith_curr_var_name_index = hint_curr_meta.pith_var_name_index
        self.pith_curr_var_name = PITH_INDEX_TO_VAR_NAME[
            self.pith_curr_var_name_index]

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

    # ..................{ ADDERS                             }..................
    def add_func_scope_type_or_types(
        self, type_or_types: TypeOrSetOrTupleTypes) -> str:
        '''
        Add a new **scoped class or tuple of classes** (i.e., new key-value pair
        of the passed dictionary mapping from the name to value of each globally
        or locally scoped attribute externally accessed elsewhere, whose key is
        a machine-readable name internally generated by this function to
        uniquely refer to the passed class or tuple of classes and whose value
        is that class or tuple) to this local scope of this wrapper function
        *and* return that name.

        This method is merely a high-level convenience wrapping the lower-level
        :func:`beartype._check.code.codescope.add_func_scope_type_or_types`
        function.

        Parameters
        ----------
        type_or_types : TypeOrSetOrTupleTypes
            Classes to be added to this scope, defined as either:

            * A single class.
            * A set of one or more classes.
            * A tuple of one or more classes.

        Returns
        -------
        str
            Name of this class or tuple in this scope generated by this function.

        See Also
        ------
        :func:`beartype._check.code.codescope.add_func_scope_type_or_types`
            Further details.
        '''

        # Defer to the lower-level add_func_scope_type_or_types() adder.
        return add_func_scope_type_or_types(
            type_or_types=type_or_types,
            func_scope=self.func_wrapper_scope,
            exception_prefix=EXCEPTION_PREFIX_FUNC_WRAPPER_LOCAL,
        )

    # ..................{ ENQUEUERS                          }..................
    def enqueue_hint_or_sane_child(
        self,
        hint_or_sane: HintOrHintSanifiedData,
        indent_level: int,
        pith_expr: str,
        pith_var_name_index: int,
    ) -> str:
        '''
        **Enqueue** (i.e., append) to the end of the this queue new
        **type-checking metadata** (i.e., a :class:`.HintMeta` object)
        describing the currently iterated child type hint with the passed
        metadata, enabling this hint to be visited by the ongoing breadth-first
        search (BFS) traversing over this queue.

        Parameters
        ----------
        hint_or_sane : HintOrHintSanifiedData
            Either a type hint *or* **sanified type hint metadata** (i.e.,
            :data:`.HintSanifiedData` object) to be type-checked.

        All remaining passed keyword parameters are passed as is to the
        lower-level :meth:`.HintMeta.reinit` method.

        Returns
        -------
        str
            Placeholder string to be subsequently replaced by code type-checking
            this child pith against this child type hint.
        '''

        # Child hint and type variable lookup table encapsulated by this data.
        hint, typevar_to_hint = unpack_hint_or_sane(hint_or_sane)

        # Return the placeholder string to be subsequently replaced by code
        # type-checking this child pith against this child hint, produced by
        # enqueueing new type-checking metadata describing this child hint.
        return self.enqueue_hint_child(
            hint=hint,
            indent_level=indent_level,
            pith_expr=pith_expr,
            pith_var_name_index=pith_var_name_index,
            typevar_to_hint=typevar_to_hint,
        )


    def enqueue_hint_child(self, **kwargs) -> str:
        '''
        **Enqueue** (i.e., append) to the end of the this queue new
        **type-checking metadata** (i.e., a :class:`.HintMeta` object)
        describing the currently iterated child type hint with the passed
        metadata, enabling this hint to be visited by the ongoing breadth-first
        search (BFS) traversing over this queue.

        Parameters
        ----------
        All passed keyword parameters are passed as is to the lower-level
        :meth:`.HintMeta.reinit` method.

        Returns
        -------
        str
            Placeholder string to be subsequently replaced by code type-checking
            this child pith against this child type hint.
        '''
        # print(f'Enqueing child hint {self.index_last+1} with {repr(kwargs)}...')

        # Increment the 0-based index of metadata describing the last visitable
        # hint in this list (which also serves as the unique identifier of the
        # currently iterated child hint) *BEFORE* overwriting the existing
        # metadata at this index.
        #
        # Note this index is guaranteed to *NOT* exceed the fixed length of this
        # list. By prior validation, "FIXED_LIST_SIZE_MEDIUM" is guaranteed to
        # be substantially larger than "hints_meta_index_last".
        self.index_last += 1

        # Type hint type-checking metadata at this index.
        hint_meta = self.__getitem__(self.index_last)

        # Replace prior fields of this metadata with the passed fields.
        hint_meta.reinit(**kwargs)

        # Return the placeholder substring associated with this type hint.
        return hint_meta.hint_placeholder