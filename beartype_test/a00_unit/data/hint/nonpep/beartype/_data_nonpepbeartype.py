#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype-specific PEP-noncompliant type hints** (i.e., unofficial type hints
supported *only* by the :mod:`beartype.beartype` decorator) test data.

These hints include:

* **Fake builtin types** (i.e., types that are *not* builtin but which
  nonetheless erroneously masquerade as being builtin).
* **Tuple unions** (i.e., tuples containing *only* standard classes and
  forward references to standard classes).
'''

# ....................{ ADDERS                             }....................
def add_data(data_module: 'ModuleType') -> None:
    '''
    Add :mod:`beartype`-specific PEP-noncompliant type hint test data to
    various global containers declared by the passed module.

    Parameters
    ----------
    data_module : ModuleType
        Module to be added to.
    '''

    # ..................{ IMPORTS                            }..................
    # Defer data-specific imports.
    from beartype.plug import BeartypeHintable
    from beartype.vale import Is
    from beartype_test.a00_unit.data.hint.util.data_hintmetacls import (
        HintNonpepMetadata,
        HintPithSatisfiedMetadata,
        HintPithUnsatisfiedMetadata,
    )
    from beartype_test._util.mod.pytmodtyping import iter_typing_attrs

    # ..................{ TUPLES                             }..................
    # Add beartype-specific PEP-noncompliant test type hints to this dictionary
    # global.
    data_module.HINTS_NONPEP_META.extend((
        # ................{ TUPLE UNION                        }................
        # Beartype-specific tuple unions (i.e., tuples containing one or more
        # isinstanceable classes).

        # Tuple union of one isinstanceable class.
        HintNonpepMetadata(
            hint=(str,),
            piths_meta=(
                # String constant.
                HintPithSatisfiedMetadata('Pinioned coin tokens'),
                # Byte-string constant.
                HintPithUnsatisfiedMetadata(
                    pith=b'Murkily',
                    # Match that the exception message raised for this pith
                    # declares the types *NOT* satisfied by this object.
                    exception_str_match_regexes=(
                        r'\bstr\b',
                    ),
                    # Match that the exception message raised for this pith
                    # does *NOT* contain a newline or bullet delimiter.
                    exception_str_not_match_regexes=(
                        r'\n',
                        r'\*',
                    ),
                ),
            ),
        ),

        # Tuple union of two or more isinstanceable classes.
        HintNonpepMetadata(
            hint=(int, str),
            piths_meta=(
                # Integer constant.
                HintPithSatisfiedMetadata(12),
                # String constant.
                HintPithSatisfiedMetadata('Smirk‐opined — openly'),
                # Byte-string constant.
                HintPithUnsatisfiedMetadata(
                    pith=b'Betokening',
                    # Match that the exception message raised for this object
                    # declares the types *NOT* satisfied by this object.
                    exception_str_match_regexes=(
                        r'\bint\b',
                        r'\bstr\b',
                    ),
                    # Match that the exception message raised for this object
                    # does *NOT* contain a newline or bullet delimiter.
                    exception_str_not_match_regexes=(
                        r'\n',
                        r'\*',
                    ),
                ),
            ),
        ),
    ))

    # ..................{ VALIDATORS ~ is                    }..................
    # Beartype-specific validators defined as lambda functions.
    IsNonempty = Is[lambda text: bool(text)]

    # ..................{ FACTORIES                          }..................
    # For each "Annotated" type hint factory importable from a typing module...
    for Annotated in iter_typing_attrs('Annotated'):
        # ..................{ LOCALS ~ plugin                }..................
        # Local variables requiring an "Annotated" type hint factory
        # additionally exercising beartype's plugin API.

        class StringNonempty(str, BeartypeHintable):
            '''
            **Non-empty string** (i.e., :class:`str` subclass satisfying the
            :class:`BeartypeHintable` protocol by defining the
            :meth:`__beartype_hint__` class method to return a type hint
            constraining instances of this subclass to non-empty strings).
            '''

            @classmethod
            def __beartype_hint__(cls) -> object:
                '''
                Beartype type hint transform reducing to an annotated of this
                subclass validating instances of this subclass to be non-empty.
                '''

                # Munificent one-liner: I invoke thee!
                return Annotated[cls, IsNonempty]

        #FIXME: *WOOPS.* Didn't thank about recursion, did we? Clearly, the
        #__beartype_hint__() method should only be called once per type.
        #However, the "StringNonempty" class defined above is invoking infinite
        #recursion -- probably due to returning a type hint embedding itself,
        #which @beartype then inspects the child type hints of, which include
        #"cls == StringNonempty", which then recalls __beartype_hint__() during
        #reduction, and so on ad naseum.
        #
        #Sadly, this may require us to refactor our current BFS into a DFS.
        #Doing so would then enable us to define a set of all hints that should
        #*NOT* be subject to reduction by __beartype_hint__(); that set is, of
        #course, the current set of all parent type hints of the current type
        #hint. Short of that, however, it's non-trivial to see how we could
        #possibly do this under our current BFS architecture. *WOOPS.*
        #FIXME: *AH-HA!* We figured out how to do this *WITHOUT* resorting to a
        #horrifying DFS refactoring. Specifically:
        #* Add yet another new entry to each "hint_meta" FixedList as follows:
        #  * Define a new "HINT_META_INDEX_HINTABLES" constant.
        #  * For the root "hint_meta", initialize the value of:
        #        hint_root_meta[HINT_META_INDEX_HINTABLES] = None
        #* Define a new private _reduce_hintable() function in the same
        #  submodule resembling:
        #      def _reduce_hintable(
        #          hint: object,
        #          hint_meta: Optional[FixedList] = None,
        #          __beartype_hint__: Callable[[], object],
        #      )
        #          if not callable(__beartype_hint__):
        #              raise SomeExceptiot(...)
        #
        #          if hint_meta is not None:
        #             hint_meta_hintables = hint_meta[HINT_META_INDEX_HINTABLES]
        #
        #             if hint_meta_hintables is None:
        #                 hint_meta_hintables = hint_meta[
        #                     HINT_META_INDEX_HINTABLES] = set()
        #
        #             if hint in hint_meta_hintables:
        #                 return hint
        #
        #          hint_meta_hintables.add(hint)
        #          return __beartype_hint__()
        #* Refactor the reduce_hint() function to accept an optional argument
        #  and call the above _reduce_hintable() function:
        #      def reduce_hint(
        #          ...
        #
        #          #FIXME: Or is this actually just an "tuple"? If so, we should
        #          #constrain that as a fully fixed-length tuple.
        #          # Optional parameters.
        #          hint_meta: Optional[FixedList] = None,
        #      )
        #
        #      __beartype_hint__ = getattr(hint, '__beartype_hint__', None)
        #
        #      if __beartype_hint__ is not None:
        #          hint = _reduce_hintable(
        #              hint=hint,
        #              hint_meta=hint_meta,
        #              __beartype_hint__=__beartype_hint__,
        #          )
        #* Refactor sanify_hint_root(), sanify_hint_child(), and all
        #  intermediary functions to also both accept *AND* pass downward
        #  similar "hint_meta" parameters.
        #* Refactor all calls to reduce_hint() *ONLY* from within the
        #  make_check_expr() to additionally pass the "hint_meta" parameter.
        #  However, there exists a significant caveat:
        #  * *WE'RE PRETTY SURE WE'RE CURRENTLY NOT CALLING* reduce_hint() *ON
        #    THE ROOT HINT FROM WITHIN* make_check_expr(). Why? Because
        #    make_check_expr() avoids doing so for efficiency, since the caller
        #    has already done so. Maybe? In so, we'll need to change that;
        #    regardless of efficiency, either:
        #    * The caller should no longer be calling sanify_hint_root().
        #      Instead, *ONLY* make_check_expr() should be calling
        #      sanify_hint_root(). *OR*...
        #    * The caller should call sanify_hint_root(), but additionally be
        #      responsible for:
        #      * Instantiating at least an empty "hint_meta" tuple for the root
        #        type hint.
        #      * Passing that tuple as the "hint_meta" parameter to its call of
        #        sanify_hint_root().
        #      Also, in this case:
        #      * *ALL* "hint_meta" parameters added above should be mandatory.
        #      * make_check_expr() should:
        #        * Accept a new mandatory "hint_root_meta" parameter.
        #        * Properly initialize this parameter as it currently does,
        #          making care to preserve the "HINT_META_INDEX_HINTABLES" index
        #          as is.

        # # ................{ TUPLES                             }................
        # # Add PEP 593-specific test type hints to this tuple global.
        # data_module.HINTS_NONPEP_META.extend((
        #     # ..............{ ANNOTATED ~ beartype : is : plugin }..............
        #     # Note that beartype's plugin API straddles the fine line between
        #     # PEP-compliant and PEP-noncompliant type hints. Superficially, most
        #     # isinstanceable types are PEP-noncompliant and thus exercised in
        #     # unit tests via the "HintNonpepMetadata" dataclass. Semantically,
        #     # isinstanceable type satisfying the "BeartypeHintable" protocol
        #     # define __beartype_hint__() class methods returning PEP-compliant
        #     # type hints instead exercised in unit tests via the
        #     # "HintPepMetadata" dataclass. To avoid confusion, these types are:
        #     # Superficially accepted as PEP-noncompliant. Treating them instead
        #     # as PEP-compliant would be feasible but require non-trivial
        #     # replacement of these types with the type hints returned by their
        #     # __beartype_hint__() class methods. Doing so would also probably
        #     # break literally everything. Did we mention that?
        #
        #     # Isinstanceable type satisfying the "BeartypeHintable" protocol,
        #     # whose __beartype_hint__() class method returns an annotated of an
        #     # isinstanceable type annotated by one beartype-specific validator
        #     # defined as a lambda function.
        #     HintNonpepMetadata(
        #         hint=StringNonempty,
        #         piths_meta=(
        #             # String constant satisfying this validator.
        #             HintPithSatisfiedMetadata(
        #                 "Impell no pretty‐spoked fellahs’ prudently"),
        #             # Byte-string constant *NOT* an instance of the expected
        #             # type.
        #             HintPithUnsatisfiedMetadata(
        #                 pith=b'Impudent Roark-sparkful',
        #                 # Match that the exception message raised for this
        #                 # object embeds the code for this validator's lambda
        #                 # function.
        #                 exception_str_match_regexes=(
        #                     r'Is\[.*\bbool\(text\).*\]',),
        #             ),
        #             # Empty string constant violating this validator.
        #             HintPithUnsatisfiedMetadata(''),
        #         ),
        #     ),
        # ))
