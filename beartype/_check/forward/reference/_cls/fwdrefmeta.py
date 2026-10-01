#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype **forward reference metaclasses** (i.e., low-level metaclasses of
classes deferring the resolution of a stringified type hint referencing an
attribute that has yet to be defined and annotating a class or callable
decorated by the :func:`beartype.beartype` decorator).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ TODO                               }....................
#FIXME: *RECURSION GUARDS*! Namely, we currently have none. But as the body of
#__instancecheck_str__() dunder method notes:
#    Any codebase encouraging forward references to reference one another is a
#    codebase inviting a cyclic forward reference graph inducing infinite
#    runtime recursion.
#
#We have two and *ONLY* two options here. Either way, we need to at least begin
#*DETECTING* forward references that refer to other forward references and then
#either:
#* Outright prohibit such references by raising an immediate exception. This is
#  almost certainly what we should at least initially do.
#* Permit such references but only under the caveat that their forward reference
#  graph contains *NO* cycles. This is obviously quite a bit more work, as we'll
#  need to properly track this graph with a full-blown recursion guard. Data
#  structures and caching woes abound.
#
#Doing nothing is fine for the moment. Why? This is all edge-case extreme abuse
#misuse cases, anyway. The number of codebases that will even use forward
#references to refer to full-blown type hints (rather than simple types) is
#already vanishingly small. Ergo, our shrug is both smug and convenient. *shrug*

# ....................{ IMPORTS                            }....................
from beartype._check.forward.reference._cls.fwdrefcache import (
    BeartypeForwardRefABC,
    ref_proxy_cache,
)
from beartype._conf.confcommon import BEARTYPE_CONF_NONRANDOM
from beartype._data.kind.datakindiota import SENTINEL
from beartype._data.typing.datatypingport import Hint
from beartype._util.cache.func.utilcachefunc import callable_cached
from beartype._util.cls.pep.clspep3119 import is_object_isinstanceable
from beartype._util.error.utilerrwarn import issue_deprecation
from beartype._util.hint.pep.utilpeptest import is_hint_pep
from beartype._util.text.utiltextidentifier import is_dunder
from beartype._util.utilobjget import get_object_name

# ....................{ METACLASSES                        }....................
class BeartypeForwardRefMetaclass(type):
    '''
    **Forward reference metaclass** (i.e., metaclass of the
    :class:`.BeartypeForwardRefABC` superclass deferring the resolution of a
    type hint referencing an attribute that has yet to be defined in the lexical
    scope of the external caller).

    This metaclass memoizes each **forward reference** (i.e.,
    :class:`.BeartypeForwardRefABC` instance) according to the fully-qualified
    name of the attribute referenced by that forward reference. Doing so ensures
    that only the first :class:`.BeartypeForwardRefABC` instance referring to a
    unique attribute is required to dynamically resolve that attribute at
    runtime; all subsequent :class:`.BeartypeForwardRefABC` instances referring
    to the same attribute transparently reuse the attribute previously resolved
    by the first such instance, effectively reducing the time cost of resolving
    forward references to a constant-time operation with negligible constants.

    This metaclass dynamically and efficiently resolves each forward reference
    in a just-in-time (JIT) manner on the first :func:`isinstance` call whose
    second argument is that forward reference. Forward references *never* passed
    to the :func:`isinstance` builtin are *never* resolved, which is good.
    '''

    # ....................{ DUNDERS                        }....................
    #FIXME: This is great, but still insufficient. Additionally:
    #* If the caller resides in a "beartype."-prefixed submodule, do what we
    #  currently do.
    #* Else, immediately resolve the referent by accessing
    #  "__resolved_type_beartype__" and then (as above) proxy the __getattr__()
    #  of this referent by calling getattr() against this referent.
    def __getattr__(  # type: ignore[misc]
        cls: BeartypeForwardRefABC, hint_name: str) -> BeartypeForwardRefABC:
        '''
        **Fully-qualified forward reference subclass** (i.e.,
        :class:`.BeartypeForwardRefABC` subclass whose metaclass is this
        metaclass and whose
        :attr:`.BeartypeForwardRefABC.__hint_name_beartype__` class variable is
        the fully-qualified name of an external class).

        This dunder method creates and returns a new forward reference subclass
        referring to an external class whose name is concatenated from (in
        order):

        #. The fully-qualified name of the external package or module referred
           to by the passed forward reference subclass.
        #. The passed unqualified basename, presumably referring to a
           subpackage, submodule, or class of that external package or module.

        Design
        ------
        The syntactic implementation of this dunder method is largely trivial.
        The semantic justification for this implementation is, however, anything
        but. Indeed, justifying this implementation warrants a full-length
        dissertation on runtime resolution of forward references. This is that
        dissertation.

        Broadly speaking, there are two use cases for which CPython implicitly
        invokes this dunder method: two use cases whose intentions and
        requirements are so at odds with one another that seamlessly satisfying
        both is an exercise in code torture.

        The first use case is the intended (and also most common) use case:
        **absolute forward reference resolution deferral.** Given a
        :pep:`484`-compliant stringified absolute forward reference to a
        subscripted generic that has yet to be defined (e.g.,
        ``"some_package.some_submodule.SomeType[T]"``), how *exactly* does
        :mod:`beartype` resolve that subscripted generic in a manner consistent
        with efficient runtime type-checking? Is such resolution even feasible?
        The answers, of course, are: "Carefully." and "Yuppers."

        One brute-force approach to resolving stringified forward references
        containing arbitrarily complex Python expressions at runtime would be to
        parse those references through a Python-specific Parser Expression
        Grammar (PEG). Although technically feasible, embedding a full-blown
        Python parser within :mod:`beartype` would be so fragile and inefficient
        as to be effectively infeasible. Consequently, :mod:`beartype` does
        *not* do that. Instead, :mod:`beartype` is clever.

        The clever approach is to charm Python itself into parsing those
        references. After all, Python clearly knows how to parse Python.
        :mod:`beartype` simply needs to transform those references into some
        format readily digestible by Python's builtin Python parser. Our
        solution? The :func:`eval` builtin coupled with our non-standard
        :class:`beartype._check.forward.scope.fwdscopecls.BeartypeForwardScope`
        dictionary subclass, which overrides the ``__missing__`` dunder method
        explicitly called by the superclass :meth:`dict.__getitem__` method
        implicitly called on each ``[``- and ``]``-delimited attempt to access a
        forward reference whose type has yet to be resolved by mapping the name
        of that reference to an actual **forward reference proxy** (i.e.,
        instance of this metaclass). The :func:`eval` builtin then implicitly
        instantiates one forward reference proxy encapsulating each undefined
        top-level attribute inside the passed absolute forward reference. Given
        ``"some_package.some_submodule.SomeType[T]"``, :func:`eval` then first
        instantiates one forward reference proxy encapsulating the undefined
        top-level attribute ``"some_package"``. Clearly, a forward reference
        proxy for ``"some_package"`` does *not* suffice to proxy the entire
        ``"some_package.some_submodule.SomeType[T]"`` forward reference.

        Cue this dunder method. :func:`eval` then attempts to access the
        ``"some_submodule"`` attribute of the forward reference proxy for
        ``"some_package"``. Doing so implicitly invokes this dunder method,
        which then instantiates another forward reference proxy encapsulating
        the undefined mid-level attribute ``"some_submodule"``. :func:`eval`
        then attempts to access the ``"SomeType[T]"`` attribute of the forward
        reference proxy for ``"some_submodule"``. Doing so implicitly invokes
        this dunder method, which then instantiates a final forward reference
        proxy encapsulating the undefined leaf-level attribute
        ``"SomeType[T]"``. Lastly, :func:`eval` then evaluates the expression
        ``"some_package.some_submodule.SomeType[T]"`` to the proxy for
        ``"SomeType[T]"``, which :func:`eval` then returns as its value. The
        intermediate proxies for both ``"some_package"`` and
        ``"some_submodule"`` are now irrelevant and thus garbage-collectable.

        This scheme is simple, effective, and (most importantly) efficient. But
        it's also prone to overly permissive proxying that intersects poorly
        with the second use case. Why? Because this scheme naively assumes that
        each invocation of this dunder method is **trustworthy**: that is, that
        each invocation of this dunder method is an attempt to access some valid
        module attribute that is known *a priori* to exist. This assumption
        holds for stringified absolute forward references used as type hints by
        the caller internally proxied by :mod:`beartype`. This assumption breaks
        when an invocation of this dunder method is **untrustworthy**: that is,
        when an invocation of this dunder method is merely an attempt to decide
        whether a module contains an attribute that is not known *a priori* to
        exist. In short, the second use case is the :func:`hasattr` builtin.

        The :func:`hasattr` builtin is actually implemented in terms of the
        :func:`getattr` builtin via the Easier to Ask for Permission than
        Forgiveness (EAFP) principle, implying that :func:`hasattr` internally
        invokes this dunder method. Although implemented in low-level C, a
        pure-Python implementation of :func:`hasattr` might vaguely resemble:

        .. code-block:: python

           def hasattr(obj: object, attr_name: str) -> bool:
               try:
                   getattr(obj, attr_name)
               except AttributeError:
                   return False
               return True

        The :func:`hasattr` builtin thus expects this dunder method to raise the
        :exc:`AttributeError` exception when the module proxied by this forward
        reference proxy fails to define an attribute with the passed name.
        However, this expectation conflicts with the overly permissive proxying
        performed by the scheme outlined above. In that first use case,
        :mod:`beartype` encapsulates an external module that is *not* safely
        importable with this forward reference proxy. Since :mod:`beartype` has
        *no* safe means of deciding whether that module actually defines an
        attribute with the passed name or not, :mod:`beartype` naively assumes
        that module to define that attribute. Under the scheme outlined above,
        this dunder method would *never* raise the :exc:`AttributeError` and the
        :func:`hasattr` attribute would *always* return :data:`True` when passed
        a forward reference proxy.

        Does this second use case arise in practice? In theory, it shouldn't.
        After all, forward reference proxies are mostly isolated to private
        subpackages in the :mod:`beartype` codebase... *mostly.* In practice,
        this second use case commonly arises. For efficiency, :mod:`beartype`
        replaces unusable stringified absolute forward references that are root
        type hints annotating the parameters and returns of
        :func:`beartype.beartype`-decorated callable with usable forward
        reference proxies. Popular third-party frameworks like pytest and
        Django then introspect those forward reference proxies during their
        non-trivial workloads. This introspection either directly calls the
        :func:`hasattr` builtin *or* replicates that builtin in pure-Python to
        detect whether those forward reference proxies define framework-specific
        dunder attributes of relevance to those frameworks.

        Parameters
        ----------
        cls : Type[BeartypeForwardRefABC]
            Forward reference subclass to concatenate this basename against.
        hint_name : str
            Unqualified basename to be concatenated against this forward
            reference subclass.

        Returns
        -------
        BeartypeForwardRefABC
            Fully-qualified forward reference subclass concatenated as above.
        '''

        # Previously cached target referent type hint this forward reference
        # proxy refers to if a prior call of this method already resolved this
        # referent *OR* the sentinel placeholder otherwise (i.e., if this is the
        # first call of this method passed this proxy).
        referent_hint = (
            ref_proxy_cache.get_ref_proxy_referent_hint_if_resolved_or_sentinel(
                cls))

        # If this forward reference proxy has already been resolved to its
        # referent (e.g., by a prior isinstance() or issubclass() type-check),
        # forward this dunder method call directly to that referent.
        if referent_hint is not SENTINEL:
            # print(f'Forward reference proxy "{cls.__hint_name_beartype__}" resolved to {referent_hint}!')
            return getattr(referent_hint, hint_name)
        # Else, this forward reference proxy has yet to be resolved.
        #
        # If a non-existent dunder attribute was requested, assume this
        # erroneous attempt to access a non-existent attribute of this forward
        # reference proxy to *ACTUALLY* be an Easier to Ask for Permission than
        # Forgiveness (EAFP)-driven to detect whether this forward scope defines
        # this attribute ala the hasattr() builtin. See also the "Design"
        # subsection of this dunder method's docstring for further commentary.
        elif is_dunder(hint_name):
            # Raise the standard "AttributeError" exception expected by EAFP.
            #
            # Note that we intentionally avoid suffixing the exception message
            # by a "." character here. Python treats "AttributeError" exceptions
            # as special. Notably, Python appears to actually:
            # 1. Parse apart the messages of these exceptions for the
            #    double-quoted attribute name embedded in these messages.
            # 2. Suffix these messages by a "." character followed by a sentence
            #    suggesting an existing attribute with a similar name to that of
            #    the attribute name previously parsed from these messages.
            #
            # For example, given an erroneous lookup of a non-existent dunder
            # attribute "__nomnom_beartype__", Python expands the exception
            # message raised below into:
            #     AttributeError: Forward reference proxy "MuhRef" dunder
            #     attribute "__nomnom_beartype__" not found. Did you mean:
            #     '__hint_name_beartype__'?
            raise AttributeError(
                f'Forward reference proxy "{cls.__name__}" '
                f'dunder attribute "{hint_name}" not found'
            )
        # Else, the caller resides inside the "beartype" package and is
        # requesting a non-existent non-dunder attribute. In this case, safely
        # assume this request to comprise a higher-level attempt to resolve an
        # absolute stringified forward reference (e.g., the request for the
        # "some_submodule" attribute from the "some_package" forward reference
        # proxy given the initial absolute stringified forward reference
        # "some_package.some_submodule.SomeType").

        # Avoid circular import dependencies.
        from beartype._check.forward.reference.fwdrefproxy import (
            proxy_hint_pep484_ref_str_subbable)

        # Return a new fully-qualified forward reference proxy subclass
        # concatenated as described above.
        return proxy_hint_pep484_ref_str_subbable(
            scope_name=cls.__scope_name_beartype__,
            hint_name=f'{cls.__hint_name_beartype__}.{hint_name}',
            exception_prefix=cls.__exception_prefix_beartype__
        )


    @callable_cached
    def __repr__(cls: BeartypeForwardRefABC) -> str:  # type: ignore[misc]
        '''
        Machine-readable string representing this forward reference subclass.

        This dunder method is memoized for efficiency.
        '''

        # Machine-readable representation to be returned.
        #
        # Note that this representation intentionally:
        # * Is prefixed by the @beartype-specific substring "<forwardref ",
        #   resembling the representation of classes (e.g., "<class 'bool'>").
        #   Why? Because various other @beartype submodules ignore objects whose
        #   representations are prefixed by the "<" character, which are
        #   usefully treated as having a standard representation that is
        #   ignorable for most intents and purposes. This includes:
        #   * The die_if_hint_pep604_inconsistent() raiser.
        # * Omits the prefixing substring "__" and suffixing substring
        #   "_beartype__" from the names of class variables appended below. Why?
        #   Because those substrings are semantically meaningless and only serve
        #   to further obfuscate the underlying forward reference in tracebacks.
        cls_repr = f'<forwardref {cls.__name__}('

        # If this reference thinly wraps a PEP 749-compliant object-oriented
        # forward reference (i.e., "annotationlib.ForwardRef" object), append
        # *ONLY* the representation of that object for brevity.
        if cls.__hint_pep749_ref_beartype__:
            cls_repr += f'pep749_ref={repr(cls.__hint_pep749_ref_beartype__)}'
        # Else, this reference does *NOT* thinly wrap a PEP 749-compliant
        # object-oriented forward reference (i.e., "annotationlib.ForwardRef"
        # object). By elimination, this reference *MUST* thickly wrap a
        # PEP 484-compliant stringified forward reference. In this case...
        else:
            # Append *ONLY* the representations of the relevant strings.
            cls_repr += (
                  f'name={repr(cls.__hint_name_beartype__)}'
                f', scope_name={repr(cls.__scope_name_beartype__)}'
            )

            # If this reference is additionally closure-relative, notify the
            # user of that fact as well.
            if cls.__func_local_parent_codeobj_weakref_beartype__:
                cls_repr += (
                    f', func_local_parent_codeobj_weakref='
                    f'{repr(cls.__func_local_parent_codeobj_weakref_beartype__)}'
                )
            # Else, this reference is *NOT* additionally closure-relative.

        #FIXME: Unit test this edge case, please.
        # If this is a subscripted forward reference subclass, append additional
        # metadata representing this subscription.
        #
        # Ideally, we would test whether this is a subclass of the
        # "BeartypeForwardRefSubbedABC" superclass as follows:
        #     if issubclass(cls, BeartypeForwardRefSubbedABC):
        #
        # Sadly, doing so invokes the __subclasscheck__() dunder method defined
        # above, which invokes the
        # BeartypeForwardRefABC.__is_subclass_beartype__() method defined
        # above, which tests the type referred to by this subclass rather than
        # this subclass itself. In short, this is why you play with madness.
        try:
            cls_repr += (
                f', args={repr(cls.__args_beartype__)}'
                f', kwargs={repr(cls.__kwargs_beartype__)}'
            )
        # If doing so fails with the expected "AttributeError", then this is
        # *NOT* a subscripted forward reference subclass. Since this is
        # ignorable, silently ignore this common case. *sigh*
        except AttributeError:
            pass

        # Close this representation.
        cls_repr += ')>'

        # Return this representation.
        return cls_repr

    # ....................{ DUNDERS ~ pep : 3119 : instance}....................
    def __instancecheck__(cls: BeartypeForwardRefABC, obj: object) -> bool:  # type: ignore[misc]
        '''
        :data:`True` only if the passed object satisfies the target referent
        type hint referred to by this **forward reference proxy** (i.e.,
        concrete :class:`.BeartypeForwardRefABC` subclass whose metaclass is
        this metaclass and whose class variables refer to that referent).

        Specifically:

        * If that referent is an isinstanceable type, this dunder method returns
          :data:`True` only if this object is an instance of that type.
        * Else if that referent is type hint supported by :mod:`beartype`, this
          dunder method returns the boolean returned by the
          :func:`beartype.door.is_bearable` statement-level type-checker when
          passed both this object and hint.

        Parameters
        ----------
        cls : Type[BeartypeForwardRefABC]
            Forward reference proxy to test this object against.
        obj : object
            Arbitrary object to be tested.

        Returns
        -------
        bool
            :data:`True` only if this object satisfies this referent.
        '''

        # ....................{ RESOLVE                    }....................
        # @beartype-supported type hint referred to by the PEP-compliant forward
        # reference encapsulated by this proxy.
        #
        # Note that merely accessing this property suffices to raise a
        # human-readable exception if the type hint referred to by this
        # reference is *NOT* supported by @beartype. Ergo, this hint is now
        # guaranteed to be supported and thus safely passable to the
        # is_bearable() dunder method defined below. Maybe. WHO EVEN KNOWS!?!
        resolved_hint = ref_proxy_cache.cache_ref_proxy_referent_hint(cls)

        # ....................{ ISINSTANCEABLE             }....................
        # If
        if (
            # This hint is isinstanceable (i.e., safely passable directly as the
            # second parameter to the isinstance() builtin) *AND*...
            is_object_isinstanceable(resolved_hint) and
            # This hint is *NOT* PEP-compliant (e.g., due to being a PEP 484- or
            # 585-compliant generic in either subscripted or unsubscripted
            # form, which conveys more semantics than merely conveyed by a
            # simple PEP-noncompliant isinstanceable type)...
            not is_hint_pep(resolved_hint)
        ):
        # Then this hint is a PEP-noncompliant isinstanceable object. In this
        # case, reduce to an efficient call to the isinstance() builtin.
        #
        # Note that:
        # * This is the common case. Technically, PEP 484 (and thus @beartype as
        #   well) permits forward references to refer to arbitrary type hints.
        #   Pragmatically, 99% of *ALL* real-world forward references of
        #   interest to production workflows refer to isinstanceable types.
        # * This is only an optimization, albeit an extremely critical one.
        #   @beartype-generated type-checking wrapper code effectively reduces
        #   to direct invocations of the isinstance() builtin and thus
        #   transitive indirect invocations of this dunder method implicitly
        #   called by that builtin under PEP 3119 semantics. This dunder method
        #   is thus on the hot path for @beartype. If optimization is warranted
        #   anywhere in the @beartype codebase, it is here.
            # print(f'Isinstanceable resolved hint detected: {repr(resolved_hint)}')
            return isinstance(obj, resolved_hint)
        # Else, this hint is either:
        # * Not isinstanceable, in which case this hint is *NOT* safely passable
        #   to the isinstance() builtin.
        # * A PEP-compliant isinstanceable object, in which case this hint is
        #   safely passable to the isinstance() builtin but only by ignoring the
        #   unignorable semantics conveyed by this object's conformance with one
        #   or more PEP standards.
        #
        # In either case, avoid passing this hint to that builtin.

        # ....................{ NON-ISINSTANCEABLE         }....................
        # By validation internally performed by the
        # cache_ref_proxy_referent_hint() method called above, this hint is
        # supported by @beartype and thus safely passable to the slower (but
        # still micro-optimized to the hilt) @beartype-specific pair of
        # is_bearable() and die_if_unbearable() functions.

        # Avoid circular import dependencies.
        from beartype.door._func.doorfunc import is_bearable

        # Return true only if the passed object satisfies this hint.
        return is_bearable(
            obj=obj,
            hint=resolved_hint,

            #FIXME: *DEFINITELY INSUFFICIENT.* It's essential that we respect
            #the user configuration by instead:
            #* Defining a new "BeartypeForwardRefABC.__conf_beartype__" class
            #  variable.
            #* Adding a new *MANDATORY* "conf" parameter to *ALL* proxy_*()
            #  functions defined by the "fwdrefproxy" submodule.
            #* Pass that parameter in all calls to those functions.
            #* Generalize _proxy_hint_ref() to assign "__conf_beartype__" like
            #  so:
            #      # New keyword dictionary permuted from this input.
            #      conf_nonrandom_kwargs = conf.kwargs.copy()
            #      conf_nonrandom_kwargs['is_debug'] = True

            #      # New beartype configuration initialized by this dictionary.
            #      conf_nonrandom = BeartypeConf(**conf_nonrandom_kwargs)
            #
            #      ref_proxy.__conf_beartype__ = conf_nonrandom
            #* Pass "cls.__conf_beartype__" below. Phew!

            # Force this object to be type-checked deterministically (e.g., by
            # only type-checking the first items of pure-Python sequences). By
            # default, beartype type-checks objects non-deterministically (e.g.,
            # by type-checking randomly selected items of these sequences). This
            # default behaviour reduces the statistical likelihood of false
            # negatives (e.g., this is_bearable() call returning true when it
            # should instead return false). That's good. Unfortunately, this
            # default behaviour is non-deterministic and thus unstable across
            # repeated calls to related type-checking functionality requiring
            # stable type-checking decisions. That's bad.
            #
            # Does the latter use case actually arise here? It does. If this
            # is_bearable() call indicates this object to violate this hint by
            # returning false from this __instancecheck__() dunder method, the
            # higher-level "beartype._check.error" error handler then
            # subsequently handles this violation by calling the
            # beartype-specific __instancecheck_str__() dunder method defined
            # below to generate a human-readable exception message. Predictably,
            # that __instancecheck_str__() dunder method does so by effectively
            # (though not actually) calling the die_if_unbearable() raiser. You
            # see the issue, we trust. Since both this is_bearable() call *AND*
            # that die_if_unbearable() call behave non-deterministically by
            # default, the consequence is a catastrophic desynchronization
            # between the two for the common use case in which this object
            # either is *OR* contains one or more pure-Python non-empty
            # sequences (which is where beartype's non-deterministic
            # type-checking behaviour arises). Forcing deterministic
            # type-checking behaviour trivially avoids such desynchronization,
            # albeit at a non-negligible cost of increasing the statistical
            # likelihood of false negatives from this first is_bearable() call.
            # That's not great, obviously, but that's still significantly better
            # than catastrophic desynchronization. It's in the name. It's
            # catastrophic. Can't get much worse than a catastrophe.
            conf=BEARTYPE_CONF_NONRANDOM,
        )


    def __instancecheck_str__(cls: BeartypeForwardRefABC, obj: object) -> str:
        '''
        Human-readable substring to be embedded in the message of a
        :exc:`beartype.roar.BeartypeCallHintViolation` describing why the object
        currently being type-checked violates the type hint referred to by this
        :mod:`beartype`-specific forward reference proxy, in response to a prior
        call to the sibling :meth:`.__instancecheck__` dunder method passed the
        passed object returning :data:`False`.

        This :mod:`beartype`-specific dunder method is internally called by the
        higher-level :mod:`beartype._check.error` subpackage when handling
        type-checking violations indicated by the sibling :pep:`3119`-compliant
        :meth:`.__instancecheck__` dunder method defined above returning
        :data:`False`. The workflow is non-trivial. The
        :func:`beartype.beartype` decorator dynamically generates type-checking
        wrapper functions whose bodies detect and handle type-checking
        violations by calling a violation handler defined by the private
        :mod:`beartype._check.error` subpackage. That handler then raises a
        human-readable exception message describing why the object currently
        being type-checked violates the type hint referred to by this
        :mod:`beartype`-specific forward reference proxy. How? By internally
        calling this :mod:`beartype`-specific dunder method defined on *all*
        such proxies, of course. Truly, *what could be simpler!?*

        Parameters
        ----------
        cls : Type[BeartypeForwardRefABC]
            Forward reference proxy the :meth:`.__instancecheck__` dunder method
            previously detected the passed object as violating the type hint
            referred to by this proxy.
        obj: object
            That object.

        Returns
        -------
        str
            Human-readable substring to be embedded in the message of a
            :exc:`beartype.roar.BeartypeCallHintViolation` exception.
        '''

        # ....................{ IMPORTS                    }....................
        # Avoid circular import dependencies.
        from beartype._check.cls.call.calldataexternal import (
            BEARTYPE_CALL_EXTERNAL_META)
        from beartype._check.error.errmain import (
            get_hint_object_violation_message)

        # ....................{ RESOLVE                    }....................
        # @beartype-supported type hint referred to by the PEP-compliant forward
        # reference encapsulated by this proxy.
        #
        # Note that this beartype-specific __instancecheck_str__() dunder method
        # should *ONLY* be called when the __instancecheck__() dunder method
        # defined above was already implicitly called by an isinstance() call in
        # the body of a beartype-generated type-checking wrapper function, in
        # which case that prior __instancecheck__() call is guaranteed to have
        # already successfully resolved this forward reference to this type hint
        # by accessing this property (*WITHOUT* that property internally raising
        # an exception). In short, this access should trivially reduce to an
        # efficient O(1)-style cached property lookup.
        resolved_hint = ref_proxy_cache.cache_ref_proxy_referent_hint(cls)

        # ....................{ MESSAGE                    }....................
        # Type-checking violation message describing the failure of this object
        # to satisfy the target referent type hint referred to by this forward
        # reference proxy under the same beartype configuration employed by the
        # sibling is_bearable() call performed by the sibling
        # __instancecheck__() dunder method.
        #
        # Note that the *ONLY* legitimate caller of this beartype-specific
        # dunder method is the "beartype._check.error" subpackage, which embeds
        # this message as a substring of a larger message of a subsequently
        # raised larger-scale violation exception.
        violation_message = get_hint_object_violation_message(
            # Beartype external call metadata singleton, required to
            # transparently resolve the extreme edge case (and possibly even
            # PEP-noncompliant abuse or misuse) in which this beartype-specific
            # forward reference proxy refers to a type hint that itself either
            # is or contains one or more:
            # * PEP 484-compliant stringified forward reference type hints.
            # * PEP 749-compliant objectified forward reference type hints.
            #
            # Ideally, that should *NEVER* occur. Any codebase encouraging
            # forward references to reference one another is a codebase inviting
            # a cyclic forward reference graph inducing infinite recursion.
            #
            # Pragmatically, that will *DEFINITELY* occur. When that does, we
            # transparently enable those forward references to themselves be
            # resolved into their target referent type hints through this
            # singleton, which performs call stack introspection up the call
            # stack as a means of resolving those forward references.
            #
            # Note that explicitly passing this singleton here preserves
            # synchronization with the is_bearable() call performed by the
            # sibling __instancecheck__() dunder method, which implicitly
            # leverages this exact same singleton for the same purpose.
            call_curr=BEARTYPE_CALL_EXTERNAL_META,
            # See the is_bearable() call performed by the sibling
            # __instancecheck__() dunder method for further details.
            conf=BEARTYPE_CONF_NONRANDOM,
            hint=resolved_hint,
            obj=obj,
        )

        # ....................{ RETURN                     }....................
        # Return this message.
        return violation_message

    # ....................{ DUNDERS ~ pep : 3119 : subclass}....................
    def __subclasscheck__(cls: BeartypeForwardRefABC, obj: object) -> bool:  # type: ignore[misc]
        '''
        :data:`True` only if the passed object is a subclass of the target
        referent type referred to by this **forward reference proxy** (i.e.,
        concrete :class:`.BeartypeForwardRefABC` subclass whose metaclass is
        this metaclass and whose class variables refer to that referent).

        Parameters
        ----------
        cls : Type[BeartypeForwardRefABC]
            Forward reference proxy to test this object against.
        obj : object
            Arbitrary object to be tested.

        Returns
        -------
        bool
            :data:`True` only if this object is a subclass of that referent.

        Raises
        ------
        TypeError
            If this object is *not* a type.
        '''

        # PEP 3119-compliant isinstanceable type referred to by the
        # PEP-compliant forward reference encapsulated by this proxy.
        #
        # Note that merely accessing this property suffices to raise a
        # human-readable exception if the type hint referred to by this
        # reference is *NOT* an isinstanceable type. Ergo, this type is now
        # guaranteed to be isinstanceable and thus safely passable to the
        # issubclass() dunder method defined below. Hopefully. WHO EVEN KNOWS!?!
        resolved_type = ref_proxy_cache.cache_ref_proxy_referent_type(cls)

        # Return true only if the passed object is a subclass of this type.
        return issubclass(obj, resolved_type)  # type: ignore[arg-type]

    # ....................{ PROPERTIES                     }....................
    #FIXME: Unit test us up, please. Note that there is are two intriguing edge
    #cases that should be tested as well:
    #* When the target referent is itself a stringified forward reference.
    #* When the target referent is itself another forward reference proxy.
    @property
    def __resolved_hint_beartype__(cls: BeartypeForwardRefABC) -> Hint:  # type: ignore[misc]
        '''
        **Referent** (i.e., arbitrary type hint referred to by the forward
        reference encapsulated by this forward reference proxy after dynamically
        resolving this reference to this referent) if this reference refers to a
        **supported type hint** (i.e., object supported by the
        :func:`beartype.beartype` decorator as a valid type hint annotating
        callable parameters and returns) *or* raise an exception otherwise
        (e.g., if this type hint is unsupported by :mod:`beartype`).

        This class property is manually memoized for efficiency. However, note
        this class property is *not* automatically memoized (e.g., by the
        ``property_cached`` decorator). Why? Because manual memoization enables
        other functionality in the beartype codebase to explicitly unmemoize all
        previously memoized forward referents across all forward reference
        proxies, effectively forcing all subsequent calls of this property
        across all forward reference proxies to reimport their forward referents.
        Why is that desirable? Because other functionality in the beartype
        codebase detects when the user has manually reloaded user-defined
        modules defining user-defined types annotating user-defined callables
        previously decorated by the :mod:`beartype.beartype` decorator. Since
        reloading those modules redefines those types, all previously cached
        types (including those memoized by this property) *must* then be assumed
        to be invalid and thus uncached. In short, manual memoization allows
        beartype to avoid desynchronization between memoized and actual types.

        This class property is officially in the public :mod:`beartype` API and
        guaranteed to be available across *all* current and future
        :mod:`beartype` releases.

        Caveats
        -------
        Downstream callers consuming callable type hints modified by a
        previously applied :mod:`beartype.beartype` decorator may occasionally
        encounter **forward reference proxies** (i.e., instances of this
        metaclass). Forward reference proxies are *not* intended to be usable as
        perfect substitutes for the underlying classes they proxy. Instead,
        downstream callers are recommended to manually resolve these proxies to
        the underlying classes they proxy by accessing this property. Consider
        this trivial one-liner that does so for a type hint ``type_hint``:

        .. code-block:: python

           # If this type hint is actually a @beartype-specific forward
           # reference proxy that only refers to the desired type hint,
           # dereference that proxy to obtain that type hint.
           type_hint = getattr(
               type_hint, '__resolved_hint_beartype__', type_hint)

        Raises
        ------
        BeartypeCallHintForwardRefException
            If either:

            * This forward referent is unimportable.
            * This forward referent is importable but either:

              * Not a supported type hint.
              * A supported type hint that is this forward reference proxy,
                implying this proxy circularly proxies itself.
        '''

        # Trivially defer to this lower-level method of this global cache.
        return ref_proxy_cache.cache_ref_proxy_referent_hint(cls)


    @property
    def __resolved_type_beartype__(cls: BeartypeForwardRefABC) -> type:  # type: ignore[misc]
        '''
        **Referent type** (i.e., arbitrary type referred to by the forward
        reference encapsulated by this forward reference proxy after dynamically
        resolving this reference to this referent) if this reference refers to
        an **isinstanceable type** (i.e., class whose metaclass does *not*
        define an ``__instancecheck__()`` dunder method raising unexpected
        exceptions) *or* raise an exception otherwise (e.g., if this reference
        does *not* refer to an isinstanceable type).

        This class property is manually memoized for efficiency.

        This class property is officially in the public :mod:`beartype` API and
        guaranteed to be available across *all* current and future
        :mod:`beartype` releases.

        Raises
        ------
        BeartypeCallHintForwardRefException
            If either:

            * This forward referent is unimportable.
            * This forward referent is importable but either:

              * Not an isinstanceable type.
              * An isinstanceable type that is this forward reference proxy,
                implying this proxy circularly proxies itself.

        See Also
        --------
        :meth:`.__resolved_hint_beartype__`
            Further details.
        '''

        # Trivially defer to this lower-level method of this global cache.
        return ref_proxy_cache.cache_ref_proxy_referent_type(cls)


    #FIXME: Remove this officially deprecated property after a sufficient number
    #@beartype releases following @beartype 0.23.0, please. *sigh*
    @property
    def __type_beartype__(cls: BeartypeForwardRefABC) -> type:  # type: ignore[misc]

        # Fully-qualified name of this forward reference proxy metaclass.
        metaclass_name = get_object_name(type(cls))

        # Issue a deprecation warning.
        issue_deprecation(
            attr_name_deprecated=(
                f'{metaclass_name}.__type_beartype__'),
            attr_name_nondeprecated=(
                f'{metaclass_name}.__resolved_type_beartype__'),
        )

        # Defer to the equivalent non-deprecated property. *sigh*
        return cls.__resolved_type_beartype__
