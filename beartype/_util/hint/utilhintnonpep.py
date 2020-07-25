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

# ....................{ IMPORTS                           }....................
from beartype.roar import BeartypeDecorHintValueNonPepException
from beartype._util.cache.utilcachecall import callable_cached
from beartype._util.hint.pep.utilhintpeptest import die_if_hint_pep

# See the "beartype.__init__" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ EXCEPTIONS                        }....................
@callable_cached
def die_unless_hint_nonpep(
    # Mandatory parameters.
    hint: object,

    # Optional parameters.
    hint_label: str = 'Type hint',
    is_str_valid: bool = True,
    exception_cls: type = BeartypeDecorHintValueNonPepException,
) -> None:
    '''
    Raise an exception unless the passed object is a **PEP-noncompliant type
    hint** (i.e., :mod:`beartype`-specific annotation *not* compliant with
    annotation-centric PEPs).

    This validator is memoized for efficiency.

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

        * ``True``, this object is valid only if this object is either a class,
          classname, or tuple of classes and/or classnames.
        * ``False``, this object is valid only if this object is either a class
          or tuple of classes.
    exception_cls : Optional[type]
        Type of the exception to be raised by this function. Defaults to
        :class:`BeartypeDecorHintValueNonPepException`.

    Raises
    ----------
    exception_type
        If this object is neither:

        * A **type** (i.e., class).
        * If ``is_str_valid``, a **string** (i.e., forward reference specified
          as either a fully-qualified or unqualified classname).
        * A **non-empty tuple** (i.e., semantic union of types) containing one
          or more:

          * Types.
          * If ``is_str_valid``, strings.
    '''
    assert isinstance(hint_label, str), (
        '{!r} not a string.'.format(hint_label))
    assert isinstance(is_str_valid, bool), (
        '{!r} not a boolean.'.format(is_str_valid))
    assert isinstance(exception_cls, type), (
        '{!r} not a type.'.format(exception_cls))

    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # BEGIN: Synchronize changes here with tuple iteration performed below.
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    # If this object is a forward reference (i.e., fully-qualified or
    # unqualified classname), this string refers to either:
    #
    # * A PEP-noncompliant type hint and is thus valid.
    # * A PEP 484 type hint and is thus invalid.
    #
    # However, forward references are only safely resolvable at call time.
    # Attempting to resolve a forward reference at an earlier time usually
    # induces a circular import dependency (i.e., edge-case in which two
    # modules mutually import one other, usually transitively rather than
    # directly). Circumventing these dependencies is the entire raison d'etre
    # (i.e., reason for existence) of forward references in the first place.
    #
    # Validating this reference here would require importing the module
    # defining this attribute. Since the @beartype decorator calling this
    # function is typically invoked via the global scope of a source module,
    # importing this target module here would be functionally equivalent to
    # importing that target module from that source module -- triggering a
    # circular import dependency in susceptible source modules.
    #
    # Ergo, there exists no means of differentiating between these two cases at
    # this presumably early time. Instead, we silently accept this string as is
    # for now and subsequently validate its type immediately after resolving
    # this string to its referent at wrapper function call time.
    if isinstance(hint, str):
        # If forward references are unsupported, raise an exception.
        if not is_str_valid:
            raise exception_cls(
                '{} forward reference {!r} unsupported.'.format(
                    hint_label, hint))

        # Else, silently accept this forward reference as is for now.
        return
    # Else, this object is *NOT* a forward reference.

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
    # Else, this object is neither a forward reference nor class.

    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # END: Synchronize changes above with tuple iteration performed below.
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    # If this object is a tuple...
    if isinstance(hint, tuple):
        # If this tuple is empty, raise an exception.
        if not hint:
            raise exception_cls('{} tuple empty.'.format(hint_label))
        # Else, this tuple is non-empty.

        # For each item of this tuple...
        for hint_item in hint:
            # Duplicate the above logic. For negligible efficiency gains (and
            # more importantly to avoid exhausting the stack), avoid calling
            # this function recursively to do so. *shrug*

            # If this item is a forward reference,
            if isinstance(hint_item, str):
                # If forward references are unsupported, raise an exception.
                if not is_str_valid:
                    raise exception_cls(
                        '{} {!r} forward reference {!r} unsupported.'.format(
                            hint_label, hint, hint_item))

                # Else, silently accept this item.
                continue
            # Else, this item is *NOT* a forward reference.

            # If this item is a class...
            if isinstance(hint_item, type):
                # If this is a PEP-compliant class, raise an exception.
                die_if_hint_pep(
                    hint=hint,
                    hint_label=hint_label,
                    exception_cls=exception_cls,
                )

                # Else, this is a PEP-noncompliant class. In this case,
                # silently accept this class as is.
                continue

            # Else, this item is neither a forward reference nor class. Ergo,
            # this item is *NOT* a PEP-noncompliant type hint.
            #
            # If forward references are supported, raise an exception noting
            # that.
            if is_str_valid:
                raise exception_cls(
                    '{} {!r} item {!r} neither type nor string.'.format(
                        hint_label, hint, hint_item))
            # Else, forward references are unsupported. In this case, raise an
            # exception noting that.
            else:
                raise exception_cls(
                    '{} {!r} item {!r} not type.'.format(
                        hint_label, hint, hint_item))

        # Since the prior iteration failed to raise an exception, this tuple
        # contains only forward references and/or PEP-noncompliant classes.
        # Ergo, this tuple is a PEP-noncompliant type hint. Accept this as is.
        return

    # Else, this object is neither a forward reference, class, nor tuple. Ergo,
    # this object is *NOT* a PEP-noncompliant type hint.
    #
    # If forward references are supported, raise an exception noting that.
    if is_str_valid:
        raise exception_cls(
            '{} {!r} neither type, string, nor '
            'tuple of types and strings.'.format(hint_label, hint))
    # Else, forward references are unsupported. In this case, raise an
    # exception noting that.
    else:
        raise exception_cls(
            '{} {!r} neither type nor tuple of types.'.format(
                hint_label, hint))
