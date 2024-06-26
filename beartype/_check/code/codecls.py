#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2024 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype **type-checking code classes** (i.e., low-level classes storing
metadata describing each iteration of the breadth-first search (BFS) dynamically
generating pure-Python code snippets type-checking arbitrary objects against
PEP-compliant type hints).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ TODO                               }....................
# All "FIXME:" comments for this submodule reside in this package's "__init__"
# submodule to improve maintainability and readability here.

#FIXME: This refactoring has yet another profound benefit. What? We can
#precompute the values of "pith_curr_var_name" at "HintMeta" instantiation time.
#Since that string *NEVER* changes, just assign each ""pith_curr_var_name"
#according to its index. Indeed, this suggests we probably no longer need
#either:
#* "pith_curr_var_name_index".
#* The entire "codesnipcls" submodule.
#
#Well, isn't this turning out to be a significant facepalm.

# ....................{ IMPORTS                            }....................
from beartype.typing import (
    TYPE_CHECKING,
)
from beartype._check.code.snip.codesnipstr import (
    CODE_HINT_CHILD_PLACEHOLDER_PREFIX,
    CODE_HINT_CHILD_PLACEHOLDER_SUFFIX,
)
from beartype._util.cache.pool.utilcachepoollistfixed import (
    FIXED_LIST_SIZE_MEDIUM,
    FixedList,
)
from beartype._util.utilobject import SENTINEL

# ....................{ DATACLASSES                        }....................
#FIXME: Unit test us up, please.
class HintMeta(object):
    '''
    **Type hint type-checking metadata** (i.e., low-level dataclass storing
    metadata describing the possibly nested type hint visited by the current
    iteration of the breadth-first search (BFS) dynamically generating
    pure-Python type-checking code snippets in the
    :func:`beartype._check.code.codemake.make_check_expr` factory).

    Attributes
    ----------
    hint : object
        Type hint currently visited by this BFS.
    hint_placeholder : str
        **Type-checking placeholder substring** to be globally replaced in the
        **type-checking wrapper function code snippet** (i.e., the
        ``func_wrapper_code`` local defined by the
        :func:`beartype._check.code.codemake.make_check_expr` factory) by a
        Python code snippet type-checking the **current pith expression** (i.e.,
        the ``pith_var_name`` local) against the **currently visited type hint**
        (i.e., the :attr:`hint` instance variable).

        This substring provides indirection enabling the currently visited
        parent hint to defer and delegate the generation of code type-checking
        each child type hint of this parent hint to the subsequent time at which
        that child type hint is visited by that BFS.

        This substring is intentionally prefixed and suffixed by characters
        that:

        * Are intentionally invalid as Python code, guaranteeing that the
          top-level call to the func:`exec` builtin subsequently performed by
          the :func:`beartype.beartype` decorator will raise a
          :exc:`SyntaxError` exception if the caller failed to replace *all*
          placeholder substrings.
        * Protect the :attr:`pith_var_name_index` integer embedded in this
          substring against ambiguous global replacements of longer such
          integers containing this integer (e.g., the integer 1, contained in
          the longer integers 11 and 21). If this integer were *not* protected
          in this manner, then the first substring ``"0"`` would ambiguously
          overlap with the subsequent substring ``"10"``, which would then
          produce catastrophically erroneous and undebuggable Python code.

        Example
        -------
        For example, the
        :func:`beartype._check.code.codemake.make_check_expr` factory might
        generate intermediary code resembling the following on visiting the
        :obj:`typing.Union` parent type hint of a subscripted ``Union[int,
        str]`` type hint *before* visiting either the :class:`int` or
        :class:`str` child type hints of that parent type hint:

        .. code-block:: python

           if not (
               @{0}! or
               @{1}!
           ):
               raise get_func_pith_violation(
                   func=__beartype_func,
                   pith_name=$%PITH_ROOT_NAME/~,
                   pith_value=__beartype_pith_root,
               )

        Note the unique substrings ``"@{0}!"`` and ``"@{1}!"`` in that code,
        which that factory iteratively replaces with code type-checking each of
        the child type hints (e.g., :class:`int`, :class:`str`) subscripting
        that :obj:`typing.Union` parent type hint. The final code memoized by
        that factory might then resemble:

        .. code-block:: python

           if not (
               isinstance(__beartype_pith_root, int) or
               isinstance(__beartype_pith_root, str)
           ):
               raise get_func_pith_violation(
                   func=__beartype_func,
                   pith_name=$%PITH_ROOT_NAME/~,
                   pith_value=__beartype_pith_root,
               )
    pith_expr : str
        **Pith expression** (i.e., Python code snippet evaluating to the value
        of) the current **pith** (i.e., possibly nested object of the passed
        parameter or return to be type-checked against the currently visited
        type hint).

        Note that this expression is intentionally *not* an assignment
        expression but rather the original inefficient expression provided by
        the parent type hint of the currently visited type hint.
    pith_var_name_index : int
        **Pith variable name index** (i.e., 0-based integer suffixing the name
        of each local variable assigned the value of the current pith in a
        assignment expression, thus uniquifying this variable in the body of the
        current wrapper function). Indexing the
        :obj:`beartype._check.code.snip.codesnipcls.PITH_INDEX_TO_VAR_NAME`
        dictionary singleton by this integer efficiently yields the current
        **pith variable name** locally storing the value of the current pith.

        Note that this integer is intentionally incremented as an efficient
        low-level scalar rather than as an inefficient high-level
        :class:`itertools.Counter` object. Since both are equally thread-safe in
        the internal context of a function body, the former is preferable.
    indent_level : int
        **Indentation level** (i.e., 1-based positive integer providing the
        current level of indentation appropriate for the currently visited type
        hint). Indexing the
        :obj:`beartype._data.code.datacodeindent.INDENT_LEVEL_TO_CODE`
        dictionary singleton by this integer efficiently yields the current
        **indendation string** suitable for prefixing each line of code
        type-checking the current pith against the current type hint.
    '''

    # ..................{ CLASS VARIABLES                    }..................
    # Slot all instance variables defined on this object to minimize the time
    # complexity of both reading and writing variables across frequently called
    # cache dunder methods. Slotting has been shown to reduce read and write
    # costs by approximately ~10%, which is non-trivial.
    __slots__ = (
        'hint',
        'hint_placeholder',
        'pith_expr',
        'pith_var_name_index',
        'indent_level',
    )

    # Squelch false negatives from mypy. This is absurd. This is mypy. See:
    #     https://github.com/python/mypy/issues/5941
    if TYPE_CHECKING:
        hint: object
        hint_placeholder: str
        pith_expr: str
        pith_var_name_index: int
        indent_level: int

    # ..................{ INITIALIZERS                       }..................
    def __init__(self, pith_var_name_index: int) -> None:
        '''
        Initialize this type-checking metadata dataclass.

        Parameters
        ----------
        pith_var_name_index : int
            Pith variable name index. See the class docstring.
        '''
        assert isinstance(pith_var_name_index, int), (
            f'{repr(pith_var_name_index)} not integer.')
        assert pith_var_name_index >= 0, (
            f'{repr(pith_var_name_index)} negative.')

        # Classify all passed parameters.
        self.pith_var_name_index = pith_var_name_index

        # Placeholder string to be globally replaced by code type-checking the
        # current pith against this hint.
        self.hint_placeholder = (
            f'{CODE_HINT_CHILD_PLACEHOLDER_PREFIX}'
            f'{str(pith_var_name_index)}'
            f'{CODE_HINT_CHILD_PLACEHOLDER_SUFFIX}'
        )

        # Nullify all remaining parameters for safety.
        self.hint = SENTINEL
        self.pith_expr = SENTINEL  # type: ignore[assignment]
        self.indent_level = SENTINEL  # type: ignore[assignment]

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

    Attributes
    ----------
    index_last : int
        0-based index of metadata describing the last visitable hint in this
        list. For efficiency, this integer also uniquely identifies the
        current child type hint of the currently visited parent type hint.
    '''

    # ..................{ CLASS VARIABLES                    }..................
    # Slot all instance variables defined on this object to minimize the time
    # complexity of both reading and writing variables across frequently
    # called @beartype decorations. Slotting has been shown to reduce read and
    # write costs by approximately ~10%, which is non-trivial.
    __slots__ = (
        'index_last',
    )

    # Squelch false negatives from mypy. This is absurd. This is mypy. See:
    #     https://github.com/python/mypy/issues/5941
    if TYPE_CHECKING:
        index_last: int

    # ..................{ INITIALIZERS                       }..................
    def __init__(self) -> None:
        '''
        Initialize this type-checking metadata list.
        '''

        # Initialize our superclass.
        super().__init__(size=FIXED_LIST_SIZE_MEDIUM)

        # 0-based index of metadata describing the last visitable hint in this
        # queue, initialized to "-1" to ensure that the initial incrementation
        # of this index by the enqueue_hint_child() method initializes index 0
        # of this queue.
        self.index_last = -1

    # ..................{ DUNDERS                            }..................
    def __getitem__(self, index: int) -> HintMeta:  # type: ignore[override]
        '''
        **Type hint type-checking metadata** (i.e., :class:`HintMeta` object)
        describing the type hint visited at the passed index by the
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
        index : int
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
        assert isinstance(index, int), f'{repr(index)} not integer.'
        assert 0 <= index <= len(self), f'{index} not in [0, {len(self)}].'

        # Type hint type-checking metadata at this index.
        hint_meta = FixedList.__getitem__(index)  # type: ignore[call-overload]

        # If this metadata has yet to be instantiated...
        if hint_meta is None:
            # Instantiate a new "HintMeta" object with all fields initialized
            # to sane values appropriate for this index.
            hint_meta = self[index] = HintMeta(pith_var_name_index=index)
        # Else, this metadata has already been instantiated.

        # Return this metadata.
        return hint_meta

    # ..................{ METHODS                            }..................
    def enqueue_hint_child(
        self,
        hint: object,
        pith_expr: str,
        indent_level: int,
    ) -> str:
        '''
        **Enqueue** (i.e., append) a new tuple of metadata describing the
        currently iterated child type hint to the end of the this queue,
        enabling this hint to be visited by the ongoing breadth-first search
        (BFS) traversing over this queue.

        Parameters
        ----------
        hint : object
            Currently iterated child type hint subscripting the currently
            visited type hint.
        pith_expr : str
            Python code snippet evaluating to the child pith to be type-checked
            against the currently iterated child type hint.
        indent_level : int
            1-based indentation level describing the current level of
            indentation appropriate for the currently iterated child hint.

        Returns
        -------
        str
            Placeholder string to be subsequently replaced by code type-checking
            this child pith against this child type hint.
        '''
        assert isinstance(pith_expr, str), (
            f'{repr(pith_expr)} not string.')
        assert isinstance(indent_level, int), (
            f'{repr(indent_level)} not integer.')
        assert pith_expr, f'{repr(pith_expr)} empty.'
        assert indent_level > 1, f'{repr(indent_level)} <= 1.'

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
        hint_meta.hint = hint
        hint_meta.pith_expr = pith_expr
        hint_meta.indent_level = indent_level

        # Return the placeholder substring associated with this type hint.
        return hint_meta.hint_placeholder
