#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2020 Cecil Curry.
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

# See the "beartype.__init__" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ EXCEPTIONS                        }....................
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
    exception_type
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
    assert isinstance(hint_label, str), (
        f'{repr(hint_label)} not string.')
    assert isinstance(exception_cls, type), (
        f'{repr(exception_cls)} not type.')

    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # BEGIN: Synchronize changes here with both:
    # * The is_hint_nonpep() tester defined below.
    # * Tuple iteration performed below.
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    # Avoid circular import dependencies.
    from beartype._util.hint.pep.utilhintpeptest import die_if_hint_pep

    # If this object is a class...
    if isinstance(hint, type):
        # If this is a PEP-compliant class, raise an exception.
        die_if_hint_pep(
            hint=hint,
            hint_label=hint_label,
            exception_cls=exception_cls,
        )

        # Else, this is a PEP-noncompliant class. In this case, silently accept
        # this class as is.
        return
    # Else, this object is *NOT* a class.

    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # END: Synchronize changes above with tuple iteration performed below.
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    # If this object is a tuple...
    if isinstance(hint, tuple):
        # If this tuple is empty, raise an exception.
        if not hint:
            raise exception_cls(f'{hint_label} tuple empty.')
        # Else, this tuple is non-empty.

        # For each item of this tuple...
        for hint_item in hint:
            # Duplicate the above logic. For negligible efficiency gains (and
            # more importantly to avoid exhausting the stack), avoid calling
            # this function recursively to do so. *shrug*

            # If this item is a class...
            if isinstance(hint_item, type):
                # If this is a PEP-compliant class, raise an exception.
                die_if_hint_pep(
                    hint=hint_item,
                    hint_label=hint_label,
                    exception_cls=exception_cls,
                )
                # Else, this is a PEP-noncompliant class. In this case,
                # silently accept this class as is.
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

    # Else, this object is neither a forward reference, class, nor tuple. Ergo,
    # this object is *NOT* a PEP-noncompliant type hint.
    #
    # If forward references are supported, raise an exception noting that.
    if is_str_valid:
        raise exception_cls(
            f'{hint_label} {repr(hint)} '
            f'neither type, string, nor tuple of types and strings.'
        )
    # Else, forward references are unsupported. In this case, raise an
    # exception noting that.
    else:
        raise exception_cls(
            f'{hint_label} {repr(hint)} neither type nor tuple of types.')

# ....................{ TESTERS                           }....................
@callable_cached
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

    This tester is memoized for efficiency.

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

    Raises
    ----------
    TypeError
        If this object is **unhashable** (i.e., *not* hashable by the builtin
        :func:`hash` function and thus unusable in hash-based containers like
        dictionaries and sets). All supported type hints are hashable.
    '''
    assert isinstance(is_str_valid, bool), f'{repr(is_str_valid)} not boolean.'

    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # BEGIN: Synchronize changes here with die_unless_hint_nonpep() above.
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    # Avoid circular import dependencies.
    from beartype._util.hint.pep.utilhintpeptest import is_hint_pep

    # Return true only if either...
    return (
        # If this object is a class, return true only if this is *NOT* a
        # PEP-compliant class, in which case this *MUST* be a PEP-noncompliant
        # class by definition.
        not is_hint_pep(hint) if isinstance(hint, type) else
        # Else, this object is neither a class nor forward reference.
        #
        # If this object is a non-empty tuple, return true only if each item of
        # this tuple is either a caller-permitted forward reference *OR* a
        # PEP-noncompliant class.
        all(
            not is_hint_pep(hint_item) if isinstance(hint_item, type) else
            is_str_valid               if isinstance(hint_item, str) else
            False
            for hint_item in hint
        ) if (isinstance(hint, tuple) and hint) else
        # Else, this object is neither a forward reference, class, nor
        # non-empty tuple. Return false, as this object is *NOT* a
        # PEP-noncompliant type hint.
        False
    )
