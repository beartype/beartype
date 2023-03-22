#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **PEP-agnostic type hint reducers** (i.e., low-level callables
*temporarily* converting type hints from one format into another, either
losslessly or in a lossy manner).

Type hint reductions imposed by this submodule are purely internal to
:mod:`beartype` itself and thus transient in nature. These reductions are *not*
permanently applied to the ``__annotations__`` dunder dictionaries of the
classes and callables annotated by these type hints.

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.typing import (
    Any,
    Callable,
    Dict,
    Optional,
)
from beartype._conf.confcls import BeartypeConf
from beartype._data.datatyping import (
    Pep484TowerComplex,
    Pep484TowerFloat,
)
from beartype._data.hint.pep.sign.datapepsigncls import HintSign
from beartype._data.hint.pep.sign.datapepsigns import (
    HintSignAnnotated,
    # HintSignBinaryIO,
    HintSignDataclassInitVar,
    HintSignFinal,
    HintSignGeneric,
    # HintSignIO,
    HintSignNewType,
    HintSignNone,
    HintSignNumpyArray,
    # HintSignTextIO,
    HintSignType,
    HintSignTypeVar,
    HintSignTypedDict,
)
from beartype._util.cache.utilcachecall import callable_cached
from beartype._util.hint.pep.mod.utilmodnumpy import reduce_hint_numpy_ndarray
from beartype._util.hint.pep.proposal.pep484.utilpep484 import (
    reduce_hint_pep484_none)
from beartype._util.hint.pep.proposal.pep484.utilpep484generic import (
    reduce_hint_pep484_generic)
from beartype._util.hint.pep.proposal.pep484.utilpep484newtype import (
    get_hint_pep484_newtype_class)
from beartype._util.hint.pep.proposal.pep484.utilpep484typevar import (
    reduce_hint_pep484_typevar)
from beartype._util.hint.pep.proposal.pep484585.utilpep484585type import (
    reduce_hint_pep484585_subclass_superclass_if_ignorable)
from beartype._util.hint.pep.proposal.utilpep557 import (
    get_hint_pep557_initvar_arg)
from beartype._util.hint.pep.proposal.utilpep589 import reduce_hint_pep589
from beartype._util.hint.pep.proposal.utilpep591 import reduce_hint_pep591
from beartype._util.hint.pep.proposal.utilpep593 import reduce_hint_pep593
from beartype._util.hint.pep.utilpepget import get_hint_pep_sign_or_none
from beartype._util.hint.utilhinttest import die_unless_hint

# ....................{ REDUCERS                           }....................
@callable_cached
def reduce_hint(
    hint: Any,
    conf: BeartypeConf,
    arg_name: Optional[str],
    exception_prefix: str,
) -> object:
    '''
    Lower-level type hint reduced (i.e., converted) from the passed higher-level
    type hint if this hint is reducible *or* this hint as is otherwise (i.e., if
    this hint is irreducible).

    This reducer is memoized for efficiency.

    Parameters
    ----------
    hint : Any
        Type hint to be possibly reduced.
    conf : BeartypeConf
        **Beartype configuration** (i.e., self-caching dataclass encapsulating
        all settings configuring type-checking for the passed object).
    arg_name : Optional[str]
        Either:

        * If this hint annotates a parameter of some callable, the name of that
          parameter.
        * If this hint annotates the return of some callable, ``"return"``.
        * Else, :data:`None`.
    exception_prefix : str
        Human-readable label prefixing the representation of this object in the
        exception message.

    Returns
    ----------
    object
        Either:

        * If the passed higher-level type hint is reducible, a lower-level type
          hint reduced (i.e., converted, extracted) from this hint.
        * Else, this hint as is unmodified.

    Raises
    ----------
    BeartypeDecorHintNonpepNumpyException
        See the
        :func:`beartype._util.hint.pep.mod.utilmodnumpy.reduce_hint_numpy_ndarray`
        function for further details.
    '''
    assert isinstance(conf, BeartypeConf), f'{repr(conf)} not configuration.'

    # ..................{ SIGN                               }..................
    # Sign uniquely identifying this hint if this hint is identifiable *OR*
    # "None" otherwise.
    hint_sign = get_hint_pep_sign_or_none(hint)

    # This reduction is intentionally implemented as a linear series of tests,
    # ordered in descending likelihood of a match for efficiency. While
    # alternatives (that are more readily readable and maintainable) do exist,
    # these alternatives all appear to be substantially less efficient.
    #
    # ..................{ NON-PEP                            }..................
    # If this hint is unidentifiable...
    #
    # Since this includes *ALL* isinstanceable classes (including both
    # user-defined classes and builtin types), this is *ALWAYS* detected first.

    #FIXME: Refactor this into a proper reducer registered with the
    #"_HINT_SIGN_TO_REDUCER" dictionary as a key-value pair resembling:
    #    None: reduce_hint_class,  # type: ignore[dict-item]
    #
    #Doing so will require:
    #* Refactoring *ALL* currently defined reducers to accept variadic arguments
    #  (i.e., "*args, **kwargs"). Trivial, thankfully. See the newly defined
    #  reduce_hint_pep647() function as an example.
    #* Passing "conf=conf" to these reducers below.
    #* Defining a new reduce_hint_class() reducer elsewhere whose body is the
    #  body of this "if" conditional.
    if hint_sign is None:
        # If...
        if (
            # This configuration enables support for the PEP 484-compliant
            # implicit numeric tower *AND*...
            conf.is_pep484_tower and
            # This hint is either the builtin "float" or "complex" classes
            # governed by this tower...
            (hint is float or hint is complex)
        # Then expand this hint to the corresponding numeric tower.
        ):
            # Expand this hint to match...
            hint = (
                # If this hint is the builtin "float" class, both the builtin
                # "float" and "int" classes;
                Pep484TowerFloat
                if hint is float else
                # Else, this hint is the builtin "complex" class by the above
                # condition; in this case, the builtin "complex", "float", and
                # "int" classes.
                Pep484TowerComplex
            )
        # Else, this hint is truly unidentifiable.
        else:
            # If this hint is *NOT* a valid type hint, raise an exception.
            #
            # Note this function call is effectively memoized and thus fast.
            die_unless_hint(hint=hint, exception_prefix=exception_prefix)
            # Else, this hint is a valid type hint.

        # Return this hint as is unmodified.
        return hint
    # ..................{ FALLBACK                           }..................
    # Else, this hint was *NOT* reduced hint.
    else:
        # Callable reducing this hint if a callable reducing hints with this
        # sign was previously registered *OR* "None" otherwise (i.e., if *NO*
        # such callable was registered, in which case this hint is preserved).
        hint_reducer = _HINT_SIGN_TO_REDUCER.get(hint_sign)

        # If a callable reducing hints with this sign was previously registered,
        # reduce this hint to a lower-level hint via this callable.
        if hint_reducer is not None:
            hint = hint_reducer(  # type: ignore[call-arg]
                hint=hint, exception_prefix=exception_prefix)  # pyright: ignore[reportGeneralTypeIssues]
        # Else, *NO* such callable was registered. Preserve this hint as is!

    # Return this possibly reduced hint.
    return hint

# ....................{ PRIVATE ~ globals                  }....................
#FIXME: After dropping Python 3.7 support:
#* Replace "Callable[[object, str], object]" here with a callback protocol:
#      https://mypy.readthedocs.io/en/stable/protocols.html#callback-protocols
#  Why? Because the current approach forces positional arguments. But we call
#  these callables with keyword arguments above! Chaos ensues.
#* Remove the "# type: ignore[call-arg]" pragmas above, which are horrible.
#* Remove the "# type: ignore[dict-item]" pragmas above, which are horrible.
_HINT_SIGN_TO_REDUCER: Dict[HintSign, Callable[[object, str], object]] = {
    # ..................{ PEP 484                            }..................
    # If this hint is a PEP 484-compliant IO generic base class *AND* the active
    # Python interpreter targets Python >= 3.8 and thus supports PEP
    # 544-compliant protocols, reduce this functionally useless hint to the
    # corresponding functionally useful beartype-specific PEP 544-compliant
    # protocol implementing this hint.
    #
    # Note that PEP 484-compliant IO generic base classes are technically usable
    # under Python < 3.8 (e.g., by explicitly subclassing those classes from
    # third-party classes). Ergo, we can neither safely emit warnings nor raise
    # exceptions on visiting these classes under *ANY* Python version.
    HintSignGeneric: reduce_hint_pep484_generic,  # type: ignore[dict-item]

    # If this hint is a PEP 484-compliant new type, reduce this hint to the
    # user-defined class aliased by this hint. Although this logic could also
    # be performed elsewhere, doing so here simplifies matters.
    HintSignNewType: get_hint_pep484_newtype_class,  # type: ignore[dict-item]

    # If this is the PEP 484-compliant "None" singleton, reduce this hint to
    # the type of that singleton. While *NOT* explicitly defined by the
    # "typing" module, PEP 484 explicitly supports this singleton:
    #     When used in a type hint, the expression None is considered
    #     equivalent to type(None).
    #
    # The "None" singleton is used to type callables lacking an explicit
    # "return" statement and thus absurdly common.
    HintSignNone: reduce_hint_pep484_none,  # type: ignore[dict-item]

    #FIXME: Remove this branch *AFTER* deeply type-checking type variables.
    # If this type variable was parametrized by one or more bounded
    # constraints, reduce this hint to these constraints.
    HintSignTypeVar: reduce_hint_pep484_typevar,  # type: ignore[dict-item]

    # ..................{ PEP (484|585)                      }..................
    # If this hint is a PEP 484- or 585-compliant subclass type hint subscripted
    # by an ignorable child type hint (e.g., "object", "typing.Any"), silently
    # ignore this argument by reducing this hint to the "type" superclass.
    # While this logic could be performed elsewhere, doing so here simplifies
    # matters dramatically. Note that this reduction *CANNOT* be performed by
    # the is_hint_ignorable() tester, as subclass type hints subscripted by
    # ignorable child type hints are *NOT* ignorable; they're simply safely
    # reducible to the "type" superclass.
    #
    # Subclass type hints are reasonably uncommon and thus detected late.
    HintSignType: reduce_hint_pep484585_subclass_superclass_if_ignorable,  # type: ignore[dict-item]

    # ..................{ PEP 557                            }..................
    # If this hint is a dataclass-specific initialization-only instance
    # variable (i.e., instance of the PEP 557-compliant "dataclasses.InitVar"
    # class introduced by Python 3.8.0), reduce this functionally useless hint
    # to the functionally useful child type hint subscripting this parent hint.
    HintSignDataclassInitVar: get_hint_pep557_initvar_arg,  # type: ignore[dict-item]

    # ..................{ PEP 589                            }..................
    #FIXME: Remove *AFTER* deeply type-checking typed dictionaries. For now,
    #shallowly type-checking such hints by reduction to untyped dictionaries
    #remains the sanest temporary work-around.

    # If this hint is a PEP 589-compliant typed dictionary (i.e.,
    # "typing.TypedDict" or "typing_extensions.TypedDict" subclass), silently
    # ignore all child type hints annotating this dictionary by reducing this
    # hint to the "Mapping" superclass. Yes, "Mapping" rather than "dict". By
    # PEP 589 edict:
    #     First, any TypedDict type is consistent with Mapping[str, object].
    #
    # Typed dictionaries are largely discouraged in the typing community, due to
    # their non-standard semantics and syntax.
    HintSignTypedDict: reduce_hint_pep589,  # type: ignore[dict-item]

    # ..................{ PEP 591                            }..................
    #FIXME: Remove *AFTER* deeply type-checking typed dictionaries. For now,
    #shallowly type-checking such hints by reduction to untyped dictionaries
    #remains the sanest temporary work-around.

    # If this hint is a PEP 591-compliant "typing.Final[...]" type hint,
    # silently reduce this hint to its subscripted argument (e.g., from
    # "typing.Final[int]" to merely "int").
    HintSignFinal: reduce_hint_pep591,  # type: ignore[dict-item]

    # ..................{ PEP 593                            }..................
    # If this hint is a PEP 593-compliant beartype-agnostic type metahint,
    # ignore all annotations on this hint by reducing this hint to the
    # lower-level hint it annotates.
    HintSignAnnotated: reduce_hint_pep593,  # type: ignore[dict-item]

    # ..................{ NON-PEP ~ numpy                    }..................
    # If this hint is a PEP-noncompliant typed NumPy array (e.g.,
    # "numpy.typing.NDArray[np.float64]"), reduce this hint to the equivalent
    # well-supported beartype validator.
    HintSignNumpyArray: reduce_hint_numpy_ndarray,  # type: ignore[dict-item]
}
'''
Dictionary mapping from each sign uniquely identifying PEP-compliant type hints
to that sign's **reducer** (i.e., callable reducing those higher-level hints to
lower-level type hints).

Each value of this dictionary should be a callable with signature resembling:

.. code-block:: python

   def reduce_pep{pep_number}_hint(
       hint: object, exception_prefix: str) -> object:
'''
