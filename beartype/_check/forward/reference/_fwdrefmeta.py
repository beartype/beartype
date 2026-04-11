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

#FIXME: *THREAD-SAFETY*! The bodies of all of the following callables need to
#internally wrap *EVERYTHING* inside a submodule-specific "RLock":
#* __resolved_hint_beartype__.
#* __resolved_type_beartype__.
#* _is_ref_proxy_resolved().
#
#Maybe even more? No idea. Subtle race conditions ignite if we fail. *gulp*

# ....................{ IMPORTS                            }....................
from beartype.roar import (
    BeartypeCallHintForwardRefException,
    BeartypeCallHintPep484ForwardRefStrException,
)
from beartype._conf.confcommon import BEARTYPE_CONF_NONRANDOM
from beartype._data.cls.dataclsany import BeartypeAny
from beartype._data.kind.datakindiota import SENTINEL
from beartype._data.typing.datatypingport import Hint
from beartype._util.cls.pep.clspep3119 import (
    die_unless_object_isinstanceable,
    is_object_isinstanceable,
)
from beartype._util.cache.utilcachecall import callable_cached
from beartype._util.error.utilerrwarn import issue_deprecation
from beartype._util.hint.pep.proposal.pep484585.generic.pep484585genget import (
    get_hint_pep484585_generic_type)
from beartype._util.hint.pep.proposal.pep484585.generic.pep484585gentest import (
    is_hint_pep484585_generic)
from beartype._util.hint.pep.proposal.pep749.pep484749forwardref import (
    resolve_hint_pep484749_ref_object)
from beartype._util.hint.utilhinttest import (
    die_unless_hint,
    is_hint,
)
from beartype._util.module.utilmodimport import (
    import_module_attr,
    import_module_attr_or_sentinel,
)
from beartype._util.text.utiltextidentifier import is_dunder
from beartype._util.utilobject import get_object_name
from typing import Optional

# ....................{ PRIVATE ~ hints                    }....................
_BeartypeForwardRefABC = type[
    'beartype._check.forward.reference._fwdrefabc.BeartypeForwardRefABC']   # type: ignore[name-defined]
'''
:pep:`585`-compliant type hint matching all instances of this forward reference
metaclass.
'''

# ....................{ METACLASSES                        }....................
class BeartypeForwardRefMeta(type):
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
    #* Else, immediately resolve the referent by accessing "__resolved_type_beartype__"
    #  and then (as above) proxy the __getattr__() of this referent by calling
    #  getattr() against this referent.
    def __getattr__(  # type: ignore[misc]
        cls: _BeartypeForwardRefABC, hint_name: str) -> _BeartypeForwardRefABC:
        '''
        **Fully-qualified forward reference subclass** (i.e.,
        :class:`.BeartypeForwardRefABC` subclass whose metaclass is this
        metaclass and whose :attr:`.BeartypeForwardRefABC.__hint_name_beartype__`
        class variable is the fully-qualified name of an external class).

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
        _BeartypeForwardRefABC
            Fully-qualified forward reference subclass concatenated as above.
        '''

        #FIXME: Unit test up this edge case, please.
        # If this forward reference proxy has already been resolved to its
        # referent (e.g., by a prior isinstance() or issubclass() check),
        # forward this dunder method call directly to that referent.
        if _is_ref_proxy_resolved(cls):
            return getattr(cls.__resolved_hint_beartype__, hint_name)
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
            # by a "." character here. Why? Because Python treats
            # "AttributeError" exceptions as special. Notably, Python appears to
            # actually:
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
    def __repr__(cls: _BeartypeForwardRefABC) -> str:  # type: ignore[misc]
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
    def __instancecheck__(cls: _BeartypeForwardRefABC, obj: object) -> bool:  # type: ignore[misc]
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
        #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        # CAUTION: Synchronize with the __is_subclass_beartype__() method below.
        #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        # @beartype-supported type hint referred to by the PEP-compliant forward
        # reference encapsulated by this proxy.
        #
        # Note that merely accessing this property suffices to raise a
        # human-readable exception if the type hint referred to by this
        # reference is *NOT* supported by @beartype. Ergo, this hint is now
        # guaranteed to be supported and thus safely passable to the
        # is_bearable() dunder method defined below. Maybe. WHO EVEN KNOWS!?!
        resolved_hint = cls.__resolved_hint_beartype__

        # If the cls.__resolved_hint_beartype__() property dynamically resolving
        # the PEP 484-compliant stringified forward reference underlying this
        # proxy (if any) failed to do so by falling back to the
        # beartype-specific private "BeartypeAny" type, do *NOT* simply return
        # true only if the passed object is an instance of the external class
        # referenced by this forward reference. Why? Because the "BeartypeAny"
        # metaclass unconditionally returns true for all possible objects,
        # inviting false negatives (i.e., failure to raise type-checking
        # violations if this object is *NOT* an instance of that external
        # class). Luckily, we can do better. Specifically...
        if resolved_hint is BeartypeAny:
            #FIXME: Can we do even better? No idea. Maybe. Maybe not. We could
            #also try doing something like testing:
            #    get_object_name(obj) == f'__scope_name_beartype__.__hint_name_beartype__'
            #
            #Not sure if that's too restrictive and thus invites false
            #positives, which would be even worse than false negatives. Guess
            #we can just test that trivially and then discard the approach if it
            #clearly fails in obvious cases? Right. Sounds half-sane, huh?

            # Return true only if the unqualified basename of the type referred
            # to by this forward reference is the same as that of this object.
            # Since these two types share the same basename, this object is
            # likelier to be an instance of the type referred to by this forward
            # reference. The cautious reader will have noted the weasel word
            # "likelier" doing heavy lifting here.
            #
            # Technically, this is merely an ad-hoc heuristic. It's trivial to
            # concoct malicious (albeit thankfully unlikely) scenarios in which
            # an object whose type shares the same basename as that of a
            # forward reference is *NOT* an instance of the actual type referred
            # to by that reference. It happens. It's also unlikely.
            #
            # Pragmatically, this heuristic has the beneficial effect of
            # dramatically reducing the likelihood of false negatives in this
            # edge case (which is good) *WITHOUT* any concomitant harmful effect
            # like emitting false positives (which is also good). In other
            # words, this heuristic has entirely good effects and is thus
            # preferable to our only alternative (which is doing nothing).
            #
            # Why is this heuristic guaranteed to *NOT* emit false positives?
            # Assume this heuristic emitted false positives. Then this heuristic
            # invites erroneous type-checking violations by returning False when
            # it should instead return True for some object "obj" and forward
            # reference proxy "cls", implying:
            #     obj_classname != cls.__hint_name_beartype__
            #
            # However, this heuristic should instead return True, implying that
            # this object *MUST* be an instance of the type referred to by the
            # stringified forward reference proxied by this proxy, implying:
            #     obj_classname == cls.__hint_name_beartype__
            #
            # A contradiction! Ergo, this heuristic is guaranteed to *NOT* emit
            # false positives. QED. \o/
            return cls.__hint_name_beartype__ == obj.__class__.__name__
        # Else, that property succeeded. Ergo, this hint is trustworthy.

        # ....................{ ISINSTANCEABLE             }....................
        # If this hint is isinstanceable (i.e., safely passable directly as the
        # second parameter to the isinstance() builtin), reduce to an efficient
        # call to that builtin.
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
        if is_object_isinstanceable(resolved_hint):
            return isinstance(obj, resolved_hint)
        # Else, this hint is *NOT* isinstanceable and thus *NOT* safely passable
        # to the isinstance() builtin.

        # ....................{ NON-ISINSTANCEABLE         }....................
        # By validation internally performed by the "__resolved_hint_beartype__"
        # property accessed above, this hint is supported by @beartype and thus
        # safely passable to the substantially slower (but still as
        # micro-optimized to the hilt as feasible) @beartype-specific pair of
        # is_bearable() and die_if_unbearable() functions.

        # Avoid circular import dependencies.
        from beartype.door._func.doorfunc import is_bearable

        # Return true only if the passed object satisfies this hint.
        return is_bearable(
            obj=obj,
            hint=resolved_hint,

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


    #FIXME: Uncomment *AFTER* this dunder method actually behaves as expected.
    #We're currently getting false positives from closure references, probably
    #because "BeartypeAny" is a weirdo thing nobody understands. Ahh! Ahhhhhhh!
    # def __instancecheck_str__(cls, obj: object) -> str:
    def __instancecheck_strOHGODS__(cls, obj: object) -> str:
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

        # Avoid circular import dependencies.
        from beartype._check.error.errmain import get_hint_object_violation
        from beartype._check.metadata.call.callmetaexternal import (
            BEARTYPE_CALL_EXTERNAL_META)

        # Human-readable type-checking violation exception detailing the failure
        # of this object to satisfy the target referent type hint referred to by
        # this forward reference proxy under the same beartype configuration
        # employed by the is_bearable() call performed by the sibling
        # __instancecheck__() dunder method.
        check_violation = get_hint_object_violation(
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
            call_meta=BEARTYPE_CALL_EXTERNAL_META,
            hint=cls.__resolved_hint_beartype__,
            obj=obj,
            # See the is_bearable() call performed by the sibling
            # __instancecheck__() dunder method for further details.
            conf=BEARTYPE_CONF_NONRANDOM,
            # Nonsense required by the get_hint_object_violation() API. Our
            # younger self thought he was doing a good thing. YOUNGER SELF!!!!!!
            exception_prefix='',
        )

        # Return this violation exception's human-readable message.
        return str(check_violation)

    # ....................{ DUNDERS ~ pep : 3119 : subclass}....................
    def __subclasscheck__(cls: _BeartypeForwardRefABC, obj: object) -> bool:  # type: ignore[misc]
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

        #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        # CAUTION: Synchronize with the __is_instance_beartype__() method above.
        #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        # PEP 3119-compliant isinstanceable type referred to by the
        # PEP-compliant forward reference encapsulated by this proxy.
        #
        # Note that merely accessing this property suffices to raise a
        # human-readable exception if the type hint referred to by this
        # reference is *NOT* an isinstanceable type. Ergo, this type is now
        # guaranteed to be isinstanceable and thus safely passable to the
        # issubclass() dunder method defined below. Hopefully. WHO EVEN KNOWS!?!
        resolved_type = cls.__resolved_type_beartype__

        # If the cls.__resolved_type_beartype__() property dynamically resolving
        # the PEP 484-compliant stringified forward reference underlying this
        # proxy (if any) failed to do so by falling back to the
        # beartype-specific private "BeartypeAny" type...
        if resolved_type is BeartypeAny:
            # If this object is *NOT* a type, raise the standard "TypeError"
            # exception expected to be raised by the issubclass() builtin in
            # this common edge case. To do so trivially, we intentionally
            # masquerade as the root "object" superclass. *shrug*
            #
            # Weird Python is worky Python. It do be like that.
            issubclass(obj, object)  # type: ignore[arg-type]

            # Return true only if the unqualified basename of the type referred
            # to by this forward reference is the same as that of this object.
            return cls.__hint_name_beartype__ == obj.__name__  # type: ignore[attr-defined]
        # Else, that property succeeded. Ergo, this type is trustworthy.

        # Return true only if the passed object is a subclass of this type.
        return issubclass(obj, resolved_type)  # type: ignore[arg-type]

    # ....................{ PROPERTIES                     }....................
    #FIXME: Internally call is_hint() and die_unless_hint(), please. *sigh*
    #FIXME: Unit test us up, please. Note that there is are two intriguing edge
    #cases that should be tested as well:
    #* When the target referent is itself a stringified forward reference.
    #* When the target referent is itself another forward reference proxy.
    @property
    def __resolved_hint_beartype__(cls: _BeartypeForwardRefABC) -> Hint:  # type: ignore[misc]
        '''
        **Referent** (i.e., arbitrary type hint referred to by the forward
        reference encapsulated by this forward reference proxy after dynamically
        resolving this reference to this referent) if this reference refers to a
        **supported type hint** (i.e., object supported by the
        :func:`beartype.beartype` decorator as a valid type hint annotating
        callable parameters and returns) *or* raise an exception otherwise
        (e.g., if this type hint is unsupported by :func:`beartype.beartype`).

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
           type_hint = getattr(type_hint, '__resolved_hint_beartype__', type_hint)

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

        # ....................{ CACHE                      }....................
        # Cached referent referred to by this forward reference proxy if a prior
        # access of this property has already resolved this referent *OR* "None"
        # (i.e., if this is the first access of this property).
        referent: Optional[Hint] = _ref_proxy_to_resolved_hint_get(cls)

        # If a prior access of this property has already resolved this referent,
        # immediately return this previously resolved referent as is.
        if referent is not None:
            return referent
        # Else, this referent has yet to be resolved, implying this to be the
        # first call to this property.

        # ....................{ RESOLVE                    }....................
        # If this reference thinly wraps a PEP 749-compliant object-oriented
        # forward reference  (i.e., "annotationlib.ForwardRef" object), resolve
        # this reference in a PEP 749-specific manner.
        if cls.__hint_pep749_ref_beartype__:
            # Forward referent dynamically imported from this module if this
            # module is both importable and defines this referent *OR* the
            # sentinel placeholder (i.e., if this module is either unimportable
            # or fails to define this referent).
            referent = resolve_hint_pep484749_ref_object(
                hint=cls.__hint_pep749_ref_beartype__,
                exception_prefix=cls.__exception_prefix_beartype__,
            )
        # Else, this reference does *NOT* thinly wrap such a reference and
        # *MUST* thus instead thickly wrap a PEP 484-compliant stringified
        # forward reference. In this case, resolve this reference in a PEP
        # 484-specific manner.
        else:
            referent = _resolve_hint_pep484_ref_str(cls)

        # ....................{ VALIDATE                   }....................
        # If this referent is this forward reference proxy, this proxy
        # circularly proxies itself. Since allowing this edge case would openly
        # invite infinite recursion, we detect this edge case and instead raise
        # a human-readable exception.
        if referent is cls:
            raise BeartypeCallHintForwardRefException(
                f'{_make_ref_proxy_exception_prefix(cls)}'
                f'that target referent circularly '
                f'(i.e., infinitely recursively) references itself.'
            )
        # Else, this referent is *NOT* this forward reference proxy.

        # Cache this referent for subsequent lookup by this property *BEFORE*
        # validating this referent to be a supported hint. If this property is
        # validated to *NOT* be a supported hint, this referent will be
        # immediately uncached below. Of course, this is insane. Ideally, this
        # referent would be cached only *AFTER* validating this referent to be a
        # supported hint. Unfortunately, doing so invites infinite recursion as
        # follows (in order):
        # * This __resolved_hint_beartype__() property getter calls...
        # * die_unless_hint(), which calls...
        # * die_unless_object_isinstanceable(), which calls...
        # * "isinstance(None, cls)", which calls...
        # * BeartypeForwardRefMeta.__subclasscheck__(), which calls...
        # * "issubclass(obj, cls.__resolved_type_beartype__)", which calls...
        # * This __resolved_hint_beartype__() property getter, which calls...
        # * die_unless_hint() yet again. Repeat as needed for pain.
        #
        # Caching this referent first circumvents this recursion by ensuring
        # that all subsequent access of this property after the first access of
        # this property casually returns this referent rather than repeatedly
        # (thus uselessly) calling the die_unless_hint() raiser.
        _cache_ref_proxy_referent(cls=cls, referent=referent)

        # If this referent is *NOT* a supported type hint...
        #
        # Note that:
        # * This tester is memoized and thus requires parameters be passed only
        #   positionally.
        # * The optional "is_ref_proxy_valid: bool = False" parameter accepted
        #   by this tester is intentionally left unpassed. Doing so ensures
        #   that, if this referent is itself a forward reference proxy, this
        #   referent is *NOT* treated as isinstanceable if that proxy *CANNOT*
        #   be resolved to the referent that proxy refers to. While an unlikely
        #   edge case, unlikely edge cases are million-to-one chances in a
        #   Pratchett novel: you just know it's coming up.
        if not is_hint(referent):
            # Uncache this referent. See above for commentary.
            _uncache_ref_proxy_referent(cls=cls, referent=referent)

            # Raise a readable exception detailing why this referent is *NOT* a
            # supported type hint.
            die_unless_hint(
                hint=referent,  # pyright: ignore
                exception_cls=BeartypeCallHintForwardRefException,
                exception_prefix=_make_ref_proxy_exception_prefix(cls),
            )
        # Else, this referent is a supported type hint.

        # ....................{ RETURN                     }....................
        # Return this referent.
        return referent  # type: ignore[return-value]


    @property
    def __resolved_type_beartype__(cls: _BeartypeForwardRefABC) -> type:  # type: ignore[misc]
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

        # ....................{ CACHE                      }....................
        # Cached referent referred to by this forward reference proxy if a prior
        # access of this property has already resolved this referent *OR* "None"
        # (i.e., if this is the first access of this property).
        referent: Optional[type] = _ref_proxy_to_resolved_type_get(cls)

        # If a prior access of this property has already resolved this referent,
        # immediately return this previously resolved referent as is.
        if referent is not None:
            return referent
        # Else, this referent has yet to be resolved, implying this to be the
        # first call to this property.

        # ....................{ RESOLVE                    }....................
        # Cached referent referred to by this forward reference proxy if this
        # referent is a hint supported by @beartype *OR* raise an exception
        # (i.e., if @beartype fails to support this hint).
        referent = cls.__resolved_hint_beartype__

        # ....................{ VALIDATE                   }....................
        # If this referent is a subscripted generic (e.g., "MuhGeneric[int]")...
        if is_hint_pep484585_generic(referent):  # pyright: ignore
            # Reduce this referent to the child type subscripting this generic
            # (e.g., "int" in the prior example). Why? Because subscripted
            # generics are neither isinstanceable *NOR* issubclassable: e.g.,
            #     >>> MuhGeneric[T]: ...
            #     >>> issubclass(type, MuhGeneric)
            #     TypeError: issubclass() argument 2 cannot be a
            #     parameterized generic
            referent = get_hint_pep484585_generic_type(
                hint=referent,  # pyright: ignore
                exception_cls=BeartypeCallHintForwardRefException,
                exception_prefix=cls.__exception_prefix_beartype__,
            )

            # Re-cache this referent under this preferable reduction.
            _cache_ref_proxy_referent(cls=cls, referent=referent)
        # Else, this referent is *NOT* a subscripted generic.

        # If this referent is *NOT* an isinstanceable type...
        #
        # Note that:
        # * This tester is memoized and thus requires parameters be passed only
        #   positionally.
        # * The optional "is_ref_proxy_valid: bool = False" parameter accepted
        #   by this tester is intentionally left unpassed. Doing so ensures
        #   that, if this referent is itself a forward reference proxy, this
        #   referent is *NOT* treated as isinstanceable if that proxy *CANNOT*
        #   be resolved to the referent that proxy refers to.
        #   While an unlikely edge case, unlikely edge cases are like
        #   million-to-one chances in a Pratchett novel: they're coming up.
        if not is_object_isinstanceable(referent):
            # Uncache this referent. See also the "__resolved_hint_beartype__"
            # property for further commentary.
            _uncache_ref_proxy_referent(cls=cls, referent=referent)  # pyright: ignore

            # Raise a readable exception detailing why this referent is *NOT* an
            # isinstanceable type.
            die_unless_object_isinstanceable(
                obj=referent,  # pyright: ignore
                exception_cls=BeartypeCallHintForwardRefException,
                exception_prefix=_make_ref_proxy_exception_prefix(cls),
            )
        # Else, this referent is an isinstanceable type.

        # Return this referent.
        return referent  # type: ignore[return-value]


    #FIXME: Remove this officially deprecated property after a sufficient number
    #@beartype releases following @beartype 0.23.0, please. *sigh*
    @property
    def __type_beartype__(cls: _BeartypeForwardRefABC) -> type:  # type: ignore[misc]

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

# ....................{ PRIVATE ~ globals : hint           }....................
_ref_proxy_to_resolved_hint: dict[_BeartypeForwardRefABC, Hint] = {}
'''
**Forward reference type hint referent cache** (i.e., dictionary mapping from
each forward reference proxy to the target referent type hint referred to by
that proxy).

This cache serves a dual purpose. Notably, this cache both enables:

* External callers to iterate over all previously instantiated forward reference
  proxies. This is particularly useful when responding to module reloading,
  which requires that *all* previously cached types be uncached.
* The
  :attr:`.BeartypeForwardRefMeta.__resolved_hint_beartype__` property to
  internally memoize this referent. Since the existing ``property_cached``
  decorator could also trivially do so, this is a negligible side effect.
'''


_ref_proxy_to_resolved_hint_get = _ref_proxy_to_resolved_hint.get
'''
:meth:`dict.get` method bound to the :data:`._ref_proxy_to_resolved_hint` global
dictionary, globalized as a negligible microoptimization.
'''

# ....................{ PRIVATE ~ globals : type           }....................
_ref_proxy_to_resolved_type: dict[_BeartypeForwardRefABC, type] = {}
'''
**Forward reference type referent cache** (i.e., dictionary mapping from each
forward reference proxy to the target referent type referred to by that proxy).

See Also
--------
:data:`._ref_proxy_to_resolved_hint`
    Further details.
'''


_ref_proxy_to_resolved_type_get = _ref_proxy_to_resolved_type.get
'''
:meth:`dict.get` method bound to the :data:`._ref_proxy_to_resolved_type` global
dictionary, globalized as a negligible microoptimization.
'''

# ....................{ PRIVATE ~ testers                  }....................
#FIXME: Unit test us up, please.
def _is_ref_proxy_resolved(cls: _BeartypeForwardRefABC) -> bool:
    '''
    :data:`True` only if the passed **forward reference proxy** (i.e.,
    :class:`._BeartypeForwardRefABC` object) has already been resolved to its
    **target referent** (i.e., type hint referred to by this source reference).

    Parameters
    ----------
    cls : _BeartypeForwardRefABC
        Forward reference proxy to be inspected.

    Returns
    -------
    bool
        :data:`True` only if this proxy has been resolved to its referent.
    '''
    assert isinstance(cls, BeartypeForwardRefMeta), (
        f'{repr(cls)} not beartype forward reference proxy.')

    # Return true only if this proxy has been resolved to its referent.
    return cls in _ref_proxy_to_resolved_hint

# ....................{ PRIVATE ~ (un|)cachers             }....................
#FIXME: Unit test us up, please.
def _cache_ref_proxy_referent(
    cls: _BeartypeForwardRefABC, referent: Hint) -> None:
    '''
    Associate the passed **forward reference proxy** (i.e.,
    :class:`._BeartypeForwardRefABC` object) with the passed **target referent**
    (i.e., externally declared type hint referred to by this source reference).

    Parameters
    ----------
    cls : _BeartypeForwardRefABC
        Forward reference proxy to cache this referent against.
    referent : Hint
        Target referent type hint to be cached.
    '''
    assert isinstance(cls, BeartypeForwardRefMeta), (
        f'{repr(cls)} not beartype forward reference proxy.')

    # Cache this target referent against this source forward reference proxy.
    _ref_proxy_to_resolved_hint[cls] = referent


def _uncache_ref_proxy_referent(
    cls: _BeartypeForwardRefABC, referent: Hint) -> None:
    '''
    De-associate the passed **forward reference proxy** (i.e.,
    :class:`._BeartypeForwardRefABC` object) from the passed **target referent**
    (i.e., externally declared type hint referred to by this source reference).

    Parameters
    ----------
    cls : _BeartypeForwardRefABC
        Forward reference proxy to uncache this referent against.
    referent : Hint
        Target referent type hint to be uncached.
    '''
    assert isinstance(cls, BeartypeForwardRefMeta), (
        f'{repr(cls)} not beartype forward reference proxy.')

    # Uncache this target referent against this source forward reference proxy.
    del _ref_proxy_to_resolved_hint[cls]

# ....................{ PRIVATE ~ factories                }....................
#FIXME: Unit test us up, please. *sigh*
def _make_ref_proxy_exception_prefix(cls: _BeartypeForwardRefABC) -> str:
    '''
    Human-readable substring intended to prefix exception messages raised when
    the passed **forward reference proxy** (i.e.,
    :class:`.BeartypeForwardRefMeta` instance) fails to dynamically resolve the
    source forward reference this proxy encapsulates to its target referent.

    Caveats
    -------
    **This factory function is computationally expensive and thus intended to be
    called only when an exception is guaranteed to be raised.**

    Parameters
    ----------
    cls : _BeartypeForwardRefABC
        Forward reference proxy to be resolved.

    Returns
    -------
    str
        Human-readable substring as detailed above.
    '''
    assert isinstance(cls, BeartypeForwardRefMeta), (
        f'{repr(cls)} not beartype forward reference proxy.')

    # Human-readable substring to prefix raised exception messages with.
    exception_prefix = cls.__exception_prefix_beartype__

    # If this reference thinly wraps a PEP 749-compliant object-oriented forward
    # reference, define this substring in a PEP 749-specific manner.
    if cls.__hint_pep749_ref_beartype__:
        exception_prefix += 'PEP 649 unquoted forward reference type hint "'  # pyright: ignore
    # Else, this reference does *NOT* thinly wrap a PEP 749-compliant
    # object-oriented forward reference (i.e., "annotationlib.ForwardRef"
    # object). By elimination, this reference *MUST* thickly wrap a
    # PEP 484-compliant stringified forward reference. In this case...
    else:
        exception_prefix += (  # pyright: ignore
            'PEP 484 stringified forward reference type hint "')

    # PEP 484-compliant stringified forward reference type hint reconstituted
    # from its constituent substrings encapsulated by this proxy.
    #
    # Note that:
    # * The "cls.__scope_name_beartype__" class variable is guaranteed to be a
    #   non-empty string *ONLY* for PEP 484-compliant stringified forward
    #   reference type hints. Ergo, we make no assumptions of its existence.
    # * PEP 749-compliant unquoted forward reference type hints literally do
    #   *NOT* exist at runtime. Ergo, this hint *MUST* be reconstituted when
    #   this proxy encapsulates such a hint.
    if cls.__scope_name_beartype__:
        exception_prefix += f'{cls.__scope_name_beartype__}.'
    exception_prefix += (
        f'{cls.__hint_name_beartype__}" '
        f'unresolvable to its target referent, as '
    )

    # Return this prefix.
    return exception_prefix

# ....................{ PRIVATE ~ uncachers                }....................

# ....................{ PRIVATE ~ resolvers                }....................
#FIXME: Unit test us up, please. *sigh*
def _resolve_hint_pep484_ref_str(cls: _BeartypeForwardRefABC) -> Hint:
    '''
    Resolve the :pep:`484`-compliant **stringified forward reference type
    hint** (i.e., string referring to a referent target type hint that typically
    has yet to be defined in the current lexical scope) encapsulated by the
    passed **forward reference proxy subclass** (i.e.,
    :class:`.BeartypeForwardRefMeta` instance) to that referent.

    This resolver is intentionally *not* memoized (e.g., by the
    ``@callable_cached`` decorator). Resolving both absolute *and* relative
    forward references assumes contextual context (e.g., the fully-qualified
    name of the object to which relative forward references are relative to)
    that *cannot* be safely and context-freely memoized away.

    Parameters
    ----------
    cls : _BeartypeForwardRefABC
        Forward reference proxy subclass to be resolved.

    Returns
    -------
    Hint
        Non-string type hint to which this reference refers.

    Raises
    ------
    exception_cls
        If attempting to dynamically evaluate this reference raises an
        exception, typically due to this reference being syntactically invalid
        as Python.
    '''
    assert isinstance(cls, BeartypeForwardRefMeta), (
        f'{repr(cls)} not beartype forward reference proxy.')
    # print(f'Importing ref "{cls.__hint_name_beartype__}" from module "{cls.__scope_name_beartype__}"...')

    # Forward referent dynamically imported from this module if this module is
    # both importable and defines this referent *OR* the sentinel placeholder
    # (i.e., if this module is unimportable or fails to define this referent).
    referent = import_module_attr_or_sentinel(
        attr_name=cls.__hint_name_beartype__,  # pyright: ignore
        module_name=cls.__scope_name_beartype__,  # pyright: ignore
        exception_cls=BeartypeCallHintPep484ForwardRefStrException,
        # Delay calling the preferable (yet expensive)
        # _make_ref_proxy_exception_prefix(cls) function until required below.
        exception_prefix=cls.__exception_prefix_beartype__,  # pyright: ignore
    )

    # If this module is unimportable *OR* fails to define this referent...
    if referent is SENTINEL:
        # If this proxy does *NOT* proxy a PEP 484-compliant stringified forward
        # reference type hint annotating a locally decorated callable...
        #
        # See the "__func_local_parent_codeobj_weakref_beartype__" docstring for
        # further details.
        if cls.__func_local_parent_codeobj_weakref_beartype__ is None:
            # Raise a human-readable exception describing this failure by
            # instead deferring to the mandatory variant of the import function
            # called above.
            import_module_attr(
                attr_name=cls.__hint_name_beartype__,  # pyright: ignore
                module_name=cls.__scope_name_beartype__,  # pyright: ignore
                exception_cls=BeartypeCallHintPep484ForwardRefStrException,
                exception_prefix=_make_ref_proxy_exception_prefix(cls),
            )

            # Validate sanity by ensuring that the prior call raised the
            # expected exception.
            assert False  # pragma: no cover
        # Else, this proxy proxies a PEP 484-compliant stringified forward
        # reference type hint annotating a locally decorated callable. In this
        # case, avoid emitting false positives.

        #FIXME: *NON-IDEAL*. Ideally, we would now disambiguate between
        #the two edge cases documented by the
        #"__func_local_parent_codeobj_weakref_beartype__" docstring.
        #However, doing so (probably) requires us to implement some new
        #functionality we don't currently have and is thus somewhat
        #non-trivial. For the moment, avoid doing so until somebody
        #strenuously complains about this. *lol* -> *sigh*
        #
        #Specifically, we want to do this:
        #* Introspect up the call stack for the first stack frame whose
        #  code object is the same code object weakly referred to by
        #  this "__func_local_parent_codeobj_weakref_beartype__" class
        #  variable.
        #* Dynamically resolving this reference against the global and
        #  local scope of that stack frame.
        #* If this reference remains unresolvable at that point,
        #  fallback to silently ignoring this reference as we do below.

        # Indirectly notify the beartype-specific parent
        # __is_instance_beartype__() and __is_subclass_beartype__() dunder
        # methods called by the beartype-agnostic parent parent
        # __instancecheck__() and __subclasscheck__() dunder methods this
        # reference *CANNOT* be resolved to its referent. How? By pretending to
        # resolve this reference to an arbitrary private type isolated to the
        # beartype codebase. This type is private and thus guaranteed to *NEVER*
        # be ambiguously used as a type hint referred to by stringified forward
        # references in third-party packages.
        #
        # Pretending to resolve this reference to this type is a crude
        # unreadable alternative to internally setting a hypothetical
        # "__is_type_unresolved_beartype__" class variable defined on the
        # "BeartypeForwardRefABC" type. Although more readable and thus
        # superficially preferable, the latter approach also requires defining
        # yet another class variable consuming corresponding space merely to
        # facilitate communication between this parent metaclass and its child
        # classes. Space efficiency takes precedence over code readability.
        #
        # This private type has been intentionally selected so as to minimize
        # unexpected issues in the unlikely event of Murphy and Her Dumb Law.
        # Since "BeartypeAny" is semantically analogous to the ignorable root
        # "object" superclass, resolving to "BeartypeAny" here implies that
        # erroneously implemented __is_instance_beartype__() and
        # __is_subclass_beartype__() dunder methods would fallback to silently
        # ignoring the passed objects without complaint.
        referent = BeartypeAny
    # Else, this module is both importable and defines this referent.

    # Return this referent.
    return referent
