#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2021 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **PEP-agnostic type hint getter utilities** (i.e., callables
querying type hints supported by :mod:`beartype` for various properties,
regardless of whether those hints comply with PEP standards or not).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                           }....................
from beartype._cave._cavefast import NoneType
from beartype._data.hint.pep.sign.datapepsigns import (
    HintSignAnnotated,
    HintSignNewType,
    HintSignNumpyArray,
    HintSignType,
)
from typing import Any

# See the "beartype.cave" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ GETTERS                           }....................
def get_hint_reduced(
    # Mandatory parameters.
    hint: Any,

    # Optional parameters.
    exception_prefix: str = '',
) -> Any:
    '''
    Lower-level type hint reduced (i.e., converted, extracted) from the passed
    higher-level type hint if this hint is reducible *or* this hint as is
    otherwise (i.e., if this hint is irreducible).

    Specifically, if the passed hint is:

    * *Not* PEP-compliant, this hint is returned as is unmodified.
    * PEP 593-compliant (i.e., :class:`typing.Annotated`) but beartype-agnostic
      (i.e., its second argument is *not* an instance of the
      :class:`beartype.vale._valevale.BeartypeValidator` class produced by
      subscripting the :class:`beartype.vale.Is` class), this hint is reduced
      to the first argument subscripting this hint. Doing so ignores *all*
      irrelevant annotations on this hint (e.g., reducing
      ``typing.Annotated[str, 50, False]`` to simply ``str``).

    Parameters
    ----------
    hint : Any
        Type hint to be possibly reduced.
    exception_prefix : str, optional
        Human-readable label prefixing the representation of this object in the
        exception message. Defaults to the empty string.

    Returns
    ----------
    Any
        Either:

        * If the passed higher-level type hint is reducible, a lower-level type
          hint reduced (i.e., converted, extracted) from this hint.
        * Else, this hint as is unmodified.

    Raises
    ----------
    :exc:`BeartypeDecorHintNonpepNumpyException`
        See the
        :func:`beartype._util.hint.pep.mod.utilmodnumpy.reduce_hint_numpy_ndarray`
        function for further details.
    '''

    # Avoid circular import dependencies.
    from beartype._util.hint.pep.utilpepget import get_hint_pep_sign_or_none
    from beartype._util.hint.pep.proposal.utilpep544 import (
        reduce_hint_pep484_generic_io_to_pep544_protocol,
        is_hint_pep484_generic_io,
    )

    # Sign uniquely identifying this hint if this hint is identifiable *OR*
    # "None" otherwise.
    hint_sign = get_hint_pep_sign_or_none(hint)

    # This reduction is intentionally implemented as a linear series of tests,
    # ordered in descending likelihood of a match for efficiency. While
    # alternatives (that are more readily readable and maintainable) do exist,
    # these alternatives all appear to be substantially less efficient.
    #
    # ..................{ NON-PEP                           }..................
    # If this hint is unidentifiable, return this hint as is unmodified.
    if hint_sign is None:
        return hint
    # ..................{ PEP 484 ~ none                    }..................
    # If this is the PEP 484-compliant "None" singleton, reduce this hint to
    # the type of that singleton. While *NOT* explicitly defined by the
    # "typing" module, PEP 484 explicitly supports this singleton:
    #     When used in a type hint, the expression None is considered
    #     equivalent to type(None).
    # The "None" singleton is used to type callables lacking an explicit
    # "return" statement and thus absurdly common. Ergo, detect this first.
    elif hint is None:
        hint = NoneType
    # ..................{ PEP 593                           }..................
    # If this hint is a PEP 593-compliant metahint...
    #
    # Since metahints form the core backbone of our beartype-specific data
    # validation API, metahints are extremely common and thus detected next.
    elif hint_sign is HintSignAnnotated:
        # Avoid circular import dependencies.
        from beartype._util.hint.pep.proposal.utilpep593 import (
            get_hint_pep593_metahint,
            is_hint_pep593_beartype,
        )

        # If this metahint is beartype-agnostic and thus irrelevant to us,
        # ignore all annotations on this hint by reducing this hint to the
        # lower-level hint it annotates.
        if not is_hint_pep593_beartype(hint):
            hint = get_hint_pep593_metahint(hint)
        # Else, this metahint is beartype-specific. In this case, preserve
        # this hint as is for subsequent handling elsewhere.
    # ..................{ NON-PEP ~ numpy                   }..................
    # If this hint is a PEP-noncompliant typed NumPy array (e.g.,
    # "numpy.typing.NDArray[np.float64]"), reduce this hint to the equivalent
    # well-supported beartype validator.
    #
    # Typed NumPy arrays are increasingly common and thus detected next.
    elif hint_sign is HintSignNumpyArray:
        # Avoid circular import dependencies.
        from beartype._util.hint.pep.mod.utilmodnumpy import (
            reduce_hint_numpy_ndarray)
        hint = reduce_hint_numpy_ndarray(
            hint=hint, exception_prefix=exception_prefix)
    # ..................{ PEP (484|585) ~ subclass          }..................
    # If this hint is a PEP 484-compliant subclass type hint subscripted by an
    # ignorable child type hint (e.g., "object", "typing.Any"), silently ignore
    # this argument by reducing this hint to the "type" superclass. Although
    # this logic could also be performed elsewhere, doing so here simplifies
    # matters dramatically. Note that this reduction *CANNOT* be performed by
    # the is_hint_ignorable() tester, as subclass type hints subscripted by
    # ignorable child type hints are *NOT* ignorable; they're simply safely
    # reducible to the "type" superclass.
    #
    # Subclass type hints are reasonably uncommon and thus detected late.
    elif hint_sign is HintSignType:
        # Avoid circular import dependencies.
        from beartype._util.hint.pep.proposal.pep484585.utilpepsubclass import (
            reduce_hint_pep484585_subclass_superclass_if_ignorable)
        hint = reduce_hint_pep484585_subclass_superclass_if_ignorable(
            hint=hint, exception_prefix=exception_prefix)
    # ..................{ PEP 484 ~ new type                }..................
    # If this hint is a PEP 484-compliant new type, reduce this hint to the
    # user-defined class aliased by this hint. Although this logic could also
    # be performed elsewhere, doing so here simplifies matters.
    #
    # New type hints are functionally useless for most meaningful purposes and
    # thus fairly rare in the wild. Ergo, detect these late.
    elif hint_sign is HintSignNewType:
        # Avoid circular import dependencies.
        from beartype._util.hint.pep.proposal.utilpep484 import (
            get_hint_pep484_newtype_class)
        hint = get_hint_pep484_newtype_class(hint)
    # ..................{ PEP 484 ~ io                      }..................
    # If this hint is a PEP 484-compliant IO generic base class *AND* the
    # active Python interpreter targets Python >= 3.8 and thus supports PEP
    # 544-compliant protocols, reduce this functionally useless hint to the
    # corresponding functionally useful beartype-specific PEP 544-compliant
    # protocol implementing this hint.
    #
    # IO generic base classes are extremely rare and thus detected last.
    #
    # Note that PEP 484-compliant IO generic base classes are technically
    # usable under Python < 3.8 (e.g., by explicitly subclassing those classes
    # from third-party classes). Ergo, we can neither safely emit warnings nor
    # raise exceptions on visiting these classes under *ANY* Python version.
    elif is_hint_pep484_generic_io(hint):
        hint = reduce_hint_pep484_generic_io_to_pep544_protocol(hint)

    # Return this possibly reduced hint.
    return hint
