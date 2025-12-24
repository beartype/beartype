#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`484`--compliant **relative forward reference type hint
utilities** (i.e., low-level callables introspecting :pep:`484`-compliant
forward reference type hints whose resolution is relative to some parent
objects -- typically parent callables, types, or modules).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.roar import BeartypeDecorHintForwardRefException
from beartype._cave._cavefast import HintPep484RefTypes
from beartype._data.typing.datatyping import (
    HintPep484Ref,
    TupleStrOrNoneAndStr,
    TypeException,
)
from typing import Optional

# ....................{ RAISERS                            }....................
#FIXME: Validate that this forward reference string is *NOT* the empty string.
#FIXME: Validate that this forward reference string is a syntactically valid
#"."-delimited concatenation of Python identifiers. We already have logic
#performing that validation somewhere, so let's reuse that here, please.
#Right. So, we already have an is_identifier() tester; now, we just need to
#define a new die_unless_identifier() validator.
def die_unless_hint_pep484_ref(
    # Mandatory parameters.
    hint: object,

    # Optional parameters.
    exception_cls: TypeException = BeartypeDecorHintForwardRefException,
    exception_prefix: str = '',
) -> None:
    '''
    Raise an exception unless the passed object is a :pep:`484`-compliant
    **forward reference hint** (i.e., object referring to a user-defined type
    that typically has yet to be defined).

    Equivalently, this validator raises an exception if this object is neither:

    * A string whose value is the syntactically valid name of a class.
    * An instance of the :class:`typing.ForwardRef` class. The :mod:`typing`
      module implicitly replaces all strings subscripting :mod:`typing` objects
      (e.g., the ``MuhType`` in ``List['MuhType']``) with
      :class:`typing.ForwardRef` instances containing those strings as instance
      variables, for nebulous reasons that make little justifiable sense but
      what you gonna do 'cause this is 2020. *Fight me.*

    Parameters
    ----------
    hint : object
        Object to be validated.
    exception_cls : Type[Exception], default: BeartypeDecorHintForwardRefException
        Type of exception to be raised in the event of a fatal error. Defaults
        to :exc:`.BeartypeDecorHintForwardRefException`.
    exception_prefix : str, default: ''
        Human-readable substring prefixing raised exception messages. Defaults
        to the empty string.

    Raises
    ------
    exception_cls
        If this object is *not* a forward reference type hint.
    '''

    # If this object is *NOT* a forward reference type hint, raise an exception.
    if not isinstance(hint, HintPep484RefTypes):
        assert isinstance(exception_cls, type), (
            f'{repr(exception_cls)} not exception subclass.')
        assert isinstance(exception_prefix, str), (
            f'{repr(exception_prefix)} not string.')

        raise exception_cls(
            f'{exception_prefix}type hint {repr(hint)} not forward reference '
            f'(i.e., neither string nor "typing.ForwardRef" object).'
        )
    # Else, this object is a forward reference type hint.

# ....................{ GETTERS                            }....................
#FIXME: Unit test us up, please.
def get_hint_pep484_ref_names_relative(
    # Mandatory parameters.
    hint: HintPep484Ref,

    # Optional parameters.
    exception_cls: TypeException = BeartypeDecorHintForwardRefException,
    exception_prefix: str = '',
) -> TupleStrOrNoneAndStr:
    '''
    Possibly undefined fully-qualified module name and possibly qualified
    classname referred to by the passed :pep:`484`-compliant **forward reference
    hint** (i.e., object indirectly referring to a user-defined type that
    typically has yet to be defined).

    This getter is intentionally *not* memoized (e.g., by the
    ``callable_cached`` decorator), as the implementation mostly reduces to an
    efficient one-liner.

    Caveats
    -------
    **Callers are recommended to call the higher-level**
    :func:`.get_hint_pep484_ref_names_absolute` **getter rather than this
    lower-level getter,** which fails to guarantee canonicalization and is thus
    considerably less safe.

    Parameters
    ----------
    hint : object
        Forward reference to be introspected.
    exception_cls : Type[Exception], default: BeartypeDecorHintForwardRefException
        Type of exception to be raised in the event of a fatal error. Defaults
        to :exc:`.BeartypeDecorHintForwardRefException`.
    exception_prefix : str, default: ''
        Human-readable label prefixing the representation of this object in the
        exception message. Defaults to the empty string.

    Returns
    -------
    tuple[Optional[str], str]
        2-tuple ``(hint_module_name, hint_type_name)`` where:

        * ``hint_module_name`` is the possibly undefined fully-qualified module
          name referred to by this forward reference, defined as either:

          * If this forward reference is a :class:`typing.ForwardRef` object
            passed a module name at instantiation time via the ``module``
            parameter, this module name.
          * Else, :data:`None`.

        * ``hint_type_name`` is the possibly qualified classname referred to by this
          forward reference.

    Raises
    ------
    exception_cls
        If either:

        * This forward reference is *not* actually a forward reference.
        * This forward reference is **relative** (i.e., contains *no* ``.``
          delimiters) and either:

          * Neither the passed callable nor class define the ``__module__``
            dunder attribute.
          * The passed callable and/or class define the ``__module__``
            dunder attribute, but the values of those attributes all refer to
            unimportable modules that do *not* appear to physically exist.
    '''

    # If this is *NOT* a forward reference, raise an exception.
    die_unless_hint_pep484_ref(hint)
    # Else, this is a forward reference.

    # Possibly unqualified basename of the class to which reference refers.
    hint_name: str = None  # type: ignore[assignment]

    # Fully-qualified name of the module to which this reference is relative if
    # this reference is relative to an importable module *OR* "None" otherwise
    # (i.e., if this reference is either absolute and thus not relative to a
    # module *OR* relative to an unimportable module).
    #
    # Note that, although *ALL* callables and classes should define the
    # "__module__" instance variable underlying the call to this getter, *SOME*
    # callables and classes do not. For this reason, we intentionally:
    # * Call the get_object_module_name_or_none() getter rather than
    #   get_object_module_name().
    # * Explicitly detect "None".
    # * Raise a human-readable exception.
    #
    # Doing so produces significantly more readable exceptions than merely
    # calling get_object_module_name(). Problematic objects include:
    # * Objects defined in Sphinx-specific "conf.py" configuration files. In all
    #   likelihood, Sphinx is running these files in some sort of arcane and
    #   non-standard manner (over which beartype has *NO* control).
    hint_module_name: Optional[str] = None

    # If this reference is a string, the classname of this reference is this
    # reference itself.
    if isinstance(hint, str):
        hint_name = hint
    # Else, this reference is *NOT* a string. By process of elimination, this
    # reference *MUST* be a "typing.ForwardRef" instance. In this case...
    else:
        # Forward reference classname referred to by this reference.
        hint_name = hint.__forward_arg__

        # Fully-qualified name of the module to which this presumably
        # relative forward reference is relative to if any *OR* "None"
        # otherwise (i.e., if *NO* such name was passed at forward reference
        # instantiation time).
        #
        # Since the active Python interpreter targets >= Python 3.10, this
        # "typing.ForwardRef" object defines an optional "__forward_module__:
        # Optional[str] = None" dunder attribute whose value is either:
        # * If Python passed the "module" parameter when instantiating this
        #   "typing.ForwardRef" object, the value of that parameter -- which is
        #   presumably the fully-qualified name of the module to which this
        #   presumably relative forward reference is relative to.
        # * Else, "None".
        #
        # Note that:
        # * This requires violating privacy encapsulation by accessing dunder
        #   attributes unique to "typing.ForwardRef" objects. Sad, yet true.
        # * This object defines a significant number of other
        #   "__forward_"-prefixed dunder instance variables, which exist *ONLY*
        #   to enable the blatantly useless typing.get_type_hints() function to
        #   avoid repeatedly (and thus inefficiently) reevaluating the same
        #   forward reference. *sigh*
        # * Technically, this dunder attribute has been defined since at least
        #   Python >= 3.9.18. Sadly, one or more unknown earlier patch releases
        #   of the Python 3.9 development cycle do *NOT* support this. This is
        #   currently only safely usable under Python >= 3.10 -- all patch
        #   releases of which are known to define this dunder attribute.
        hint_module_name = hint.__forward_module__

    # Return metadata describing this forward reference relative to this module.
    return hint_module_name, hint_name

# ....................{ IMPORTERS                          }....................
#FIXME: Unit test us up, please.
def import_pep484_ref_type(
    # Mandatory parameters.
    hint: HintPep484Ref,

    # Optional parameters.
    exception_cls: TypeException = BeartypeDecorHintForwardRefException,
    exception_prefix: str = '',
    **kwargs
) -> type:
    '''
    Class referred to by the passed :pep:`484`-compliant **forward reference
    hint** (i.e., object indirectly referring to a user-defined type that
    typically has yet to be defined) canonicalized if this hint is unqualified
    relative to the module declaring the first of whichever of the passed owner
    type and/or callable is *not* :data:`None`.

    This getter is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator), as the passed object is typically a
    :func:`beartype.beartype`-decorated callable passed exactly once to this
    function.

    Parameters
    ----------
    hint : HintPep484Ref
        Forward reference type hint to be resolved.
    exception_cls : Type[Exception], default: BeartypeDecorHintForwardRefException
        Type of exception to be raised in the event of a fatal error. Defaults
        to :exc:`.BeartypeDecorHintForwardRefException`.
    exception_prefix : str, default: ''
        Human-readable label prefixing the representation of this object in the
        exception message. Defaults to the empty string.

    All remaining keyword parameters are passed as is to the lower-level
    :func:`.get_hint_pep484_ref_names_absolute` getter.

    Returns
    -------
    type
        Class referred to by this forward reference.

    Raises
    ------
    exception_cls
        If either:

        * This forward reference is *not* actually a forward reference.
        * This forward reference is **relative** (i.e., contains *no* ``.``
          delimiters) and either:

          * Neither the passed callable nor class define the ``__module__``
            dunder attribute.
          * The passed callable and/or class define the ``__module__``
            dunder attribute, but the values of those attributes all refer to
            unimportable modules that do *not* appear to physically exist.
        * The object referred to by this forward reference is either:

          * Undefined.
          * Defined but not a class.

    See Also
    --------
    :func:`.get_hint_pep484_ref_names_absolute`
        Further details.
    '''

    # Avoid circular import dependencies.
    from beartype._check.forward.reference.fwdrefmake import (
        make_forwardref_subbable_subtype)
    from beartype._util.hint.pep.proposal.pep484.forward.pep484refabsolute import (
        get_hint_pep484_ref_names_absolute)

    # Possibly undefined fully-qualified module name and possibly unqualified
    # classname referred to by this forward reference relative to this type
    # stack and callable.
    hint_module_name, hint_ref_name = get_hint_pep484_ref_names_absolute(
        hint=hint,
        exception_cls=exception_cls,
        exception_prefix=exception_prefix,
        **kwargs
    )

    # Forward reference proxy referring to this class.
    hint_ref = make_forwardref_subbable_subtype(
        hint_module_name, hint_ref_name)

    # Return the class dynamically imported from this proxy.
    return hint_ref.__type_beartype__
