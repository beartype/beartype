#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2024 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype decorator return code generator** (i.e., low-level callables
dynamically generating Python expressions type-checking the annotated return of
the callable currently being decorated by the :func:`beartype.beartype`
decorator in a general-purpose manner).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.typing import NoReturn
from beartype._check.checkcall import BeartypeCall
from beartype._check.checkmake import (
    make_code_raiser_func_pith_check,
    make_code_raiser_func_pep484_noreturn_check,
)
from beartype._check.convert.convsanify import sanify_hint_root_func
from beartype._data.func.datafuncarg import (
    ARG_NAME_RETURN,
    ARG_NAME_RETURN_REPR,
)
from beartype._data.hint.datahinttyping import LexicalScope
from beartype._decor.wrap.wrapsnip import (
    CODE_RETURN_CHECK_PREFIX,
    CODE_RETURN_CHECK_SUFFIX,
    PEP484_CODE_CHECK_NORETURN,
)
from beartype._decor.wrap._wraputil import unmemoize_func_wrapper_code
from beartype._util.error.utilerrraise import reraise_exception_placeholder
from beartype._util.error.utilerrwarn import reissue_warnings_placeholder
from beartype._util.hint.utilhinttest import (
    is_hint_ignorable,
    is_hint_needs_cls_stack,
)
from beartype._util.kind.map.utilmapset import update_mapping
from beartype._util.text.utiltextprefix import prefix_callable_return
from beartype._util.utilobject import SENTINEL
from warnings import catch_warnings

# ....................{ CODERS                             }....................
def code_check_return(bear_call: BeartypeCall) -> str:
    '''
    Generate a Python code snippet type-checking the annotated return declared
    by the decorated callable if any *or* the empty string otherwise (i.e., if
    this return is unannotated).

    Parameters
    ----------
    bear_call : BeartypeCall
        Decorated callable to be type-checked.

    Returns
    -------
    str
        Code type-checking any annotated return of the decorated callable.

    Raises
    ------
    BeartypeDecorHintPep484585Exception
        If this callable is either:

        * A coroutine *not* annotated by a :obj:`typing.Coroutine` type hint.
        * A generator *not* annotated by a :obj:`typing.Generator` type hint.
        * An asynchronous generator *not* annotated by a
          :obj:`typing.AsyncGenerator` type hint.
    BeartypeDecorHintNonpepException
        If the type hint annotating this return (if any) of this callable is
        neither:

        * **PEP-compliant** (i.e., :mod:`beartype`-agnostic hint compliant with
          annotation-centric PEPs).
        * **PEP-noncompliant** (i.e., :mod:`beartype`-specific type hint *not*
          compliant with annotation-centric PEPs)).
    '''
    assert isinstance(bear_call, BeartypeCall), (
        f'{repr(bear_call)} not beartype call.')

    # Type hint annotating this callable's return if any *OR* "SENTINEL"
    # otherwise (i.e., if this return is unannotated).
    #
    # Note that "None" is a semantically meaningful PEP 484-compliant type hint
    # equivalent to "type(None)". Ergo, we *MUST* explicitly distinguish
    # between that type hint and an unannotated return.
    hint = bear_call.func_arg_name_to_hint_get(ARG_NAME_RETURN, SENTINEL)

    # If this return is unannotated, silently reduce to a noop.
    if hint is SENTINEL:
        return ''
    # Else, this return is annotated.

    # Python code snippet to be returned, defaulting to the empty string
    # implying this callable's return to either be unannotated *OR* annotated by
    # a safely ignorable type hint.
    func_wrapper_code = ''

    # Lexical scope (i.e., dictionary mapping from the relative unqualified name
    # to value of each locally or globally scoped attribute accessible to a
    # callable or class), initialized to "None" for safety.
    func_scope: LexicalScope = None  # type: ignore[assignment]

    # Attempt to...
    try:
        # With a context manager "catching" *ALL* non-fatal warnings emitted
        # during this logic for subsequent "playrback" below...
        with catch_warnings(record=True) as warnings_issued:
            # Preserve the original unsanitized type hint for subsequent
            # reference *BEFORE* sanitizing this type hint.
            hint_insane = hint

            # Sanitize this hint to either:
            # * If this hint is PEP-noncompliant, the PEP-compliant type hint
            #   converted from this PEP-noncompliant type hint.
            # * If this hint is PEP-compliant and supported, this hint as is.
            # * Else, raise an exception.
            #
            # Do this first *BEFORE* passing this hint to any further callables.
            hint = sanify_hint_root_func(
                hint=hint, pith_name=ARG_NAME_RETURN, bear_call=bear_call)
            # print(f'Sanified {repr(bear_call.func_wrappee)} return hint {repr(hint_insane)} to {repr(hint)}...')

            # If this is the PEP 484-compliant "typing.NoReturn" type hint
            # permitted *ONLY* as a return annotation...
            if hint is NoReturn:
                # Pre-generated code snippet validating this callable to *NEVER*
                # successfully return by unconditionally generating a violation.
                code_noreturn_check = PEP484_CODE_CHECK_NORETURN.format(
                    func_call_prefix=bear_call.func_wrapper_code_call_prefix)

                # Code snippet handling the previously generated violation by
                # either raising that violation as a fatal exception or emitting
                # that violation as a non-fatal warning.
                (
                    code_noreturn_violation,
                    func_scope,
                    _
                ) = make_code_raiser_func_pep484_noreturn_check(bear_call.conf)

                # Full code snippet to be returned.
                func_wrapper_code = (
                    f'{code_noreturn_check}{code_noreturn_violation}')
            # Else, this is *NOT* "typing.NoReturn". In this case...
            else:
                # If this PEP-compliant hint is unignorable, generate and return
                # a snippet type-checking this return against this hint.
                if not is_hint_ignorable(hint):
                    # Type stack if required by this hint *OR* "None" otherwise.
                    # See is_hint_needs_cls_stack() for details.
                    #
                    # Note that the original unsanitized "hint_insane" (e.g.,
                    # "typing.Self") rather than the new sanitized "hint" (e.g.,
                    # the class currently being decorated by @beartype) is
                    # passed to that tester. See _code_check_args() for details.
                    cls_stack = (
                        bear_call.cls_stack
                        if is_hint_needs_cls_stack(hint_insane) else
                        None
                    )
                    # print(f'return hint {repr(hint_insane)} -> {repr(hint)} cls_stack: {repr(cls_stack)}')

                    # Empty tuple, passed below to satisfy the
                    # _unmemoize_func_wrapper_code() API.
                    hint_refs_type_basename = ()

                    # Code snippet type-checking any arbitrary return.
                    (
                        code_return_check_pith,
                        func_scope,
                        hint_refs_type_basename,
                    ) = make_code_raiser_func_pith_check(  # type: ignore[assignment]
                        hint,
                        bear_call.conf,
                        cls_stack,
                        False,  # <-- True only for parameters
                    )

                    # Unmemoize this snippet against this return.
                    code_return_check = unmemoize_func_wrapper_code(
                        bear_call=bear_call,
                        func_wrapper_code=code_return_check_pith,
                        pith_repr=ARG_NAME_RETURN_REPR,
                        hint_refs_type_basename=hint_refs_type_basename,
                    )

                    #FIXME: [SPEED] Optimize the following two string munging
                    #operations into a single string-munging operation resembling:
                    #    func_wrapper_code = CODE_RETURN_CHECK.format(
                    #        func_call_prefix=bear_call.func_wrapper_code_call_prefix,
                    #        check_expr=code_return_check_pith_unmemoized,
                    #    )
                    #
                    #Then define "CODE_RETURN_CHECK" in the "wrapsnip" submodule to
                    #resemble:
                    #    CODE_RETURN_CHECK = (
                    #        f'{CODE_RETURN_CHECK_PREFIX}{{check_expr}}'
                    #        f'{CODE_RETURN_CHECK_SUFFIX}'
                    #    )

                    # Code snippet type-checking this return.
                    code_return_check_prefix = CODE_RETURN_CHECK_PREFIX.format(
                        func_call_prefix=(
                            bear_call.func_wrapper_code_call_prefix))

                    # Full code snippet to be returned, consisting of:
                    # * Calling the decorated callable and localize its return
                    #   *AND*...
                    # * Type-checking this return *AND*...
                    # * Returning this return from this wrapper function.
                    func_wrapper_code = (
                        f'{code_return_check_prefix}'
                        f'{code_return_check}'
                        f'{CODE_RETURN_CHECK_SUFFIX}'
                    )
                # Else, this hint is ignorable.
                # if not func_wrapper_code: print(f'Ignoring {bear_call.func_name} return hint {repr(hint)}...')
        # If one or more warnings were issued, reissue these warnings with each
        # placeholder substring (i.e., "EXCEPTION_PLACEHOLDER" instance)
        # replaced by a human-readable description of this callable and
        # annotated return.
        if warnings_issued:
            reissue_warnings_placeholder(
                warnings=warnings_issued,
                target_str=prefix_callable_return(
                    func=bear_call.func_wrappee,
                    is_color=bear_call.conf.is_color,
                ),
            )
        # Else, *NO* warnings were issued.
    # If any exception was raised, reraise this exception with each placeholder
    # substring (i.e., "EXCEPTION_PLACEHOLDER" instance) replaced by a
    # human-readable description of this callable and annotated return.
    except Exception as exception:
        reraise_exception_placeholder(
            exception=exception,
            target_str=prefix_callable_return(
                func=bear_call.func_wrappee,
                is_color=bear_call.conf.is_color,
            ),
        )

    # If a local scope is required to type-check this return, merge this scope
    # into the local scope currently required by the current wrapper function.
    if func_scope:
        update_mapping(bear_call.func_wrapper_scope, func_scope)
    # Else, *NO* local scope is required to type-check this return.

    # Return this code.
    return func_wrapper_code
