#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2020 Cecil Curry.
# See "LICENSE" for further details.

'''
**Beartype type-checking error cause sleuth** (i.e., object recursively
fabricating the human-readable string describing the failure of the pith
associated with this object to satisfy this PEP-compliant type hint also
associated with this object) classes.

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                           }....................
from beartype.roar import _BeartypeCallHintPepRaiseException
from beartype._util.hint.pep.proposal.utilhintpep484 import (
    get_hint_pep484_generic_bases_unerased_or_none,
    get_hint_pep484_newtype_class,
    is_hint_pep484_newtype,
)
from beartype._util.hint.pep.proposal.utilhintpep544 import (
    get_hint_pep544_io_protocol_from_generic,
    is_hint_pep544_io_generic,
)
from beartype._util.hint.pep.proposal.utilhintpep593 import (
    get_hint_pep593_hint,
    is_hint_pep593,
)
from beartype._util.hint.pep.utilhintpepget import (
    get_hint_pep_args,
    get_hint_pep_sign,
)
from beartype._util.hint.pep.utilhintpeptest import (
    is_hint_pep,
    is_hint_pep_typevar,
)
from beartype._util.hint.utilhinttest import (
    is_hint_forwardref,
    is_hint_ignorable,
)
from typing import NoReturn

# See the "beartype.__init__" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ CLASSES                           }....................
class CauseSleuth(object):
    '''
    **Type-checking error cause sleuth** (i.e., object recursively fabricating
    the human-readable string describing the failure of the pith associated
    with this object to satisfy this PEP-compliant type hint also associated
    with this object).

    Attributes
    ----------
    cause_indent : str
        **Indentation** (i.e., string of zero or more spaces) preceding each
        line of the string returned by this getter if this string spans
        multiple lines *or* ignored otherwise (i.e., if this string is instead
        embedded in the current line).
    exception_label : str
        Human-readable label describing the parameter or return value from
        which this object originates, typically embedded in exceptions raised
        from this getter in the event of unexpected runtime failure.
    func : object
        Decorated callable generating this type-checking error.
    hint : object
        Type hint to validate this object against.
    hint_sign : object
        Unsubscripted :mod:`typing` attribute identifying this hint if this hint
        is PEP-compliant *or* ``None`` otherwise.
    hint_childs : Optional[tuple]
        Either:

        * If this hint is PEP-compliant:

          * If this hint is a generic, tuple of the one or more unerased
            pseudo-superclasses (i.e., :mod:`typing` objects originally listed
            as superclasses prior to their implicit type erasure by the
            :mod:`typing` module) subclassed by this generic.
          * Else, the possibly empty tuple of all arguments subscripting this
            hint if this

        * Else, ``None``.
    pith : object
        Arbitrary object to be validated.
    '''

    # ..................{ CLASS VARIABLES                   }..................
    # Slot *ALL* instance variables defined on this object to both:
    # * Prevent accidental declaration of erroneous instance variables.
    # * Minimize space and time complexity.
    __slots__ = (
        'cause_indent',
        'exception_label',
        'func',
        'hint',
        'hint_sign',
        'hint_childs',
        'pith',
    )


    _INIT_PARAM_NAMES = frozenset((
        'cause_indent',
        'exception_label',
        'func',
        'hint',
        'pith',
    ))
    '''
    Frozen set of the names of all parameters accepted by the :meth:`init`
    method, defined as a set to enable efficient membership testing.
    '''


    _VAR_NAMES = frozenset(__slots__)
    '''
    Frozen set of the names of all instance variables permitted on this object,
    defined as a set to enable efficient membership testing.
    '''

    # ..................{ INITIALIZERS                      }..................
    def __init__(
        self,
        func: object,
        pith: object,
        hint: object,
        cause_indent: str,
        exception_label: str,
    ) -> None:
        '''
        Initialize this object.
        '''
        assert callable(func), f'{repr(func)} not callable.'
        assert isinstance(cause_indent, str), (
            f'{repr(cause_indent)} not string.')
        assert isinstance(exception_label, str), (
            f'{repr(exception_label)} not string.')

        # Classify all passed parameters.
        self.func = func
        self.pith = pith
        self.hint = hint
        self.cause_indent = cause_indent
        self.exception_label = exception_label

        # Nullify all remaining parameters for safety.
        self.hint_sign = None
        self.hint_childs = None

        # ................{ REDUCTION                         }................
        #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        # CAVEATS: Synchronize changes here with the corresponding block of the
        # beartype._decor._code._pep._pephint.pep_code_check_hint() function.
        #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        # This logic reduces the currently visited hint to an arbitrary object
        # associated with this hint when this hint conditionally satisfies any
        # of various conditions.
        #
        # ................{ REDUCTION ~ pep 484               }................
        # If this is a PEP 484-compliant new type hint, reduce this hint to the
        # user-defined class aliased by this hint. Although this logic could
        # also be performed below, doing so here simplifies matters.
        if is_hint_pep484_newtype(self.hint):
            self.hint = get_hint_pep484_newtype_class(self.hint)
        # ................{ REDUCTION ~ pep 544               }................
        # If this is a PEP 484-compliant IO generic base class *AND* the active
        # Python interpreter targets at least Python >= 3.8 and thus supports
        # PEP 544-compliant protocols, reduce this functionally useless hint to
        # the corresponding functionally useful beartype-specific PEP
        # 544-compliant protocol implementing this hint.
        elif is_hint_pep544_io_generic(self.hint):
            self.hint = get_hint_pep544_io_protocol_from_generic(self.hint)
        # ................{ REDUCTION ~ pep 593               }................
        # If this is a PEP 593-compliant type metahint, ignore all annotations
        # on this hint (i.e., "hint_curr.__metadata__" tuple) by reducing this
        # hint to its origin (e.g., "str" in "Annotated[str, 50, False]").
        elif is_hint_pep593(self.hint):
            self.hint = get_hint_pep593_hint(self.hint)
        # ................{ REDUCTION ~ end                   }................

        # If this hint is PEP-compliant...
        if is_hint_pep(self.hint):
            # Unsubscripted "typing" attribute identifying this hint.
            self.hint_sign = get_hint_pep_sign(self.hint)

            # Tuple of the one or more unerased pseudo-superclasses subclassed
            # by this hint if this hint is a generic *OR* "None" otherwise.
            self.hint_childs = get_hint_pep484_generic_bases_unerased_or_none(self.hint)

            # If this hint is *NOT* a generic, generalize this variable to the
            # possibly empty tuple of all arguments subscripting this hint.
            if self.hint_childs is None:
                self.hint_childs = get_hint_pep_args(self.hint)

    # ..................{ GETTERS                           }..................
    def get_cause_or_none(self) -> 'Optional[str]':
        '''
        Human-readable string describing the failure of this pith to satisfy
        this PEP-compliant type hint if this pith fails to satisfy this pith
        *or* ``None`` otherwise (i.e., if this pith satisfies this hint).

        Design
        ----------
        This getter is intentionally generalized to support objects both
        satisfying and *not* satisfying hints as equally valid use cases. While
        the parent :func:`.peperror.raise_pep_call_exception` function
        calling this getter is *always* passed an object *not* satisfying the
        passed hint, this getter is under no such constraints. Why? Because
        this getter is also called to find which of an arbitrary number of
        objects transitively nested in the object passed to
        :func:`.peperror.raise_pep_call_exception` fails to satisfy the
        corresponding hint transitively nested in the hint passed to that
        function.

        For example, consider the PEP-compliant type hint ``List[Union[int,
        str]]`` describing a list whose items are either integers or strings
        and the list ``list(range(256)) + [False,]`` consisting of the integers
        0 through 255 followed by boolean ``False``. Since this list is a
        standard sequence, the
        :func:`._peperrorsequence.get_cause_or_none_sequence_standard`
        function must decide the cause of this list's failure to comply with
        this hint by finding the list item that is neither an integer nor a
        string, implemented by by iteratively passing each list item to the
        :func:`._peperrorunion.get_cause_or_none_union` function. Since
        the first 256 items of this list are integers satisfying this hint,
        :func:`._peperrorunion.get_cause_or_none_union` returns
        ``None`` to
        :func:`._peperrorsequence.get_cause_or_none_sequence_standard`
        before finally finding the non-compliant boolean item and returning the
        human-readable cause.

        Returns
        ----------
        Optional[str]
            Either:

            * If this object fails to satisfy this hint, human-readable string
            describing the failure of this object to do so.
            * Else, ``None``.

        Raises
        ----------
        _BeartypeCallHintPepRaiseException
            If this type hint is either:

            * PEP-noncompliant (e.g., tuple union).
            * PEP-compliant but no getter function has been implemented to
              handle this category of PEP-compliant type hint yet.
        '''

        # Getter function returning the desired string.
        get_cause_or_none = None

        # If this hint is ignorable, all possible objects satisfy this hint,
        # implying this hint *CANNOT* by definition be the cause of this
        # failure. In this case, immediately report None.
        if is_hint_ignorable(self.hint):
            return None
        # Else, this hint is unignorable.
        #
        # If *NO* sign uniquely identifies this hint, this hint is
        # PEP-noncompliant. In this case...
        elif self.hint_sign is None:
            # Avoid circular import dependencies.
            from beartype._decor._code._pep._error._peperrortype import (
                get_cause_or_none_type)

            # Defer to the getter function supporting non-"typing" classes.
            get_cause_or_none = get_cause_or_none_type
        # Else, this hint is PEP-compliant.
        #
        # If this PEP-compliant hint is its own unsubscripted "typing"
        # attribute (e.g., "typing.List" rather than "typing.List[str]") and is
        # thus subscripted by *NO* child hints...
        elif self.hint is self.hint_sign:
            # If this hint is the non-standard "typing.NoReturn" type hint
            # specific to return values...
            if self.hint is NoReturn:
                # Avoid circular import dependencies.
                from beartype._decor._code._pep._error._peperrorreturn import (
                    get_cause_or_none_noreturn)

                # Defer to the getter function specific to this hint.
                get_cause_or_none = get_cause_or_none_noreturn
            # Else, this hint is a standard PEP-compliant type hint supported
            # by both parameters and return values. In this case, we assume
            # this hint to originate from an origin type.
            else:
                # Avoid circular import dependencies.
                from beartype._decor._code._pep._error._peperrortype import (
                    get_cause_or_none_type_origin)

                # Defer to the getter function supporting hints originating
                # from origin types.
                get_cause_or_none = get_cause_or_none_type_origin
        # Else, this PEP-compliant hint is *NOT* its own unsubscripted "typing"
        # attribute. In this case...
        else:
            # Avoid circular import dependencies.
            from beartype._decor._code._pep._error.peperror import (
                _TYPING_ATTR_TO_GETTER)

            # If this hint is neither...
            if not (
                # Subscripted by no child hints *NOR*...
                self.hint_childs or
                # A forward reference nor type variable, whose designs reside
                # well outside the standard "typing" dunder variable API and
                # are thus *NEVER* subscripted by child hints...
                is_hint_forwardref(self.hint) or
                is_hint_pep_typevar(self.hint)
            ):
            # Then this hint should have been subscripted by one or more child
            # hints but wasn't. In this case, raise an exception.
                raise _BeartypeCallHintPepRaiseException(
                    f'{self.exception_label} argumentative PEP type hint '
                    f'{repr(self.hint)} unsubscripted.'
                )
            # Else, thus subscripted by one or more child hints (e.g.,
            # "typing.List[str]" rather than "typing.List")
            #
            # Else, this hint is subscripted by one or more child hints.

            # Getter function returning the desired string for this attribute
            # if any *OR* "None" otherwise.
            get_cause_or_none = _TYPING_ATTR_TO_GETTER.get(
                self.hint_sign, None)

            # If no such function has been implemented to handle this attribute
            # yet, raise an exception.
            if get_cause_or_none is None:
                raise _BeartypeCallHintPepRaiseException(
                    f'{self.exception_label} PEP type hint '
                    f'{repr(self.hint)} unsupported (i.e., no '
                    f'"get_cause_or_none_"-prefixed getter function defined '
                    f'for this category of hint).'
                )
            # Else, a getter function has been implemented to handle this
            # attribute.

        # Call this getter function with ourselves and return the string
        # returned by this getter.
        return get_cause_or_none(self)

    # ..................{ PERMUTERS                         }..................
    def permute(self, **kwargs) -> 'CauseSleuth':
        '''
        Shallow copy of this object such that each the passed keyword argument
        overwrites the instance variable of the same name in this copy.

        Parameters
        ----------
        Keyword arguments of the same name and type as instance variables of
        this object (e.g., ``hint``, ``pith``).

        Returns
        ----------
        CauseSleuth
            Shallow copy of this object such that each keyword argument
            overwrites the instance variable of the same name in this copy.

        Raises
        ----------
        _BeartypeCallHintPepRaiseException
            If the name of any passed keyword argument is *not* the name of an
            existing instance variable of this object.

        Examples
        ----------
            >>> sleuth = CauseSleuth(
            ...     pith=[42,]
            ...     hint=typing.List[int],
            ...     cause_indent='',
            ...     exception_label='List of integers',
            ... )
            >>> sleuth_copy = sleuth.permute(pith=[24,])
            >>> sleuth_copy.pith
            [24,]
            >>> sleuth_copy.hint
            typing.List[int]
        '''

        # For the name of each passed keyword argument...
        for param_name in kwargs.keys():
            # If this copy does *NOT* already define an instance variable of
            # the same name, raise an exception.
            if param_name not in self._VAR_NAMES:
                raise _BeartypeCallHintPepRaiseException(
                    f'Unrecognized instance variable '
                    f'{self.__class__.__name__}.{param_name} not permutable.'
                )

        # For the name of each instance variable initializable by this class...
        for param_name in self._INIT_PARAM_NAMES:
            # If this variable is not already defined by these arguments,
            # cascade the current value of this variable into these arguments.
            if param_name not in kwargs:
                kwargs[param_name] = getattr(self, param_name)

        # Return a new instance of this class initialized with these arguments.
        return CauseSleuth(**kwargs)
