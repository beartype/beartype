#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **beartype plugin type utilities** (i.e., low-level callables
specifically applicable to pure-Python classes defining :mod:`beartype`-specific
attributes specifically intended to be consumed by the :func:`beartype.beartype`
decorator).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
# from beartype._check.forward.reference.fwdreftest import is_beartype_ref_proxy
from collections.abc import Callable
from typing import Optional

# ....................{ TESTERS                            }....................
#FIXME: Unit test us up, please.
#FIXME: *PUBLICLY DOCUMENT IN OUR ONLINE DOCUMENTATION, PLEASE*. Jeez. Getting
#@leycec to write docos is like pulling rabid hen's teeth around here. *sigh*
def get_type_beartype_plugin_get_violation_str_or_none(cls: type) -> (
    Optional[Callable[[object,], str]]):
    '''
    PEP-noncompliant mod:`beartype`-specific **type-checking violation message
    getter** (i.e., ``__instancecheck_str__()`` dunder method accepting as
    mandatory positional parameters both the passed pure-Python type and an
    arbitrary object that is guaranteed is to not be an instance of that type
    *and* returning a substring describing as a human-readable sentence fragment
    the failure of that arbitrary object to be an instance of that type) if that
    type defines that getter *OR* :data:`"None` otherwise (i.e., if that type
    defines no such getter).

    Note that this constitutes a plugin API. Although currently
    mod:`beartype`-specific, this API is intended to receive widespread adoption
    as a pseudo-standard throughout the runtime type-checking community (e.g.,
    by :mod:`typeguard` and possibly Pydantic). Various third-party packages
    that publish custom type hint factories currently leverage this API to
    generate package-specific violation messages, including:

    * :mod:`jaxtyping`. For the good of Google!
    * :mod:`optypes`. NumPy be praised!

    Usage
    -----
    Third-party packages typically comply with this plugin API by defining types
    whose metaclasses define *both*:

    * The :pep:`3119`-compliant ``__instancecheck__()`` dunder method *not*
      introspected by this getter. The :func:`isinstance` builtin implicitly
      calls this dunder method when this type is passed as the second parameter
      to that builtin and then returns the boolean returned by this dunder
      method. This dunder method *must*:

      * Accept as mandatory positional parameters:

        * This type.
        * An arbitrary object.

      * Return either:

        * If that object an instance of that type, :data:`True`.
        * Else, :data:`False`.

    * The PEP-noncompliant ``__instancecheck_str__()`` dunder method
      introspected by this getter. This dunder method *must*:

      * Accept as mandatory positional parameters:

        * This type.
        * An arbitrary object.

      * Return a substring describing as a human-readable sentence fragment the
        failure of that arbitrary object to be an instance of that type.
        Crucially, this sentence fragment should:

        * *Not* be prefixed by a capital letter.
        * *Not* be suffixed by a period (i.e., ``"."`` character).

    That type then implicitly inherits these dunder methods from its metaclass,
    which then exposes the ``__instancecheck_str__()`` dunder method to this
    getter and then callers of this getter. This non-standard
    ``__instancecheck_str__()`` design pattern thus trivially generalizes the
    standard :pep:`3119`-compliant ``__instancecheck__()`` design pattern.

    Whereas :func:`isinstance` *always* calls ``__instancecheck__()`` to decide
    whether the object passed as the first parameter object to that builtin is
    an instance of this type, :mod:`beartype` only conditionally calls
    ``__instancecheck_str__()`` with the same parameters that :func:`isinstance`
    passed to ``__instancecheck__()`` when that object is *not* an instance of
    this type (i.e., when that ``__instancecheck__()`` passed these parameters
    returned :data:`False`).

    Consider the following normative metaclass defining ``__instancecheck__()``
    to defer to the :func:`isinstance` builtin and ``__instancecheck__()`` to
    describe that call to :func:`isinstance`:

    .. code-block:: python

        class _InstancecheckStrMetaclass(type):  # <-- metaclasses subclass the "type" builtin (so boring)
            # Actual type tested by the __instancecheck__() dunder method defined below.
            __type_proxied__: type = str

            def __instancecheck__(cls: 'InstancecheckStr', obj: Any) -> bool:  # <-- PEP 3119-compliant dunder method (boring strengthens)
                return isinstance(obj, cls.__type_proxied__)

            def __instancecheck_str__(cls: 'InstancecheckStr', obj: Any) -> str:  # <-- beartype-specific dunder method! *EXCITING HYPE*!!
                return (
                    f'object {repr(obj)} not instance of '  # <-- *NOTE* lowercased first word... *vomit everywhere*
                    f'"{cls.__module__}.{cls.__name__}"'  # <---- *NOTE* lack of trailing period... *vomit buckets*
                )

        class InstancecheckStr(metaclass=_InstancecheckStrMetaclass): ...

    Parameters
    ----------
    cls : type
        Pure-Python type to be inspected.

    Returns
    -------
    Optional[Callable[[type, object]
        Either:

        * If the passed type defines the ``__instancecheck_str__()`` dunder
          method, that method.
        * Else, :data:`None`.
    '''

    #FIXME: Excise us up, please. *sigh*
    # if is_beartype_ref_proxy(cls):
    #     return None

    # Metaclass-specific __instancecheck_str__() dunder method if the
    # metaclass of this class defines this method *OR* "None" otherwise
    # (i.e., if that metaclass does *NOT* define this method).
    return getattr(cls, '__instancecheck_str__', None)
