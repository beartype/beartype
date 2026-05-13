#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype **forward reference fake classes** (i.e., low-level class hierarchy
pretending to resolve otherwise unresolvable runtime-hostile forward references
through bald-faced trickery, casual deceit, and code prestidigitation the likes
of which no living Pythonista could countenance).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype._util.cache.utilcachecall import callable_cached

# ....................{ PRIVATE ~ metaclasses              }....................
class _BeartypeForwardRefFakeMeta(type):
    '''
    Beartype **forward reference fake metaclass** (i.e., metaclass of the
    :class:`.BeartypeForwardRefFakeABC` abstract base class (ABC), whose
    concrete subclasses each pretend to resolve an otherwise unresolvable
    runtime-hostile forward reference through bald-faced trickery, casual
    deceit, and code prestidigitation the likes of which no living Pythonista
    could countenance).
    '''

    # ....................{ DUNDERS                        }....................
    @callable_cached
    def __repr__(cls: type['BeartypeForwardRefFakeABC']) -> str:  # type: ignore[misc]
        '''
        Machine-readable string representing this forward reference fake proxy.

        This dunder method is memoized for efficiency.
        '''

        # Return the machine-readable representation of this fake proxy.
        #
        # Note that this representation is intentionally prefixed by the
        # @beartype-specific substring "<forwardreffake ", resembling the
        # representation of classes (e.g., "<class 'bool'>"). Why? Because
        # various other @beartype submodules ignore objects whose
        # representations are prefixed by the "<" character, which are usefully
        # treated as having a standard representation that is ignorable for most
        # intents and purposes. This includes:
        #   * The die_if_hint_pep604_inconsistent() raiser.
        return f'<forwardreffake {cls.__module__}.{cls.__name__}>'

    # ....................{ DUNDERS ~ pep : 3119           }....................
    def __instancecheck__(  # type: ignore[misc]
        fake_proxy: type['BeartypeForwardRefFakeABC'], obj: object) -> bool:  # pyright: ignore
        '''
        :data:`True` only if the passed object superficially appears to be an
        instance of the **nested type** (i.e., low-level class whose declaration
        is confined to the body of a previously called higher-level callable and
        thus inaccessible to the current call stack lacking a stack frame
        encapsulating that prior call) referred to by the :pep:`484`-compliant
        stringified relative forward reference type hint proxied by the passed
        forward reference fake proxy.

        The :func:`isinstance` builtin implicitly calls this
        :pep:`3119`-compliant metaclass dunder method when passed a forward
        reference fake proxy as its second parameter.

        Parameters
        ----------
        fake_proxy : type['BeartypeForwardRefFakeABC']
            Fake proxy to pretend to proxy this :func:`isinstance` check for.
        obj : object
            User-defined object to pretend to test this fake proxy against.
        '''

        # Return true only if the type of the passed user-defined object is a
        # subclass of the nested type referred to by the PEP 484-compliant
        # stringified relative forward reference type hint proxied by this
        # forward reference fake proxy, implying this object to be an instance
        # of that nested type.
        #
        # Note that this tester is memoized and thus requires that parameters be
        # only passed positionally.
        return _is_fake_proxy_superclass(fake_proxy, obj.__class__)


    def __subclasscheck__(  # type: ignore[misc]
        fake_proxy: type['BeartypeForwardRefFakeABC'], subclass: type) -> bool:  # pyright: ignore
        '''
        :data:`True` only if the passed type superficially appears to be a
        subclass of the **nested type** (i.e., low-level class whose declaration
        is confined to the body of a previously called higher-level callable and
        thus inaccessible to the current call stack lacking a stack frame
        encapsulating that prior call) referred to by the :pep:`484`-compliant
        stringified relative forward reference type hint proxied by the passed
        forward reference fake proxy.

        The :func:`issubclass` builtin implicitly calls this
        :pep:`3119`-compliant metaclass dunder method when passed a forward
        reference fake proxy as its second parameter.

        Parameters
        ----------
        fake_proxy : type['BeartypeForwardRefFakeABC']
            Fake proxy to pretend to proxy this :func:`issubclass` check for.
        subclass : object
            User-defined type to pretend to test this fake proxy against.

        Raises
        ------
        TypeError
            If this user-defined type is *not* actually a type.
        '''

        # Return true only if this user-defined type is a subclass of the nested
        # type referred to by the PEP 484-compliant stringified relative forward
        # reference type hint proxied by this forward reference fake proxy.
        #
        # Note that this tester is memoized and thus requires that parameters be
        # only passed positionally.
        return _is_fake_proxy_superclass(fake_proxy, subclass)

# ....................{ PRIVATE ~ superclasses             }....................
class BeartypeForwardRefFakeABC(object, metaclass=_BeartypeForwardRefFakeMeta):
    '''
    Beartype **forward reference fake abstract base class (ABC)** (i.e.,
    superclass whose concrete subclasses each pretend to resolve an otherwise
    unresolvable runtime-hostile forward reference through bald-faced trickery,
    casual deceit, and code prestidigitation the likes of which no living
    Pythonista could countenance).
    '''

    pass

# ....................{ PRIVATE ~ testers                  }....................
@callable_cached
def _is_fake_proxy_superclass(
    fake_proxy: type[BeartypeForwardRefFakeABC], subclass: type) -> bool:
    '''
    :data:`True` only if the passed **forward reference fake proxy** (i.e.,
    concrete :class:`.BeartypeForwardRefFakeABC` subclass created and returned
    by the public
    :func:`.beartype._check.forward.reference.fwdrefproxy.proxy_hint_pep484_ref_str_fake`
    type factory) pretends to be a superclass of the passed user-defined type.

    This tester returns :data:`True` if and only if the unqualified basename of
    this fake proxy is that of at least one of the transitive superclasses in
    the method resolution order (MRO) of this user-defined class (including this
    user-defined class type itself).

    This tester is memoized for efficiency.

    Parameters
    ----------
    fake_proxy : type[BeartypeForwardRefFakeABC]
        Forward reference fake proxy to test this subclass against.
    subclass : type
        User-defined type to be tested as a subclass of this fake proxy.

    Returns
    -------
    bool
        :data:`True` only if this fake proxy pretends to be a superclass of this
        user-defined class.

    Raises
    ------
    TypeError
        If this user-defined type is *not* actually a type.
    '''

    # ....................{ VALIDATE                       }....................
    # Note that this test *CANNOT* be written as:
    #     isinstance(fake_proxy, BeartypeForwardRefFakeABC)
    #
    # Why? Because doing so would ignite infinite recursion by implicitly
    # calling the _BeartypeForwardRefFakeMeta.__instancecheck__() dunder method,
    # which directly calls this lower-level tester. Metaclasses do be like that.
    # print(f'fake_proxy: {repr(fake_proxy}); class: {repr(fake_proxy.__class__)}')
    assert fake_proxy.__class__ is _BeartypeForwardRefFakeMeta, (
        f'{repr(fake_proxy)} not forward reference fake proxy.')

    # If this other type is *NOT* a type, raise the standard "TypeError"
    # exception expected to be raised by the issubclass() builtin in this common
    # edge case. issubclass() implicitly calls the
    # _BeartypeForwardRefFakeMeta.__subclasscheck__() dunder method, which
    # directly calls this lower-level tester. To do so trivially, we
    # intentionally masquerade as the root "object" superclass.
    #
    # Weird Python is worky Python. Metaclasses do still be like that.
    issubclass(subclass, object)  # type: ignore[arg-type]

    # ....................{ FAST                           }....................
    # Unqualified basename of this fake proxy, localized purely as a negligible
    # microoptimization. It's best not to ask questions. You're thinking them,
    # though, aren't you!?
    fake_proxy_basename = fake_proxy.__name__

    # The unqualified basename of this fake proxy is that of this other type,
    # immediately return true.
    #
    # Note that this is merely a microoptimization for the common case, avoiding
    # the needlessly expensive iteration performed below unless necessary.
    if fake_proxy_basename == subclass.__name__:
        return True
    # Else, the unqualified basename of this fake proxy is *NOT* that of this
    # subclass.

    # ....................{ SLOW                           }....................
    # Method resolution order (MRO) of this other type, localized purely as a
    # negligible microoptimization. It is what it is. Don't judge us! *sobs*
    subclass_mro = subclass.__mro__

    # If this other type resides in a subclass hierarchy of at least three
    # transitive superclasses (including this other type itself), at least one
    # transitive superclass of this other type has yet to be inspected. Why
    # only one? Because:
    # * "subclass_mro[0]" is this other type itself, which the "if" conditional
    #   above has already omitted as inapplicable to this fake proxy.
    # * "subclass_mro[-1]" is the root "object" superclass of all types. Since
    #   *ALL* types are necessarily subclasses of the root "object" superclass,
    #   proxying that superclass with a "fake" proxy would be senseless. *NO*
    #   caller should do that. Ergo, we safely ignore that superclass.
    #
    # These two types are both guaranteed to reside in this MRO *AND* be
    # ignorable for superclass detection purposes. Omitting these two types thus
    # increases the minimum size of an unignorable MRO from one to three.
    if len(subclass_mro) >= 3:
        # Tuple of all unignorable transitive superclasses in the MRO of this
        # other type (as discussed above).
        subclass_mro_unignorable = subclass_mro[1:-1]

        # For each such unignorable transitive superclass...
        #
        # Note that the any() builtin has been profiled to be almost twice as
        # slow as the manual approach performed here -- even under newer Python
        # interpreters (e.g., CPython 3.15).
        for subclass_superclass in subclass_mro_unignorable:
            # If the unqualified basename of this fake proxy is that of this
            # unignorable transitive superclass, immediately return true.
            if fake_proxy_basename == subclass_superclass.__name__:
                return True
            # Else, the unqualified basename of this fake proxy is *NOT* that of
            # this unignorable transitive superclass. In this case, continue to
            # the next.
    # Else, this other type resides outside an unignorable subclass hierarchy
    # (ignoring the ignorable root "object" superclass, anyway).

    # ....................{ FALLBACK                       }....................
    # Return false as a last-ditch fallback. We're desperate, Python!
    return False

# ....................{ PRIVATE ~ tuples                   }....................
BeartypeForwardRefFakeABC_BASES = (BeartypeForwardRefFakeABC,)
'''
1-tuple containing *only* the :class:`.BeartypeForwardRefFakeABC` superclass to
reduce space and time consumption.
'''
