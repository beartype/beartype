#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2024 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`604`-compliant type hint utilities.

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_10

# ....................{ VERSIONS                           }....................
# If the active Python interpreter targets Python >= 3.10 and thus supports PEP
# 604, define testers requiring this level of support...
if IS_PYTHON_AT_LEAST_3_10:
    # ....................{ IMPORTS                        }....................
    # Defer version-specific imports.
    from beartype.roar import BeartypeDecorHintPep604Exception
    from beartype._cave._cavefast import (
        HintPep604Type,
        HintPep604Types,
    )

    # ....................{ RAISERS                        }....................
    #FIXME: Unit test us up, please.
    def die_if_hint_pep604_inconsistent(hint: object) -> None:

        # Avoid circular import dependencies.
        from beartype._util.hint.utilhintget import get_hint_repr

        # If this hint is invalid as an item of a PEP 604-compliant new union,
        # silently reduce to a noop.
        if not isinstance(hint, HintPep604Types):
            return
        # Else, this hint is valid as an item of a PEP 604-compliant new union.

        # Machine-readable representation of this hint.
        hint_repr = get_hint_repr(hint)

        # If this representation is prefixed by the "<" character, this
        # representation is assumed to be (at least *SOMEWHAT*) standardized and
        # thus internally consistent. This includes:
        # * Standard classes (e.g., "<class 'bool'>").
        # * @beartype-specific forward reference subclasses (e.g., "<forwardref
        #   UndeclaredClass(__beartype_scope__='some_package')>").
        #
        # This is *NOT* simply an optimization. Standardized representations
        # *MUST* be excluded from consideration, as the representations of new
        # unions containing these hints is *NOT* prefixed by "<": e.g.,
        #     >>> repr(bool)
        #     <class 'bool'>
        #     >>> bool | None
        #     bool | None
        if hint_repr[0] == '<':
            return
        # Else, this representation is *NOT* prefixed by the "<" character.

        # Arbitrary PEP 604-compliant new union defined as the conjunction
        # of this hint with an arbitrary builtin type guaranteed to exist.
        #
        # Note that order is significant.
        hint_pep604 = hint | int  # type: ignore[operator]

        # Machine-readable representation of this new union.
        hint_pep604_repr = get_hint_repr(hint_pep604)

        # If the representation of this new union is *NOT* prefixed by the
        # representation of this hint, raise an exception.
        if not hint_pep604_repr.startswith(hint_repr):
            raise BeartypeDecorHintPep604Exception(
                f'Type hint {hint_repr} inconsistent with respect to '
                f'repr() strings. Since @beartype requires consistency '
                f'between type hints and repr() strings, this hint is '
                f'unsupported by @beartype. Consider reporting this issue '
                f'to the third-party developer implementing this hint: e.g.,\n'
                f'\t>>> repr({hint_repr})\n'
                f'\t{hint_repr}  # <-- this is fine\n'
                f'\t>>> repr({hint_repr} | int)\n'
                f'\t{hint_pep604_repr}  # <-- *THIS IS REALLY SUPER BAD*\n'
                f'\n'
                f'\t# Ideally, that output should instead resemble:\n'
                f'\t>>> repr({hint_repr} | int)\n'
                f'\t{hint_repr} | int  # <-- what @beartype wants!'
            )
        # Else, the representation of this new union is prefixed by the
        # representation of this hint as expected.

    # ....................{ TESTERS                        }....................
    def is_hint_pep604(hint: object) -> bool:

        # Release the werecars, Bender!
        return isinstance(hint, HintPep604Type)
# Else, the active Python interpreter targets Python < 3.10 and thus fails to
# support PEP 604. In this case, define fallback functions.
#
# Tonight, we howl at the moon. Tomorrow, the one-liner!
else:
    def die_if_hint_pep604_inconsistent(hint: object) -> None:
        pass

    def is_hint_pep604(hint: object) -> bool:
        return False


die_if_hint_pep604_inconsistent.__doc__ = (
    '''
    Raise an exception if the passed object is a :pep:`604`-compliant
    **inconsistent type hint** (i.e., object permissible as an item of a
    :pep:`604`-compliant new union whose machine-readable representation is
    *not* the machine-readable representation of this hint in new unions).

    Motivation
    ----------
    This raiser protects the :mod:`beartype` codebase against inconsistencies in
    poorly implemented third-party type hints whose **machine-readable
    representations** (i.e., strings returned by passing those hints to the
    :func:`repr` builtin) differ from their representations in new unions
    containing those hints.

    Ideally, *no* such inconsistencies would ever exist. For unknown reasons,
    some third-party type hints induce such inconsistencies. :mod:`nptyping` is
    the canonical example. Type hint factories published by :mod:`nptyping`
    dynamically create in-memory classes all sharing the same fully-qualified
    names despite being distinct classes. Ye who code, grok and weep: e.g.,

    .. code-block:: pycon

       # Define two typical "nptyping" type hints.
       >>> from nptyping import Float64, NDArray, Shape
       >>> foo = NDArray[Shape["N, N"], Float64]
       >>> bar = NDArray[Shape["*"], Float64]

       >>> repr(foo)
       NDArray[Shape["N, N"], Float64]  # <-- this is sane
       >>> repr(bar)
       NDArray[Shape["*"], Float64]  # <-- this is sane, too

       >>> foo == bar
       False    # <-- still sane
       >>> foo.__name__
       NDArray  # <-- this is insane
       >>> bar.__name__
       NDArray  # <-- still insane after all these years

       >>> foo | None == bar | None
       False           # <-- back to sane
       >>> repr(foo | None)
       NDArray | None  # <-- big yikes
       >>> repr(bar | None)
       NDArray | None  # <-- yikes intensifies

    ``foo`` and ``bar`` are distinct type hints matching different NumPy arrays;
    their representations are likewise distinct. The new unions of those hints
    with :data:`None` are also distinct type hints; nonetheless, the
    representations of those new unions **are the exact same.**

    This raiser detects this inconsistency by raising an exception from the
    :func:`beartype.beartype` decorator. If we failed to do so, then
    :func:`beartype.beartype` would behave non-deterministically when presented
    with such hints. Consider the following decoration:

    .. code-block:: python

       @beartype
       def bad_func(first_array: foo | None, second_array: bar | None) -> None:
           ...

    Given that decoration, :func:`beartype.beartype` would (in order):

    #. Cache the first new union ``foo | None`` under the string representation
       ``"NDArray | None"``.
    #. Erroneously replace the second new union ``bar | None`` with the
       previously cached new union ``foo | None``. Why? Because those two new
       unions share the same representations. From the limited perspective of
       :mod:`beartype`, those two new unions are effectively the same new union
       and thus can be safely de-duplicated. *This is why we facepalm.*

    Parameters
    ----------
    hint : object
        Type hint to be inspected.

    Raises
    ------
    bool
        :data:`True` only if this object is a :pep:`604`-compliant union.
    ''')


is_hint_pep604.__doc__ = (
    '''
    :data:`True` only if the passed object is a :pep:`604`-compliant **union**
    (i.e., ``|``-delimited disjunction of two or more isinstanceable types).

    Parameters
    ----------
    hint : object
        Type hint to be inspected.

    Returns
    -------
    bool
        :data:`True` only if this object is a :pep:`604`-compliant union.
    ''')
