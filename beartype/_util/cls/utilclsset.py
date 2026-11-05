#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **class setters** (i.e., low-level callables modifying various
properties of arbitrary classes).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................

# ....................{ SETTERS                            }....................
#FIXME: Unit test us up.
def set_type_attr(cls: type, attr_name: str, attr_value: object) -> None:
    '''
    Dynamically set the **class variable** (i.e., attribute of the passed class)
    with the passed name to the passed value.

    Parameters
    ----------
    cls : type
        Class to set this attribute on.
    attr_name : str
        Name of the class attribute to be set.
    attr_value : object
        Value to set this class attribute to.

    Caveats
    -------
    **This function is unavoidably slow.** Class attributes are *only* settable
    by calling the tragically slow :func:`setattr` builtin. Attempting to
    directly set an attribute on the class dictionary raises an exception: e.g.,

    .. code-block:: pycon

       >>> class OhGodHelpUs(object): pass
       >>> OhGodHelpUs.__dict__['even_god_cannot_help'] = 2
       TypeError: 'mappingproxy' object does not support item assignment

    Why? Because class dictionaries are actually low-level :class:`mappingproxy`
    objects that intentionally override the ``__setattr__()`` dunder method to
    unconditionally raise an exception. Why? Because that constraint enables the
    :meth:`type.__setattr__` dunder method to enforce critical efficiency
    constraints on class attributes -- including that class attribute keys are
    *not* only strings but also valid Python identifiers:

    See also this `relevant StackOverflow answer by Python luminary Raymond
    Hettinger <answer_>`__.

    .. _answer:
       https://stackoverflow.com/a/32720603/2809027
    '''
    assert isinstance(cls, type), f'{repr(cls)} not type.'

    # ....................{ IMPORTS                        }....................
    # Avoid circular import dependencies.
    from beartype._util.cls.pep.clspep557 import is_pep557_dataclass_frozen

    # ....................{ LOCALS                         }....................
    # setattr()-like callable to be called to set this attribute on this class.
    # Defaults to the C-based setattr() builtin, which internally defers to the
    # __setattr__() dunder method guaranteed to be defined by all classes (due
    # to the existence of the type.__setattr__() dunder method). Though this
    # default suffices for most use cases, a small subset of outlier edge cases
    # require that setattr()-like alternative.
    #
    # PEP 557-compliant frozen dataclasses are the canonical example. They
    # guarantee immutability by overriding the __setattr__() dunder method
    # (implicitly called by the setattr() builtin) to unconditionally raise an
    # exception. While understandable, this behaviour prevents the @beartype
    # decorator from monkey-patching type-checking into frozen dataclasses by
    # replacing their default __setattr__() with a @beartype-specific
    # alternative performing type-checking; attempting to do so ironically
    # invokes that same __setattr__(), which then raises an exception. This
    # behaviour can be circumvented by passing the type.__setattr__() dunder
    # method as this parameter, which then applies the desired monkey-patch
    # *WITHOUT* raising an exception. In short, stupid kludges is the answer.
    #
    # Specifically, this callable is defined as either...
    setattr_func = (
        # If this type is a PEP 557-compliant frozen dataclass, the
        # type.__setattr__() dunder method as detailed above.
        type.__setattr__
        if is_pep557_dataclass_frozen(cls) else
        # Else, this type is *NOT* a PEP 557-compliant frozen dataclass. In this
        # case, the standard setattr() builtin suffices.
        setattr
    )

    # ....................{ SETATTR                        }....................
    # Attempt to set the class attribute with this name to this value.
    try:
        setattr_func(cls, attr_name, attr_value)
    # If doing so raises a builtin "TypeError"...
    except TypeError as exception:
        # Message raised with this "TypeError".
        exception_message = str(exception)

        # If this message satisfies a well-known pattern unique to the current
        # Python version, then this exception signifies this attribute to be
        # inherited from an immutable builtin type (e.g., "str") subclassed by
        # this user-defined subclass. In this case, silently skip past this
        # uncheckable attribute to the next. Since the active Python interpreter
        # targets Python >= 3.10, specifically match a message of the form:
        #     cannot set '{attr_name}' attribute of immutable type '{cls_name}'
        if (
            exception_message.startswith("cannot set '") and
            "' attribute of immutable type " in exception_message
        ):
            return
        # Else, this message does *NOT* satisfy that pattern.

        # Preserve this exception by re-raising this exception.
        raise
