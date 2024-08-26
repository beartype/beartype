#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2024 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype **Decidedly Object-Oriented Runtime-checking (DOOR) fixtures** (i.e.,
:mod:`pytest`-specific context managers passed as parameters to unit tests
exercising the :mod:`beartype.door` subpackage).
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from pytest import fixture

# ....................{ FIXTURES ~ equality                }....................
@fixture(scope='session')
def door_cases_equality() -> 'Iterable[Tuple[object, object, bool]]':
    '''
    Session-scoped fixture returning an iterable of **hint equality cases**
    (i.e., 3-tuples ``(hint_a, hint_b, is_equal)`` describing the equality
    relations between two PEP-compliant type hints), efficiently cached across
    all tests requiring this fixture.

    This iterable is intentionally defined by the return of this fixture rather
    than as a global constant of this submodule. Why? Because the former safely
    defers all heavyweight imports required to define this iterable to the call
    of the first unit test requiring this fixture, whereas the latter unsafely
    performs those imports at pytest test collection time.

    Returns
    -------
    Iterable[Tuple[object, object, bool]]
        Iterable of one or more 3-tuples ``(hint_a, hint_b, is_equal)``,
        where:

        * ``hint_a`` is the PEP-compliant type hint to be passed as the first
          parameter to the :meth:`beartype.door.TypeHint.__equals__` tester.
        * ``hint_b`` is the PEP-compliant type hint to be passed as the second
          parameter to the :meth:`beartype.door.TypeHint.__equals__` tester.
        * ``is_equal`` is ``True`` only if these hints are equal according to
          that tester.
    '''

    # ..................{ IMPORTS                            }..................
    # Defer fixture-specific imports.
    from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_9
    from numbers import Number

    # Intentionally import from "typing" rather than "beartype.typing" to
    # guarantee PEP 484-compliant type hints.
    from typing import (
        Any,
        List,
        Tuple,
        Union,
    )

    # ..................{ LISTS                              }..................
    HINT_EQUALITY_CASES = [
        # ..................{ HINTS ~ argless : bare         }..................
        # PEP 484-compliant unsubscripted type hints, which are necessarily
        # equal to themselves.
        (tuple, Tuple, True),
        (list, list, True),
        (list, List, True),

        # ..................{ HINTS ~ arg : sequence         }..................
        # PEP 484-compliant sequence type hints.
        (list, List[Any], True),
        (tuple, Tuple[Any, ...], True),

        # ..................{ HINTS ~ arg : union            }..................
        # PEP 484-compliant union type hints.
        (Union[int, str], Union[str, list], False),
        (Union[Number, int], Union[Number, float], True),

        # Test that union equality ignores order.
        (Union[int, str], Union[str, int], True),

        # Test that union equality compares child type hints collectively rather
        # than individually.
        #
        # Note that this pair of cases tests numerous edge cases, including:
        # * Equality comparison of non-unions against unions. Although
        #   "Union[int]" superficially appears to be a union, Python reduces
        #   "Union[int]" to simply "int" at runtime.
        (Union[bool, int], Union[int], True),
        (Union[int], Union[bool, int], True),
    ]

    # If the active Python interpreter targets Python >= 3.9 and thus supports
    # both PEP 585 and 593...
    if IS_PYTHON_AT_LEAST_3_9:
        from beartype.typing import Annotated
        from collections.abc import (
            Awaitable as AwaitableABC,
            Sequence as SequenceABC,
        )

        # Append cases exercising version-specific relations.
        HINT_EQUALITY_CASES.extend((
            # PEP 585-compliant type hints.
            (tuple[str, ...], Tuple[str, ...], True),
            (list[str], List[str], True),
            (AwaitableABC[SequenceABC[int]], AwaitableABC[SequenceABC[int]], True),

            # PEP 593-compliant type hints.
            (Annotated[int, "hi"], Annotated[int, "hi"], True),
            (Annotated[int, "hi"], Annotated[int, "low"], False),
            (Annotated[int, "hi"], Annotated[int, "low"], False),
        ))

    # Return this mutable list coerced into an immutable tuple for safety.
    return tuple(HINT_EQUALITY_CASES)

# ....................{ FIXTURES ~ infer                   }....................
@fixture(scope='session')
def door_cases_infer_hint() -> 'Iterable[Tuple[object, object]]':
    '''
    Session-scoped fixture returning an iterable of **type hint inference
    cases** (i.e., 2-tuples ``(obj, hint)`` describing the type hint matching an
    arbitrary object), efficiently cached across all tests requiring this
    fixture.

    This iterable is intentionally defined by the return of this fixture rather
    than as a global constant of this submodule. Why? Because the former safely
    defers all heavyweight imports required to define this iterable to the call
    of the first unit test requiring this fixture, whereas the latter unsafely
    performs those imports at pytest test collection time.

    Returns
    -------
    Iterable[Tuple[object, object]]
        Iterable of one or more 2-tuples ``(obj, hint)``, where:

        * ``obj`` is an arbitrary object to be passed as the first parameter to
          the :func:`beartype.door.infer_hint` function.
        * ``hint`` is the type hint returned by that function when passed that
          object.
    '''

    # ..................{ IMPORTS                            }..................
    # Defer fixture-specific imports.
    from beartype.typing import (
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
    from beartype._util.module.utilmodtest import is_module
    from beartype._util.py.utilpyversion import (
        IS_PYTHON_AT_LEAST_3_11,
        IS_PYTHON_AT_LEAST_3_10,
        IS_PYTHON_AT_LEAST_3_9,
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

    # ..................{ LOCALS                             }..................
    # PEP 593-compliant "Annotated" type hint factory imported from either the
    # standard "typing" or third-party "typing_extensions" modules if importable
    # from at least one of those modules *OR* "None" otherwise.
    Annotated = import_typing_attr_or_none_safe('Annotated')

    # PEP 612-compliant "Concatenate" type hint factory and "ParamSpec" class
    # imported from either the standard "typing" or third-party
    # "typing_extensions" modules if importable from at least one of those
    # modules *OR* "None" otherwise.
    Concatenate = import_typing_attr_or_none_safe('Concatenate')
    ParamSpec = import_typing_attr_or_none_safe('ParamSpec')

    # ..................{ LISTS ~ cases                      }..................
    #FIXME: Also test recursion protection somewhere, please.

    # List of all type hint inference cases (i.e., 2-tuples "(obj, hint)"
    # describing the type hint matching an arbitrary object) to be returned by
    # this fixture.
    INFER_HINT_CASES = [
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
            (
                # If "typing(|_extensions).Annotated" is importable, the
                # narrowest "collections.abc" protocol matching this object
                # annotated to require an instance of this object's type.
                Annotated[Mapping[str, bytes], IsInstance[ClassMapping]]
                if Annotated is not None else
                # Else, "typing(|_extensions).Annotated" is unimportable. In
                # this case, merely this protocol.
                Mapping[str, bytes]
            ),
        ),
        (
            ClassMutableMapping({
                b'Yet ghastly.': 'For, as fast years flow away,',
                b'The smooth brow gathers,': 'and the hair grows thin',
            }),
            (
                # If "typing(|_extensions).Annotated" is importable, the
                # narrowest "collections.abc" protocol matching this object
                # annotated to require an instance of this object's type.
                Annotated[
                    MutableMapping[bytes, str], IsInstance[ClassMutableMapping]]
                if Annotated is not None else
                # Else, "typing(|_extensions).Annotated" is unimportable. In
                # this case, merely this protocol.
                MutableMapping[bytes, str]
            ),
        ),

        # "collections.abc.MutableSequence" protocol hierarchy.
        (
            ClassContainer([
                b'Beneath the shade of trees', b'beside the flow']),
            (
                # If "typing(|_extensions).Annotated" is importable, the
                # narrowest "collections.abc" protocol matching this object
                # annotated to require an instance of this object's type.
                Annotated[Container, IsInstance[ClassContainer]]
                if Annotated is not None else
                # Else, "typing(|_extensions).Annotated" is unimportable. In
                # this case, merely this protocol.
                Container
            ),
        ),
        (
            ClassCollection([
                'Of the wild babbling rivulet;', 'and now']),
            (
                # If "typing(|_extensions).Annotated" is importable, the
                # narrowest "collections.abc" protocol matching this object
                # annotated to require an instance of this object's type.
                Annotated[Collection[str], IsInstance[ClassCollection]]
                if Annotated is not None else
                # Else, "typing(|_extensions).Annotated" is unimportable. In
                # this case, merely this protocol.
                Collection[str]
            ),
        ),
        (
            ClassSequence([
                b'He must descend.', b'With rapid steps he went']),
            (
                # If "typing(|_extensions).Annotated" is importable, the
                # narrowest "collections.abc" protocol matching this object
                # annotated to require an instance of this object's type.
                Annotated[Sequence[bytes], IsInstance[ClassSequence]]
                if Annotated is not None else
                # Else, "typing(|_extensions).Annotated" is unimportable. In
                # this case, merely this protocol.
                Sequence[bytes]
            ),
        ),
        (
            ClassMutableSequence([
                'Forgetful of the grave', 'where', 'when the flame']),
            (
                # If "typing(|_extensions).Annotated" is importable, the
                # narrowest "collections.abc" protocol matching this object
                # annotated to require an instance of this object's type.
                Annotated[
                    MutableSequence[str], IsInstance[ClassMutableSequence]]
                if Annotated is not None else
                # Else, "typing(|_extensions).Annotated" is unimportable. In
                # this case, merely this protocol.
                MutableSequence[str]
            ),
        ),
        # Object satisfying both the "collections.abc.Mapping" *AND*
        # "collections.abc.Sequence" protocols, exercising various edge cases
        # with respect to protocol overlap and ambiguity.
        (
            ClassMappingSequence([
                b'And white,', b'and where irradiate dewy eyes',]),
            (
                # If "typing(|_extensions).Annotated" is importable, the
                # narrowest "collections.abc" protocol matching this object
                # annotated to require an instance of this object's type.
                Annotated[Sequence[bytes], IsInstance[ClassMappingSequence]]
                if Annotated is not None else
                # Else, "typing(|_extensions).Annotated" is unimportable. In
                # this case, merely this protocol.
                Sequence[bytes]
            ),
        ),

        # "collections.abc.Sized" protocol.
        (
            ClassSized("The forest's solemn canopies were changed"),
            (
                # If "typing(|_extensions).Annotated" is importable, the
                # narrowest "collections.abc" protocol matching this object
                # annotated to require an instance of this object's type.
                Annotated[Sized, IsInstance[ClassSized]]
                if Annotated is not None else
                # Else, "typing(|_extensions).Annotated" is unimportable. In
                # this case, merely this protocol.
                Sized
            ),
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
        # A deque of items all of the same class is annotated as the PEP 484- or
        # 585-compliant "deque" type subscripted by that class.
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

        # A list of items all of the same class is annotated as the PEP 484- or
        # 585-compliant "list" type subscripted by that class.
        (['expose', 'extreme', 'explosions!',], List[str]),

        # A list of items all of differing classes is annotated as the PEP 484-
        # and 585-compliant "list" type subscripted by a PEP 604- or
        # 484-compliant union type hint of those classes -- including...
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
        # larger container but containing a fairly large number of items) is
        # annotated as the variadic PEP 484- and 585-compliant "tuple" type
        # subscripted by a single type hint matching the types of all items.
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

        # ((b'heh', [0xBEEEEEEEF, 'ohnoyoudont',], (
        #     (b'heh', [0xBEEEEEEEF, 'ohnoyoudont',]).
        #     .
        # )),

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
        # of a different class is annotated as the PEP 585-compliant "dict" type
        # sequentially subscripted by those classes.
        (
            ClassDict({
                b'Threw their thin shadows': 'down the rugged slope',
                b'And nought but': 'gnarlèd roots of ancient pines',
            }),
            (
                # If the active Python interpreter targets Python >= 3.9 and
                # thus supports PEP 585, this user-defined dictionary
                # subscripted by these child key and value type hints.
                ClassDict[bytes, str]
                if IS_PYTHON_AT_LEAST_3_9 else
                # Else, the active Python interpreter targets Python < 3.9 and
                # thus fails to support PEP 585. In this case, the standard
                # "typing.Dict" factory subscripted by these child key and value
                # type hints.
                Dict[bytes, str]
            ),
        ),

        # A user-defined list of items all of the same class is annotated as the
        # PEP 585-compliant "list" type subscripted by that class.
        (
            ClassList((
                b'The struggling brook:', b'tall spires of windlestrae',)),
            (
                # If the active Python interpreter targets Python >= 3.9 and
                # thus supports PEP 585, this user-defined list subscripted by
                # this child type hint.
                ClassList[bytes]
                if IS_PYTHON_AT_LEAST_3_9 else
                # Else, the active Python interpreter targets Python < 3.9 and
                # thus fails to support PEP 585. In this case, the standard
                # "typing.List" factory subscripted by this child type hint.
                List[bytes]
            ),
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
        INFER_HINT_CASES.extend((
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

    # ..................{ RETURN                             }..................
    # Return this mutable list coerced into an immutable tuple for safety.
    return tuple(INFER_HINT_CASES)

# ....................{ FIXTURES ~ subhint                 }....................
#FIXME: Rename to door_cases_is_subhint() for orthogonality.
@fixture(scope='session')
def door_cases_is_subhint() -> 'Iterable[Tuple[object, object, bool]]':
    '''
    Session-scoped fixture returning an iterable of **type subhint cases**
    (i.e., 3-tuples ``(subhint, superhint, is_subhint)`` describing the subhint
    relations between two type hints), efficiently cached across all tests
    requiring this fixture.

    This iterable is intentionally defined by the return of this fixture rather
    than as a global constant of this submodule. Why? Because the former safely
    defers all heavyweight imports required to define this iterable to the call
    of the first unit test requiring this fixture, whereas the latter unsafely
    performs those imports at pytest test collection time.

    Returns
    -------
    Iterable[Tuple[object, object, bool]]
        Iterable of one or more 3-tuples ``(subhint, superhint, is_subhint)``,
        where:

        * ``subhint`` is the type hint to be passed as the first parameter to
          the :func:`beartype.door.is_subhint` tester.
        * ``superhint`` is the type hint to be passed as the second parameter to
          the :func:`beartype.door.is_subhint` tester.
        * ``is_subhint`` is :data:`True` only if that subhint is actually a
          subhint of that superhint according to that tester.
    '''

    # ..................{ IMPORTS                            }..................
    # Defer fixture-specific imports.
    import collections.abc
    import typing
    from beartype._data.hint.datahinttyping import S, T
    from beartype._util.hint.pep.utilpepget import get_hint_pep_typevars
    from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_9
    from collections.abc import (
        Collection as CollectionABC,
        Sequence as SequenceABC,
    )

    # Intentionally import from "beartype.typing" rather than "typing" to
    # guarantee PEP 544-compliant caching protocol type hints.
    from beartype.typing import (
        Literal,
        Protocol,
        TypedDict,
    )

    # Intentionally import from "typing" rather than "beartype.typing" to
    # guarantee PEP 484-compliant type hints.
    from typing import (
        Any,
        Awaitable,
        ByteString,
        Callable,
        Collection,
        DefaultDict,
        Dict,
        Generic,
        Hashable,
        Iterable,
        List,
        Mapping,
        NamedTuple,
        NewType,
        Optional,
        Reversible,
        Sequence,
        Sized,
        Tuple,
        Type,
        TypeVar,
        Union,
    )

    # ..................{ NEWTYPES                           }..................
    NewStr = NewType('NewStr', str)

    # ..................{ TYPEVARS                           }..................
    # Arbitrary constrained type variables.
    T_sequence = TypeVar('T_sequence', bound=SequenceABC)
    T_int_or_str = TypeVar('T_int_or_str', int, str)

    # ..................{ CLASSES                            }..................
    class MuhThing:
        def muh_method(self):
            pass

    class MuhSubThing(MuhThing):
        pass

    class MuhNutherThing:
        def __len__(self) -> int:
            pass


    class MuhDict(TypedDict):
        '''
        Arbitrary typed dictionary.
        '''

        thing_one: str
        thing_two: int


    class MuhThingP(Protocol):
        '''
        Arbitrary caching @beartype protocol.
        '''

        def muh_method(self):
            ...


    class MuhTuple(NamedTuple):
        '''
        Arbitrary named tuple.
        '''

        thing_one: str
        thing_two: int

    # ..................{ CLASSES ~ generics                 }..................
    class MuhGeneric(Generic[T]):
        '''
        Arbitrary generic parametrized by one unconstrained type variable.
        '''

        pass


    class MuhGenericTwo(Generic[S, T]):
        '''
        Arbitrary generic parametrized by two unconstrained type variables.
        '''

        pass


    class MuhGenericTwoIntInt(MuhGenericTwo[int, int]):
        '''
        Arbitrary concrete generic subclass inheriting the
        :class:`.MuhGenericTwo` generic superclass subscripted twice by the
        builtin :class:`int` type.
        '''

        pass

    # ..................{ LISTS ~ cases                      }..................
    # List of all hint subhint cases (i.e., 3-tuples "(subhint, superhint,
    # is_subhint)" describing the subhint relations between two PEP-compliant
    # type hints) to be returned by this fixture.
    HINT_SUBHINT_CASES = [
        # ..................{ PEP 484 ~ argless : any        }..................
        # PEP 484-compliant catch-all type hint.
        (MuhThing, Any, True),
        (Tuple[object, ...], Any, True),
        (Union[int, MuhThing], Any, True),

        # Although *ALL* type hints are subhints of "Any", "Any" is only a
        # subhint of itself.
        (Any, Any, True),
        (Any, object, False),

        # ..................{ PEP 484 ~ argless : bare       }..................
        # PEP 484-compliant unsubscripted type hints, which are necessarily
        # subhints of themselves.
        (list, list, True),
        (list, List, True),

        # PEP 484-compliant unsubscripted sequence type hints.
        (Sequence, List, False),
        (Sequence, list, False),
        (List, Sequence, True),
        (list, Sequence, True),
        (list, SequenceABC, True),
        (list, CollectionABC, True),

        # ..................{ PEP 484 ~ argless : type       }..................
        # PEP 484-compliant argumentless abstract base classes (ABCs).
        (bytes, ByteString, True),
        (str, Hashable, True),
        (MuhNutherThing, Sized, True),
        (MuhTuple, tuple, True),  # not really types

        # PEP 484-compliant new type type hints.
        (NewStr, NewStr, True),
        (NewStr, int, False),
        (NewStr, str, True),
        (int, NewStr, False),
        (str, NewStr, False),  # NewType act like subtypes

        # ..................{ PEP 484 ~ argless : typevar    }..................
        # PEP 484-compliant type variables.
        (list, T_sequence, True),
        (T_sequence, list, False),
        (int, T_int_or_str, True),
        (str, T_int_or_str, True),
        (list, T_int_or_str, False),
        (Union[int, str], T_int_or_str, True),
        (Union[int, str, None], T_int_or_str, False),
        (T, T_sequence, False),
        (T_sequence, T, True),
        (T_sequence, Any, True),
        (Any, T, True),  # Any is compatible with an unconstrained TypeVar
        (Any, T_sequence, False),  # but not vice versa

        # ..................{ PEP 484 ~ argless : number     }..................
        # Blame Guido.
        (bool, int, True),

        # PEP 484-compliant implicit numeric tower, which we explicitly and
        # intentionally do *NOT* comply with. Floats are not integers. Notably,
        # floats *CANNOT* losslessly represent many integers and are thus
        # incompatible in general.
        (float, int, False),
        (complex, int, False),
        (complex, float, False),
        (int, float, False),
        (float, complex, False),

        # ..................{ PEP 484 ~ arg : callable       }..................
        # PEP 484-compliant callable type hints.
        (Callable, Callable[..., Any], True),
        (Callable[[], int], Callable[..., Any], True),
        (Callable[[int, str], List[int]], Callable, True),
        (Callable[[int, str], List[int]], Callable, True),
        (
            Callable[[float, List[str]], int],
            Callable[[int, Sequence[str]], int],
            True,
        ),
        (Callable[[Sequence], int], Callable[[list], int], False),
        (Callable[[], int], Callable[..., None], False),
        (Callable[..., Any], Callable[..., None], False),
        (Callable[[float], None], Callable[[float, int], None], False),
        (Callable[[], int], Sequence[int], False),
        (Callable[[int, str], int], Callable[[int, str], Any], True),
        # (types.FunctionType, Callable, True),  # FIXME

        # ..................{ PEP 484 ~ arg : generic        }..................
        # PEP 484-compliant generics parametrized by one type variable.
        (MuhGeneric, MuhGeneric, True),
        (MuhGeneric, MuhGeneric[int], False),
        (MuhGeneric[int], MuhGeneric, True),
        (MuhGeneric[int], MuhGeneric[T_sequence], False),
        (MuhGeneric[list], MuhGeneric[T_sequence], True),
        (MuhGeneric[list], MuhGeneric[Sequence], True),
        (MuhGeneric[str], MuhGeneric[T_sequence], True),
        (MuhGeneric[Sequence], MuhGeneric[list], False),
        (MuhGeneric[T_sequence], MuhGeneric, True),

        #FIXME: Uncomment after resolving open issue #271, please.
        # PEP 484-compliant generics parametrized by two type variables.
        # (MuhGenericTwoIntInt, MuhGenericTwo[int, int], True),

        # ..................{ PEP 484 ~ arg : mapping        }..................
        # PEP 484-compliant mapping type hints.
        (dict, Dict, True),
        (Dict[str, int], Dict, True),
        (dict, Dict[str, int], False),
        (
            DefaultDict[str, Sequence[int]],
            Mapping[Union[str, int], Iterable[Union[int, str]]],
            True,
        ),

        # ..................{ PEP 484 ~ arg : sequence       }..................
        # PEP 484-compliant sequence type hints.
        (List[int], List[int], True),
        (List[int], Sequence[int], True),
        (Sequence[int], Iterable[int], True),
        (Iterable[int], Sequence[int], False),
        (Sequence[int], Reversible[int], True),
        (Sequence[int], Reversible[str], False),
        (Collection[int], Sized, True),
        (List[int], List, True),  # if the super is un-subscripted, assume Any
        (List[int], List[Any], True),
        (Awaitable, Awaitable[str], False),
        (List[int], List[str], False),

        # PEP 484-compliant tuple type hints.
        (tuple, Tuple, True),
        (Tuple, Tuple, True),
        (tuple, Tuple[Any, ...], True),
        (tuple, Tuple[()], False),
        (Tuple[()], tuple, True),
        (Tuple[int, str], Tuple[int, str], True),
        (Tuple[int, str], Tuple[int, str, int], False),
        (Tuple[int, str], Tuple[int, Union[int, list]], False),
        (Tuple[Union[int, str], ...], Tuple[int, str], False),
        (Tuple[int, str], Tuple[str, ...], False),
        (Tuple[int, str], Tuple[Union[int, str], ...], True),
        (Tuple[Union[int, str], ...], Tuple[Union[int, str], ...], True),
        (Tuple[int], Dict[str, int], False),
        (Tuple[Any, ...], Tuple[str, int], False),

        # PEP 484-compliant nested sequence type hints.
        (List[int], Union[str, List[Union[int, str]]], True),

        # ..................{ PEP 484 ~ arg : subclass       }..................
        # PEP 484-compliant subclass type hints.
        (Type[int], Type[int], True),
        (Type[int], Type[str], False),
        (Type[MuhSubThing], Type[MuhThing], True),
        (Type[MuhThing], Type[MuhSubThing], False),
        (MuhThing, Type[MuhThing], False),

        # ..................{ PEP 484 ~ arg : union          }..................
        # PEP 484-compliant unions.
        (int, Union[int, str], True),
        (Union[int, str], Union[list, int, str], True),
        (Union[str, int], Union[int, str, list], True),  # order doesn't matter
        (Union[str, list], Union[str, int], False),
        (Union[int, str, list], list, False),
        (Union[int, str, list], Union[int, str], False),
        (int, Optional[int], True),
        (Optional[int], int, False),
        (list, Optional[Sequence], True),

        # ..................{ PEP 544                        }..................
        # PEP 544-compliant type hints.
        (MuhThing, MuhThingP, True),
        (MuhNutherThing, MuhThingP, False),
        (MuhThingP, MuhThing, False),

        # ..................{ PEP 586                        }..................
        # PEP 586-compliant type hints.
        (Literal[7], int, True),
        (Literal["a"], str, True),
        (Literal[7, 8, "3"], Union[int, str], True),
        (Literal[7, 8, "3"], Union[list, int], False),
        (Literal[True], Union[Literal[True], Literal[False]], True),
        (Literal[7, 8], Literal[7, 8, 9], True),
        (int, Literal[7], False),
        (Union[Literal[True], Literal[False]], Literal[True], False),

        # ..................{ PEP 589                        }..................
        # PEP 589-compliant type hints.
        (MuhDict, dict, True),
    ]

    # ..................{ LISTS ~ typing                     }..................
    # List of the unqualified basenames of all standard ABCs published by
    # the standard "collections.abc" module, defined as...
    COLLECTIONS_ABC_BASENAMES = [
        # For the unqualified basename of each attribute defined by the standard
        # "collections.abc" module...
        COLLECTIONS_ABC_BASENAME
        for COLLECTIONS_ABC_BASENAME in dir(collections.abc)
        # If this basename is *NOT* prefixed by an underscore, this attribute is
        # public and thus an actual ABC. In this case, include this ABC.
        if not COLLECTIONS_ABC_BASENAME.startswith('_')
        # Else, this is an unrelated private attribute. In this case, silently
        # ignore this attribute and continue to the next.
    ]

    # List of the unqualified basenames of all standard abstract base classes
    # (ABCs) supported by the standard "typing" module, defined as the
    # concatenation of...
    TYPING_ABC_BASENAMES = (
        # List of the unqualified basenames of all standard ABCs published by
        # the standard "collections.abc" module *PLUS*...
        COLLECTIONS_ABC_BASENAMES +
        # List of the unqualified basenames of all ancillary ABCs *NOT*
        # published by the standard "collections.abc" module but nonetheless
        # supported by the standard "typing" module.
        ['Deque']
    )

    # ..................{ HINTS ~ abcs                       }..................
    # For the unqualified basename of each standard ABCs supported by the
    # standard "typing" module...
    #
    # Note this also constitutes a smoke test (i.e., high-level test validating
    # core functionality) for whether the DOOR API supports standard abstract
    # base classes (ABCs). Smoke out those API inconsistencies, pytest!
    for TYPING_ABC_BASENAME in TYPING_ABC_BASENAMES:
        #FIXME: This logic is likely to fail under a future Python release.
        # Type hint factory published by the "typing" module corresponding to
        # this ABC if any *OR* "None" otherwise (i.e., if "typing" publishes
        # *NO* such type hint factory).
        TypingABC = getattr(typing, TYPING_ABC_BASENAME, None)

        # If "typing" publishes *NO* such type hint factory, silently ignore
        # this ABC and continue to the next.
        if TypingABC is None:
            continue
        # Else, "typing" publishes this type hint factory.

        # Number of type variables parametrizing this ABC, defined as either...
        TYPING_ABC_TYPEVARS_LEN = (
            # If the active Python interpreter targets Python >= 3.9, a private
            # instance variable of this type hint factory yielding this
            # metadata. Under Python >= 3.9, unsubscripted type hint factories
            # are *NOT* parametrized by type variables.
            TypingABC._nparams
            if IS_PYTHON_AT_LEAST_3_9 else
            # Else, the active Python interpreter targets Python < 3.9. In this
            # case, the number of type variables directly parametrizing this
            # ABC.
            len(get_hint_pep_typevars(TypingABC))
        )

        # If this ABC is parametrized by one or more type variables, exercise
        # that this ABC subscripted by one or more arbitrary concrete types is a
        # non-trivial subhint of this same ABC subscripted by one or more
        # arbitrary different ABCs of those concrete types.
        if TYPING_ABC_TYPEVARS_LEN:
            subhint =   TypingABC[(list,)     * TYPING_ABC_TYPEVARS_LEN]
            superhint = TypingABC[(Sequence,) * TYPING_ABC_TYPEVARS_LEN]
        # Else, this ABC is parametrized by *NO* type variables. In this case,
        # fallback to exercising that this ABC is a trivial subhint of itself.
        else:
            subhint =   TypingABC
            superhint = TypingABC

        # Append a new hint subhint case exercising that this subhint is
        # actually a subhint of this superhint.
        HINT_SUBHINT_CASES.append((subhint, superhint, True))

    # ..................{ HINTS ~ version                    }..................
    # If the active Python interpreter targets Python >= 3.9 and thus supports
    # both PEP 585 and 593...
    if IS_PYTHON_AT_LEAST_3_9:
        # Defer version-specific imports.
        from beartype.typing import Annotated

        # Append cases exercising version-specific relations.
        HINT_SUBHINT_CASES.extend((
            # PEP 585-compliant type hints.
            (tuple, Tuple, True),
            (tuple[()], Tuple[()], True),

            # PEP 593-compliant type hints.
            (Annotated[int, "a note"], int, True),  # annotated is subtype of unannotated
            (int, Annotated[int, "a note"], False),  # but not vice versa
            (Annotated[list, True], Annotated[Sequence, True], True),
            (Annotated[list, False], Annotated[Sequence, True], False),
            (Annotated[list, 0, 0], Annotated[list, 0], False),  # must have same num args
            (Annotated[List[int], "metadata"], List[int], True),
        ))

    # Return this mutable list coerced into an immutable tuple for safety.
    return tuple(HINT_SUBHINT_CASES)
