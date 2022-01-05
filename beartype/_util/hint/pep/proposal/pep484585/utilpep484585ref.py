#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2022 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`484`- and :pep:`585`-compliant **forward reference type hint
utilities** (i.e., callables generically applicable to both :pep:`484`- and
:pep:`585`-compliant forward reference type hints).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                           }....................
from beartype.roar import BeartypeDecorHintForwardRefException
from beartype._util.cls.utilclstest import die_unless_type
from beartype._util.hint.pep.proposal.pep484.utilpep484ref import (
    HINT_PEP484_FORWARDREF_TYPE,
    get_hint_pep484_forwardref_type_basename,
    is_hint_pep484_forwardref,
)
from beartype._util.mod.utilmodimport import import_module_attr
from beartype._util.mod.utilmodule import get_object_module_name
from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_7
from beartype._data.datatyping import TypeException
from typing import Any, Union

# See the "beartype.cave" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ HINTS                             }....................
HINT_PEP484585_FORWARDREF_TYPES = (str, HINT_PEP484_FORWARDREF_TYPE)
'''
Tuple union of all :pep:`484`- or :pep:`585`-compliant **forward reference
types** (i.e., classes of all forward reference objects).

Specifically, this union contains:

* :class:`str`, the class of all :pep:`585`-compliant forward reference objects
  implicitly preserved by all :pep:`585`-compliant type hint factories when
  subscripted by a string.
* :class:`HINT_PEP484_FORWARDREF_TYPE`, the class of all :pep:`484`-compliant
  forward reference objects implicitly created by all :mod:`typing` type hint
  factories when subscripted by a string.

While :pep:`585`-compliant type hint factories preserve string-based forward
references as is, :mod:`typing` type hint factories coerce string-based forward
references into higher-level objects encapsulating those strings. The latter
approach is the demonstrably wrong approach, because encapsulating strings only
harms space and time complexity at runtime with *no* concomitant benefits.
'''


HINT_PEP484585_FORWARDREF_UNION: Any = (
    # If the active Python interpreter targets Python >= 3.7, include the sane
    # "typing.ForwardRef" type in this union;
    Union[str, HINT_PEP484_FORWARDREF_TYPE]
    if IS_PYTHON_AT_LEAST_3_7 else
    # Else, the active Python interpreter targets Python 3.6. In this case,
    # exclude the insane "typing._ForwardRef" type from this union. Naively
    # including that type here induces fatal runtime exceptions resembling:
    #     AttributeError: type object '_ForwardRef' has no attribute '_gorg'
    # Since "Union[str]" literally reduces to simply "str", we prefer the
    # latter here for clarity.
    str
)
'''
Union of all :pep:`484`- or :pep:`585`-compliant **forward reference types**
(i.e., classes of all forward reference objects).

See Also
----------
:data`HINT_PEP484585_FORWARDREF_TYPES`
    Further details.
'''

# ....................{ VALIDATORS ~ kind : forwardref    }....................
def die_unless_hint_pep484585_forwardref(
    # Mandatory parameters.
    hint: object,

    # Optional parameters.
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
    exception_prefix : str, optional
        Human-readable label prefixing the representation of this object in the
        exception message. Defaults to the empty string.

    Raises
    ----------
    :exc:`BeartypeDecorHintForwardRefException`
        If this object is *not* a forward reference type hint.
    '''

    # If this is *NOT* a forward reference type hint, raise an exception.
    if not isinstance(hint, HINT_PEP484585_FORWARDREF_TYPES):
        raise BeartypeDecorHintForwardRefException(
            f'{exception_prefix}type hint {repr(hint)} not forward reference '
            f'(i.e., neither string nor "typing.ForwardRef" instance).'
        )

# ....................{ GETTERS ~ kind : forwardref       }....................
#FIXME: Unit test against nested classes.
#FIXME: Validate that this forward reference string is *NOT* the empty string.
#FIXME: Validate that this forward reference string is a syntactically valid
#"."-delimited concatenation of Python identifiers. We already have logic
#performing that validation somewhere, so let's reuse that here, please.
#Right. So, we already have an is_identifier() tester; now, we just need to
#define a new die_unless_identifier() validator.
def get_hint_pep484585_forwardref_classname(
    hint: HINT_PEP484585_FORWARDREF_UNION) -> str:
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
      :class:`typing.ForwardRef` class imposes *no* runtime constraints and
      thus implicitly supports both qualified and unqualified classnames.
    * If this hint is a :pep:`585`-compliant forward reference (i.e., string),
      this string as is referring to a possibly unqualified classname. Both
      :pep:`585` and :mod:`beartype` itself impose *no* runtime constraints and
      thus explicitly support both qualified and unqualified classnames.

    This getter is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator), as the implementation trivially reduces
    to an efficient one-liner.

    Parameters
    ----------
    hint : object
        Forward reference to be inspected.

    Returns
    ----------
    str
        Possibly unqualified classname referred to by this forward reference.

    Raises
    ----------
    BeartypeDecorHintForwardRefException
        If this forward reference is *not* actually a forward reference.

    See Also
    ----------
    :func:`get_hint_pep484585_forwardref_classname_relative_to_object`
        Getter returning fully-qualified forward reference classnames.
    '''

    # If this is *NOT* a forward reference type hint, raise an exception.
    die_unless_hint_pep484585_forwardref(hint)

    # Return either...
    return (
        # If this hint is a PEP 484-compliant forward reference, the typically
        # unqualified classname referred to by this reference.
        get_hint_pep484_forwardref_type_basename(hint)
        if is_hint_pep484_forwardref(hint) else
        # Else, this hint is a string. In this case, this string as is.
        hint
    )


#FIXME: Unit test against nested classes.
def get_hint_pep484585_forwardref_classname_relative_to_object(
    hint: HINT_PEP484585_FORWARDREF_UNION, obj: object) -> str:
    '''
    Fully-qualified classname referred to by the passed **forward reference
    type hint** (i.e., object indirectly referring to a user-defined class that
    typically has yet to be defined) canonicalized if this hint is unqualified
    relative to the module declaring the passed object (e.g., callable, class).

    This tester is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator), as the implementation trivially reduces
    to an efficient one-liner.

    Parameters
    ----------
    hint : object
        Forward reference to be canonicalized.
    obj : object
        Object to canonicalize the classname referred to by this forward
        reference if that classname is unqualified (i.e., relative).

    Returns
    ----------
    str
        Fully-qualified classname referred to by this forward reference
        relative to this callable.

    Raises
    ----------
    BeartypeDecorHintForwardRefException
        If this forward reference is *not* actually a forward reference.
    _BeartypeUtilModuleException
        If ``module_obj`` does *not* define the ``__module__`` dunder instance
        variable.

    See Also
    ----------
    :func:`get_hint_pep484585_forwardref_classname`
        Getter returning possibly unqualified forward reference classnames.
    '''

    # Possibly unqualified classname referred to by this forward reference.
    forwardref_classname = get_hint_pep484585_forwardref_classname(hint)

    # Return either...
    return (
        # If this classname contains one or more "." characters and is thus
        # already hopefully fully-qualified, this classname as is;
        forwardref_classname
        if '.' in forwardref_classname else
        # Else, the "."-delimited concatenation of the fully-qualified name of
        # the module declaring this class with this unqualified classname.
        f'{get_object_module_name(obj)}.{forwardref_classname}'
    )

# ....................{ IMPORTERS                         }....................
#FIXME: Unit test us up, please.
def import_pep484585_forwardref_type_relative_to_object(
    # Mandatory parameters.
    hint: HINT_PEP484585_FORWARDREF_UNION,
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
    hint : HINT_PEP484585_FORWARDREF_UNION
        Forward reference type hint to be resolved.
    obj : object
        Object to canonicalize the classname referred to by this forward
        reference if that classname is unqualified (i.e., relative).
    exception_cls : Type[Exception]
        Type of exception to be raised by this function. Defaults to
        :class:`BeartypeDecorHintForwardRefException`.
    exception_prefix : str, optional
        Human-readable label prefixing the representation of this object in the
        exception message. Defaults to the empty string.

    Returns
    ----------
    type
        Class referred to by this forward reference.

    Raises
    ----------
    :exc:`exception_cls`
        If the object referred to by this forward reference is either undefined
        *or* is defined but is not a class.
    '''

    # Human-readable label prefixing exception messages raised below.
    EXCEPTION_PREFIX = f'{exception_prefix}{repr(hint)} referenced class '

    # Fully-qualified classname referred to by this forward reference relative
    # to this object.
    hint_forwardref_classname = (
        get_hint_pep484585_forwardref_classname_relative_to_object(
            hint=hint, obj=obj))

    # Object dynamically imported from this classname.
    hint_forwardref_type = import_module_attr(
        module_attr_name=hint_forwardref_classname,
        exception_cls=exception_cls,
        exception_prefix=EXCEPTION_PREFIX,
    )

    # If this object is *NOT* a class, raise an exception.
    die_unless_type(
        cls=hint_forwardref_type,
        exception_cls=exception_cls,
        exception_prefix=EXCEPTION_PREFIX,
    )
    # Else, this object is a class.

    # Return this class.
    return hint_forwardref_type
