#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2021 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype core validation classes.**

This private submodule defines the core low-level class hierarchy driving the
entire :mod:`beartype` validation ecosystem.

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ TODO                              }....................
# All "FIXME:" comments for this submodule reside in this package's "__init__"
# submodule to improve maintainability and readability here.

# ....................{ IMPORTS                           }....................
from beartype.roar import BeartypeValeSubscriptionException
from beartype._util.kind.utilkinddict import merge_mappings_two
from beartype._util.func.utilfuncarg import (
    die_unless_func_args_len_flexible_equal,
    is_func_argless,
)
from beartype._util.func.utilfuncscope import CallableScope
from beartype._util.text.utiltextrepr import represent_object
from typing import Any, Callable, Union

# See the "beartype.cave" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ HINTS                             }....................
SubscriptedIsValidator = Callable[[Any,], bool]
'''
PEP-compliant type hint matching a **validator** (i.e., caller-defined callable
accepting a single arbitrary object and returning either ``True`` if that
object satisfies an arbitrary constraint *or* ``False`` otherwise).

Validators are suitable for subscripting the :class:`Is` class.
'''


SubscriptedIsRepresenter = Union[str, Callable[[], str]]
'''
**Representer** (i.e., either a string *or* caller-defined callable accepting
no arguments returning a machine-readable representation of this validator).

Technically, this representation *could* be passed by the caller rather than
this callable dynamically generating that representation. Pragmatically,
generating this representation is sufficiently slow for numerous types of
validators that deferring their generation until required by a call to the
:meth:`__repr__` dunder method externally called by a call to the :func:`repr`
builtin` on this validator is effectively mandatory. Data validators whose
representations are particularly slow to generate include:

* The :class:`Is` class subscripted by a lambda rather than non-lambda
  function. Generating the representation of that class subscripted by a
  non-lambda function only requires introspecting the name of that function and
  is thus trivially fast. However, lambda functions have no names and are thus
  *only* distinguishable by their source code; generating the representation of
  that class subscripted by a lambda function requires parsing the source code
  of the file declaring that lambda for the exact substring of that code
  declaring that lambda.
'''

# ....................{ CLASSES ~ subscripted             }....................
class _SubscriptedIs(object):
    '''
    **Beartype validator** (i.e., object encapsulating a caller-defined
    validation callable returning ``True`` when an arbitrary object passed to
    that callable satisfies an arbitrary constraint, suitable for subscripting
    (indexing) :pep:`593`-compliant :attr:`typing.Annotated` type hints
    enforcing that validation on :mod:`beartype`-decorated callable parameters
    and returns annotated by those hints).

    Caveats
    ----------
    **This private class is not intended to be externally instantiated** (e.g.,
    by calling the :meth:`__init__` constructor). This class is *only* intended
    to be internally instantiated by subscripting (indexing) various public
    type hint factories (e.g., :class:`beartype.vale.Is`).

    Attributes
    ----------
    _is_valid : SubscriptedIsValidator
        **Validator** (i.e., caller-defined callable accepting a single
        arbitrary object and returning either ``True`` if that object satisfies
        an arbitrary constraint *or* ``False`` otherwise).
    _is_valid_code : str
        **Validator code** (i.e., Python code snippet validating the
        previously localized parameter or return value against the same
        validation performed by the :meth:`is_valid` function). For efficiency,
        callers validating data through dynamically generated code (e.g., the
        :func:`beartype.beartype` decorator) rather than standard function
        calls (e.g., the private :mod:`beartype._decor._hint._pep._error`
        subpackage) should prefer :attr:`is_valid_code` to :meth:`is_valid`.
        Despite performing the same validation as the :meth:`is_valid`
        callable, this code avoids the additional stack frame imposed by
        calling that callable and thus constitutes an optimization.
    _is_valid_code_locals : CallableScope
        **Validator code local scope** (i.e., dictionary mapping from the name
        to value of each local attribute referenced in :attr:`code`) required
        to dynamically compile this validator code into byte code at runtime.
    _get_repr : SubscriptedIsRepresenter
        **Representer** (i.e., either a string *or* caller-defined callable
        accepting no arguments returning a machine-readable representation of
        this validator). See the :data:`SubscriptedIsRepresenter` type hint for
        further details.

    See Also
    ----------
    :class:`Is`
        Class docstring for further details.
    '''

    # ..................{ CLASS VARIABLES                   }..................
    # Slot all instance variables defined on this object to minimize the time
    # complexity of both reading and writing variables across frequently called
    # cache dunder methods. Slotting has been shown to reduce read and write
    # costs by approximately ~10%, which is non-trivial.
    __slots__ = (
        '_is_valid',
        '_is_valid_code',
        '_is_valid_code_locals',
        '_get_repr',
    )

    # ..................{ INITIALIZERS                      }..................
    def __init__(
        self,
        is_valid: SubscriptedIsValidator,
        is_valid_code: str,
        is_valid_code_locals: CallableScope,
        get_repr: SubscriptedIsRepresenter,
    ) -> None:
        '''
        Initialize this object with the passed validation callable, code, and
        code local scope.

        See the class docstring for usage instructions.

        Parameters
        ----------
        is_valid : SubscriptedIsValidator
            **Validator** (i.e., caller-defined callable accepting a single
            arbitrary object and returning either ``True`` if that object
            satisfies an arbitrary constraint *or* ``False`` otherwise).
        is_valid_code : str
            **Validator code** (i.e., Python code snippet validating the
            previously localized parameter or return value against the same
            validation performed by the :func:`is_valid` function). This code:

            * *Must* contain one or more ``"{obj}"`` substrings, which external
              code generators (e.g., the :func:`beartype.beartype` decorator)
              will globally replace at evaluation time with the actual test
              subject object to be validated by this code.
            * *May* contain one or more ``"{indent}"`` substrings, which such
              code generators will globally replace at evaluation time with the
              line-oriented indentation required to generate a
              valid Python statement embedding this code. For consistency with
              :pep:`8`-compliant and well-established Python style guides, any
              additional indentation hard-coded into this code should be
              aligned to **four-space indentation.**
        is_valid_code_locals : Optional[CallableScope]
            **Validator code local scope** (i.e., dictionary mapping from the
            name to value of each local attribute referenced in
            :attr:`is_valid_code` code) required to dynamically compile this
            validator code into byte code at runtime.
        get_repr : SubscriptedIsRepresenter
            **Representer** (i.e., either a string *or* caller-defined callable
            accepting no arguments returning a machine-readable representation
            of this validator). See the :data:`SubscriptedIsRepresenter` type
            hint for further details.

        Raises
        ----------
        BeartypeValeSubscriptionException
            If either:

            * ``is_valid`` is either:

              * *Not* callable.
              * A C-based rather than pure-Python callable.
              * A pure-Python callable accepting two or more arguments.

            * ``is_valid_code`` is either:

              * *Not* a string.
              * A string either:

                * Empty.
                * Non-empty but **invalid** (i.e., *not* containing the test
                  subject substring ``{obj}``).

            * ``is_valid_locals`` is *not* a dictionary.
            * ``get_repr`` is either:

              * *Not* callable.
              * A C-based rather than pure-Python callable.
              * A pure-Python callable accepting one or more arguments.
        '''

        # If this validator is either uncallable, a C-based callable, *OR* a
        # pure-Python callable accepting more or less than one parameter, raise
        # an exception.
        die_unless_func_args_len_flexible_equal(
            func=is_valid,
            func_args_len_flexible=1,
            func_label=(
                f'Class "beartype.vale.Is" subscripted argument '
                f'{repr(is_valid)}'
            ),
            exception_cls=BeartypeValeSubscriptionException,
        )
        # Else, this validator is a pure-Python callable accepting exactly one
        # argument. Since no further validation can be performed on this
        # callable without unsafely calling that callable, we accept this
        # callable as is for now.
        #
        # Note that we *COULD* technically inspect annotations if defined on
        # this callable as well. Since this callable is typically defined as a
        # lambda, annotations are typically *NOT* defined on this callable.

        # If this code is *NOT* a string, raise an exception.
        if not isinstance(is_valid_code, str):
            raise BeartypeValeSubscriptionException(
                f'Data validator code not string:\n'
                f'{represent_object(is_valid_code)}'
            )
        # Else, this code is a string.
        #
        # If this code is the empty string, raise an exception.
        elif not is_valid_code:
            raise BeartypeValeSubscriptionException(
                'Data validator code empty.')
        # Else, this code is a non-empty string.
        #
        # If this code does *NOT* contain the test subject substring
        # "{obj}" and is invalid, raise an exception.
        elif '{obj}' not in is_valid_code:
            raise BeartypeValeSubscriptionException(
                f'Data validator code invalid (i.e., test subject '
                f'substring "{{obj}}" not found):\n{is_valid_code}'
            )
        # Else, this code is hopefully valid.
        #
        # If this code is *NOT* explicitly prefixed by "(" and suffixed by
        # ")", do so to ensure this code remains safely evaluable when
        # embedded in parent expressions.
        elif not (
            is_valid_code[ 0] == '(' and
            is_valid_code[-1] == ')'
        ):
            is_valid_code = f'({is_valid_code})'
        # Else, this code is explicitly prefixed by "(" and suffixed by ")".

        # If this dictionary of code locals is *NOT* a dictionary, raise an
        # exception.
        if not isinstance(is_valid_code_locals, dict):
            raise BeartypeValeSubscriptionException(
                f'Data validator locals '
                f'{represent_object(is_valid_code_locals)} not '
                f'dictionary.'
            )
        # Else, this dictionary of code locals is a dictionary.

        # Classify this validator, effectively binding this callable to this
        # object as an object-specific static method.
        self._is_valid = is_valid

        # Classify this representer via a writeable property internally
        # validating this representer.
        self.get_repr = get_repr

        # Classify all remaining parameters.
        self._is_valid_code = is_valid_code
        self._is_valid_code_locals = is_valid_code_locals

    # ..................{ PROPERTIES ~ read-only            }..................
    # Properties with no corresponding setter and thus read-only.

    @property
    def is_valid(self) -> SubscriptedIsValidator:
        '''
        **Validator** (i.e., caller-defined callable accepting a single
        arbitrary object and returning either ``True`` if that object satisfies
        an arbitrary constraint *or* ``False`` otherwise).
        '''

        return self._is_valid

    # ..................{ PROPERTIES ~ writeable            }..................
    # Properties with a corresponding setter and thus writeable.

    @property
    def get_repr(self) -> SubscriptedIsRepresenter:
        '''
        **Representer** (i.e., either a string *or* caller-defined callable
        accepting no arguments returning a machine-readable representation of
        this validator). See the :data:`SubscriptedIsRepresenter` type hint for
        further details.
        '''

        return self._get_repr


    @get_repr.setter
    def get_repr(self, get_repr: SubscriptedIsRepresenter) -> None:
        '''
        Override the initial representer for this validator.

        Parameters
        ----------
        get_repr : SubscriptedIsRepresenter
            **Representer** (i.e., either a string *or* caller-defined callable
            accepting no arguments returning a machine-readable representation
            of this validator). See the :data:`SubscriptedIsRepresenter` type
            hint for further details.

        Raises
        ----------
        :exc:`BeartypeValeSubscriptionException`
            This representer is either:

            * *Not* callable.
            * A C-based rather than pure-Python callable.
            * A pure-Python callable accepting one or more arguments.
        '''

        # If this representer is neither...
        if not (
            # A string *NOR*...
            isinstance(get_repr, str) or
            # A pure-Python callable accepting one argument...
            is_func_argless(
                func=get_repr,
                func_label='Representer',
                exception_cls=BeartypeValeSubscriptionException,
            )
        # Then raise an exception.
        ):
            raise BeartypeValeSubscriptionException(
                f'Representer {repr(get_repr)} neither string nor '
                f'argument-less pure-Python callable.'
            )
        # Else, this representer is an argument-less pure-Python callable.

        # Set this representer.
        self._get_repr = get_repr

    # ..................{ DUNDERS ~ operator                }..................
    # Define a domain-specific language (DSL) enabling callers to dynamically
    # combine and Override
    def __and__(self, other: '_SubscriptedIs') -> (
        '_SubscriptedIs'):
        '''
        **Conjunction** (i.e., ``self & other``), synthesizing a new
        :class:`_SubscriptedIs` object whose validator returns ``True`` only
        when the validators of both this *and* the passed
        :class:`_SubscriptedIs` objects all return ``True``.

        Parameters
        ----------
        other : _SubscriptedIs
            Object to conjunctively synthesize with this object.

        Returns
        ----------
        _SubscriptedIs
            New object conjunctively synthesized with this object.

        Raises
        ----------
        BeartypeValeSubscriptionException
            If the passed object is *not* also an instance of the same class.
        '''

        # If the passed object is *NOT* also an instance of this class, raise
        # an exception.
        if not isinstance(other, _SubscriptedIs):
            raise BeartypeValeSubscriptionException(
                f'Subscripted "beartype.vale.Is*" class & operand '
                f'{represent_object(other)} not '
                f'subscripted "beartype.vale.Is*" class.'
            )
        # Else, the passed object is also an instance of this class.

        # Generate code conjunctively performing both validations.
        is_valid_code = f'({self._is_valid_code} and {other._is_valid_code})'

        # Generate locals safely merging the locals required by the code
        # provided by both this and that validator.
        is_valid_code_locals = merge_mappings_two(
            self._is_valid_code_locals, other._is_valid_code_locals)

        # Closures for great justice.
        return _SubscriptedIs(
            is_valid=lambda obj: self.is_valid(obj) and other.is_valid(obj),
            is_valid_code=is_valid_code,
            is_valid_code_locals=is_valid_code_locals,  # type: ignore[arg-type]
            get_repr=lambda: f'{repr(self)} & {repr(other)}',
        )


    def __or__(self, other: '_SubscriptedIs') -> (
        '_SubscriptedIs'):
        '''
        **Disjunction** (i.e., ``self | other``), synthesizing a new
        :class:`_SubscriptedIs` object whose validator returns ``True`` only
        when the validators of either this *or* the passed
        :class:`_SubscriptedIs` objects return ``True``.

        Parameters
        ----------
        other : _SubscriptedIs
            Object to disjunctively synthesize with this object.

        Returns
        ----------
        _SubscriptedIs
            New object disjunctively synthesized with this object.
        '''

        # If the passed object is *NOT* also an instance of this class, raise
        # an exception.
        if not isinstance(other, _SubscriptedIs):
            raise BeartypeValeSubscriptionException(
                f'Subscripted "beartype.vale.Is*" class | operand '
                f'{represent_object(other)} not '
                f'subscripted "beartype.vale.Is*" class.'
            )
        # Else, the passed object is also an instance of this class.

        # Generate code disjunctively performing both validations.
        is_valid_code = f'({self._is_valid_code} or {other._is_valid_code})'

        # Generate locals safely merging the locals required by the code
        # provided by both this and that validator.
        is_valid_code_locals = merge_mappings_two(
            self._is_valid_code_locals, other._is_valid_code_locals)

        # Closures for great justice.
        return _SubscriptedIs(
            is_valid=lambda obj: self.is_valid(obj) or other.is_valid(obj),
            is_valid_code=is_valid_code,
            is_valid_code_locals=is_valid_code_locals,  # type: ignore[arg-type]
            get_repr=lambda: f'{repr(self)} | {repr(other)}',
        )


    #FIXME: Fun optimization: if inverting something that's already been
    #inverted, return the original "_SubscriptedIs" object sans inversion. :p
    def __invert__(self) -> '_SubscriptedIs':
        '''
        **Negation** (i.e., ``~self``), synthesizing a new
        :class:`_SubscriptedIs` object whose validator returns ``True`` only
        when the validators of this :class:`_SubscriptedIs` object returns
        ``False``.

        Returns
        ----------
        _SubscriptedIs
            New object negating this object.
        '''

        # Closures for profound lore.
        return _SubscriptedIs(
            is_valid=lambda obj: not self.is_valid(obj),
            # Inverted validator code, defined as the trivial boolean negation
            # of this validator.
            is_valid_code=f'(not {self._is_valid_code})',
            is_valid_code_locals=self._is_valid_code_locals,
            get_repr=lambda: f'~{repr(self)}',
        )

    # ..................{ DUNDERS ~ str                     }..................
    def __repr__(self) -> str:
        '''
        Machine-readable representation of this validator.

        This function is memoized for efficiency.

        Warns
        ----------
        BeartypeValeLambdaWarning
            If this validator is implemented as a pure-Python lambda function
            whose definition is *not* parsable from the script or module
            defining that lambda.
        '''

        # If the instance variable underlying this dunder method is a callable,
        # reduce this variable to the string returned by this callable.
        if callable(self._get_repr):
            self._get_repr = self._get_repr()

        # In either case, this variable is now a string. Guarantee this.
        assert isinstance(self._get_repr, str), f'{self._get_repr} not string.'

        # Return this string as is.
        return self._get_repr
