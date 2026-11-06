#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **object setters** (i.e., low-level callables mutating various
properties of arbitrary objects in a general-purpose manner).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................

# ....................{ SETTERS                            }....................
#FIXME: Unit test us up.
#FIXME: Globally refactor all low-level object.__setattr__() calls everywhere to
#call this high-level setter instead. *sigh*
def set_object_attr(obj: object, attr_name: str, attr_value: object) -> None:
    '''
    Dynamically set the **instance variable** (i.e., attribute bound to the
    passed object) with the passed name to the passed value.

    Parameters
    ----------
    obj : object
        Object to set this attribute on.
    attr_name : str
        Name of the instance variable to be set.
    attr_value : object
        Value to set this instance variable to.

    See Also
    --------
    :func:`beartype._util.cls.utilclsset.set_type_attr`
        Similar function dynamically setting class variables instead.
    '''

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
    # behaviour can be circumvented by passing the object.__setattr__() dunder
    # method instead, which then applies the desired monkey-patch *WITHOUT*
    # raising an exception. In short, stupid kludges is the answer.
    #
    # Specifically, this callable is defined as either...
    setattr_func = (
        # If the type of this object is a PEP 557-compliant frozen dataclass,
        # the object.__setattr__() dunder method as detailed above.
        object.__setattr__
        if is_pep557_dataclass_frozen(type(obj)) else
        # Else, this type is *NOT* a PEP 557-compliant frozen dataclass. In this
        # case, the standard setattr() builtin suffices.
        setattr
    )

    # ....................{ SETATTR                        }....................
    # Set the instance variable with this name to this value.
    setattr_func(obj, attr_name, attr_value)
