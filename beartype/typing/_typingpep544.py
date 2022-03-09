#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2022 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype** :pep:`544` **optimization layer.**

This private submodule implements a :func:`beartype.beartype``-compatible
(i.e., decorated by :func:`typing.runtime_checkable`) drop-in replacement for
:class:`typing.Protocol` that can lead to significant performance improvements.
'''

# ....................{ IMPORTS                           }....................
from beartype._util.py.utilpyversion import (
    IS_PYTHON_3_7,
    IS_PYTHON_AT_LEAST_3_7,
    IS_PYTHON_AT_LEAST_3_8,
    IS_PYTHON_AT_LEAST_3_9,
)

# ....................{ PEP 544 ~ preamble                }....................
# True only if the active Python interpreter already implicitly supports PEP
# 544 out-of-the-box *OR* can be explicitly forced to do so.
#
# OMG, what is this thing and why is it here? More specifically, why use this
# weird guard in addition to that IS_PYTHON_AT_LEAST_3_7 check below? Why not
# just create (and rely) on a dependency on typing-extensions when installing
# into Python 3.7? For example, we could amend "setup.py" to force:
#     'install_requires': ('typing-extensions>=3.10;python_version<"3.8"', ...),
#
# Great questions! Thanks for asking!
#
# It turns out there is a principled reason and practical reason. Actually,
# there is a practical reason in line with principles, which we'll attempt to
# pass off as principle (which isn't very principled of us, but oh well).
#
# The theological reason is that beartype hopes never to impose mandatory
# dependencies on anyone. Instead, we can leave that decision up
# to whomever is doing the installing. Further, the mechanism that person would
# almost certainly use to signal a need for access to Protocol in 3.7 is to
# install typing-extensions, which is the very same behavior that enables
# beartype to have it here. This maintains the appearance of an elegant design,
# when really all we were trying to do avoid the circular dependency at
# installation. #AccidentalGeniusForTheWin

#FIXME: We can remove nearly all gating in this module upon retiring support
#for Python 3.7 (and IS_PYTHON_AT_LEAST_3_7). At that point, no checks are
#necessary because all Python versions will support PEP 544.
_IS_PEP_544_SUPPORTABLE = False

# If the active Python interpreter targets at least Python >= 3.7 and thus does *NOT*
# implicitly support PEP 544 out-of-the-box, decide whether it can be
# explicitly forced to do so below.
if IS_PYTHON_AT_LEAST_3_7:
    # Defer Python version-specific imports.
    from typing import TypeVar

    #FIXME: Move this definition (and the TypeVar import) nearer to the _TT
    #definition below when retiring IS_PYTHON_AT_LEAST_3_7.
    _T_co = TypeVar("_T_co", covariant=True)
    '''
    Arbitrary covariant type variable.
    '''

    # If the active Python interpreter targets Python >= 3.8 and thus
    # implicitly supports PEP 544 out-of-the-box...
    if IS_PYTHON_AT_LEAST_3_8:
        #FIXME: Remove the above gate and consolidate with the logic below
        #when retiring IS_PYTHON_AT_LEAST_3_7.
        _IS_PEP_544_SUPPORTABLE = True

        #FIXME: The ignore[attr-defined] is for Python 3.7 because Mypy doesn't
        #understand IS_PYTHON_AT_LEAST_3_8. That ignore should be removable
        #when retiring PYTHON_AT_LEAST_3_7.
        # Defer Python version-specific imports, including non-caching
        # protocols to be overridden by caching equivalents below (and other
        # requirements from various sources, depending on runtime environment).
        from typing import (  # type: ignore[attr-defined]
            EXCLUDED_ATTRIBUTES,
            Protocol as _ProtocolSlow,
            SupportsAbs as _SupportsAbsSlow,
            SupportsBytes as _SupportsBytesSlow,
            SupportsComplex as _SupportsComplexSlow,
            SupportsFloat as _SupportsFloatSlow,
            SupportsIndex as _SupportsIndexSlow,
            SupportsInt as _SupportsIntSlow,
            SupportsRound as _SupportsRoundSlow,
            runtime_checkable,
        )
    # Else, the active Python interpreter targets only Python >= 3.7 and thus
    # does *NOT* implicitly support PEP 544 out-of-the-box. In this case,
    # decide whether it can be explicitly forced to do so below.
    else:
        #FIXME: Remove this whole branch when retiring IS_PYTHON_3_7 and
        #IS_PYTHON_AT_LEAST_3_7.
        assert IS_PYTHON_3_7

        # Attempt to...
        try:
            # Import non-caching protocols to be overridden by caching
            # equivalents below from the external "typing_extensions" module.
            from typing_extensions import (  # type: ignore[misc]
                runtime_checkable,
            )
        # If doing so fails, "typing_extensions" has *NOT* been installed
        # under this interpreter. In this case, silently reduce to a noop.
        except ImportError:
            pass
        # Else, this interpreter can be forced to support PEP 544.
        else:
            _IS_PEP_544_SUPPORTABLE = True

            # Defer heavyweight imports.
            import sys, typing
            from abc import abstractmethod
            from typing import (
                Generic,
                Iterable,
                Union,
                _GenericAlias,
                _collect_type_vars,
                _tp_cache,
                _type_check,
            )
            from typing_extensions import (
                _PROTO_WHITELIST,
                _ProtocolMeta,
                _check_generic,
                _get_protocol_attrs,
                _is_callable_members_only,
                _no_init,
            )

            class _ProtocolSlow(metaclass=_ProtocolMeta):
                # There is quite a lot of overlapping code with typing.Generic.
                # Unfortunately it is hard to avoid this while these live in two different
                # modules. The duplicated code will be removed when Protocol is moved to typing.
                """Base class for protocol classes. Protocol classes are defined as::

                    class Proto(Protocol):
                        def meth(self) -> int:
                            ...

                Such classes are primarily used with static type checkers that recognize
                structural subtyping (static duck-typing), for example::

                    class C:
                        def meth(self) -> int:
                            return 0

                    def func(x: Proto) -> int:
                        return x.meth()

                    func(C())  # Passes static type check

                See PEP 544 for details. Protocol classes decorated with
                @typing_extensions.runtime act as simple-minded runtime protocol that checks
                only the presence of given attributes, ignoring their type signatures.

                Protocol classes can be generic, they are defined as::

                    class GenProto(Protocol[T]):
                        def meth(self) -> T:
                            ...
                """
                __slots__ = ()
                _is_protocol = True

                def __new__(cls, *args, **kwds):
                    if cls is Protocol:
                        raise TypeError("Type Protocol cannot be instantiated; "
                                        "it can only be used as a base class")
                    return super().__new__(cls)

                @_tp_cache
                def __class_getitem__(cls, params):
                    if not isinstance(params, tuple):
                        params = (params,)
                    if not params and cls is not Tuple:
                        raise TypeError(
                            "Parameter list to {}[...] cannot be empty".format(cls.__qualname__))
                    msg = "Parameters to generic types must be types."
                    params = tuple(_type_check(p, msg) for p in params)
                    if cls is _ProtocolSlow:
                        # Generic can only be subscripted with unique type variables.
                        if not all(isinstance(p, TypeVar) for p in params):
                            i = 0
                            while isinstance(params[i], TypeVar):
                                i += 1
                            raise TypeError(
                                "Parameters to Protocol[...] must all be type variables."
                                " Parameter {} is {}".format(i + 1, params[i]))
                        if len(set(params)) != len(params):
                            raise TypeError(
                                "Parameters to Protocol[...] must all be unique")
                    else:
                        # Subscripting a regular Generic subclass.
                        _check_generic(cls, params)
                    return _GenericAlias(cls, params)

                def __init_subclass__(cls, *args, **kwargs):
                    tvars = []
                    # if '__orig_bases__' in cls.__dict__:
                    #     error = Generic in cls.__orig_bases__
                    # else:
                    #     error = Generic in cls.__bases__
                    # if error:
                    #     raise TypeError("Cannot inherit from plain Generic")
                    if '__orig_bases__' in cls.__dict__:
                        tvars = _collect_type_vars(cls.__orig_bases__)
                        # Look for Generic[T1, ..., Tn] or Protocol[T1, ..., Tn].
                        # If found, tvars must be a subset of it.
                        # If not found, tvars is it.
                        # Also check for and reject plain Generic,
                        # and reject multiple Generic[...] and/or Protocol[...].
                        gvars = None
                        for base in cls.__orig_bases__:
                            if (isinstance(base, _GenericAlias) and
                                    base.__origin__ in (Generic, _ProtocolSlow)):
                                # for error messages
                                the_base = 'Generic' if base.__origin__ is Generic else 'Protocol'
                                if gvars is not None:
                                    raise TypeError(
                                        "Cannot inherit from Generic[...]"
                                        " and/or Protocol[...] multiple types.")
                                gvars = base.__parameters__
                        if gvars is None:
                            gvars = tvars
                        else:
                            tvarset = set(tvars)
                            gvarset = set(gvars)
                            if not tvarset <= gvarset:
                                s_vars = ', '.join(str(t) for t in tvars if t not in gvarset)
                                s_args = ', '.join(str(g) for g in gvars)
                                raise TypeError("Some type variables ({}) are"
                                                " not listed in {}[{}]".format(s_vars,
                                                                               the_base, s_args))
                            tvars = gvars
                    cls.__parameters__ = tuple(tvars)

                    # Determine if this is a protocol or a concrete subclass.
                    if not cls.__dict__.get('_is_protocol', None):
                        cls._is_protocol = any(b is _ProtocolSlow for b in cls.__bases__)

                    # Set (or override) the protocol subclass hook.
                    def _proto_hook(other):
                        if not cls.__dict__.get('_is_protocol', None):
                            return NotImplemented
                        if not getattr(cls, '_is_runtime_protocol', False):
                            if sys._getframe(2).f_globals['__name__'] in ['abc', 'functools']:
                                return NotImplemented
                            raise TypeError("Instance and class checks can only be used with"
                                            " @runtime protocols")
                        if not _is_callable_members_only(cls):
                            if sys._getframe(2).f_globals['__name__'] in ['abc', 'functools']:
                                return NotImplemented
                            raise TypeError("Protocols with non-method members"
                                            " don't support issubclass()")
                        if not isinstance(other, type):
                            # Same error as for issubclass(1, int)
                            raise TypeError('issubclass() arg 1 must be a class')
                        for attr in _get_protocol_attrs(cls):
                            for base in other.__mro__:
                                if attr in base.__dict__:
                                    if base.__dict__[attr] is None:
                                        return NotImplemented
                                    break
                                annotations = getattr(base, '__annotations__', {})
                                if (isinstance(annotations, typing.Mapping) and
                                        attr in annotations and
                                        isinstance(other, _ProtocolMeta) and
                                        other._is_protocol):
                                    break
                            else:
                                return NotImplemented
                        return True
                    if '__subclasshook__' not in cls.__dict__:
                        cls.__subclasshook__ = _proto_hook

                    # We have nothing more to do for non-protocols.
                    if not cls._is_protocol:
                        return

                    # Check consistency of bases.
                    for base in cls.__bases__:
                        if not (base in (object, Generic) or
                                base.__module__ == 'collections.abc' and
                                base.__name__ in _PROTO_WHITELIST or
                                isinstance(base, _ProtocolMeta) and base._is_protocol):
                            raise TypeError('Protocols can only inherit from other'
                                            ' protocols, got %r' % base)
                    cls.__init__ = _no_init

            # These are [gulp] copied directly from _get_protocol_attrs in
            # <https://github.com/python/typing/blob/master/typing_extensions/src/typing_extensions.py>.
            # Why? Because typing-extensions doesn't (yet?) define
            # EXCLUDED_ATTRIBUTES and Python 3.7's typing module has no concept
            # of them.
            EXCLUDED_ATTRIBUTES = (
                '__abstractmethods__', '__annotations__', '__weakref__',
                '_is_protocol', '_is_runtime_protocol', '__dict__',
                '__args__', '__slots__',
                '__next_in_mro__', '__parameters__', '__origin__',
                '__orig_bases__', '__extra__', '__tree_hash__',
                '__doc__', '__subclasshook__', '__init__', '__new__',
                '__module__', '_MutableMapping__marker', '_gorg'
            )

            #FIXME: Redefine SupportsIndex as _SupportsIndexSlow, too. Booo!

            # Why redefine all of these? Because there's no concept of
            # @runtime_checkable in Python 3.7. Further, to avoid metaclass
            # conflicts, we need each to derive from typing_extensions.Protocol.
            # Why typing_extensions doesn't provide @runtime_checkable versions
            # (like it does for SupportsIndex) is beyond me.
            @runtime_checkable
            class _SupportsAbsSlow(_ProtocolSlow[_T_co]):  # type: ignore[no-redef]
                __slots__: Union[str, Iterable[str]] = ()
                @abstractmethod
                def __abs__(self) -> _T_co:
                    pass

            @runtime_checkable
            class _SupportsBytesSlow(_ProtocolSlow):  # type: ignore[no-redef]
                __slots__: Union[str, Iterable[str]] = ()
                @abstractmethod
                def __bytes__(self) -> bytes:
                    pass

            @runtime_checkable
            class _SupportsComplexSlow(_ProtocolSlow):  # type: ignore[no-redef]
                __slots__: Union[str, Iterable[str]] = ()
                @abstractmethod
                def __complex__(self) -> complex:
                    pass

            @runtime_checkable
            class _SupportsFloatSlow(_ProtocolSlow):  # type: ignore[no-redef]
                __slots__: Union[str, Iterable[str]] = ()
                @abstractmethod
                def __float__(self) -> float:
                    pass

            @runtime_checkable
            class _SupportsIndexSlow(_ProtocolSlow):  # type: ignore[no-redef]
                __slots__: Union[str, Iterable[str]] = ()

                @abstractmethod
                def __index__(self) -> int:
                    pass

            @runtime_checkable
            class _SupportsIntSlow(_ProtocolSlow):  # type: ignore[no-redef]
                __slots__: Union[str, Iterable[str]] = ()
                @abstractmethod
                def __int__(self) -> int:
                    pass

            @runtime_checkable
            class _SupportsRoundSlow(_ProtocolSlow[_T_co]):  # type: ignore[no-redef]
                __slots__: Union[str, Iterable[str]] = ()
                @abstractmethod
                def __round__(self, ndigits: int = 0) -> _T_co:
                    pass

# ....................{ PEP 544 ~ main                    }....................
# If the active Python interpreter supports PEP 544...
#
# This is one of those cases where one pines for a module-scope return
# statement. (I seem to remember a bug/feature request about that somewhere,
# but couldn't find it after a brief search.)

#FIXME: Remove this gate and consolidate with the above logic when retiring
#IS_PYTHON_3_7 and IS_PYTHON_AT_LEAST_3_7.
if _IS_PEP_544_SUPPORTABLE:
    # ..................{ IMPORTS                           }..................
    from beartype._util.cache.utilcachecall import callable_cached
    from typing import (  # type: ignore[attr-defined]
        TYPE_CHECKING,
        Any,
        Generic,
        Union,
    )

    # Note that this branch is intentionally tested first, despite the
    # resulting negation. Why? Because mypy quietly defecates all over itself
    # if the order of these two branches is reversed.
    if not IS_PYTHON_AT_LEAST_3_9:
        from typing import Dict, Iterable, Tuple, Type  # type: ignore[misc]
    # Else, the active Python interpreter targets Python >= 3.9 and thus
    # supports PEP 585. In this case, embrace non-deprecated PEP 585-compliant
    # type hints.
    else:
        from collections.abc import Iterable

        Dict = dict  # type: ignore[misc]
        Tuple = tuple  # type: ignore[assignment]
        Type = type  # type: ignore[assignment]

    # If the active Python interpreter was invoked by a static type checker
    # (e.g., mypy), violate privacy encapsulation. Doing so invites breakage
    # under newer Python releases. Confining any potential breakage to this
    # technically optional static type-checking phase minimizes the fallout by
    # ensuring that this API continues to behave as expected at runtime.
    #
    # See also this deep typing voodoo:
    #     https://github.com/python/mypy/issues/11614
    if TYPE_CHECKING:
        from abc import ABCMeta as _ProtocolMeta
    # Else, this interpreter was *NOT* invoked by a static type checker and is
    # thus subject to looser runtime constraints. In this case, access the same
    # metaclass *WITHOUT* violating privacy encapsulation.
    else:
        _ProtocolMeta = type(_ProtocolSlow)

    # ..................{ CONSTANTs                         }..................
    _PROTOCOL_ATTR_NAMES_IGNORABLE = frozenset(EXCLUDED_ATTRIBUTES)
    '''
    Frozen set of the names all **ignorable non-protocol attributes** (i.e.,
    attributes *not* considered part of the protocol of a
    :class:`beartype.typing.Protocol` subclass when passing that protocol to
    the :func:`isinstance` builtin in structural subtyping checks).
    '''

    _TT = TypeVar("_TT", bound=type)
    '''
    Arbitrary type variable bound (i.e., confined) to classes.
    '''

    # ..................{ METACLASSES                       }..................
    class _CachingProtocolMeta(_ProtocolMeta):
        '''
        **Caching protocol metaclass** (i.e., drop-in replacement for the
        private metaclass of the public :class:`typing.Protocol` superclass
        that additionally caches :meth:`class.__instancecheck__` results).

        This metaclass amortizes the `non-trivial time complexity of protocol
        validation <protocol cost_>`__ to a trivial constant-time lookup.

        .. _protocol cost:
           https://github.com/python/mypy/issues/3186#issuecomment-885718629

        Caveats
        ----------
        **This metaclass will yield unpredictable results for any object with
        one or more methods not declared by the class of that object,**
        including objects whose methods are dynamically assembled at runtime.
        This metaclass is ill-suited for such "types."

        Motivation
        ----------
        Although any non-caching protocol can be coerced into a caching
        protocol through inheritance, the former will remain incompatible with
        runtime type checkers (including :mod:`beartype`) until explicitly
        decorated by :func:`typing.runtime_checkable`. As example:

        .. code-block:: python

          >>> from abc import abstractmethod
          >>> from typing import Protocol
          >>> from beartype.typing import _CachingProtocolMeta, runtime_checkable

          >>> @runtime_checkable
          ... class _MyProtocol(Protocol):  # plain vanilla protocol
          ...   @abstractmethod
          ...   def myfunc(self, arg: int) -> str:
          ...     pass

          >>> @runtime_checkable  # redundant, but useful for documentation
          ... class MyProtocol(
          ...   _MyProtocol,
          ...   Protocol,
          ...   metaclass=_CachingProtocolMeta,  # caching version
          ... ):
          ...   pass

          >>> class MyImplementation:
          ...   def myfunc(self, arg: int) -> str:
          ...     return str(arg * -2 + 5)

          >>> my_thing: MyProtocol = MyImplementation()
          >>> isinstance(my_thing, MyProtocol)
          True

        The easy way to ensure your protocol caches checks and is
        :func:`typing.runtime_checkable` is to inherit from
        :class:`beartype.typing.Protocol` instead:

        .. code-block:: python

          >>> from beartype.typing import Protocol

          >>> class MyBearProtocol(Protocol):
          ...   @abstractmethod
          ...   def myfunc(self, arg: int) -> str:
          ...     pass

          >>> my_thing: MyBearProtocol = MyImplementation()
          >>> isinstance(my_thing, MyBearProtocol)
          True
        '''

        _abc_inst_check_cache: Dict[type, bool]

        # ................{ DUNDERS                           }................
        def __new__(
            mcls: Type[_TT],
            name: str,
            bases: Tuple[type, ...],
            namespace: Dict[str, Any],
            **kw: Any,
        ) -> _TT:

            # See <https://github.com/python/mypy/issues/9282>
            cls = super().__new__(mcls, name, bases, namespace, **kw)  # type: ignore[misc]

            # Mark this protocol class as a runtime protocol. By default,
            # "typing.Protocol" subclasses are only static-time. Although
            # marking a protocol class as a runtime protocol only defines a
            # single private boolean on this class (and thus imposes *NO* space
            # or time burden whatsoever), typing authors unwisely elected to
            # force everyone everywhere to unconditionally mark protocols as
            # runtime by decorate every runtime protocol by @runtime_checkable.
            # Since that is demonstrably insane, we pretend they choose wisely.
            #
            # To do so, we forcefully enable a private boolean instance
            # variable widely tested throghout the "typing" module. For unknown
            # reasons, this line of the typing.Protocol.__init__() method
            # forcefully disables this boolean despite the "__bases__" tuple of
            # this protocol class explicitly listing "typing.Protocol":
            #     cls._is_protocol = any(b is Protocol for b in cls.__bases__)
            #
            # Note that the @runtime_checkable decorator itself *CANNOT* be
            # applied to this protocol class. Why? Because that decorator
            # internally raises this exception if this private boolean instance
            # variable is false:
            #     TypeError: @runtime_checkable can be only applied to protocol
            #     classes, got <class
            #     'beartype.typing._typingpep544.SupportsAbs'>
            #
            # We lie to tell the truth.
            cls._is_protocol = True

            # Prefixing this class member with "_abc_" is necessary to prevent
            # it from being considered part of the Protocol. See also:
            #     https://github.com/python/cpython/blob/main/Lib/typing.py
            cls._abc_inst_check_cache = {}

            # Return this caching protocol.
            return cls


        def __instancecheck__(cls, inst: Any) -> bool:
            '''
            ``True`` only if the passed object is a **structural subtype**
            (i.e., satisfies the protocol defined by) the passed protocol.

            Parameters
            ----------
            cls : type
                :pep:`544`-compliant protocol to check this object against.
            inst : Any
                Arbitrary object to check against this protocol.

            Returns
            ----------
            bool
                ``True`` only if this object satisfies this protocol.
            '''

            # Attempt to...
            try:
                #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                # CAUTION: This *MUST* remain *SUPER* tight!! Even adding a
                # mere assertion here can add ~50% to our best-case runtime.
                #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                # Return a pre-cached boolean indicating whether an object of
                # the same arbitrary type as the object passed to this call
                # satisfied the same protocol in a prior call of this method.
                return cls._abc_inst_check_cache[type(inst)]
            # If this method has yet to be passed the same protocol *AND* an
            # object of the same type as the object passed to this call...
            except KeyError:
                # If you're going to do *anything*, do it here. Try not to
                # expand the rest of this method if you can avoid it.
                inst_t = type(inst)
                bases_pass_muster = True

                for base in cls.__bases__:
                    #FIXME: This branch probably erroneously matches unrelated
                    #user-defined types whose names just happen to be "Generic"
                    #or "Protocol". Ideally, we should tighten that up to only
                    #match the actual "{beartype,}.typing.{Generic,Protocol}"
                    #superclasses. Of course, note that
                    #"beartype.typing.Protocol" is *NOT* "typing.Protocol', so
                    #we'll want to explicitly test against both.
                    if base is cls or base.__name__ in (
                        'Protocol',
                        'Generic',
                        'object',
                    ):
                        continue
                    if not isinstance(inst, base):
                        bases_pass_muster = False
                        break

                cls._abc_inst_check_cache[inst_t] = bases_pass_muster and (
                    _check_only_my_attrs(cls, inst))

                return cls._abc_inst_check_cache[inst_t]


    #FIXME: Docstring us up, please.
    #FIXME: Comment us up, please.
    def _check_only_my_attrs(cls, inst: Any, _EMPTY_DICT = {}) -> bool:

        cls_attr_name_to_value = cls.__dict__
        cls_attr_name_to_hint = cls_attr_name_to_value.get(
            '__annotations__', _EMPTY_DICT)
        cls_attr_names = (
            cls_attr_name_to_value | cls_attr_name_to_hint
            if IS_PYTHON_AT_LEAST_3_9 else
            dict(cls_attr_name_to_value, **cls_attr_name_to_hint)
        )

        # For the name of each attribute declared by this protocol class...
        for cls_attr_name in cls_attr_names:
            # If...
            if (
                # This name implies this attribute to be unignorable *AND*...
                #
                # Specifically, if this name is neither...
                not (
                    # A private attribute defined by dark machinery in the
                    # "ABCMeta" metaclass for abstract base classes *OR*...
                    cls_attr_name.startswith('_abc_') or
                    # That of an ignorable non-protocol attribute...
                    cls_attr_name in _PROTOCOL_ATTR_NAMES_IGNORABLE
                # This attribute is either...
                ) and (
                    # Undefined by the passed object *OR*...
                    #
                    # This method has been specifically "blocked" (i.e.,
                    # ignored) by the passed object from being type-checked as
                    # part of this protocol. For unknown and presumably
                    # indefensible reasons, PEP 544 explicitly supports a
                    # fragile, unreadable, and error-prone idiom enabling
                    # objects to leave methods "undefined." What this madness!
                    not hasattr(inst, cls_attr_name) or
                    (
                        #FIXME: Unit test this up, please.
                        # A callable *AND*...
                        callable(getattr(cls, cls_attr_name, None)) and
                        # The passed object nullified this method. *facepalm*
                        getattr(inst, cls_attr_name) is None
                    )
                )
            ):
                # Then the passed object violates this protocol. In this case,
                # return false.
                return False

        # Else, the passed object satisfies this protocol. In this case, return
        # true.
        return True

    # ..................{ CLASSES                           }..................
    @runtime_checkable
    class Protocol(
        _ProtocolSlow,
        # Force protocols to be generics. Although the standard
        # "typing.Protocol" superclass already implicitly subclasses from the
        # "typing.Generic" superclass, the non-standard
        # "typing_extensions.Protocol" superclass does *NOT*. Ergo, we force
        # this to be the case.
        Generic,
        metaclass=_CachingProtocolMeta,
    ):
        '''
        :func:`beartype.beartype`-compatible (i.e., decorated by
        :func:`typing.runtime_checkable`) drop-in replacement for
        :class:`typing.Protocol` that can lead to significant performance
        improvements.

        Uses :class:`_CachingProtocolMeta` to cache :func:`isinstance` check
        results.

        Examples
        ----------
        .. code-block:: python

           >>> from abc import abstractmethod
           >>> from beartype import beartype
           >>> from beartype.typing import Protocol

           >>> class MyBearProtocol(Protocol):  # <-- runtime-checkable through inheritance
           ...   @abstractmethod
           ...   def myfunc(self, arg: int) -> str:
           ...     pass

           >>> my_thing: MyBearProtocol = MyImplementation()
           >>> isinstance(my_thing, MyBearProtocol)
           True

           >>> @beartype
           ... def do_somthing(thing: MyBearProtocol) -> None:
           ...   thing.myfunc(0)
        '''

        # ................{ CLASS VARIABLES                   }................
        __slots__: Union[str, Iterable[str]] = ()

        # ................{ DUNDERS                           }................
        @callable_cached
        def __class_getitem__(cls, item):

            # We have to redefine this method because typing.Protocol's version
            # is very persnickety about only working for typing.Generic and
            # typing.Protocol. That's an exclusive club, and we ain't in it.
            # (RIP, GC.) Let's see if we can sneak in, shall we?

            # FIXME: Once <https://bugs.python.org/issue46581> is addressed,
            # consider replacing the madness below with something like:
            #   cached_gen_alias = _ProtocolSlow.__class_getitem__(_ProtocolSlow, params)
            #   our_gen_alias = cached_gen_alias.copy_with(params)
            #   our_gen_alias.__origin__ = cls
            #   return our_gen_alias

            # If the superclass typing.Protocol.__class_getitem__() dunder
            # method has been wrapped as expected with caching by the private
            # (and thus *NOT* guaranteed to exist) @typing._tp_cache decorator,
            # call that unwrapped method directly to obtain the expected
            # generic alias.
            #
            # Note that:
            # * We intentionally call the unwrapped method rather than the
            #   decorated closure wrapping that method with memoization. Why?
            #   Because subsequent logic monkey-patches this generic alias to
            #   refer to this class rather than the standard "typing.Protocol".
            #   However, doing so violates internal expectations of the
            #   @typing._tp_cache decorator performing this memoization.
            # * This method is already memoized by our own @callable_cached
            #   decorator. Calling the decorated closure wrapping that
            #   unwrapped method with memoization would needlessly consume
            #   excess space and time for *NO* additional benefit.
            if hasattr(super().__class_getitem__, '__wrapped__'):
                # Protocol class to be passed as the "cls" parameter to the
                # unwrapped superclass typing.Protocol.__class_getitem__()
                # dunder method. There exist two unique cases corresponding to
                # two unique branches of an "if" conditional in that method,
                # depending on whether either this "Protocol" superclass or a
                # user-defined subclass of this superclass is being
                # subscripted. Specifically, this class is...
                protocol_cls = (
                    # If this "Protocol" superclass is being directly
                    # subclassed by one or more type variables (e.g.,
                    # "Protocol[S, T]"), the non-caching "typing.Protocol"
                    # superclass underlying this caching protocol superclass.
                    # Since the aforementioned "if" conditional performs an
                    # explicit object identity test for the "typing.Protocol"
                    # superclass, we *MUST* pass that rather than this
                    # superclass to trigger that conditional appropriately.
                    _ProtocolSlow
                    if cls is Protocol else
                    # Else, a user-defined subclass of this "Protocol"
                    # superclass is being subclassed by one or more type
                    # variables *OR* types satisfying the type variables
                    # subscripting the superclass (e.g.,
                    # "UserDefinedProtocol[str]" for a user-defined subclass
                    # class UserDefinedProtocol(Protocol[AnyStr]). In this
                    # case, this subclass as is.
                    cls
                )

                gen_alias = super().__class_getitem__.__wrapped__(
                    protocol_cls, item)
            # We shouldn't ever be here, but if we are, we're making the
            # assumption that typing.Protocol.__class_getitem__() no longer
            # caches. Heaven help us if that ever uses some proprietary
            # memoization implementation we can't see anymore because it's not
            # based on the standard @functools.wraps decorator.
            else:
                gen_alias = super().__class_getitem__(item)

            # Switch the origin of this generic alias from its default of
            # "typing.Protocol" to this caching protocol class. If *NOT* done,
            # CPython incorrectly sets the metaclass of subclasses to the
            # non-caching "type(typing.Protocol)" metaclass rather than our
            # caching "_CachingProtocolMeta" metaclass.
            #
            # Luddite alert: we don't fully understand the mechanics here. We
            # suspect no one does.
            gen_alias.__origin__ = cls

            # We're done! Time for a honey brewskie break. We earned it.
            return gen_alias

    #FIXME: Ensure that the main @beartype codebase handles protocols whose
    #repr() starts with "beartype.typing" as well, please.

    # Replace the unexpected (and thus non-compliant) fully-qualified name of
    # the module declaring this caching protocol superclass (e.g.,
    # "beartype.typing._typingpep544") with the expected (and thus compliant)
    # fully-qualified name of the standard "typing" module declaring the
    # non-caching "typing.Protocol" superclass.
    #
    # If this is *NOT* done, then the machine-readable representation of this
    # caching protocol superclass when subscripted by one or more type
    # variables (e.g., "beartype.typing.Protocol[S, T]") will be differ
    # significantly from that of the non-caching "typing.Protocol" superclass
    # (e.g., beartype.typing._typingpep544.Protocol[S, T]"). Because
    # @beartype (and possibly other third-party packages) expect the two
    # representations to comply, this awkward monkey-patch preserves sanity.
    Protocol.__module__ = 'beartype.typing'

    # ..................{ PROTOCOLS                         }..................
    class SupportsAbs(_SupportsAbsSlow[_T_co], Protocol, Generic[_T_co]):
        '''
        Caching variant of :class:`typing.SupportsAbs`.
        '''
        __module__: str = 'beartype.typing'
        __slots__: Union[str, Iterable[str]] = ()


    class SupportsBytes(_SupportsBytesSlow, Protocol):
        '''
        Caching variant of :class:`typing.SupportsBytes`.
        '''
        __module__: str = 'beartype.typing'
        __slots__: Union[str, Iterable[str]] = ()


    class SupportsComplex(_SupportsComplexSlow, Protocol):
        '''
        Caching variant of :class:`typing.SupportsComplex`.
        '''
        __module__: str = 'beartype.typing'
        __slots__: Union[str, Iterable[str]] = ()


    class SupportsFloat(_SupportsFloatSlow, Protocol):
        '''
        Caching variant of :class:`typing.SupportsFloat`."
        '''
        __module__: str = 'beartype.typing'
        __slots__: Union[str, Iterable[str]] = ()


    class SupportsInt(_SupportsIntSlow, Protocol):
        '''
        Caching variant of :class:`typing.SupportsInt`.
        '''
        __module__: str = 'beartype.typing'
        __slots__: Union[str, Iterable[str]] = ()


    class SupportsIndex(_SupportsIndexSlow, Protocol):
        '''
        Caching variant of :class:`typing.SupportsIndex`.
        '''
        __module__: str = 'beartype.typing'
        __slots__: Union[str, Iterable[str]] = ()


    class SupportsRound(_SupportsRoundSlow[_T_co], Protocol, Generic[_T_co]):
        '''
        Caching variant of :class:`typing.SupportsRound`.
        '''
        __module__: str = 'beartype.typing'
        __slots__: Union[str, Iterable[str]] = ()
