#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype decorator parameter code generator** (i.e., low-level callables
dynamically generating Python expressions type-checking all annotated parameters
of the callable currently being decorated by the :func:`beartype.beartype`
decorator in a general-purpose manner).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ TODO                               }....................
# All "FIXME:" comments for this submodule reside in this package's "__init__"
# submodule to improve maintainability and readability here.

#FIXME: [SPEED] We currently generate non-optimal type-checking code for
#*MANDATORY* parameters. *OPTIONAL* parameters seem fine. Sadly, mandatory are
#more common. We appear to be unconditionally generating the following code for
#*ALL* parameters, regardless of whether that parameter is mandatory or not:
#    (line 0015)     # Localize this positional or keyword parameter if passed *OR* to the
#    (line 0016)     # sentinel "__beartype_get_violation" guaranteed to never be passed.
#    (line 0017)     __beartype_pith_0 = (
#    (line 0018)         args[0] if __beartype_args_len > 0 else
#    (line 0019)         kwargs.get('two_fair_argent_wings', __beartype_get_violation)
#    (line 0020)     )
#    (line 0021)
#    (line 0022)     # If this parameter was passed...
#    (line 0023)     if __beartype_pith_0 is not __beartype_get_violation:
#    (line 0024)         # Type-check this parameter or return against this type hint.
#    (line 0025)         if not ...
#
#If the current parameter is mandatory, the first "if" conditional is a
#superfluous waste of time. Obviously, a mandatory parameter is *ALWAYS* passed.
#That needn't be tested. Ergo, the above code should instead reduce to the
#following for a mandatory parameter:
#    (line 0015)     # Localize this positional or keyword parameter if passed *OR* to the
#    (line 0016)     # sentinel "__beartype_get_violation" guaranteed to never be passed.
#    (line 0017)     __beartype_pith_0 = (
#    (line 0018)         args[0] if __beartype_args_len > 0 else
#    (line 0019)         kwargs['two_fair_argent_wings']
#    (line 0020)     )
#    (line 0021)
#    (line 0022)     # Type-check this parameter or return against this type hint.
#    (line 0023)     if not ...
#
#Critically, note that the optimized code generated for mandatory parameters
#features two distinct changes:
#1. Efficient direct parameter lookup in the "kwargs" dictionary via "["- and
#   "]"-delimited syntax rather than less efficient indirect parameter lookup
#   via a kwargs.get() call. Efficiency isn't really the concern here (although
#   it does matter, of course). Strictness is the concern. A mandatory parameter
#   absolutely *MUST* be passed. If that isn't the case, a low-level CPython
#   exception *MUST* be raised. Actually... *WAIT*. Issues arise here. Notably:
#   * Because our type-checking wrapper functions only currently accept variadic
#     "*args, **kwargs" parameters, the exception raised by directly accessing
#     "kwargs['two_fair_argent_wings']" if the caller failed to pass that
#     parameter will basically be useless, unreadable, and awful. Welp. That's
#     it, folks! That's a critical deal-breaker. No wonder we embraced the
#     current approach, huh? We can't go ahead with this optimization until we
#     implement our long-overdue refactoring where we generate type-checking
#     wrapper functions whose signatures *PERFECTLY* mirror those of the
#     original underlying callables they wrap. Until then, this is a no-go, bro!

# ....................{ IMPORTS                            }....................
from beartype.roar import (
    BeartypeDecorHintPepException,
    BeartypeDecorParamNameException,
)
from beartype._check.make.checkmakefunc import make_code_raiser_func_pith_check
from beartype._check.convert.convmain import sanify_hint_root_func
from beartype._check.cls.call.calldatadecorfunc import (
    BeartypeCallDecorFuncData,
    prefix_decor_func_callable_arg_name,
)
from beartype._check.cls.hint.hintsane import (
    HINT_SANE_IGNORABLE,
    HintSane,
)
from beartype._data.check.code.datacodename import ARG_NAME_ARGS_NAME_KEYWORDABLE
from beartype._data.check.code.func.datacodefuncwrap import (
    CODE_INIT_ARGS_LEN,
    ARG_KIND_TO_CODE_LOCALIZE,
)
from beartype._data.check.error.dataerrmagic import EXCEPTION_PLACEHOLDER
from beartype._data.func.datafuncarg import ARG_NAME_RETURN
from beartype._data.typing.datatyping import LexicalScope
from beartype._data.typing.datatypingport import Hint
from beartype._util.error.utilerrraise import reraise_exception_placeholder
from beartype._util.error.utilerrwarn import reissue_warnings_placeholder
from beartype._util.func.arg.utilfuncargiter import (
    ArgKind,
    iter_func_args,
)
from beartype._util.func.arg.utilfuncargtest import is_func_arg_variadic_keyword
from beartype._util.kind.maplike.utilmapset import update_mapping
from beartype._data.kind.datakindiota import SENTINEL
from collections.abc import MutableSet
from typing import Optional
from warnings import catch_warnings

# ....................{ CODERS                             }....................
def code_check_args(decor_func: BeartypeCallDecorFuncData) -> str:
    '''
    Generate a Python code snippet type-checking all annotated parameters of the
    decorated callable if any *or* the empty string otherwise (i.e., if these
    parameters are unannotated).

    Parameters
    ----------
    decor_func : BeartypeCallDecorFuncData
        Decorated callable to be type-checked.

    Returns
    -------
    str
        Code type-checking all annotated parameters of the decorated callable.

    Raises
    ------
    BeartypeDecorParamNameException
        If the name of any parameter declared on this callable is prefixed by
        the reserved substring ``__bear``.
    BeartypeDecorHintNonpepException
        If any type hint annotating any parameter of this callable is neither:

        * A PEP-noncompliant type hint.
        * A supported PEP-compliant type hint.
    '''
    assert isinstance(decor_func, BeartypeCallDecorFuncData), (
        f'{repr(decor_func)} not beartype decorator call metadata.')

    # ..................{ LOCALS ~ func                      }..................
    # If *NO* callable parameters are annotated, silently reduce to a noop.
    #
    # Note that this is purely an optimization short-circuit mildly improving
    # efficiency for the common case of callables accepting either no
    # parameters *OR* one or more parameters, all of which are unannotated.
    if (
        # That callable is annotated by exactly one type hint *AND*...
        len(decor_func.decoratee_annotations) == 1 and
        # That type hint annotates that callable's return rather than a
        # parameter accepted by that callable...
        ARG_NAME_RETURN in decor_func.decoratee_annotations
    ):
        return ''
    # Else, one or more callable parameters are annotated.

    # Python code snippet to be returned, defaulting to the empty string
    # implying this callable's parameters to all either be unannotated *OR*
    # annotated only by safely ignorable type hints.
    func_wrapper_code = ''

    # Lexical scope (i.e., dictionary mapping from the relative unqualified name
    # to value of each locally or globally scoped attribute accessible to a
    # callable or class), initialized to "None" for safety.
    func_scope: LexicalScope = None  # type: ignore[assignment]

    # ..................{ LOCALS ~ parameter                 }..................
    #FIXME: Remove this *AFTER* optimizing signature generation, please.
    # True only if that callable possibly accepts one or more positional
    # parameters.
    is_args_positional = False

    #FIXME: ******UNIT TEST US UP, PLEASE.******* Do so exhaustively until
    #exhausted. This is super-critical. Yo!
    #FIXME: Remove the "args_name_keywordable" local variable and associated
    #"ARG_NAME_ARGS_NAME_KEYWORDABLE" global variable *AFTER* refactoring
    #@beartype to generate callable-specific wrapper signatures.

    # Either...
    args_name_keywordable: Optional[MutableSet[str]] = (
        #FIXME: [SPEED] Minor optimization. If the decorated callable *ONLY*
        #accepts an annotated variadic keyword parameter and no other
        #parameters, then the empty set reused from a global "SET_EMPTY" import
        #suffices here. Probably. Consider, anyway. *sigh*
        # If the decorated callable accepts an annotated variadic keyword
        # parameter (e.g., "**kwargs: int"), the set of the names of all
        # keywordable parameters (i.e., parameters that may be passed by
        # keyword), defined as the union of the:
        # * Set of the names of all flexible parameters (i.e., parameters that
        #   may be passed either positionally or by keyword).
        # * Set of the names of all keyword-only parameters.
        #
        # This set is required in the body of the type-checking function
        # wrapping the decorated callable to differentiate between:
        # * Keyword parameters explicitly accepted by the decorated callable,
        #   which are trivially type-checked by existing logic.
        # * Keyword parameters *NOT* explicitly accepted by the decorated
        #   callable and thus implicitly accepted only as excess keyword
        #   parameters added by CPython itself to the annotated variadic keyword
        #   parameter (e.g., "**kwargs: int") accepted by the decorated
        #   callable. Excess keyword parameters *CANNOT* be trivially
        #   type-checked by existing logic, due to the non-triviality of
        #   deciding whether a keyword parameter even is "excess" or not.
        set()
        if is_func_arg_variadic_keyword(
            # See the call to the iter_func_args() generator function below for
            # further commentary on these parameters.
            func=decor_func.func_wrappee_wrappee, is_unwrap=False) else
        # Else, "None".
        None
    )

    # ..................{ LOCALS ~ hint                      }..................
    # Possibly insane hint annotating the current parameter if any *OR* the
    # sentinel placeholder otherwise (i.e., if this parameter is unannotated).
    hint_insane: Hint = None  # type: ignore[assignment]

    # Sanified hint metadata annotating the current parameter, sanified from
    # this possibly insane hint.
    hint_sane: HintSane = None  # type: ignore[assignment]

    # ..................{ GENERATE                           }..................
    # Kind and name of this parameter.
    arg_kind: ArgKind = None  # type: ignore[assignment]
    arg_name: str     = None  # type: ignore[assignment]

    # Default value of this parameter if this parameter is optional *OR* the
    # "ArgMandatory" singleton otherwise (i.e., if this parameter is mandatory).
    arg_default: object = None

    # For the 0-based index of each parameter accepted by that callable and the
    # "ArgKindNameDefault" 3-tuple describing this parameter (in declaration order)...
    #
    # Note that:
    # * While bizarre, this syntax is the accepted Pythonic idiom for iterating
    #   over dictionary key-value pairs while both indexing and unpacking those
    #   key-value pairs.
    # * The enumerate() builtin has been profiled to be marginally faster than
    #   manually incrementing the "arg_index" local variable in the body of this
    #   "for" loop. Yeah. We actually checked that. *hangs head*
    for arg_index, (arg_name, (arg_kind, arg_default)) in enumerate(
        decor_func.func_wrappee_wrappee_arg_name_to_kind_default.items()):
        # If...
        if (
            # The set of the names of all keywordable parameters is needed to
            # type-check the decorated callable *AND*...
            args_name_keywordable is not None and
            # This parameter is keywordable...
            arg_kind in _ARG_KINDS_KEYWORD
        ):
            # Add the name of this parameter to this set.
            args_name_keywordable.add(arg_name)
        # Else, this parameter *CANNOT* be passed by keyword.

        # Type hint annotating this parameter if any *OR* the sentinel
        # placeholder otherwise (i.e., if this parameter is unannotated).
        #
        # Note that "None" is a semantically meaningful PEP 484-compliant type
        # hint equivalent to "type(None)". Ergo, we *MUST* explicitly
        # distinguish between that type hint and unannotated parameters.
        hint_insane = decor_func.decoratee_annotations_get(  # type: ignore[assignment]
            arg_name, SENTINEL)

        # If this parameter is unannotated, continue to the next parameter.
        if hint_insane is SENTINEL:
            continue
        # Else, this parameter is annotated.

        # Attempt to...
        try:
            # print(f'Generating code type-checking {decor_func.func_wrapper_name}() parameter "{arg_name}"...')
            # print(f'...unreduced hint {repr(hint_insane)}!')

            # If this parameter's name is reserved for use by the @beartype
            # decorator, raise an exception.
            if arg_name.startswith('__bear'):
                raise BeartypeDecorParamNameException(
                    f'{EXCEPTION_PLACEHOLDER}reserved by @beartype.')
            # Else, this parameter's name is *NOT* reserved for use by the
            # @beartype decorator.

            # With a context manager "catching" *ALL* non-fatal warnings issued
            # during this logic for subsequent "playback" below...
            with catch_warnings(record=True) as warnings_issued:
                # Sane hint sanified from this possibly insane parameter hint if
                # sanifying this hint generated no supplementary metadata *OR*
                # that metadata otherwise. Additionally, if this hint is
                # unsupported by @beartype, raise an exception.
                hint_sane = sanify_hint_root_func(
                    decor_func=decor_func,
                    hint=hint_insane,
                    pith_name=arg_name,
                    arg_kind=arg_kind,
                    exception_prefix=EXCEPTION_PLACEHOLDER,
                )

                # If this hint is ignorable, continue to the next parameter.
                if hint_sane is HINT_SANE_IGNORABLE:
                    # print(f'Ignoring {decor_func.func_name} parameter {arg_name} hint {repr(hint)}...')
                    continue
                # Else, this hint is unignorable.

                #FIXME: Fundamentally unsafe and thus temporarily disabled *FOR
                #THE MOMENT.* @dataclass fields, for example, violate typing
                #semantics: e.g.,
                #    from dataclasses import dataclass, field
                #    from typing import Dict
                #
                #    from beartype import beartype
                #
                #    @beartype
                #    @dataclass
                #    class A:
                #        test_dict: Dict[str, str] = field(default_factory=dict)
                #FIXME: Once this has been repaired, please re-enable:
                #* The "test_decor_arg_kind_flex_optional" unit test.

                # # If this parameter is optional *AND* the default value of this
                # # optional parameter violates this hint, raise an exception.
                # _die_if_arg_default_unbearable(
                #     decor_func=decor_func, arg_default=arg_default, hint=hint)
                # # Else, this parameter is either optional *OR* the default value
                # # of this optional parameter satisfies this hint.

                # If this parameter either may *OR* must be passed positionally,
                # record this fact.
                #
                # Note this conditional branch *MUST* be tested after validating
                # this parameter to be unignorable; if this branch were instead
                # nested *BEFORE* validating this parameter to be unignorable,
                # beartype would fail to reduce to a noop for otherwise
                # ignorable callables -- which would be rather bad, really.
                if arg_kind in _ARG_KINDS_POSITIONAL:
                    is_args_positional = True
                # Else, this parameter *CANNOT* be passed positionally.

                #FIXME: [SPEED] Negligibly optimize the ".get" access away:
                #    ARG_LOCALIZE_TEMPLATE = ARG_KIND_TO_CODE_LOCALIZE_get(  # type: ignore
                #        arg_kind, None)
                # Python code template localizing this parameter if this kind of
                # parameter is supported *OR* "None" otherwise.
                ARG_LOCALIZE_TEMPLATE = ARG_KIND_TO_CODE_LOCALIZE.get(  # type: ignore
                    arg_kind, None)

                # If this kind of parameter is unsupported, raise an exception.
                #
                # Note this edge case should *NEVER* occur, as the parent
                # function should have simply ignored this parameter.
                if ARG_LOCALIZE_TEMPLATE is None:
                    raise BeartypeDecorHintPepException(
                        f'{EXCEPTION_PLACEHOLDER}kind {repr(arg_kind)} '
                        f'currently unsupported by @beartype.'
                    )
                # Else, this kind of parameter is supported. Ergo, this code is
                # non-"None".
                # print(f'Generating code type-checking {decor_func.func_wrapper_name}() parameter "{arg_name}"...')
                # print(f'...reduced hint {repr(hint_sane.hint)}!')

                # Code snippet type-checking any parameter with arbitrary name.
                #
                # Note that this memoized code factory requires parameters to be
                # passed positionally for efficiency.
                (
                    code_arg_check,
                    func_scope,
                ) = make_code_raiser_func_pith_check(
                    decor_func=decor_func,
                    hint_sane=hint_sane,
                    pith_name=arg_name,
                )

                # Python code snippet localizing this parameter.
                code_arg_localize = ARG_LOCALIZE_TEMPLATE.format(
                    arg_name=arg_name, arg_index=arg_index)

                # Append code type-checking this parameter against this hint.
                func_wrapper_code += f'{code_arg_localize}{code_arg_check}'

                # Merge the local scope required to check this parameter into
                # the local scope required by the current wrapper function.
                update_mapping(decor_func.func_wrapper_locals, func_scope)

            # If one or more warnings were issued, reissue these warnings with
            # each placeholder substring (i.e., "EXCEPTION_PLACEHOLDER"
            # instance) replaced by a human-readable description of this
            # callable and annotated parameter.
            if warnings_issued:
                # print(f'warnings_issued: {warnings_issued}')
                reissue_warnings_placeholder(
                    warnings=warnings_issued,
                    target_str=prefix_decor_func_callable_arg_name(
                        decor_func=decor_func, arg_name=arg_name),
                )
            # Else, *NO* warnings were issued.

            # print(f'Generated code type-checking {decor_func.func_wrapper_name}() parameter "{arg_name}"...')
            # print(f'...unreduced hint {repr(hint_insane)}!')
        # If any exception was raised, reraise this exception with each
        # placeholder substring (i.e., "EXCEPTION_PLACEHOLDER" instance)
        # replaced by a human-readable description of this callable and
        # annotated parameter.
        except Exception as exception:
            reraise_exception_placeholder(
                exception=exception,
                #FIXME: Embed the kind of parameter both here and above as well
                #(e.g., "positional-only", "keyword-only", "variadic
                #positional"), ideally by improving the existing
                #prefix_callable_arg_name() function to introspect this kind
                #from the callable code object.
                target_str=prefix_decor_func_callable_arg_name(
                    decor_func=decor_func, arg_name=arg_name),
            )

    # ..................{ RETURN                             }..................
    # If that callable accepts an annotated variadic keyword parameter, expose
    # the set of the names of all keywordable parameters to this wrapper
    # function needed to type-check that annotated variadic keyword parameter.
    if args_name_keywordable is not None:
        decor_func.func_wrapper_locals[ARG_NAME_ARGS_NAME_KEYWORDABLE] = (
            args_name_keywordable)
    # Else, that callable accepts *NO* annotated variadic parameter.

    # If that callable accepts one or more annotated positional parameters,
    # prefix this code by a snippet localizing the number of these parameters.
    if is_args_positional:
        func_wrapper_code = f'{CODE_INIT_ARGS_LEN}{func_wrapper_code}'
    # Else, that callable accepts *NO* annotated positional parameters.

    # Return this code.
    return func_wrapper_code

# ....................{ PRIVATE ~ constants                }....................
#FIXME: Shift these constants into a more appropriate "beartype._data"
#submodule, please. *sigh*
_ARG_KINDS_KEYWORD = frozenset((
    ArgKind.KEYWORD_ONLY,
    ArgKind.POSITIONAL_OR_KEYWORD,
))
'''
Frozen set of all **keyword parameter kinds** (i.e., :attr:`ArgKind` enumeration
members signifying that a callable parameter either may *or* must be passed by
keyword).
'''


_ARG_KINDS_POSITIONAL = frozenset((
    ArgKind.POSITIONAL_ONLY,
    ArgKind.POSITIONAL_OR_KEYWORD,
))
'''
Frozen set of all **positional parameter kinds** (i.e., :class:`.ArgKind`
enumeration members signifying that a callable parameter either may *or* must be
passed positionally).
'''
