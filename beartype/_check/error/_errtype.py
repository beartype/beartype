#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype class type hint violation describers** (i.e., functions returning
human-readable strings explaining violations of type hints that are standard
isinstanceable classes rather than PEP-specific objects).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.roar import (
    BeartypeCallHintForwardRefException,
    BeartypePlugInstancecheckStrException,
)
from beartype.roar._roarexc import _BeartypeCallHintPepRaiseException
from beartype.typing import (
    Any,
    Optional,
)
from beartype._data.hint.datahinttyping import (
    TupleTypes,
    TypeOrTupleTypes,
)
from beartype._data.hint.pep.sign.datapepsigns import (
    HintSignForwardRef,
    HintSignType,
    HintSignUnion,
)
from beartype._check.error.errcause import ViolationCause
from beartype._util.cls.utilclstest import is_type_subclass
from beartype._util.cls.pep.utilpep3119 import (
    die_unless_object_issubclassable,
    die_unless_type_isinstanceable,
)
from beartype._util.func.arg.utilfuncargtest import (
    die_unless_func_args_len_flexible_equal)
from beartype._util.hint.nonpep.utilnonpeptest import (
    die_unless_hint_nonpep_tuple)
from beartype._util.hint.pep.proposal.pep484585.pep484585ref import (
    import_pep484585_ref_type)
from beartype._util.hint.pep.utilpepget import (
    get_hint_pep_args,
    get_hint_pep_origin_type_isinstanceable_or_none,
    get_hint_pep_sign_or_none,
)
from beartype._util.text.utiltextjoin import join_delimited_disjunction_types
from beartype._util.text.utiltextlabel import label_type
from beartype._util.text.utiltextrepr import represent_pith

# ....................{ GETTERS ~ instance : type          }....................
def find_cause_instance_type(cause: ViolationCause) -> ViolationCause:
    '''
    Output cause describing whether the pith of the passed input cause either is
    or is not an instance of the isinstanceable class of that cause.

    Parameters
    ----------
    cause : ViolationCause
        Input cause providing this data.

    Returns
    -------
    BeartypePlugInstancecheckStrException
        If the metaclass of this isinstanceable class defines the
        :mod:`beartype`-specific ``__instancecheck_str__()`` dunder method but
        either:

        * This method is *not* a pure-Python callable.
        * This method is a pure-Python callable with an unexpected signature
          that differs from the expected API:

          .. code-block:: python

             def __instancecheck_str__(cls, obj: typing.Any) -> str:

        * This method is a pure-Python callable with the expected signature that
          returns either:

          * An object that is *not* a string.
          * The empty string.
    ViolationCause
        Output cause type-checking this data.
    '''
    assert isinstance(cause, ViolationCause), f'{repr(cause)} not cause.'

    # Isinstanceable class against which this pith was type-checked.
    hint: type = cause.hint  # type: ignore[assignment]

    # Pith type-checked against this isinstanceable class.
    pith = cause.pith

    # If this hint is *NOT* an isinstanceable class, raise an exception.
    die_unless_type_isinstanceable(
        cls=hint,
        exception_cls=_BeartypeCallHintPepRaiseException,
        exception_prefix=cause.exception_prefix,
    )
    # Else, this hint is an isinstanceable class.

    # Output cause justification. If this pith either:
    # * Violates this hint, this is a human-readable substring describing this
    #   violation.
    # * Satisfies this hint, "None".
    cause_str_or_none: Optional[str] = None

    # If this pith is *NOT* an instance of this class...
    if not isinstance(pith, hint):
        # Metaclass-specific __instancecheck_str__() dunder method if the
        # metaclass of this class defines this method *OR* "None" otherwise
        # (i.e., if that metaclass does *NOT* define this method).
        #
        # Note that this constitutes a plugin API. Although currently
        # beartype-specific, this API is intended to receive widespread adoption
        # as a pseudo-standard throughout the runtime type-checking community
        # (e.g., by typeguard and possibly Pydantic). Various third-party
        # packages that publish custom type hint factories currently leverage
        # this API to generate package-specific violation messages, including:
        # * @patrick-kidger's "jaxtyping" package. For the good of Google!
        get_hint_violation_str = getattr(hint, '__instancecheck_str__', None)

        # If the metaclass of this class defines this dunder method...
        if get_hint_violation_str:
            # Human-readable substring prefixing *ALL* exceptions raised below.
            EXCEPTION_PREFIX = (
                f'{cause.exception_prefix}{repr(hint)} '
                f'beartype-specific dunder method __instancecheck_str__() '
            )

            # If this method is *NOT* a pure-Python callable accepting exactly
            # two parameters, this method does *NOT* satisfy the expected API:
            #      def __instancecheck_str__(cls, obj: typing.Any) -> str:
            #
            # In this case, raise an exception.
            die_unless_func_args_len_flexible_equal(
                func=get_hint_violation_str,
                func_args_len_flexible=2,
                exception_cls=BeartypePlugInstancecheckStrException,
                exception_prefix=EXCEPTION_PREFIX,
            )
            # Else, this method satisfies the expected API.

            # Human-readable substring describing this violation generated by
            # the metaclass of this class.
            cause_str_or_none = get_hint_violation_str(pith)

            # If this string is *NOT* actually a string, raise an exception.
            if not isinstance(cause_str_or_none, str):
                raise BeartypePlugInstancecheckStrException(
                    f'{EXCEPTION_PREFIX}return {cause_str_or_none} not string.')
            # Else, this string is actually a string.
            #
            # If this string is empty, raise an exception.
            elif not cause_str_or_none:
                raise BeartypePlugInstancecheckStrException(
                    f'{EXCEPTION_PREFIX}return string empty.')
            # Else, this string is non-empty.
        # Else, the metaclass of this class does *NOT* define this method. In
        # this case, fallback to a standard substring describing this violation.
        else:
            cause_str_or_none = (
                f'{represent_pith(pith)} not instance of '
                f'{label_type(cls=hint, is_color=cause.conf.is_color)}'
            )
    # Else, this pith is an instance of this class.

    # Output cause to be returned, permuted from this input cause with this
    # output cause justification.
    cause_return = cause.permute(cause_str_or_none=cause_str_or_none)

    # Return this output cause.
    return cause_return


def find_cause_instance_type_forwardref(
    cause: ViolationCause) -> ViolationCause:
    '''
    Output cause describing whether the pith of the passed input cause either is
    or is not an instance of the class referred to by the **forward reference
    type hint** (i.e., string whose value is the either absolute *or* relative
    name of a user-defined type which has yet to be defined) of that cause.

    Parameters
    ----------
    cause : ViolationCause
        Input cause providing this data.

    Returns
    -------
    ViolationCause
        Output cause type-checking this data.
    '''
    assert isinstance(cause, ViolationCause), f'{repr(cause)} not cause.'
    assert cause.hint_sign is HintSignForwardRef, (
        f'{cause.hint_sign} not forward reference.')

    # Class referred to by this absolute or relative forward reference.
    hint_ref_type = import_pep484585_ref_type(
        hint=cause.hint,  # type: ignore[arg-type]
        cls_stack=cause.cls_stack,
        func=cause.func,
        exception_cls=BeartypeCallHintForwardRefException,
        exception_prefix=cause.exception_prefix,
    )

    # Defer to the function handling isinstanceable classes. Neato!
    return find_cause_instance_type(cause.permute(hint=hint_ref_type))


def find_cause_type_instance_origin(cause: ViolationCause) -> ViolationCause:
    '''
    Output cause describing whether the pith of the passed input cause either is
    or is not an instance of the isinstanceable type underlying the
    **originative type hint** (i.e., PEP-compliant type hint originating from a
    non-:mod:`typing` class, typically due to being either a
    :pep:`585`-compliant type hint *or* a third-party type hint subclassing the
    :class:`types.GenericAlias` superclass defined by :pep:`585`) of that cause.

    Parameters
    ----------
    cause : ViolationCause
        Input cause providing this data.

    Returns
    -------
    ViolationCause
        Output cause type-checking this data.
    '''
    assert isinstance(cause, ViolationCause), f'{repr(cause)} not cause.'

    # Isinstanceable origin type originating this hint if any *OR* "None".
    hint_type = get_hint_pep_origin_type_isinstanceable_or_none(cause.hint)

    # If this hint does *NOT* originate from such a type, raise an exception.
    if hint_type is None:
        raise _BeartypeCallHintPepRaiseException(
            f'{cause.exception_prefix}type hint '
            f'{repr(cause.hint)} not originated from '
            f'isinstanceable origin type.'
        )
    # Else, this hint originates from such a type.

    # Defer to the getter function handling non-"typing" classes. Presto!
    return find_cause_instance_type(cause.permute(hint=hint_type))

# ....................{ GETTERS ~ instance : types         }....................
def find_cause_instance_types_tuple(cause: ViolationCause) -> ViolationCause:
    '''
    Output cause describing whether the pith of the passed input cause either is
    or is not an instance of one or more isinstanceable types in the tuple of
    these types of that cause.

    Parameters
    ----------
    cause : ViolationCause
        Input cause providing this data.

    Returns
    -------
    ViolationCause
        Output cause type-checking this data.
    '''
    assert isinstance(cause, ViolationCause), f'{repr(cause)} not cause.'

    # This tuple union.
    hint: TupleTypes = cause.hint  # type: ignore[assignment]

    # If this hint is *NOT* a tuple union, raise an exception.
    die_unless_hint_nonpep_tuple(
        hint=hint,
        exception_prefix=cause.exception_prefix,
        exception_cls=_BeartypeCallHintPepRaiseException,
    )
    # Else, this hint is a tuple union.

    # If this pith is an instance of one or more types in this tuple union,
    # record that this pith satisfies this tuple union.
    if isinstance(cause.pith, hint):
        cause_return = cause.permute(cause_str_or_none=None)
    # Else, this pith is an instance of *NO* types in this tuple union. In
    # this case, this pith violates this tuple union.
    else:
        # Machine-readable representation of this tuple union.
        hint_repr = join_delimited_disjunction_types(
            types=hint, is_color=cause.conf.is_color)

        # Output cause to be returned, permuted from this input cause such that
        # the output cause justification is a substring describing this failure.
        cause_return = cause.permute(cause_str_or_none=(
            f'{represent_pith(cause.pith)} not instance of {hint_repr}'))

    # Return this output cause.
    return cause_return

# ....................{ GETTERS ~ subclass : type          }....................
def find_cause_subclass_type(cause: ViolationCause) -> ViolationCause:
    '''
    Output cause describing whether the pith of the passed input cause either is
    or is not a subclass of the issubclassable type of that cause.

    Parameters
    ----------
    cause : ViolationCause
        Input cause providing this data.

    Returns
    -------
    ViolationCause
        Output cause type-checking this data.
    '''
    assert isinstance(cause, ViolationCause), f'{repr(cause)} not cause.'
    assert cause.hint_sign is HintSignType, (
        f'{cause.hint_sign} not HintSignType.')

    # Shallow output cause describing the failure of this path to be a type if
    # this pith a non-type *OR* "None" otherwise (i.e., if this pith is a type).
    cause_shallow = find_cause_type_instance_origin(cause)

    # If this pith is *NOT* a type, return this shallow cause.
    if cause_shallow.cause_str_or_none is not None:
        return cause_shallow
    # Else, this pith is a type.

    # Superclass this pith is required to be a subclass of.
    hint_child: TypeOrTupleTypes = cause.hint_childs[0]  # pyright: ignore

    # If this superclass is ignorable, then *ALL* types including this pith
    # satisfy this superclass. In this case, return the passed cause as is.
    if hint_child is Any:
        return cause
    # Else, this superclass is unignorable.

    # Arbitrary object uniquely identifying this superclass.
    hint_child_sign = get_hint_pep_sign_or_none(hint_child)

    # If this child hint is a forward reference to a superclass...
    if hint_child_sign is HintSignForwardRef:
        # Superclass referred to by this absolute or relative forward reference.
        hint_child = import_pep484585_ref_type(
            hint=hint_child,  # type: ignore[arg-type]
            cls_stack=cause.cls_stack,
            func=cause.func,
            exception_cls=BeartypeCallHintForwardRefException,
            exception_prefix=cause.exception_prefix,
        )
    # Else, this child hint is *NOT* a forward reference.
    #
    # If this child hint is a union of superclasses, reduce this union to a
    # tuple of superclasses. Only the latter is safely passable as the second
    # parameter to the issubclass() builtin under all supported Python versions.
    elif hint_child_sign is HintSignUnion:
        hint_child = get_hint_pep_args(hint_child)
    # Else, this child hint is *NOT* a union. By process of elimination, this
    # child hint *MUST be a class. In this case, preserve this class as is.

    # If this child hint is *NOT* an issubclassable object, raise an exception.
    #
    # Technically, this validation is only necessary when this child hint was a
    # forward reference. Pragmatically, there's *NO* harm in performing this
    # validation in all possible cases. Ergo, we do. *shrug*
    die_unless_object_issubclassable(
        obj=hint_child,
        exception_cls=_BeartypeCallHintPepRaiseException,
        exception_prefix=cause.exception_prefix,

        # If this child hint is still a forward reference, raise an exception.
        # Ideally, the above conditional should already have resolved all
        # forward references.
        is_forwardref_valid=False,
    )
    # Else, this child hint is an issubclassable object.

    # If this pith subclasses this superclass, return the passed cause as is.
    if is_type_subclass(cause.pith, hint_child):
        return cause
    # Else, this pith does *NOT* subclass this superclass. In this case...
    else:
        # Output cause to be returned, permuted from this input cause.
        cause_return = cause.permute()

        # Description of this superclasses, defined as either...
        hint_child_label = (
            # If this superclass is a type, a description of this type;
            label_type(cls=hint_child, is_color=cause.conf.is_color)
            if isinstance(hint_child, type) else
            # Else, this superclass is a tuple of types. In this case, a
            # description of these types...
            join_delimited_disjunction_types(
                types=hint_child, is_color=cause.conf.is_color)
        )

        # Human-readable string describing this failure.
        cause_return.cause_str_or_none = (
            f'{represent_pith(cause.pith)} not subclass of {hint_child_label}')

    # Return this cause.
    return cause_return
