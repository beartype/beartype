#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2024 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype **Decidedly Object-Oriented Runtime-checking (DOOR) procedural callable
type hint inferrers** (i.e., lower-level functions dynamically subscripted type
hints describing callable objects).
'''

# ....................{ IMPORTS                            }....................
from beartype.typing import (
    Callable,
    Optional,
)
from beartype._cave._cavefast import (
    HintPep612ParamSpecArgType,
    HintPep612ParamSpecType,
)
from beartype._data.func.datafuncarg import ARG_NAME_RETURN
from beartype._data.hint.pep.sign.datapepsigns import (
    HintSignParamSpecArgs,
    HintSignParamSpecKwargs,
)
from beartype._util.api.utilapityping import (
    import_typing_attr,
    import_typing_attr_or_none,
)
from beartype._util.cache.utilcachecall import callable_cached
from beartype._util.func.arg.utilfuncargiter import (
    ArgKind,
    ArgMandatory,
    iter_func_args,
)
from beartype._util.func.utilfuncget import get_func_annotations
from beartype._util.func.utilfunctest import is_func_python
from beartype._util.func.utilfuncwrap import unwrap_func_all_isomorphic
from beartype._util.hint.pep.utilpepget import get_hint_pep_sign_or_none
from beartype._util.hint.pep.proposal.utilpep612 import (
    get_hint_pep612_paramspec,
    make_hint_pep612_concatenate_list_or_none,
)
from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_11
from collections.abc import (
    Callable as CallableABC,
)

# ....................{ INFERERS                           }....................
#FIXME: Unit test us up, please.
#FIXME: Revise docstring up, please.
@callable_cached
def infer_hint_callable(func: CallableABC) -> object:
    '''
    **Callable type hint** (i.e., :class:`collections.abc.Callable` protocol
    possibly subscripted by two or more child type hints describing the
    parameters and return) validating the passed callable.

    Specifically, this function (in order):

    #. If the passed callable is non-pure-Python *and*:

       * If the passed callable wraps a lower-level pure-Python callable (e.g.,
         via the standard :func:`functools.wraps` decorator), then the passed
         callable is iteratively unwrapped until obtaining the lowest-level
         pure-Python callable that is *not* such a wrapper.
       * Else, the unsubscripted :class:`collections.abc.Callable` protocol is
         returned as is.

    #. If that callable is unannotated, the unsubscripted
       :class:`collections.abc.Callable` protocol is returned as is.
    #. Else, that callable is annotated by one or more parameter and/or return
       child type hints. If that callable accepts *no* parameters, that callable
       *must* have been annotated by only a return child type hint. In this
       case, the :pep:`585`-compliant type hint ``collections.abc.Callable[...,
       {hint_return}]`` is returned.
    #. Else, that callable accepts one or more parameters. If those parameters
       are all unannotated, the :pep:`585`-compliant type hint
       ``collections.abc.Callable[..., {hint_return}]`` is again returned.
    #. Else, one or more of those parameters are annotated. If that callable
       accepts only mandatory positional-only and/or flexible parameters, the
       :pep:`585`-compliant type hint
       ``collections.abc.Callable[[{hint_param_1}, ???, {hint_param_N}],
       {hint_return}]`` is returned.
    #. Else, that callable accepts one or more of the following:

       * An optional positional-only parameter.
       * An optional flexible parameter.
       * A variadic positional parameter.
       * A keyword-only parameter.
       * A variadic keyword parameter.

       Several distinct cases now arise:

       * If that callable accepts a variadic positional parameter annotated by
         the :pep:`612`-compliant ``P.args`` parameter child type hint *and* a
         corresponding variadic keyword parameter annotated by the
         :pep:`612`-compliant ``P.kwargs`` parameter child type hint for some
         :pep:`612`-compliant **parameter specification** (i.e.,
         :obj:`typing.ParamSpec` object) ``P`` *and*:

         * No other parameters, the :pep:`612`-compliant type hint
           ``collections.abc.Callable[P, {hint_return}]`` is returned.
         * Only one or more mandatory positional-only and/or flexible
           parameters, the :pep:`612`-compliant type hint
           ``collections.abc.Callable[typing.Concatenate[{hint_param_1}, ???,
           {hint_param_N}, P]], {hint_return}]`` is returned.
         * Else, that callable accepts one or more parameters that *cannot* be
           annotated under any existing PEP standard. In this case, these
           unsupported parameters *must* be ignored by replacing the trailing
           ``P`` subscripting the prior ``typing.Concatenate[???]`` child type
           hint with an **ellipsis** (i.e., ``...`` singleton). Although
           undocumented, at least mypy_ and possibly other static type-checkers
           (e.g., pyright_) have extended :pep:`612` for unknown reasons to
           permit this replacement. Interestingly, this undocumented behaviour
           does *not* support both a parameter specification and an ellipsis;
           this behaviour only supports either a parameter specification *or* an
           ellipsis. While the ellipsis is necessary here, the parameter
           specification is not and *must* thus be dropped. Let ``N`` be the
           0-based index of the last mandatory positional-only and/or flexible
           parameter in the signature of that callable. Then, in this case, the
           ludicrous :pep:`612`-compliant type hint
           ``collections.abc.Callable[typing.Concatenate[{hint_param_1}, ???,
           {hint_param_N}, ...]], {hint_return}]`` is returned.

       * Else, that callable again accepts one or more parameters that *cannot*
         be annotated under any existing PEP standard. In this case, these
         unsupported parameters *must* be ignored by abusing the
         :pep:`612`-compliant :obj:`typing.Concatenate` type hint factory.
         Although the child parameter list of :pep:`585`-compliant
         ``collections.abc.Callable[[{hint_params}], {hint_return}]`` type hints
         does *not* support an ellipsis, the child parameter list of
         :pep:`612`-compliant
         ``collections.abc.Callable[typing.Concatenate[{hint_params}],
         {hint_return}]`` type hints does. In theory, :pep:`612` should *not*
         apply here, as that callable accepts *no* :pep:`612`-compliant
         parameter specification. In practice, :pep:`612` can be abused to
         support otherwise unsupportable parameters. Again, let ``N`` be the
         0-based index of the last mandatory positional-only and/or flexible
         parameter in the signature of that callable. Then, in this case, the
         ludicrous :pep:`612`-compliant type hint
         ``collections.abc.Callable[typing.Concatenate[{hint_param_1}, ???,
         {hint_param_N}, ...]], {hint_return}]`` is returned.

    Although admittedly imperfect, this inference strategy nonetheless supports
    a *much* broader set of callable signatures with *much* narrower type hints
    than existing PEP standards would superficially appear to support.

    This function is memoized for efficiency.

    Parameters
    ----------
    func : CallableABC
        Callable to infer a type hint from.

    Returns
    -------
    object
        Callable type hint validating this callable.

    See Also
    --------
    https://stackoverflow.com/a/77467213/2809027
        StackOverflow answer inspiring this implementation.
    '''

    # ....................{ LOCALS                         }....................
    # Preserve the passed callable under a different name for subsequent reuse.
    func_wrapper = func

    # If the passed callable isomorphically wraps another lower-level callable
    # (i.e., if the former is a @functools.wraps()-decorated callable accepting
    # *ONLY* "*args, **kwargs" parameters), reduce the former to the latter.
    func = unwrap_func_all_isomorphic(func_wrapper)

    #FIXME: *HANDLE THIS.* Do so in a similar manner to that of the
    #beartype._decor.decornontype.beartype_pseudofunc() function, please.
    #Namely, attempt to see whether the "func.__call__" instance variable exists
    #and is a pure-Python callable. If so, replace "func" with that: e.g.,
    #    func = getattr(func, '__call__', None)
    #    if func is None:
    #        return obj.__class__  # <-- don't return "Callable" here, because.
    #
    #Even then, we should embed this "Callable[...]" type hint inside an
    #"Annotated[...]" parent type hint ensuring that only objects of the passed
    #object's type are matched. See similar logic in the "infercollectionsabc"
    #submodule: e.g.,
    #    return Annotated[hint, IsInstance[obj.__class__]]

    # If this unwrapped callable is *NOT* pure-Python, this is a pseudo-callable
    # (i.e., arbitrary pure-Python *OR* C-based object whose class defines the
    # __call__() dunder method enabling this object to be called like a standard
    # callable). In this case, trivially return the unsubscripted
    # "collections.abc.Callable" protocol.
    if not is_func_python(func):
        return Callable
    # Else, this callable is pure-Python.

    # Hint to be returned, defaulting to the unsubscripted
    # "collections.abc.Callable" protocol.
    hint: object = Callable

    # Dictionary mapping from the name of each annotated parameter accepted
    # by this unwrapped callable to the type hint annotating that parameter.
    #
    # Note that the functools.update_wrapper() function underlying the
    # @functools.wrap decorator underlying all sane decorators propagates this
    # dictionary from lower-level wrappees to higher-level wrappers by default.
    # We intentionally access the annotations dictionary of this higher-level
    # wrapper, which *SHOULD* be the superset of that of this lower-level
    # wrappee (and thus more reflective of reality).
    pith_name_to_hint = get_func_annotations(func_wrapper)

    # ....................{ INTROSPECT                     }....................
    # If one or more parameters or returns of this callable are annotated...
    if pith_name_to_hint:
        # dict.get() method bound to this dictionary, localized for efficiency.
        pith_name_to_hint_get = pith_name_to_hint.get

        # List of all child hints annotating the parameters of that callable if
        # that callable accepts such parameters *OR* the empty list otherwise.
        hint_params: object = []

        # Child hint annotating the return of that callable, defined as either:
        # * If this return is annotated, the hint annotating this return.
        # * Else, by process of elimination, one or more parameters of this
        #   callable are annotated instead. Logic below synthesizes the parent
        #   hint to be returned by subscripting the "collections.abc.Callable"
        #   hint factory with the list of these parameter child hints. PEP 484
        #   makes *NO* provision for subscripting this factory with only
        #   parameter child hints (and no return child hint); instead, PEP 484
        #   requires this factory *ALWAYS* be subscripted by both parameter and
        #   return child hints. Ergo, a return child hint is *ALWAYS* necessary.
        #   This being the case, we default to the ignorable "object" supertype.
        hint_return = pith_name_to_hint_get(ARG_NAME_RETURN, object)

        # True only if one or more parameters of that callable *cannot* be
        # annotated as parameter child type hints of a parent
        # "Callable[[...], Any]" type hint.
        #
        # See the docstring for detailed discussion of which kinds of parameters
        # can and cannot be annotated as parameter child type hints.
        is_param_unhintable = False

        # True only if that callable accepts one or more parameters.
        is_params = False

        # True only if *ALL* parameters of that callable are unannotated,
        # defaulting to true for simplicity.
        is_params_ignorable = True

        # PEP 612-compliant parameter specification variadic positional
        # parameter instance variable (e.g., "*args: P.args") if that callable
        # accepts a variadic positional parameter annotated by such a variable
        # *OR* "None" otherwise.
        pep612_paramspec_args: Optional[HintPep612ParamSpecArgType] = None

        # PEP 612-compliant parameter specification that is the parent of both
        # variadic positional and keyword parameter instance variables
        # annotating the variadic positional and keyword parameters accepted by
        # that callable (e.g., the "P" in "*args: P.args, **kwargs: P.kwargs")
        # if that callable accepts such parameters *OR* "None" otherwise.
        pep612_paramspec: Optional[HintPep612ParamSpecType] = None

        # For the kind, name, and default value of of each parameter accepted by
        # that callable (in declaration order)...
        for arg_kind, arg_name, arg_default in iter_func_args(
            # Possibly lowest-level wrappee underlying the passed possibly
            # higher-level wrapper. The latter typically fails to convey the
            # same callable metadata conveyed by the former -- including the
            # names and kinds of parameters accepted by the possibly unwrapped
            # callable. This renders the latter mostly useless for our purposes.
            func=func,
            # Avoid inefficiently attempting to re-unwrap this wrappee.
            is_unwrap=False,
        ):
            # Child hint annotating this parameter if any *OR* the root "object"
            # superclass otherwise.
            hint_param = pith_name_to_hint_get(arg_name, object)

            # Note that that callable accepts one or more parameters.
            is_params = True

            # True only if *ALL* parameters of that callable are unannotated,
            # extended for the current parameter.
            is_params_ignorable = (
                is_params_ignorable and hint_param is object)

            # If this is a keyword-only parameter, this parameter is unsupported
            # by any existing PEP standard. Record this and halt iteration.
            if arg_kind is ArgKind.KEYWORD_ONLY:
                is_param_unhintable = True
                break
            # Else, this is *NOT* a keyword-only parameter.
            #
            # If this is a variadic positional parameter...
            elif arg_kind is ArgKind.VARIADIC_POSITIONAL:
                # If this parameter is annotated...
                if hint_param is not object:
                    # Sign uniquely identifying this hint if this hint is
                    # PEP-compliant *OR* "None" (i.e., if this hint is a
                    # PEP-noncompliant type).
                    hint_param_sign = get_hint_pep_sign_or_none(hint_param)

                    # If this variadic positional parameter is annotated by a
                    # PEP 612-compliant parameter specification variadic
                    # positional parameter instance variable (e.g., resembling
                    # "*args: P.args"), record this and continue to the next
                    # parameter.
                    if hint_param_sign is HintSignParamSpecArgs:
                        pep612_paramspec_args = hint_param  # pyright: ignore
                        continue
                    # Else, this variadic positional parameter is annotated by a
                    # type hint unsupported by any existing PEP standard.
                # Else, this parameter is unannotated.

                # Else, this variadic positional parameter is either unannotated
                # *OR* annotated by a type hint unsupported by any existing PEP
                # standard. In either case, record this and halt iteration.
                is_param_unhintable = True
                break
            # Else, this is *NOT* a variadic positional parameter.
            #
            # If this is a variadic keyword parameter...
            elif arg_kind is ArgKind.VARIADIC_KEYWORD:
                # If this parameter is annotated...
                if hint_param is not object:
                    # Sign uniquely identifying this hint if this hint is
                    # PEP-compliant *OR* "None" (i.e., if this hint is a
                    # PEP-noncompliant type).
                    hint_param_sign = get_hint_pep_sign_or_none(hint_param)

                    # If this variadic keyword parameter is annotated by a
                    # PEP 612-compliant parameter specification variadic
                    # keyword parameter instance variable (e.g., resembling
                    # "**kwargs: P.kwargs")..., record this and continue to the
                    # next parameter.
                    if hint_param_sign is HintSignParamSpecKwargs:
                        # If that callable also accepts a variadic positional
                        # parameter annotated by a corresponding PEP
                        # 612-compliant parameter specification variadic
                        # positional parameter instance variable...
                        if pep612_paramspec_args:
                            # PEP 612-compliant parent parameter specifications
                            # containing this pair of instance variables.
                            pep612_paramspec_args_paramspec = (
                                get_hint_pep612_paramspec(
                                    pep612_paramspec_args))
                            pep612_paramspec_kwargs_paramspec = (
                                get_hint_pep612_paramspec(hint_param))  # pyright: ignore

                            # If this pair of instance variables derive from the
                            # same PEP 612-compliant parent parameter
                            # specification, record this and halt iteration. By
                            # definition, *NO* parameters follow this parameter;
                            # the variadic keyword parameter is *ALWAYS* the
                            # last possible parameter in any parameter list.
                            if (
                                pep612_paramspec_args_paramspec is
                                pep612_paramspec_kwargs_paramspec
                            ):
                                pep612_paramspec = (
                                    pep612_paramspec_args_paramspec)
                                break
                            # Else, this pair of instance variables derive from
                            # different PEP 612-compliant parent parameter
                            # specifications. This is horrible. Who would do
                            # something horrible like this? Somebody horrible.
                        # Else, that callable fails to accept such a variadic
                        # positional parameter.
                    # Else, this variadic keyword parameter is annotated by a
                    # type hint unsupported by any existing PEP standard.
                # Else, this parameter is unannotated.

                # Else, this variadic keyword parameter is either unannotated
                # *OR* annotated by a type hint unsupported by any existing PEP
                # standard. In either case, record this and halt iteration.
                is_param_unhintable = True
                break
            # Else, this is *NOT* a variadic keyword parameter. By process of
            # elimination, this *MUST* be either a positional-only or flexible
            # parameter.
            #
            # If this is an optional positional-only or flexible parameter, this
            # parameter is unsupported by any existing PEP standard. Record this
            # and halt iteration.
            elif arg_default is not ArgMandatory:
                is_param_unhintable = True
                break
            # Else, this is a mandatory positional-only or flexible parameter.
            # In this case, append the child hint annotating this parameter to
            # the list of all child parameter hints.
            else:
                hint_params.append(hint_param)  # type: ignore[attr-defined]

        # If that callable accepts *NO* parameters, preserve the list of all
        # child parameter hints as the empty list.
        if not is_params:
            pass
        # Else, that callable accepts one or more parameters.
        #
        # If *ALL* parameters of that callable are unannotated, ignore these
        # parameters by setting the list of all child parameter hints to the
        # ellipsis.
        elif is_params_ignorable:
            hint_params = ...
        # Else, one or more parameters of that callable are annotated.
        #
        # If that callable accepts one or more unsupported parameters...
        elif is_param_unhintable:
            # If the active Python interpreter targets Python >= 3.11, then the
            # PEP 612-compliant "typing(|_extensions).Concatenate" hint factory
            # is subscriptable by a trailing ellipsis. In this case...
            if IS_PYTHON_AT_LEAST_3_11:
                # Generalize the list of all child parameter hints to this
                # factory subscripted by all child hints annotating all
                # mandatory positional-only and flexible parameters accepted by
                # that callable suffixed by the ellipsis ignoring all remaining
                # unsupported parameters.
                #
                # See the docstring for detailed discussion of this behaviour.
                hint_params = make_hint_pep612_concatenate_list_or_none(
                    hint_params, ...)  # type: ignore[arg-type]

                # If this factory is unimportable, we sadly have *NO* recourse
                # but to silently ignore *ALL* parameters.
                if hint_params is None:
                    hint_params = ...
                # Else, this factory is importable. In this case, preserve this
                # hint as is.
            # Else, the active Python interpreter targets Python < 3.11. In this
            # case, the PEP 612-compliant "typing(|_extensions).Concatenate"
            # hint factory is *NOT* subscriptable by a trailing ellipsis.
            # Attempting to do so raises:
            #     TypeError: The last parameter to Concatenate should be a
            #     ParamSpec variable.
            #
            # In this case, we sadly have *NO* recourse but to silently ignore
            # *ALL* parameters.
            else:
                hint_params = ...
        # Else, that callable accepts *NO* unsupported parameters.
        #
        # If that callable accepts a PEP 612-compliant parameter
        # specification...
        elif pep612_paramspec is not None:
            # If that callable accepts one or more mandatory positional-only or
            # flexible parameters...
            if hint_params:
                # Generalize the list of all child parameter hints to the PEP
                # 612-compliant "Concatenate[...]"  hint factory subscripted by
                # all child hints annotating all mandatory positional-only and
                # flexible parameters accepted by that callable suffixed by the
                # this parameter specification.
                hint_params = make_hint_pep612_concatenate_list_or_none(
                    hint_params, pep612_paramspec)  # type: ignore[arg-type]

                # If this factory is unimportable, we sadly have *NO* recourse
                # but to silently ignore *ALL* parameters.
                if hint_params is None:
                    hint_params = ...
                # Else, this factory is importable. In this case, preserve this
                # hint as is.
            # Else, that callable accepts *NO* mandatory positional-only or
            # flexible parameters. In this case, set the list of all child
            # parameter hints to this parameter specification as is.
            else:
                hint_params = pep612_paramspec
        # Else, that callable accepts *NO* PEP 612-compliant parameter
        # specification. In this case, that callable accepts *ONLY* one or more
        # mandatory positional-only and/or flexible parameters. In this case,
        # preserve this list of all child parameter hints as is.

        # Callable hint to be returned, defined as either...
        hint = (
            # The unsubscripted "collections.abc.Callable" protocol if...
            Callable
            if (
                # The list of all child parameter hints is the ellipsis
                # (signifying all parameters to be ignorable) *AND*...
                hint_params is ... and
                # The child return hint is the ignorable "object" superclass.
                hint_return is object
            ) else
            # Else, the "collections.abc.Callable" type hint factory subscripted
            # by these unignorable child parameter and return type hints.
            Callable[hint_params, hint_return]  # pyright: ignore
        )
    # Else, *NO* parameters or returns of this callable are annotated.

    # Return this hint.
    return hint
