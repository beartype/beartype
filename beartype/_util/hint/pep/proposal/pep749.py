#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`749`-compliant **deferred type hints** (i.e., hints that are
possibly unquoted forward references referring to currently undefined types
under Python >= 3.14).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.roar import BeartypeDecorHintPep749Exception
from beartype.typing import Union
from beartype._cave._cavefast import Format  # pyright: ignore
from beartype._data.kind.datakindiota import (
    SENTINEL,
    Iota,
)
from beartype._data.typing.datatyping import TypeException
from beartype._data.typing.datatypingport import Hint
from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_14

# ....................{ GETTERS                            }....................
#FIXME: Unit test us up, please.
#FIXME: Revise docstring, please. *sigh*
def get_hint_pep749_subhint(
    # Mandatory parameters.
    hint: Hint,
    subhint_name_dynamic: str,
    subhint_name_static: str,

    # Optional parameters.
    hint_format: Format = Format.FORWARDREF,
    exception_cls: TypeException = BeartypeDecorHintPep749Exception,
    exception_prefix: str = '',
) -> Hint:
    '''
    :pep:`749`-compliant **subhint** (i.e., nested type hint defined as an
    attribute on a parent type hint whose value is a possibly unquoted forward
    reference referring to a currently undefined type) with the passed static
    or dynamic attribute names defined on the passed parent type hint if any
    *or* raise an exception otherwise (i.e., if this parent type hint fails to
    define an attribute having either of these names).

    This getter is intentionally *not* memoized (e.g., by the
    ``@callable_cached`` decorator), as the implementation trivially reduces to
    a one-liner.

    Parameters
    ----------
    hint : Hint
        Parent type hint to be inspected.
    subhint_name_dynamic : str
        Unqualified basename of the attribute defined on this parent type hint
        yielding this hint's **dynamic subhint** (i.e., bound method accepting
        the passed format and returning this subhint in this format).
    subhint_name_static : str
        Unqualified basename of the attribute defined on this parent type hint
        yielding this hint's **static subhint** (i.e., dunder instance variable
        whose value directly provides this subhint).
    hint_format : Format, default: Format.FORWARDREF
        Format of annotated hints to be returned. Defaults to
        :attr:`Format.FORWARDREF`, in which case this getter safely encapsulates
        each otherwise unsafe unquoted forward reference transitively
        subscripting each hint annotating this hintable with a safe
        :class:`annotationlib.ForwardRef` object. Note that the remaining
        formats are situational at best. See also the
        :func`beartype._util.hint.pep.proposal.pep649.get_pep649_hintable_annotations`
        getter for further details.
    exception_cls : TypeException, default: BeartypeDecorHintPep749Exception
        Type of exception to be raised in the event of a fatal error. Defaults
        to :exc:`.BeartypeDecorHintPep749Exception`.
    exception_prefix : str, default: ''
        Human-readable substring prefixing raised exception messages. Defaults
        to the empty string.

    Returns
    -------
    Hint
        Subhint with this static or dynamic attribute name defined on this hint.

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

    # Subhint defined by this hintable if any *OR* the sentinel placeholder.
    hint_subhint = get_hint_pep749_subhint_or_sentinel(
        hint=hint,
        subhint_name_dynamic=subhint_name_dynamic,
        subhint_name_static=subhint_name_static,
        hint_format=hint_format,
        exception_cls=exception_cls,
        exception_prefix=exception_prefix,
    )

    # If this hint fails to define this subhint, raise an exception.
    if hint_subhint is SENTINEL:
        assert isinstance(exception_cls, type), (
            f'{repr(exception_cls)} not class.')
        assert issubclass(exception_cls, Exception), (
            f'{repr(exception_cls)} not exception subclass.')
        assert isinstance(exception_prefix, str), (
            f'{repr(exception_prefix)} not string.')

        # Raise a human-readable exception.
        raise exception_cls(
            f'{exception_prefix}type hint {repr(hint_subhint)} '
            f'static subhint "{subhint_name_static}" and '
            f'PEP 749 dynamic subhint "{subhint_name_dynamic}" both undefined.'
        )
    # Else, that hintable is a hintable.

    # Return this subhint.
    return hint_subhint  # pyright: ignore

# ....................{ VERSIONS                           }....................
# If the active Python interpreter targets Python >= 3.14...
if IS_PYTHON_AT_LEAST_3_14:
    # ....................{ IMPORTS                        }....................
    # Defer version-specific imports.
    from annotationlib import call_evaluate_function  # type: ignore[import-not-found]

    # ....................{ GETTERS                        }....................
    #FIXME: Consider memoization. This getter is likely to be *EXTREMELY*
    #slow. That said, we are simply outta volunteer time on this one.
    #Sometimes, you just gotta ship it as is. *shrug*
    #FIXME: Unit test us up, please. *sigh*
    #FIXME: Docstring us up, please. When doing so, quote this pertinent passage
    #from PEP 749:
    #    Except for evaluate_value, these attributes may be None if the object
    #    does not have a bound, constraints, or default. Otherwise, the
    #    attribute is a callable, similar to an __annotate__ function, that
    #    takes a single integer argument and returns the evaluated value.
    #    Unlike __annotate__ functions, these callables return a single value,
    #    not a dictionary of annotations. These attributes are read-only.
    def get_hint_pep749_subhint_or_sentinel(  # pyright: ignore
        # Mandatory parameters.
        hint: Hint,
        subhint_name_dynamic: str,
        subhint_name_static: str,

        # Optional parameters.
        hint_format: Format = Format.FORWARDREF,
        exception_cls: TypeException = BeartypeDecorHintPep749Exception,
        exception_prefix: str = '',
    ) -> Union[Hint, Iota]:
        assert isinstance(subhint_name_dynamic, str), (
            f'{repr(subhint_name_dynamic)} not string.')
        assert isinstance(subhint_name_static, str), (
            f'{repr(subhint_name_static)} not string.')
        assert isinstance(hint_format, Format), (
            f'{repr(hint_format)} not annotation format.')

        #FIXME: Comment us up, please. *sigh*
        # Either:
        # * Evaluator function with signature matching the PEP 484-compliant
        #   hint "collections.abc.Callable[[int], Hint]".
        attr_dynamic = getattr(hint, subhint_name_dynamic, SENTINEL)

        if attr_dynamic is SENTINEL:
            attr_static = getattr(hint, subhint_name_static, SENTINEL)

            if attr_static is SENTINEL:
                #FIXME: Pass an actual exception message, please. *sigh*
                raise exception_cls()

            return attr_static
        elif attr_dynamic is None:
            return SENTINEL
        elif not callable(attr_dynamic):
            raise exception_cls(
                f'{repr(attr_dynamic)} uncallable.')

        return call_evaluate_function(attr_dynamic, hint_format)

# Else, the active Python interpreter targets Python <= 3.13. In this case,
# trivially defer to the PEP 484-compliant "__annotations__" dunder attribute.
else:
    # ....................{ GETTERS                        }....................
    def get_hint_pep749_subhint_or_sentinel(  # type: ignore[misc]
        hint: Hint,
        subhint_name_dynamic: str,
        subhint_name_static: str,
        **kwargs
    ) -> Union[Hint, Iota]:

        #FIXME: Pretty unsafe. Consider raising an explanatory exception if this
        #attribute is undefined. Of course, at that point, we're just violating
        #DRY with the sibling get_hint_pep749_subhint_or_sentinel()
        #implementation defined above.
        #FIXME: Revise commentary, please.

        # Return either the PEP 484-compliant "__annotations__" dunder attribute
        # if the passed hintable defines this attribute *OR* "None" otherwise
        # (i.e., if this hintable fails to define this attribute).
        return getattr(hint, subhint_name_static)
