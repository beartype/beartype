#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2024 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype :pep:`484`- or :pep:`585`-compliant **container type-checking code
factories** (i.e., low-level callables dynamically generating pure-Python code
snippets type-checking arbitrary objects against container type hints).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.roar import BeartypeDecorHintPepException
from beartype.typing import (
    Optional,
    Tuple,
)
from beartype._check.code.codecls import (
    HintMeta,
    HintsMeta,
)
from beartype._check.code.codemagic import (
    EXCEPTION_PREFIX_FUNC_WRAPPER_LOCAL)
from beartype._check.code.codescope import add_func_scope_type
from beartype._check.code.snip.codesnipcls import PITH_INDEX_TO_VAR_NAME
from beartype._check.convert.convsanify import (
    sanify_hint_child_if_unignorable_or_none)
from beartype._check.logic.logmap import (
    HINT_SIGN_PEP484585_CONTAINER_ARGS_1_TO_LOGIC_get)
from beartype._conf.confcls import BeartypeConf
from beartype._data.code.datacodeindent import INDENT_LEVEL_TO_CODE
from beartype._data.hint.datahinttyping import (
    LexicalScope,
)
from beartype._data.hint.pep.sign.datapepsigns import HintSignTuple
from beartype._data.hint.datahinttyping import TypeStack
from beartype._util.hint.pep.proposal.pep484585.pep484585 import (
    get_hint_pep484585_arg)
from beartype._util.hint.pep.utilpepget import (
    get_hint_pep_args,
    get_hint_pep_origin_type_isinstanceable,
    get_hint_pep_sign,
)

# ....................{ FACTORIES                          }....................
def make_hint_pep484585_container_check_expr(
    hint_meta: HintMeta,
    hints_meta: HintsMeta,
    cls_stack: TypeStack,
    conf: BeartypeConf,
    func_wrapper_scope: LexicalScope,
    pith_curr_assign_expr: str,
    pith_curr_var_name_index: int,
    exception_prefix: str,
) -> Tuple[Optional[str], str, bool]:
    '''
    Either a Python code snippet type-checking the current pith against the
    passed :pep:`484`- or :pep:`585`-compliant container type hint if this hint
    is **unignorable** (i.e., subscripted by *no* ignorable child type hints)
    *or* :data:`None` otherwise (i.e., if this hint is ignorable).

    This factory is intentionally *not* memoized (e.g., by the
    :func:`.callable_cached` decorator), due to accepting **context-sensitive
    parameters** (i.e., whose values contextually depend on context unique to
    the code being generated for the currently decorated callable) such as
    ``pith_curr_assign_expr``.

    Parameters
    ----------
    hint_meta : HintMeta
        Metadata describing the currently visited hint, appended by the
        previously visited parent hint to the ``hints_meta`` stack.
    hints_meta : HintsMeta
        Stack of metadata describing all visitable hints currently discovered by
        this breadth-first search (BFS).
    cls_stack : TypeStack, optional
        **Type stack** (i.e., either a tuple of the one or more
        :func:`beartype.beartype`-decorated classes lexically containing the
        class variable or method annotated by this hint *or* :data:`None`).
        Defaults to :data:`None`.
    conf : BeartypeConf
        **Beartype configuration** (i.e., self-caching dataclass encapsulating
        all settings configuring type-checking for the passed object).
    func_wrapper_scope : LexicalScope
        Local scope (i.e., dictionary mapping from the name to value of each
        attribute referenced in the signature) of this wrapper function required
        by this Python code snippet.
    pith_curr_assign_expr : str
        Assignment expression assigning this full Python expression to the
        unique local variable assigned the value of this expression.
    pith_curr_var_name_index : int
        Integer suffixing the name of each local variable assigned the value of
        the current pith in a assignment expression, thus uniquifying this
        variable in the body of the current wrapper function.
    exception_prefix : str, optional
        Human-readable substring prefixing the representation of this object in
        the exception message. Defaults to the empty string.

    Returns
    -------
    Tuple[Optional[str], str, bool]
        2-tuple ``(func_curr_code, hint_curr_expr, is_var_random_int_needed)``
        where:

        * ``func_curr_code`` is either:

          * If this hint is ignorable, :data:`None`.
          * Else, a Python code snippet type-checking the current pith against
            this hint.

        * ``hint_curr_expr`` is a Python expression evaluating to the origin
          type of this hint as a hidden :mod:`beartype`-specific parameter
          injected into the signature of the current wrapper function.
        * ``is_var_random_int_needed`` is :data:`True` only if this hint require
          a pseudo-random integer. If :data:`True`, logic elsewhere prefixes the
          body of this wrapper function with code generating this integer.
    '''
    assert isinstance(hint_meta, HintMeta), (
        f'{repr(hint_meta)} not "HintMeta" object.')
    assert isinstance(hints_meta, HintsMeta), (
        f'{repr(hints_meta)} not "HintsMeta" object.')
    assert isinstance(pith_curr_assign_expr, str), (
        f'{repr(pith_curr_assign_expr)} not string.')
    assert isinstance(pith_curr_var_name_index, int), (
        f'{repr(pith_curr_var_name_index)} not integer.')

    # ....................{ LOCALS                         }....................
    # Python code snippet type-checking the current pith against this hint.
    func_curr_code: str = None  # type: ignore[assignment]

    # True only if this hint require a pseudo-random integer. If true, logic
    # elsewhere prefixes the body of this wrapper function with code generating
    # this integer.
    is_var_random_int_needed = False

    # This container hint, localized for negligible efficiency gains. *sigh*
    hint = hint_meta.hint

    # Python expression evaluating to the origin type of this hint as a hidden
    # beartype-specific parameter injected into the signature of this wrapper.
    hint_curr_expr = add_func_scope_type(
        # Origin type underlying this hint.
        cls=get_hint_pep_origin_type_isinstanceable(hint),
        func_scope=func_wrapper_scope,
        exception_prefix=EXCEPTION_PREFIX_FUNC_WRAPPER_LOCAL,
    )
    # print(f'Container type hint {hint_curr} origin type scoped: {hint_curr_expr}')

    # Sign uniquely identifying this hint.
    hint_sign = get_hint_pep_sign(hint)

    # Tuple of all child hints subscripting this hint if any *OR* the empty
    # tuple otherwise (e.g., if this hint is its own unsubscripted factory).
    #
    # Note that the "__args__" dunder attribute is *NOT* guaranteed to exist for
    # arbitrary PEP-compliant type hints. Ergo, we obtain this attribute via a
    # higher-level utility getter.
    hint_childs = get_hint_pep_args(hint)

    # Possibly ignorable insane child hint subscripting this parent hint,
    # defined as either...
    hint_child = (  # pyright: ignore
        # If this parent hint is a variable-length tuple, the
        # get_hint_pep_sign() getter called above has already validated the
        # contents of this tuple. In this case, efficiently get the lone child
        # hint of this parent hint *WITHOUT* validation.
        hint_childs[0]
        if hint_sign is HintSignTuple else
        # Else, this hint is a single-argument container, in which case the
        # contents of this container have yet to be validated. In this case,
        # inefficiently get the lone child hint of this parent hint *WITH*
        # validation.
        get_hint_pep484585_arg(hint=hint, exception_prefix=exception_prefix)
    )
    # print(f'Sanifying container hint {repr(hint_curr)} child hint {repr(hint_child)}...')
    # print(f'...with type variable lookup table {repr(hint_curr_meta.typevar_to_hint)}.')

    # Unignorable sane child hint sanified from this possibly ignorable insane
    # child hint *OR* "None" otherwise (i.e., if this child hint is ignorable).
    hint_or_sane_child = sanify_hint_child_if_unignorable_or_none(
        hint=hint_child,
        cls_stack=cls_stack,
        conf=conf,
        typevar_to_hint=hint_meta.typevar_to_hint,
        exception_prefix=exception_prefix,
    )

    # ....................{ FORMAT                         }....................
    # If this child hint is unignorable:
    # * Shallowly type-check the type of the current pith.
    # * Deeply type-check an efficiently retrievable item of this pith.
    if hint_or_sane_child is not None:
        # Hint sign logic type-checking this sign if any *OR* "None" otherwise.
        hint_sign_logic = (
            HINT_SIGN_PEP484585_CONTAINER_ARGS_1_TO_LOGIC_get(hint_sign))

        # If *NO* hint sign logic type-checks this sign, raise an exception.
        # Note that this logic should *ALWAYS* be non-"None". Nonetheless,
        # assumptions make a donkey.
        if hint_sign_logic is None:  # pragma: no cover
            raise BeartypeDecorHintPepException(
                f'{exception_prefix}'
                f'1-argument container type hint {repr(hint)} '
                f'beartype sign {repr(hint_sign)} '
                f'code generation logic not found.'
            )
        # Else, some hint sign logic type-checks this sign.

        # Python expression deeply type-checking this pith against this hint.
        func_curr_code = hint_sign_logic.make_code(
            hint_meta=hint_meta,
            hints_meta=hints_meta,
            hint_curr_expr=hint_curr_expr,
            hint_or_sane_child=hint_or_sane_child,
            pith_curr_assign_expr=pith_curr_assign_expr,
            pith_curr_var_name_index=pith_curr_var_name_index,
        )

        # Record whether this expression requires a pseudo-random integer.
        is_var_random_int_needed = hint_sign_logic.is_var_random_int_needed
    # Else, this child hint is ignorable. In this case, fallback to trivial code
    # shallowly type-checking this pith as an instance of this origin type.

    # ....................{ RETURN                         }....................
    # Return this Python code snippet.
    return (func_curr_code, hint_curr_expr, is_var_random_int_needed)
