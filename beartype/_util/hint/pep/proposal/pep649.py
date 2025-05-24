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
#FIXME: Refactor all unsafe access of the low-level "__annotations__" dunder
#attribute to instead call this high-level getter, please. The only remaining
#one appears to be the higher-level "beartype.typing._typingpep544" submodule.
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


#FIXME: Unit test us up, please.
def get_pep649_hintable_annotations_or_none(
    hintable: Pep649Hintable) -> Optional[Pep649HintableAnnotations]:
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

    # Demonstrable monstrosity demons!
    #
    # Note that:
    # * The "__annotations__" dunder attribute is guaranteed to exist *ONLY* for
    #   standard pure-Python callables. Various other callables of interest
    #   (e.g., functions exported by the standard "operator" module) do *NOT*
    #   necessarily declare that attribute. Since this getter is commonly called
    #   in general-purpose contexts where this guarantee does *NOT*
    #   necessarily hold, we intentionally access that attribute safely albeit
    #   somewhat more slowly via getattr().
    return getattr(hintable, '__annotations__', None)

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

    # Set the "__annotations__" dictionary dictionary on this hintable.
    hintable.__annotations__ = annotations
