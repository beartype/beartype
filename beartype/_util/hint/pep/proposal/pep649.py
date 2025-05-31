#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`649`-compliant **annotations** (i.e., ``__annotation__``
dunder dictionaries dynamically created by ``__annotate__()`` dunder methods,
mapping from the names of annotated child objects of parent hintables to the
type hints annotating those child objects).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.roar._roarexc import BeartypeDecorHintPep649Exception
from beartype.typing import (
    Optional,
)
from beartype._data.hint.datahinttyping import (
    Pep649Hintable,
    Pep649HintableAnnotations,
    TypeException,
)
from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_14
from beartype._util.text.utiltextlabel import label_beartypeable_kind

# ....................{ GETTERS                            }....................
#FIXME: See "FIXME:" comments in the "beartype._check.metadata.metadecor"
#submodule for how this needs to be refactored to support Python >= 3.14. *sigh*
#FIXME: Unit test us up, please.
def get_pep649_hintable_annotations(
    # Mandatory parameters.
    hintable: Pep649Hintable,

    # Optional parameters.
    exception_cls: TypeException = BeartypeDecorHintPep649Exception,
    exception_prefix: str = '',
) -> Pep649HintableAnnotations:
    '''
    **Annotations** (i.e., possibly empty ``__annotations__`` dunder dictionary
    mapping from the name of each annotated child object of the passed hintable
    to the type hint annotating that child object) annotating the passed
    **hintable** (i.e., ideally pure-Python object defining the
    ``__annotations__`` dunder attribute as well as the :pep:`649`-compliant
    ``__annotate__`` dunder method if the active Python interpreter targets
    Python >= 3.14) if this hintable defines the ``__annotations__`` dunder
    dictionary *or* raise an exception otherwise (i.e., if this hintable fails
    to define the ``__annotations__`` dunder dictionary).

    Parameters
    ----------
    hintable : Pep649Hintable
        Hintable to be inspected.
    exception_cls : TypeException, default: BeartypeDecorHintPep649Exception
        Type of exception to be raised in the event of a fatal error. Defaults
        to :exc:`.BeartypeDecorHintPep649Exception`.
    exception_prefix : str, default: ''
        Human-readable substring prefixing raised exception messages. Defaults
        to the empty string.

    Returns
    -------
    Pep649HintableAnnotations
        ``__annotations__`` dunder dictionary defined by this hintable.

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
    hint_annotations = get_pep649_hintable_annotations_or_none(hintable)

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
            f'{exception_prefix}'
            f'{label_beartypeable_kind(hintable)} {repr(hintable)} '  # type: ignore[type-var]
            f'not annotatable by type hints '
            f'(i.e., fails to define "__annotations__" dunder dictionary).'
        )
    # Else, that hintable is a hintable.

    # Return this dictionary.
    return hint_annotations


# If the active Python interpreter targets Python >= 3.14...
if IS_PYTHON_AT_LEAST_3_14:
    # Defer version-specific imports.
    from annotationlib import (  # type: ignore[import-not-found]
        Format,
        get_annotations,
    )
    from beartype.typing import Dict
    from beartype._cave._cavefast import (
        CallableOrClassTypes,
        ModuleType,
    )
    from beartype._data.kind.datakindiota import SENTINEL
    from beartype._util.module.utilmodget import (
        get_module_name,
        get_object_module_name_or_none,
    )
    from beartype._util.utilobject import get_object_basename_scoped


    #FIXME: Unit test us up, please.
    def clear_pep649_caches() -> None:

        # Clear all dictionary globals declared below.
        _MODULE_NAME_TO_ANNOTATIONS.clear()
        _MODULE_NAME_TO_HINTABLE_BASENAME_TO_ANNOTATIONS.clear()


    #FIXME: Unit test us up, please.
    #FIXME: Also, don't neglect to *IMMEDIATELY* excise the
    #@method_cached_arg_by_id decorator. Quite a facepalm there, folks.
    # Note that this getter is memoized *ONLY* under Python >= 3.14. Why?
    # Because the get_annotations() getter *ONLY* memoizes the annotations
    # dictionary it creates and returns when passed the "format=Format.VALUE"
    # keyword parameter. When passed *ANY* other "format" value,
    # get_annotations() avoids avoids caching its return value. Creating this
    # return value is algorithmically non-trivial and computationally expensive.
    # So, we are effectively required to memoize this return value here.
    def get_pep649_hintable_annotations_or_none(
        hintable: Pep649Hintable) -> Optional[Pep649HintableAnnotations]:

        # If this hintable is either a callable *OR* class...
        #
        # Note that almost all hintables of interest are either callables or
        # classes. This common case is intentionally detected first for speed.
        if isinstance(hintable, CallableOrClassTypes):
            # Fully-qualified name of the module defining this hintable if any
            # *OR* "None" otherwise (e.g., if this hintable is defined in-memory
            # outside a module namespace).
            module_name = get_object_module_name_or_none(hintable)

            # If a module defines this hintable...
            if module_name:
                # Dictionary mapping from the lexically scoped name of each
                # hintable defined by this module previously memoized by a prior
                # call to this getter if any *OR* the sentinel otherwise (i.e.,
                # if this getter has yet to be passed such a hintable).
                hintable_basename_to_annotations = (
                    _MODULE_NAME_TO_HINTABLE_BASENAME_TO_ANNOTATIONS.get(
                        module_name, SENTINEL))

                # If such a dictionary was *NOT* memoized...
                if hintable_basename_to_annotations is SENTINEL:
                    # Default this dictionary to a new empty dictionary,
                    # additionally memoized into this global cache for speed.
                    hintable_basename_to_annotations = (
                        _MODULE_NAME_TO_HINTABLE_BASENAME_TO_ANNOTATIONS[
                            module_name]) = {}
                # Else, this dictionary was memoized.
                #
                # In either case, this dictionary now exists.

                # Lexically scoped name of this hintable excluding the
                # fully-qualified name of the module defining this hintable.
                hintable_basename = get_object_basename_scoped(hintable)

                # "__annotations__" dunder dictionary for this module previously
                # memoized by a prior call to this getter if any *OR* the
                # sentinel otherwise (i.e., if this getter has yet to be passed
                # this module).
                hintable_annotations = hintable_basename_to_annotations.get(  # type: ignore[union-attr]
                    hintable_basename, SENTINEL)

                # If such a dictionary was memoized, return this dictionary.
                if hintable_annotations is not SENTINEL:
                    return hintable_annotations  # type: ignore[return-value]
                # Else, *NO* such dictionary was memoized.

                # "__annotations__" dunder dictionary for this hintable.
                hintable_annotations = (
                    _get_pep649_hintable_annotations_or_none_uncached(hintable))

                # Cache this dictionary under this hintable's basename.
                hintable_basename_to_annotations[hintable_basename] = (  # type: ignore[index]
                    hintable_annotations)

                # Return this dictionary.
                return hintable_annotations
            # Else, *NO* module defines this hintable. In this case, fallback to
            # unmemoized behaviour. Although non-ideal, a hintable residing
            # outside a module arguably constitutes an erroneous edge case that
            # should generally *NEVER* occur. Optimizing this is *NOT* worth it.
        # Else, this hintable is neither a callable *NOR* class.
        #
        # If this hintable is a module...
        elif isinstance(hintable, ModuleType):
            # Fully-qualified name of this module.
            module_name = get_module_name(hintable)

            #FIXME: [SPEED] Globalize this getter for efficiency, please. *sigh*
            # "__annotations__" dunder dictionary for this module previously
            # memoized by a prior call to this getter if any *OR* the sentinel
            # otherwise (i.e., if this getter has yet to be passed this module).
            module_annotations = _MODULE_NAME_TO_ANNOTATIONS.get(
                module_name, SENTINEL)

            # If such a dictionary was memoized, return this dictionary.
            if module_annotations is not SENTINEL:
                return module_annotations  # type: ignore[return-value]
            # Else, *NO* such dictionary was memoized.

            # "__annotations__" dunder dictionary for this module.
            module_annotations = (
                _get_pep649_hintable_annotations_or_none_uncached(hintable))

            # Cache this dictionary under this module's fully-qualified name.
            _MODULE_NAME_TO_ANNOTATIONS[module_name] = module_annotations

            # Return this dictionary.
            return module_annotations
        # Else, this hintable is an unknown type of object.

        # Fallback to the unmemoized getter underlying this memoized getter.
        # Although non-ideal, the only general-purpose alternative would be to
        # memoize a reference to this object, preventing this object from *EVER*
        # being garbage-collected, inviting memory leaks. In other words, there
        # exist *NO* safe means of memoizing arbitrary user-defined objects.
        return _get_pep649_hintable_annotations_or_none_uncached(hintable)


    def _get_pep649_hintable_annotations_or_none_uncached(
        hintable: Pep649Hintable) -> Optional[Pep649HintableAnnotations]:
        '''
        **Unmemoized annotations** (i.e., possibly empty ``__annotations__``
        dunder dictionary mapping from the name of each annotated child object
        of the passed hintable to the type hint annotating that child object)
        annotating the passed **hintable** (i.e., ideally pure-Python object
        defining the ``__annotations__`` dunder attribute as well as the
        :pep:`649`-compliant ``__annotate__`` dunder method if the active Python
        interpreter targets Python >= 3.14) if this hintable defines the
        ``__annotations__`` dunder dictionary *or* :data:`None` otherwise (i.e.,
        if this hintable fails to define the ``__annotations__`` dunder
        dictionary).

        This getter exhibits non-amortized worst-case :math:`O(n)` linear time
        complexity for :math:`n` the total number of unquoted forward references
        across all type hints annotating this hintable.

        Parameters
        ----------
        hintable : Pep649Hintable
            Hintable to be inspected.

        Returns
        -------
        Optional[Pep649HintableAnnotations]
            Either:

            * If this hintable is actually a hintable, the ``__annotations__``
              dunder dictionary defined by this hintable.
            * Else, :data:`None`.
        '''

        # If the passed hintable defines the PEP 649-compliant __annotate__()
        # dunder method...
        #
        # Note that:
        # * The __annotate__() dunder method is guaranteed to exist *ONLY* for
        #   standard pure-Python hintables. Various other hintables of interest
        #   (e.g., functions exported by the standard "operator" module) do
        #   *NOT* necessarily declare this method. Since this getter is commonly
        #   called in general-purpose contexts where this guarantee does
        #   *NOT* necessarily hold, we intentionally access this attribute
        #   safely albeit somewhat more slowly via getattr().
        # * The get_annotations() getter called below safely accepts the
        #   "Format.FORWARDREF" format *ONLY* when this hintable defines the
        #   __annotate__() dunder method. If this hintable does *NOT* define
        #   __annotate__() and get_annotations() is passed "Format.FORWARDREF",
        #   then get_annotations() raises either:
        #   * If this hintable at least defines the "__annotations__" dunder
        #     dictionary but this dictionary contains one or more unquoted
        #     forward references, a "NameError" exception.
        #   * Else, a "TypeError" exception.
        #   However, this higher-level getter is designed exactly to avoid
        #   raising these sorts of exceptions! Ergo, get_annotations() is safely
        #   callable only when the __annotate__() dunder method exists.
        if hasattr(hintable, '__annotate__'):
            # Defer to the PEP 649-compliant high-level
            # annotationlib.get_annotations() getter internally deferring to the
            # PEP 649-compliant low-level __annotate__() dunder callable rather
            # than the PEP 484-compliant "__annotations__" dunder attribute.
            # Why? Because the latter reduces to calling
            # "get_annotations(hintable, format=Format.VALUE)", which raises a
            # "NameError" exception if the passed hintable is annotated by one
            # or more unquoted forward references. This is unacceptable API
            # design. Yet, this is Python >= 3.14.
            return get_annotations(hintable, format=Format.FORWARDREF)
        # Else, this hintable does *NOT* define __annotate__().

        # Return either the PEP 484-compliant "__annotations__" dunder attribute
        # if this hintable defines this attribute *OR* "None" otherwise
        # (i.e., if this hintable fails to define this attribute).
        #
        # Note that:
        # * The "__annotations__" dunder attribute is guaranteed to exist *ONLY*
        #   for standard pure-Python hintables. See above for further details.
        # * The "__annotations__" dunder attribute and __annotate__() dunder
        #   method are strongly coupled. If one is defined, the other should
        #   be defined. If one is undefined, the other should be undefined.
        #   Ergo, it should *NEVER* be the case that the __annotate__() dunder
        #   method is undefined but the "__annotations__" dunder attribute is.
        #   Ergo, this edge case should *NEVER* arise. Naturally, this edge case
        #   will often arise. Why? Because nothing prevents third-party packages
        #   from manually defining "__annotations__" dunder attributes on
        #   arbitrary objects. Although CPython *COULD* prohibit that (e.g., by
        #   defining the "object.__annotations__" descriptor to do just that),
        #   CPython currently does *NOT* prohibit that. In fact, no
        #   "object.__annotations__" descriptor currently exists to even do so.
        return getattr(hintable, '__annotations__', None)


    _MODULE_NAME_TO_ANNOTATIONS: (
        Dict[str, Optional[Pep649HintableAnnotations]]) = {}
    '''
    Dictionary mapping from the fully-qualified name of each module defining one
    or more global variables annotated by type hints to that module's **memoized
    annotations dictionary** (i.e., dictionary from the name of each such global
    variable to the type hint annotating that global variable as returned by the
    :func:`.get_pep649_hintable_annotations_or_none` getter when passed that
    module).
    '''


    _MODULE_NAME_TO_HINTABLE_BASENAME_TO_ANNOTATIONS: (
        Dict[str, Dict[str, Optional[Pep649HintableAnnotations]]]) = {}
    '''
    Dictionary mapping from the fully-qualified name of each module to a nested
    dictionary mapping from the unqualified basename of each:

    * Callable in that module accepting one or more parameters annotated by type
      hints and/or returning a value annotated by a type hint to that callable's
      **memoized annotations dictionary** (i.e., dictionary from the name of
      each such parameter or return to the type hint annotating that parameter
      or return as returned by the
      :func:`.get_pep649_hintable_annotations_or_none` getter when passed that
      callable).
    * Class in that module defining one or more class variables annotated by
      type hints to that class' **memoized annotations dictionary** (i.e.,
      dictionary from the name of each such class variable to the type hint
      annotating that class variable as returned by the
      :func:`.get_pep649_hintable_annotations_or_none` getter when passed that
      class).
    '''
# Else, the active Python interpreter targets Python <= 3.13. In this case,
# trivially defer to the PEP 484-compliant "__annotations__" dunder attribute.
else:
    def clear_pep649_caches() -> None:
        pass


    def get_pep649_hintable_annotations_or_none(
        hintable: Pep649Hintable) -> Optional[Pep649HintableAnnotations]:

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




clear_pep649_caches.__doc__ = (
    '''
    Clear (i.e., empty) *all* internal :pep:`649`-specific caches specifically
    leveraged by this submodule, enabling callers to reset this submodule to its
    initial state.
    '''
)
get_pep649_hintable_annotations_or_none.__doc__ = (
    '''
    **Memoized annotations** (i.e., possibly empty ``__annotations__`` dunder
    dictionary mapping from the name of each annotated child object of the
    passed hintable to the type hint annotating that child object) annotating
    the passed **hintable** (i.e., ideally pure-Python object defining the
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

    Parameters
    ----------
    hintable : Pep649Hintable
        Hintable to be inspected.

    Returns
    -------
    Optional[Pep649HintableAnnotations]
        Either:

        * If this hintable is actually a hintable, the ``__annotations__``
          dunder dictionary defined by this hintable.
        * Else, :data:`None`.
    '''
)

# ....................{ SETTERS                            }....................
#FIXME: Generalize to support Python >= 3.14, please.
#FIXME: Unit test us up, please.
def set_pep649_hintable_annotations(
    # Mandatory parameters.
    hintable: Pep649Hintable,
    annotations: Pep649HintableAnnotations,

    # Optional parameters.
    exception_cls: TypeException = BeartypeDecorHintPep649Exception,
    exception_prefix: str = '',
) -> None:
    '''
    Set the **annotations** (i.e., ``__annotations__`` dunder dictionary mapping
    from the name of each annotated child object of the passed hintable to the
    type hint annotating that child object) annotating the passed **hintable**
    (i.e., ideally pure-Python object defining the ``__annotations__`` dunder
    attribute as well as the :pep:`649`-compliant ``__annotate__`` dunder method
    if the active Python interpreter targets Python >= 3.14) to the passed
    dictionary.

    Parameters
    ----------
    hintable : Pep649Hintable
        Hintable to be inspected.
    annotations : Pep649HintableAnnotations
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
    assert isinstance(annotations, dict), f'{repr(annotations)} not dictionary.'
    assert all(
        isinstance(annotations_key, str) for annotations_key in annotations
    ), f'{repr(annotations)} not dictionary mapping from names to type hints.'

    # If this hintable is *NOT* actually a hintable, raise an exception.
    # Amusingly, the simplest means of implementing this validation is to simply
    # retrieve the prior "__annotations__" dunder dictionary currently set on
    # this hintable.
    get_pep649_hintable_annotations(
        hintable=hintable,
        exception_cls=exception_cls,
        exception_prefix=exception_prefix,
    )
    # Else, this hintable is actually a hintable.

    # Attempt to...
    try:
        # Atomically (i.e., all-at-once) replace this hintable's existing
        # "__annotations__" dunder dictionary with these new annotations. Do so
        # atomically for both safety and efficiency.
        hintable.__annotations__ = annotations
    # If doing so fails with an exception resembling the following, this
    # hintable is *NOT* pure-Python. The canonical example are C-based decorator
    # objects (e.g., class, property, or static method descriptors), whose
    # exception message reads:
    #     AttributeError: 'method' object has no attribute '__annotations__'
    #
    # C-based decorator objects define a read-only "__annotations__" dunder
    # attribute that proxies an original writeable "__annotations__" dunder
    # attribute of the pure-Python callables they originally decorated. Ergo,
    # detecting this edge case is non-trivial and most easily deferred to
    # this late time. While non-ideal, simplicity >>>> idealism in this case.
    except AttributeError:
        #FIXME: *UGH.* PEP 649 and 749 do *NOT* want anyone to directly set
        #annotations entries under Python >= 3.14. Consider options. Maybe just
        #raise an explanatory exception under Python >= 3.14? *sigh*

        # For the name of each annotated attribute of this hintable and the new
        # hint which which to annotate this attribute, overwrite the prior hint
        # originally annotating this attribute with this new hint.
        #
        # Note that:
        # * The above assignment is an efficient O(1) operation and thus
        #   intentionally performed first.
        # * This iteration-based assignment is an inefficient O(n) operation
        #   (where "n" is the number of annotated attributes of this hintable)
        #   and thus intentionally performed last here.
        for attr_name, attr_hint in annotations.items():
            hintable.__annotations__[attr_name] = attr_hint
