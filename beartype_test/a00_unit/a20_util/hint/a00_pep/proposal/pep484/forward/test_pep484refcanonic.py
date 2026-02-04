#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Test-wide :pep:`484`-compliant **absolute forward reference type hint utility**
unit
tests.

This submodule unit tests the public API of the private
:mod:`beartype._util.hint.pep.proposal.pep484.forward.pep484refcanonic` submodule.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS ~ canonicalizer              }....................
#FIXME: Refactor into an equivalent unit test validating that beartype correctly
#reduces forward references to non-string type hints. The
#canonicalize_hint_pep484_ref() function no longer exists.
# def test_canonicalize_hint_pep484_ref() -> None:
#     '''
#     Test the
#     :func:`beartype._util.hint.pep.proposal.pep484.forward.pep484refcanonic.canonicalize_hint_pep484_ref`
#     canonicalizer.
#     '''
#
#     # ....................{ IMPORTS                        }....................
#     # Defer test-specific imports.
#     from beartype.roar import BeartypeDecorHintForwardRefException
#     from beartype.typing import ForwardRef
#     from beartype._util.hint.pep.proposal.pep484.forward.pep484refcanonic import (
#         canonicalize_hint_pep484_ref)
#     from beartype_test.a00_unit.data.data_type import (
#         ClassModuleNameFake,
#         ClassModuleNameNone,
#         function_module_name_fake,
#         function_module_name_none,
#     )
#     from pytest import raises
#     from re import (
#         compile as re_compile,
#         search as re_search,
#     )
#
#     # ....................{ LOCALS ~ str                   }....................
#     # Fully-qualified name of the current module defining this unit test.
#     THIS_MODULE_NAME = __name__
#
#     # Arbitrary absolute forward reference module names defined as strings.
#     ALAS_ALAS_MODULE = 'He_overleaps.the'
#     THE_MASK_OF_ANARCHY_MODULE = 'as_I.lay_asleep'
#     WITH_GREAT_POWER_IT_MODULE = 'And_with.great_power.it_forth'
#
#     # Arbitrary absolute forward reference basenames defined as strings.
#     ALAS_ALAS_BASENAME = 'bounds'
#     THE_MASK_OF_ANARCHY_BASENAME = 'in_Italy'
#     WITH_GREAT_POWER_IT_BASENAME = 'led_me'
#
#     # Arbitrary absolute forward references defined as strings.
#     ALAS_ALAS = f'{ALAS_ALAS_MODULE}.{ALAS_ALAS_BASENAME}'
#     THE_MASK_OF_ANARCHY = (
#         f'{THE_MASK_OF_ANARCHY_MODULE}.{THE_MASK_OF_ANARCHY_BASENAME}')
#     WITH_GREAT_POWER_IT = (
#         f'{WITH_GREAT_POWER_IT_MODULE}.{WITH_GREAT_POWER_IT_BASENAME}')
#
#     #FIXME: "CASTLEREAGH" is currently unused. *shrug*
#     # Arbitrary fully-qualified names of hypothetical modules.
#     # CASTLEREAGH = 'He_had.a_mask.like_Castlereagh'
#     OF_DIM_SLEEP = 'In_the.wide.pathless_desert'
#
#     # Arbitrary relative forward references defined as strings.
#     VERY_SMOOTH = 'Very_smooth_he_looked_yet_grim'
#     THUS_TREACHEROUSLY = 'Lost_lost_for_ever_lost'
#
#     # ....................{ LOCALS ~ typing                }....................
#     # Arbitrary absolute forward reference encapsulated by a PEP 484-compliant
#     # "typing.ForwardRef" object.
#     WITH_GREAT_POWER = ForwardRef(WITH_GREAT_POWER_IT)
#
#     # ....................{ CALLABLES                      }....................
#     def and_pendent_mountains():
#         '''
#         Arbitrary function whose ``__module__`` dunder attribute is preserved as
#         the fully-qualified name of this currently importable module.
#         '''
#
#         pass
#
#     # ....................{ CLASSES                        }....................
#     class OfRainbowClouds(object):
#         '''
#         Arbitrary class whose ``__module__`` dunder attribute is preserved as
#         the fully-qualified name of this currently importable module.
#         '''
#
#         pass
#
#
#     class InsultAndBlind(object):
#         '''
#         Arbitrary parent class nesting an arbitrary child class.
#         '''
#
#         class AndStifleUpMyPomp(object):
#             '''
#             Arbitrary child class nested in an arbitrary parent class.
#             '''
#
#
#     # Partially-qualified name of the nested class defined above relative to the
#     # current module defining this unit test.
#     AND_STIFLE_UP_MY_POMP = 'InsultAndBlind.AndStifleUpMyPomp'
#
#     # ....................{ PASS ~ absolute                }....................
#     # Assert that this getter preserves an absolute forward reference in string
#     # format as is.
#     assert canonicalize_hint_pep484_ref(THE_MASK_OF_ANARCHY) == (
#         THE_MASK_OF_ANARCHY_MODULE, THE_MASK_OF_ANARCHY_BASENAME)
#
#     # Assert that this getter preserves an absolute forward reference in
#     # "typing.ForwardRef" format as is.
#     assert canonicalize_hint_pep484_ref(WITH_GREAT_POWER) == (
#         WITH_GREAT_POWER_IT_MODULE, WITH_GREAT_POWER_IT_BASENAME)
#
#     # ....................{ PASS ~ relative : cls_stack    }....................
#     # Assert that this getter canonicalizes a relative forward reference to the
#     # *ONLY* type on a type stack against the "__module__" dunder attribute of
#     # that type.
#     assert canonicalize_hint_pep484_ref(
#         hint='InsultAndBlind', cls_stack=(InsultAndBlind,)) == (
#         THIS_MODULE_NAME, 'InsultAndBlind')
#
#     # Assert that this getter canonicalizes a relative forward reference to the
#     # most deeply nested type on a type stack containing a hierarchy of two or
#     # more types against the "__module__" dunder attribute of that type.
#     #
#     # Note this constitutes a unique edge case distinct from the prior case.
#     assert canonicalize_hint_pep484_ref(
#         hint=AND_STIFLE_UP_MY_POMP,
#         cls_stack=(InsultAndBlind, InsultAndBlind.AndStifleUpMyPomp),
#     ) == (THIS_MODULE_NAME, AND_STIFLE_UP_MY_POMP)
#
#     # Assert that this getter canonicalizes a relative forward reference against
#     # the "__module__" dunder attribute of a type stack.
#     assert canonicalize_hint_pep484_ref(
#         hint=VERY_SMOOTH,
#         cls_stack=(OfRainbowClouds,),
#         func=and_pendent_mountains,
#     ) == (THIS_MODULE_NAME, VERY_SMOOTH)
#
#     # ....................{ PASS ~ relative : func         }....................
#     # Assert that this getter canonicalizes a relative forward reference against
#     # the "__module__" dunder attribute of a function.
#     assert canonicalize_hint_pep484_ref(
#         hint=VERY_SMOOTH, func=and_pendent_mountains) == (
#         THIS_MODULE_NAME, VERY_SMOOTH)
#
#     # ....................{ PASS ~ relative : builtin      }....................
#     # Assert that this getter preserves the passed relative forward reference as
#     # is when this reference is the name of a builtin type, even when passed
#     # neither a class *NOR* callable.
#     assert canonicalize_hint_pep484_ref('int') == ('builtins', 'int')
#
#     # Assert that this getter preserves the passed relative forward reference as
#     # is when this reference is the name of a builtin type, even when passed
#     # a class and callable both defining the "__module__" dunder attribute to be
#     # the fully-qualified names of imaginary and thus unimportable modules that
#     # do *NOT* physically exist.
#     assert canonicalize_hint_pep484_ref(
#         hint='int',
#         cls_stack=(ClassModuleNameFake,),
#         func=function_module_name_fake,
#     ) == ('builtins', 'int')
#
#     # ....................{ PASS ~ typing : module name    }....................
#     # Since the active Python interpreter targets >= Python 3.10, then this
#     # typing.ForwardRef.__init__() method accepts an additional optional
#     # "module: Optional[str] = None" parameter preserving the fully-qualified
#     # name of the module to which the passed unqualified basename is relative.
#     # Assert that this getter successfully introspects that module name.
#
#     # Arbitrary relative forward reference defined as a non-string relative to
#     # the fully-qualified name of a hypothetical module.
#     BEAUTIFUL_SHAPE = ForwardRef(THUS_TREACHEROUSLY, module=OF_DIM_SLEEP)
#
#     # Arbitrary absolute forward reference defined as a non-string relative to
#     # the fully-qualified name of a hypothetical module.
#     #
#     # Note that this exercises an edge case. Technically, passing both an
#     # absolute forward reference *AND* a module name is a non-sequitur.
#     # Pragmatically, the ForwardRef.__init__() method blindly permits callers to
#     # do just that. Ergo, @beartype *MUST* guard against this.
#     DARK_GATE_OF_DEATH = ForwardRef(ALAS_ALAS, module=OF_DIM_SLEEP)
#
#     # Assert this getter canonicalizes the passed relative forward reference
#     # against the fully-qualified name of the module with which this reference
#     # was instantiated when defined as a "typing.ForwardRef".
#     assert canonicalize_hint_pep484_ref(BEAUTIFUL_SHAPE) == (
#         OF_DIM_SLEEP, THUS_TREACHEROUSLY)
#
#     # Assert this getter preserves the passed absolute forward reference as is
#     # *WITHOUT* canonicalizing this reference against the fully-qualified name
#     # of the module with which this reference was instantiated when defined as a
#     # "typing.ForwardRef".
#     assert canonicalize_hint_pep484_ref(DARK_GATE_OF_DEATH) == (
#         OF_DIM_SLEEP, ALAS_ALAS)
#
#     # ....................{ FAIL                           }....................
#     # Assert that this getter raises the expected exception when passed a
#     # relative forward reference and neither a type *NOR* function.
#     with raises(BeartypeDecorHintForwardRefException):
#         canonicalize_hint_pep484_ref(VERY_SMOOTH)
#
#     # ....................{ FAIL ~ cls_stack               }....................
#     # Assert that this getter raises the expected exception when passed a
#     # relative forward reference and *ONLY* a type defining the "__module__"
#     # dunder attribute to be the fully-qualified name of an imaginary and thus
#     # unimportable module that does *NOT* physically exist.
#     with raises(BeartypeDecorHintForwardRefException):
#         canonicalize_hint_pep484_ref(
#             hint=VERY_SMOOTH, cls_stack=(ClassModuleNameFake,))
#
#     # Assert that this getter raises the expected exception when passed a
#     # relative forward reference and *ONLY* a type defining the "__module__"
#     # dunder attribute to be "None".
#     with raises(BeartypeDecorHintForwardRefException):
#         canonicalize_hint_pep484_ref(
#             hint=VERY_SMOOTH, cls_stack=(ClassModuleNameNone,))
#
#     # ....................{ FAIL ~ func                    }....................
#     # Assert that this getter raises the expected exception when passed a
#     # relative forward reference and *ONLY* a function defining the
#     # "__module__" dunder attribute to be the fully-qualified name of an
#     # imaginary and thus unimportable module that does *NOT* physically exist.
#     with raises(BeartypeDecorHintForwardRefException):
#         canonicalize_hint_pep484_ref(
#             hint=VERY_SMOOTH, func=function_module_name_fake)
#
#     # Assert that this getter raises the expected exception when passed a
#     # relative forward reference and *ONLY* a function defining the
#     # "__module__" dunder attribute to be "None".
#     with raises(BeartypeDecorHintForwardRefException):
#         canonicalize_hint_pep484_ref(
#             hint=VERY_SMOOTH, func=function_module_name_none)
#
#     # ....................{ FAIL ~ cls_stack + func        }....................
#     # Regular expression matching two consecutive "*"-prefixed bullet points.
#     REGEX_TWO_BULLETS = re_compile(r'(\n\* .+?\.){2}')
#
#     # Assert that this getter raises the expected exception when passed a
#     # relative forward reference and a type and function both defining the
#     # "__module__" dunder attribute to be the fully-qualified names of imaginary
#     # and thus unimportable modules that do *NOT* physically exist.
#     with raises(BeartypeDecorHintForwardRefException) as exception_info:
#         canonicalize_hint_pep484_ref(
#             hint=VERY_SMOOTH,
#             cls_stack=(ClassModuleNameFake,),
#             func=function_module_name_fake,
#         )
#
#     # Previously raised exception message.
#     exception_message = str(exception_info.value)
#
#     # Assert this message contains two consecutive "*"-prefixed bullet points.
#     assert re_search(REGEX_TWO_BULLETS, exception_message) is not None
#
#     # Assert that this getter raises the expected exception when passed a
#     # relative forward reference and a type and function both defining the
#     # "__module__" dunder attribute to be "None".
#     with raises(BeartypeDecorHintForwardRefException) as exception_info:
#         canonicalize_hint_pep484_ref(
#             hint=VERY_SMOOTH,
#             cls_stack=(ClassModuleNameNone,),
#             func=function_module_name_none,
#         )
#
#     # Previously raised exception message.
#     exception_message = str(exception_info.value)
#
#     # Assert this message contains two consecutive "*"-prefixed bullet points.
#     assert re_search(REGEX_TWO_BULLETS, exception_message) is not None

# ....................{ TESTS ~ finder                     }....................
#FIXME: Refactor into an equivalent unit test validating that beartype correctly
#reduces forward references to non-string type hints. The
#find_hint_pep484_ref_on_cls_stack_or_none() function no longer exists.
# def test_find_hint_pep484_ref_on_cls_stack_or_none() -> None:
#     '''
#     Test the
#     :func:`beartype._util.hint.pep.proposal.pep484.forward.pep484refcanonic.find_hint_pep484_ref_on_cls_stack_or_none`
#     finder.
#     '''
#
#     # ....................{ IMPORTS                        }....................
#     # Defer test-specific imports.
#     from beartype.typing import ForwardRef
#     from beartype._util.hint.pep.proposal.pep484.forward.pep484refcanonic import (
#         find_hint_pep484_ref_on_cls_stack_or_none)
#
#     # ....................{ LOCALS                         }....................
#     # Fully-qualified name of the current module defining this unit test.
#     THIS_MODULE_NAME = __name__
#
#     # ....................{ CLASSES                        }....................
#     class OverTheFieryFrontier(object):
#         '''
#         Arbitrary class whose ``__module__`` dunder attribute is preserved as
#         the fully-qualified name of this currently importable module.
#         '''
#
#         pass
#
#
#     class FallNo(object):
#         '''
#         Arbitrary parent class nesting an arbitrary child class.
#         '''
#
#         class ByTellusAnd(object):
#             '''
#             Arbitrary child class nested in an arbitrary parent class.
#             '''
#
#             class HerBrinyRobes(object):
#                 '''
#                 Arbitrary leaf class nested in an arbitrary child class.
#                 '''
#
#                 pass
#
#     # ....................{ PASS ~ ignore                  }....................
#     # Assert that this finder ignores an already absolute forward reference in
#     # "typing.ForwardRef" format.
#     assert find_hint_pep484_ref_on_cls_stack_or_none(
#         hint=ForwardRef('OverTheFieryFrontier', module=THIS_MODULE_NAME),
#         cls_stack=(OverTheFieryFrontier,),
#     ) is None
#
#     # Assert that this finder ignores a relative forward reference in string
#     # format referring to an unrecognized attribute that is *NOT* the only type
#     # on a type stack.
#     assert find_hint_pep484_ref_on_cls_stack_or_none(
#         hint='of_my_realms',
#         cls_stack=(OverTheFieryFrontier,),
#     ) is None
#
#     # Assert that this finder ignores a relative forward reference in string
#     # format referring to an unrecognized attribute that is *NOT* the partially
#     # qualified name of a type on a type stack of two or more types.
#     assert find_hint_pep484_ref_on_cls_stack_or_none(
#         hint='FallNo.ByTellusAnd.of_my_realms',
#         cls_stack=(
#             FallNo,
#             FallNo.ByTellusAnd,
#             FallNo.ByTellusAnd.HerBrinyRobes,
#         ),
#     ) is None
#
#     # ....................{ PASS ~ canonicalize            }....................
#     # Assert that this finder reduces a relative forward reference referring to
#     # to the *ONLY* type on a type stack in both string and "typing.ForwardRef"
#     # formats to that type.
#     assert find_hint_pep484_ref_on_cls_stack_or_none(
#         hint='OverTheFieryFrontier',
#         cls_stack=(OverTheFieryFrontier,),
#     ) is OverTheFieryFrontier
#     assert find_hint_pep484_ref_on_cls_stack_or_none(
#         hint=ForwardRef('OverTheFieryFrontier'),
#         cls_stack=(OverTheFieryFrontier,),
#     ) is OverTheFieryFrontier
#
#     # Assert that this finder reduces a relative forward reference referring to
#     # any arbitrary nested type on a type stack of three or more types other
#     # than the first and last such types in both string and "typing.ForwardRef"
#     # formats to that type.
#     #
#     # Note this constitutes a unique edge case distinct from prior cases.
#     assert find_hint_pep484_ref_on_cls_stack_or_none(
#         hint='FallNo.ByTellusAnd',
#         cls_stack=(
#             FallNo,
#             FallNo.ByTellusAnd,
#             FallNo.ByTellusAnd.HerBrinyRobes,
#         ),
#     ) is FallNo.ByTellusAnd
#     assert find_hint_pep484_ref_on_cls_stack_or_none(
#         hint=ForwardRef('FallNo.ByTellusAnd'),
#         cls_stack=(
#             FallNo,
#             FallNo.ByTellusAnd,
#             FallNo.ByTellusAnd.HerBrinyRobes,
#         ),
#     ) is FallNo.ByTellusAnd
#
#     # Assert that this finder reduces a relative forward reference referring to
#     # the most deeply nested type on a type stack of two or more types in
#     # both string and "typing.ForwardRef" formats to that type.
#     #
#     # Note this constitutes a unique edge case distinct from prior cases.
#     assert find_hint_pep484_ref_on_cls_stack_or_none(
#         hint='FallNo.ByTellusAnd.HerBrinyRobes',
#         cls_stack=(
#             FallNo,
#             FallNo.ByTellusAnd,
#             FallNo.ByTellusAnd.HerBrinyRobes,
#         ),
#     ) is FallNo.ByTellusAnd.HerBrinyRobes
#     assert find_hint_pep484_ref_on_cls_stack_or_none(
#         hint=ForwardRef('FallNo.ByTellusAnd.HerBrinyRobes'),
#         cls_stack=(
#             FallNo,
#             FallNo.ByTellusAnd,
#             FallNo.ByTellusAnd.HerBrinyRobes,
#         ),
#     ) is FallNo.ByTellusAnd.HerBrinyRobes
