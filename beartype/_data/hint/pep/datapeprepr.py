#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **bare PEP-compliant type hint representations** (i.e., global
constants pertaining to machine-readable strings returned by the :func:`repr`
builtin suffixed by *no* "["- and "]"-delimited subscription representations).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.typing import (
    Dict,
    Set,
)
from beartype._data.hint.datahinttyping import (
    DictStrToHintSign,
    FrozenSetStrs,
    HintSignTrie,
)
from beartype._data.hint.pep.sign.datapepsigns import (
    HintSignAny,
    HintSignAbstractSet,
    HintSignAsyncContextManager,
    HintSignAsyncIterable,
    HintSignAsyncIterator,
    HintSignAsyncGenerator,
    HintSignAwaitable,
    HintSignBinaryIO,
    HintSignByteString,
    HintSignCallable,
    HintSignChainMap,
    HintSignCollection,
    HintSignContainer,
    HintSignCoroutine,
    HintSignContextManager,
    HintSignCounter,
    HintSignDefaultDict,
    HintSignDeque,
    HintSignDict,
    HintSignForwardRef,
    HintSignFrozenSet,
    HintSignGenerator,
    HintSignItemsView,
    HintSignIterable,
    HintSignIterator,
    HintSignKeysView,
    HintSignList,
    HintSignMapping,
    HintSignMappingView,
    HintSignMatch,
    HintSignMutableMapping,
    HintSignMutableSequence,
    HintSignMutableSet,
    HintSignNewType,
    HintSignNone,
    HintSignNumpyArray,
    HintSignOrderedDict,
    HintSignPanderaAny,
    HintSignParamSpec,
    HintSignParamSpecArgs,
    HintSignParamSpecKwargs,
    HintSignPep484585GenericUnsubscripted,
    HintSignPep557DataclassInitVar,
    HintSignPep695TypeAliasUnsubscripted,
    HintSignProtocol,
    HintSignReversible,
    HintSignSequence,
    HintSignSet,
    HintSignPattern,
    HintSignTextIO,
    HintSignTuple,
    HintSignType,
    HintSignTypeVar,
    HintSignTypeVarTuple,
    HintSignUnion,
    HintSignValuesView,
)

# ....................{ HINTS                              }....................
DictStrToDictStrToHintSign = Dict[str, DictStrToHintSign]
'''
PEP-compliant type hint matching the types of the
:data:`.HINT_MODULE_NAME_TO_HINT_BASENAME_TO_SIGN` and
:data:`.HINT_MODULE_NAME_TO_TYPE_BASENAME_TO_SIGN` dictionary globals.
'''

# ....................{ MAPPINGS ~ repr                    }....................
# The majority of this dictionary is initialized with automated inspection below
# in the _init() function. The *ONLY* key-value pairs explicitly defined here
# are those *NOT* amenable to such inspection.
HINT_REPR_PREFIX_ARGS_0_OR_MORE_TO_SIGN: DictStrToHintSign = {
    # ..................{ PEP 484                            }..................
    # All other PEP 484-compliant representation prefixes are defined by
    # automated inspection below.

    # PEP 484-compliant abstract base classes (ABCs) requiring non-standard and
    # non-trivial type-checking. Although most types are trivially type-checked
    # by the isinstance() builtin, these types break the mold in various ways.

    #FIXME: Uhm. Shouldn't this be "HintSignIO" rather than
    #"HintSignPep484585GenericUnsubscripted"? What's this about, exactly? Please
    #explain this away... somehow.
    "<class 'typing.IO'>":       HintSignPep484585GenericUnsubscripted,
    "<class 'typing.BinaryIO'>": HintSignBinaryIO,
    "<class 'typing.TextIO'>":   HintSignTextIO,
}
'''
Dictionary mapping from the **possibly unsubscripted PEP-compliant type hint
representation prefix** (i.e., unsubscripted prefix of the machine-readable
strings returned by the :func:`repr` builtin for PEP-compliant type hints
permissible in both subscripted and unsubscripted forms) of each hint uniquely
identifiable by that representation to its identifying sign.

Notably, this dictionary maps from the representation prefixes of:

* *All* :pep:`484`-compliant type hints. Whereas *all* :pep:`585`-compliant type
  hints (e.g., ``list[str]``) are necessarily subscripted and thus omitted from
  this dictionary, *all* :pep:`484`-compliant type hints support at least
  unsubscripted form and most :pep:`484`-compliant type hints support
  subscription as well. Moreover, the unsubscripted forms of most
  :pep:`484`-compliant type hints convey deep semantics and thus require
  detection as PEP-compliant (e.g., :obj:`typing.List`, requiring detection and
  reduction to :class:`list`).
'''


# The majority of this dictionary is defined by explicit key-value pairs here.
HINT_REPR_PREFIX_ARGS_1_OR_MORE_TO_SIGN: DictStrToHintSign = {
    # ..................{ PEP 585                            }..................
    # PEP 585-compliant type hints *MUST* by definition be subscripted (e.g.,
    # "list[str]" rather than "list"). While the stdlib types underlying those
    # hints are isinstanceable classes and thus also permissible as type hints
    # when unsubscripted (e.g., simply "list"), unsubscripted classes convey no
    # deep semantics and thus need *NOT* be detected as PEP-compliant.
    #
    # For maintainability, these key-value pairs are intentionally listed in the
    # same order as the official list in PEP 585 itself.
    'tuple': HintSignTuple,
    'list': HintSignList,
    'dict': HintSignDict,
    'set': HintSignSet,
    'frozenset': HintSignFrozenSet,
    'type': HintSignType,
    'collections.deque': HintSignDeque,
    'collections.defaultdict': HintSignDefaultDict,
    'collections.OrderedDict': HintSignOrderedDict,
    'collections.Counter': HintSignCounter,
    'collections.ChainMap': HintSignChainMap,
    'collections.abc.Awaitable': HintSignAwaitable,
    'collections.abc.Coroutine': HintSignCoroutine,
    'collections.abc.AsyncIterable': HintSignAsyncIterable,
    'collections.abc.AsyncIterator': HintSignAsyncIterator,
    'collections.abc.AsyncGenerator': HintSignAsyncGenerator,
    'collections.abc.Iterable': HintSignIterable,
    'collections.abc.Iterator': HintSignIterator,
    'collections.abc.Generator': HintSignGenerator,
    'collections.abc.Reversible': HintSignReversible,
    'collections.abc.Container': HintSignContainer,
    'collections.abc.Collection': HintSignCollection,
    'collections.abc.Callable': HintSignCallable,
    'collections.abc.Set': HintSignAbstractSet,
    'collections.abc.MutableSet': HintSignMutableSet,
    'collections.abc.Mapping': HintSignMapping,
    'collections.abc.MutableMapping': HintSignMutableMapping,
    'collections.abc.Sequence': HintSignSequence,
    'collections.abc.MutableSequence': HintSignMutableSequence,
    'collections.abc.ByteString': HintSignByteString,
    'collections.abc.MappingView': HintSignMappingView,
    'collections.abc.KeysView': HintSignKeysView,
    'collections.abc.ItemsView': HintSignItemsView,
    'collections.abc.ValuesView': HintSignValuesView,
    'contextlib.AbstractContextManager': HintSignContextManager,
    'contextlib.AbstractAsyncContextManager': HintSignAsyncContextManager,
    're.Pattern': HintSignPattern,
    're.Match': HintSignMatch,

    # ..................{ NON-PEP ~ lib : numpy              }..................
    # The PEP-noncompliant "numpy.typing.NDArray" type hint is permissible in
    # both subscripted and unsubscripted forms. In the latter case, this hint
    # is implicitly subscripted by generic type variables. In both cases, this
    # hint presents a uniformly reliable representation -- dramatically
    # simplifying detection via a common prefix of that representation here:
    #     >>> import numpy as np
    #     >>> import numpy.typing as npt
    #     >>> repr(npt.NDArray)
    #     numpy.ndarray[typing.Any, numpy.dtype[+ScalarType]]
    #     >>> repr(npt.NDArray[np.float64])
    #     repr: numpy.ndarray[typing.Any, numpy.dtype[numpy.float64]]
    #
    # Ergo, unsubscripted "numpy.typing.NDArray" type hints present themselves
    # as implicitly subscripted through their representation.
    'numpy.ndarray': HintSignNumpyArray,
}
'''
Dictionary mapping from the **necessarily subscripted PEP-compliant type hint
representation prefixes** (i.e., unsubscripted prefix of the machine-readable
strings returned by the :func:`repr` builtin for subscripted PEP-compliant type
hints) of all hints uniquely identifiable by those representations to
their identifying signs.

Notably, this dictionary maps from the representation prefixes of:

* All :pep:`585`-compliant type hints. Whereas all :pep:`484`-compliant type
  hints support both subscripted and unsubscripted forms (e.g.,
  ``typing.List``, ``typing.List[str]``), all :pep:`585`-compliant type hints
  necessarily require subscription. While the stdlib types underlying
  :pep:`585`-compliant type hints are isinstanceable classes and thus also
  permissible as type hints when unsubscripted (e.g., simply :class:`list`),
  isinstanceable classes convey *no* deep semantics and thus need *not* be
  detected as PEP-compliant.
'''

# ....................{ MAPPINGS ~ repr : trie             }....................
# The majority of this trie is defined by explicit key-value pairs here.
HINT_REPR_PREFIX_TRIE_ARGS_0_OR_MORE_TO_SIGN: HintSignTrie = {
    # ..................{ NON-PEP ~ lib : pandera            }..................
    # All PEP-noncompliant "pandera.typing" type hints are permissible in
    # both subscripted and unsubscripted forms.
    'pandera': {
        'typing': HintSignPanderaAny,
    }
}
'''
**Sign trie** (i.e., dictionary-of-dictionaries tree data structure enabling
efficient mapping from the machine-readable representations of type hints
created by an arbitrary number of type hint factories defined by an external
third-party package to their identifying sign) from the **possibly unsubscripted
PEP-compliant type hint representation prefix** (i.e., unsubscripted prefix of
the machine-readable strings returned by the :func:`repr` builtin for
PEP-compliant type hints permissible in both subscripted and unsubscripted
forms) of each hint uniquely identifiable by that representation to its
identifying sign.
'''

# ....................{ MAPPINGS ~ type                    }....................
# The majority of this dictionary is initialized with automated inspection
# below in the _init() function. The *ONLY* key-value pairs explicitly defined
# here are those *NOT* amenable to such inspection.
HINT_MODULE_NAME_TO_HINT_BASENAME_TO_SIGN: DictStrToDictStrToHintSign = {
    # Note that the root "object" superclass *CANNOT* be safely mapped to the
    # "typing.Any" singleton with logic resembling:
    #    # ..................{ BUILTINS                           }..................
    #    # Standard builtins module.
    #    'builtins': {
    #        # ..................{ NON-PEP                        }..................
    #        # The PEP-noncompliant root "object" superclass is semantically
    #        # equivalent to the PEP-compliant "typing.Any" singleton from the
    #        # runtime type-checking perspective. Why? Because "object" is the
    #        # transitive superclass of all classes. Attributes annotated as "object"
    #        # unconditionally match *ALL* objects under isinstance()-based type
    #        # covariance and thus semantically reduce to unannotated attributes.
    #        # Reduce this hint to "typing.Any", which then reduces this hint to the
    #        # ignorable "HINT_SANE_IGNORABLE" singleton.
    #        'object': HintSignAny,
    #    },
    #
    # Why? Because doing so would then erroneously render the otherwise
    # PEP-noncompliant "object" type PEP-compliant, which would then cause
    # raisers like die_if_pep() and die_unless_pep() to exhibit anomalous
    # behaviour with respect to this type. In short, the clever solution is the
    # wrong solution. *sigh*

    # ..................{ TYPING                             }..................
    # Default *ALL* typing-like modules to the empty dictionary to simplify
    # logic in the _init() function called below.

    # Standard typing module.
    'typing': {},

    # Third-party typing backports module.
    'typing_extensions': {},

    # Third-party @beartype typing module.
    'beartype.typing': {},
}
'''
**Type hint type trie** (i.e., dictionary-of-dictionaries tree data structure
mapping from the fully-qualified names of packages and modules to a nested
dictionary mapping from the unqualified basenames of all PEP-compliant type
hints residing in those packages and modules such that those hints are both
types *and* uniquely identifiable by those types to their identifying signs).
'''


# The majority of this dictionary is initialized with automated inspection
# below in the _init() function. The *ONLY* key-value pairs explicitly defined
# here are those *NOT* amenable to such inspection.
HINT_MODULE_NAME_TO_TYPE_BASENAME_TO_SIGN: DictStrToDictStrToHintSign = {
    # ..................{ BUILTINS                           }..................
    # Standard builtins module.
    'builtins': {
        # ..................{ PEP 484                        }..................
        # PEP 484-compliant forward reference type hints may be annotated
        # either:
        # * Explicitly as "typing.ForwardRef" instances, which automated
        #   inspection performed by the _init() function below already handles.
        # * Implicitly as strings, which this key-value pair here detects. Note
        #   this unconditionally matches *ALL* strings, including both:
        #   * Invalid Python identifiers (e.g., "0d@yw@r3z").
        #   * Absolute forward references (i.e., fully-qualified classnames)
        #     technically non-compliant with PEP 484 but seemingly compliant
        #     with PEP 585.
        #
        #   Since the distinction between PEP-compliant and -noncompliant
        #   forward references is murky at best and since unconditionally
        #   matching *ALL* string as PEP-compliant substantially simplifies
        #   logic throughout the codebase, we (currently) opt to do so.
        'str': HintSignForwardRef,

        # The C-based "builtins.NoneType" type does *NOT* actually exist: e.g.,
        #     >>> from builtins import NoneType
        #     ImportError: cannot import name 'NoneType' from 'builtins'
        #     (unknown location)
        #
        # This implies that users *CANNOT* make user-defined instances of this
        # type, which then implies that the *ONLY* instance of this type is
        # guaranteed to be the PEP 484-compliant "None" singleton, which
        # circuitously reduces to "types.NoneType" under PEP 484.
        #
        # PEP 484 explicitly supports this singleton as follows:
        #     When used in a type hint, the expression None is considered
        #     equivalent to type(None).
        #
        # Note that the representation of the type of the "None" singleton
        # (i.e., "<class 'NoneType'>") is intentionally omitted here despite the
        # "None" singleton reducing to that type. Indeed, the *ONLY* reason we
        # detect this singleton at all is to enable that reduction. Although
        # this singleton conveys a PEP-compliant semantic, the type of this
        # singleton explicitly conveys *NO* PEP-compliant semantics. That type
        # is simply a standard isinstanceable type (like any other). Indeed,
        # attempting to erroneously associate the type of the "None" singleton
        # with the same sign here would cause that type to be detected as
        # conveying sign-specific PEP-compliant semantics rather than *NO* such
        # semantics, which would then substantially break and complicate dynamic
        # code generation for no benefit whatsoever.
        'NoneType': HintSignNone,
    },

    # ..................{ DATACLASSES                        }..................
    # Standard PEP 557-compliant dataclass module.
    'dataclasses': {
        # ..................{ PEP 557                        }..................
        # PEP 557-compliant "dataclasses.InitVar" type hints are merely
        # instances of that class.
        'InitVar': HintSignPep557DataclassInitVar,
    },

    # ..................{ TYPES                              }..................
    # Standard module containing common low-level C-based types.
    'types': {
        # ..................{ PEP 604                        }..................
        # PEP 604-compliant |-style unions (e.g., "int | float") are internally
        # implemented as instances of the low-level C-based "types.UnionType"
        # type. Thankfully, these unions are semantically interchangeable with
        # comparable PEP 484-compliant unions (e.g., "typing.Union[int,
        # float]"); both kinds expose equivalent dunder attributes (e.g.,
        # "__args__", "__parameters__"), enabling subsequent code generation to
        # conflate the two without issue.
        'UnionType': HintSignUnion,
    },

    # ..................{ TYPING                             }..................
    # Standard typing module.
    'typing': {
        # ..................{ PEP 484                        }..................
        # Python >= 3.10 implements PEP 484-compliant "typing.NewType" type
        # hints as instances of that pure-Python class.
        #
        # Note that we intentionally omit both "beartype.typing.NewType" *AND*
        # "typing_extensions.NewType" here, as:
        # * "beartype.typing.NewType" is a merely an alias of "typing.NewType".
        # * Regardless of the current Python version,
        #   "typing_extensions.NewType" type hints remain implemented in the
        #   manner of Python < 3.10 -- which is to say, as closures of that
        #   function. Ergo, . See also:
        #       https://github.com/python/typing/blob/master/typing_extensions/src_py3/typing_extensions.py
        'NewType': HintSignNewType,
    },

    # Third-party typing backports module, intentionally mapped here to the
    # empty dictionary to simplify logic in the _init() function called below.
    'typing_extensions': {},

    # Third-party @beartype typing module, intentionally mapped here to the
    # empty dictionary to simplify logic in the _init() function called below.
    'beartype.typing': {},
}
'''
**Type hint type trie** (i.e., dictionary-of-dictionaries tree data structure
mapping from the fully-qualified names of packages and modules to a nested
dictionary mapping from the unqualified basenames of the types of all
PEP-compliant type hints residing in those packages and modules that are
uniquely identifiable by those types to their identifying signs).
'''

# ....................{ SETS ~ deprecated                  }....................
# Initialized with automated inspection below in the _init() function.
HINTS_PEP484_REPR_PREFIX_DEPRECATED: FrozenSetStrs = set()  # type: ignore[assignment]
'''
Frozen set of all **bare deprecated** :pep:`484`-compliant **type hint
representations** (i.e., machine-readable strings returned by the :func:`repr`
builtin suffixed by *no* "["- and "]"-delimited subscription representations
for all :pep:`484`-compliant type hints obsoleted by :pep:`585`-compliant
subscriptable classes).
'''

# ....................{ INITIALIZERS                       }....................
def _init() -> None:
    '''
    Initialize this submodule.
    '''

    # ..................{ IMPORTS                            }..................
    # Defer initialization-specific imports.
    from beartype._data.api.standard.datamodtyping import TYPING_MODULE_NAMES
    from beartype._data.hint.pep.sign.datapepsigns import (
        HINT_SIGNS_TYPING,
        HintSignUnpack,
    )
    from beartype._util.py.utilpyversion import (
        IS_PYTHON_3_11,
    )

    # ..................{ GLOBALS                            }..................
    # Permit redefinition of these globals below.
    global HINTS_PEP484_REPR_PREFIX_DEPRECATED

    # ..................{ HINTS                              }..................
    # Length of the ignorable substring prefixing the name of each sign.
    _HINT_SIGN_PREFIX_LEN = len('HintSign')

    # ..................{ HINTS ~ repr                       }..................
    # Dictionary mapping from the unqualified names of typing attributes whose
    # names are erroneously desynchronized from their bare machine-readable
    # representations to the actual representations of those attributes.
    #
    # The unqualified names and representations of *MOST* typing attributes are
    # rigorously synchronized. However, those two strings are desynchronized
    # for a proper subset of Python versions and typing attributes:
    #     $ ipython3.8
    #     >>> import typing
    #     >>> repr(typing.List[str])
    #     typing.List[str]   # <-- this is good
    #     >>> repr(typing.ContextManager[str])
    #     typing.AbstractContextManager[str]   # <-- this is pants
    #
    # This dictionary enables subsequent logic to transparently resynchronize
    # the unqualified names and representations of pants typing attributes.
    _HINT_TYPING_ATTR_NAME_TO_REPR_PREFIX: Dict[str, str] = {}

    # If the active Python interpreter targets Python 3.11.x, identify PEP 646-
    # and 692-compliant hints that are instances of the private
    # "typing._UnpackGenericAlias" as "Unpack[...]" hints.
    #
    # Note that this fragile violation of privacy encapsulation is *ONLY* needed
    # under Python 3.11.x, where the machine-readable representation of unpacked
    # type variable tuples is ambiguously idiosyncratic and thus *NOT* a
    # reasonable heuristic for detecting such unpacking: e.g.,
    #     $ python3.11
    #     >>> from typing import TypeVarTuple
    #     >>> Ts = TypeVarTuple('Ts')
    #     >>> list_of_Ts = [*Ts]
    #     >>> repr(list_of_Ts[0])
    #     *Ts    # <-- ambiguous and thus a significant issue
    #
    #     $ python3.12
    #     >>> from typing import TypeVarTuple
    #     >>> Ts = TypeVarTuple('Ts')
    #     >>> list_of_Ts = [*Ts]
    #     >>> repr(list_of_Ts[0])
    #     typing.Unpack[Ts]    # <-- unambiguous and thus a non-issue
    if IS_PYTHON_3_11:
        HINT_MODULE_NAME_TO_TYPE_BASENAME_TO_SIGN[
            'typing']['_UnpackGenericAlias'] = HintSignUnpack
    # Else, the active Python interpreter does *NOT* target Python 3.11.x.

    # ..................{ HINTS ~ types                      }..................
    # Dictionary mapping from the unqualified names of all classes defined by
    # typing modules that are themselves valid PEP-compliant type hints to their
    # corresponding signs.
    _TYPING_ATTR_HINT_BASENAME_TO_SIGN = {
        # ................{ PEP 484                            }................
        # Unsubscripted "typing.Generic" superclass, which imposes no
        # constraints and is also semantically synonymous with the "object"
        # superclass. Since PEP 484 stipulates that *ANY* unsubscripted
        # subscriptable PEP-compliant type hint factories semantically expand to
        # those factories subscripted by an implicit "Any" argument, "Generic"
        # semantically expands to the implicit "Generic[Any]" singleton.
        'Generic': HintSignPep484585GenericUnsubscripted,

        # ....................{ PEP 544                    }....................
        # Unsubscripted "typing.Protocol" superclass. For unknown and presumably
        # uninteresting reasons, *ALL* possible objects satisfy this superclass.
        # Ergo, this superclass is synonymous with the "object" root superclass:
        #     >>> from typing import Protocol
        #     >>> isinstance(object(), Protocol)
        #     True
        #     >>> isinstance('wtfbro', Protocol)
        #     True
        #     >>> isinstance(0x696969, Protocol)
        #     True
        'Protocol': HintSignProtocol,
    }

    # Dictionary mapping from the unqualified names of all classes defined by
    # typing modules used to instantiate PEP-compliant type hints to their
    # corresponding signs.
    _TYPING_ATTR_TYPE_BASENAME_TO_SIGN = {
        # ....................{ PEP 484                    }....................
        # All PEP 484-compliant forward references are necessarily instances of
        # the same class.
        'ForwardRef' : HintSignForwardRef,

        # All PEP 484-compliant type variables are necessarily instances of the
        # same class.
        'TypeVar': HintSignTypeVar,

        #FIXME: "Generic" is ignorable when unsubscripted. Excise this up!
        # The unsubscripted PEP 484-compliant "Generic" superclass is
        # explicitly equivalent under PEP 484 to the "Generic[Any]"
        # subscription and thus slightly conveys meaningful semantics.
        # 'Generic': HintSignPep484585GenericUnsubscripted,

        # ....................{ PEP 612                    }....................
        # PEP 612-compliant "typing.ParamSpec" type hints as merely instances of
        # that low-level C-based type.
        'ParamSpec': HintSignParamSpec,

        # PEP 612-compliant "*args: P.args" type hints as merely instances of
        # the low-level C-based "typing.ParamSpecArgs" type.
        'ParamSpecArgs': HintSignParamSpecArgs,

        # PEP 612-compliant "**kwargs: P.kwargs" type hints as merely instances
        # of the low-level C-based "typing.ParamSpecKwargs" type.
        'ParamSpecKwargs': HintSignParamSpecKwargs,

        # ....................{ PEP 646                    }....................
        # All PEP 646-compliant type variable tuples are necessarily instances
        # of the same class.
        'TypeVarTuple': HintSignTypeVarTuple,

        # ....................{ PEP 695                    }....................
        # PEP 695-compliant "type" aliases are merely instances of the low-level
        # C-based "typing.TypeAliasType" type.
        'TypeAliasType': HintSignPep695TypeAliasUnsubscripted,
    }

    # ..................{ HINTS ~ deprecated                 }..................
    # Set of the unqualified names of all deprecated PEP 484-compliant typing
    # attributes.
    _HINT_PEP484_TYPING_ATTR_BASENAMES_DEPRECATED: Set[str] = {
        # ..................{ PEP ~ 484                      }..................
        # Unqualified basenames of all deprecated PEP 484-compliant
        # typing attributes (e.g., "typing.List") that have since been obsoleted
        # by equivalent bare PEP 585-compliant builtin classes (e.g., "list").
        'AbstractSet',
        'AsyncContextManager',
        'AsyncGenerator',
        'AsyncIterable',
        'AsyncIterator',
        'Awaitable',
        'ByteString',
        'Callable',
        'ChainMap',
        'Collection',
        'Container',
        'ContextManager',
        'Coroutine',
        'Counter',
        'DefaultDict',
        'Deque',
        'Dict',
        'FrozenSet',
        'Generator',
        'Hashable',
        'ItemsView',
        'Iterable',
        'Iterator',
        'KeysView',
        'List',
        'MappingView',
        'Mapping',
        'Match',
        'MutableMapping',
        'MutableSequence',
        'MutableSet',
        'OrderedDict',
        'Pattern',
        'Reversible',
        'Sequence',
        'Set',
        'Sized',
        'Tuple',
        'Type',
        'ValuesView',
    }

    # ..................{ HINTS ~ ignorable                  }..................
    #FIXME: *CURRENTLY UNUSED.* That said, this should be used... somehow.
    # # Set of the unqualified names of all shallowly ignorable typing non-class
    # # attributes. Since classes and non-class attributes have incommensurate
    # # machine-readable representations, these two types of attributes *MUST* be
    # # isolated to distinct sets. See "_HINT_TYPING_TYPE_NAMES_IGNORABLE" below.
    # _HINT_TYPING_ATTR_NAMES_IGNORABLE = {
    #     # ................{ PEP 484                            }................
    #     # The "Any" singleton is semantically synonymous with the ignorable
    #     # PEP-noncompliant "beartype.cave.AnyType" and hence "object" types.
    #     #
    #     # Note that the "typing_extensions.Any" singleton is inexplicably a
    #     # different object than the "typing.Any" singleton. WHYYYYYYYYYYY!?!?
    #     'Any',
    #
    #     # The unsubscripted "Optional" singleton semantically expands to the
    #     # implicit "Optional[Any]" singleton by the same argument. Since PEP
    #     # 484 also stipulates that all "Optional[t]" singletons semantically
    #     # expand to "Union[t, type(None)]" singletons for arbitrary arguments
    #     # "t", "Optional[Any]" semantically expands to merely "Union[Any,
    #     # type(None)]". Since all unions subscripted by "Any" semantically
    #     # reduce to merely "Any", the "Optional" singleton also reduces to
    #     # merely "Any".
    #     #
    #     # This intentionally excludes "Optional[type(None)]", which the
    #     # "typing" module physically reduces to merely "type(None)". *shrug*
    #     'Optional',
    #
    #     # The unsubscripted "Union" singleton semantically expands to the
    #     # implicit "Union[Any]" singleton by the same argument. Since PEP 484
    #     # stipulates that a union of one type semantically reduces to only that
    #     # type, "Union[Any]" semantically reduces to merely "Any". Despite
    #     # their semantic equivalency, however, these objects remain
    #     # syntactically distinct with respect to object identification: e.g.,
    #     #     >>> Union is not Union[Any]
    #     #     True
    #     #     >>> Union is not Any
    #     #     True
    #     #
    #     # This intentionally excludes:
    #     # * The "Union[Any]" and "Union[object]" singletons, since the "typing"
    #     #   module physically reduces:
    #     #   * "Union[Any]" to merely "Any" (i.e., "Union[Any] is Any"), which
    #     #     this frozen set already contains.
    #     #   * "Union[object]" to merely "object" (i.e., "Union[object] is
    #     #     object"), which this frozen set also already contains.
    #     # * "Union" singleton subscripted by one or more ignorable type hints
    #     #   contained in this set (e.g., "Union[Any, bool, str]"). Since there
    #     #   exist a countably infinite number of these subscriptions, these
    #     #   subscriptions *CANNOT* be explicitly listed in this set. Instead,
    #     #   these subscriptions are dynamically detected by the high-level
    #     #   beartype._util.hint.pep.utilhinttest.is_hint_ignorable() tester
    #     #   function and thus referred to as deeply ignorable type hints.
    #     'Union',
    # }

    # ..................{ INITIALIZATION                     }..................
    # For the fully-qualified name of each quasi-standard typing module...
    for typing_module_name in TYPING_MODULE_NAMES:
        # For the unqualified basename of each type hint that is itself a type
        # identifiable by a sign to that sign, map from the fully-qualified name
        # of that type in this module to this sign.
        for hint_basename, hint_sign in (
            _TYPING_ATTR_HINT_BASENAME_TO_SIGN.items()):
            # print(f'[datapeprepr] Mapping hint "{typing_module_name}.{typing_attr_basename}" -> {hint_sign}')
            HINT_MODULE_NAME_TO_HINT_BASENAME_TO_SIGN[
                typing_module_name][hint_basename] = hint_sign

        # For the unqualified basename of each type of each type hint
        # identifiable by a sign to that sign, map from the fully-qualified name
        # of that type in this module to this sign.
        for type_basename, hint_sign in (
            _TYPING_ATTR_TYPE_BASENAME_TO_SIGN.items()):
            # print(f'[datapeprepr] Mapping type "{typing_module_name}.{typing_attr_basename}" -> {hint_sign}')
            HINT_MODULE_NAME_TO_TYPE_BASENAME_TO_SIGN[
                typing_module_name][type_basename] = hint_sign

        # For each deprecated PEP 484-compliant typing attribute name,
        # add that attribute relative to this module to this set.
        for typing_attr_basename in (
            _HINT_PEP484_TYPING_ATTR_BASENAMES_DEPRECATED):
            # print(f'[datapeprepr] Registering deprecated "{typing_module_name}.{typing_attr_basename}"...')
            HINTS_PEP484_REPR_PREFIX_DEPRECATED.add(  # type: ignore[attr-defined]
                f'{typing_module_name}.{typing_attr_basename}')

        # For the name of each typing sign (i.e., identifying *ALL* standard
        # PEP-compliant "typing" type hints and type hint factories available in
        # the most recent stable CPython release)...
        for hint_sign_typing in HINT_SIGNS_TYPING:
            # Unqualified basename of the typing attribute uniquely identified
            # by this sign.
            typing_attr_basename = hint_sign_typing.name

            # Substring prefixing the machine-readable representation of this
            # attribute, conditionally defined as either:
            # * If this name is erroneously desynchronized from this
            #   representation under the active Python interpreter, the actual
            #   representation of this attribute under this interpreter (e.g.,
            #   "AbstractContextManager" for the "typing.ContextManager" hint).
            # * Else, this name is correctly synchronized with this
            #   representation under the active Python interpreter. In this
            #   case, fallback to this name as is (e.g., "List" for the
            #   "typing.List" hint).
            hint_repr_prefix = _HINT_TYPING_ATTR_NAME_TO_REPR_PREFIX.get(
                typing_attr_basename, typing_attr_basename)

            #FIXME: It'd be great to eventually generalize this to support
            #aliases from one unwanted sign to another wanted sign. Perhaps
            #something resembling:
            ## In global scope above:
            #_HINT_SIGN_REPLACE_SOURCE_BY_TARGET = {
            #    HintSignProtocol: HintSignPep484585GenericUnsubscripted,
            #}
            #
            #    # In this iteration here:
            #    ...
            #    hint_sign_replaced = _HINT_SIGN_REPLACE_SOURCE_BY_TARGET.get(
            #        hint_sign, hint_sign)
            #
            #    # Map from that attribute in this module to this sign.
            #    # print(f'[datapeprepr] Mapping repr("{typing_module_name}.{hint_repr_prefix}[...]") -> {repr(hint_sign)}...')
            #    HINT_REPR_PREFIX_ARGS_0_OR_MORE_TO_SIGN[
            #        f'{typing_module_name}.{hint_repr_prefix}'] = hint_sign_replaced
            # print(f'[datapeprepr] Mapping repr("{typing_module_name}.{hint_repr_prefix}[...]") -> {repr(hint_sign)}...')

            # Map from that attribute in this module to this sign.
            HINT_REPR_PREFIX_ARGS_0_OR_MORE_TO_SIGN[
                f'{typing_module_name}.{hint_repr_prefix}'] = hint_sign_typing

    # ..................{ SYNTHESIS                          }..................
    # Freeze all relevant global sets for safety.
    HINTS_PEP484_REPR_PREFIX_DEPRECATED = frozenset(
        HINTS_PEP484_REPR_PREFIX_DEPRECATED)

    # ..................{ DEBUGGING                          }..................
    # Uncomment as needed to display the contents of these objects.

    # from pprint import pformat
    # print(f'HINTS_PEP484_REPR_PREFIX_DEPRECATED: {pformat(HINTS_PEP484_REPR_PREFIX_DEPRECATED)}')
    # print(f'HINT_REPR_PREFIX_ARGS_0_OR_MORE_TO_SIGN: {pformat(HINT_REPR_PREFIX_ARGS_0_OR_MORE_TO_SIGN)}')
    # print(f'HINT_REPR_PREFIX_ARGS_1_OR_MORE_TO_SIGN: {pformat(HINT_REPR_PREFIX_ARGS_1_OR_MORE_TO_SIGN)}')
    # print(f'HINT_MODULE_NAME_TO_TYPE_BASENAME_TO_SIGN: {pformat(HINT_MODULE_NAME_TO_TYPE_BASENAME_TO_SIGN)}')


# Initialize this submodule.
_init()
