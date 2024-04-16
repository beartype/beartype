#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2024 Beartype authors.
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

# ....................{ IMPORTS                            }....................
from beartype.roar import (
    BeartypeDecorHintParamDefaultForwardRefWarning,
    BeartypeDecorHintParamDefaultViolation,
    BeartypeDecorHintPepException,
    BeartypeDecorParamNameException,
)
from beartype.roar._roarexc import _BeartypeHintForwardRefExceptionMixin
from beartype._check.checkcall import BeartypeCall
from beartype._check.checkmake import make_code_raiser_func_pith_check
from beartype._check.convert.convsanify import sanify_hint_root_func
from beartype._conf.confcls import BeartypeConf
from beartype._data.error.dataerrmagic import EXCEPTION_PLACEHOLDER
from beartype._data.func.datafuncarg import ARG_NAME_RETURN
from beartype._decor.wrap.wrapsnip import (
    CODE_INIT_ARGS_LEN,
    EXCEPTION_PREFIX_DEFAULT,
    ARG_KIND_TO_CODE_LOCALIZE,
)
from beartype._decor.wrap._wraputil import unmemoize_func_wrapper_code
from beartype._util.error.utilerrraise import reraise_exception_placeholder
from beartype._util.error.utilerrwarn import (
    issue_warning,
    reissue_warnings_placeholder,
)
from beartype._util.func.arg.utilfuncargiter import (
    ARG_META_INDEX_DEFAULT,
    ARG_META_INDEX_KIND,
    ARG_META_INDEX_NAME,
    ArgKind,
    ArgMandatory,
    iter_func_args,
)
from beartype._util.hint.utilhinttest import (
    is_hint_ignorable,
    is_hint_needs_cls_stack,
)
from beartype._util.kind.map.utilmapset import update_mapping
from beartype._util.text.utiltextmunge import lowercase_str_char_first
from beartype._util.text.utiltextprefix import (
    prefix_callable_arg_name,
    prefix_pith_value,
)
from beartype._util.utilobject import SENTINEL
from warnings import catch_warnings

# ....................{ CODERS                             }....................
def code_check_args(bear_call: BeartypeCall) -> str:
    '''
    Generate a Python code snippet type-checking all annotated parameters of
    the decorated callable if any *or* the empty string otherwise (i.e., if
    these parameters are unannotated).

    Parameters
    ----------
    bear_call : BeartypeCall
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
    assert isinstance(bear_call, BeartypeCall), (
        f'{repr(bear_call)} not beartype call.')

    # ..................{ LOCALS ~ func                      }..................
    # If *NO* callable parameters are annotated, silently reduce to a noop.
    #
    # Note that this is purely an optimization short-circuit mildly improving
    # efficiency for the common case of callables accepting either no
    # parameters *OR* one or more parameters, all of which are unannotated.
    if (
        # That callable is annotated by only one type hint *AND*...
        len(bear_call.func_arg_name_to_hint) == 1 and
        # That type hint annotates that callable's return rather than a
        # parameter accepted by that callable...
        ARG_NAME_RETURN in bear_call.func_arg_name_to_hint
    ):
        return ''
    # Else, one or more callable parameters are annotated.

    # Python code snippet to be returned.
    func_wrapper_code = ''

    # ..................{ LOCALS ~ parameter                 }..................
    #FIXME: Remove this *AFTER* optimizing signature generation, please.
    # True only if this callable possibly accepts one or more positional
    # parameters.
    is_args_positional = False

    # ..................{ LOCALS ~ hint                      }..................
    # Type hint annotating the current parameter if any *OR* "_PARAM_HINT_EMPTY"
    # otherwise (i.e., if this parameter is unannotated).
    hint_insane = None

    # This type hint sanitized into a possibly different type hint more readily
    # consumable by @beartype's code generator.
    hint = None

    # ..................{ GENERATE                           }..................
    #FIXME: Locally remove the "arg_index" local variable (and thus avoid
    #calling the enumerate() builtin here) AFTER* refactoring @beartype to
    #generate callable-specific wrapper signatures.

    # For the 0-based index of each parameter accepted by this callable and the
    # "ParameterMeta" object describing this parameter (in declaration order)...
    for arg_index, arg_meta in enumerate(iter_func_args(
        # Possibly lowest-level wrappee underlying the possibly higher-level
        # wrapper currently being decorated by the @beartype decorator. The
        # latter typically fails to convey the same callable metadata conveyed
        # by the former -- including the names and kinds of parameters accepted
        # by the possibly unwrapped callable. This renders the latter mostly
        # useless for our purposes.
        func=bear_call.func_wrappee_wrappee,
        func_codeobj=bear_call.func_wrappee_wrappee_codeobj,
        is_unwrap=False,
    )):
        # Kind and name of this parameter.
        arg_kind: ArgKind = arg_meta[ARG_META_INDEX_KIND]  # type: ignore[assignment]
        arg_name: str = arg_meta[ARG_META_INDEX_NAME]  # type: ignore[assignment]

        # Default value of this parameter if this parameter is optional *OR* the
        # "ArgMandatory" singleton otherwise (i.e., if this parameter is
        # mandatory).
        arg_default: object = arg_meta[ARG_META_INDEX_DEFAULT]

        # Type hint annotating this parameter if any *OR* the sentinel
        # placeholder otherwise (i.e., if this parameter is unannotated).
        #
        # Note that "None" is a semantically meaningful PEP 484-compliant type
        # hint equivalent to "type(None)". Ergo, we *MUST* explicitly
        # distinguish between that type hint and unannotated parameters.
        hint_insane = bear_call.func_arg_name_to_hint_get(arg_name, SENTINEL)

        # If this parameter is unannotated, continue to the next parameter.
        if hint_insane is SENTINEL:
            continue
        # Else, this parameter is annotated.

        # Attempt to...
        try:
            # With a context manager "catching" *ALL* non-fatal warnings emitted
            # during this logic for subsequent "playrback" below...
            with catch_warnings(record=True) as warnings_issued:
                # If this parameter's name is reserved for use by the @beartype
                # decorator, raise an exception.
                if arg_name.startswith('__bear'):
                    raise BeartypeDecorParamNameException(
                        f'{EXCEPTION_PLACEHOLDER}reserved by @beartype.')
                # If either the type of this parameter is silently ignorable,
                # continue to the next parameter.
                elif arg_kind in _ARG_KINDS_IGNORABLE:
                    continue
                # Else, this parameter is non-ignorable.

                # Sanitize this hint into a possibly different type hint more
                # readily consumable by @beartype's code generator *BEFORE*
                # passing this hint to any further callables.
                hint = sanify_hint_root_func(
                    hint=hint_insane, pith_name=arg_name, bear_call=bear_call)

                # If this hint is ignorable, continue to the next parameter.
                #
                # Note that this is intentionally tested *AFTER* this hint has
                # been coerced into a PEP-compliant type hint to implicitly
                # ignore PEP-noncompliant type hints as well (e.g., "(object,
                # int, str)").
                if is_hint_ignorable(hint):
                    # print(f'Ignoring {bear_call.func_name} parameter {arg_name} hint {repr(hint)}...')
                    continue
                # Else, this hint is unignorable.

                #FIXME: Fundamentally unsafe and thus temporarily disabled *FOR
                #THE MOMENT.* The issue is that our current implementation of
                #the is_bearable() tester internally called by this function
                #refuses to resolve relative forward references -- which is
                #obviously awful. Ideally, that tester *ABSOLUTELY* should
                #resolve relative forward references. Until it does, however,
                #this is verboten dark magic that is unsafe in the general case.
                #FIXME: Note that there exist even *MORE* edge cases, however:
                #@dataclass fields, which violate typing semantics: e.g.,
                #    from dataclasses import dataclass, field
                #    from typing import Dict
                #
                #    from beartype import beartype
                #
                #    @beartype
                #    @dataclass
                #    class A:
                #        test_dict: Dict[str, str] = field(default_factory=dict)
                #FIXME: Once this has been repaired, please reenable:
                #* The "test_decor_arg_kind_flex_optional" unit test.

                # # If this parameter is optional *AND* the default value of this
                # # optional parameter violates this hint, raise an exception.
                # _die_if_arg_default_unbearable(
                #     bear_call=bear_call, arg_default=arg_default, hint=hint)
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

                # Type stack if required by this hint *OR* "None" otherwise. See
                # the is_hint_needs_cls_stack() tester for further discussion.
                #
                # Note that the original unsanitized "hint_insane" (e.g.,
                # "typing.Self") rather than the new sanitized "hint" (e.g., the
                # class currently being decorated by @beartype) is passed to
                # that tester. Why? Because the latter may already have been
                # reduced above to a different (and seemingly innocuous) type
                # hint that does *NOT* appear to require a type stack at late
                # *EXCEPTION RAISING TIME* (i.e., the
                # beartype._check.error.errorget.get_func_pith_violation()
                # function) but actually does. Only the original unsanitized
                # "hint_insane" is truth.
                cls_stack = (
                    bear_call.cls_stack
                    # if is_hint_needs_cls_stack(hint) else
                    if is_hint_needs_cls_stack(hint_insane) else
                    None
                )
                # print(f'arg "{arg_name}" hint {repr(hint)} cls_stack: {repr(cls_stack)}')

                # Code snippet type-checking *ANY* parameter with *ANY*
                # arbitrary name.
                (
                    code_arg_check_pith,
                    func_scope,
                    hint_refs_type_basename,
                ) = make_code_raiser_func_pith_check(
                    hint,
                    bear_call.conf,
                    cls_stack,
                    True,  # <-- True only for parameters
                )

                # Merge the local scope required to check this parameter into
                # the local scope currently required by the current wrapper
                # function.
                update_mapping(bear_call.func_wrapper_scope, func_scope)

                # Python code snippet localizing this parameter.
                code_arg_localize = ARG_LOCALIZE_TEMPLATE.format(
                    arg_name=arg_name, arg_index=arg_index)

                # Unmemoize this snippet against the current parameter.
                code_arg_check = unmemoize_func_wrapper_code(
                    bear_call=bear_call,
                    func_wrapper_code=code_arg_check_pith,
                    pith_repr=repr(arg_name),
                    hint_refs_type_basename=hint_refs_type_basename,
                )

                # Append code type-checking this parameter against this hint.
                func_wrapper_code += f'{code_arg_localize}{code_arg_check}'

            # If one or more warnings were issued, reissue these warnings with
            # each placeholder substring (i.e., "EXCEPTION_PLACEHOLDER"
            # instance) replaced by a human-readable description of this
            # callable and annotated parameter.
            if warnings_issued:
                # print(f'warnings_issued: {warnings_issued}')
                reissue_warnings_placeholder(
                    warnings=warnings_issued,
                    target_str=prefix_callable_arg_name(
                        func=bear_call.func_wrappee,
                        arg_name=arg_name,
                        is_color=bear_call.conf.is_color,
                    ),
                )
            # Else, *NO* warnings were issued.
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
                #prefix_callable_arg_name() function to introspect this kind from
                #the callable code object.
                target_str=prefix_callable_arg_name(
                    func=bear_call.func_wrappee,
                    arg_name=arg_name,
                    is_color=bear_call.conf.is_color,
                ),
            )

    # If this callable accepts one or more positional type-checked parameters,
    # prefix this code by a snippet localizing the number of these parameters.
    if is_args_positional:
        func_wrapper_code = f'{CODE_INIT_ARGS_LEN}{func_wrapper_code}'
    # Else, this callable accepts *NO* positional type-checked parameters. In
    # this case, preserve this code as is.

    # Return this code.
    return func_wrapper_code

# ....................{ PRIVATE ~ constants                }....................
#FIXME: Remove this set *AFTER* handling these kinds of parameters.
_ARG_KINDS_IGNORABLE = frozenset((
    ArgKind.VAR_KEYWORD,
))
'''
Frozen set of all :attr:`ArgKind` enumeration members to be ignored
during annotation-based type checking in the :func:`beartype.beartype`
decorator.

This includes:

* Constants specific to variadic keyword parameters (e.g., ``**kwargs``), which
  are currently unsupported by :func:`beartype`.
* Constants specific to positional-only parameters, which apply only to
  non-pure-Python callables (e.g., defined by C extensions). The
  :func:`beartype` decorator applies *only* to pure-Python callables, which
  provide no syntactic means for specifying positional-only parameters.
'''


_ARG_KINDS_POSITIONAL = frozenset((
    ArgKind.POSITIONAL_ONLY,
    ArgKind.POSITIONAL_OR_KEYWORD,
))
'''
Frozen set of all **positional parameter kinds** (i.e.,
:attr:`ArgKind` enumeration members signifying that a callable parameter
either may *or* must be passed positionally).
'''

# ....................{ PRIVATE ~ raisers                  }....................
def _die_if_arg_default_unbearable(
    bear_call: BeartypeCall, arg_default: object, hint: object) -> None:
    '''
    Raise a violation exception if the annotated optional parameter of the
    decorated callable with the passed default value violates the type hint
    annotating that parameter at decoration time.

    Parameters
    ----------
    bear_call : BeartypeCall
        Decorated callable to be type-checked.
    arg_default : object
        Either:

        * If this parameter is mandatory, the :data:`.ArgMandatory` singleton.
        * If this parameter is optional, the default value of this optional
          parameter to be type-checked.
    hint : object
        Type hint to type-check against this default value.

    Warns
    -----
    BeartypeDecorHintParamDefaultForwardRefWarning
        If this type hint contains one or more forward references that *cannot*
        be resolved at decoration time. While this does *not* necessarily
        constitute a fatal error from the end user perspective, this does
        constitute a non-fatal issue worth informing the end user of.

    Raises
    ------
    BeartypeDecorHintParamDefaultViolation
        If this default value violates this type hint.
    '''

    # ..................{ PREAMBLE                           }..................
    # If this parameter is mandatory, silently reduce to a noop.
    if arg_default is ArgMandatory:
        return
    # Else, this parameter is optional and thus defaults to a default value.

    assert isinstance(bear_call, BeartypeCall), (
        f'{repr(bear_call)} not beartype call.')

    # ..................{ IMPORTS                            }..................
    # Defer heavyweight imports prohibited at global scope.
    from beartype.door import (
        die_if_unbearable,
        is_bearable,
    )

    # ..................{ MAIN                               }..................
    # Attempt to...
    try:
        # If this default value satisfies this hint, silently reduce to a noop.
        #
        # Note that this is a non-negligible optimization. Technically, this
        # preliminary test is superfluous: only the call to the
        # die_if_unbearable() raiser below is required. Pragmatically, this
        # preliminary test avoids a needlessly expensive dictionary copy in the
        # common case that this value satisfies this hint.
        if is_bearable(
            obj=arg_default,
            hint=hint,
            conf=bear_call.conf,
        ):
            return
        # Else, this default value violates this hint.
    # If doing so raises a forward hint exception, this hint contains one or
    # more unresolvable forward references to user-defined objects that have yet
    # to be defined. In all likelihood, these objects are subsequently defined
    # after the definition of this decorated callable. While this does *NOT*
    # necessarily constitute a fatal error from the end user perspective, this
    # does constitute a non-fatal issue worth informing the end user of. In this
    # case, we coerce this exception into a warning.
    except _BeartypeHintForwardRefExceptionMixin as exception:
        # Forward hint exception message raised above. To readably embed this
        # message in the longer warning message emitted below, the first
        # character of this message is lowercased as well.
        exception_message = lowercase_str_char_first(str(exception))

        # Emit this non-fatal warning.
        issue_warning(
            cls=BeartypeDecorHintParamDefaultForwardRefWarning,
            message=(
                f'{EXCEPTION_PREFIX_DEFAULT}value '
                f'{prefix_pith_value(pith=arg_default, is_color=bear_call.conf.is_color)}'
                f'uncheckable at @beartype decoration time, as '
                f'{exception_message}'
            ),
        )

        # Loudly reduce to a noop. Since this forward reference is unresolvable,
        # further type-checking attempts are entirely fruitless.
        return

    # Modifiable keyword dictionary encapsulating this beartype configuration.
    conf_kwargs = bear_call.conf.kwargs.copy()

    #FIXME: This should probably be configurable as well. For now, this is fine.
    #We shrug noncommittally. We shrug, everyone! *shrug*
    # Set the type of violation exception raised by the subsequent call to the
    # die_if_unbearable() function to the expected type.
    conf_kwargs['violation_door_type'] = BeartypeDecorHintParamDefaultViolation

    # New beartype configuration initialized by this dictionary.
    conf = BeartypeConf(**conf_kwargs)

    # Raise this type of violation exception.
    die_if_unbearable(
        obj=arg_default,
        hint=hint,
        conf=conf,
        exception_prefix=EXCEPTION_PREFIX_DEFAULT,
    )
