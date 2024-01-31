#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2024 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`484`- and :pep:`585`-compliant **forward reference type hint
utilities** (i.e., callables generically applicable to both :pep:`484`- and
:pep:`585`-compliant forward reference type hints).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.roar import BeartypeDecorHintForwardRefException
from beartype._data.cls.datacls import TYPES_PEP484585_REF
from beartype._data.hint.datahinttyping import (
    Pep484585ForwardRef,
    TypeException,
)
from beartype._util.cache.utilcachecall import callable_cached
from beartype._util.cls.utilclstest import die_unless_type
from beartype._util.module.utilmodget import get_object_module_name_or_none
from beartype._util.module.utilmodimport import import_module_attr
from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_9

# ....................{ VALIDATORS                         }....................
#FIXME: Validate that this forward reference string is *NOT* the empty string.
#FIXME: Validate that this forward reference string is a syntactically valid
#"."-delimited concatenation of Python identifiers. We already have logic
#performing that validation somewhere, so let's reuse that here, please.
#Right. So, we already have an is_identifier() tester; now, we just need to
#define a new die_unless_identifier() validator.
def die_unless_hint_pep484585_ref(
    # Mandatory parameters.
    hint: object,

    # Optional parameters.
    exception_cls: TypeException = BeartypeDecorHintForwardRefException,
    exception_prefix: str = '',
) -> None:
    '''
    Raise an exception unless the passed object is either a :pep:`484`- or
    :pep:`585`-compliant **forward reference type hint** (i.e., object
    referring to a user-defined class that typically has yet to be defined).

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
    exception_cls : Type[Exception]
        Type of exception to be raised in the event of a fatal error. Defaults
        to :exc:`.BeartypeDecorHintForwardRefException`.
    exception_prefix : str, optional
        Human-readable label prefixing the representation of this object in the
        exception message. Defaults to the empty string.

    Raises
    ------
    exception_cls
        If this object is *not* a forward reference type hint.
    '''

    # If this object is *NOT* a forward reference type hint, raise an exception.
    if not isinstance(hint, TYPES_PEP484585_REF):
        assert isinstance(exception_cls, type), (
            f'{repr(exception_cls)} not exception subclass.')
        assert isinstance(exception_prefix, str), (
            f'{repr(exception_prefix)} not string.')

        raise exception_cls(
            f'{exception_prefix}type hint {repr(hint)} not forward reference '
            f'(i.e., neither string nor "typing.ForwardRef" object).'
        )
    # Else, this object is a forward reference type hint.

# ....................{ GETTERS ~ kind : forwardref        }....................
@callable_cached
def get_hint_pep484585_ref_name(hint: Pep484585ForwardRef) -> str:
    '''
    Possibly unqualified classname referred to by the passed :pep:`484`- or
    :pep:`585`-compliant **forward reference type hint** (i.e., object
    indirectly referring to a user-defined class that typically has yet to be
    defined).

    Specifically, this function returns:

    * If this hint is a :pep:`484`-compliant forward reference (i.e., instance
      of the :class:`typing.ForwardRef` class), the typically unqualified
      classname referred to by that reference. Although :pep:`484` only
      explicitly supports unqualified classnames as forward references, the
      :class:`typing.ForwardRef` class imposes *no* runtime constraints and thus
      implicitly supports both qualified and unqualified classnames.
    * If this hint is a :pep:`585`-compliant forward reference (i.e., string),
      this string as is referring to a possibly unqualified classname. Both
      :pep:`585` and :mod:`beartype` itself impose *no* runtime constraints and
      thus explicitly support both qualified and unqualified classnames.

    This getter is memoized for efficiency.

    Parameters
    ----------
    hint : object
        Forward reference to be inspected.

    Returns
    -------
    str
        Possibly unqualified classname referred to by this forward reference.

    Raises
    ------
    exception_cls
        If this forward reference is *not* actually a forward reference.

    See Also
    --------
    :func:`.get_hint_pep484585_ref_name_relative_to_object`
        Getter returning fully-qualified forward reference classnames.
    '''

    # If this is *NOT* a forward reference type hint, raise an exception.
    die_unless_hint_pep484585_ref(hint)

    # If this hint is a string, return this string as is.
    if isinstance(hint, str):
        return hint
    # Else, this hint is *NOT* a string. However, this hint is a forward
    # reference. By process of elimination, this hint *MUST* be an instance of
    # the PEP 484-compliant "typing.ForwardRef" class.

    # Unqualified basename of the type referred to by this reference.
    hint_name = hint.__forward_arg__

    # If the active Python interpreter targets >= Python 3.9, then this
    # "typing.ForwardRef" object defines an additional optional
    # "__forward_module__: Optional[str] = None" dunder attribute whose value is
    # either:
    # * If Python passed the "module" parameter when instantiating this
    #   "typing.ForwardRef" object, the value of that parameter -- which is
    #   presumably the fully-qualified name of the module to which this
    #   presumably relative forward reference is relative to.
    # * Else, "None".
    #
    # Note that:
    # * This requires violating privacy encapsulation by accessing dunder
    #   attributes unique to "typing.ForwardRef" objects.
    # * This object defines a significant number of other "__forward_"-prefixed
    #   dunder instance variables, which exist *ONLY* to enable the blatantly
    #   useless typing.get_type_hints() function to avoid repeatedly (and thus
    #   inefficiently) reevaluating the same forward reference. *sigh*
    #
    # In this case...
    if IS_PYTHON_AT_LEAST_3_9:
        # Fully-qualified name of the module to which this presumably relative
        # forward reference is relative to if any *OR* "None" otherwise (i.e.,
        # if *NO* such name was passed at forward reference instantiation time).
        hint_module_name = hint.__forward_module__

        # If...
        if (
            # This reference was instantiated with a module name...
            hint_module_name and
            # This reference is actually relative (rather than already absolute)
            # and could thus benefit from canonicalization...
            '.' not in hint_name
        ):
            # Canonicalize this unqualified basename into a fully-qualified name
            # relative to this module name.
            hint_name = f'{hint_module_name}.{hint_name}'
        # Else, this reference is presumably relative to the external function
        # call transitively responsible for this call stack. Since we can't
        # particularly do anything about that from here, percolate this relative
        # forward reference back up the call stack to the caller.
    # Else, the active Python interpreter targets < Python 3.9 and thus fails to
    # define the  "__forward_module__" dunder attribute.

    # Return this possibly qualified name.
    return hint_name


#FIXME: Unit test against nested classes.
def get_hint_pep484585_ref_name_relative_to_object(
    # Mandatory parameters.
    hint: Pep484585ForwardRef,
    obj: object,

    # Optional parameters.
    exception_cls: TypeException = BeartypeDecorHintForwardRefException,
    exception_prefix: str = '',
) -> str:
    '''
    Fully-qualified classname referred to by the passed **forward reference type
    hint** (i.e., object indirectly referring to a user-defined class that
    typically has yet to be defined) canonicalized if this hint is unqualified
    relative to the module declaring the passed object (e.g., callable, class).

    This getter is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator), as the implementation mostly reduces to
    an efficient one-liner.

    Parameters
    ----------
    hint : object
        Forward reference to be canonicalized.
    obj : object
        Object to canonicalize the classname referred to by this forward
        reference if that classname is unqualified (i.e., relative).

    Returns
    -------
    str
        Fully-qualified classname referred to by this forward reference
        relative to this callable.

    Raises
    ------
    exception_cls
        If either:

        * This forward reference is *not* actually a forward reference.
        * This forward reference is **relative** (i.e., contains *no* ``.``
          delimiters) and the passed ``obj`` does *not* define the
          ``__module__`` dunder instance variable.

    See Also
    --------
    :func:`.get_hint_pep484585_ref_name`
        Getter returning possibly unqualified forward reference classnames.
    '''

    # Possibly unqualified classname referred to by this forward reference.
    hint_name = get_hint_pep484585_ref_name(hint)

    # If this classname contains one or more "." characters and is thus already
    # (...hopefully) fully-qualified, return this classname as is.
    if '.' in hint_name:
        return hint_name
    # Else, this classname contains *NO* "." characters and is thus *NOT*
    # fully-qualified.

    # Fully-qualified name of the module declaring the passed object if any *OR*
    # "None" otherwise.
    #
    # Note that, although *ALL* objects should define the "__module__" instance
    # variable underlying the call to this getter function, *SOME* real-world
    # objects do not. For this reason, we intentionally:
    # * Call the get_object_module_name_or_none() rather than
    #   get_object_module_name() function.
    # * Explicitly detect "None".
    # * Raise a human-readable exception.
    #
    # Doing so produces significantly more readable exceptions than merely
    # calling get_object_module_name(). Problematic objects include:
    # * Objects defined in Sphinx-specific "conf.py" configuration files. In all
    #   likelihood, Sphinx is running these files in some sort of arcane and
    #   non-standard manner (over which beartype has *NO* control).
    obj_module_name = get_object_module_name_or_none(obj)

    # If this object is declared by a module, canonicalize the name of this
    # reference by returning the "."-delimited concatenation of the
    # fully-qualified name of this module with this unqualified classname.
    if obj_module_name:
        return f'{get_object_module_name_or_none(obj)}.{hint_name}'
    # Else, this object is *NOT* declared by a module.
    #
    # If this object is the "None" singleton, this function was almost certainly
    # transitively called by a high-level "beartype.door" runtime type-checker
    # (e.g., is_bearable(), die_if_unbearable()). In this case, raise an
    # exception appropriate for this common edge case.
    elif obj is None:
        raise exception_cls(
            f'{exception_prefix}relative forward reference "{hint_name}" '
            f'currently only type-checkable in type hints annotating '
            f'@beartype-decorated callables and classes. '
            f'For your own safety and those of the codebases you love, '
            f'consider canonicalizing this '
            f'relative forward reference into an absolute forward reference '
            f'(e.g., by replacing "{hint_name}" with '
            f'"{{some_package}}.{hint_name}").'
        )
    # Else, this object is *NOT* the "None" singleton.

    # Raise a generic exception suitable for an arbitrary object.
    raise exception_cls(
        f'{exception_prefix}relative forward reference "{hint_name}" '
        f'not type-checkable against module-less {repr(obj)}.'
    )

# ....................{ IMPORTERS                          }....................
#FIXME: Unit test us up, please.
def import_pep484585_ref_type_relative_to_object(
    # Mandatory parameters.
    hint: Pep484585ForwardRef,
    obj: object,

    # Optional parameters.
    exception_cls: TypeException = BeartypeDecorHintForwardRefException,
    exception_prefix: str = '',
) -> type:
    '''
    Class referred to by the passed :pep:`484` or :pep:`585`-compliant
    **forward reference type hint** (i.e., object indirectly referring to a
    user-defined class that typically has yet to be defined) canonicalized if
    this hint is unqualified relative to the module declaring the passed object
    (e.g., callable, class).

    This getter is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator), as the passed object is typically a
    :func:`beartype.beartype`-decorated callable passed exactly once to this
    function.

    Parameters
    ----------
    hint : Pep484585ForwardRef
        Forward reference type hint to be resolved.
    obj : object
        Object to canonicalize the classname referred to by this forward
        reference if that classname is unqualified (i.e., relative).
    exception_cls : Type[Exception]
        Type of exception to be raised in the event of a fatal error. Defaults
        to :exc:`.BeartypeDecorHintForwardRefException`.
    exception_prefix : str, optional
        Human-readable label prefixing the representation of this object in the
        exception message. Defaults to the empty string.

    Returns
    -------
    type
        Class referred to by this forward reference.

    Raises
    ------
    exception_cls
        If the object referred to by this forward reference is either undefined
        *or* is defined but is not a class.
    '''

    # Human-readable label prefixing exception messages raised below.
    exception_prefix = f'{exception_prefix}{repr(hint)} referenced class '

    # Fully-qualified classname referred to by this forward reference relative
    # to this object.
    hint_forwardref_classname = (
        get_hint_pep484585_ref_name_relative_to_object(
            hint=hint,
            obj=obj,
            exception_cls=exception_cls,
            exception_prefix=exception_prefix,
        ))

    # Object dynamically imported from this classname.
    hint_forwardref_type = import_module_attr(
        module_attr_name=hint_forwardref_classname,
        exception_cls=exception_cls,
        exception_prefix=exception_prefix,
    )

    # If this object is *NOT* a class, raise an exception.
    die_unless_type(
        cls=hint_forwardref_type,
        exception_cls=exception_cls,
        exception_prefix=exception_prefix,
    )
    # Else, this object is a class.

    # Return this class.
    return hint_forwardref_type
