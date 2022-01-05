#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2022 Beartype authors.
# See "LICENSE" for further details.

'''
**Core unary beartype validators** (i.e., :class:`BeartypeValidator` subclasses
implementing unary operations on a single lower-level beartype validator).

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
class BeartypeValidatorUnary(BeartypeValidator):
    '''
    **Unary beartype validator** (i.e., validator modifying the boolean
    truthiness returned by the validation performed by a single lower-level
    beartype validator).

    Attributes
    ----------
    _validator_operand : BeartypeValidator
        Lower-level validator operated upon by this higher-level validator.
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
        '_validator_operand',
    )

    # ..................{ INITIALIZERS                      }..................
    def __init__(
        self,

        # Mandatory parameters.
        validator_operand: BeartypeValidator,
        *args,
        **kwargs
    ) -> None:
        '''
        Initialize this validator from the passed metadata.

        Parameters
        ----------
        validator_operand : BeartypeValidator
            Lower-level validator operated upon by this higher-level validator.

        Raises
        ----------
        BeartypeValeSubscriptionException
            If this operand is *not* itself a beartype validator.
        '''

        # Initialize our superclass with all remaining parameters.
        super().__init__(*args, **kwargs)

        #FIXME: Unit test us up, please.
        # If this operand is *NOT* a beartype validator, raise an exception.
        if not isinstance(validator_operand, BeartypeValidator):
            raise BeartypeValeSubscriptionException(
                f'Unary binary validator {repr(self)} operand '
                f'{represent_object(validator_operand)} not beartype '
                f'validator (i.e., "beartype.vale.Is*[...]" object).'
            )
        # Else, this operand is a beartype validator.

        # Classify this operand.
        self._validator_operand = validator_operand

# ....................{ SUBCLASSES                        }....................
class BeartypeValidatorNegation(BeartypeValidatorUnary):
    '''
    **Negation beartype validator** (i.e., validator negating the boolean
    truthiness returned by the validation performed by a lower-level beartype
    validator, typically instantiated and returned by the
    :meth:`BeartypeValidator.__invert__` dunder method of that validator).
    '''

    # ..................{ GETTERS                           }..................
    #FIXME: Unit test us up, please.
    def get_diagnosis(
        self,
        obj: object,
        indent_level_outer: str,
        indent_level_inner: str,
    ) -> str:

        # Line diagnosing this object against this negated parent validator.
        line_outer_prefix = format_diagnosis_line(
            validator_repr='~(',
            indent_level_outer=indent_level_outer,
            indent_level_inner=indent_level_inner,
            is_obj_valid=self.is_valid(obj),
        )

        # Line diagnosing this object against this non-negated child validator
        # with an increased indentation level for readability.
        line_inner_operand = self._validator_operand.get_diagnosis(
            obj=obj,
            indent_level_outer=indent_level_outer,
            indent_level_inner=indent_level_inner + CODE_INDENT_1,
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
            f'{line_inner_operand}\n'
            f'{line_outer_suffix}'
        )
