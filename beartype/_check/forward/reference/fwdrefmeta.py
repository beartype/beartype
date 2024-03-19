#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2024 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype **forward reference metaclasses** (i.e., low-level metaclasses of
classes deferring the resolution of a stringified type hint referencing an
attribute that has yet to be defined and annotating a class or callable
decorated by the :func:`beartype.beartype` decorator).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.roar import BeartypeCallHintForwardRefException
from beartype.typing import Dict
from beartype._data.hint.datahinttyping import BeartypeForwardRef
from beartype._util.cls.pep.utilpep3119 import (
    die_unless_object_isinstanceable)
from beartype._util.hint.pep.proposal.pep484585.utilpep484585generic import (
    is_hint_pep484585_generic,
    get_hint_pep484585_generic_type,
)
from beartype._util.module.utilmodimport import import_module_attr
from beartype._util.text.utiltextidentifier import is_dunder

# ....................{ METACLASSES                        }....................
class BeartypeForwardRefMeta(type):
    '''
    **Forward reference metaclass** (i.e., metaclass of the
    :class:`.BeartypeForwardRefABC` superclass deferring the resolution of a
    stringified type hint referencing an attribute that has yet to be defined
    and annotating a class or callable decorated by the
    :func:`beartype.beartype` decorator).

    This metaclass memoizes each **forward reference** (i.e.,
    :class:`.BeartypeForwardRefABC` instance) according to the fully-qualified
    name of the attribute referenced by that forward reference. Doing so ensures
    that only the first :class:`.BeartypeForwardRefABC` instance referring to a
    unique attribute is required to dynamically resolve that attribute at
    runtime; all subsequent :class:`.BeartypeForwardRefABC` instances referring
    to the same attribute transparently reuse the attribute previously resolved
    by the first such instance, effectively reducing the time cost of resolving
    forward references to a constant-time operation with negligible constants.

    This metaclass dynamically and efficiently resolves each forward reference
    in a just-in-time (JIT) manner on the first :func:`isinstance` call whose
    second argument is that forward reference. Forward references *never* passed
    to the :func:`isinstance` builtin are *never* resolved, which is good.
    '''

    # ....................{ DUNDERS                        }....................
    def __getattr__(cls: BeartypeForwardRef, hint_name: str) -> (  # type: ignore[misc]
        BeartypeForwardRef):
        '''
        **Fully-qualified forward reference subclass** (i.e.,
        :class:`.BeartypeForwardRefABC` subclass whose metaclass is this
        metaclass and whose :attr:`.BeartypeForwardRefABC.__name_beartype__`
        class variable is the fully-qualified name of an external class).

        This dunder method creates and returns a new forward reference subclass
        referring to an external class whose name is concatenated from (in
        order):

        #. The fully-qualified name of the external package or module referred
           to by the passed forward reference subclass.
        #. The passed unqualified basename, presumably referring to a
           subpackage, submodule, or class of that external package or module.

        Parameters
        ----------
        cls : Type[BeartypeForwardRefABC]
            Forward reference subclass to concatenate this basename against.
        hint_name : str
            Unqualified basename to be concatenated against this forward
            reference subclass.

        Returns
        -------
        Type['_BeartypeForwardRefIndexableABC']
            Fully-qualified forward reference subclass concatenated as described
            above.
        '''

        # Avoid circular import dependencies.
        from beartype._check.forward.reference.fwdrefmake import (
            make_forwardref_indexable_subtype)

        # If this unqualified basename is that of a non-existent dunder
        # attribute, raise the standard "AttributeError" exception.
        #
        # Note that we intentionally avoid suffixing the exception message by a
        # "." character here. Why? Because Python treats "AttributeError"
        # exceptions as special. Notably, Python appears to actually:
        # 1. Parse apart the messages of these exceptions for the double-quoted
        #    attribute name embedded in these messages.
        # 2. Suffix these messages by a "." character followed by a sentence
        #    suggesting an existing attribute with a similar name to that of the
        #    attribute name previously parsed from these messages.
        #
        # For example, given an erroneous lookup of a non-existent dunder
        # attribute "__nomnom_beartype__", Python expands the exception message
        # raised below into:
        #     AttributeError: Forward reference proxy "MuhRef" dunder attribute
        #     "__nomnom_beartype__" not found. Did you mean:
        #     '__name_beartype__'?
        if is_dunder(hint_name):
            raise AttributeError(
                f'Forward reference proxy "{cls.__name__}" dunder attribute '
                f'"{hint_name}" not found'
            )
        # Else, this unqualified basename is *NOT* that of a non-existent dunder
        # attribute.

        # Return a new fully-qualified forward reference subclass concatenated
        # as described above.
        return make_forwardref_indexable_subtype(
            cls.__scope_name_beartype__,  # type: ignore[arg-type]
            f'{cls.__name_beartype__}.{hint_name}',
        )


    def __instancecheck__(cls: BeartypeForwardRef, obj: object) -> bool:  # type: ignore[misc]
        '''
        :data:`True` only if the passed object is an instance of the external
        class referenced by the passed **forward reference subclass** (i.e.,
        :class:`.BeartypeForwardRefABC` subclass whose metaclass is this
        metaclass and whose :attr:`.BeartypeForwardRefABC.__name_beartype__`
        class variable is the fully-qualified name of that external class).

        Parameters
        ----------
        cls : Type[BeartypeForwardRefABC]
            Forward reference subclass to test this object against.
        obj : object
            Arbitrary object to be tested as an instance of the external class
            referenced by this forward reference subclass.

        Returns
        -------
        bool
            :data:`True` only if this object is an instance of the external
            class referenced by this forward reference subclass.
        '''

        # Return true only if this forward reference subclass insists that this
        # object satisfies the external class referenced by this subclass.
        return cls.__is_instance_beartype__(obj)


    def __subclasscheck__(cls: BeartypeForwardRef, obj: object) -> bool:  # type: ignore[misc]
        '''
        :data:`True` only if the passed object is a subclass of the external
        class referenced by the passed **forward reference subclass** (i.e.,
        :class:`.BeartypeForwardRefABC` subclass whose metaclass is this
        metaclass and whose :attr:`.BeartypeForwardRefABC.__name_beartype__`
        class variable is the fully-qualified name of that external class).

        Parameters
        ----------
        cls : Type[BeartypeForwardRefABC]
            Forward reference subclass to test this object against.
        obj : object
            Arbitrary object to be tested as a subclass of the external class
            referenced by this forward reference subclass.

        Returns
        -------
        bool
            :data:`True` only if this object is a subclass of the external class
            referenced by this forward reference subclass.
        '''

        # Return true only if this forward reference subclass insists that this
        # object is an instance of the external class referenced by this
        # subclass.
        return cls.__is_subclass_beartype__(obj)


    def __repr__(cls: BeartypeForwardRef) -> str:  # type: ignore[misc]
        '''
        Machine-readable string representing this forward reference subclass.
        '''

        # Machine-readable representation to be returned.
        #
        # Note that this representation is intentionally prefixed by the
        # @beartype-specific substring "<forwardref ", resembling the
        # representation of classes (e.g., "<class 'bool'>"). Why? Because
        # various other @beartype submodules ignore objects whose
        # representations are prefixed by the "<" character, which are usefully
        # treated as having a standard representation that is ignorable for most
        # intents and purposes. This includes:
        # * The die_if_hint_pep604_inconsistent() raiser.
        cls_repr = (
            f'<forwardref {cls.__name__}('
              f'__name_beartype__={repr(cls.__name_beartype__)}'
            f', __scope_name_beartype__={repr(cls.__scope_name_beartype__)}'
        )

        #FIXME: Unit test this edge case, please.
        # If this is a subscripted forward reference subclass, append additional
        # metadata representing this subscription.
        #
        # Ideally, we would test whether this is a subclass of the
        # "_BeartypeForwardRefIndexedABC" superclass as follows:
        #     if issubclass(cls, _BeartypeForwardRefIndexedABC):
        #
        # Sadly, doing so invokes the __subclasscheck__() dunder method defined
        # above, which invokes the
        # BeartypeForwardRefABC.__is_subclass_beartype__() method defined
        # above, which tests the type referred to by this subclass rather than
        # this subclass itself. In short, this is why you play with madness.
        try:
            cls_repr += (
                f', __args_beartype__={repr(cls.__args_beartype__)}'
                f', __kwargs_beartype__={repr(cls.__kwargs_beartype__)}'
            )
        # If doing so fails with the expected "AttributeError", then this is
        # *NOT* a subscripted forward reference subclass. Since this is
        # ignorable, silently ignore this common case. *sigh*
        except AttributeError:
            pass

        # Close this representation.
        cls_repr += ')>'

        # Return this representation.
        return cls_repr

    # ....................{ PROPERTIES                     }....................
    @property
    def __type_beartype__(cls: BeartypeForwardRef) -> type:  # type: ignore[misc]
        '''
        **Forward referee** (i.e., type hint referenced by this forward
        reference subclass, which is usually but *not* necessarily a class).

        This class property is manually memoized for efficiency. However, note
        this class property is *not* automatically memoized (e.g., by the
        ``property_cached`` decorator). Why? Because manual memoization enables
        other functionality in the beartype codebase to explicitly unmemoize all
        previously memoized forward referees across all forward reference
        proxies, effectively forcing all subsequent calls of this property
        across all forward reference proxies to reimport their forward referees.
        Why is that desirable? Because other functionality in the beartype
        codebase detects when the user has manually reloaded user-defined
        modules defining user-defined types annotating user-defined callables
        previously decorated by the :mod:`beartype.beartype` decorator. Since
        reloading those modules redefines those types, all previously cached
        types (including those memoized by this property) *must* then be assumed
        to be invalid and thus uncached. In short, manual memoization allows
        beartype to avoid desynchronization between memoized and actual types.

        Raises
        ------
        BeartypeCallHintForwardRefException
            If either:

            * This forward referee is unimportable.
            * This forward referee is importable but either:

              * Not a type.
              * A type that is this forward reference proxy, implying this proxy
                circularly proxies itself.
        '''

        # Forward referee referred to by this forward reference proxy if a prior
        # access of this property has already resolved this referee *OR* "None"
        # otherwise (i.e., if this is the first access of this property).
        referee = _forwardref_to_referee.get(cls)

        # If this forward referee has yet to be resolved, this is the first call
        # to this property. In this case...
        if referee is None:  # type: ignore[has-type]
            # print(f'Importing forward ref "{cls.__name_beartype__}" from module "{cls.__scope_name_beartype__}"...')

            # Forward referee dynamically imported from this module.
            referee = import_module_attr(
                attr_name=cls.__name_beartype__,
                module_name=cls.__scope_name_beartype__,
                exception_cls=BeartypeCallHintForwardRefException,
                exception_prefix='Forward reference ',
            )

            # If this referee is this forward reference subclass, then this
            # subclass circularly proxies itself. Since allowing this edge case
            # would openly invite infinite recursion, we detect this edge case
            # and instead raise a human-readable exception.
            if referee is cls:
                raise BeartypeCallHintForwardRefException(
                    f'Forward reference proxy {repr(cls)} circularly '
                    f'(i.e., infinitely recursively) references itself.'
                )
            # Else, this referee is *NOT* this forward reference subclass.
            #
            # If this referee is a subscripted generic (e.g.,
            # "MuhGeneric[int]"), reduce this referee to the class subscripting
            # this generic (e.g., "int").
            elif is_hint_pep484585_generic(referee):
                referee = get_hint_pep484585_generic_type(
                    hint=referee,
                    exception_cls=BeartypeCallHintForwardRefException,
                    exception_prefix='Forward reference ',
                )
            # Else, this referee is *NOT* a subscripted generic.

            # If this referee is *NOT* an isinstanceable class, raise an
            # exception.
            die_unless_object_isinstanceable(
                obj=referee,
                exception_cls=BeartypeCallHintForwardRefException,
                exception_prefix='Forward reference ',
            )
            # Else, this referee is an isinstanceable class.

            # Cache this referee for subsequent lookup by this property.
            _forwardref_to_referee[cls] = referee
        # Else, this referee has already been resolved.
        #
        # In either case, this referee is now resolved.

        # Return this previously resolved referee.
        return referee  # type: ignore[return-value]

# ....................{ PRIVATE ~ globals                  }....................
_forwardref_to_referee: Dict[BeartypeForwardRef, type] = {}
'''
**Forward reference referee cache** (i.e., dictionary mapping from each forward
reference proxy to the arbitrary class referred to by that proxy).

This cache serves a dual purpose. Notably, this cache both enables:

* External callers to iterate over all previously instantiated forward reference
  proxies. This is particularly useful when responding to module reloading,
  which requires that *all* previously cached types be uncached.
* The
  :attr:`.BeartypeForwardRefMeta.__type_beartype__` property to internally
  memoize the arbitrary class referred to by this referee. Since the existing
  ``property_cached`` decorator could trivially do so as well, however, this is
  only a negligible side effect.
'''
