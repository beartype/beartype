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

    #FIXME: Unit test us up, please.
    #FIXME: Contemplate how, actually, to safely memoize this. Hintables are
    #externally user-defined. We can't retain references to hintables without
    #risking memory leaks. What we *CAN* do, however, is retain references to
    #strings -- notably, the "hintable.__qualname__" dunder attribute if that
    #attribute exists. So, that's what we'll cache on. Naturally, we should
    #implement this caching scheme manually via a global private dictionary
    #declared below rather than a standard caching decorator.
    #
    #Note that, if the "hintable.__qualname__" dunder attribute does *NOT*
    #exist, then we should simply avoid attempting to cache anything while still
    #calling get_annotations().
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
# Else, the active Python interpreter targets Python <= 3.13. In this case,
# trivially defer to the PEP 484-compliant "__annotations__" dunder attribute.
else:
    #FIXME: Unit test us up, please.
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


get_pep649_hintable_annotations_or_none.__doc__ = (
    '''
    **Annotations** (i.e., possibly empty ``__annotations__`` dunder dictionary
    mapping from the name of each annotated child object of the passed hintable
    to the type hint annotating that child object) annotating the passed
    **hintable** (i.e., ideally pure-Python object defining the
    ``__annotations__`` dunder attribute as well as the :pep:`649`-compliant
    ``__annotate__`` dunder method if the active Python interpreter targets
    Python >= 3.14) if this hintable defines the ``__annotations__`` dunder
    dictionary *or* :data:`None` otherwise (i.e., if this hintable fails to
    define the ``__annotations__`` dunder dictionary).

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
