#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype **Decidedly Object-Oriented Runtime-checking (DOOR) type hint inference
fixtures** (i.e., :mod:`pytest`-specific context managers passed as parameters
to unit tests exercising the :mod:`beartype.door.infer_hint` function).
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from pytest import fixture

# ....................{ FIXTURES                           }....................
@fixture(scope='session')
def door_cases_infer_hint() -> (
    'Dict[beartype.BeartypeConf, Iterable[Tuple[object, object]]]'):
    '''
    Session-scoped fixture returning a dictionary mapping from each relevant
    beartype configuration to a corresponding iterable of all **type hint
    inference cases** specific to that configuration, efficiently cached across
    all tests requiring this fixture.

    This container is intentionally defined by the return of this fixture rather
    than as a global constant of this submodule. Why? Because the former safely
    defers all heavyweight imports required to define this container to the call
    of the first unit test requiring this fixture, whereas the latter unsafely
    performs those imports at pytest test collection time.

    Returns
    -------
    Dict[beartype.BeartypeConf, Iterable[Tuple[object, object]]]
        Dictionary mapping from each relevant beartype configuration to a
        corresponding iterable of all **type hint inference cases** specific to
        that configuration, where each type hint inference case is a 2-tuple
        ``(obj, hint)`` describing the type hint matching an arbitrary object
        as follows:

        * ``obj`` is an arbitrary object to be passed as the first parameter to
          the :func:`beartype.door.infer_hint` function.
        * ``hint`` is the type hint returned by that function when passed that
          object.
    '''

    # ..................{ IMPORTS                            }..................
    # Defer fixture-specific imports.
    from beartype import (
        BeartypeConf,
        BeartypeStrategy,
    )
    from beartype.typing import (
        Annotated,
        Callable,
        Collection,
        Container,
        Counter,
        Deque,
        Dict,
        FrozenSet,
        KeysView,
        List,
        Mapping,
        MutableMapping,
        MutableSequence,
        Sequence,
        Set,
        Sized,
        Tuple,
        Type,
        Union,
        ValuesView,
    )
    from beartype.vale import IsInstance
    from beartype._util.py.utilpyversion import (
        IS_PYTHON_AT_LEAST_3_11,
        IS_PYTHON_AT_LEAST_3_10,
    )
    from beartype_test.a00_unit.data.data_type import (
        Class,
        ClassCollection,
        ClassContainer,
        ClassDict,
        ClassList,
        ClassMapping,
        ClassMappingSequence,
        ClassMutableMapping,
        ClassMutableSequence,
        ClassSequence,
        ClassSized,
    )
    from beartype_test.a00_unit.data.func.data_func import (
        func_argless_return_unhinted,
        func_argless_return_hinted,
        func_args_unhinted_return_unhinted,
        func_args_flex_mandatory_kwonly_mandatory_hinted_return_hinted,
        func_args_flex_mandatory_optional_hinted_return_unhinted,
        func_args_flex_mandatory_varkw_hinted_return_hinted,
        func_args_flex_mandatory_varpos_hinted_return_hinted,
        func_args_unhinted_return_hinted,
    )
    from beartype_test._util.module.pytmodtyping import (
        import_typing_attr_or_none_safe)
    from collections import (
        Counter as CounterType,
        deque,
    )

    # ..................{ LOCALS ~ hint                      }..................
    # PEP 612-compliant "Concatenate" type hint factory and "ParamSpec" class
    # imported from either the standard "typing" or third-party
    # "typing_extensions" modules if importable from at least one of those
    # modules *OR* "None" otherwise.
    Concatenate = import_typing_attr_or_none_safe('Concatenate')
    ParamSpec = import_typing_attr_or_none_safe('ParamSpec')

    # ..................{ LOCALS ~ O(1)                      }..................
    # List of all type hint inference cases (i.e., 2-tuples "(obj, hint)"
    # describing the type hint matching an arbitrary object) specific to O(1)
    # constant-time type hint inference. Since this strategy achieves O(1)
    # constant time by inferring type hints pseudo-randomly, this list should
    # *ONLY* contain containers whose items are all of the same types.
    CASES_STRATEGY_O1 = [
        # ..................{ NON-PEP                        }..................
        # Builtin scalars are annotated as the builtin types of those scalars.
        ('Of his frail exultation shall be spent', str),
        (b'Mingling its solemn song, whilst the broad river', bytes),
        (True, bool),
        (73, int),
        (94.0251, float),

        # An instance of a PEP-noncompliant class (i.e., a class *NOT* covered
        # by an existing PEP standard) satisfying no broader type hint is
        # annotated simply as that class.
        (Class(), Class),

        # ..................{ PEP                            }..................
        # Any arbitrary type hint is annotated as itself.
        (Union[int, List[bytes]], Union[int, List[bytes]]),

        # ..................{ PEP 484                        }..................
        # The "None" singleton is annotated as itself under PEP 484.
        (None, None),

        # ..................{ PEP [484|585]                  }..................
        # A class is annotated as the PEP 484- or 585-compliant "type" supertype
        # subscripted by that class.
        (Class, Type[Class]),

        # ..................{ PEP [484|585] ~ abc            }..................
        # An instance of a PEP-noncompliant class (i.e., a class *NOT* covered
        # by an existing PEP standard) satisfying a standard "collections.abc"
        # protocol is annotated as the narrowest such protocol. Moreover, for
        # each instance that is a container (i.e., satisfies the standard
        # "collections.abc.Container" protocol), that annotation is subscripted
        # by a child type hint annotating the items of that container.

        # "collections.abc.MutableMapping" protocol hierarchy.
        (
            ClassMapping({
                'Branchless and blasted,': b'clenched with grasping roots',
                'The unwilling soil.': b'A gradual change was here,',
            }),
            # The narrowest "collections.abc" protocol matching this object
            # annotated to require an instance of this object's type.
            Annotated[Mapping[str, bytes], IsInstance[ClassMapping]],
        ),
        (
            ClassMutableMapping({
                b'Yet ghastly.': 'For, as fast years flow away,',
                b'The smooth brow gathers,': 'and the hair grows thin',
            }),
            # The narrowest "collections.abc" protocol matching this object
            # annotated to require an instance of this object's type.
            Annotated[
                MutableMapping[bytes, str], IsInstance[ClassMutableMapping]],
        ),

        # "collections.abc.MutableSequence" protocol hierarchy.
        (
            ClassContainer([
                b'Beneath the shade of trees', b'beside the flow']),
            # The narrowest "collections.abc" protocol matching this object
            # annotated to require an instance of this object's type.
            Annotated[Container, IsInstance[ClassContainer]],
        ),
        (
            ClassCollection([
                'Of the wild babbling rivulet;', 'and now']),
            # The narrowest "collections.abc" protocol matching this object
            # annotated to require an instance of this object's type.
            Annotated[Collection[str], IsInstance[ClassCollection]],
        ),
        (
            ClassSequence([
                b'He must descend.', b'With rapid steps he went']),
            # The narrowest "collections.abc" protocol matching this object
            # annotated to require an instance of this object's type.
            Annotated[Sequence[bytes], IsInstance[ClassSequence]],
        ),
        (
            ClassMutableSequence([
                'Forgetful of the grave', 'where', 'when the flame']),
            # The narrowest "collections.abc" protocol matching this object
            # annotated to require an instance of this object's type.
            Annotated[
                MutableSequence[str], IsInstance[ClassMutableSequence]],
        ),
        # Object satisfying both the "collections.abc.Mapping" *AND*
        # "collections.abc.Sequence" protocols, exercising various edge cases
        # with respect to protocol overlap and ambiguity.
        (
            ClassMappingSequence([
                b'And white,', b'and where irradiate dewy eyes',]),
            # The narrowest "collections.abc" protocol matching this object
            # annotated to require an instance of this object's type.
            Annotated[Sequence[bytes], IsInstance[ClassMappingSequence]],
        ),

        # "collections.abc.Sized" protocol.
        (
            ClassSized("The forest's solemn canopies were changed"),
            # The narrowest "collections.abc" protocol matching this object
            # annotated to require an instance of this object's type.
            Annotated[Sized, IsInstance[ClassSized]],
        ),

        # ..................{ PEP [484|585] ~ callable       }..................
        #FIXME: Additionally test:
        #* A pure-Python function isomorphically wrapping another function.
        #* A pure-Python function non-isomorphically wrapping another function.

        # A C-based callable is annotated as the unsubscripted PEP 484- or
        # 585-compliant "Callable" type.
        (
            iter,
            Callable,
        ),

        # A pure-Python callable annotated by *NO* return type hint accepting
        # *NO* parameters is annotated as the PEP 484- or 585-compliant
        # "Callable" type subscripted by the empty list followed by the
        # ignorable "object" superclass.
        (
            func_argless_return_unhinted,
            Callable[[], object],
        ),

        # A pure-Python callable annotated by a return type hint accepting *NO*
        # parameters is annotated as the PEP 484- or 585-compliant "Callable"
        # type subscripted by the empty list followed by that hint.
        (
            func_argless_return_hinted,
            Callable[[], str],
        ),

        # An unannotated pure-Python callable is annotated as the PEP 484- or
        # 585-compliant "Callable" type subscripted by either...
        (
            func_args_unhinted_return_unhinted,
            (
                # If the active Python interpreter targets Python >= 3.11 and
                # thus supports PEP 612:
                # * The PEP 612-compliant "typing(|_extensions).Concatenate"
                #   hint factory subscripted by one "object" child type hint for
                #   each mandatory positional-only or flexible parameter
                #   accepted by that callable followed by a trailing ellipsis.
                # * The ignorable "object" superclass, matching the return.
                Callable[Concatenate[object, object, ...], object]
                if IS_PYTHON_AT_LEAST_3_11 else
                # Else, the active Python interpreter targets Python < 3.11 and
                # thus fails to support PEP 612. In this case, the unsubscripted
                # PEP 484- or 585-compliant "Callable" type.
                Callable
            )
        ),

        # A pure-Python callable annotated by a return type hint and *NO*
        # parameter type hints is annotated as the PEP 484- or 585-compliant
        # "Callable" type subscripted by either...
        (
            func_args_unhinted_return_hinted,
            (
                # If the active Python interpreter targets Python >= 3.11 and
                # thus supports PEP 612:
                # * The PEP 612-compliant "typing(|_extensions).Concatenate"
                #   hint factory subscripted by one "object" child type hint for
                #   each mandatory positional-only or flexible parameter
                #   accepted by that callable followed by a trailing ellipsis.
                # * That return type hint.
                Callable[Concatenate[object, object, ...], str]
                if IS_PYTHON_AT_LEAST_3_11 else
                # Else, the active Python interpreter targets Python < 3.11 and
                # thus fails to support PEP 612. In this case, an ellipsis
                # followed by that return type hint.
                Callable[..., str]
            )
        ),

        # A pure-Python callable annotated by *NO* return type hint and one or
        # more mandatory and optional flexible parameter type hints is annotated
        # as the PEP 484- or 585-compliant "Callable" type subscripted by
        # either...
        (
            func_args_flex_mandatory_optional_hinted_return_unhinted,
            (
                # If the active Python interpreter targets Python >= 3.11 and
                # thus supports PEP 612:
                # * The PEP 612-compliant "typing(|_extensions).Concatenate"
                #   hint factory subscripted by these mandatory parameter type
                #   hints followed by a trailing ellipsis.
                # * The ignorable "object" superclass, matching the return.
                Callable[Concatenate[int, bytes, ...], object]
                if IS_PYTHON_AT_LEAST_3_11 else
                # Else, the active Python interpreter targets Python < 3.11 and
                # thus fails to support PEP 612. In this case, the unsubscripted
                # PEP 484- or 585-compliant "Callable" type.
                Callable
            )
        ),

        # A pure-Python callable annotated by a return type hint and one or
        # more mandatory flexible parameter type hints and a variadic positional
        # parameter type hint is annotated as the PEP 484- or 585-compliant
        # "Callable" type subscripted by either...
        (
            func_args_flex_mandatory_varpos_hinted_return_hinted,
            (
                # If the active Python interpreter targets Python >= 3.11 and
                # thus supports PEP 612:
                # * The PEP 612-compliant "typing(|_extensions).Concatenate"
                #   hint factory subscripted by these mandatory parameter type
                #   hints followed by a trailing ellipsis.
                # * That return type hint.
                Callable[Concatenate[bool, float, ...], str]
                if IS_PYTHON_AT_LEAST_3_11 else
                # Else, the active Python interpreter targets Python < 3.11 and
                # thus fails to support PEP 612. In this case, the PEP 484- or
                # 585-compliant "Callable" type subscripted by an ellipsis and
                # that return type hint.
                Callable[..., str]
            )
        ),

        # A pure-Python callable annotated by a return type hint and one or
        # more mandatory flexible parameter type hints and a variadic keyword
        # parameter type hint is annotated as the PEP 484- or 585-compliant
        # "Callable" type subscripted by either...
        (
            func_args_flex_mandatory_varkw_hinted_return_hinted,
            (
                # If the active Python interpreter targets Python >= 3.11 and
                # thus supports PEP 612:
                # * The PEP 612-compliant "typing(|_extensions).Concatenate"
                #   hint factory subscripted by these mandatory parameter type
                #   hints followed by a trailing ellipsis.
                # * That return type hint.
                Callable[Concatenate[str, int, ...], bytes]
                if IS_PYTHON_AT_LEAST_3_11 else
                # Else, the active Python interpreter targets Python < 3.11 and
                # thus fails to support PEP 612. In this case, the PEP 484- or
                # 585-compliant "Callable" type subscripted by an ellipsis and
                # that return type hint.
                Callable[..., bytes]
            )
        ),

        # A pure-Python callable annotated by a return type hint and one or
        # more mandatory flexible parameter type hints and a mandatory
        # keyword-only parameter type hint is annotated as the PEP 484- or
        # 585-compliant "Callable" type subscripted by either...
        (
            func_args_flex_mandatory_kwonly_mandatory_hinted_return_hinted,
            (
                # If the active Python interpreter targets Python >= 3.11 and
                # thus supports PEP 612:
                # * The PEP 612-compliant "typing(|_extensions).Concatenate"
                #   hint factory subscripted by these mandatory parameter type
                #   hints followed by a trailing ellipsis.
                # * That return type hint.
                Callable[Concatenate[float, int, ...], bytes]
                if IS_PYTHON_AT_LEAST_3_11 else
                # Else, the active Python interpreter targets Python < 3.11 and
                # thus fails to support PEP 612. In this case, the PEP 484- or
                # 585-compliant "Callable" type subscripted by an ellipsis and
                # that return type hint.
                Callable[..., bytes]
            )
        ),

        # ..................{ PEP [484|585] ~ counter        }..................
        # A counter of items all of the same class is annotated as the PEP 484-
        # or 585-compliant "Counter" type subscripted by that class.
        (
            CounterType({
                'For the uniform and': 27, 'lightsome evening sky.': 89,}),
            Counter[str],
        ),

        # ..................{ PEP [484|585] ~ deque          }..................
        # A deque of items all of the same class is annotated as the PEP 484- or
        # 585-compliant "deque" type subscripted by that class.
        (
            deque(('On the green moss his tremulous step,', 'that caught',)),
            Deque[str],
        ),

        # ..................{ PEP [484|585] ~ dict           }..................
        #FIXME: Validate that all other empty data structures behave as
        #expected, please. *sigh*

        # The empty dictionary is annotated as the unsubscripted PEP 484- or
        # 585-compliant "dict" type.
        (
            {},
            Dict,
        ),

        # A dictionary of one item is annotated as the PEP 484- or 585-compliant
        # "dict" type subscripted by the classes of that item.
        (
            {'In wanton sport, those bright leaves,': b'whose decay,',},
            Dict[str, bytes],
        ),

        # A dictionary of two or more items all of the same class is annotated
        # as the PEP 484- or 585-compliant "dict" type subscripted by that
        # class.
        (
            {b'Grey rocks': 'did peep from', b'the spare moss,': 'and stemmed'},
            Dict[bytes, str],
        ),

        # ..................{ PEP [484|585] ~ frozenset      }..................
        # A frozen set of items all of the same class is annotated as the PEP
        # 484- or 585-compliant "frozenset" type subscripted by that class.
        (
            frozenset({"I' the passing wind!", 'Beside the grassy shore',}),
            FrozenSet[str],
        ),

        # ..................{ PEP [484|585] ~ keysview       }..................
        # A keys view of keys all of the same class is annotated as the PEP 484-
        # or 585-compliant "KeysView" type subscripted by that class.
        ({
            b'What oozy cavern': 'or what wandering cloud expose',
            b'Contains thy waters,': 'as the universe',
        }.keys(), KeysView[bytes]),

        # ..................{ PEP [484|585] ~ list           }..................
        # An empty list is annotated as the unsubscripted PEP 484- or
        # 585-compliant "list" type hint factory.
        ([], List),

        # A list of items all of the same type is annotated as the PEP 484- or
        # 585-compliant "list" type subscripted by that type.
        (['expose', 'extreme', 'explosions!',], List[str]),

        # ..................{ PEP [484|585] ~ set            }..................
        # A set of items all of the same class is annotated as the PEP 484- or
        # 585-compliant "set" type subscripted by that class.
        ({'Of the small stream he went;', 'he did impress',}, Set[str]),

        # ..................{ PEP [484|585] ~ tuple          }..................
        # A subjectively small root tuple (i.e., tuple *NOT* contained in a
        # larger container and containing a fairly small number of items) is
        # annotated as the fixed-length PEP 484- and 585-compliant "tuple" type
        # iteratively subscripted by type hints matching the types of all items.
        (
            ('Foaming and hurrying o', b'er its rugged path', 94, 4.3618,),
            Tuple[str, bytes, int, float],
        ),

        # A subjectively large root tuple (i.e., tuple *NOT* contained in a
        # larger container but containing a fairly large number of items all of
        # the same type) is annotated as the variadic PEP 484- and
        # 585-compliant "tuple" type subscripted by that type.
        (
            (
                'The wilds to love tranquillity. One step,'
                'One human step alone, has ever broken',
                'The stillness of its solitude:—one voice',
                'Alone inspired its echoes;—even that voice',
            ) * 4,
            Tuple[str, ...]
        ),

        # ..................{ PEP [484|585] ~ valuesview     }..................
        # A values view of values all of the same class is annotated as the PEP
        # 484- or 585-compliant "ValuesView" type subscripted by that class.
        ({
            'Tell where these living thoughts reside,': b'when stretched',
            'Upon thy flowers': b'my bloodless limbs shall waste',
        }.values(), ValuesView[bytes]),

        # ..................{ PEP 585 ~ builtin              }..................
        # An instance of a user-defined class subclassing a PEP 585-compliant
        # builtin collection type (e.g., "dict", "list") is annotated as that
        # user-defined class subscripted by a child type hint annotating the
        # items of that collection.

        # A user-defined dictionary of keys all of the same class and values all
        # of another class is annotated as the PEP 585-compliant "dict" type
        # sequentially subscripted by those classes.
        (
            ClassDict({
                b'Threw their thin shadows': 'down the rugged slope',
                b'And nought but': 'gnarlèd roots of ancient pines',
            }),
            # This user-defined dictionary subscripted by these child key and
            # value type hints.
            ClassDict[bytes, str],
        ),

        # A user-defined list of items all of the same class is annotated as the
        # PEP 585-compliant "list" type subscripted by that class.
        (
            ClassList((
                b'The struggling brook:', b'tall spires of windlestrae',)),
            # This user-defined list subscripted by this child type hint.
            ClassList[bytes],
        ),
    ]

    # ..................{ VERSIONS                           }..................
    # If the PEP 612-compliant "ParamSpec" class is importable from either the
    # standard "typing" or third-party "typing_extensions" modules...
    if ParamSpec is not None:
        # Defer attribute-specific imports.
        from beartype_test.a00_unit.data.func.data_pep612 import (
            P,
            func_args_flex_mandatory_kwonly_optional_paramspec_return_hinted,
            func_args_flex_mandatory_paramspec_distinct_return_hinted,
            func_args_flex_mandatory_paramspec_return_hinted,
            func_args_flex_mandatory_paramspec_varkwonly_return_hinted,
            func_args_flex_mandatory_paramspec_varposonly_return_hinted,
            func_args_paramspec_return_hinted,
        )

        # Extend this list with "ParamSpec"-specific cases.
        CASES_STRATEGY_O1.extend((
            # ..................{ PEP 612                    }..................
            # A pure-Python callable annotated by a return type hint accepting
            # variadic positional and keyword parameters annotated as the
            # corresponding instance variables of a PEP 612-compliant parameter
            # specification is annotated as the PEP 484- or 585-compliant
            # "Callable" type subscripted by that parameter specification
            # followed by that return type hint.
            (
                func_args_paramspec_return_hinted,
                Callable[P, bytes],
            ),

            # A pure-Python callable annotated by a return type hint accepting
            # one or more mandatory flexible parameter type hints *AND* variadic
            # positional and keyword parameters annotated as the corresponding
            # instance variables of a PEP 612-compliant parameter specification
            # is annotated as the PEP 484- or 585-compliant "Callable" type
            # subscripted by:
            # * The PEP 612-compliant "typing(|_extensions).Concatenate" hint
            #   factory subscripted by these mandatory parameter type hints
            #   followed by that parameter specification.
            # * That return type hint.
            (
                func_args_flex_mandatory_paramspec_return_hinted,
                Callable[Concatenate[int, bool, P], str],
            ),

            # A pure-Python callable annotated by a return type hint accepting
            # one or more mandatory flexible parameter type hints and a variadic
            # positional parameter annotated as the corresponding instance
            # variables of a PEP 612-compliant parameter specification with *NO*
            # variadic keyword parameter is annotated as either...
            (
                func_args_flex_mandatory_paramspec_varposonly_return_hinted,
                (
                    # If the active Python interpreter targets Python >= 3.11
                    # and thus supports PEP 612, the PEP 484- or 585-compliant
                    # "Callable" type subscripted by:
                    # * The PEP 612-compliant "typing(|_extensions).Concatenate"
                    #   hint factory subscripted by these mandatory parameter
                    #   type hints followed by an ellipsis.
                    # * That return type hint.
                    Callable[Concatenate[int, float, ...], bytes]
                    if IS_PYTHON_AT_LEAST_3_11 else
                    # Else, the active Python interpreter targets Python < 3.11
                    # and thus fails to support PEP 612. In this case, the PEP
                    # 484- or 585-compliant "Callable" type subscripted by an
                    # ellipsis and that return type hint.
                    Callable[..., bytes]
                ),
            ),

            # A pure-Python callable annotated by a return type hint accepting
            # one or more mandatory flexible parameter type hints and a variadic
            # keyword parameter annotated as the corresponding instance
            # variables of a PEP 612-compliant parameter specification with *NO*
            # variadic positional parameter is annotated as either...
            (
                func_args_flex_mandatory_paramspec_varkwonly_return_hinted,
                (
                    # If the active Python interpreter targets Python >= 3.11
                    # and thus supports PEP 612, the PEP 484- or 585-compliant
                    # "Callable" type subscripted by:
                    # * The PEP 612-compliant "typing(|_extensions).Concatenate"
                    #   hint factory subscripted by these mandatory parameter
                    #   type hints followed by an ellipsis.
                    # * That return type hint.
                    Callable[Concatenate[bool, bytes, ...], str]
                    if IS_PYTHON_AT_LEAST_3_11 else
                    # Else, the active Python interpreter targets Python < 3.11
                    # and thus fails to support PEP 612. In this case, the PEP
                    # 484- or 585-compliant "Callable" type subscripted by an
                    # ellipsis and that return type hint.
                    Callable[..., str]
                ),
            ),

            # A pure-Python callable annotated by a return type hint accepting
            # one or more mandatory flexible parameter type hints, a variadic
            # positional parameter annotated as the corresponding instance
            # variables of a PEP 612-compliant parameter specification, and a
            # variadic keyword parameter annotated as the corresponding instance
            # variables of a different parameter specification is annotated as
            # either...
            (
                func_args_flex_mandatory_paramspec_distinct_return_hinted,
                (
                    # If the active Python interpreter targets Python >= 3.11
                    # and thus supports PEP 612, the PEP 484- or 585-compliant
                    # "Callable" type subscripted by:
                    # * The PEP 612-compliant "typing(|_extensions).Concatenate"
                    #   hint factory subscripted by these mandatory parameter
                    #   type hints followed by an ellipsis.
                    # * That return type hint.
                    Callable[Concatenate[float, int, ...], bytes]
                    if IS_PYTHON_AT_LEAST_3_11 else
                    # Else, the active Python interpreter targets Python < 3.11
                    # and thus fails to support PEP 612. In this case, the PEP
                    # 484- or 585-compliant "Callable" type subscripted by an
                    # ellipsis and that return type hint.
                    Callable[..., bytes]
                ),
            ),

            # A pure-Python callable annotated by a return type hint accepting
            # one or more mandatory flexible parameter type hints, an optional
            # flexible parameter type hint, *AND* variadic positional and
            # keyword parameters annotated as the corresponding instance
            # variables of a PEP 612-compliant parameter specification is
            # annotated as either...
            (
                func_args_flex_mandatory_kwonly_optional_paramspec_return_hinted,
                (
                    # If the active Python interpreter targets Python >= 3.11
                    # and thus supports PEP 612, the PEP 484- or 585-compliant
                    # "Callable" type subscripted by:
                    # * The PEP 612-compliant "typing(|_extensions).Concatenate"
                    #   hint factory subscripted by these mandatory parameter
                    #   type hints followed by an ellipsis.
                    # * That return type hint.
                    Callable[Concatenate[float, complex, ...], bytes]
                    if IS_PYTHON_AT_LEAST_3_11 else
                    # Else, the active Python interpreter targets Python < 3.11
                    # and thus fails to support PEP 612. In this case, the PEP
                    # 484- or 585-compliant "Callable" type subscripted by an
                    # ellipsis and that return type hint.
                    Callable[..., bytes]
                ),
            ),
        ))
    # Else, the PEP 612-compliant "ParamSpec" class is unimportable.

    # ..................{ LOCALS ~ O(N)                      }..................
    # List of all type hint inference cases (i.e., 2-tuples "(obj, hint)"
    # describing the type hint matching an arbitrary object) specific to O(n)
    # linear-time type hint inference. Since this strategy deterministically
    # infers type hints in a fully recursive manner, this list may contain
    # containers whose items are of differing types.
    CASES_STRATEGY_ON = CASES_STRATEGY_O1 + [
        # ..................{ PEP [484|585] ~ list           }..................
        # A list of items all of differing types is annotated as the PEP 484-
        # and 585-compliant "list" type subscripted by a PEP 604- or
        # 484-compliant union type hint of those types -- including...
        ([
            # A string.
            'Thy dazzling waves, thy loud and hollow gulfs,',
            # A byte string.
            b'Thy searchless fountain, and invisible course',
            # An integer.
            len('Have each their type in me: and the wide sky,'),
            # A list of strings.
            ['And measureless ocean', 'may declare', 'as soon',],
        ], List[
            # If the active Python interpreter targets Python >= 3.10 and thus
            # supports PEP 604-compliant new-style unions, this kind of union;
            str | bytes | int | List[str]
            if IS_PYTHON_AT_LEAST_3_10 else
            # Else, the active Python interpreter targets Python < 3.10 and thus
            # fails to support PEP 604-compliant new-style unions. In this case,
            # fallback to a PEP 484-compliant old-style union.
            Union[str, bytes, int, List[str]]
        ]),

        # ..................{ PEP [484|585] ~ tuple          }..................
        # A subjectively large root tuple (i.e., tuple *NOT* contained in a
        # larger container but containing a fairly large number of items all of
        # differing types) is annotated as the variadic PEP 484- and
        # 585-compliant "tuple" type subscripted by a single type hint matching
        # all of those types.
        (
            (
                'Fell into that immeasurable void,',
                b'Scattering its waters to the passing winds.',
                37,
                9.1725,
            ) * 4,
            Tuple[
                (
                    # If the active Python interpreter targets Python >= 3.10
                    # and thus supports PEP 604-compliant new-style unions, this
                    # kind of union;
                    str | bytes | int | float
                    if IS_PYTHON_AT_LEAST_3_10 else
                    # Else, the active Python interpreter targets Python < 3.10
                    # and thus fails to support PEP 604-compliant new-style
                    # unions. In this case, fallback to a PEP 484-compliant
                    # old-style union.
                    Union[str, bytes, int, float]
                ),
                # Trailing ellipsis, connoting a variadic tuple type hint.
                ...,
            ],
        ),
    ]

    # ..................{ DICTS ~ cases                      }..................
    # Dictionary mapping from each relevant beartype configuration to a
    # corresponding list of all type hint inference cases specific to that
    # configuration (i.e., 2-tuples "(obj, hint)" describing the type hint
    # matching an arbitrary object) to be returned by this fixture.
    CONF_TO_CASES = {
        # O(1) constant-time type hint inference.
        BeartypeConf(strategy=BeartypeStrategy.O1): CASES_STRATEGY_O1,

        # O(n) linear-time type hint inference.
        BeartypeConf(strategy=BeartypeStrategy.On): CASES_STRATEGY_ON,
    }

    # ..................{ RETURN                             }..................
    # Return this dictionary.
    return CONF_TO_CASES
