#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype type-checking error cause sleuth** (i.e., object recursively
fabricating the human-readable string describing the failure of the pith
associated with this object to satisfy this PEP-compliant type hint also
associated with this object) classes.

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ TODO                               }....................
#FIXME: The "ViolationCause.hint_childs" tuple is arguably useless. It's only
#used in one other submodule and can, in any case, be trivially reconstructed
#from the more useful "ViolationCause.hint_or_sane_childs" tuple. In other
#words, please excise "ViolationCause.hint_childs".

#FIXME: The recursive "ViolationCause" class strongly overlaps with the equally
#recursive (and substantially superior) "beartype.door.TypeHint" class. Ideally:
#* Define a new private "beartype.door._doorerror" submodule.
#* Shift the "ViolationCause" class to
#  "beartype.door._doorerror._TypeHintUnbearability".
#* Shift the _TypeHintUnbearability.find_cause() method to a new
#  *PRIVATE* TypeHint._find_cause() method.
#* Preserve most of the remainder of the "_TypeHintUnbearability" class as a
#  dataclass encapsulating metadata describing the current type-checking
#  violation. That metadata (e.g., "cause_indent") is inappropriate for
#  general-purpose type hints. Exceptions include:
#  * "hint", "hint_sign", and "hint_or_sane_childs" -- all of which are subsumed
#    by the "TypeHint" dataclass and should thus be excised.
#* Refactor the TypeHint._find_cause() method to accept an instance of
#  the "_TypeHintUnbearability" dataclass: e.g.,
#      class TypeHint(...):
#          def _get_unbearability_cause_or_none(
#              self, unbearability: _TypeHintUnbearability) -> Optional[str]:
#              ...
#* Refactor existing find_cause_*() getters (e.g.,
#  find_cause_sequence_args_1(), find_cause_pep484604_union()) into
#  _get_unbearability_cause_or_none() methods of the corresponding "TypeHint"
#  subclasses, please.
#
#This all seems quite reasonable. Now, let's see whether it is. *gulp*
#FIXME: Actually, the above comment now ties directly into feature request #235.
#Resolving the above comment mostly suffices to resolve #235. That said, the
#above isn't *QUITE* right. It's pretty nice -- but we can do better. See the
#following comment at #235 for that better:
#    https://github.com/beartype/beartype/issues/235#issuecomment-1707127231

# ....................{ IMPORTS                            }....................
from beartype.roar._roarexc import _BeartypeCallHintPepRaiseException
from beartype.typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Optional,
)
from beartype._cave._cavemap import NoneTypeOr
from beartype._check.convert.convsanify import (
    sanify_hint_child)
from beartype._check.metadata.metasane import (
    HintOrHintSanifiedData,
    TupleHintOrHintSanifiedData,
    get_hint_or_sane_hint,
    unpack_hint_or_sane,
)
from beartype._conf.confcls import BeartypeConf
from beartype._data.hint.datahintpep import (
    Hint,
    TupleHints,
    TypeVarToHint,
)
from beartype._data.hint.datahinttyping import TypeStack
from beartype._data.kind.datakindmap import FROZENDICT_EMPTY
from beartype._data.hint.pep.sign.datapepsigncls import HintSign
from beartype._data.hint.pep.sign.datapepsignset import (
    HINT_SIGNS_SUPPORTED_DEEP,
    HINT_SIGNS_ORIGIN_ISINSTANCEABLE,
)
from beartype._util.hint.pep.utilpepget import (
    get_hint_pep_args,
    get_hint_pep_sign_or_none,
)
from beartype._util.hint.pep.utilpeptest import is_hint_pep
from beartype._util.kind.map.utilmapfrozen import FrozenDict
from beartype._util.utilobject import SENTINEL
from beartype._util.utilobjmake import permute_object

# ....................{ CLASSES                            }....................
class ViolationCause(object):
    '''
    **Type-checking violation cause finder** (i.e., object recursively
    fabricating the human-readable string describing the failure of the pith
    associated with this finder to satisfy this PEP-compliant type hint also
    associated with this finder).

    Attributes
    ----------
    cause_indent : str
        **Indentation** (i.e., string of zero or more spaces) preceding each
        line of the string returned by this getter if this string spans
        multiple lines *or* ignored otherwise (i.e., if this string is instead
        embedded in the current line).
    cause_str_or_none : Optional[str]
        If this pith either:

        * Violates this hint, a human-readable string describing this violation.
        * Satisfies this hint, :data:`None`.
    cls_stack : TypeStack, optional
        **Type stack** (i.e., either a tuple of the one or more
        :func:`beartype.beartype`-decorated classes lexically containing the
        class variable or method annotated by this hint *or* :data:`None`).
    conf : BeartypeConf
        **Beartype configuration** (i.e., self-caching dataclass encapsulating
        all flags, options, settings, and other metadata configuring the
        current decoration of the decorated callable or class).
    exception_prefix : str
        Human-readable label describing the parameter or return value from
        which this object originates, typically embedded in exceptions raised
        from this getter in the event of unexpected runtime failure.
    func : Optional[Callable]
        Either:

        * If this violation originates from a decorated callable, that
          callable.
        * Else, :data:`None`.
    hint : Hint
        Type hint to validate this object against.
    hint_childs : Optional[TupleHints]
        Either:

        * If this hint is PEP-compliant, the possibly empty tuple of all child
          hints subscripting (indexing) this hint.
        * Else, :data:`None`.

        This instance variable is effectively a streamlined variant of the
        :attr:`hint_or_sane_childs` instance variable. Whereas the latter
        *includes* all supplementary metadata, the former instance variable
        *excludes* all supplementary metadata and thus only contains hints.
    hint_or_sane_childs : Optional[TupleHintOrHintSanifiedData]
        Either:

        * If this hint is PEP-compliant, the possibly empty tuple of all child
          hints subscripting (indexing) this hint such that each item is either:

          * If sanifying this child hint generated supplementary metadata, that
            metadata (i.e., a :class:`.HintSanifiedData` object).
          * Else, this child hint as is.

        * Else, :data:`None`.
    hint_sign : Optional[HintSign]
        Either:

        * If this hint is PEP-compliant, the sign identifying this hint.
        * Else, :data:`None` otherwise.
    pith : Any
        Arbitrary object to be validated.
    pith_name : Optional[str]
        Either:

        * If this hint directly annotates a callable parameter (as the root type
          hint of that parameter), the name of this parameter.
        * If this hint directly annotates a callable return (as the root type
          hint of that return), the magic string ``"return"``.
        * Else, :data:`None`.
    random_int : Optional[int]
        **Pseudo-random integer** (i.e., unsigned 32-bit integer
        pseudo-randomly generated by the parent :func:`beartype.beartype`
        wrapper function in type-checking randomly indexed container items by
        the current call to that function) if that function generated such an
        integer *or* ``None`` otherwise (i.e., if that function generated *no*
        such integer). See the same parameter accepted by the higher-level
        :func:`beartype._check.error.errget.get_func_pith_violation` function.
    typevar_to_hint : TypeVarToHint
        **Type variable lookup table** (i.e., immutable dictionary mapping from
        each :pep:`484`-compliant type variable parametrizing either the
        currently visited type hint *or* a transitive parent type hint of this
        hint to the corresponding non-type variable type hint subscripting that
        hint). See also the comparable
        :func:`beartype._check.codecls.HintMeta.typevar_to_hint` instance
        variable.
    '''

    # ..................{ CLASS VARIABLES                    }..................
    # Slot *ALL* instance variables defined on this object to both:
    # * Prevent accidental declaration of erroneous instance variables.
    # * Minimize space and time complexity.
    __slots__ = (
        'cause_indent',
        'cause_str_or_none',
        'cls_stack',
        'conf',
        'exception_prefix',
        'func',
        'hint',
        'hint_childs',
        'hint_or_sane_childs',
        'hint_sign',
        'pith',
        'pith_name',
        'random_int',
        'typevar_to_hint',
    )


    # Squelch false negatives from mypy. This is absurd. This is mypy. See:
    #     https://github.com/python/mypy/issues/5941
    if TYPE_CHECKING:
        cause_indent: str
        cause_str_or_none: Optional[str]
        cls_stack: TypeStack
        conf: BeartypeConf
        exception_prefix: str
        func: Optional[Callable]
        hint: Hint
        hint_childs: TupleHints
        hint_or_sane_childs: TupleHintOrHintSanifiedData
        hint_sign: Optional[HintSign]
        pith: Any
        pith_name: Optional[str]
        random_int: Optional[int]
        typevar_to_hint: TypeVarToHint


    _INIT_PARAM_NAMES = frozenset((
        'cause_indent',
        'cause_str_or_none',
        'cls_stack',
        'conf',
        'exception_prefix',
        'func',
        'hint',
        'hint_or_sane',
        'pith',
        'pith_name',
        'random_int',
        'typevar_to_hint',
    ))
    '''
    Frozen set of the names of all parameters accepted by the :meth:`init`
    method, defined as a set to enable efficient membership testing.
    '''

    # ..................{ INITIALIZERS                       }..................
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # CAUTION: Whenever adding, deleting, or renaming any parameter accepted by
    # this method, make similar changes to the "_INIT_PARAM_NAMES" set above.
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    def __init__(
        self,

        # Mandatory parameters.
        cause_indent: str,
        cls_stack: TypeStack,
        conf: BeartypeConf,
        exception_prefix: str,
        func: Optional[Callable],
        pith: Any,
        pith_name: Optional[str],
        random_int: Optional[int],

        # Optional parameters.
        hint: Hint = SENTINEL,  # type: ignore[arg-type]
        hint_or_sane: HintOrHintSanifiedData = SENTINEL,  # type: ignore[arg-type]
        cause_str_or_none: Optional[str] = None,
        typevar_to_hint: TypeVarToHint = FROZENDICT_EMPTY,
    ) -> None:
        '''
        Initialize this type-checking violation cause finder.

        Parameters
        ----------
        hint : Hint
            Unsanified hint to validate this object against. This parameter is
            mutually exclusive with the competing ``hint_or_sane`` parameter.
            Defaults to the sentinel placeholder such that either:

            * This parameter is unpassed (thus, the sentinel) and the
              ``hint_or_sane`` parameter is passed (thus, *not* the sentinel).
            * This parameter is passed (thus, *not* the sentinel) and the
              ``hint_or_sane`` parameter is unpassed (thus, the sentinel).
        hint_or_sane : HintOrHintSanifiedData
            Sanified hint *or* **supplementary metadata** (i.e.,
            :class:`.HintSanifiedData` object) generated by the sanification of
            this hint to validate this object against. This parameter is
            mutually exclusive with the competing ``hint_or_sane`` parameter.
            Defaults to the sentinel placeholder such that either:

            * This parameter is unpassed (thus, the sentinel) and the
              ``hint_or_sane`` parameter is passed (thus, *not* the sentinel).
            * This parameter is passed (thus, *not* the sentinel) and the
              ``hint_or_sane`` parameter is unpassed (thus, the sentinel). In
              this case, this parameter is defined as either:

              * If this hint is reducible to:

                * An ignorable lower-level hint, :obj:`typing.Any`.
                * An unignorable lower-level hint, either:

                  * If reducing this hint to that lower-level hint generates
                    supplementary metadata, that metadata.
                  * Else, that lower-level hint alone.

              * Else, this hint is irreducible. In this case, this hint
                unmodified.

        See the class docstring for a description of all remaining parameters.
        '''
        assert isinstance(cls_stack, NoneTypeOr[tuple]), (
            f'{repr(cls_stack)} neither tuple nor "None".')
        assert isinstance(conf, BeartypeConf), (
            f'{repr(conf)} not configuration.')
        assert func is None or callable(func), (
            f'{repr(func)} neither callable nor "None".')
        assert isinstance(cause_indent, str), (
            f'{repr(cause_indent)} not string.')
        assert isinstance(cause_str_or_none, NoneTypeOr[str]), (
            f'{repr(cause_str_or_none)} not string or "None".')
        assert isinstance(exception_prefix, str), (
            f'{repr(exception_prefix)} not string.')
        # assert isinstance(is_hint_root, bool), (
        #     f'{repr(is_hint_root)} not boolean.')
        assert isinstance(pith_name, NoneTypeOr[str]), (
            f'{repr(pith_name)} not string or "None".')
        assert isinstance(random_int, NoneTypeOr[int]), (
            f'{repr(random_int)} not integer or "None".')
        assert isinstance(typevar_to_hint, FrozenDict), (
            f'{repr(typevar_to_hint)} not frozen dictionary.')

        # Classify all passed parameters.
        self.cause_indent = cause_indent
        self.cause_str_or_none = cause_str_or_none
        self.cls_stack = cls_stack
        self.conf = conf
        self.exception_prefix = exception_prefix
        self.func = func
        self.pith = pith
        self.pith_name = pith_name
        self.random_int = random_int
        self.typevar_to_hint = typevar_to_hint

        # Nullify all remaining parameters for safety.
        self.hint_childs = None  # type: ignore[assignment]
        self.hint_or_sane_childs = None  # type: ignore[assignment]

        # If the caller passed *NO* sanified hint...
        if hint_or_sane is SENTINEL:
            assert hint is not SENTINEL, (
                f'"hint" {repr(hint)} and '
                f'"hint_or_sane" {repr(hint_or_sane)} parameters both unpassed.'
            )

            # Sane hint sanified from this possibly insane hint if sanifying
            # this hint did not generate supplementary metadata *OR* that
            # metadata (i.e., if doing so generated supplementary metadata).
            hint_or_sane = self.sanify_hint_child(hint)
            # print(f'Sanified error parent hint {repr(hint)} to {repr(hint_or_sane)}.')
        # Else, the caller passed a sanified hint. In this case...
        else:
            # Silently ignore the passed unsanified hint if any by simply
            # deleting the latter.
            #
            # Note that we would ideally raise an exception if the caller also
            # passed an unsanified hint, but that doing so would raise
            # complications with our current implementation of the permute()
            # method. Since this dataclass *ONLY* applies to private
            # functionality *NEVER* exposed to end users, a bit of wonkiness in
            # this private API is currently an acceptable tradeoff.
            # Assert that the caller passed an unsanified hint.
            del hint

        # Sane hint sanified from this possibly insane hint *AND* the
        # corresponding type variable lookup table unpacked from this metadata.
        self.hint, self.typevar_to_hint = unpack_hint_or_sane(hint_or_sane)

        # Sign uniquely identifying this hint if this hint is PEP-compliant *OR*
        # "None" otherwise (i.e., if this hint is PEP-noncompliant).
        self.hint_sign = get_hint_pep_sign_or_none(self.hint)

        #FIXME: Refactor into a new private method for maintainability, please.
        # If this hint is both...
        if (
            # Unignorable *AND*...
            self.hint is not Any and
            # PEP-compliant...
            is_hint_pep(self.hint)
        ):
            # Tuple of the zero or more arguments subscripting this hint.
            hint_childs_insane = get_hint_pep_args(self.hint)

            # List of the zero or more possibly ignorable sane child hints
            # subscripting this parent hint, initialized to the empty list.
            hint_childs_sane = []

            # List of the zero or more possibly ignorable metadata generated by
            # sanifying these child hints, initialized to the empty list.
            hint_or_sane_childs_sane = []

            # For each possibly ignorable insane child hints subscripting this
            # parent hint...
            for hint_child_insane in hint_childs_insane:
                # Sane child hint sanified from this possibly insane child hint.
                hint_child_sane: Hint = None  # pyright: ignore

                # Sane child hint sanified from this possibly insane child hint
                # if sanifying this child hint did not generate supplementary
                # metadata *OR* that metadata otherwise (i.e., if sanifying this
                # child hint generated supplementary metadata).
                hint_or_sane_child_sane: HintOrHintSanifiedData = None  # pyright: ignore

                # If this child hint is PEP-compliant...
                #
                # Note that arbitrary PEP-noncompliant arguments *CANNOT* be
                # safely sanitized. Why? Because arbitrary arguments are *NOT*
                # necessarily valid hints. Consider the hint "tuple[()]", where
                # the argument "()" is invalid as a hint but valid an argument
                # to that hint. Else, this child hint is PEP-noncompliant. In
                # this case, preserve this child hint as is.
                if is_hint_pep(hint_child_insane):
                    # Sanify this child hint into this metadata.
                    hint_or_sane_child_sane = self.sanify_hint_child(
                        hint_child_insane)

                    # Sane child hint encapsulated by this metadata.
                    hint_child_sane = get_hint_or_sane_hint(
                        hint_or_sane_child_sane)
                # Else, this child hint is PEP-noncompliant. In this case,
                # preserve this child hint as is.
                else:
                    hint_child_sane = hint_or_sane_child_sane = (
                        hint_child_insane)

                # Append this possibly ignorable sane child hint and
                # supplementary metadata to these lists.
                hint_childs_sane.append(hint_child_sane)
                hint_or_sane_childs_sane.append(hint_or_sane_child_sane)

            # Tuples of the zero or more possibly ignorable sane child hints and
            # supplementary metadatum, coerced from these lists.
            self.hint_childs = tuple(hint_childs_sane)
            self.hint_or_sane_childs = tuple(hint_or_sane_childs_sane)
        # Else, this hint is PEP-noncompliant (e.g., isinstanceable class).

    # ..................{ DUNDERS                            }..................
    def __repr__(self) -> str:
        '''
        Machine-readable representation of this error cause.
        '''

        # Represent this metadata with just the minimal subset of metadata
        # needed to reasonably describe this metadata.
        return (
            f'{self.__class__.__name__}('
            f'hint={repr(self.hint)}, '
            f'hint_sign={repr(self.hint_sign)}, '
            f'hint_childs={repr(self.hint_childs)}, '
            f'hint_or_sane_childs={repr(self.hint_or_sane_childs)}, '
            f'conf={repr(self.conf)}, '
            f'cause_indent={repr(self.cause_indent)}, '
            f'cause_str_or_none={repr(self.cause_str_or_none)}, '
            f'cls_stack={repr(self.cls_stack)}, '
            f'func={repr(self.func)}, '
            f'pith={repr(self.pith)}, '
            f'pith_name={repr(self.pith_name)}, '
            f'random_int={repr(self.random_int)}, '
            f'typevar_to_hint={repr(self.typevar_to_hint)}, '
            f'exception_prefix={repr(self.exception_prefix)}, '
            f')'
        )

    # ..................{ FINDERS                            }..................
    def find_cause(self) -> 'ViolationCause':
        '''
        Output cause describing whether the pith of this input cause either
        satisfies or violates the type hint of this input cause.

        Design
        ------
        This method is intentionally generalized to support objects both
        satisfying and *not* satisfying hints as equally valid use cases. While
        the parent
        :func:`beartype._check.error.errget.get_func_pith_violation` function
        calling this method is *always* passed an object *not* satisfying the
        passed hint, this method is under no such constraints. Why? Because this
        method is also called to find which of an arbitrary number of objects
        transitively nested in the object passed to
        :func:`beartype._check.error.errget.get_func_pith_violation` fails to
        satisfy the corresponding hint transitively nested in the hint passed to
        that function.

        For example, consider the type hint ``List[Union[int, str]]`` describing
        a list whose items are either integers or strings and the list
        ``list(range(256)) + [False,]`` consisting of the integers 0 through 255
        followed by boolean :data:`False`. Since that list is a sequence, the
        :func:`._peperrorsequence.find_cause_sequence_args_1` function must
        decide the cause of this list's failure to comply with this hint by
        finding the list item that is neither an integer nor a string,
        implemented by by iteratively passing each list item to the
        :func:`._peperrorunion.find_cause_pep484604_union` function. Since the
        first 256 items of this list are integers satisfying this hint,
        :func:`._peperrorunion.find_cause_pep484604_union` returns a dataclass
        instance whose :attr:`cause` field is :data:`None` up to
        :func:`._peperrorsequence.find_cause_sequence_args_1` before finally
        finding the non-compliant boolean item and returning its cause.

        Returns
        -------
        ViolationCause
            Output cause type-checking this pith against this type hint.

        Raises
        ------
        _BeartypeCallHintPepRaiseException
            If this type hint is either:

            * PEP-noncompliant (e.g., tuple union).
            * PEP-compliant but no getter function has been implemented to
              handle this category of PEP-compliant type hint yet.
        '''

        # If this hint is ignorable, all possible objects satisfy this hint.
        # Since this hint *CANNOT* (by definition) be the cause of this failure,
        # return the same cause as is.
        if self.hint is Any:
            return self
        # Else, this hint is unignorable.

        # Getter function returning the desired string.
        cause_finder: Callable[[ViolationCause], ViolationCause] = None  # type: ignore[assignment]

        #FIXME: Trivially simplify this method by:
        #* Define a new find_cause_nonpep() function elsewhere whose body is
        #  the body of this "if" conditional branch.
        #* Register this function with HINT_SIGN_TO_GET_CAUSE_FUNC: e.g.,
        #  HINT_SIGN_TO_GET_CAUSE_FUNC = {
        #      ...,
        #      None: find_cause_nonpep,
        #  }
        #* Remove this "if" conditional branch.

        # If *NO* sign uniquely identifies this hint, this hint is either
        # PEP-noncompliant *OR* only contextually PEP-compliant in certain
        # specific use cases. In either case...
        if self.hint_sign is None:
            # Avoid circular import dependencies.
            from beartype._check.error._errtype import (
                find_cause_instance_types_tuple,
                find_cause_instance_type,
            )

            # If this hint is a tuple union, defer to the finder specific to
            # tuple unions.
            if isinstance(self.hint, tuple):
                cause_finder = find_cause_instance_types_tuple
            # Else, this hint is *NOT* a tuple union. In this case, assume this
            # hint to be an isinstanceable class by deferring to the finder
            # specific to isinstanceable classes.
            #
            # Note that if this assumption is *NOT* the case, this finder
            # subsequently raises a human-readable exception.
            else:
                cause_finder = find_cause_instance_type
        # Else, this hint is PEP-compliant.
        #
        # If this hint...
        elif (
            # Originates from an origin type and may thus be shallowly
            # type-checked against that type *AND is either...
            self.hint_sign in HINT_SIGNS_ORIGIN_ISINSTANCEABLE and (
                # Unsubscripted *OR*...
                not get_hint_pep_args(self.hint) or
                # Currently unsupported with deep type-checking...
                self.hint_sign not in HINT_SIGNS_SUPPORTED_DEEP
            )
        # Then this hint is both unsubscripted and originating from a standard
        # type origin. In this case, this hint was type-checked shallowly.
        ):
            # Avoid circular import dependencies.
            from beartype._check.error._errtype import (
                find_cause_type_instance_origin)

            # Defer to the getter function supporting hints originating from
            # origin types.
            cause_finder = find_cause_type_instance_origin
        # Else, this hint is either subscripted *OR* unsubscripted but not
        # originating from a standard type origin. In either case, this hint was
        # type-checked deeply.
        else:
            # Avoid circular import dependencies.
            from beartype._check.error._errmap import (
                HINT_SIGN_TO_GET_CAUSE_FUNC)

            # Getter function returning the desired string for this attribute if
            # any *OR* "None" otherwise.
            cause_finder = HINT_SIGN_TO_GET_CAUSE_FUNC.get(
                self.hint_sign, None)  # type: ignore[arg-type]

            # If no such function has been implemented to handle this attribute
            # yet, raise an exception.
            if cause_finder is None:
                raise _BeartypeCallHintPepRaiseException(
                    f'{self.exception_prefix} type hint '
                    f'{repr(self.hint)} unsupported (i.e., no '
                    f'"find_cause_"-prefixed getter function defined '
                    f'for this category of hint).'
                )
            # Else, a getter function has been implemented to handle this
            # attribute.

        # Call this getter function with ourselves and return the string
        # returned by this getter.
        return cause_finder(self)

    # ..................{ PERMUTERS                          }..................
    def permute(self, **kwargs) -> 'ViolationCause':
        '''
        Shallow copy of this object such that each passed keyword parameter
        overwrites the instance variable of the same name in this copy.

        Parameters
        ----------
        Keyword parameters of the same name and type as instance variables of
        this object (e.g., ``hint: Hint``, ``pith: object``).

        Returns
        -------
        ViolationCause
            Shallow copy of this object such that each keyword parameter
            overwrites the instance variable of the same name in this copy.

        Raises
        ------
        _BeartypeCallHintPepRaiseException
            If the name of any passed keyword parameter is *not* that of an
            existing instance variable of this object.

        Examples
        --------
        .. code-block:: pycon

           >>> sleuth = ViolationCause(
           ...     pith=[42,]
           ...     hint=typing.List[int],
           ...     cause_indent='',
           ...     exception_prefix='List of integers',
           ... )
           >>> sleuth_copy = sleuth.permute(pith=[24,])
           >>> sleuth_copy.pith
           [24,]
           >>> sleuth_copy.hint
           typing.List[int]
        '''

        # Set us up the permutation! Make your time!
        return permute_object(
            obj=self,
            init_arg_name_to_value=kwargs,
            init_arg_names=self._INIT_PARAM_NAMES,
            exception_cls=_BeartypeCallHintPepRaiseException,
        )

    # ..................{ SANIFIERS                          }..................
    def sanify_hint_child(self, hint: Hint) -> HintOrHintSanifiedData:
        '''
        Type hint sanified (i.e., sanitized) from the passed **possibly insane
        child type hint** (i.e., hint transitively subscripting the root type
        hint annotating a parameter or return of the currently decorated
        callable) if this hint is both reducible and ignorable, this hint
        unmodified if this hint is both irreducible and ignorable, and
        :object:`typing.Any` otherwise (i.e., if this hint is ignorable).

        This method is merely a convenience wrapper for the lower-level
        :func:`.sanify_hint_child` sanifier.

        Parameters
        ----------
        hint : Hint
            Type hint to be sanified.

        Returns
        -------
        HintOrHintSanifiedData
            Either:

            * If the passed hint is reducible to:

              * An ignorable lower-level hint, :obj:`typing.Any`.
              * An unignorable lower-level hint, either:

                * If reducing this hint to that lower-level hint generates
                  supplementary metadata, that metadata.
                * Else, that lower-level hint alone.

            * Else, this hint is irreducible. In this case, this hint
              unmodified.

        See Also
        --------
        :func:`.sanify_hint_child`
            Further details.
        '''

        # Sane hint sanified from this possibly insane hint if sanifying this
        # hint did not generate supplementary metadata *OR* that metadata
        # otherwise (i.e., if doing so generated supplementary metadata).
        hint_or_sane_child = sanify_hint_child(
            hint=hint,
            cls_stack=self.cls_stack,
            conf=self.conf,
            pith_name=self.pith_name,
            typevar_to_hint=self.typevar_to_hint,
            exception_prefix=self.exception_prefix,
        )

        # Return this metadata.
        return hint_or_sane_child
