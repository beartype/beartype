#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2020 Cecil Curry.
# See "LICENSE" for further details.

'''
**Beartype annotation and type hinting utilities.**

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                           }....................
from beartype.roar import BeartypeDecorHintValueException
from beartype._util import utilobj
from beartype._util.utilcache import callable_cached

# See the "beartype.__init__" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ EXCEPTIONS                        }....................
#FIXME: Validate strings to be syntactically valid classnames via a globally
#scaped compiled regular expression. Raising early exceptions at decoration
#time is preferable to raising late exceptions at call time.

def die_unless_hint_nonpep(
    # Mandatory parameters.
    hint: object,

    # Optional parameters.
    is_str_valid: bool = True,
    hint_label: str = 'Type hint',
    exception_cls: type = BeartypeDecorHintValueException,
) -> None:
    '''
    Raise an exception unless the passed object is a **PEP-noncompliant type
    hint** (i.e., :mod:`beartype`-specific annotation intentionally *not*
    compliant with annotation-centric PEPs).

    Parameters
    ----------
    obj : object
        Object to be validated.
    is_str_valid : Optional[bool]
        ``True`` only if this function permits this object to be a string.
        Defaults to ``True``. If this boolean is:

        * ``True``, this object is valid only if this object is either a class,
          classname, or tuple of classes and/or classnames.
        * ``False``, this object is valid only if this object is either a class
          or tuple of classes.
    hint_label : str
        Human-readable noun prefixing this object's representation in the
        exception message to be raised by this function unless this object is a
        PEP-noncompliant type hint. Defaults to ``Type hint``.
    exception_cls : type
        Type of the exception to be raised by this function unless this object
        is a PEP-noncompliant type hint. Defaults to
        :class:`BeartypeDecorHintValueException`.

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
    assert isinstance(exception_cls, type), (
        '{!r} not a type.'.format(exception_cls))
    assert isinstance(hint_label, str), (
        '{!r} not a string.'.format(hint_label))

    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # BEGIN: Synchronize changes here with the tuple iteration below.
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
        # If this is a PEP 484-compliant class, raise an exception.
        if is_hint_typing(hint):
            raise exception_cls(
                '{} PEP 484 type {!r} unsupported.'.format(hint_label, hint))

        # Else, this is a PEP-noncompliant class. In this case, silently accept
        # this class as is.
        return
    # Else, this object is neither a forward reference nor class.

    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # END: Synchronize changes above with the tuple iteration below.
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
                # If this is a PEP 484-compliant class, raise an exception.
                if is_hint_typing(hint_item):
                    raise exception_cls(
                        '{} {!r} PEP 484 type {!r} unsupported.'.format(
                            hint_label, hint, hint_item))

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

# ....................{ TESTERS                           }....................
#FIXME: Detect functions created by "typing.NewType(subclass_name, superclass)"
#somehow, either here or elsewhere. These functions are simply the identity
#function at runtime and thus a complete farce. They're not actually types!
#Ideally, we would replace each such function by the underlying "superclass"
#type originally passed to that function, but we have no idea if that's even
#feasible. Welcome to "typing", friends.

@callable_cached
def is_hint_typing(hint: object) -> bool:
    '''
    ``True`` only if the passed object is a `PEP 484`_ type (i.e., class or
    object declared by the stdlib :mod:`typing` module).

    For efficiency, this tester is memoized.

    Motivation
    ----------
    Standard types allow callers to test for compliance with protocols,
    interfaces, and abstract base classes by calling either the
    :func:`isinstance` or :func:`issubclass` builtins. This is the
    well-established Pythonic standard for deciding conformance to an API.

    Insanely, `PEP 484`_ *and* the :mod:`typing` module implementing `PEP 484`_
    reject community standards by explicitly preventing callers from calling
    either the :func:`isinstance` or :func:`issubclass` builtins on `PEP
    484`_ types. Moreover, neither `PEP 484`_ nor :mod:`typing` implement
    public APIs for testing whether arbitrary objects comply with `PEP 484`_ or
    :mod:`typing`.

    Thus this tester function, which "fills in the gaps" by implementing this
    laughably critical oversight.

    Parameters
    ----------
    obj : object
        Object to be inspected.

    Returns
    ----------
    bool
        ``True`` only if this object is a `PEP 484`_ type.

    .. _PEP 484:
       https://www.python.org/dev/peps/pep-0484
    '''

    # Either the passed object if this object is a class *OR* the class of this
    # object otherwise (i.e., if this object is *NOT* a class).
    hint_type = utilobj.get_obj_type(hint)

    # If this type is defined by the stdlib "typing" module, return true.
    #
    # Note that there might exist an alternate means of deciding this boolean,
    # documented here merely for completeness:
    #
    #     try:
    #         isinstance(obj, object)
    #         return False
    #     except TypeError as type_error:
    #         return str(type_error).endswith(
    #             'cannot be used with isinstance()')
    #
    # The above effectively implements an Aikido throw by using the fact that
    # "typing" types prohibit isinstance() calls against those types. While
    # clever (and deliciously obnoxious), the above logic:
    #
    # * Requires catching exceptions in the common case and is thus *MUCH* less
    #   efficient than the preferable approach implemented here.
    # * Assumes that *ALL* "typing" types prohibit such calls. Sadly, only a
    #   proper subset of such types prohibit such calls.
    # * Assumes that those "typing" types that do prohibit such calls raise
    #   exceptions with reliable messages across *ALL* Python versions.
    #
    # In short, there is no general-purpose clever solution. *sigh*
    if utilobj.get_obj_module_name_or_none(hint_type) == 'typing':
        return True

    # For each superclass of this class...
    #
    # This edge case is required to handle user-defined subclasses declared in
    # user-defined modules of superclasses declared by the "typing" module:
    #
    #    # In a user-defined module...
    #    from typing import TypeVar, Generic
    #    T = TypeVar('T')
    #    class UserDefinedGeneric(Generic[T]): pass
    for hint_type_supertype in hint_type.__mro__:
        # If this superclass is defined by "typing", return true.
        if utilobj.get_obj_module_name_or_none(
            hint_type_supertype) == 'typing':
            return True

    # Else, neither this type nor any superclass of this type is defined by the
    # "typing" module. Ergo, this is *NOT* a PEP 484-compliant type.
    return False
