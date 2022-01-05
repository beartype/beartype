#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2022 Beartype authors.
# See "LICENSE" for further details.

'''
**Core unary beartype validators** (i.e., :class:`BeartypeValidator` subclasses
implementing binary operations on pairs of lower-level beartype validators).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                           }....................
from beartype.roar import BeartypeValeSubscriptionException
from beartype.vale._core._valecore import BeartypeValidator
from beartype.vale._util._valeutiltext import format_diagnosis_line
from beartype._util.text.utiltextmagic import CODE_INDENT_1
from beartype._util.text.utiltextrepr import represent_object

# See the "beartype.cave" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ SUPERCLASSES                      }....................
class BeartypeValidatorBinary(BeartypeValidator):
    '''
    **Binary beartype validator** (i.e., validator modifying the boolean
    truthiness returned by the validation performed by a pair of lower-level
    beartype validators).

    Attributes
    ----------
    _validator_operand_1 : BeartypeValidator
        First lower-level validator operated upon by this higher-level
        validator.
    _validator_operand_2 : BeartypeValidator
        Second lower-level validator operated upon by this higher-level
        validator.
    '''

    # ..................{ CLASS VARIABLES                   }..................
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # CAUTION: Subclasses declaring uniquely subclass-specific instance
    # variables *MUST* additionally slot those variables. Subclasses violating
    # this constraint will be usable but unslotted, which defeats our purposes.
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # Slot all instance variables defined on this object to minimize the time
    # complexity of both reading and writing variables across frequently called
    # cache dunder methods. Slotting has been shown to reduce read and write
    # costs by approximately ~10%, which is non-trivial.
    __slots__ = (
        '_validator_operand_1',
        '_validator_operand_2',
    )

    # ..................{ INITIALIZERS                      }..................
    def __init__(
        self,

        # Mandatory parameters.
        validator_operand_1: BeartypeValidator,
        validator_operand_2: BeartypeValidator,
        *args,
        **kwargs
    ) -> None:
        '''
        Initialize this validator from the passed metadata.

        Parameters
        ----------
        validator_operand_1 : BeartypeValidator
            First lower-level validator operated upon by this higher-level
            validator.
        validator_operand_2 : BeartypeValidator
            Second lower-level validator operated upon by this higher-level
            validator.

        All remaining parameters are passed as is to the superclass
        :meth:`BeartypeValidator.__init__` method.

        Raises
        ----------
        BeartypeValeSubscriptionException
            If either of these operands are *not* beartype validators.
        '''

        # Initialize our superclass with all remaining parameters.
        super().__init__(*args, **kwargs)

        #FIXME: Unit test us up, please.
        # If either of theser operands are *NOT* beartype validators, raise an
        # exception.
        if not isinstance(validator_operand_1, BeartypeValidator):
            raise BeartypeValeSubscriptionException(
                f'Binary beartype validator {repr(self)} first operand '
                f'{represent_object(validator_operand_1)} not beartype '
                f'validator (i.e., "beartype.vale.Is*[...]" object).'
            )
        elif not isinstance(validator_operand_2, BeartypeValidator):
            raise BeartypeValeSubscriptionException(
                f'Binary beartype validator {repr(self)} second operand '
                f'{represent_object(validator_operand_2)} not beartype '
                f'validator (i.e., "beartype.vale.Is*[...]" object).'
            )
        # Else, both of these operands are beartype validators.

        # Classify this operand.
        self._validator_operand_1 = validator_operand_1
        self._validator_operand_2 = validator_operand_2

# ....................{ SUBCLASSES                        }....................
class BeartypeValidatorConjunction(BeartypeValidatorBinary):
    '''
    **Conjunction beartype validator** (i.e., validator conjunctively
    evaluating the boolean truthiness returned by the validation performed by a
    pair of lower-level beartype validators, typically instantiated and
    returned by the :meth:`BeartypeValidator.__and__` dunder method of the
    first validator passed the second).
    '''

    # ..................{ GETTERS                           }..................
    #FIXME: Unit test us up, please.
    #FIXME: This violates DRY with the get_diagnosis() method defined below.
    #FIXME: Overly verbose for conjunctions involving three or more
    #beartype validators. Contemplate compaction schemes, please. Specifically,
    #we need to detect this condition here and then compact based on that:
    #    # If either of these validators are themselves conjunctions...
    #    if isinstance(self._validator_operand_1, BeartypeValidatorConjunction):
    #       ...
    #    if isinstance(self._validator_operand_2, BeartypeValidatorConjunction):
    #       ...
    def get_diagnosis(
        self,
        obj: object,
        indent_level_outer: str,
        indent_level_inner: str,
    ) -> str:

        # Innermost indentation level indented one level deeper than the passed
        # innermost indentation level.
        indent_level_inner_nested = indent_level_inner + CODE_INDENT_1

        # Line diagnosing this object against this parent conjunction.
        line_outer_prefix = format_diagnosis_line(
            validator_repr='(',
            indent_level_outer=indent_level_outer,
            indent_level_inner=indent_level_inner,
            is_obj_valid=self.is_valid(obj),
        )

        # Line diagnosing this object against this original first child
        # validator, with an increased indentation level for readability.
        line_inner_operand_1 = self._validator_operand_1.get_diagnosis(
            obj=obj,
            indent_level_outer=indent_level_outer,
            indent_level_inner=indent_level_inner_nested,
        )

        # Line diagnosing this object against this passed second child
        # validator, with an increased indentation level for readability.
        line_inner_operand_2 = self._validator_operand_2.get_diagnosis(
            obj=obj,
            indent_level_outer=indent_level_outer,
            indent_level_inner=indent_level_inner_nested,
        )

        # Line providing the suffixing ")" delimiter for readability.
        line_outer_suffix = format_diagnosis_line(
            validator_repr=')',
            indent_level_outer=indent_level_outer,
            indent_level_inner=indent_level_inner,
        )

        # Return these lines concatenated.
        return (
            f'{line_outer_prefix}\n'
            f'{line_inner_operand_1} &\n'
            f'{line_inner_operand_2}\n'
            f'{line_outer_suffix}'
        )


class BeartypeValidatorDisjunction(BeartypeValidatorBinary):
    '''
    **Disjunction beartype validator** (i.e., validator disjunctively
    evaluating the boolean truthiness returned by the validation performed by a
    pair of lower-level beartype validators, typically instantiated and
    returned by the :meth:`BeartypeValidator.__and__` dunder method of the
    first validator passed the second).
    '''

    # ..................{ GETTERS                           }..................
    #FIXME: Unit test us up, please.
    #FIXME: This violates DRY with the get_diagnosis() method defined above.
    #FIXME: Overly verbose output for disjunctions involving three or more
    #beartype validators. Contemplate compaction schemes, please. Specifically,
    #we need to detect this condition here and then compact based on that:
    #    # If either of these validators are themselves conjunctions...
    #    if isinstance(self._validator_operand_1, BeartypeValidatorDisjunction):
    #       ...
    #    if isinstance(self._validator_operand_2, BeartypeValidatorDisjunction):
    #       ...
    def get_diagnosis(
        self,
        obj: object,
        indent_level_outer: str,
        indent_level_inner: str,
    ) -> str:

        # Innermost indentation level indented one level deeper than the passed
        # innermost indentation level.
        indent_level_inner_nested = indent_level_inner + CODE_INDENT_1

        # Line diagnosing this object against this parent disjunction.
        line_outer_prefix = format_diagnosis_line(
            validator_repr='(',
            indent_level_outer=indent_level_outer,
            indent_level_inner=indent_level_inner,
            is_obj_valid=self.is_valid(obj),
        )

        # Line diagnosing this object against this original first child
        # validator, with an increased indentation level for readability.
        line_inner_operand_1 = self._validator_operand_1.get_diagnosis(
            obj=obj,
            indent_level_outer=indent_level_outer,
            indent_level_inner=indent_level_inner_nested,
        )

        # Line diagnosing this object against this passed second child
        # validator, with an increased indentation level for readability.
        line_inner_operand_2 = self._validator_operand_2.get_diagnosis(
            obj=obj,
            indent_level_outer=indent_level_outer,
            indent_level_inner=indent_level_inner_nested,
        )

        # Line providing the suffixing ")" delimiter for readability.
        line_outer_suffix = format_diagnosis_line(
            validator_repr=')',
            indent_level_outer=indent_level_outer,
            indent_level_inner=indent_level_inner,
        )

        # Return these lines concatenated.
        return (
            f'{line_outer_prefix}\n'
            f'{line_inner_operand_1} |\n'
            f'{line_inner_operand_2}\n'
            f'{line_outer_suffix}'
        )
