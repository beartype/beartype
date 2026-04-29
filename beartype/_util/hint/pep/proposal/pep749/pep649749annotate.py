#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`649`- and :pep:`749`-compliant **annotations** (i.e.,
``__annotation__`` dunder dictionaries under Python >= 3.14 dynamically created
by ``__annotate__()`` dunder methods, mapping from the names of annotated child
objects of parent hintables to the type hints annotating those child objects).

This private submodule is *not* intended for importation by downstream callers.
'''
# ....................{ TODO                               }....................
#FIXME: Also, don't neglect to *IMMEDIATELY* excise the
#@method_cached_arg_by_id decorator. Quite a facepalm there, folks.

# ....................{ IMPORTS                            }....................
from beartype.roar import (
    BeartypeDecorHintPep649Exception,
    BeartypeDecorHintPep749ForwardRefObjectException,
)
from beartype._cave._cavefast import HintPep749RefFormat  # type: ignore[attr-defined]
from beartype._data.kind.datakindiota import (
    SENTINEL,
    Iota,
)
from beartype._data.typing.datatyping import (
    Pep649749Hintable,
    Pep649749HintableAnnotations,
    TypeException,
)
from beartype._data.typing.datatypingport import Hint
from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_14
from beartype._util.text.utiltextlabel import (
    label_exception_traceback,
    label_object,
)
from typing import (
    Optional,
    Union,
)

# ....................{ HINTS                              }....................
HintOrPep649749HintableAnnotationsOrSentinel = Union[
    Pep649749HintableAnnotations, Iota, Hint]
'''
:pep:`649`- and :pep:`749`-compliant type hint matching either the placeholder
sentinel, any PEP-compliant hint, *or* **hintable annotations** (i.e.,
``__annotations__`` dunder dictionary mapping from the name of each annotated
parameter or return of a callable *or* annotated variable of a class or module
to the type hint annotating that parameter, return, or variable).
'''

# ....................{ GETTERS                            }....................
#FIXME: Unit test us up, please.
def get_hintable_pep649749_annotations(
    # Mandatory parameters.
    hintable: Pep649749Hintable,

    # Optional parameters.
    hint_format: HintPep749RefFormat = HintPep749RefFormat.FORWARDREF,
    exception_cls: TypeException = BeartypeDecorHintPep649Exception,
    exception_prefix: str = '',
) -> Pep649749HintableAnnotations:
    '''
    **Immutable memoized annotations** (i.e., :class:`.FrozenDict` instance
    encapsulating the possibly empty ``__annotations__`` dunder dictionary
    mapping from the name of each annotated child object of the passed hintable
    to the type hint annotating that child object) annotating the passed
    **hintable** (i.e., ideally pure-Python object defining the
    ``__annotations__`` dunder dictionary as well as the :pep:`649`-compliant
    ``__annotate__()`` dunder method if the active Python interpreter targets
    Python >= 3.14) if this hintable defines the ``__annotations__`` dunder
    dictionary *or* raise an exception otherwise (i.e., if this hintable fails
    to define the ``__annotations__`` dunder dictionary).

    This getter is memoized for efficiency, guaranteeing amortized worst-case
    :math:`O(1)` constant time complexity. The first call to this getter passed
    a new hintable annotated by one or more type hints containing :math:`n`
    unquoted forward references exhibits non-amortized worst-case :math:`O(n)`
    linear time complexity, justifying the memoization of this getter.

    Parameters
    ----------
    hintable : Pep649749Hintable
        Hintable to be inspected.
    hint_format : HintPep749RefFormat, default: HintPep749RefFormat.FORWARDREF
        HintPep749RefFormat of annotated hints to be returned. Defaults to
        :attr:`HintPep749RefFormat.FORWARDREF`, in which case this getter safely
        encapsulates each otherwise unsafe unquoted forward reference
        transitively subscripting each hint annotating this hintable with a safe
        :class:`annotationlib.ForwardRef` object. Note that the remaining
        formats are situational at best. Specifically:

        * The :attr:`HintPep749RefFormat.VALUE` format is useful *only* to
          detect whether this hintable is annotated by one or more unquoted
          forward references or not. These hintables occasionally require
          special-case handling elsewhere, which this format facilitates.
          Notably, if this hintable is annotated by one or more unquoted forward
          references, this getter raises a :exc:`NameError` exception when
          passed this format.
        * The :attr:`HintPep749RefFormat.STRING` format is useful mostly just
          for documentation purposes. A tangential use case does *occasionally*
          arise, though: comparing annotations dictionaries of two hintables
          annotated by one or more unquoted forward references such that one of
          those dictionaries was postponed under :pep:`563` (i.e., ``from
          __future__ import annotations``). These dictionaries are comparable
          under this format but *not* the default
          :attr:`HintPep749RefFormat.FORWARDREF` format. Why? **Forward
          reference proxies** (i.e., :class:`annotationlib.ForwardRef` objects).
          Whereas :attr:`HintPep749RefFormat.FORWARDREF` injects incomparable
          forward reference proxies into these dictionaries that effectively
          prohibit dictionary comparisons, this format just preserves unquoted
          forward references in the strings it returns.
    exception_cls : TypeException, default: BeartypeDecorHintPep649Exception
        Type of exception to be raised in the event of a fatal error. Defaults
        to :exc:`.BeartypeDecorHintPep649Exception`.
    exception_prefix : str, default: ''
        Human-readable substring prefixing raised exception messages. Defaults
        to the empty string.

    Returns
    -------
    Pep649749HintableAnnotations
        ``__annotations__`` dunder dictionary set on this hintable.

    Raises
    ------
    exception_cls
         If this hintable fails to define the ``__annotations__`` dunder
         dictionary. Since *all* pure-Python hintables (including unannotated
         hintables) define this dictionary, this getter raises an exception only
         if the passed hintable is either:

         * *Not* actually a hintable.
         * A **pseudo-callable object** (i.e., otherwise uncallable object whose
           class renders all instances of that class callable by defining the
           ``__call__()`` dunder method).
    '''

    # "__annotations__" dictionary dictionary defined by this hintable if this
    # hintable is actually a hintable *OR* "None" otherwise.
    hint_annotations = get_hintable_pep649749_annotations_or_none(
        hintable=hintable,
        hint_format=hint_format,
        exception_cls=exception_cls,
        exception_prefix=exception_prefix,
    )

    # If this hintable is *NOT* actually a hintable, raise an exception.
    if hint_annotations is None:
        assert isinstance(exception_cls, type), (
            f'{repr(exception_cls)} not class.')
        assert issubclass(exception_cls, Exception), (
            f'{repr(exception_cls)} not exception subclass.')
        assert isinstance(exception_prefix, str), (
            f'{repr(exception_prefix)} not string.')

        # Raise a human-readable exception.
        raise exception_cls(
            f'{exception_prefix}{label_object(hintable)} '
            f'not annotatable by type hints '
            f'(i.e., PEP 649 "__annotate__" and "__annotations__" '
            f'dunder attributes undefined).'
        )
    # Else, that hintable is a hintable.

    # Return this dictionary.
    return hint_annotations

# ....................{ GETTERS ~ hint(s)                  }....................
def get_hintable_pep649749_annotations_format_value_or_none(
    # Mandatory parameters.
    hintable: Pep649749Hintable,

    # Optional parameters.
    exception_cls: TypeException = (
        BeartypeDecorHintPep749ForwardRefObjectException),
    exception_prefix: str = '',
) -> Optional[Pep649749HintableAnnotations]:
    '''
    **Value-formatted annotation(s)** (i.e., :pep:`484`-compliant
    ``__annotations__`` dunder dictionary mapping mapping from the name of each
    annotated attribute of the passed hintable to the type hint annotating that
    attribute in the non-default :attr:`.HintPep749RefFormat.VALUE` format)
    annotating the passed **hintable** (i.e., ideally pure-Python object
    defining that dictionary as well as the :pep:`649`-compliant
    ``__annotate__`` dunder method if the active Python interpreter targets
    Python >= 3.14) if this hintable defines that dictionary *or* :data:`None`
    otherwise (i.e., if this hintable fails to define that dictionary).

    Parameters
    ----------
    hintable : Union[Hint, Pep649749Hintable]
        Hintable to be inspected.
    exception_cls : TypeException, default: BeartypeDecorHintPep749ForwardRefObjectException
        Type of exception to be raised in the event of a fatal error. Defaults
        to :exc:`.BeartypeDecorHintPep749ForwardRefObjectException`.
    exception_prefix : str, default: ''
        Human-readable substring prefixing raised exception messages. Defaults
        to the empty string.

    Returns
    -------
    Optional[HintOrPep649749HintableAnnotations]
        Value of the ``__annotations__`` dunder attribute bound to this
        hintable, which should ideally be either:

        * Non-empty dictionary of type hints in the non-default
          :attr:`.HintPep749RefFormat.VALUE` format.
        * :data:`None`.

    See Also
    --------
    :func:`.get_hintable_pep649749_hint_or_hints_format_value_or_sentinel`
        Further details.
    '''

    # "__annotations__" dunder dictionary defined on this hintable if any *OR*
    # the sentinel placeholder otherwise.
    hintable_annotations = (
        get_hintable_pep649749_hint_or_hints_format_value_or_sentinel(
            hintable=hintable,
            attribute_name='__annotations__',
            exception_cls=exception_cls,
            exception_prefix=exception_prefix,
        ))

    # Return either this dictionary if *NOT* the sentinel or "None" otherwise.
    return (
        hintable_annotations if hintable_annotations is not SENTINEL else None)  # type: ignore[return-value]


def get_hintable_pep649749_hint_or_hints_format_value_or_sentinel(
    # Mandatory parameters.
    hintable: Union[Hint, Pep649749Hintable],
    attribute_name: str,

    # Optional parameters.
    exception_cls: TypeException = (
        BeartypeDecorHintPep749ForwardRefObjectException),
    exception_prefix: str = '',
) -> HintOrPep649749HintableAnnotationsOrSentinel:
    '''
    **Value-formatted annotation(s)** (i.e., either :pep:`792`-compliant dunder
    attribute whose value is a deferred annotation *or* :pep:`484`-compliant
    ``__annotations__`` dunder dictionary mapping mapping from the name of each
    annotated attribute of the passed hintable to the type hint annotating that
    attribute in the non-default :attr:`.HintPep749RefFormat.VALUE` format)
    annotating the passed **hintable** (i.e., ideally pure-Python object
    defining that attribute as well as the :pep:`649`-compliant ``__annotate__``
    dunder method if the active Python interpreter targets Python >= 3.14) if
    this hintable defines that attribute *or* :data:`None` otherwise (i.e., if
    this hintable fails to define that attribute).

    This getter provides a safe alternative to attempting to directly access
    this attribute on this hintable (e.g., ``hintable.__annotations__``), whose
    existence is no longer guaranteed under :pep:`649` and :pep:`749`.

    Caveats
    -------
    **This getter should always be called in lieu of attempting to "safely"
    access the contents of the** ``__annotations__`` dunder dictionary (e.g.,
    via ``getattr(hintable, '__annotations__', None)``). Safely accessing the
    contents of the ``__annotations__`` dunder dictionary succeeds in common use
    cases while erroneously failing with :data:`None` rather than raising
    human-readable exceptions when the passed hintable is annotated by one or
    more :pep:`649`-compliant **invalid unquoted forward references** (i.e.,
    whose direct access raises an unexpected :pep:`649`-noncompliant
    :exc:`AttributeError` exception despite that ``__annotations__`` dunder
    dictionary actually existing as a valid attribute of this hintable).

    For example, "safely" accessing the ``__annotations__`` dunder dictionary on
    this function erroneously fails with :data:`None` rather than raising a
    non-standard :exc:`AttributeError` exception as desired:

    .. code-block:: python

       # Import boring machinery. It is boring.
       import redis
       redis = redis.Redis(host="0.0.0.0", port=6379, db=0)

       # Function erroneously annotated by a PEP 649-compliant invalid
       # unquoted forward reference.
       def read_dis(an_weep: redis.Redis) -> None: pass

       # *THIS IS AWFUL*.
       print('"Safe" __annotations__:')
       print(getattr(read_dis, '__annotations__', None))
       print()

       # This is better, although still awful.
       print('Unsafe __annotations__:')
       print(read_dis.__annotations__)

    ...which prints::

       Safe" __annotations__:
       None

       Unsafe __annotations__:
       Traceback (most recent call last):
         File "/home/leycec/tmp/mopy.py", line 17, in <module>
           print(read_dis.__annotations__)
                 ^^^^^^^^^^^^^^^^^^^^^^^^
         File "/home/leycec/tmp/mopy.py", line 9, in __annotate__
           def read_dis(an_weep: redis.Redis) -> None: pass
                      ^^^^^^^^^^^
       AttributeError: 'Redis' object has no attribute 'Redis'

    In other words, the "safe" approach to accessing the contents of the
    ``__annotations__`` dunder dictionary is actually the least safe! Because
    this is highly non-intuitive, callers should *always* call this getter
    rather than attempting to reinvent the illogical wheel manually.

    Parameters
    ----------
    hintable : Union[Hint, Pep649749Hintable]
        Hintable to be inspected.
    attribute_name : str
        Unqualified basename of the attribute to introspect on this hintable.
    exception_cls : TypeException, default: BeartypeDecorHintPep749ForwardRefObjectException
        Type of exception to be raised in the event of a fatal error. Defaults
        to :exc:`.BeartypeDecorHintPep749ForwardRefObjectException`.
    exception_prefix : str, default: ''
        Human-readable substring prefixing raised exception messages. Defaults
        to the empty string.

    Returns
    -------
    Optional[HintOrPep649749HintableAnnotations]
        Value of the ``__annotations__`` dunder attribute bound to this
        hintable, which should ideally be either:

        * Non-empty dictionary of type hints in the non-default
          :attr:`.HintPep749RefFormat.VALUE` format.
        * :data:`None`.

    Raises
    ------
    NameError
        If this hintable is annotated by one or more type hints transitively
        subscripted by one or more :pep:`649`-compliant unquoted forward
        references.
    exception_cls
        If this hintable is annotated by one or more type hints transitively
        subscripted by one or more unquoted forward references.

    See Also
    --------
    https://github.com/beartype/beartype/issues/527#issuecomment-4001362638
        Real-world issue resolved by this getter, also inspiring the
        minimal-reproducible :mod:`redis` example above.
    '''
    assert isinstance(attribute_name, str), (
        f'{repr(attribute_name)} not string.')

    # Attempt to directly return the contents of the "__annotations__" dunder
    # attribute bound to this hintable in the non-default "VALUE" format if this
    # hintable both defines that attribute *AND* is annotated by no PEP
    # 649-compliant unquoted forward references.
    #
    # Note that this branch implicitly handles two edge cases:
    # * The "hintable.__annotations__" dunder attribute exists and has been
    #   implicitly set to a dictionary by the hintable.__annotate__() dunder
    #   method. This is PEP 649-compliant and the most common case.
    # * The "hintable.__annotations__" dunder attribute exists and has been
    #   explicitly set to "None" by an external caller. This is PEP
    #   649-compliant, surprisingly.
    # * The optional default is intentionally left undefined, ensuring correct
    #   propagation of *ANY* exception (including the standard PEP 749-compliant
    #   "AttributeError" exception) up the call stack.
    try:
        return getattr(hintable, attribute_name)
    # If directly accessing this attribute on this hintable raises the standard
    # "AttributeError" exception, we must now disambiguate between two cases:
    # * The "hintable.__annotations__" dunder attribute both does and should
    #   *NOT* exist, in which case attempting to access that attribute correctly
    #   raised the standard "AttributeError" exception. This is PEP
    #   649-compliant, too.
    # * The "hintable.__annotations__" dunder attribute *SHOULD* exist but
    #   doesn't, in which case attempting to access that attribute ambiguously
    #   and thus incorrectly raised the same "AttributeError" exception. This is
    #   *NOT* PEP 649-compliant. While an extreme outlier, this edge case
    #   actually occurred in real-world production
    #   code and *MUST* thus be handled. See the minimal-reproducible "redis"
    #   example in the docstring.
    except AttributeError as exception:
        # Message raised with this standard "AttributeError" exception.
        exception_message = str(exception)

        # If this message contains the substring "__annotations__", this is the
        # normal low-level message raised by the CPython interpreter on
        # erroneously attempting to access the "__annotations__" dunder
        # attribute on a non-hintable (i.e., object *NOT* defining that
        # attribute): e.g.,
        #     >>> 'A string is *NOT* a hintable.'.__annotations__
        #     AttributeError: 'str' object has no attribute
        #     '__annotations__'. Did you mean: '__contains__'?
        #
        # This common edge case is PEP 649-compliant. In this case, vaguely
        # mimic the expected behaviour of the simpler "getattr(hintable,
        # '__annotations__', None)" one-liner by returning the sentinel.
        #
        # Note that returning the "None" singleton would induce ambiguities with
        # PEP 749-compliant evaluate null values (which can be "None"). The
        # sentinel suffers no such issues and is thus returned instead.
        if attribute_name in exception_message:
            return SENTINEL
        # Else, this message does *NOT* contain the substring "__annotations__".
        # This is irregular. Something terrible again, didn't it!?!?

        # Human-readable traceback formatted from this exception, indented to
        # improve readability when embedded below.
        exception_traceback = label_exception_traceback(exception)

        # Raise a high-level human-readable exception wrapping this low-level
        # unreadable exception up the call stack as the only sane means of
        # notifying the user of... SOMETHING TERRIBLE.
        raise exception_cls(
            f'{exception_prefix}{label_object(hintable)} '
            f'annotated by '
            f'invalid PEP 749 unquoted forward reference type hint '
            f'referring to undefined attribute:\n'
            f'{exception_traceback}'
        ) from exception
    # If directly accessing this attribute on this hintable raises any other
    # exception (including the standard "NameError" exception raised if this
    # hintable is annotated by one or more unquoted forward references),
    # silently permit this exception to unwind back up the call stack.

# ....................{ VERSIONS                           }....................
# If the active Python interpreter targets Python >= 3.14...
if IS_PYTHON_AT_LEAST_3_14:
    # ....................{ IMPORTS                        }....................
    # Defer version-specific imports.
    from annotationlib import get_annotations  # type: ignore[import-not-found]
    from beartype._util.error.utilerrget import get_name_error_attr_name
    from beartype._util.cache.utilcacheobjattr import (
        ObjectAttrTypes,
        object_attr_cache_lock,
        get_object_attr_cached_or_sentinel,
        set_object_attr_cached,
    )

    # ....................{ GETTERS                        }....................
    #FIXME: Unit test us up, please.
    def get_hintable_pep649749_annotations_or_none(  # pyright: ignore
        # Mandatory parameters.
        hintable: Pep649749Hintable,

        # Optional parameters.
        hint_format: HintPep749RefFormat = HintPep749RefFormat.FORWARDREF,
        exception_cls: TypeException = BeartypeDecorHintPep649Exception,
        exception_prefix: str = '',
    ) -> Optional[Pep649749HintableAnnotations]:

        # ....................{ PEP 649                    }....................
        # If the caller requested the default "FORWARDREF" format...
        if hint_format is HintPep749RefFormat.FORWARDREF:
            # For efficiency, attempt to first assume that this hintable's
            # "__annotations__" dunder dictionary complies with the non-default
            # "VALUE" format (i.e., if this hintable is annotated by type hints
            # transitively subscripted by *NO* unquoted forward references).
            # Unquoted forward references are expected to be reasonably rare.
            # So, this is the common case and thus a helpful optimization goal.
            #
            # Note that the optional "exception_cls" parameter is intentionally
            # *NOT* passed to ensure that a granular exception type is raised.
            try:
                return (
                    get_hintable_pep649749_annotations_format_value_or_none(
                        hintable=hintable, exception_prefix=exception_prefix))
            # If this hintable's __annotate__() dunder method underlying its
            # "__annotations__" dunder dictionary raised a "NameError" exception
            # when passed the non-default "VALUE" format by CPython, this
            # hintable does *NOT* comply with the format and is thus annotated
            # by type hints transitively subscripted by one or more unquoted
            # forward references. In this case, fallback to support unquoted
            # forward references via full-blown memoized "FORWARDREF" handling.
            except NameError:
                # If this hintable is a pure-Python function, type, or module,
                # this hintable supports caching of arbitrary attributes. In
                # this case...
                if isinstance(hintable, ObjectAttrTypes):
                    # "__annotations__" dunder dictionary in the "FORWARDREF"
                    # format previously cached by a prior call to either this or
                    # the set_pep649749_hintable_annotations() function if any *OR*
                    # the sentinel placeholder otherwise.
                    hintable_annotations = get_object_attr_cached_or_sentinel(
                        obj=hintable,
                        attr_name_if_obj_function=(
                            _ANNOTATIONS_ATTR_NAME_IF_OBJ_FUNC),
                        attr_name_if_obj_type_or_module=(
                            _ANNOTATIONS_ATTR_NAME_IF_OBJ_TYPE_OR_MODULE),
                    )

                    # If such a dictionary was cached, return this dictionary.
                    if hintable_annotations is not SENTINEL:
                        # print(f'Returning hintable {hintable} annotations {hintable_annotations}...')
                        return hintable_annotations  # type: ignore[return-value]
                    # Else, *NO* such dictionary was cached. In this case...
                    else:
                        # print(f'Caching hintable {hintable} annotations...')

                        # Dictionary in this format.
                        #
                        # Note that this dictionary is guaranteed to both exist
                        # (i.e., be non-"None") and non-empty (i.e., contain one
                        # or more hints). Why? Because accessing the
                        # "__annotations__" dunder dictionary raised a
                        # "NameError" exception above, implying this dictionary
                        # to not only exist but contain one or more hints
                        # transitively subscripted by one or more unquoted
                        # forward references.
                        hintable_annotations = (
                            _get_hintable_pep649749_annotations_or_none_uncached(  # type: ignore[assignment]
                                hintable=hintable,
                                hint_format=hint_format,
                                exception_cls=exception_cls,
                                exception_prefix=exception_prefix,
                            ))

                        # Cache this dictionary with this hintable for efficient
                        # lookup by a subsequent call to this getter.
                        set_object_attr_cached(
                            obj=hintable,
                            attr_name_if_obj_function=(
                                _ANNOTATIONS_ATTR_NAME_IF_OBJ_FUNC),
                            attr_name_if_obj_type_or_module=(
                                _ANNOTATIONS_ATTR_NAME_IF_OBJ_TYPE_OR_MODULE),
                            attr_value=hintable_annotations,
                        )
                    # Else, such a dictionary was memoized.
                # Else, this hintable is neither a pure-Python function, type,
                # *NOR* module, implying this hintable to *NOT* support caching
                # of arbitrary attributes.
        # Else, the caller did *NOT* request the default "FORWARDREF" format.

        # ....................{ PEP 484                    }....................
        # If the caller requested the non-default "VALUE" format, trivially
        # return this hintable's existing "__annotations__" dunder dictionary.
        # If this is the first access of this dictionary, doing so implicitly:
        # 1. Invokes this hintable's __annotate__() dunder method with this same
        #    non-default "VALUE" format.
        # 2. Caches the returned "__annotations__" dunder dictionary inside this
        #    hintable. This getter avoids re-caching this dictionary.
        #
        # Note that the optional "exception_cls" parameter is intentionally
        # *NOT* passed to ensure that a granular exception type is raised.
        elif hint_format is HintPep749RefFormat.VALUE:
            return get_hintable_pep649749_annotations_format_value_or_none(
                hintable=hintable, exception_prefix=exception_prefix)
        # Else, the caller requested another non-default format (e.g.,
        # "STRING"). Since this format is so situational as to be functionally
        # useless for most intents and purposes, this getter avoids caching the
        # "__annotations__" dunder dictionary unique to this format altogether.

        # ....................{ FALLBACK                   }....................
        # Fallback to the unmemoized getter underlying this memoized getter.
        # Although non-ideal, the only general-purpose alternative would be to
        # memoize a reference to this object, preventing this object from *EVER*
        # being garbage-collected, inviting memory leaks. In other words, there
        # exist *NO* safe means of memoizing arbitrary user-defined objects.
        return _get_hintable_pep649749_annotations_or_none_uncached(
            hintable=hintable,
            hint_format=hint_format,
            exception_cls=exception_cls,
            exception_prefix=exception_prefix,
        )

    # ....................{ SETTERS                        }....................
    #FIXME: Detect and handle the (possibly common) edge case in which this
    #setter has already been passed this hintable at least once, in which case
    #this hintable's __annotate__() dunder method has *ALREADY* been replaced
    #with an __annotate_beartype__() monkey-patch. We *DEFINITELY* shouldn't
    #keep doing that ad nauseum. Instead, any existing __annotate_beartype__()
    #monkey-patch should be replaced inline *WITHOUT* deferring to
    #"hintable_annotate_old", which in this case will be that existing
    #__annotate_beartype__(). Basically, we just need to generalize this:
    #    hintable_annotate_old = getattr(hintable, '__annotate__', None)
    #
    #...to additionally check whether that hintable is already an
    #__annotate_beartype__() monkey-patch and, if so, defer to the *TRUE*
    #original __annotate__() dunder method. What's the catch? We don't currently
    #preserve the original __annotate__() dunder method in a @beartype-specific
    #dunder attribute on our __annotate_beartype__() monkey-patches. I suppose
    #we'll need to start doing that. The logic resembles:
    #    hintable_annotate_old = getattr(hintable, '__annotate__', None)
    #    hintable_annotate_old_wrappee = getattr(
    #        hintable_annotate_old, '__beartype_annotate_wrappee__', None)
    #    if hintable_annotate_old_wrappee is not None:
    #        hintable_annotate_old = hintable_annotate_old_wrappee
    #
    #Then we'll just need to monkey-patch the "__beartype_annotate_wrappee__"
    #attribute into our __annotate_beartype__() monkey-patch. *sigh*
    #FIXME: Oh. Right. The above is *BASICALLY* almost perfect, except that
    #there's no need for a @beartype-specific "__beartype_annotate_wrappee__"
    #monkey-patch. Instead, just use @functools.wraps(hintable_annotate_old) as
    #Guido intended. High fives all around, Team Bear! \o/

    #FIXME: Unit test us up, please.
    def set_pep649749_hintable_annotations(
        # Mandatory parameters.
        hintable: Pep649749Hintable,
        annotations: Pep649749HintableAnnotations,

        # Optional parameters.
        exception_cls: TypeException = BeartypeDecorHintPep649Exception,
        exception_prefix: str = '',
    ) -> None:
        assert isinstance(annotations, dict), (
            f'{repr(annotations)} not dictionary.')
        assert all(
            isinstance(annotations_key, str) for annotations_key in annotations
        ), f'{repr(annotations)} not dictionary mapping names to type hints.'
        # print(f'Setting hintable {hintable} annotations to {annotations}...')

        # ....................{ PREAMBLE                   }....................
        # Thread-safely...
        with object_attr_cache_lock:
            # ....................{ CACHE                  }....................
            # If this hintable is *NOT* actually a hintable, raise an exception.
            # Amusingly, the simplest means of implementing this validation is
            # to simply retrieve the existing "__annotations__" dunder
            # dictionary currently defined on this hintable.
            get_hintable_pep649749_annotations(
                hintable=hintable,
                exception_cls=exception_cls,
                exception_prefix=exception_prefix,
            )
            # Else, this hintable is actually a hintable defining the requisite
            # pair of PEP 649- and 749-compliant dunder attributes:
            # * __annotate__().
            # * "__annotations__".

            # If this hintable is a pure-Python function, type, or module, this
            # hintable supports caching of arbitrary attributes. In this case,
            # re-cache this dictionary onto this hintable to avoid
            # desynchronization with a prior "__annotations__" dunder dictionary
            # cached previously onto this hintable.
            if isinstance(hintable, ObjectAttrTypes):
                set_object_attr_cached(
                    obj=hintable,
                    attr_name_if_obj_function=(
                        _ANNOTATIONS_ATTR_NAME_IF_OBJ_FUNC),
                    attr_name_if_obj_type_or_module=(
                        _ANNOTATIONS_ATTR_NAME_IF_OBJ_TYPE_OR_MODULE),
                    attr_value=annotations,
                )
            # Else, this hintable is neither a pure-Python function, type, *NOR*
            # module and thus fails to support caching of arbitrary attributes.

            # ....................{ LOCALS                 }....................
            # Existing __annotate__() dunder method set on this hintable if any
            # *OR* "None" (e.g., if an external caller has already explicitly
            # set the "__annotations__" dunder attribute on this hintable, which
            # implicitly sets the __annotate__() dunder method to "None").
            hintable_annotate_old = getattr(hintable, '__annotate__', None)

            # Either:
            # * If this hintable is annotated by type hints transitively
            #   subscripted by one or more unquoted forward references, the
            #   "NameError" exception implicitly raised by attempting to access
            #   the existing "__annotations__" dunder dictionary set on this
            #   hintable cached according to the "VALUE" format.
            # * If this hintable is annotated by type hints transitively
            #   subscripted by *NO* unquoted forward references, "None".
            hintable_annotations_old_name_error: Optional[Exception] = None

            # Attempt to access the existing "__annotations__" dunder dictionary
            # previously cached with this hintable under the non-default "VALUE"
            # format if this hintable is annotated by type hints transitively
            # subscripted by no unquoted forward references *OR* implicitly
            # raise the "NameError" exception otherwise (i.e., if this hintable
            # is annotated by type hints transitively subscripted by one or more
            # unquoted forward references).
            try:
                hintable.__annotations__
            # If accessing this dictionary above raised a "NameError" exception,
            # this hintable is annotated by type hints transitively subscripted
            # by one or more unquoted forward references. Preserve this
            # exception for subsequent re-raising below.
            except NameError as exception:
                hintable_annotations_old_name_error = exception

            # ....................{ CLOSURE                }....................
            # Note that the docstring of this callable *CANNOT* be formatted as
            # an f-string dynamically embedding the passed hintable: e.g., 
            #     def __annotate_beartype__(
            #         hint_format: HintPep749RefFormat) -> (
            #             Pep649749HintableAnnotations):
            #         f'''
            #         Hintable {repr(hintable)} :pep:`649`- and :pep:`749`-compliant
            #         ...
            #         '''
            #
            # Why? Who knows, honestly. The above approach succeeds for the
            # standard "Format.VALUE" and "Format.FORWARDREF" formats while
            # inexplicably failing for the "Format.STRING" format with a
            # super-odd exception from the "annotationlib" module resembling:
            #     TypeError: Cannot stringify annotation containing string
            #     formatting
            #
            # In all likelihood, this is an outstanding bug in the
            # "annotationlib" module. Since there's little to nothing we can do
            # about that, we abide by this artificial constraint (and grumble).
            def __annotate_beartype__(
                hint_format: HintPep749RefFormat) -> (
                    Pep649749HintableAnnotations):
                '''
                :pep:`649`- and :pep:`749`-compliant ``__annotate__()`` dunder
                method that effectively monkey-patches the user-defined
                ``__annotations__`` dunder dictionary of the parent object with
                :mod:`beartype`-specific improvements.

                These improvements include:

                * **Memoization** (i.e., caching) across root type hints,
                  reducing space consumption.
                * :pep:`563`-compliant conversion of unquoted forward references
                  under the ``from __future__ import annotations`` pragma into
                  equivalent :mod:`beartype`-specific **forward reference
                  proxies** (i.e., objects proxying undefined types).

                This getter dunder method is intentionally given a
                :mod:`beartype`-specific name to aid in external debugging.

                Parameters
                ----------
                hint_format : HintPep749RefFormat
                    Kind of annotation format to be returned. See also
                    :pep:`649` and :pep:`749` for further details.

                Returns
                -------
                Pep649749HintableAnnotations
                    ``__annotations__`` dunder dictionary set on this hintable.
                '''

                #FIXME: Submit an upstream CPython issue about this. This
                #behaviour is super-weird, non-orthogonal, and invites extremely
                #subtle and non-trivial to debug issues in user code like this.
                #To resolve this, CPython devs should consider:
                #* Defining a new "_annotationlib" C extension.
                #* Moving the existing "annotationlib.HintPep749RefFormat" enum
                #  to this C extension.
                #* Adding to the top of "annotationlib":
                #      from _annotationlib import Format
                #* Refactoring the C-based CPython interpreter to pass the
                #  "_annotationlib.Format.VALUE" enum member rather than the
                #  magic integer constant "1" to __annotate__() dunder methods
                #  when creating the "__annotations__" dunder dictionary.
                #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                # CAUTION: CPython implicitly calls this monkey-patched dunder
                # function with magic integer constants (e.g., "1") rather than
                # readable enum members (e.g., "Format.FORWARDREF"). In other
                # words, *THIS FUNCTION MUST NOT ATTEMPT TO COMPARE THE PASSED
                # PARAMETER TO ENUM MEMBERS WITH THE "is" BUILTIN.* Doing so is
                # guaranteed to silently fail in non-debuggable ways with
                # sporadic false negatives or positives. We know. We were there.
                #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

                #FIXME: [SPEED] Globalize access to frequently accessed
                #"HintPep749RefFormat" members and reference those globals
                #instead below. This method *COULD* be frequently called enough
                #to warrant micro-optimization.

                # If the caller requested the default "FORWARDREF" format,
                # trivially return the "__annotations__" dunder dictionary
                # passed by the original earlier caller to the parent
                # set_pep649749_hintable_annotations() setter of this closure.
                #
                # If this dictionary contains:
                # * *NO* unquoted forward references, this dictionary already
                #   complies with the "VALUE" format. However, the "FORWARDREF"
                #   format simply reduces to "VALUE" if a dictionary contains
                #   *NO* unquoted forward references. Ergo, this dictionary also
                #   complies with the "FORWARDREF" format (which implements the
                #   superset of "VALUE").
                # * One or more unquoted forward references, this dictionary
                #   already complies with the default "FORWARDREF" format. Why?
                #   A complex and non-obvious chain of casuistry. Bear with us.
                #   If this dictionary did *NOT* already comply with the
                #   "FORWARDREF" format, then (by process of elimination)
                #   this dictionary *MUST* at least comply with the "VALUE"
                #   format. However, since this dictionary contains unquoted
                #   forward references, the annotationlib.get_annotations()
                #   getter would have raised a "NameError" exception when
                #   attempting to return this dictionary under the "VALUE"
                #   format, in which case this dictionary could *NOT* possibly
                #   exist. Clearly, however, this dictionary exists. Since this
                #   is an obvious contradiction, this dictionary *MUST*
                #   necessarily already comply with the "FORWARDREF" format.
                #
                # There now exist two possible cases:
                # * The caller passed "FORWARDREF" and this dictionary complies
                #   with the "FORWARDREF" format. *WONDERFUL*!
                # * The caller passed "FORWARDREF" and this dictionary only
                #   complies with the "VALUE" format, which implies this
                #   dictionary contains *NO* unquoted forward references. Since
                #   the "FORWARDREF" format simply reduces to "VALUE" if a
                #   dictionary contains *NO* unquoted forward references, this
                #   case is still wonderful. *WONDERFUL*!
                if hint_format == HintPep749RefFormat.FORWARDREF:  # <-- "==", *NOT* "is"!
                    return annotations
                # Else, the caller did *NOT* request the "FORWARDREF" format.
                #
                # If the caller requested the "VALUE" format...
                elif hint_format == HintPep749RefFormat.VALUE:  # <-- "==", *NOT* "is"!
                    # If attempting to access the existing "__annotations__"
                    # dunder dictionary set on this hintable cached according to
                    # the non-default "VALUE" format raised a "NameError"
                    # exception above, this hintable was annotated by type hints
                    # transitively subscripted by one or more unquoted forward
                    # references. In this case, re-raise the same exception to
                    # notify the caller of this critical fact.
                    if hintable_annotations_old_name_error is not None:
                        raise hintable_annotations_old_name_error
                    # Else, doing so did *NOT* raise a "NameError" exception,
                    # implying this hintable was annotated by type hints
                    # transitively subscripted by *NO* unquoted forward
                    # references, implying the old "__annotations__" dunder
                    # dictionary complies with the "HintPep749RefFormat.VALUE"
                    # format.

                    # Return the new "__annotations__" dunder dictionary. By
                    # definition, this dictionary exists and thus implicitly
                    # complies with the "HintPep749RefFormat.VALUE" format too.
                    return annotations
                # Else, the caller did *NOT* request the "VALUE" format.
                #
                # If the caller requested the "VALUE_WITH_FAKE_GLOBALS" format
                # private to the standard "annotationlib" module, raise a
                # standard "NotImplementedError" exception as explicitly
                # required by PEP 749 under this edge case:
                #       Users who manually write annotate functions should raise
                #       NotImplementedError if the VALUE_WITH_FAKE_GLOBALS
                #       format is requested, so the standard library will not
                #       call the manually written annotate function with “fake
                #       globals”, which could have unpredictable results.
                #
                # Note that this edge case must be explicitly handled *BEFORE*
                # deferring to an existing __annotate__() dunder method already
                # defined on this hintable. If defined, that method is outside
                # our explicit control and thus *CANNOT* be trusted to properly
                # handle this edge case. Indeed, @beartype previously trusted
                # that method to do so. For unknown reasons (that probably
                # reduce to a CPython bug), deferring to the default C-based
                # __annotate__() dunder methods defined on functions for this
                # edge case causes the standard
                # annotationlib.call_annotate_function() to raise the following
                # non-human-readable (and almost certainly incorrect) exception
                # when passed the "Format.STRING" format:
                #     ValueError: not enough values to unpack (expected 2, got 1)
                elif hint_format == HintPep749RefFormat.VALUE_WITH_FAKE_GLOBALS:
                    raise NotImplementedError()
                # Else, the caller did *NOT* request the
                # "VALUE_WITH_FAKE_GLOBALS" format.
                #
                # If this hintable already defined an existing __annotate__()
                # dunder method, defer to that method by...
                elif hintable_annotate_old is not None:
                    # print(f'Caller requested odd format {hint_format}...')

                    # New "__annotations__" dunder dictionary coerced to the
                    # passed format by that prior __annotate__() dunder method.
                    annotations_formatted = hintable_annotate_old(hint_format)
                    # print(f'Format {hint_format} annotations: {repr(annotations_formatted)}')

                    # Return this new "__annotations__" dunder dictionary.
                    return annotations_formatted
                # Else, *NO* existing __annotate__() dunder method was
                # previously defined on this hintable. This beartype-specific
                # implementation of that method *MUST* now either:
                # * Attempt to manually redefine this format. Although feasible,
                #   doing so would be non-trivial and undesirable. See above.
                # * Raise the builtin "NotImplementedError" exception. The
                #   caller is then expected to manually implement this format.
                #   Thankfully, the high-level call_annotate_function() and
                #   get_annotations() functions defined by the standard
                #   "annotationslib" module do just that; they explicitly catch
                #   this exception and respond by implementing the "STRING"
                #   format in the expected way. This is the only sane solution.
                #
                # Unsurprisingly, we opt for the latter approach by simply
                # falling through to the fallback defined below.

                # Notify the caller that this __annotate__() implementation
                # fails to support this format by raising a
                # "NotImplementedError" exception.
                #
                # Note that:
                # * PEP 649 itself encourages user-defined __annotate__()
                #   implementations to raise bare "NotImplementedError"
                #   exceptions lacking messages. Indeed, the
                #   standard call_annotate_function() and get_annotations()
                #   functions defined by the "annotationlib" module trivially
                #   catch these exceptions and ignore any associated messages.
                # * PEP 749 explicitly instructs user-defined __annotate__()
                #   implementations to raise "NotImplementedError" exceptions
                #   when passed the private ".VALUE_WITH_FAKE_GLOBALS" format:
                #       Users who manually write annotate functions should raise
                #       NotImplementedError if the VALUE_WITH_FAKE_GLOBALS
                #       format is requested, so the standard library will not
                #       call the manually written annotate function with “fake
                #       globals”, which could have unpredictable results.
                raise NotImplementedError()

            # ....................{ MONKEY-PATCH           }....................
            # Attempt to...
            try:
                # Silently replace this hintable's existing __annotate__()
                # dunder method with this new beartype-specific monkey-patch
                hintable.__annotate__ = __annotate_beartype__  # type: ignore[union-attr]
                # print(f'new annotations: {annotations}')
                # print(f'{hintable}.__annotate__: {hintable.__annotate__}')
                # print(f'{hintable}.__annotations__: {hintable.__annotations__}')
                # print(f'{hintable}.__annotate__(3): {hintable.__annotate__(HintPep749RefFormat.FORWARDREF)}')
                # hintable_annotations_cached = get_hintable_pep649749_annotations(hintable)
                # print(f'{hintable}.__annotate__(3) [cached]: {hintable_annotations_cached}')
            # If doing so fails with an exception resembling the following, this
            # hintable is *NOT* pure-Python. The canonical example are C-based
            # decorator objects (e.g., class, property, or static method
            # descriptors), whose exception message reads:
            #     AttributeError: 'method' object has no attribute
            #     '__annotate__' and no __dict__ for setting new attributes. Did
            #     you mean: '__getstate__'?
            #
            # C-based decorator objects only define:
            # * A read-only __annotate__() dunder method that proxies an
            #   original writeable __annotate__() dunder method of the
            #   pure-Python callables they originally decorated.
            # * A read-only "__annotations__" dunder attribute that proxies an
            #   original writeable "__annotations__" dunder attribute of the
            #   pure-Python callables they originally decorated.
            #
            # Detecting this edge case is non-trivial and most easily deferred
            # to this late time. While non-ideal, simplicity >>>> idealism here.
            except AttributeError as exception:
                # print(f'{hintable}.__annotate__() not settable: {repr(AttributeError)}')

                # Lower-level presumably pure-Python callable wrapped by this
                # higher-level presumably C-based decorator object if this
                # decorator object wraps such a callable *OR* "None" otherwise
                # (i.e., if this object does *NOT* wrap such a callable).
                #
                # Note that this callable is intentionally accessed as the
                # "__func__" dunder attribute on this decorator object, as the
                # following standard decorator objects *ALL* wrap their
                # decorated callables with this attribute:
                # * Bound instance method descriptors.
                # * @classmethod-decorated class method descriptors.
                # * @staticmethod-decorated static method descriptors.
                #
                # See also the "beartype._util.func.utilfuncwrap" submodule.
                hintable_func = getattr(hintable, '__func__', None)

                #FIXME: File an upstream CPython issue about this, please. *sigh*
                #FIXME: Remove this edge case *AFTER* some future Python version
                #fully satisfies PEP 749 by implementing this paragraph:
                #    The constructors for classmethod() and staticmethod() currently
                #    copy the __annotations__ attribute from the wrapped object to
                #    the wrapper. They will instead have writable attributes for
                #    __annotate__ and __annotations__. Reading these attributes will
                #    retrieve the corresponding attribute from the underlying
                #    callable and cache it in the wrapper’s __dict__. Writing to
                #    these attributes will directly update the __dict__, without
                #    affecting the wrapped callable.
                #
                #Currently, Python does *NOT* do that. Neither the __annotate__()
                #nor "__annotate__" dunder attributes are settable on @classmethod
                #or @staticmethod descriptors:
                #    class Yum(object):
                #        @classmethod
                #        def guh(cls) -> None: pass
                #
                #    def ugh_annotate(): return {}
                #
                #    yim = Yum()
                #    print(Yum.guh.__annotate__)          # <-- reading this works
                #    Yum.guh.__annotate__ = ugh_annotate  # <-- writing this fails
                #
                #The above example currently raises:
                #    AttributeError: 'method' object has no attribute '__annotate__'
                #    and no __dict__ for setting new attributes. Did you mean:
                #    '__getstate__'?
                #
                #Presumably, Python will start doing that at some point. Once Python
                #does, this issue becomes a non-issue. For the moment, efficiency is
                #irrelevant. We just need this to work for a temporary span of time.
                #FIXME: Once Python resolves this issue, also remove the
                #temporary "if IS_PYTHON_AT_MOST_3_13:" hack from our companion
                #test_resolve_pep563() unit test. *sigh*

                # If...
                if (
                    # This higher-level C-based decorator object wraps a
                    # lower-level pure-Python callable *AND*...
                    hintable_func is not None and
                    # This decorator object does *NOT* wrap itself...
                    #
                    # Note that:
                    # * This edge case should never occur. Indeed, if this
                    #   decorator object is one of the standard decorator
                    #   objects listed above, this edge case is guaranteed to
                    #   *NOT* occur.
                    # * This identity test is a Poor Man's Recursion Guard.
                    #   Clearly, this identity test does *NOT* actually
                    #   constitute a recursion guard. Implementing a "true"
                    #   recursion guard would require tracking a set of all
                    #   previously seen hintables across recursive calls. Since
                    #   it's unclear whether this edge
                    #   case will even arise in practice, it's unclear whether
                    #   the effort is worth investing in a "true" recursion
                    #   guard. The Poor Man's Recursion Guard suffices...
                    hintable_func is not hintable
                ):
                    # Set the "__annotations__" dunder dictionary on this
                    # lower-level pure-Python callable *BEFORE* setting the
                    # __annotate__() dunder method on this callable below. Why?
                    # Because CPython currently propagates *ONLY*
                    # "__annotations__" but not __annotate__() from this
                    # lower-level pure-Python callable on up to this
                    # higher-level C-based decorator object. Do so *BEFORE*
                    # setting __annotate__(), which implicitly nullifies
                    # "__annotations__". (Look. All of this is busted. I sigh.)
                    hintable_func.__annotations__ = annotations

                    # Set the __annotate__() dunder method on this lower-level
                    # pure-Python callable.
                    set_pep649749_hintable_annotations(
                        hintable=hintable_func,
                        annotations=annotations,
                        exception_cls=exception_cls,
                        exception_prefix=exception_prefix,
                    )
                # Else, either this higher-level presumably C-based decorator
                # object does not wrap a lower-level presumably pure-Python
                # callable *OR* this decorator object wraps itself. In either
                # case, unwrapping this decorator object would be harmful.
                # Unsurprisingly, avoid doing so.
                else:
                    # If the "__annotations__" dunder attribute of this hintable
                    # is *NOT* a dictionary, this dunder attribute has
                    # *PROBABLY* been nullified to "None", *PROBABLY* due to
                    # another decorator having previously set the __annotate__()
                    # dunder method of the presumably pure-Python callable
                    # underlying this C-based decorator object. Yes, there are a
                    # lot of assumptions *PROBABLY* happening here. The only
                    # remaining means of setting the passed annotations
                    # dictionary on this hintable would be to set the
                    # "__annotations__" dunder attribute to this dictionary.
                    # However, attempting to set the __annotate__() dunder
                    # method raised an "AttributeError"! Ergo, attempting to set
                    # the "__annotations__" dunder dictionary would almost
                    # certainly raise the same exception. Since there exist *NO*
                    # remaining means of setting the passed annotations
                    # dictionary on this hintable, we have *NO* recourse but to
                    # notify the caller of this modern tragedy by raising an
                    # exception.
                    if not isinstance(hintable.__annotations__, dict):
                        raise exception_cls(
                            f'{exception_prefix}{label_object(hintable)} '
                            f'type hints not settable to '
                            f'annotations dictionary {repr(annotations)} '
                            f'(i.e., PEP 649 "__annotate__" and "__annotations__" '
                            f'dunder attributes not settable, but "__annotations__" '
                            f'dunder attribute already set to '
                            f'non-dictionary value {repr(hintable.__annotations__)}).'
                        ) from exception
                    # Else, the "__annotations__" dunder attribute of this
                    # hintable is a dictionary.

                    # For the name of each annotated attribute of this hintable
                    # and the new hint which which to annotate this attribute,
                    # overwrite the prior hint originally annotating this
                    # attribute with this new hint.
                    #
                    # Note that:
                    # * The above assignment is an efficient O(1) operation and
                    #   thus intentionally performed first.
                    # * This iteration-based assignment is an inefficient O(n)
                    #   operation (for "n" the number of attributes annotated on
                    #   this hintable) and thus intentionally performed last.
                    # print('Doing suspicious stuff. *sigh*')
                    for attr_name, attr_hint in annotations.items():
                        hintable.__annotations__[attr_name] = attr_hint

    # ....................{ PRIVATE ~ globals : str        }....................
    _ANNOTATIONS_ATTR_NAME_IF_OBJ_FUNC = '__beartype_annotations'
    '''
    Unique name of the **memoized function annotations attribute** (i.e.,
    attribute cached for each pure-Python function passed to the
    :func:`beartype.beartype` decorator accepting one or more parameters and/or
    returns annotated by type hints whose attribute value is that function's
    **memoized annotations dictionary** (i.e., dictionary from the name of each
    such parameter or return to the type hint annotating that parameter or
    return as returned by the :func:`.get_hintable_pep649749_annotations_or_none`
    getter when passed that function)).
    '''


    _ANNOTATIONS_ATTR_NAME_IF_OBJ_TYPE_OR_MODULE = 'annotations'
    '''
    Unique name of the **memoized type or module annotations attribute** (i.e.,
    attribute cached for each pure-Python type or module passed to the
    :func:`beartype.beartype` decorator defining one or more class or global
    variables annotated by type hints whose attribute value is that type's or
    module's **memoized annotations dictionary** (i.e., dictionary from the name
    of each such variable to the type hint annotating that variable as returned
    by the :func:`.get_hintable_pep649749_annotations_or_none` getter when passed
    that type or module)).
    '''

    # ....................{ PRIVATE ~ getters              }....................
    def _get_hintable_pep649749_annotations_or_none_uncached(
        hintable: Pep649749Hintable,
        hint_format: HintPep749RefFormat,
        exception_cls: TypeException,
        exception_prefix: str,
    ) -> Optional[Pep649749HintableAnnotations]:
        '''
        **Formatted annotations** (i.e., ``__annotations__`` dunder dictionary
        mapping from the name of each annotated attribute of the passed hintable
        to the type hint annotating that attribute in the passed format)
        annotating the passed **hintable** (i.e., ideally pure-Python object
        defining the ``__annotations__`` dunder attribute as well as the
        :pep:`649`-compliant ``__annotate__`` dunder method if the active Python
        interpreter targets Python >= 3.14) if this hintable defines the
        ``__annotations__`` dunder dictionary *or* :data:`None` otherwise (i.e.,
        if this hintable fails to define the ``__annotations__`` dunder
        dictionary).

        This getter exhibits non-amortized worst-case :math:`O(n)` linear time
        complexity for :math:`n` the total number of unquoted forward references
        transitively subscripting all type hints annotating this hintable.

        Parameters
        ----------
        hintable : Pep649749Hintable
            Hintable to be inspected.
        hint_format : HintPep749RefFormat
            HintPep749RefFormat of annotated hints to be returned.
        exception_cls : TypeException
            Type of exception to be raised in the event of a fatal error.
        exception_prefix : str
            Human-readable substring prefixing raised exception messages.

        Returns
        -------
        Optional[Pep649749HintableAnnotations]
            Either:

            * If this hintable is actually a hintable, the ``__annotations__``
              dunder dictionary set on this hintable.
            * Else, :data:`None`.

        Raises
        ------
        exception_cls
            If:

            * This hintable is annotated by one or more type hints transitively
              subscripted by one or more unquoted forward references.
            * This hintable's __annotate__() dunder method has been nullified
              (i.e., previously set to :data:`None` and thus destroyed).
        '''

        # ....................{ LOCALS                     }....................
        # Annotations dictionary to be returned if this hintable is annotated
        # *OR* "None" otherwise (i.e., if this hintable is unannotated).
        hintable_annotations: Optional[Pep649749HintableAnnotations] = None

        # ....................{ FORMAT ~ forwardref        }....................
        # If this format requests that unquoted forward references be wrapped by
        # "annotationlib.ForwardRef" objects, do *NOT* unconditionally call the
        # annotationlib.get_annotations() getter. Why? Because that getter
        # raises unreadable exceptions when passed this format under various
        # common edge cases. Instead...
        if hint_format is HintPep749RefFormat.FORWARDREF:
            # ....................{ PEP 649                }....................
            # If this hintable defines the PEP 649-compliant __annotate__()
            # dunder method to be anything *OTHER* than "None", this hintable is
            # expected to be annotated by one or more type hints.
            #
            # Note that:
            # * The __annotate__() dunder method is guaranteed to exist *ONLY*
            #   for standard pure-Python hintables. Various other hintables of
            #   interest (e.g., functions exported by the standard "operator"
            #   module) do *NOT* necessarily declare this method. Since this
            #   getter is commonly called in general-purpose contexts where this
            #   guarantee does *NOT* necessarily hold, we intentionally access
            #   this attribute safely albeit somewhat more slowly via getattr().
            # * PEP 649 supports external nullification of the __annotate__()
            #   dunder method (i.e., by setting this dunder attribute to
            #   "None"). Indeed, PEP 649 explicitly requires nullification as a
            #   means of efficiently declaring a hintable to be unannotated:
            #       If an object has no annotations, __annotate__ should be
            #       initialized to None, rather than to a function that returns
            #       an empty dict.
            # * The __annotate__() dunder method and "__annotations__" dunder
            #   dictionary invalidate one another. Setting one nullifies the
            #   other:
            #       * Setting o.__annotate__ to a callable invalidates the
            #         cached annotations dict.
            #       * Setting o.__annotations__ to a legal value automatically
            #         sets o.__annotate__ to None.
            #   Thus, the __annotate__() dunder method being "None" does *NOT*
            #   imply this hintable to be unannotated. The "__annotations__"
            #   dunder attribute may be a non-"None" non-empty dictionary, in
            #   which case this hintable would be annotated. Where annotations
            #   are concerned, there are now multiple sources of objective
            #   truth. This is awful.
            # * The get_annotations() getter called below safely accepts the
            #   "FORWARDREF" format *ONLY* when this hintable defines the
            #   __annotate__() dunder method. If this hintable does *NOT* define
            #   __annotate__() and get_annotations() is passed "FORWARDREF",
            #   then get_annotations() raises either:
            #   * If this hintable at least defines the "__annotations__" dunder
            #     dictionary but this dictionary contains one or more unquoted
            #     forward references, a "NameError" exception.
            #   * Else, a "TypeError" exception.
            #
            #   However, this higher-level getter is designed exactly to avoid
            #   raising these sorts of exceptions! Ergo, get_annotations() is
            #   safely callable only when the __annotate__() dunder method
            #   exists.
            if getattr(hintable, '__annotate__', None) is not None:
                # Defer to the PEP 649-compliant high-level
                # annotationlib.get_annotations() getter internally deferring to
                # the PEP 649-compliant low-level __annotate__() dunder callable
                # rather than the PEP 484-compliant "__annotations__" dunder
                # attribute. Why? Because the latter reduces to calling
                # "get_annotations(hintable, format=HintPep749RefFormat.VALUE)",
                # which raises a "NameError" exception if the passed hintable is
                # annotated by one or more unquoted forward references. This is
                # unacceptable API design. Yet, this is Python >= 3.14.
                #
                # Note that:
                # * get_annotations() is guaranteed to *NEVER* return "None". If
                #   the __annotate__() dunder method and "__annotations__"
                #   dunder attribute are both "None", then get_annotations()
                #   raises a "TypeError" exception. However, get_annotations()
                #   is the canonical means of retrieving annotations under
                #   Python >= 3.14. Thus, we infer that at most one of but *NOT*
                #   both of __annotate__() and "__annotations__" may be "None".
                # * get_annotations() is guaranteed to *ALWAYS* return a new
                #   dictionary rather than the same value as that of the
                #   "__annotations__" dunder dictionary when the passed format
                #   is "FORWARDREF". This inefficiency is baked into
                #   get_annotations() and thus *CANNOT* be avoided.
                hintable_annotations = get_annotations(
                    hintable, format=hint_format)
                # print(f'Found hintable {hintable} annotations {hintable_annotations} in {hint_format}...')
            # Else, this hintable does *NOT* define __annotate__().

            # ....................{ PEP 484                }....................
            # Return either the PEP 484-compliant "__annotations__" dunder
            # dictionary if this hintable defines this dictionary *OR* "None"
            # (i.e., if this hintable fails to define this dictionary).
            #
            # Note that:
            # * The "__annotations__" dunder attribute is guaranteed to exist
            #   *ONLY* for standard pure-Python hintables. See above.
            # * The "__annotations__" dunder attribute is expected to either:
            #   * If this hintable actually is a hintable, be non-"None". Why?
            #     Because the __annotate__() dunder method was "None". By the
            #     logic given above, it should *NEVER* be the case that both
            #     __annotate__() and "__annotations__" are "None". However,
            #     __annotate__() was "None". It follows that "__annotations__"
            #     should now be non-"None" (and thus a valid dictionary).
            #   * Else, *NOT* exist. Ideally, unhintable objects should *NEVER*
            #     define the "__annotations__" dunder attribute.
            #
            #   Ergo, it follows that this getter returns "None" *ONLY* when
            #   this hintable is *NOT* actually a hintable. Sanity preserved!
            # * The "__annotations__" dunder attribute is *NOT* safely
            #   accessible under Python >= 3.14 in the worst case. If this
            #   dictionary contains one or more type hints subscripted by one or
            #   more unquoted forward references, then directly accessing this
            #   attribute is guaranteed to raise a non-human-readable
            #   "NameError" exception. Consequently, we perform this unsafe
            #   fallback *ONLY* when the __annotate__() dunder method does *NOT*
            #   exist. Although non-ideal, PEP 649 explicitly permits callers to
            #   set this attribute -- presumably as an unsafe means of
            #   preserving backward compatibility. That would be fine, except
            #   that setting this attribute nullifies and thus destroys any
            #   previously set __annotate__() dunder method! Again:
            #       * Setting o.__annotations__ to a legal value automatically
            #         sets o.__annotate__ to None.
            # * The "__annotations__" dunder dictionary and __annotate__()
            #   dunder method are strongly coupled. If one is defined, the other
            #   should be defined. If one is undefined, the other should be
            #   undefined. Ergo, it should *NEVER* be the case that the
            #   __annotate__() dunder method is undefined but the
            #   "__annotations__" dunder dictionary is defined. Ergo, this edge
            #   case should *NEVER* arise. Naturally, this edge case will often
            #   arise. Why? Because nothing prevents third-party packages from
            #   manually defining "__annotations__" dunder dictionaries on
            #   arbitrary objects. Although CPython *COULD* prohibit that (e.g.,
            #   by defining the "object.__annotations__" descriptor to do just
            #   that), CPython currently does *NOT* prohibit that. In fact, no
            #   "object.__annotations__" descriptor exists to even do so.
            else:
                # Attempt to fallback to the PEP 484-compliant "__annotations__"
                # dunder dictionary if this hintable defines this dictionary
                # *OR* "None" otherwise.
                #
                # Note that the optional "exception_cls" parameter is
                # intentionally *NOT* passed to ensure that a granular exception
                # type is raised.
                try:
                    hintable_annotations = (
                        get_hintable_pep649749_annotations_format_value_or_none(
                            hintable=hintable,
                            exception_prefix=exception_prefix,
                        ))
                # If accessing this dictionary raises an unreadable "NameError"
                # exception, this hintable is annotated by one or more type
                # hints transitively subscripted by one or more unquoted forward
                # references. However, this hintable's __annotate__() dunder
                # method has been nullified (i.e., previously set to "None" and
                # thus destroyed)! In this case, calling the get_annotations()
                # getter called above would simply re-raise the same:
                #     NameError: name 'UndefinedType' is not defined
                #
                # While uncommon, this edge case arises when some previously
                # applied obsolete PEP 649-noncompliant decorator unsafely set
                # the "__annotations__" dunder dictionary on this hintable,
                # which then implicitly nullified the __annotate__() dunder
                # method. Since this constitutes a fatal issue that the caller
                # should be informed about, raise a more readable exception.
                except NameError as exception:
                    # Name of the currently undefined attribute referred to be
                    # the first unquoted forward reference possibly deeply
                    # nested in the first hint annotating this hintable.
                    hint_ref_name = get_name_error_attr_name(exception)

                    # Raise an exception embedding this name.
                    raise exception_cls(
                        f'{exception_prefix}{label_object(hintable)} '
                        f'unsafely annotated by unresolvable type hints, as:\n'
                        f'* One or more type hints transitively subscripted by '
                        f'unquoted forward reference "{hint_ref_name}".\n'
                        f'* __annotate__() dunder method nullified '
                        f'(i.e., previously set to "None" and thus destroyed).\n'
                        f'{repr(hintable)} is presumably decorated by a '
                        f'PEP 649-noncompliant decorator unsafely setting the '
                        f'"__annotations__" dunder attribute, '
                        f'which no decorators should do under Python >= 3.14. '
                        f'Consider submitting an upstream issue report to '
                        f'the authors of that decorator. Politely request that '
                        f'they join the modern world and support PEP 649.'
                    ) from exception
        # ....................{ FORMAT ~ other             }....................
        # Else, this is any format *EXCEPT* the format requesting that unquoted
        # forward references be wrapped by "annotationlib.ForwardRef" objects.
        # In this case, unconditionally call the annotationlib.get_annotations()
        # getter; doing so does *NOT* raise unexpected exceptions and is thus
        # safely callable when passed this format.
        else:
            hintable_annotations = get_annotations(hintable, format=hint_format)

        # ....................{ RETURN                     }....................
        #FIXME: Actually, let's just return this mutable annotations dictionary
        #as is for the moment. Although non-ideal, this is mostly fine. Why?
        #Because when "hint_format" is the default
        #"HintPep749RefFormat.FORWARDREF" (which is the case for 99.99% of all
        #calls to this getter), this annotations dictionary is guaranteed to be
        #a copy of the underlying "__annotations__" dunder dictionary. Mutating
        #a copy is always fine. Of course, we then memoize this copy.
        #Ordinarily, mutating a memoized object would absolutely *NOT* be fine.
        #In this case, though, mutating this memoized object is actually ideal.
        #Why? Because then we only need to coerce hints once (e.g., via a call
        #to the coerce_func_hint_root() function), because the result of doing
        #so is then memoized. Look. Not even can I follow what I just wrote.

        # Return this annotations dictionary, coerced into an immutable frozen
        # dictionary for safety (e.g., to prevent accidental external mutation).
        # return FrozenDict(hintable_annotations)
        return hintable_annotations
# Else, the active Python interpreter targets Python <= 3.13. In this case,
# trivially defer to the PEP 484-compliant "__annotations__" dunder attribute.
else:
    # ....................{ GETTERS                        }....................
    def get_hintable_pep649749_annotations_or_none(  # type: ignore[misc]
        hintable: Pep649749Hintable, **kwargs) -> (
        Optional[Pep649749HintableAnnotations]):

        # Return either the PEP 484-compliant "__annotations__" dunder attribute
        # if the passed hintable defines this attribute *OR* "None" otherwise
        # (i.e., if this hintable fails to define this attribute).
        #
        # Note that the "__annotations__" dunder attribute is guaranteed to
        # exist *ONLY* for standard pure-Python hintables. Various other
        # hintables of interest (e.g., functions exported by the standard
        # "operator" module) do *NOT* necessarily declare this attribute. Since
        # this getter is commonly called in general-purpose contexts where this
        # guarantee does *NOT* necessarily hold, we intentionally access this
        # attribute safely albeit somewhat more slowly via getattr().
        return getattr(hintable, '__annotations__', None)

    # ....................{ SETTERS                        }....................
    def set_pep649749_hintable_annotations(
        # Mandatory parameters.
        hintable: Pep649749Hintable,
        annotations: Pep649749HintableAnnotations,

        # Optional parameters.
        exception_cls: TypeException = BeartypeDecorHintPep649Exception,
        exception_prefix: str = '',
    ) -> None:
        assert isinstance(annotations, dict), (
            f'{repr(annotations)} not dictionary.')
        assert all(
            isinstance(annotations_key, str) for annotations_key in annotations
        ), f'{repr(annotations)} not dictionary mapping names to type hints.'

        # If this hintable is *NOT* actually a hintable, raise an exception.
        # Amusingly, the simplest means of implementing this validation is to
        # simply retrieve the prior "__annotations__" dunder dictionary
        # currently set on this hintable.
        get_hintable_pep649749_annotations(
            hintable=hintable,
            exception_cls=exception_cls,
            exception_prefix=exception_prefix,
        )
        # Else, this hintable is actually a hintable.

        # Attempt to...
        try:
            # Atomically (i.e., all-at-once) replace this hintable's existing
            # "__annotations__" dunder dictionary with these new annotations. Do
            # so atomically for both safety and efficiency.
            hintable.__annotations__ = annotations
        # If doing so fails with an exception resembling the following, this
        # hintable is *NOT* pure-Python. The canonical example are C-based
        # decorator objects (e.g., class, property, or static method
        # descriptors), whose exception message reads:
        #     AttributeError: 'method' object has no attribute '__annotations__'
        #
        # C-based decorator objects define a read-only "__annotations__" dunder
        # attribute that proxies an original writeable "__annotations__" dunder
        # attribute of the pure-Python callables they originally decorated.
        # Detecting this edge case is non-trivial and most easily deferred to
        # this late time. While non-ideal, simplicity >>>> idealism here.
        except AttributeError:
            # For the name of each annotated attribute of this hintable and the
            # new hint which which to annotate this attribute, overwrite the
            # prior hint originally annotating this attribute with this new
            # hint.
            #
            # Note that:
            # * The above assignment is an efficient O(1) operation and thus
            #   intentionally performed first.
            # * This iteration-based assignment is an inefficient O(n) operation
            #   (where "n" is the number of annotated attributes of this
            #   hintable) and thus intentionally performed last here.
            for attr_name, attr_hint in annotations.items():
                hintable.__annotations__[attr_name] = attr_hint

# ....................{ VERSIONS ~ docs                    }....................
get_hintable_pep649749_annotations_or_none.__doc__ = (
    '''
    **Immutable memoized annotations** (i.e., :class:`.FrozenDict` instance
    encapsulating the possibly empty ``__annotations__`` dunder dictionary
    mapping from the name of each annotated child object of the passed hintable
    to the type hint annotating that child object) annotating the passed
    **hintable** (i.e., ideally pure-Python object defining the
    ``__annotations__`` dunder attribute as well as the :pep:`649`-compliant
    ``__annotate__`` dunder method if the active Python interpreter targets
    Python >= 3.14) if this hintable defines the ``__annotations__`` dunder
    dictionary *or* :data:`None` otherwise (i.e., if this hintable fails to
    define the ``__annotations__`` dunder dictionary).

    This getter is memoized for efficiency, guaranteeing amortized worst-case
    :math:`O(1)` constant time complexity. The first call to this getter passed
    a new hintable annotated by one or more type hints containing :math:`n`
    unquoted forward references exhibits non-amortized worst-case :math:`O(n)`
    linear time complexity, justifying the memoization of this getter.

    This getter is memoized *only* under Python >= 3.14. Why? Because the
    lower-level :func:`annotationlib.get_annotations` getter underlying this
    higher-level getter *only* memoizes the annotations dictionary it creates
    and returns when passed the ``format=HintPep749RefFormat.VALUE`` keyword
    parameter. When passed *any* other ``format`` value,
    :func:`annotationlib.get_annotations` avoids avoids caching its return
    value. Creating this return value is algorithmically non-trivial and
    expensive. Sadly, we are effectively required to memoize this return here.

    Parameters
    ----------
    hintable : Pep649749Hintable
        Hintable to be inspected.
    hint_format : HintPep749RefFormat, default: HintPep749RefFormat.FORWARDREF
        HintPep749RefFormat of annotated hints to be returned. Defaults to
        :attr:`HintPep749RefFormat.FORWARDREF`, in which case this getter safely
        encapsulates each otherwise unsafe unquoted forward reference
        transitively subscripting each hint annotating this hintable with a safe
        :class:`annotationlib.ForwardRef` object. See also the higher-level
        :func`.get_hintable_pep649749_annotations` getter for further details.
    exception_cls : TypeException, default: BeartypeDecorHintPep649Exception
        Type of exception to be raised in the event of a fatal error. Defaults
        to :exc:`.BeartypeDecorHintPep649Exception`.
    exception_prefix : str, default: ''
        Human-readable substring prefixing raised exception messages. Defaults
        to the empty string.

    Returns
    -------
    Optional[Pep649749HintableAnnotations]
        Either:

        * If this hintable is actually a hintable, the ``__annotations__``
          dunder dictionary set on this hintable.
        * Else, :data:`None`.
    '''
)
set_pep649749_hintable_annotations.__doc__ = (
    '''
    Set the **annotations** (i.e., ``__annotations__`` dunder dictionary mapping
    from the name of each annotated child object of the passed hintable to the
    type hint annotating that child object) annotating the passed **hintable**
    (i.e., ideally pure-Python object defining the ``__annotations__`` dunder
    attribute as well as the :pep:`649`-compliant ``__annotate__`` dunder method
    if the active Python interpreter targets Python >= 3.14) to the passed
    dictionary.

    Caveats
    -------
    **This setter preserves unmodified the existing**
    :attr:`HintPep749RefFormat.VALUE` **and** :attr:`HintPep749RefFormat.STRING`
    **formats of the** ``__annotations__`` **dunder dictionary of the passed
    hintable,** as originally created and returned by the original
    ``__annotate__`` dunder method bound to this hintable. This setter *only*
    modifies the :attr:`HintPep749RefFormat.FORWARDREF` format. Why? Because
    there exist two distinct cases, which although distinct imply the same
    conclusion:

    * When the caller of an ``__annotate__`` dunder method passes the
      :attr:`HintPep749RefFormat.VALUE` format, they expect that method to raise
      a :exc:`NameError` exception if the ``__annotations__`` dunder dictionary
      underlying that call contains one or more unquoted forward references.
      Indeed, this is the *only* efficient (and thus reasonable) means of
      detecting whether a hintable is annotated by unquoted forward references.
      This is also the only valid use case for passing the
      :attr:`HintPep749RefFormat.VALUE` format. Although this valid use case is
      of marginal utility, it is still of utility and *must* be preserved as
      such. But the passed ``annotations`` dictionary exists (rather than
      raising a :exc:`NameError` exception) and thus contains *no* unquoted
      forward references! Ergo, this ``annotations`` dictionary *cannot* be
      returned if the caller passes the :attr:`HintPep749RefFormat.VALUE`
      format. Doing so would destroy this format's only valid use case, which
      can only be preserved by deferring to the original ``__annotate__`` dunder
      method bound to this hintable.
    * When the caller of an ``__annotate__`` dunder method passes the
      :attr:`HintPep749RefFormat.STRING` format, they expect that method to
      return human- and machine-readable string representations of the
      *original* type hints annotating this hintable. These strings are expected
      to be readably concise and machine-comparable. These strings are, in
      particular, *not* expected to contain **forward reference proxies** (e.g.,
      either standard :class:`annotationlib.ForwardRef` objects or non-standard
      beartype-specific objects behaving similarly). Forward reference proxies
      typically have verbose string representations, confounding
      human-readability. They also do *not* necessarily compare equal to other
      objects, confounding machine-comparability. In short, the string
      representation of ``__annotations__`` dunder dictionaries should contain
      *no* forward reference proxies. However, the dictionaries passed to this
      setter often contain forward reference proxies! Ergo, this ``annotations``
      dictionary *cannot* be returned if the caller passes the
      :attr:`HintPep749RefFormat.STRING` format. Doing so would destroy this
      format's most common use cases, which can only be preserved by deferring
      to the original ``__annotate__`` dunder method bound to this hintable.

      More generally (and ignoring the above concerns about forward reference
      proxies), we can say that callers requesting documentation are ultimately
      requesting human-readable string representations of the *original* type
      hints annotating this hintable. Those type hints are what the third-party
      packages defining those hintables intended those hintables to be annotated
      as. Those type hints embody those intentions, thus constituting the most
      readable description of those hintables.

    **This setter replaces the original** ``__annotate__`` **dunder method bound
    to this hintable,** monkey-patching that method with a new ``__annotate__``
    dunder method that returns either:

    * If the caller passed the :attr:`HintPep749RefFormat.FORWARDREF` format,
      the ``annotations`` parameter passed to this higher-level setter.
    * Else (e.g., if the caller passed either the
      :attr:`HintPep749RefFormat.VALUE` or :attr:`HintPep749RefFormat.STRING`
      formats), the result of calling the original ``__annotate__`` dunder
      method bound to this hintable.

    Parameters
    ----------
    hintable : Pep649749Hintable
        Hintable to be inspected.
    annotations : Pep649749HintableAnnotations
        ``__annotations__`` dunder dictionary to set on this hintable.
    exception_cls : TypeException, default: BeartypeDecorHintPep649Exception
        Type of exception to be raised in the event of a fatal error. Defaults
        to :exc:`.BeartypeDecorHintPep649Exception`.
    exception_prefix : str, default: ''
        Human-readable substring prefixing raised exception messages. Defaults
        to the empty string.

    Raises
    ------
    exception_cls
         If this hintable fails to define the ``__annotations__`` dunder
         dictionary. Since *all* pure-Python hintables (including unannotated
         hintables) define this dictionary, this getter raises an exception only
         if the passed hintable is either:

         * *Not* actually a hintable.
         * A **pseudo-callable object** (i.e., otherwise uncallable object whose
           class renders all instances of that class callable by defining the
           ``__call__()`` dunder method).
    '''
)
