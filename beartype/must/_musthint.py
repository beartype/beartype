#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2021 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype data validation constraints classes.**
'''

# ....................{ TODO                              }....................
#FIXME: Docstring us up, please.

#FIXME: As intelligently requested by @Saphyel at #32, add support for
#additional classes support constraints resembling:
#
#* String constraints:
#  * Email.
#  * Uuid.
#  * Choice.
#  * Language.
#  * Locale.
#  * Country.
#  * Currency.
#* Comparison constraints
#  * EqualTo.
#  * NotEqualTo.
#  * IdenticalTo.
#  * NotIdenticalTo.
#  * LessThan.
#  * GreaterThan.
#  * Range.
#  * DivisibleBy.

# ....................{ IMPORTS                           }....................

# See the "beartype.cave" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ CLASSES                           }....................
#FIXME: Unit test us up via the public "beartype.must.Must" class alias.
#FIXME: Docstring us up, please.
#FIXME: Implement as follows:
#* Define the PEP 560-compliant __class_getitem__() class dunder method to:
#  * Accept a single argument, which *MUST* be a callable itself accepting a
#    single positional argument.
#  * Call the beartype._util.func.utilfuncmake.copy_func_shallow() function to
#    create a shallow copy of this function.
#  * Define a new "func_copy.__beartype_is_must = True" attribute on this copy,
#    enabling this copy to be detected as a "Must" subscription.
#  * Return that copy.
#* Define a new is_object_must() tester function *OUTSIDE* this class ala:
#      def is_object_must(obj: object) -> bool:
#          return (
#              callable(obj) and
#              getattr(obj, '__beartype_is_must', False) is True
#          )
#* Define in "_pepsnip":
#      ARG_NAME_CUSTOM_OBJECT = '__beartype_object_{object_id}'
#* Call that tester function from "_pephint" on each argument of an "Annotated"
#  type hint to detect whether that argument is a "Must" subscription; if so,
#  add that argument to "func_wrapper_locals" ala:
#      for hint_child in hint_curr.__args__[1:]:
#          if not is_object_must(hint_child):
#              continue
#
#          hint_child_arg_name = ARG_NAME_CUSTOM_OBJECT.format(
#              object_id=id(hint_child))
#          func_wrapper_locals[hint_child_arg_name: hint_child]
class Must(object):
    '''
    **Beartype data validator** (i.e., class subscripted (indexed) by a
    caller-defined function validating the internal structure of arbitrarily
    complex scalars, data structures, or third-party objects in a PEP-compliant
    manner supported by the :func:`beartype.beartype decorator).
    '''

    pass
