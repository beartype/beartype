#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **type hint factories** (i.e., PEP-compliant type hint factories
supplementing standard type hint factories published by the :mod:`typing` module
with custom behaviours, including backward compatibility with older Python
versions that would otherwise *not* support those factories).

This private submodule is intentionally distinct from the lower-level private
:data:`beartype._data.hint.datahinttyping` submodule.

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    FrozenSet,
    Iterable,
    List,
    Optional,
    Sequence,
    Set,
    Tuple,
    TypeVar,
    Union,
)
from beartype._util.hint.utilhintfactory import TypeHintTypeFactory
from beartype._util.api.standard.utiltyping import (
    import_typing_attr_or_fallback)
# from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_11

# ....................{ FACTORIES                          }....................
#FIXME: This approach is *PHENOMENAL.* No. Seriously, We could implement a
#full-blown "beartype.typing" subpackage (or perhaps even separate "beartyping"
#package) extending this core concept to *ALL* type hint factories, enabling
#users to trivially annotate with any type hint factory regardless of the
#current version of Python or whether "typing_extensions" is installed or not.

# Portably backport *ALL* type hint factories introduced by subsequent Python
# interpreters more recent than that of the oldest actively maintained Python
# interpreter still supported by @beartype, regardless of the current version of
# Python and regardless of whether this submodule is currently being subject to
# static type-checking or not. Praise be to MIT ML guru and stunning Hypothesis
# maintainer @rsokl (Ryan Soklaski) for this brilliant circumvention. \o/
#
# If this submodule is currently being statically type-checked (e.g., mypy),
# intentionally import from the third-party "typing_extensions" module rather
# than the standard "typing" module. Why? Because doing so eliminates Python
# version complaints from static type-checkers (e.g., mypy, pyright). Static
# type-checkers could care less whether "typing_extensions" is actually
# installed or not; they only care that "typing_extensions" unconditionally
# defines this type factory across all Python versions, whereas "typing" only
# conditionally defines these type factories under particular Python versions.
if TYPE_CHECKING:
    # ....................{ PEP 742                        }....................
    # PEP 742-compliant "TypeIs[...]" type hints first introduced by Python
    # >= 3.13 are a high internal priority for @beartype. Hinting the return of
    # the is_bearable() tester with a type guard created by this factory
    # effectively coerces that tester into an arbitrarily "smart" type narrower
    # and thus type parser at static analysis time, reducing complaints from
    # static type-checkers in downstream code deferring to that tester.

    #FIXME: Unconditionally globalize this *AFTER* dropping Python 3.12: e.g.,
    #   from typing import TypeIs as TypeIs
    from typing_extensions import TypeIs as TypeIs

    # ....................{ PEP 747                        }....................
    # PEP 747-compliant "TypeForm[...]" type hints first introduced by Python
    # >= 3.14 are a high internal priority for @beartype. Hinting parameters,
    # returns, and local variables of both private and public @beartype
    # callables (including the common first parameter "hint" accepted by most
    # callables) with type forms created by this factory enables static
    # type-checkers to ensure that these objects are actually type hints.
    #
    # Note that we intentionally alias "TypeForm" to a more concise and readable
    # name. The term "type form" does *NOT* especially mean much within the
    # context of Python type hints. The term "hint", on the other hand, does.

    #FIXME: Replace "typing_extensions" with simply "typing" this *AFTER*
    #dropping Python 3.13.
    from typing_extensions import (  # type: ignore[attr-defined]
        TypeForm as Hint,
        TypeForm as HintBare,
    )

    # See discussion below, please. *sigh*
    from typing_extensions import TypeAlias
# Else, this submodule is currently being imported at runtime by Python. In this
# case, dynamically import these type factories from whichever of the standard
# "typing" module *OR* the third-party "typing_extensions" module declares these
# factories, falling back to various builtin types if none do.
else:
    # ....................{ PEP 742                        }....................
    TypeIs = import_typing_attr_or_fallback(
        'TypeIs', TypeHintTypeFactory(bool))

    # ....................{ PEP 747                        }....................
    TypeForm = import_typing_attr_or_fallback(
        'TypeForm', TypeHintTypeFactory(object))


    HintBare = TypeForm
    '''
    PEP-compliant type hint matching *any* PEP-compliant type hint.

    This hint should *only* be used to explicitly subscript the
    :obj:`typing.TypeForm` type hint factory. For all other purposes, the
    subscripted :data:`.Hint` type hint should be strongly preferred.
    '''


    Hint = TypeForm[Any]
    '''
    PEP-compliant type hint matching *any* PEP-compliant type hint.

    Although semantically equivalent to ``typing.TypeForm[object]``, the
    unsubscripted :obj:`typing.TypeForm` type hint factory is currently unusable
    as such under Python <= 3.14. This insane hack trivially circumvents that.
    '''

# ....................{ EXPORT                             }....................
# Explicitly export the "Hint" and "HintBare" aliases of the "typing.TypeForm"
# hint factory imported above. Blame mypy.
__all__ = [
    'Hint',
    'HintBare',
]

# ....................{ HINTS                              }....................
HintOrNone = Optional[Hint]
'''
PEP-compliant type hint matching either any PEP-compliant type hint *or*
:data:`None`.
'''


T_Hint = TypeVar('T_Hint', bound=Hint)
'''
:pep:`484`-compliant **type hint type variable** (i.e.,
:class:`typing.TypeVar` object bound to match *only* PEP-compliant type
hints).
'''

# ....................{ HINTS ~ container                  }....................
#FIXME: Ideally, all of the below should themselves be annotated as ": Hint".
#Mypy likes that but pyright hates that. This is why we can't have good things.

FrozenSetHints = FrozenSet[Hint]
'''
:pep:`585`-compliant type hint matching *any* **type hint frozen set** (i.e.,
frozen set of zero or more type hints).
'''


IterableHints = Iterable[Hint]
'''
:pep:`585`-compliant type hint matching *any* **type hint iterable** (i.e.,
iterable iteratively yielding zero or more type hints).
'''


ListHints = List[Hint]
'''
:pep:`585`-compliant type hint matching *any* **type hint list** (i.e., list of
zero or more type hints).
'''


SequenceHints = Sequence[Hint]
'''
:pep:`585`-compliant type hint matching *any* **type hint sequence** (i.e.,
sequence of zero or more type hints).
'''


SetHints = Set[Hint]
'''
:pep:`585`-compliant type hint matching *any* **type hint set** (i.e., set of
zero or more type hints).
'''

# ....................{ HINTS ~ container : dict           }....................
DictStrToHint = Dict[str, Hint]
'''
:pep:`585`-compliant type hint matching a dictionary mapping from strings to
PEP-compliant type hints.
'''


TypeVarToHint = Dict[TypeVar, Hint]
'''
:pep:`585`-compliant type hint matching a **type variable lookup table** (i.e.,
dictionary mapping from :pep:`484`-compliant type variables to the arbitrary
type hints those type variables map to).

Type variable lookup tables are commonly employed throughout the :mod:`beartype`
codebase to record **type variable substitutions** (i.e., the dynamic
replacement of type variables by non-type variables in larger type hints).
'''

# ....................{ HINTS ~ container : tuple          }....................
TupleHints = Tuple[Hint, ...]
'''
:pep:`585`-compliant type hint matching *any* **child type hints** (i.e., tuple
of zero or more child type hints subscripting a parent type hint).
'''


HintOrTupleHints = Union[Hint, TupleHints]
'''
:pep:`585`-compliant type hint matching either a single type hint *or* a tuple
of zero or more type hints.
'''
