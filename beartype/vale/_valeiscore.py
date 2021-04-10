#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2021 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype core data validation classes.**

This private submodule defines the core low-level class hierarchy driving the
entire :mod:`beartype` data validation ecosystem.

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ TODO                              }....................
# All "FIXME:" comments for this submodule reside in this package's "__init__"
# submodule to improve maintainability and readability here.

# ....................{ IMPORTS                           }....................
from beartype.roar import BeartypeAnnotatedIsCoreException
from beartype._util.func.utilfuncarg import get_func_args_len_standard
from beartype._util.func.utilfunctest import is_func_python
from beartype._util.hint.pep.proposal.utilhintpep593 import (
    die_unless_hint_pep593)
from beartype._util.text.utiltextrepr import get_object_representation
from typing import Any, Callable

# See the "beartype.cave" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ HINTS                             }....................
AnnotatedIsValidator = Callable[[Any,], bool]
'''
PEP-compliant type hint matching a **data validator** (i.e., caller-defined
function accepting a single arbitrary object and returning either ``True`` if
that object satisfies an arbitrary constraint or ``False`` otherwise).

Data validators are suitable for subscripting the :class:`Is` class.
'''

# ....................{ CLASSES                           }....................
#FIXME: Handle subscriptions of this class from "_pephint" on each argument of
#an "Annotated" type hint to detect whether that argument is a "Is"
#subscription. Specifically:
#* Amend the "_pephint" BFS like so:
#    #FIXME: Implement similar checking in the "_error" subpackage. *sigh*
#    func_curr_code = ''
#
#    for hint_child in hint_curr.__args__[1:]:
#        if not isinstance(hint_child, AnnotatedIs):
#            continue
#
#        hint_child_arg_name = _ARG_NAME_CUSTOM_OBJECT_format(
#            object_id=id(hint_child))
#
#        func_curr_code += _PEP_CODE_CHECK_HINT_ANNOTATED_IS_CHILD_format(
#            pith_curr_assigned_expr=pith_curr_assigned_expr,
#            hint_child_arg_name=hint_child_arg_name,
#        )
#
#        func_wrapper_locals[hint_child_arg_name] = hint_child.is_valid
#
#    if func_curr_code:
#        func_curr_code = (
#             # Prefix this code by the substring prefixing all such code.
#            _PEP_CODE_CHECK_HINT_ANNOTATED_IS_PREFIX_format(
#                pith_curr_assign_expr=pith_curr_assign_expr,
#                hint_curr_expr=hint_curr_expr,
#            # Strip the erroneous " and" suffix appended by the last
#            # child hint from this code.
#            ) + func_curr_code[:-_OPERATOR_SUFFIX_LEN_AND]'
#        # Format the "indent_curr" prefix into this code deferred
#        # above for efficiency.
#        ).format(indent_curr=indent_curr)
#
#That should do it, in theory. Yay!

class AnnotatedIs(object):
    '''
    **Beartype data validator** (i.e., object encapsulating a caller-defined
    data validation function returning ``True`` when an arbitrary object passed
    to that function satisfies an arbitrary constraint, suitable for
    subscripting (indexing) `PEP 593`_-compliant :attr:`typing.Annotated` type
    hints, which then enforce that validation on :mod:`beartype`-decorated
    callable parameters and returns annotated by those hints).

    Caveats
    ----------
    **This class is not intended to be externally instantiated** (e.g., by
    calling the :meth:`__init__` constructor). This low-level class is *only*
    intended to be internally instantiated by subscripting (indexing) the
    higher-level :class:`Is` class factory.

    Attributes
    ----------
    is_valid : Callable[[Any,], bool]
        **Data validator** (i.e., caller-defined function accepting a single
        arbitrary object and returning either ``True`` if that object satisfies
        an arbitrary constraint *or* ``False`` otherwise).

    See Also
    ----------
    :class:`Is`
        Class docstring for further details.

    .. _PEP 593:
       https://www.python.org/dev/peps/pep-0593
    '''

    # ..................{ CLASS VARIABLES                   }..................
    # Slot all instance variables defined on this object to minimize the time
    # complexity of both reading and writing variables across frequently called
    # cache dunder methods. Slotting has been shown to reduce read and write
    # costs by approximately ~10%, which is non-trivial.
    __slots__ = ('is_valid',)

    # ..................{ INITIALIZERS                      }..................
    def __init__(self, validator: AnnotatedIsValidator) -> None:
        '''
        Initialize this object with the passed data validation function.

        See the class docstring for usage instructions.

        Parameters
        ----------
        validator : Callable[[Any,], bool]
            **Data validator** (i.e., caller-defined function accepting a
            single arbitrary object and returning either ``True`` if that
            object satisfies an arbitrary constraint *or* ``False`` otherwise).

        Raises
        ----------
        BeartypeAnnotatedIsCoreException
            If either:

            * This class was subscripted by two or more arguments.
            * This class was subscripted by one argument that either:

              * Is *not* callable.
              * Is a C-based rather than pure-Python callable.
              * Is a pure-Python callable accepting two or more arguments.
        '''

        # If this class was subscripted by either no arguments or two or more
        # arguments...
        if isinstance(validator, tuple):
            # If this class was subscripted by two or more arguments, raise a
            # human-readable exception.
            if validator:
                raise BeartypeAnnotatedIsCoreException(
                    f'Class "beartype.vale.Is" subscripted by two or more '
                    f'arguments:\n{get_object_representation(validator)}'
                )
            # Else, this class was subscripted by *NO* arguments. In this case,
            # raise a human-readable exception.
            else:
                raise BeartypeAnnotatedIsCoreException(
                    'Class "beartype.vale.Is" subscripted by empty tuple.')
        # Else, the this class was subscripted by a single argument.
        #
        # If this argument is uncallable, raise a human-readable exception.
        elif not callable(validator):
            raise BeartypeAnnotatedIsCoreException(
                f'Class "beartype.vale.Is" subscripted argument '
                f'{get_object_representation(validator)} not callable.'
            )
        # Else, this argument is callable.
        #
        # If this callable is C-based, raise a human-readable exception.
        elif not is_func_python(validator):
            raise BeartypeAnnotatedIsCoreException(
                f'Class "beartype.vale.Is" subscripted callable '
                f'{repr(validator)} not pure-Python (e.g., C-based).'
            )
        # Else, this callable is pure-Python.
        #
        # If this callable does *NOT* accept exactly one argument, raise a
        # human-readable exception.
        elif get_func_args_len_standard(validator) != 1:
            raise BeartypeAnnotatedIsCoreException(
                f'Class "beartype.vale.Is" subscripted callable '
                f'{repr(validator)} positional or keyword argument count '
                f'{get_func_args_len_standard(validator)} != 1.'
            )
        # Else, this callable accepts exactly one argument. Since no further
        # validation can be performed on this callable without unsafely calling
        # that callable, we accept this callable as is for now.
        #
        # Note that we *COULD* technically inspect annotations if defined on
        # this callable as well. Since this callable is typically defined as a
        # lambda, annotations are typically *NOT* defined on this callable.

        # Classify this data validation function, effectively binding this
        # function to this object as an object-specific static method.
        self.is_valid = validator

    # ..................{ OPERATORS                         }..................
    # Define a domain-specific language (DSL) enabling callers to dynamically
    # combine and Override
    def __and__(self, other: 'AnnotatedIs') -> (
        'AnnotatedIs'):
        '''
        **Conjunction** (i.e., ``self & other``), synthesizing a new
        :class:`AnnotatedIs` object whose data validator returns ``True`` only
        when the data validators of both this *and* the passed
        :class:`AnnotatedIs` objects all return ``True``.

        Parameters
        ----------
        other : AnnotatedIs
            Object to conjunctively synthesize with this object.

        Returns
        ----------
        AnnotatedIs
            New object conjunctively synthesized with this object.

        Raises
        ----------
        BeartypeAnnotatedIsCoreException
            If the passed object is *not* also an instance of the same class.
        '''

        # If the passed object is *NOT* also an instance of this class, raise
        # an exception.
        if not isinstance(other, AnnotatedIs):
            raise BeartypeAnnotatedIsCoreException(
                f'Second & operand {get_object_representation(other)} not '
                f'"AnnotatedIs" instance.'
            )
        # Else, the passed object is also an instance of this class.

        # Closures for great justice.
        return AnnotatedIs(
            lambda obj: self.is_valid(obj) and other.is_valid(obj))


    def __or__(self, other: 'AnnotatedIs') -> (
        'AnnotatedIs'):
        '''
        **Disjunction** (i.e., ``self | other``), synthesizing a new
        :class:`AnnotatedIs` object whose data validator returns ``True`` only
        when the data validators of either this *or* the passed
        :class:`AnnotatedIs` objects return ``True``.

        Parameters
        ----------
        other : AnnotatedIs
            Object to disjunctively synthesize with this object.

        Returns
        ----------
        AnnotatedIs
            New object disjunctively synthesized with this object.
        '''

        # If the passed object is *NOT* also an instance of this class, raise
        # an exception.
        if not isinstance(other, AnnotatedIs):
            raise BeartypeAnnotatedIsCoreException(
                f'Second | operand {get_object_representation(other)} not '
                f'"AnnotatedIs" instance.'
            )
        # Else, the passed object is also an instance of this class.

        # Closures for extreme glory.
        return AnnotatedIs(
            lambda obj: self.is_valid(obj) or other.is_valid(obj))


    def __invert__(self) -> 'AnnotatedIs':
        '''
        **Negation** (i.e., ``~self``), synthesizing a new :class:`AnnotatedIs`
        object whose data validator returns ``True`` only when the data
        validators of this :class:`AnnotatedIs` object returns ``False``.

        Returns
        ----------
        AnnotatedIs
            New object negating this object.
        '''

        # Closures for profound lore.
        return AnnotatedIs(lambda obj: not self.is_valid(obj))


class Is(object):
    '''
    **Beartype data validator factory** (i.e., class that, when subscripted
    (indexed) by a caller-defined data validation function returning ``True``
    when an arbitrary object passed to that function satisfies an arbitrary
    constraint, creates a new :class:`AnnotatedIs` object encapsulating that
    function suitable for subscripting (indexing) :attr:`typing.Annotated` type
    hints, which then enforce that validation on :mod:`beartype`-decorated
    callable parameters and returns annotated by those hints).

    Subscripting (indexing) this class produces an :class:`AnnotatedIs`
    object that validates the internal integrity, consistency, and structure of
    arbitrary objects ranging from simple builtin scalars like integers and
    strings to complex data structures defined by third-party packages like
    NumPy arrays and Pandas DataFrames. For portability, :class:`AnnotatedIs`
    objects are:

    * **PEP-compliant** and thus guaranteed to *never* violate existing or
      future standards.
    * **Safely ignorable** by *all* static and runtime type checkers other than
      :mod:`beartype` itself.

    Usage
    ----------
    Callers are expected to (in order):

    #. Annotate a callable parameter or return to be validated with a `PEP
       593`_-compliant :attr:`typing.Annotated` type hint.
    #. Subscript that hint with (in order):

       #. The type expected by that parameter or return.
       #. One or more subscriptions (indexations) of this class, each itself
          subscripted (indexed) by a **data validator** (i.e., function
          accepting a single arbitrary object and returning either ``True`` if
          that object satisfies an arbitrary constraint *or* ``False``
          otherwise). If that hint is subscripted by:

          * Only one subscription of this class, that parameter or return
            satisfies that hint when both:

            * That parameter or return is an instance of the expected type.
            * That data validator returns ``True`` when passed that parameter
              or return.

          * Two or more subscriptions of this class, that parameter or return
            satisfies that hint when both:

            * That parameter or return is an instance of the expected type.
            * *All* data validators subscripting *all* subscriptions of this
              class return ``True`` when passed that parameter or return.

          Formally, the signature of each data validator *must* resemble:

          .. _code-block:: python

             def is_object_valid(obj) -> bool:
                 return bool(obj)

          Equivalently, each validator *must* satisfy the type hint
          ``collections.abc.Callable[[typing.Any,], bool]``. If not the case,
          an exception is raised. Note that:

          * If that parameter or return is *not* an instance of the expected
            type, **no validator is called.** Equivalently, each validator is
            called *only* when that parameter or return is already an instance
            of the expected type. Validators need *not* revalidate that type
            (e.g., by passing that parameter or return and type to the
            :func:`isinstance` builtin).
          * The name of each validator is irrelevant. For convenience, most
            validators are defined as nameless lambda functions.

    For example, the following type hint only accepts non-empty strings:

    .. _code-block:: python

       Annotated[str, Is[lambda text: bool(text)]]

    :class:`AnnotatedIs` objects also support an expressive domain-specific
    language (DSL) enabling callers to trivially synthesize new objects from
    existing objects with standard Pythonic math operators:

    * **Negation** (i.e., ``not``). Negating an :class:`AnnotatedIs` object
      with the ``~`` operator synthesizes a new :class:`AnnotatedIs` object
      whose data validator returns ``True`` only when the data validator of the
      original object returns ``False``. For example, the following type hint
      only accepts strings containing *no* periods:

      .. _code-block:: python

         Annotated[str, ~Is[lambda text: '.' in text]]

    * **Conjunction** (i.e., ``and``). Conjunctively combining two or more
      :class:`AnnotatedIs` objects with the ``&`` operator synthesizes a new
      :class:`AnnotatedIs` object whose data validator returns ``True`` only
      when all data validators of the original objects return ``True``. For
      example, the following type hint only accepts non-empty strings
      containing *no* periods:

      .. _code-block:: python

         Annotated[str, (
              Is[lambda text: bool(text)] &
             ~Is[lambda text: '.' in text]
         )]

    * **Disjunction** (i.e., ``or``). Disjunctively combining two or more
      subscriptions with the ``|`` operator returns ``True`` only when at least
      one subscription returns ``True``. For example, this type hint accepts
      both empty strings *and* non-empty strings containing at least one
      period:
    * **Disjunction** (i.e., ``or``). Disjunctively combining two or more
      :class:`AnnotatedIs` objects with the ``|`` operator synthesizes a new
      :class:`AnnotatedIs` object whose data validator returns ``True`` only
      when at least one data validator of the original objects returns
      ``True``. For example, the following type hint accepts both empty strings
      *and* non-empty strings containing at least one period:

      .. _code-block:: python

         Annotated[str, (
             ~Is[lambda text: bool(text)] |
              Is[lambda text: '.' in text]
         )]

    See also the **Examples** subsection below.

    Caveats
    ----------
    **This class is currently only supported by the** :func:`beartype.beartype`
    **decorator.** All other static and runtime type checkers silently ignore
    subscriptions of this class subscripting :attr:`typing.Annotated` type
    hints.

    **This class incurs a minor time complexity cost at call time.**
    Specifically, each type hint of a :mod:`beartype`-decorated callable
    subscripted by a subscription of this class adds one additional stack frame
    to each call of that callable. While negligible (in the average case), this
    cost can become non-negligible when compounded across multiple type hints
    annotating a frequently called :mod:`beartype`-decorated callable --
    especially when those type hints are subscripted by multiple subscriptions
    of this class at different nesting levels.

    **This class prohibits instantiation.** This class is *only* intended to be
    subscripted. Attempting to instantiate this class into an object will raise
    an :exc:`BeartypeAnnotatedIsCoreException` exception.

    Examples
    ----------
    .. _code-block:: python

       from beartype import beartype
       from beartype.vale import Is
       from typing import Annotated

       IsUnquoted = Is[lambda text: '"' not in text and "'" not in text]
       """
       Constraint matching only unquoted strings.
       """

       UnquotedString = Annotated[str, IsUnquoted]
       """
       Type hint matching only unquoted strings.
       """

       @beartype
       def quote_text(text: UnquotedString) -> str:
           """
           Double-quote the passed unquoted string.
           """

           return f'"{text}"'

       IsLengthy = Is[lambda text: 4 <= len(text) <= 14]
       """
       Constraint matching only strings with lengths ranging ``[4, 14]``
       (inclusive).
       """

       UnquotedLengthyString = Annotated[str, IsUnquoted, IsLengthy]
       """
       Type hint matching only unquoted strings with lengths ranging ``[4,
       14]`` (inclusive).
       """

       @beartype
       def snip_text(text: UnquotedLengthyString) -> UnquotedString:
           """
           Return the prefix spanning characters ``[0, 3]`` (inclusive) of the
           passed unquoted string with a length ranging ``[4, 14]``
           (inclusive).
           """

           # "This is guaranteed to work," says beartype.
           return text[:3]

    .. _PEP 593:
       https://www.python.org/dev/peps/pep-0593
    '''

    # ..................{ INITIALIZERS                      }..................
    def __new__(cls, *args, **kwargs):
        '''
        Prohibit direct instantiation by unconditionally raising an exception.

        Like standard type hints (e.g., :attr:`typing.Union`), this class is
        *only* intended to be subscripted (indexed).

        Raises
        ----------
        BeartypeAnnotatedIsCoreException
            Always.
        '''

        # Murderbot would know what to do here.
        raise BeartypeAnnotatedIsCoreException(
            f'Class "{cls.__name__}" not instantiable; '
            f'index this class with data validation functions instead '
            f'(e.g., "{cls.__name__}[lambda obj: bool(obj)]").'
        )

    # ..................{ GETTERS                           }..................
    def __class_getitem__(
        cls, validator: AnnotatedIsValidator) -> AnnotatedIs:
        '''
        `PEP 560`_-compliant dunder method dynamically generating a new
        :class:`AnnotatedIs` object from the passed data validation function
        suitable for subscripting `PEP 593`_-compliant :attr:`typing.Annotated`
        type hints.

        See the class docstring for usage instructions.

        Parameters
        ----------
        validator : Callable[[Any,], bool]
            **Data validator** (i.e., caller-defined function accepting a
            single arbitrary object and returning either ``True`` if that
            object satisfies an arbitrary constraint *or* ``False`` otherwise).

        Returns
        ----------
        AnnotatedIs
            New object encapsulating this data validator.

        Raises
        ----------
        BeartypeAnnotatedIsCoreException
            If either:

            * This class was subscripted by two or more arguments.
            * This class was subscripted by one argument that either:

              * Is *not* callable.
              * Is a C-based rather than pure-Python callable.
              * Is a pure-Python callable accepting two or more arguments.

        .. _PEP 560:
           https://www.python.org/dev/peps/pep-0560
        .. _PEP 593:
           https://www.python.org/dev/peps/pep-0593
        '''

        # One one-liner to rule them all and in "pdb" bind them.
        return AnnotatedIs(validator)

# ....................{ TESTERS                           }....................
def is_hint_pep593_beartype(hint: Any) -> bool:
    '''
    ``True`` only if the first argument subscripting the passed `PEP
    593`-compliant :attr:`typing.Annotated` type hint is
    :mod:`beartype`-specific (e.g., instance of the :class:`AnnotatedIs` class
    produced by subscripting (indexing) the :class:`Is` class).

    Parameters
    ----------
    hint : Any
        `PEP 593`-compliant :attr:`typing.Annotated` type hint to be inspected.

    Returns
    ----------
    bool
        ``True`` only if the first argument subscripting this hint is
        :mod:`beartype`-specific.

    Raises
    ----------
    BeartypeDecorHintPepException
        If this object is *not* a `PEP 593`_-compliant type metahint.
    '''

    # If this object is *NOT* a PEP 593-compliant type metahint, raise an
    # exception.
    die_unless_hint_pep593(hint)
    # Else, this object is a PEP 593-compliant type metahint.

    # Attempt to return true only if the first argument subscripting this hint
    # is beartype-specific.
    #
    # Note that the "__metadata__" dunder attribute is both guaranteed to exist
    # for metahints *AND* be a non-empty tuple of arbitrary objects: e.g.,
    #     >>> from typing import Annotated
    #     >>> Annotated[int]
    #     TypeError: Annotated[...] should be used with at least two
    #     arguments (a type and an annotation).
    try:
        return isinstance(hint.__metadata__[0], AnnotatedIs)
    # If the metaclass of the first argument subscripting this hint overrides
    # the __isinstancecheck__() dunder method to raise an exception, silently
    # ignore this exception by returning false instead.
    except:
        return False
