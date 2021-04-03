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
    complex scalars, data structures, and third-party objects in a
    PEP-compliant and checker-agnostic manner explicitly supported by the
    :func:`beartype.beartype decorator).

    Callers are expected to (in order):

    #. Annotate callable parameters and returns to be validated with `PEP
       593`_-compliant :attr:`typing.Annotated` type hints.
    #. Subscript those hints with (in order):

       #. The type of those parameters and returns.
       #. One or more subscriptions (indexations) of this class. In turn, this
          class *must* be subscripted (indexed) by a callable accepting a
          single arbitrary object and returning a boolean that is ``True`` only
          if the passed object is valid. Formally, that callable should have a
          signature resembling:

          .. _code-block:: python

             def is_object_valid(obj: object) -> bool: ...

          If the passed object is invalid, that callable should preferably
          return ``False`` rather than raise an exception.

    .. _PEP 593:
       https://www.python.org/dev/peps/pep-0593

    Examples
    ----------

    .. _code-block:: python

       from beartype import beartype
       from beartype.must import Must
       from typing import Annotated

       @beartype
       def get_text_middle(text: Annotated[str, Must[
           lambda text: 4 <= len(data) <= 14]]):
           """
           Return the substring spanning characters ``[6, 9]`` inclusive
           from the passed string required to have a length in the range
           ``[4, 14]`` inclusive.
           """

           #  "This is guaranteed to work," says beartype.
           r eturn text[7:10]
    '''

    pass
