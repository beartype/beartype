#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`749`-compliant **deferred type hints** (i.e., hints that are
possibly unquoted forward references referring to currently undefined types
under Python >= 3.14).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.roar import BeartypeDecorHintPep749Exception
from beartype._cave._cavefast import HintPep749RefFormat  # type: ignore[attr-defined]
from beartype._data.kind.datakindiota import SENTINEL
from beartype._data.typing.datatyping import TypeException
from beartype._data.typing.datatypingport import (
    Hint,
    HintOrSentinel,
)
from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_14

# ....................{ GETTERS                            }....................
#FIXME: Unit test us up, please.
def get_hint_pep749_evaluator_mandatory(
    # Mandatory parameters.
    hint: Hint,
    evaluator_name_dynamic: str,
    evaluator_name_static: str,

    # Optional parameters.
    hint_format: HintPep749RefFormat = HintPep749RefFormat.FORWARDREF,
    exception_cls: TypeException = BeartypeDecorHintPep749Exception,
    exception_prefix: str = '',
) -> Hint:
    '''
    :pep:`749`-compliant **mandatory evaluator** (i.e., nested type hint defined
    as an attribute on a parent type hint whose value is required to *not* be
    :data:`None` but may be a possibly unquoted forward reference referring to a
    currently undefined type) with the passed static or dynamic attribute names
    defined on the passed parent type hint if any *or* raise an exception
    otherwise (i.e., if this parent type hint either fails to define an
    attribute having either of these names or defines such an attribute to be
    :data:`None`).

    This getter is intentionally *not* memoized (e.g., by the
    ``@callable_cached`` decorator), as the implementation trivially reduces to
    a one-liner.

    Caveats
    -------
    **This getter is only intended to be passed** :pep:`749`-compliant **hints
    whose evaluators are mandatory** (rather than optional). Currently, the only
    mandatory evaluators are:

    * :pep:`695`-compliant ``type`` alias value evaluators defined as the
      ``__value__`` dunder attribute.

    Parameters
    ----------
    hint : Hint
        Parent type hint to be inspected.
    evaluator_name_dynamic : str
        Unqualified basename of the attribute defined on this parent type hint
        yielding this hint's **dynamic evaluator** (i.e., bound method accepting
        the passed format and returning this evaluator in this format).
    evaluator_name_static : str
        Unqualified basename of the attribute defined on this parent type hint
        yielding this hint's **static evaluator** (i.e., dunder instance variable
        whose value directly provides this evaluator).
    hint_format : HintPep749RefFormat, default: HintPep749RefFormat.FORWARDREF
        HintPep749RefFormat of annotated hints to be returned. Defaults to
        :attr:`HintPep749RefFormat.FORWARDREF`, in which case this getter safely
        encapsulates each otherwise unsafe unquoted forward reference
        transitively subscripting each hint annotating this hintable with a safe
        :class:`annotationlib.ForwardRef` object. Note that the remaining
        formats are situational at best. See also the
        :func`beartype._util.hint.pep.proposal.pep649749.get_pep649_hintable_annotations`
        getter for further details.
    exception_cls : TypeException, default: BeartypeDecorHintPep749Exception
        Type of exception to be raised in the event of a fatal error. Defaults
        to :exc:`.BeartypeDecorHintPep749Exception`.
    exception_prefix : str, default: ''
        Human-readable substring prefixing raised exception messages. Defaults
        to the empty string.

    Returns
    -------
    Hint
        Subhint with this static or dynamic attribute name defined on this hint.

    Raises
    ------
    exception_cls
        If this parent type hint either:

        * Fails to define an attribute having either of these names.
        * Defines an attribute having either of these names to be **optional**
          (i.e., whose value is :data:`None`).
    '''

    # Subhint defined by this hintable if any *OR* the sentinel placeholder.
    hint_evaluator = get_hint_pep749_evaluator_optional(
        hint=hint,
        evaluator_name_dynamic=evaluator_name_dynamic,
        evaluator_name_static=evaluator_name_static,
        # Since a mandatory evaluator by definition has *NO* default, select an
        # arbitrary beartype-specific default guaranteed to *NEVER* be a valid
        # type hint. The sentinel placeholder wins again.
        evaluator_value_null=SENTINEL,
        hint_format=hint_format,
        exception_cls=exception_cls,
        exception_prefix=exception_prefix,
    )

    # If this hint nullifies this evaluator, raise an exception.
    #
    # Note that this should *NEVER* occur and cannot, in fact, be tested. *sigh*
    if hint_evaluator is SENTINEL:  # pragma: no cover
        assert isinstance(exception_cls, type), (
            f'{repr(exception_cls)} not class.')
        assert issubclass(exception_cls, Exception), (
            f'{repr(exception_cls)} not exception subclass.')
        assert isinstance(exception_prefix, str), (
            f'{repr(exception_prefix)} not string.')

        # Raise a human-readable exception.
        raise exception_cls(
            f'{exception_prefix}type hint {repr(hint)} '
            f'mandatory evaluator nullified (i.e., '
            f'static evaluator attribute "{evaluator_name_static}" and '
            f'dynamic evaluator attribute "{evaluator_name_dynamic}" '
            f'both defined to be "None").'
        )
    # Else, this hint does *NOT* nullify this evaluator.

    # Return this evaluator.
    return hint_evaluator  # pyright: ignore

# ....................{ PRIVATE ~ getters                  }....................
def _get_hint_pep749_evaluator_optional_static(  # pyright: ignore
    # Mandatory parameters.
    hint: Hint,
    evaluator_name_static: str,
    evaluator_value_null: object,

    # Optional parameters.
    exception_cls: TypeException = BeartypeDecorHintPep749Exception,
    exception_prefix: str = '',
) -> HintOrSentinel:
    '''
    :pep:`749`-compliant **optional static evaluator** (i.e., nested type hint
    defined as an attribute on a parent type hint whose value may be either the
    passed null evaluator value or a possibly unquoted forward reference
    referring to a currently undefined type) with the passed static attribute
    name defined on the passed parent type hint if this value is not this null
    evaluator value *or* the sentinel placeholder otherwise (i.e., if this
    parent type hint defines an attribute having this name whose value is this
    null evaluator value).

    This getter is intentionally *not* memoized (e.g., by the
    ``@callable_cached`` decorator), as the implementation trivially reduces to
    a one-liner.

    Parameters
    ----------
    hint : Hint
        Parent type hint to be inspected.
    evaluator_name_static : str
        Unqualified basename of the attribute defined on this parent type hint
        yielding this hint's **static evaluator** (i.e., dunder instance
        variable whose value directly provides this evaluator).
    evaluator_value_null : object
        **Null evaluator value** (i.e., arbitrary object signifying this
        evaluator to be nullified), implying this evaluator to be unspecified.
    exception_cls : TypeException, default: BeartypeDecorHintPep749Exception
        Type of exception to be raised in the event of a fatal error. Defaults
        to :exc:`.BeartypeDecorHintPep749Exception`.
    exception_prefix : str, default: ''
        Human-readable substring prefixing raised exception messages. Defaults
        to the empty string.

    Returns
    -------
    Hint
        If this parent type hint defines an attribute having this name whose
        value is either:

        * The passed null evaluator value, the sentinel placeholder.
        * Else, the value of that attribute.

    Raises
    ------
    exception_cls
        If this parent type hint fails to define an attribute having this name.
    '''
    assert isinstance(evaluator_name_static, str), (
        f'{repr(evaluator_name_static)} not string.')

    # Subhint to be returned. Specifically, either:
    # * If this hint defines a static evaluator with this name, the value of
    #   this evaluator: a simple PEP-compliant child hint.
    # * Else, the sentinel placeholder.
    evaluator_value = getattr(hint, evaluator_name_static, SENTINEL)

    # If this hint defines *NO* static evaluator with this name, raise an
    # exception.
    #
    # Note that this should *NEVER* be the case.
    if evaluator_value is SENTINEL:
        raise exception_cls(
            f'{exception_prefix}type hint {repr(hint)} '
            f'static evaluator attribute "{evaluator_name_static}" undefined.'
        )
    # Else, this hint defines a static evaluator with this name.
    #
    # If this evaluator is the null value, silently reduce to a noop and
    # immediately coerce this evaluator to the sentinel placeholder.
    elif evaluator_value is evaluator_value_null:
        evaluator_value = SENTINEL
    # Else, this evaluator is *NOT* the null value. In this case, preserve this
    # evaluator as is.

    # Return this evaluator.
    return evaluator_value

# ....................{ VERSIONS                           }....................
# If the active Python interpreter targets Python >= 3.14...
if IS_PYTHON_AT_LEAST_3_14:
    # ....................{ IMPORTS                        }....................
    # Defer version-specific imports.
    from annotationlib import call_evaluate_function  # type: ignore[import-not-found]

    # ....................{ GETTERS                        }....................
    #FIXME: Consider memoization. This getter is likely to be *EXTREMELY*
    #slow. That said, we are simply outta volunteer time on this one.
    #Sometimes, you just gotta ship it as is. *shrug*
    def get_hint_pep749_evaluator_optional(  # pyright: ignore
        # Mandatory parameters.
        hint: Hint,
        evaluator_name_dynamic: str,
        evaluator_name_static: str,
        evaluator_value_null: object,

        # Optional parameters.
        hint_format: HintPep749RefFormat = HintPep749RefFormat.FORWARDREF,
        exception_cls: TypeException = BeartypeDecorHintPep749Exception,
        exception_prefix: str = '',
    ) -> HintOrSentinel:
        assert isinstance(evaluator_name_dynamic, str), (
            f'{repr(evaluator_name_dynamic)} not string.')
        assert isinstance(hint_format, HintPep749RefFormat), (
            f'{repr(hint_format)} not annotation format.')

        # If this hint format is the forward reference format implicitly
        # coercing nested unquoted forward references into proxy objects...
        #
        # Note that this is the most common hint format and thus intentionally
        # tested first.
        if hint_format is HintPep749RefFormat.FORWARDREF:
            # Attempt to first efficiently retrieve this evaluator's static value.
            try:
                evaluator_value = _get_hint_pep749_evaluator_optional_static(
                    hint=hint,
                    evaluator_name_static=evaluator_name_static,
                    evaluator_value_null=evaluator_value_null,
                    exception_cls=exception_cls,
                    exception_prefix=exception_prefix,
                )
            # If doing so raises a builtin "NameError" exception, this evaluator
            # contains one or more unquoted forward references. In this case...
            except NameError:
                # Fallback to inefficiently retrieving this evaluator's dynamic
                # value coercing these unquoted forward references into proxies.
                evaluator_value = _get_hint_pep749_evaluator_optional_dynamic(
                    hint=hint,
                    evaluator_name_dynamic=evaluator_name_dynamic,
                    evaluator_value_null=evaluator_value_null,
                    hint_format=hint_format,
                    exception_cls=exception_cls,
                    exception_prefix=exception_prefix,
                )
        # Else, this hint format is *NOT* the forward reference format.
        #
        # If this hint format is the value format raising exceptions if this
        # evaluator contains one or more unquoted forward references...
        elif hint_format is HintPep749RefFormat.VALUE:
            # Trivially defer to this private static-specific getter.
            evaluator_value = _get_hint_pep749_evaluator_optional_static(
                hint=hint,
                evaluator_name_static=evaluator_name_static,
                evaluator_value_null=evaluator_value_null,
                exception_cls=exception_cls,
                exception_prefix=exception_prefix,
            )
        # Else, this hint format is *NOT* the value format. In this case...
        else:
            # Fallback to inefficiently retrieving this evaluator's dynamic
            # value coercing this evaluator into this format.
            evaluator_value = _get_hint_pep749_evaluator_optional_dynamic(
                hint=hint,
                evaluator_name_dynamic=evaluator_name_dynamic,
                evaluator_value_null=evaluator_value_null,
                hint_format=hint_format,
                exception_cls=exception_cls,
                exception_prefix=exception_prefix,
            )

        # Return this evaluator.
        return evaluator_value

    # ....................{ PRIVATE ~ getters              }....................
    def _get_hint_pep749_evaluator_optional_dynamic(  # pyright: ignore
        # Mandatory parameters.
        hint: Hint,
        evaluator_name_dynamic: str,
        evaluator_value_null: object,

        # Optional parameters.
        hint_format: HintPep749RefFormat = HintPep749RefFormat.FORWARDREF,
        exception_cls: TypeException = BeartypeDecorHintPep749Exception,
        exception_prefix: str = '',
    ) -> HintOrSentinel:
        '''
        :pep:`749`-compliant **optional dynamic evaluator** (i.e., nested type
        hint defined as an attribute on a parent type hint whose value may be
        either the passed null evaluator value or a low-level C-based evaluator
        function implemented by CPython whose signature matches
        ``Callable[[HintPep749RefFormat], Hint]``) with the passed dynamic
        attribute name defined by calling this evaluator function on the passed
        parent type hint if this value is not this null evaluator value *or* the
        sentinel placeholder otherwise (i.e., if this parent type hint defines
        an attribute having this name whose value is this null evaluator value).

        This getter is intentionally *not* memoized (e.g., by the
        ``@callable_cached`` decorator), as the implementation trivially reduces
        to a one-liner.

        Parameters
        ----------
        hint : Hint
            Parent type hint to be inspected.
        evaluator_name_dynamic : str
            Unqualified basename of the attribute defined on this parent type
            hint yielding this hint's **dynamic evaluator** (i.e., bound method
            accepting the passed format and returning this evaluator in this
            format).
        evaluator_value_null : object
            **Null evaluator value** (i.e., arbitrary object signifying this
            evaluator to be nullified), implying this evaluator to be
            unspecified.
        hint_format : HintPep749RefFormat, default: HintPep749RefFormat.FORWARDREF
            HintPep749RefFormat of annotated hints to be returned. Defaults to
            :attr:`HintPep749RefFormat.FORWARDREF`, in which case this getter
            safely encapsulates each otherwise unsafe unquoted forward reference
            transitively subscripting each hint annotating this hintable with a
            safe :class:`annotationlib.ForwardRef` object. Note that the
            remaining formats are situational at best. See also the
            :func`beartype._util.hint.pep.proposal.pep649749.get_pep649_hintable_annotations`
            getter for further details.
        exception_cls : TypeException, default: BeartypeDecorHintPep749Exception
            Type of exception to be raised in the event of a fatal error.
            Defaults to :exc:`.BeartypeDecorHintPep749Exception`.
        exception_prefix : str, default: ''
            Human-readable substring prefixing raised exception messages.
            Defaults to the empty string.

        Returns
        -------
        Hint
            If this parent type hint defines an attribute having this name whose
            value is either:

            * The passed null evaluator value, the sentinel placeholder.
            * Else, the value of that attribute.

        Raises
        ------
        exception_cls
            If this parent type hint fails to define an attribute having this
            name.
        '''
        assert isinstance(evaluator_name_dynamic, str), (
            f'{repr(evaluator_name_dynamic)} not string.')

        # Subhint to be returned. Specifically, either:
        # * If this hint defines a dynamic evaluator with this name, the value
        #   of this evaluator: a low-level C-based evaluator function
        #   implemented by CPython, whose signature matches
        #   "Callable[[HintPep749RefFormat], Hint]".
        # * Else, the sentinel placeholder.
        evaluator_value = getattr(hint, evaluator_name_dynamic, SENTINEL)

        # If this hint defines *NO* dynamic evaluator with this name, raise an
        # exception. Note that this should *NEVER* be the case.
        if evaluator_value is SENTINEL:
            raise exception_cls(
                f'{exception_prefix}type hint {repr(hint)} '
                f'dynamic evaluator attribute "{evaluator_name_dynamic}" undefined.'
            )
        # Else, this hint defines a dynamic evaluator with this name.
        #
        # If this evaluator is the null value, silently reduce to a noop and
        # immediately coerce this evaluator to the sentinel placeholder.
        elif evaluator_value is evaluator_value_null:
            evaluator_value = SENTINEL
        # Else, this evaluator is *NOT* the null value.
        #
        # If this evaluator is uncallable, this evaluator is *NOT* an evaluator
        # function. In this case, raise an exception.
        #
        # Note that this should *NEVER* be the case.
        elif not callable(evaluator_value):
            raise exception_cls(
                f'{repr(evaluator_value)} uncallable.')
        # Else, this evaluator is callable and thus an evaluator function. In
        # this case...
        else:
            # Subhint formatted by this evaluator function in this format.
            evaluator_value = call_evaluate_function(
                evaluator_value, hint_format)  # pyright: ignore

            # If this evaluator is the null value, silently reduce to a noop and
            # immediately coerce this evaluator to the sentinel placeholder.
            #
            # Note that this redundancy intentionally exists to handle obscure
            # (and presumably unintentional edge cases) in PEP 749. Notably:
            #     >>> from typing import TypeVar
            #     >>> T = TypeVar('T')
            #     >>> T.__bound__
            #     None  # <-- makes sense
            #     >>> T.evaluate_bound
            #     None  # <-- makes sense, sorta
            #     >>> T.__default__
            #     typing.NoDefault  # <-- makes no sense, but okay
            #     >>> T.evaluate_default
            #     <constevaluator typing.NoDefault>  # <-- makes no sense and contradicts PEP 749
            #     >>> T.evaluate_default(1)
            #     typing.NoDefault  # <-- makes no sense, but okay
            if evaluator_value is evaluator_value_null:
                evaluator_value = SENTINEL
            # Else, this evaluator is *NOT* the null value.

        # Return this evaluator.
        return evaluator_value
# Else, the active Python interpreter targets Python <= 3.13. In this case,
# trivially defer to the PEP 484-compliant "__annotations__" dunder attribute.
else:
    # ....................{ GETTERS                        }....................
    def get_hint_pep749_evaluator_optional(
        # Mandatory parameters.
        hint: Hint,
        evaluator_name_dynamic: str,
        evaluator_name_static: str,
        evaluator_value_null: object,

        # Optional parameters.
        hint_format: HintPep749RefFormat = HintPep749RefFormat.FORWARDREF,
        exception_cls: TypeException = BeartypeDecorHintPep749Exception,
        exception_prefix: str = '',
    ) -> HintOrSentinel:

        # Trivially defer to the private static-specific getter defined above.
        # Note that this call intentionally omits irrelevant parameters. Ergo,
        # these two getters *CANNOT* simply be aliased to one another.
        return _get_hint_pep749_evaluator_optional_static(
            hint=hint,
            evaluator_name_static=evaluator_name_static,
            evaluator_value_null=evaluator_value_null,
            exception_cls=exception_cls,
            exception_prefix=exception_prefix,
        )


get_hint_pep749_evaluator_optional.__doc__ = (
    '''
    :pep:`749`-compliant **optional evaluator** (i.e., nested type hint defined
    as an attribute on a parent type hint whose value may be either :data:`None`
    or a possibly unquoted forward reference referring to a currently undefined
    type) with the passed static or dynamic attribute names defined on the
    passed parent type hint if this value is not :data:`None` *or* the sentinel
    placeholder otherwise (i.e., if this parent type hint defines an attribute
    having either of these names whose value is the passed null evaluator value).

    This getter intentionally returns the sentinel placeholder (rather than
    :data:`None`) when either of these attributes is the null evaluator value.
    Why? To enable callers to distinguish between evaluators that are nullified
    from evaluators whose values are actually :data:`None`, which is (of course)
    a valid :pep:`484`-compliant type hint.

    This getter is intentionally *not* memoized (e.g., by the
    ``@callable_cached`` decorator), as the implementation trivially reduces to
    a one-liner.

    Caveats
    -------
    **This getter is only intended to be passed** :pep:`749`-compliant **hints
    whose evaluators are optional** (rather than mandatory). Currently, the only
    optional evaluators are:

    * :pep:`484`-compliant type variable bound and constraint evaluators defined
      as the ``__bound__`` and ``__constraints__`` dunder attributes.
    * :pep:`696`-compliant type variable default evaluators defined as the
      ``__default__`` dunder attribute.

    Parameters
    ----------
    hint : Hint
        Parent type hint to be inspected.
    evaluator_name_dynamic : str
        Unqualified basename of the attribute defined on this parent type hint
        yielding this hint's **dynamic evaluator** (i.e., bound method accepting
        the passed format and returning this evaluator in this format).
    evaluator_name_static : str
        Unqualified basename of the attribute defined on this parent type hint
        yielding this hint's **static evaluator** (i.e., dunder instance
        variable whose value directly provides this evaluator).
    evaluator_value_null : object
        **Null evaluator value** (i.e., arbitrary object signifying this
        evaluator to be nullified), implying this evaluator to be unspecified.
    hint_format : HintPep749RefFormat, default: HintPep749RefFormat.FORWARDREF
        HintPep749RefFormat of annotated hints to be returned. Defaults to
        :attr:`HintPep749RefFormat.FORWARDREF`, in which case this getter safely
        encapsulates each otherwise unsafe unquoted forward reference
        transitively subscripting each hint annotating this hintable with a safe
        :class:`annotationlib.ForwardRef` object. Note that the remaining
        formats are situational at best. See also the
        :func`beartype._util.hint.pep.proposal.pep649749.get_pep649_hintable_annotations`
        getter for further details.
    exception_cls : TypeException, default: BeartypeDecorHintPep749Exception
        Type of exception to be raised in the event of a fatal error. Defaults
        to :exc:`.BeartypeDecorHintPep749Exception`.
    exception_prefix : str, default: ''
        Human-readable substring prefixing raised exception messages. Defaults
        to the empty string.

    Returns
    -------
    Hint
        If this parent type hint defines an attribute having either of these
        names whose value is either:

        * The passed null evaluator value, the sentinel placeholder.
        * Else, the value of that attribute.

    Raises
    ------
    exception_cls
        If this parent type hint fails to define an attribute having either of
        these names.
    '''
)
