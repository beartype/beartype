#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2021 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype PEP-noncompliant type hint utilities.**

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ TODO                              }....................
#FIXME: Validate strings to be syntactically valid classnames via a globally
#scoped compiled regular expression. Raising early exceptions at decoration
#time is preferable to raising late exceptions at call time.
#FIXME: Indeed, we now provide such a callable:
#    from beartype._util.py.utilpymodule import die_unless_module_attr_name

# ....................{ IMPORTS                           }....................
from beartype.roar import BeartypeDecorHintNonPepException
from beartype._util.cache.utilcachecall import callable_cached
from beartype._util.cls.utilclstest import is_type_isinstanceable

# See the "beartype.cave" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ VALIDATORS                        }....................
#FIXME: Unit test this function with respect to non-isinstanceable classes.
def die_unless_hint_nonpep(
    # Mandatory parameters.
    hint: object,

    # Optional parameters.
    hint_label: str = 'Type hint',
    is_str_valid: bool = True,
    exception_cls: type = BeartypeDecorHintNonPepException,
) -> None:
    '''
    Raise an exception unless the passed object is a **PEP-noncompliant type
    hint** (i.e., :mod:`beartype`-specific annotation *not* compliant with
    annotation-centric PEPs).

    This validator is effectively (but technically *not*) memoized. See the
    :func:`beartype._util.hint.utilhinttest.die_unless_hint` validator.

    Parameters
    ----------
    hint : object
        Object to be validated.
    hint_label : Optional[str]
        Human-readable label prefixing this object's representation in the
        exception message raised by this function. Defaults to ``Type hint``.
    is_str_valid : Optional[bool]
        ``True`` only if this function permits this object to be a string.
        Defaults to ``True``. If this boolean is:

        * ``True``, this object is valid only if this object is either a class
          or tuple of classes and/or classnames.
        * ``False``, this object is valid only if this object is either a class
          or tuple of classes.
    exception_cls : Optional[type]
        Type of the exception to be raised by this function. Defaults to
        :class:`BeartypeDecorHintNonPepException`.

    Raises
    ----------
    TypeError
        If this object is **unhashable** (i.e., *not* hashable by the builtin
        :func:`hash` function and thus unusable in hash-based containers like
        dictionaries and sets). All supported type hints are hashable.
    exception_cls
        If this object is neither:

        * A non-:mod:`typing` type (i.e., class *not* defined by the
          :mod:`typing` module, whose public classes are used to instantiate
          PEP-compliant type hints or objects satisfying such hints that
          typically violate standard class semantics and thus require
          PEP-specific handling).
        * A **non-empty tuple** (i.e., semantic union of types) containing one
          or more:

          * Non-:mod:`typing` types.
          * If ``is_str_valid``, **strings** (i.e., forward references
            specified as either fully-qualified or unqualified classnames).
    '''

    # If this object is a PEP-noncompliant type hint, reduce to a noop.
    #
    # Note that this memoized call is intentionally passed positional rather
    # than keyword parameters to maximize efficiency.
    if is_hint_nonpep(hint, is_str_valid):
        return
    # Else, this object is *NOT* a PEP-noncompliant type hint. In this case,
    # subsequent logic raises an exception specific to the passed parameters.
    #
    # Note that the prior call has already validated "is_str_valid".
    assert isinstance(hint_label, str), f'{repr(hint_label)} not string.'
    assert isinstance(exception_cls, type), f'{repr(exception_cls)} not type.'

    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # BEGIN: Synchronize changes here with the is_hint_nonpep() tester below.
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    # If this object is a class...
    if isinstance(hint, type):
        # If this class is *NOT* PEP-noncompliant, raise an exception.
        _die_unless_hint_nonpep_type(
            hint=hint,
            hint_label=hint_label,
            exception_cls=exception_cls,
        )

        # Else, this class is isinstanceable. In this case, silently accept
        # this class as is.
        return
    # Else, this object is *NOT* a class.

    # If this object is a tuple, raise a tuple-specific exception.
    if isinstance(hint, tuple):
        die_unless_hint_nonpep_tuple(
            hint=hint,
            hint_label=hint_label,
            is_str_valid=is_str_valid,
            exception_cls=exception_cls,
        )

    # Else, this object is neither a forward reference, class, nor tuple. Ergo,
    # this object is *NOT* a PEP-noncompliant type hint.
    #
    # If forward references are supported, raise an exception noting that.
    if is_str_valid:
        raise exception_cls(
            f'{hint_label} {repr(hint)} '
            f'neither PEP-compliant nor -noncompliant '
            f'(e.g., standard class, forward reference, or '
            f'tuple of standard classes and forward references).'
        )
    # Else, forward references are unsupported. In this case, raise an
    # exception noting that.
    else:
        raise exception_cls(
            f'{hint_label} {repr(hint)} '
            f'neither PEP-compliant nor -noncompliant '
            f'(e.g., standard class or tuple of standard classes).'
        )


#FIXME: Optimize both this and the related _is_hint_nonpep_tuple() tester
#defined below. The key realization here is that EAFP is *MUCH* faster in this
#specific case than iteration. Why? Because iteration is guaranteed to
#internally raise a stop iteration exception, whereas EAFP only raises an
#exception if this tuple is invalid, in which case efficiency is no longer a
#concern. So, what do we do instead? Simple. We internally refactor:
#
#* If "is_str_valid" is True, we continue to perform the existing
#  implementation of both functions. *shrug*
#* Else, we:
#  * Perform a new optimized EAFP-style isinstance() check resembling that
#    performed by die_unless_hint_type_isinstanceable().
#  * Likewise for _is_hint_nonpep_tuple() vis-a-vis is_type_isinstanceable().
#FIXME: The "is_str_valid: bool = True," default is rather bad, because it's
#unsafe. The standard expectation is for tuples of types to be isinstanceable,
#which tuples of types and strings clearly are not. Ergo, we should refactor
#the codebase such that the default is instead:
#    is_str_valid: bool = False,
#FIXME: Unit test this function with respect to tuples containing
#non-isinstanceable classes.
def die_unless_hint_nonpep_tuple(
    # Mandatory parameters.
    hint: object,

    # Optional parameters.
    hint_label: str = 'Type hint',
    is_str_valid: bool = True,
    exception_cls: type = BeartypeDecorHintNonPepException,
) -> None:
    '''
    Raise an exception unless the passed object is a **PEP-noncompliant tuple**
    (i.e., :mod:`beartype`-specific tuple of one or more PEP-noncompliant types
    *not* compliant with annotation-centric PEPs).

    This validator is effectively (but technically *not*) memoized. See the
    :func:`beartype._util.hint.utilhinttest.die_unless_hint` validator.

    Parameters
    ----------
    hint : object
        Object to be validated.
    hint_label : Optional[str]
        Human-readable label prefixing this object's representation in the
        exception message raised by this function. Defaults to ``Type hint``.
    is_str_valid : Optional[bool]
        ``True`` only if this function permits this object to be a string.
        Defaults to ``True``. If this boolean is:

        * ``True``, this object is valid only if this object is either a class
          or tuple of classes and/or classnames.
        * ``False``, this object is valid only if this object is either a class
          or tuple of classes.
    exception_cls : Optional[type]
        Type of the exception to be raised by this function. Defaults to
        :class:`BeartypeDecorHintNonPepException`.

    Raises
    ----------
    TypeError
        If this object is **unhashable** (i.e., *not* hashable by the builtin
        :func:`hash` function and thus unusable in hash-based containers like
        dictionaries and sets). All supported type hints are hashable.
    exception_cls
        If this object is neither:

        * A non-:mod:`typing` type (i.e., class *not* defined by the
          :mod:`typing` module, whose public classes are used to instantiate
          PEP-compliant type hints or objects satisfying such hints that
          typically violate standard class semantics and thus require
          PEP-specific handling).
        * A **non-empty tuple** (i.e., semantic union of types) containing one
          or more:

          * Non-:mod:`typing` types.
          * If ``is_str_valid``, **strings** (i.e., forward references
            specified as either fully-qualified or unqualified classnames).
    '''

    # If this object is a PEP-noncompliant tuple, reduce to a noop.
    #
    # Note that this memoized call is intentionally passed positional rather
    # than keyword parameters to maximize efficiency.
    if _is_hint_nonpep_tuple(hint, is_str_valid):
        return
    # Else, this object is *NOT* a PEP-noncompliant tuple. In this case,
    # subsequent logic raises an exception specific to the passed parameters.
    #
    # Note that the prior call has already validated "is_str_valid".
    assert isinstance(hint_label, str), f'{repr(hint_label)} not string.'
    assert isinstance(exception_cls, type), f'{repr(exception_cls)} not type.'

    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # BEGIN: Synchronize changes here with the _is_hint_nonpep_tuple() tester.
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    # If this object is *NOT* a tuple, raise an exception.
    if not isinstance(hint, tuple):
        raise exception_cls(f'{hint_label} {repr(hint)} not tuple.')
    # Else, this object is a tuple.
    #
    # If this tuple is empty, raise an exception.
    elif not hint:
        raise exception_cls(f'{hint_label} tuple empty.')
    # Else, this tuple is non-empty.

    # For each item of this tuple...
    for hint_item in hint:
        # Duplicate the above logic. For negligible efficiency gains (and
        # more importantly to avoid exhausting the stack), avoid calling
        # this function recursively to do so. *shrug*

        # If this item is a class...
        if isinstance(hint_item, type):
            # If this class is *NOT* PEP-noncompliant, raise an exception.
            _die_unless_hint_nonpep_type(
                hint=hint_item,
                hint_label=hint_label,
                exception_cls=exception_cls,
            )
        # Else, this item is *NOT* a class.
        #
        # If this item is a forward reference...
        elif isinstance(hint_item, str):
            # If forward references are unsupported, raise an exception.
            if not is_str_valid:
                raise exception_cls(
                    f'{hint_label} {repr(hint)} '
                    f'forward reference "{hint_item}" unsupported.'
                )
            # Else, silently accept this item.
        # Else, this item is neither a class nor forward reference. Ergo,
        # this item is *NOT* a PEP-noncompliant type hint. In this case,
        # raise an exception whose message contextually depends on whether
        # forward references are permitted or not.
        else:
            raise exception_cls(
                f'{hint_label} {repr(hint)} item {repr(hint_item)} '
                f'{"neither type nor string" if is_str_valid else "not type"}.'
            )

# ....................{ VALIDATORS ~ private              }....................
def _die_unless_hint_nonpep_type(
    # Mandatory parameters.
    hint: object,

    # Optional parameters.
    hint_label: str = 'Type hint',
    exception_cls: type = BeartypeDecorHintNonPepException,
) -> None:
    '''
    Raise an exception unless the passed object is a **PEP-noncompliant type
    hint** (i.e., :mod:`beartype`-agnostic isinstanceable type *not* compliant
    with annotation-centric PEPs).

    This validator is effectively (but technically *not*) memoized. See the
    :func:`beartype._util.hint.utilhinttest.die_unless_hint` validator.

    Parameters
    ----------
    hint : object
        Object to be validated.
    hint_label : Optional[str]
        Human-readable label prefixing this object's representation in the
        exception message raised by this function. Defaults to ``Type hint``.
    exception_cls : Optional[type]
        Type of the exception to be raised by this function. Defaults to
        :class:`BeartypeDecorHintNonPepException`.

    Raises
    ----------
    TypeError
        If this object is **unhashable** (i.e., *not* hashable by the builtin
        :func:`hash` function and thus unusable in hash-based containers like
        dictionaries and sets). All supported type hints are hashable.
    exception_cls
        If this object is either:

        * *Not* isinstanceable.
        * A :mod:`typing` type (i.e., class defined by the :mod:`typing`
          module, whose public classes are used to instantiate PEP-compliant
          type hints or objects satisfying such hints that typically violate
          standard class semantics and thus require PEP-specific handling).
    '''

    # Avoid circular import dependencies.
    from beartype._util.hint.utilhinttest import (
        die_unless_hint_type_isinstanceable)
    from beartype._util.hint.pep.utilhintpeptest import die_if_hint_pep

    # If this class is PEP-compliant, raise an exception.
    die_if_hint_pep(
        hint=hint,
        hint_label=hint_label,
        exception_cls=exception_cls,
    )
    # Else, this class is PEP-noncompliant.

    # If this class is *NOT* isinstanceable, raise an exception.
    die_unless_hint_type_isinstanceable(
        hint=hint,
        hint_label=hint_label,
        exception_cls=exception_cls,
    )
    # Else, this class is isinstanceable.

# ....................{ TESTERS                           }....................
def is_hint_nonpep(
    # Mandatory parameters.
    hint: object,

    # Optional parameters.
    is_str_valid: bool = True,
) -> bool:
    '''
    ``True`` only if the passed object is a **PEP-noncompliant type hint**
    (i.e., :mod:`beartype`-specific annotation *not* compliant with
    annotation-centric PEPs).

    This tester is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator), as the implementation trivially reduces
    to an efficient one-liner.

    Parameters
    ----------
    hint : object
        Object to be inspected.
    is_str_valid : Optional[bool]
        ``True`` only if this function permits this object to be a string.
        Defaults to ``True``. If this boolean is:

        * ``True``, this object is valid only if this object is either a class
          or tuple of classes and/or classnames.
        * ``False``, this object is valid only if this object is either a class
          or tuple of classes.

    Returns
    ----------
    bool
        ``True`` only if this object is either:

        * A non-:mod:`typing` type (i.e., class *not* defined by the
          :mod:`typing` module, whose public classes are used to instantiate
          PEP-compliant type hints or objects satisfying such hints that
          typically violate standard class semantics and thus require
          PEP-specific handling).
        * A **non-empty tuple** (i.e., semantic union of types) containing one
          or more:

          * Non-:mod:`typing` types.
          * If ``is_str_valid``, **strings** (i.e., forward references
            specified as either fully-qualified or unqualified classnames).
    '''
    assert isinstance(is_str_valid, bool), f'{repr(is_str_valid)} not boolean.'

    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # BEGIN: Synchronize changes here with die_unless_hint_nonpep() above.
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    # Return true only if either...
    return (
        # If this object is a class, return true only if this is *NOT* a
        # PEP-compliant class, in which case this *MUST* be a PEP-noncompliant
        # class by definition.
        _is_hint_nonpep_type(hint) if isinstance(hint, type) else
        # Else, this object is *NOT* a class.
        #
        # If this object is a tuple, return true only if this tuple contains
        # only one or more caller-permitted forward references and
        # PEP-noncompliant classes.
        _is_hint_nonpep_tuple(hint, is_str_valid) if isinstance(hint, tuple)
        # Else, this object is neither a class nor tuple. Return false, as this
        # object *CANNOT* be PEP-noncompliant.
        else False
    )

# ....................{ TESTERS ~ private                 }....................
@callable_cached
def _is_hint_nonpep_tuple(
    # Mandatory parameters.
    hint: object,

    # Optional parameters.
    is_str_valid: bool = True,
) -> bool:
    '''
    ``True`` only if the passed object is a PEP-noncompliant non-empty tuple of
    one or more types.

    This tester is memoized for efficiency.

    Parameters
    ----------
    hint : object
        Object to be inspected.
    is_str_valid : Optional[bool]
        ``True`` only if this function permits this object to be a string.
        Defaults to ``True``. If this boolean is:

        * ``True``, this object is valid only if this object is a tuple of
          classes and/or classnames.
        * ``False``, this object is valid only if this object is a tuple of
          classes.

    Returns
    ----------
    bool
        ``True`` only if this object is a **non-empty tuple** (i.e., semantic
        union of types) containing one or more:

          * Non-:mod:`typing` types.
          * If ``is_str_valid``, **strings** (i.e., forward references
            specified as either fully-qualified or unqualified classnames).
    '''
    assert isinstance(is_str_valid, bool), f'{repr(is_str_valid)} not boolean.'

    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # BEGIN: Synchronize changes here with die_unless_hint_nonpep() above.
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    # Return true only if this object is...
    return (
        # A tuple *AND*...
        isinstance(hint, tuple) and
        # This tuple is non-empty *AND*...
        len(hint) > 0 and
        # Each item of this tuple is either a caller-permitted forward
        # reference *OR* a PEP-noncompliant class.
        all(
            _is_hint_nonpep_type(hint_item) if isinstance(hint_item, type) else
            is_str_valid                    if isinstance(hint_item, str) else
            False
            for hint_item in hint
        )
    )


def _is_hint_nonpep_type(hint: object) -> bool:
    '''
    ``True`` only if the passed object is a PEP-noncompliant type.

    This tester is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator), as the implementation trivially reduces
    to an efficient one-liner.

    Parameters
    ----------
    hint : object
        Object to be inspected.

    Returns
    ----------
    bool
        ``True`` only if this object is a PEP-noncompliant type.
    '''
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # BEGIN: Synchronize changes here with die_unless_hint_nonpep() above.
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    # Avoid circular import dependencies.
    from beartype._util.hint.pep.utilhintpeptest import is_hint_pep

    # Return true only if this object is isinstanceable and *NOT* a
    # PEP-compliant class, in which case this *MUST* be a PEP-noncompliant
    # class by definition.
    return is_type_isinstanceable(hint) and not is_hint_pep(hint)
