#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype **type-checking code classes** (i.e., low-level classes storing
metadata describing each iteration of the breadth-first search (BFS) dynamically
generating pure-Python code snippets type-checking arbitrary objects against
PEP-compliant type hints).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.typing import (
    TYPE_CHECKING,
)
from beartype._check.code.snip.codesnipcls import (
    HINT_INDEX_TO_HINT_PLACEHOLDER)
from beartype._data.hint.datahintpep import (
    Hint,
    TypeVarToHint,
)
from beartype._util.kind.map.utilmapfrozen import FrozenDict
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
    hint : Hint
        Type hint currently visited by this BFS.
    hint_placeholder : str
        **Type-checking placeholder substring** to be globally replaced in the
        **type-checking wrapper function code snippet** (i.e., the
        ``func_wrapper_code`` local defined by the
        :func:`beartype._check.code.codemake.make_check_expr` factory) by a
        Python code snippet type-checking the **current pith expression** (i.e.,
        the ``pith_var_name`` local) against the **currently visited type hint**
        (i.e., the :attr:`hint` instance variable).
    indent_level : int
        **Indentation level** (i.e., 1-based positive integer providing the
        level of indentation appropriate for the currently visited type hint).

        Indexing the
        :obj:`beartype._data.code.datacodeindent.INDENT_LEVEL_TO_CODE`
        dictionary singleton by this integer efficiently yields the current
        **indendation string** suitable for prefixing each line of code
        type-checking the current pith against the current type hint.
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
        of each local variable assigned the value of the current pith in an
        assignment expression, thus uniquifying this variable in the body of the
        current wrapper function). Indexing the
        :obj:`beartype._check.code.snip.codesnipcls.PITH_INDEX_TO_VAR_NAME`
        dictionary singleton by this integer efficiently yields the current
        **pith variable name** locally storing the value of the current pith.

        Note that this integer is intentionally incremented as an efficient
        low-level scalar rather than as an inefficient high-level
        :class:`itertools.Counter` object. Since both are equally thread-safe in
        the internal context of a function body, the former is preferable.
    typevar_to_hint : TypeVarToHint
        **Type variable lookup table** (i.e., immutable dictionary mapping from
        each :pep:`484`-compliant type variable parametrizing either the
        currently visited type hint *or* a transitive parent type hint of this
        hint to the corresponding non-type variable type hint subscripting that
        hint). This table enables runtime type-checkers to efficiently reduce a
        proper subset of type variables to non-type variables at
        :func:`beartype.beartype` decoration time, including:

        * :pep:`484`- or :pep:`585`-compliant **subscripted generics.** For
          example, this table enables runtime type-checkers to reduce the
          semantically useless pseudo-superclass ``list[T]`` to the
          semantically useful pseudo-superclass ``list[int]`` at decoration time
          in the following example:

          .. code-block:: python

             class MuhGeneric[T](list[T]): pass

             @beartype
             def muh_func(muh_arg: MuhGeneric[int]) -> None: pass

        * :pep:`695`-compliant **subscripted type aliases.** For example, this
          table enables runtime type-checkers to reduce the semantically useless
          type hint ``muh_type_alias[float]`` to the semantically useful type
          hint ``float | int`` at decoration time in the following example:

          .. code-block:: python

             type muh_type_alias[T] = T | int

             @beartype
             def muh_func(muh_arg: muh_type_alias[float]) -> None: pass
    '''

    # ..................{ CLASS VARIABLES                    }..................
    # Slot all instance variables defined on this object to minimize the time
    # complexity of both reading and writing variables across frequently called
    # cache dunder methods. Slotting has been shown to reduce read and write
    # costs by approximately ~10%, which is non-trivial.
    __slots__ = (
        'hint',
        'hint_placeholder',
        'indent_level',
        'pith_expr',
        'pith_var_name_index',
        'typevar_to_hint',
    )

    # Squelch false negatives from mypy. This is absurd. This is mypy. See:
    #     https://github.com/python/mypy/issues/5941
    if TYPE_CHECKING:
        hint: Hint
        hint_placeholder: str
        indent_level: int
        pith_expr: str
        pith_var_name_index: int
        typevar_to_hint: TypeVarToHint

    # ..................{ INITIALIZERS                       }..................
    def __init__(self, hint_index: int) -> None:
        '''
        Initialize this type-checking metadata.

        Parameters
        ----------
        hint_index : int
            0-based index of this type-checking metadata in the parent
            :class:`.HintsMeta` list containing this metadata.
        '''
        assert isinstance(hint_index, int), f'{repr(hint_index)} not integer.'
        assert hint_index >= 0, f'{repr(hint_index)} < 0.'

        # Placeholder string to be globally replaced by code type-checking the
        # current pith against this hint.
        self.hint_placeholder = HINT_INDEX_TO_HINT_PLACEHOLDER[hint_index]

        # Nullify all instance variables for safety.
        self.hint = SENTINEL  # type: ignore[assignment]
        self.indent_level = SENTINEL  # type: ignore[assignment]
        self.pith_expr = SENTINEL  # type: ignore[assignment]
        self.pith_var_name_index = SENTINEL  # type: ignore[assignment]
        self.typevar_to_hint = SENTINEL  # type: ignore[assignment]


    def reinit(
        self,
        hint: Hint,
        indent_level: int,
        pith_expr: str,
        pith_var_name_index: int,
        typevar_to_hint: TypeVarToHint,
    ) -> None:
        '''
        Reinitialize this type-checking metadata.

        Parameters
        ----------
        hint : Hint
            Currently iterated child type hint subscripting the currently
            visited type hint.
        indent_level : int
            1-based indentation level describing the current level of
            indentation appropriate for the currently iterated child hint.
        pith_expr : str
            Python code snippet evaluating to the child pith to be type-checked
            against the currently iterated child type hint.
        pith_var_name_index : int
            0-based integer suffixing the name of each local variable assigned
            the value of the current pith in an assignment expression.
        typevar_to_hint : TypeVarToHint
            **Type variable lookup table** (i.e., immutable dictionary mapping
            from the :pep:`484`-compliant **type variables** (i.e.,
            :class:`typing.TypeVar` objects) originally parametrizing the
            origins of all transitive parent hints of this hint to the
            corresponding child hints subscripting these parent hints).
        '''
        assert isinstance(indent_level, int), (
            f'{repr(indent_level)} not integer.')
        assert isinstance(pith_expr, str), (
            f'{repr(pith_expr)} not string.')
        assert isinstance(pith_var_name_index, int), (
            f'{repr(pith_var_name_index)} not integer.')
        assert isinstance(typevar_to_hint, FrozenDict), (
            f'{repr(typevar_to_hint)} not frozen dictionary.')
        assert indent_level >= 1, f'{repr(indent_level)} < 1.'
        assert pith_expr, f'{repr(pith_expr)} empty.'
        assert pith_var_name_index >= 0, f'{repr(pith_var_name_index)} < 0.'

        # Classify all passed parameters.
        self.hint = hint
        self.indent_level = indent_level
        self.pith_expr = pith_expr
        self.pith_var_name_index = pith_var_name_index
        self.typevar_to_hint = typevar_to_hint

    # ..................{ DUNDERS                            }..................
    def __repr__(self) -> str:
        '''
        Machine-readable representation of this metadata.
        '''

        # Represent this metadata with just the minimal subset of metadata
        # needed to reasonably describe this metadata.
        return (
            f'{self.__class__.__name__}('
            f'hint={repr(self.hint)}, '
            f'indent_level={repr(self.indent_level)}, '
            f'pith_expr={repr(self.pith_expr)}, '
            f'pith_var_name_index={repr(self.pith_var_name_index)}, '
            f'typevar_to_hint={repr(self.typevar_to_hint)}'
            f')'
        )
