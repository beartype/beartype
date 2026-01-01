#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`484`--compliant **absolute forward reference type hint
utilities** (i.e., low-level callables introspecting :pep:`484`-compliant
forward reference type hints whose resolution is absolute and thus requires *no*
parent objects to resolve those hints against).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ TODO                               }....................
#FIXME: Rename these submodules as follows for clarity:
#* "pep484refabsolute" -> "pep484refcanonic".
#* "pep484refrelative" -> "pep484refgeneral".

#FIXME: The following logic at the head of the canonicalize_hint_pep484_ref()
#implementation made considerable sense under Python < 3.13:
#    hint_module_name, hint_type_name = get_hint_pep484_ref_names_relative(
#        hint=hint,
#        exception_cls=exception_cls,
#        exception_prefix=exception_prefix,
#    )
#
#After all, "typing.ForwardRef" objects were just thin wrappers around simple
#strings. Reducing the former to the latter was reasonable. Under Python >=
#3.14, however, reducing "typing.ForwardRef" objects to the 2-tuple
#"(hint_module_name, hint_type_name)" is a *REALLY* bad idea.
#"typing.ForwardRef" objects are actually "annotationlib.ForwardRef" objects,
#now. They encapsulate *A LOT* of awesome functionality that cannot reasonably
#be reduced to two strings like we are currently doing.
#
#Generalize this as follows, please:
#* If this is Python >= 3.14, the passed "hint" is a "typing.ForwardRef" object,
#  *AND* this object defines a sufficient number of PEP 649-compliant dunder
#  attributes to ensure that its evaluate() method can safely canonicalize that
#  reference if relative to the referent it refers to:
#  * Then preserve this "hint" as is by trivially returning this "hint"
#    unmodified.
#
#Note that what exactly "a sufficient number of PEP 649-compliant dunder
#attributes" means can be reverse-engineered from the ForwardNef.evaluate()
#method. Specifically, if this hint defines one or more of these instance
#variables to be non-"None", then this hint can be safely canonicalized and
#resolved by calling hint.evaluate():
#* "hint.__forward_module__".
#* "hint.__globals__".
#* "hint.__owner__".
#FIXME: Of course, this isn't enough. Callers currently expect this getter to
#return 2-tuples of strings -- not single "typing.ForwardRef" objects.
#Refactoring the codebase from the former approach to the latter will prove...
#non-trivial yet extremely valuable.
#
#First, let's start with "typing.ForwardRef". In and of itself,
#"typing.ForwardRef" isn't enough. Unlike beartype-specific forward reference
#proxies, the "typing.ForwardRef" type does *NOT* have a metaclass defining the
#__instancecheck__() dunder method. In fact, the "typing.ForwardRef" type does
#*NOT* have a metaclass... *PERIOD.* Without the __instancecheck__() dunder
#method, "typing.ForwardRef" objects are unusable in a general-purpose context.
#
#To render "typing.ForwardRef" objects usable in a general-purpose context,
#we'll need to:
#* Define a new "__annotationlib_beartype__: Optional[typing.ForwardRef] = None"
#  class variable in the existing "BeartypeForwardRefABC" superclass.
#* Generalize the "BeartypeForwardRefMeta.__type_beartype__" property method to
#  preferentially resolve this forward reference via "annotationlib"-specific
#  rather than beartype-specific functionality: e.g.,
#      @property
#      def __type_beartype__(cls: BeartypeForwardRef) -> type:
#         ...
#         if cls.__annotationlib_beartype__ is not None:
#             referent = cls.__annotationlib_beartype__.evaluate()
#* Define a new make_forwardref_annotationlib_subtype() factory function in the
#  existing "beartype._check.forward.reference.fwdrefmake" submodule with
#  signature resembling:
#      from typing import ForwardRef
#      def make_forwardref_annotationlib_subtype(
#          hint: ForwardRef) -> type[BeartypeForwardRefABC]:
#* Define a new reusable "Pep484RefCanonicalized" type hint in the existing
#  "beartype._data.typing.datatyping" submodule resembling:
#      Pep484RefCanonicalized = typing.ForwardRef | tuple[str, str]
#* Define a new higher-level make_forwardref_annotationlib_subtype() factory
#  function in the existing "beartype._check.forward.reference.fwdrefmake"
#  submodule with signature and logic resembling:
#      from beartype._data.typing.datatyping import Pep484RefCanonicalized
#      from typing import ForwardRef
#
#      def make_forwardref_canonicalized_subtype(
#          hint: Pep484RefCanonicalized) -> type[BeartypeForwardRefABC]:
#          if isinstance(hint, tuple):
#              #FIXME: Validate tuple length here, obviously. *sigh*
#              hint_module_name, hint_type_name = hint
#              return make_forwardref_subbable_subtype(
#                  scope_name=hint_module_name,
#                  hint_name=hint_type_name,
#              )
#          elif isinstance(hint, ForwardRef):
#              return make_forwardref_annotationlib_subtype(hint)
#FIXME: Next, we'll need to hunt down *ALL* calls to
#get_hint_pep484_ref_names_relative() throughout the codebase. These calls are
#now all problematic, because they improperly reduce "typing.ForwardRef" objects
#to 2-tuples of strings. We'll need to ideally refactor these calls into calls
#to canonicalize_hint_pep484_ref() instead.
#FIXME: Next, we'll need to hunt down *ALL* calls to
#canonicalize_hint_pep484_ref() throughout the codebase. These calls are fine,
#but the parent logic that's calling them is no longer fine. Why? Because that
#logic assumes canonicalize_hint_pep484_ref() to return 2-tuples of strings.
#Parent logic will now need to *STOP* unpacking the value returned by
#canonicalize_hint_pep484_ref(). Instead, parent logic should simply pass that
#return value around without inspecting its contents too deeply.
#FIXME: Relatedly, the existing
#beartype._check.code.codescope.add_func_scope_ref() function is... problematic.
#As it is, that function is just a thin shim around the more full-bodied
#make_forwardref_subbable_subtype() and add_func_scope_attr() functions that do
#all the actual real work. At the very least, we'll need to refactor
#add_func_scope_ref() to accept a single "hint: Pep484RefCanonicalized"
#parameter rather than the two parameters it currently accepts.
#FIXME: Once all of that's working, consider:
#* Privatizing the lower-level make_forwardref_annotationlib_subtype() and
#  make_forwardref_subbable_subtype() factory functions.
#* Refactoring all calls to those functions to the higher-level
#  make_forwardref_canonicalized_subtype() factory function instead.
#
#Lots to do... but surely fun and valuable stuff! Surely! Oh, Gods...

# ....................{ IMPORTS                            }....................
from beartype.roar import BeartypeDecorHintForwardRefException
from beartype._cave._cavefast import HintPep484RefTypes
from beartype._cave._cavemap import NoneTypeOr
from beartype._data.cls.datacls import TYPE_BUILTIN_NAME_TO_TYPE
from beartype._data.typing.datatyping import (
    HintPep484Ref,
    TupleStrAndStr,
    TupleStrOrNoneAndStr,
    TypeException,
    TypeStack,
)
from beartype._data.api.standard.datapy import BUILTINS_MODULE_NAME
from beartype._data.typing.datatypingport import Hint
from beartype._util.module.utilmodget import get_object_module_name_or_none
from beartype._util.text.utiltextlabel import (
    label_callable,
    label_type,
)
from beartype._util.text.utiltextmunge import uppercase_str_char_first
from collections.abc import (
    Callable,
    Sequence,
)
from typing import (
    ForwardRef,
    NoReturn,
    Optional,
    Union,
)

# ....................{ CANONICALIZERS                     }....................
def canonicalize_hint_pep484_ref(
    # Mandatory parameters.
    hint: HintPep484Ref,

    # Optional parameters.
    cls_stack: TypeStack = None,
    func: Optional[Callable] = None,
    exception_cls: TypeException = BeartypeDecorHintForwardRefException,
    exception_prefix: str = '',
) -> TupleStrAndStr:
    '''
    Fully-qualified module name and unqualified classname referred to by the
    passed :pep:`484`-compliant **forward reference hint** (i.e., object
    indirectly referring to a user-defined type that typically has yet to be
    defined), canonicalized relative to the module declaring the passed type
    stack and/or callable (in that order) if this classname is unqualified.

    This getter is intentionally *not* memoized (e.g., by the
    ``callable_cached`` decorator), as the implementation mostly reduces to an
    efficient one-liner.

    Caveats
    -------
    This getter preferentially canonicalizes this forward reference if relative
    against the fully-qualified name of the module defining (in order):

    #. The passed class stack if *not* :data:`None`.
    #. The passed callable.

    This getter thus prioritizes classes over callables. Why? Because classes
    are more likely to define ``__module__`` dunder attributes referring to
    importable modules that physically exist. Why? Because dynamically
    synthesizing in-memory callables residing in imaginary and thus unimportable
    modules is trivial; dynamically synthesizing in-memory classes residing in
    imaginary and thus unimportable modules is less trivial.

    Consider the standard use case for :mod:`beartype`: beartype import hooks
    declared by the :mod:`beartype.claw` subpackage. Although hooks directly
    apply the :func:`beartype.beartype` decorator to classes and functions
    residing in importable modules that physically exist, that decorator then
    dynamically iterates over the methods of those classes. That iteration is
    dynamic and iterates over methods that both physically exist and only
    dynamically exist in-memory in unimportable modules.

    Does this edge case arise in real-world code? All too frequently. For
    unknown reasons, the :class:`typing.NamedTuple` superclass dynamically
    generates dunder methods (e.g., ``__new__``) whose ``__module__`` dunder
    attributes erroneously refer to imaginary and thus unimportable modules
    ``named_{subclass_name}`` for the unqualified basename ``{subclass_name}``
    of the current user-defined class subclassing :class:`typing.NamedTuple`
    despite that user-defined class residing in an importable module: e.g.,

    .. code-block:: pycon

       >>> from beartype import beartype
       >>> from typing import NamedTuple

       >>> @beartype
       ... class NamelessTupleIsBlameless(NamedTuple):
       ...     forward_ref: 'UndefinedType'

       >>> NamelessTupleIsBlameless.__module__
       '__main__'                        # <-- makes sense
       >>> NamelessTupleIsBlameless.__new__.__module__
       'named_NamelessTupleIsBlameless'  # <-- lol wut

    If this getter erroneously prioritized callables over classes *and* blindly
    accepted imaginary modules as valid, this getter would erroneously resolve
    the relative forward reference ``'UndefinedType'`` to
    ``'named_NamelessTupleIsBlameless.UndefinedType'`` rather than to
    ``'__main__.UndefinedType'``. And... this is why @leycec is currently bald.

    Parameters
    ----------
    hint : object
        Forward reference to be canonicalized.
    cls_stack : TypeStack, default: None
        Either:

        * If this forward reference annotates a method of a class, the
          corresponding **type stack** (i.e., tuple of the one or more
          :func:`beartype.beartype`-decorated classes lexically containing that
          method). If this forward reference is unqualified (i.e., relative),
          this getter then canonicalizes this reference against that class.
        * Else, :data:`None`.

        Defaults to :data:`None`.
    func : Optional[Callable], default: None
        Either:

        * If this forward reference annotates a callable, that callable.
          If this forward reference is also unqualified (i.e., relative), this
          getter then canonicalizes this reference against that callable.
        * Else, :data:`None`.

        Defaults to :data:`None`.
    exception_cls : Type[Exception], default: BeartypeDecorHintForwardRefException
        Type of exception to be raised in the event of a fatal error. Defaults
        to :exc:`.BeartypeDecorHintForwardRefException`.
    exception_prefix : str, default: ''
        Human-readable label prefixing the representation of this object in the
        exception message. Defaults to the empty string.

    Returns
    -------
    tuple[str, str]
        2-tuple ``(hint_module_name, hint_type_name)`` where:

        * ``hint_module_name`` is the fully-qualified module name referred to by
          this forward reference.
        * ``hint_type_name`` is the unqualified classname referred to by this
          forward reference.

    Raises
    ------
    exception_cls
        If either:

        * This forward reference is *not* actually a forward reference.
        * This forward reference is **relative** (i.e., contains *no* ``.``
          delimiters) and either:

          * Neither the ``cls_stack`` nor ``func`` parameters were passed
            *or*...
          * Either the ``cls_stack`` or ``func`` parameters were passed but
            neither defines the ``__module__`` dunder attribute *or*...
          * Either the ``cls_stack`` or ``func`` parameters were passed and
            define the ``__module__`` dunder attribute, but the values of those
            attributes all refer to unimportable modules that do *not* appear to
            physically exist.

    See Also
    --------
    :func:`.get_hint_pep484_ref_names_relative`
        Lower-level getter returning possibly relative forward references.
    '''
    assert isinstance(cls_stack, NoneTypeOr[Sequence]), (
        f'{repr(cls_stack)} neither sequence nor "None".')
    assert isinstance(func, NoneTypeOr[Callable]), (
        f'{repr(func)} neither callable nor "None".')

    # ....................{ IMPORTS                        }....................
    # Avoid circular import dependencies.
    from beartype._util.hint.pep.proposal.pep484.forward.pep484refrelative import (
        get_hint_pep484_ref_names_relative)

    # ....................{ LOCALS                         }....................
    # Possibly undefined fully-qualified module name and possibly unqualified
    # classname referred to by this forward reference. Notably, the following
    # constraints now hold:
    #    >>> hint_module_name is None or (
    #    ...     isinstance(hint_module_name, str) and
    #    ...     len(hint_module_name)
    #    ... )
    #    True
    #    >>> isinstance(hint_type_name, str) and len(hint_type_name)
    #    True
    hint_module_name, hint_type_name = get_hint_pep484_ref_names_relative(
        hint=hint,
        exception_cls=exception_cls,
        exception_prefix=exception_prefix,
    )

    # 0-based index of the current canonicalizer (i.e., private getter in the
    # _canonicalize_hint_pep484_ref_*() family of private getters
    # responsible for canonicalizing this reference) being attempted from the
    # "_HINT_CANONICALIZERS" tuple by the "while" loop performed below,
    # initialized so as to iterate starting at the first canonicalizer.
    hint_canonicalizer_index = -1

    # Current canonicalizer.
    hint_canonicalizer: _HintCanonicalizer = None  # type: ignore[assignment]

    # True only if this classname contains one or more "." characters and is
    # thus already (...hopefully) fully-qualified, conditionally defined *ONLY*
    # when the fully-qualified name of the module defining the attribute to
    # which this reference refers has yet to be decided. Since string searching
    # is expensive, this operation is performed *ONLY* as needed as a
    # microoptimization. Insert "Let him cook!" meme here.
    is_hint_type_name_qualified = (
        '.' in hint_type_name if not hint_module_name else '')

    # ....................{ CANONICALIZERS                 }....................
    # While the fully-qualified name of the module defining the attribute to
    # which this reference refers has yet to be decided...
    while not hint_module_name:
        # Increment the 0-based index of the current canonicalizer.
        hint_canonicalizer_index += 1

        # If this index exceeds that of the last available canonicalizer, no
        # canonicalizer successfully canonicalized this relative forward
        # reference. In this case, raise an exception describing this failure.
        if hint_canonicalizer_index >= _HINT_CANONICALIZER_INDEX_MAX:
            _die_as_ref_uncanonicalizable(
                hint_module_name=hint_module_name,
                hint_type_name=hint_type_name,
                cls_stack=cls_stack,
                func=func,
                exception_cls=exception_cls,
                exception_prefix=exception_prefix,
            )
        # Else, this index corresponds to that of an available canonicalizer.

        # Current canonicalizer.
        hint_canonicalizer = _HINT_CANONICALIZERS[hint_canonicalizer_index]

        # Either:
        # * If this canonicalizer successfully canonicalized this relative
        #   forward reference, the fully-qualified module name and qualified
        #   classname referred to by this reference.
        # * Else, the currently undefined module name and possibly unqualified
        #   classname preserved as is.
        hint_canonicalized = hint_canonicalizer(
            hint_type_name=hint_type_name,
            is_hint_type_name_qualified=is_hint_type_name_qualified,
            cls_stack=cls_stack,
            func=func,
            exception_cls=exception_cls,
            exception_prefix=exception_prefix,
        )

        # Strip the module and classname from the tuple returned by the prior
        # canonicalization call. Athough most canonicalizers return 2-tuples,
        # some return 3-tuples whose third item "hint_referent" is
        # unconditionally irrelevant to this specific decision problem.
        hint_module_name = hint_canonicalized[0]
        hint_type_name = hint_canonicalized[1]

    # ....................{ RETURN                         }....................
    # Guarantee sanity for caller convenience.
    assert hint_module_name, (
        f'{exception_prefix}relative forward reference "{hint}" '
        f'module name unparseable.'
    )
    assert hint_type_name, (
        f'{exception_prefix}relative forward reference "{hint}" '
        f'attribute name unparseable.'
    )

    # Return the 2-tuple of these names.
    return hint_module_name, hint_type_name


#FIXME: Obsolete in favour of find_ref_relative_on_cls_stack(), please. *sigh*
def canonicalize_hint_pep484_ref_relative_to_type_name(
    # Mandatory parameters.
    hint: HintPep484Ref,
    cls_stack: TypeStack,

    # Optional parameters.
    exception_cls: TypeException = BeartypeDecorHintForwardRefException,
    exception_prefix: str = '',
) -> TupleStrOrNoneAndStr:
    '''
    Possibly undefined fully-qualified module name and possibly unqualified
    classname referred to by the passed forward reference, canonicalized
    relative to the module declaring the passed type stack if this reference is
    the partially-qualified name of the currently decorated (i.e., most deeply
    nested) class on the passed type stack *or* preserved as is otherwise.

    Parameters
    ----------
    hint : HintPep484Ref
        Forward reference to be canonicalized.
    cls_stack : TypeStack
        Either:

        * If this forward reference annotates a method of a class, the
          corresponding **type stack** (i.e., tuple of the one or more nested
          :func:`beartype.beartype`-decorated classes lexically containing that
          method).
        * Else, :data:`None`.
    exception_cls : Type[Exception], default: BeartypeDecorHintForwardRefException
        Type of exception to be raised in the event of a fatal error. Defaults
        to :exc:`.BeartypeDecorHintForwardRefException`.
    exception_prefix : str, default: ''
        Human-readable substring prefixing raised exception messages. Defaults
        to the empty string.

    Returns
    -------
    tuple[Optional[str], str]
        2-tuple ``(hint_module_name, hint)`` such that:

        * If this classname is the partially-qualified name of the currently
          decorated (i.e., most deeply nested) class on the type stack, then:

          * ``hint_module_name`` is the fully-qualified name of the module
            declaring that class.
          * ``hint`` is the passed parameter.

        * Else, ``(None, hint)`` where ``hint`` is the passed parameter.
    '''
    assert isinstance(hint, HintPep484RefTypes), (
        f'{repr(hint)} neither string nor "typing.ForwardRef" object.')
    assert isinstance(cls_stack, NoneTypeOr[Sequence]), (
        f'{repr(cls_stack)} neither sequence nor "None".')

    # If this forward reference is a "typing.ForwardRef" instance...
    if isinstance(hint, ForwardRef):
        # Avoid circular import dependencies.
        from beartype._util.hint.pep.proposal.pep484.forward.pep484refrelative import (
            get_hint_pep484_ref_names_relative)

        # Possibly undefined fully-qualified module name and possibly
        # unqualified classname referred to by this forward reference.
        hint_module_name, hint = get_hint_pep484_ref_names_relative(
            hint=hint,
            exception_cls=exception_cls,
            exception_prefix=exception_prefix,
        )

        # If this forward reference is already absolute, this forward reference
        # *CANNOT* be definition be relative (let alone relative to a type on
        # the passed type stack). In this case, feign ignorance by silently
        # destroying this module name. It is what it is.
        if hint_module_name:
            return None, hint
        # Else, this forward reference is relative as expected.
    # Else, this forward reference is a simple string. This is the common
    # case. In this case, preserve this string as is.

    # Defer to this lower-level private getter.
    return _find_ref_relative_on_cls_stack(
        hint_type_name=hint,
        # Default this boolean to a string test in the trivial manner.
        is_hint_type_name_qualified='.' in hint,
        cls_stack=cls_stack,
    )[0:2]

# ....................{ FINDERS                            }....................
#FIXME: Additionally unit test the edge case of finding the middle-most type on
#the passed type stack, please. *sigh*
def find_ref_relative_on_cls_stack_or_none(
    # Mandatory parameters.
    hint: HintPep484Ref,
    cls_stack: TypeStack,

    # Optional parameters.
    exception_cls: TypeException = BeartypeDecorHintForwardRefException,
    exception_prefix: str = '',
) -> Optional[type]:
    '''
    Possibly undefined fully-qualified module name and possibly unqualified
    classname referred to by the passed forward reference, canonicalized
    relative to the module declaring the passed type stack if this reference is
    the partially-qualified name of the currently decorated (i.e., most deeply
    nested) class on the passed type stack *or* preserved as is otherwise.

    Parameters
    ----------
    hint : HintPep484Ref
        Forward reference to be canonicalized.
    cls_stack : TypeStack
        Either:

        * If this forward reference annotates a method of a class, the
          corresponding **type stack** (i.e., tuple of the one or more nested
          :func:`beartype.beartype`-decorated classes lexically containing that
          method).
        * Else, :data:`None`.
    exception_cls : Type[Exception], default: BeartypeDecorHintForwardRefException
        Type of exception to be raised in the event of a fatal error. Defaults
        to :exc:`.BeartypeDecorHintForwardRefException`.
    exception_prefix : str, default: ''
        Human-readable substring prefixing raised exception messages. Defaults
        to the empty string.

    Returns
    -------
    tuple[Optional[str], str]
        2-tuple ``(hint_module_name, hint)`` such that:

        * If this classname is the partially-qualified name of the currently
          decorated (i.e., most deeply nested) class on the type stack, then:

          * ``hint_module_name`` is the fully-qualified name of the module
            declaring that class.
          * ``hint`` is the passed parameter.

        * Else, ``(None, hint)`` where ``hint`` is the passed parameter.
    '''
    assert isinstance(hint, HintPep484RefTypes), (
        f'{repr(hint)} neither string nor "typing.ForwardRef" object.')
    assert isinstance(cls_stack, NoneTypeOr[Sequence]), (
        f'{repr(cls_stack)} neither sequence nor "None".')

    # If this forward reference is a "typing.ForwardRef" instance...
    if isinstance(hint, ForwardRef):
        # Avoid circular import dependencies.
        from beartype._util.hint.pep.proposal.pep484.forward.pep484refrelative import (
            get_hint_pep484_ref_names_relative)

        # Possibly undefined fully-qualified module name and possibly
        # unqualified classname referred to by this forward reference.
        hint_module_name, hint = get_hint_pep484_ref_names_relative(
            hint=hint,
            exception_cls=exception_cls,
            exception_prefix=exception_prefix,
        )

        # If this forward reference is already absolute, this forward reference
        # *CANNOT* be definition be relative (let alone relative to a type on
        # the passed type stack). In this case, feign ignorance by silently
        # reducing to a noop. It is what it is.
        if hint_module_name:
            return None
        # Else, this forward reference is relative as expected.
    # Else, this forward reference is a simple string. This is the common
    # case. In this case, preserve this string as is.

    # Either:
    # * If this reference is the partially-qualified name of a type on this
    #   type stack, the 3-tuple "(hint_module_name, hint_type_name, hint_type)"
    #   describing the canonicalization of this relative forward reference
    #   relative to the module declaring this type stack.
    # * Else, the 3-tuple "(None, hint_type_name, None)".
    _, _, hint_type = _find_ref_relative_on_cls_stack(
        hint_type_name=hint,
        # Default this boolean to a string test in the trivial manner.
        is_hint_type_name_qualified='.' in hint,
        cls_stack=cls_stack,
    )

    # Return the type on this type stack referred to by this relative forward
    # reference if any *OR* "None" otherwise.
    return hint_type

# ....................{ PRIVATE ~ hints                    }....................
_HintCanonicalizationSansReferent = TupleStrOrNoneAndStr
'''
:pep:`585`-compliant type hint matching a **referent-free canonicalizer return
value** (i.e., data structure returned by callables in the
``_canonicalize_hint_pep484_ref_*()`` family of private getters iteratively
called by the public :func:`.canonicalize_hint_pep484_ref` getter to
canonicalize :pep:`484`-compliant relative forward references but which do *not*
additionally return the object referred to by those references).

This hint matches a 2-tuple ``(hint_module_name, hint_type_name)`` returned by a
private canonicalizer such that:

* If that canonicalizer successfully canonicalized the passed relative forward
  reference, then:

  * ``hint_module_name`` is the fully-qualified name of the module to which
    that reference is relative.
  * ``hint_type_name`` is the possibly unqualified basename of the type to which
    that reference refers.

* Else, ``(None, hint_type_name)`` where ``hint_type_name`` is the parameter of
  the same name passed to that canonicalizer.
'''


_HintCanonicalizationWithReferent = tuple[Optional[str], str, Optional[Hint]]
'''
:pep:`585`-compliant type hint matching a **referential canonicalizer return
value** (i.e., data structure unconditionally returned by every callable in the
``_canonicalize_hint_pep484_ref_*()`` family of private getters iteratively
called by the public :func:`.canonicalize_hint_pep484_ref` getter to
canonicalize :pep:`484`-compliant relative forward references and which
additionally return the object referred to by those references).

This hint matches a 3-tuple ``(hint_module_name, hint_type_name,
hint_referent)`` returned by a private canonicalizer such that:

* If that canonicalizer successfully canonicalized the passed relative forward
  reference, then:

  * ``hint_module_name`` is the fully-qualified name of the module to which
    that reference is relative.
  * ``hint_type_name`` is the possibly unqualified basename of the type to which
    that reference refers.
  * ``hint_referent`` is either:

    * If that type is trivially resolvable by that canonicalizer at this early
      calling time *without* requiring deferral to a later time via a full-blown
      forward reference proxy (e.g., due to that type literally being a type on
      the ``cls_stack`` parameter passed to that canonicalizer), that type. Due
      to self-references, this case is surprisingly common.
    * Else, :data:`None`. This is the mostly common case.

* Else, ``(None, hint_type_name, None)`` where ``hint_type_name`` is the
  parameter of the same name passed to that canonicalizer.
'''


_HintCanonicalizerReturn = Union[
    _HintCanonicalizationSansReferent,
    _HintCanonicalizationWithReferent,
]
'''
:pep:`585`-compliant type hint matching a **canonicalizer return value** (i.e.,
data structure unconditionally returned by every callable in the
``_canonicalize_hint_pep484_ref_*()`` family of private getters iteratively
called by the public :func:`.canonicalize_hint_pep484_ref` getter to
canonicalize :pep:`484`-compliant relative forward references).
'''


_HintCanonicalizer = Callable[..., _HintCanonicalizerReturn]
'''
:pep:`585`-compliant type hint matching a **canonicalizer** (i.e., callable in
the ``_canonicalize_hint_pep484_ref_*()`` family of private getters iteratively
called by the public :func:`.canonicalize_hint_pep484_ref` getter to
canonicalize :pep:`484`-compliant relative forward references).
'''

# ....................{ PRIVATE ~ raisers                  }....................
def _die_as_ref_uncanonicalizable(
    hint_module_name: Optional[str],
    hint_type_name: str,
    cls_stack: TypeStack,
    func: Optional[Callable],
    exception_cls: TypeException,
    exception_prefix: str,
) -> NoReturn:
    '''
    Unconditionally raise an exception of the passed type describing why the
    passed :pep:`484`-compliant **relative forward reference hint** (i.e.,
    object indirectly referring to a user-defined type that typically has yet to
    be defined, relative to a user-defined module whose name is unknown) could
    *not* be canonicalized into an absolute forward reference by the parent
    :func:`.canonicalize_hint_pep484_ref` getter.

    Parameters
    ----------
    hint_module_name : Optional[str]
        Possibly undefined fully-qualified name of the module referred to be
        this relative forward reference.

    See :func:`.canonicalize_hint_pep484_ref` on all remaining parameters.

    Raises
    ------
    exception_cls
        See :func:`.canonicalize_hint_pep484_ref` for further details.
    '''
    assert isinstance(hint_module_name, NoneTypeOr[str]), (
        f'{repr(hint_module_name)} neither string nor "None".')
    assert isinstance(hint_type_name, str), (
        f'{repr(hint_type_name)} not string.')
    assert isinstance(cls_stack, NoneTypeOr[Sequence]), (
        f'{repr(cls_stack)} neither sequence nor "None".')
    assert isinstance(func, NoneTypeOr[Callable]), (
        f'{repr(func)} neither callable nor "None".')
    assert isinstance(exception_cls, type), (
        f'{repr(exception_cls)} not exception type.')
    assert isinstance(exception_prefix, str), (
        f'{repr(exception_prefix)} not string.')

    # If this reference annotates neither...
    if (
        # A method of a class *NOR*...
        not cls_stack and
        # A function...
        func is None
    ):
    # Then this reference does *NOT* annotate a callable. If this reference had
    # annotated a callable, it (almost certainly) would have been
    # canonicalizable against the "__module__" dunder attribute of that
    # callable, whose value is the fully-qualified name of the module declaring
    # that callable. This edge case occurs when this getter is transitively
    # called by a high-level "beartype.door" runtime type-checker (e.g.,
    # is_bearable(), die_if_unbearable()). In this case, raise a readable
    # exception offering pertinent advice.
        raise exception_cls(
            f'{exception_prefix}relative forward reference type hint '
            f'"{hint_type_name}" currently only type-checkable in '
            f'type hints annotating '
            f'@beartype-decorated callables and classes. '
            f'For your own safety and those of the codebases you love, '
            f'consider canonicalizing this '
            f'relative forward reference into an '
            f'absolute forward reference '
            f'(e.g., replace "{hint_type_name}" with '
            f'"{{your_package}}.{{your_submodule}}.{hint_type_name}").'
        )
    # Else, this reference annotates a callable. This reference *SHOULD* have
    # been canonicalizable against the "__module__" dunder attribute of that
    # callable, whose value is the fully-qualified name of the module declaring
    # that callable. Since canonicalization still failed, that value (almost
    # certainly) refers to a non-existent or otherwise unimportable module. This
    # edge case commonly arises when this callable is dynamically synthesized
    # in-memory rather than physically residing in an on-disk module. In this
    # case, raise a readable exception detailing this issue.

    # Exception message to be raised.
    exception_message = (
        f'{exception_prefix}relative forward reference type hint '
        f'"{hint_type_name}" unresolvable relative to'
    )

    # Lower-level exception submessages possibly defined below, to be embedded
    # in this higher-level exception messages.
    exception_submessage_type = ''
    exception_submessage_func = ''

    # If this reference annotates a method of a class...
    if cls_stack:
        # Possibly nested class currently being decorated.
        cls = cls_stack[-1]

        # Fully-qualified name of the module defining this type if that module
        # is importable *OR* "None" otherwise. See relevant commentary in the
        # lower-level canonicalize_hint_pep484_ref_relative_to_type_name() getter.
        hint_module_name_cls = get_object_module_name_or_none(
            obj=cls,
            # See relevant commentary in the lower-level
            # canonicalize_hint_pep484_ref_relative_to_type_name() getter.
            is_module_importable_or_none=True,
        )

        # Set this type-specific submessage to...
        exception_submessage_type = (
            # Substring describing this type, prefixed by whitespace to simplify
            # logic below.
            f' {uppercase_str_char_first(label_type(cls))} '
            # Substring describing this type's module.
            f'{_get_exception_submessage_module_name(hint_module_name_cls)}'
        )
    # Else, this reference does *NOT* annotate a method.

    # If this reference annotates a function...
    if func:
        # Fully-qualified name of the module defining this function if that
        # module is importable *OR* "None" otherwise.
        hint_module_name_func = get_object_module_name_or_none(
            obj=func,
            # See relevant commentary in the lower-level
            # canonicalize_hint_pep484_ref_relative_to_type_name() getter.
            is_module_importable_or_none=True,
        )

        # Set this function-specific submessage to...
        exception_submessage_func = (
            # Substring describing this function, prefixed by whitespace to
            # simplify logic below.
            f' {uppercase_str_char_first(label_callable(func))} '
            # Substring describing this function's module.
            f'{_get_exception_submessage_module_name(hint_module_name_func)}'
        )
    # Else, this reference does *NOT* annotate a function.

    # If both exception submessages were defined above, embed both as ASCII list
    # items prefixed by bullet points for readability. Specifically...
    if exception_submessage_type and exception_submessage_func:
        # Append this message by...
        exception_message += (
            ':'
            f'\n*{exception_submessage_type}'
            f'\n*{exception_submessage_func}'
        )
    # Else, both exception submessages were *NOT* defined above.
    #
    # If only the type-specific submessage is defined, append that.
    elif exception_submessage_type:
        exception_message += exception_submessage_type
    # Else, the type-specific submessage is undefined.
    #
    # If only the function-specific submessage is defined, append that.
    elif exception_submessage_func:
        exception_message += exception_submessage_func
    # Else, the function-specific submessage is undefined. Since this implies
    # *NO* exception submessage to be defined, append a placeholder suffix that
    # admits we have no idea anymore. Guh!
    else:
        exception_message += ' unknown parent module.'

    # Raise this exception.
    raise exception_cls(exception_message)


def _get_exception_submessage_module_name(
    hint_module_name: Optional[str]) -> str:
    '''
    Substring describing the passed possibly undefined module name (if any),
    intended to be embedded in an exception message raised by the caller.

    This low-level utility function is called *only* by the higher-level parent
    :func:`._die_as_ref_uncanonicalizable` function.

    Parameters
    ----------
    hint_module_name : Optional[str]
        Possibly undefined module name to be described.

    Returns
    -------
    str
        Substring as described above.
    '''
    assert isinstance(hint_module_name, NoneTypeOr[str]), (
        f'{repr(hint_module_name)} neither string nor "None".')

    # Return a substring describing this module as either...
    return (
        # If this object defines a "__module__" dunder attribute referring to an
        # importable module, substring describing that module.
        f'in unimportable module "{hint_module_name}".'
        if hint_module_name else
        # Else, this object defines *NO* such attribute. In this case, a
        # substring describing that failure.
        'with undefined or invalid "__module__" attribute.'
    )

# ....................{ PRIVATE ~ finders                  }....................
def _find_ref_relative_on_cls_stack(
    hint_type_name: str,
    is_hint_type_name_qualified: bool,
    cls_stack: TypeStack,
    **kwargs
) -> tuple[Optional[str], str, Optional[type]]:
    '''
    3-tuple ``(hint_module_name, hint_type_name, hint_type)`` describing the
    canonicalization of the passed :pep:`484`-compliant relative forward
    reference relative to the module declaring the passed type stack if this
    reference is the partially-qualified name of a type on this stack *or* the
    3-tuple ``(None, hint_type_name, None)`` otherwise (i.e., if this reference
    is *not* the partially-qualified name of a type on this stack).

    This low-level finder is called by higher-level finders and canonicalizers,
    both of which have a different API they conform to.

    Parameters
    ----------
    hint_type_name : str
        Possibly unqualified classname referred to by this forward reference.
    is_hint_type_name_qualified : bool
        :data:`True` only if this classname contains one or more ``"."``
        delimiters and is thus at least partially qualified already. Note that
        this parameter is an optimization to avoid repeated string searches.
    cls_stack : TypeStack
        Either:

        * If this forward reference annotates a method of a class, the
          corresponding **type stack** (i.e., tuple of the one or more nested
          :func:`beartype.beartype`-decorated classes lexically containing that
          method).
        * Else, :data:`None`.

    All remaining keyword arguments are silently ignored.

    Returns
    -------
    tuple[Optional[str], str, Optional[type]]
        3-tuple ``(hint_module_name, hint_type_name, hint_type)`` such that:

        * If this classname is the partially-qualified name of the currently
          decorated (i.e., most deeply nested) class on the type stack, then:

          * ``hint_module_name`` is the fully-qualified name of the module
            declaring that class.
          * ``hint_type_name`` is the partially qualified name of that class.
          * ``hint_type`` is that class exactly.

        * Else, ``(None, hint_type_name, None)`` where ``hint_type_name`` is the
          passed parameter of the same name.
    '''

    # Possibly undefined fully-qualified name of the module referred to be this
    # relative forward reference.
    hint_module_name: Optional[str] = None

    # Possibly undefined type on this type stack referred to by this reference.
    hint_type: Optional[type] = None

    # If this reference annotates a method of a type...
    if cls_stack:
        # Validate sanity.
        assert isinstance(hint_type_name, str), (
            f'{repr(hint_type_name)} not string.')
        assert isinstance(is_hint_type_name_qualified, bool), (
            f'{repr(is_hint_type_name_qualified)} not boolean.')
        assert isinstance(cls_stack, NoneTypeOr[Sequence]), (
            f'{repr(cls_stack)} neither sequence nor "None".')

        # Number of possibly nested classes currently being decorated by the
        # @beartype decorator.
        cls_stack_len = len(cls_stack)

        # True only if at least two nested classes are currently being decorated
        # by the @beartype decorator.
        is_cls_stack_nested = cls_stack_len >= 2

        # If...
        if (
            # This reference contains one or more "." delimiters and is thus at
            # least partially qualified and thus possibly refers to a nested
            # type *AND*...
            is_hint_type_name_qualified and
            # At least two nested classes are currently being decorated by the
            # @beartype decorator...
            is_cls_stack_nested
        ):
            # List of all unqualified basenames comprising this reference. This
            # list is guaranteed to contain at least two basenames.
            hint_type_names = hint_type_name.split('.')

            # Number of unqualified basenames comprising this reference.
            hint_type_names_len = len(hint_type_names)

            # If the number of unqualified basenames comprising this reference
            # is less than or equal to the number of nested classes currently
            # being decorated by the @beartype decorator, this classname *COULD*
            # be that of such a class. In this case...
            #
            # Note that this test is an optimization gating the *MUCH* slower
            # iterative test performed below.
            if hint_type_names_len <= cls_stack_len:
                # 0-based index of the current unqualified basename comprising
                # this reference being visited by the "while" loop below.
                hint_type_name_index = 0

                # While this index is still valid...
                while hint_type_name_index < hint_type_names_len:
                    # If...
                    if (
                        # The current unqualified basename comprising this
                        # reference is *NOT*...
                        hint_type_names[hint_type_name_index] !=
                        # The current unqualified basename of the corresponding
                        # nested type currently being decorated...
                        cls_stack[hint_type_name_index].__name__
                    ):
                        # Then this reference *CANNOT* refer to this type. In
                        # this case, immediately halt iteration.
                        break
                    # Else, this reference *COULD* possibly refer to this type.
                    # Continue onto the next such pair of strings to decide.

                    # Increment this index.
                    hint_type_name_index += 1
                # If this index is no longer valid, the above "while" loop
                # successfully halted *WITHOUT* the above "break" statement from
                # being performed. In this case, this reference necessarily
                # refers to this type. Thus...
                else:
                    # Type on this type stack referred to by this reference,
                    # defined as the most recent valid index into this type
                    # stack accessed by the above "while" loop. Since that loop
                    # successfully halted and thus incremented this index one
                    # past this desired valid index, decrement this index to
                    # undo that undesirable incrementation. It is what it is.
                    hint_type = cls_stack[hint_type_name_index - 1]
            # Else, the number of unqualified basenames comprising this
            # reference is greater than the number of nested classes currently
            # being decorated by the @beartype decorator. In this case, this
            # classname *CANNOT* be that of such a class.
        # Else, either this reference contains no "." delimiters (and is thus
        # unqualified) *OR* only one non-nested type is currently being
        # decorated by the @beartype decorator.
        #
        # If ...
        elif (
            # This reference is unqualified *AND*...
            not is_hint_type_name_qualified and
            # Only one non-nested type is currently being decorated by the
            # @beartype decorator *AND*...
            not is_cls_stack_nested and
            # This unqualified reference refers to that type...
            hint_type_name == cls_stack[-1].__name__
        ):
            # Note this fact.
            hint_type = cls_stack[-1]
        # Else, either this reference is qualified, two or more nested classes
        # are currently being decorated by the @beartype decorator, *OR* this
        # this unqualified reference does *NOT* refer to the currently decorated
        # type. Regardless, this canonicalizer *CANNOT* canonicalize this
        # reference.

        # If this reference refers to a type on this type stack...
        if hint_type:
            # Fully-qualified name of the module defining this type if this
            # module is importable *OR* "None" otherwise. Since this reducer is
            # *ONLY* passed a type stack when the @beartype decorator is
            # decorating one or more possibly nested classes *AND* since the
            # "__module__" dunder attribute defined by these classes is assumed
            # to be the module defining these classes, that module is assumed to
            # be the currently imported module. Since testing the importability
            # of the currently imported module is *ALWAYS* safe, passing
            # "is_module_importable_or_none=True" is either safe *OR* no less
            # safe in the worst case than not enabling that parameter at all
            # (as, in that case, the "__module__" dunder attribute refers to a
            # non-existent or otherwise unimportable module rather than an
            # existing importable module whose importation would induce a
            # circular import and thus exception from Python itself).
            hint_module_name = get_object_module_name_or_none(
                obj=hint_type, is_module_importable_or_none=True)
        # Else, this reference does *NOT* refer to the currently decorated type.
    # Else, this reference does *NOT* annotate a method of a type. In this
    # case, preserve this module and classname as is.

    # Return this possibly canonicalized module, classname, and class.
    return hint_module_name, hint_type_name, hint_type

# ....................{ PRIVATE ~ canonicalizers : absolute}....................
def _canonicalize_ref_absolute(
    hint_type_name: str,
    is_hint_type_name_qualified: bool,
    **kwargs
) -> _HintCanonicalizerReturn:
    '''
    Possibly undefined fully-qualified module name and possibly unqualified
    classname referred to by the forward reference ``hint`` parameter passed to
    the parent :func:`.canonicalize_hint_pep484_ref` getter, trivially
    canonicalized with low-level string munging ignoring high-level concerns
    like the type stack or callable annotated by this reference.

    Specifically, this canonicalizer splits this reference on the rightmost
    ``"."`` delimiter in this reference and then returns the 2-tuple
    ``(hint_module_name, hint_type_name)`` such that:

    * ``hint_module_name`` is the possibly empty substring preceding that
      delimiter.
    * ``hint_type_name`` is the non-empty substring following that delimiter.

    Parameters
    ----------
    hint_type_name : str
        Possibly unqualified classname referred to by this forward reference.
    is_hint_type_name_qualified : bool
        :data:`True` only if this classname contains one or more ``"."``
        delimiters and is thus at least partially qualified already. Note that
        this parameter is an optimization to avoid repeated string searches.

    All remaining keyword arguments are silently ignored.

    Returns
    -------
    tuple[Optional[str], str]
        2-tuple ``(hint_module_name, hint_type_name)`` where:

        * If the passed ``hint_type_name`` parameter contains one or more
          ``"."`` delimiters:

          * ``hint_module_name`` is the substring preceding the rightmost such
            delimiter.
          * ``hint_type_name`` is the substring following that delimiter.

        * Else, ``(None, hint_type_name)`` where ``hint_type_name`` is the
          passed parameter of the same name as is.
    '''
    assert isinstance(hint_type_name, str), (
        f'{repr(hint_type_name)} not string.')
    assert isinstance(is_hint_type_name_qualified, bool), (
        f'{repr(is_hint_type_name_qualified)} not boolean.')

    # Possibly undefined fully-qualified name of the module referred to be this
    # relative forward reference.
    hint_module_name: Optional[str] = None

    # If this classname contains one or more "." characters and is thus already
    # (...hopefully) fully-qualified as an absolute forward reference...
    if is_hint_type_name_qualified:
        # Possibly empty fully-qualified module name and unqualified basename of
        # the type referred to by this absolute forward reference.
        hint_module_name, _, hint_type_name = hint_type_name.rpartition('.')
    # If this classname contains *NO* "." characters and is thus unqualified as
    # a relative forward reference.

    # Return the 2-tuple of these names.
    return hint_module_name, hint_type_name


def _canonicalize_ref_relative_to_type_owner(
    hint_type_name: str,
    cls_stack: TypeStack,
    **kwargs
) -> TupleStrOrNoneAndStr:
    '''
    Possibly undefined fully-qualified module name and possibly unqualified
    classname referred to by the forward reference ``hint`` parameter passed to
    the parent :func:`.canonicalize_hint_pep484_ref` getter, canonicalized
    relative to the module declaring the currently decorated (i.e., most deeply
    nested) class on the passed type stack *or* preserved as is otherwise.

    Parameters
    ----------
    hint_type_name : str
        Possibly unqualified classname referred to by this forward reference.
    cls_stack : TypeStack
        Either:

        * If this forward reference annotates a method of a class, the
          corresponding **type stack** (i.e., tuple of the one or more nested
          :func:`beartype.beartype`-decorated classes containing that method).
        * Else, :data:`None`.

    All remaining keyword arguments are silently ignored.

    Returns
    -------
    tuple[Optional[str], str, type(None)]
        3-tuple ``(hint_module_name, hint_type_name, None)`` where:

        * ``hint_module_name`` is either:

          * If ``cls_stack`` is not :data:`None`, the module declaring the
            currently decorated (i.e., most deeply nested) class on this stack.
          * Else, :data:`None`.

        * ``hint_type_name`` is the passed parameter of the same name as is.
    '''

    # Possibly undefined fully-qualified name of the module to be returned.
    hint_module_name: Optional[str] = None

    # If this reference annotates a method of a type...
    if cls_stack:
        # Validate sanity.
        assert isinstance(cls_stack, NoneTypeOr[Sequence]), (
            f'{repr(cls_stack)} neither sequence nor "None".')

        # Fully-qualified name of the module defining the currently decorated
        # class, accessible as the most deeply nested type on the type stack.
        hint_module_name = get_object_module_name_or_none(
            cls_stack[-1],
            # See relevant commentary in the lower-level
            # canonicalize_hint_pep484_ref_relative_to_type_name() getter.
            is_module_importable_or_none=True,
        )
    # Else, this reference does *NOT* annotate a method of a type. In this
    # case, preserve this module and classname as is.

    # Return this possibly canonicalized module and classname.
    return hint_module_name, hint_type_name


def _canonicalize_ref_relative_to_func_owner(
    hint_type_name: str,
    func: Optional[Callable],
    **kwargs
) -> TupleStrOrNoneAndStr:
    '''
    Possibly undefined fully-qualified module name and possibly unqualified
    classname referred to by the forward reference ``hint`` parameter passed to
    the parent :func:`.canonicalize_hint_pep484_ref` getter, canonicalized
    relative to the module declaring the passed (presumably currently decorated)
    callable *or* preserved as is otherwise.

    Parameters
    ----------
    hint_type_name : str
        Possibly unqualified classname referred to by this forward reference.
    func : Optional[Callable]
        Either:

        * If this forward reference annotates a callable, that callable.
        * Else, :data:`None`.

    All remaining keyword arguments are silently ignored.

    Returns
    -------
    tuple[Optional[str], str]
        2-tuple ``(hint_module_name, hint_type_name)`` where:

        * ``hint_module_name`` is either:

          * If ``func`` is not :data:`None`, the module declaring that callable.
          * Else, :data:`None`.

        * ``hint_type_name`` is the passed parameter of the same name as is.
    '''

    # Possibly undefined fully-qualified name of the module to be returned.
    hint_module_name: Optional[str] = None

    # If this reference annotates a function...
    if func:
        # Validate sanity.
        assert isinstance(func, NoneTypeOr[Callable]), (
            f'{repr(func)} neither callable nor "None".')

        # Fully-qualified name of the module defining this function.
        hint_module_name = get_object_module_name_or_none(
            obj=func,
            # See relevant commentary in the lower-level
            # canonicalize_hint_pep484_ref_relative_to_type_name() getter.
            is_module_importable_or_none=True,
        )
    # Else, this reference does *NOT* annotate a function. In this case,
    # preserve this module and classname as is.

    # Return this possibly canonicalized module and classname.
    return hint_module_name, hint_type_name


def _canonicalize_ref_relative_to_builtins(
    hint_type_name: str, **kwargs) -> TupleStrOrNoneAndStr:
    '''
    Possibly undefined fully-qualified module name and possibly unqualified
    classname referred to by the forward reference ``hint`` parameter passed to
    the parent :func:`.canonicalize_hint_pep484_ref` getter, canonicalized
    relative to the standard :mod:`builtins` module if this classname is that of
    a builtin type (e.g., :class:`int`) *or* preserved as is otherwise.

    Parameters
    ----------
    hint_type_name : str
        Possibly unqualified classname referred to by this forward reference.

    All remaining keyword arguments are silently ignored.

    Returns
    -------
    tuple[Optional[str], str]
        2-tuple ``(hint_module_name, hint_type_name)`` where:

        * ``hint_module_name`` is either:

          * If if this classname is that of a builtin type, ``"builtins"``.
          * Else, :data:`None`.

        * ``hint_type_name`` is the passed parameter of the same name as is.
    '''
    assert isinstance(hint_type_name, str), (
        f'{repr(hint_type_name)} not string.')

    # Possibly undefined fully-qualified name of the module to be returned.
    hint_module_name: Optional[str] = None

    # If a builtin type with this classname exists, assume this reference refers
    # to this builtin type exposed by the standard "builtins" module.
    if hint_type_name in TYPE_BUILTIN_NAME_TO_TYPE:
        # Fully-qualified name of the standard "builtins" module. Note that this
        # module is *ALWAYS* guaranteed to be importable.
        hint_module_name = BUILTINS_MODULE_NAME
    # Else, this reference does *NOT* refer to a builtin type. In this case,
    # there exists *NO* owner module against which to canonicalize this relative
    # forward reference. In this case, the parent
    # canonicalize_hint_pep484_ref() getter *SHOULD* raise an exception.
    # We need not (and should not) attempt to raise an exception ourselves.

    # Return this possibly canonicalized module and classname.
    return hint_module_name, hint_type_name

# ....................{ PRIVATE ~ globals                  }....................
_HINT_CANONICALIZERS: tuple[_HintCanonicalizer, ...] = (
    # Canonicalize a relative forward reference to the currently decorated
    # possibly nested class first via this efficient class-oriented approach for
    # both efficiency *AND* (more importantly) robustness. If the class
    # currently being decorated by @beartype is a nested class (e.g., type
    # declared inside another type) *AND* the current reference refers to the
    # partially qualified name of that nested class without referring to its
    # parent module (e.g., "OuterType.InnerType" for a nested class "InnerType"
    # declared inside a global class "OuterType"), this canonicalizer correctly
    # preserves the partially qualified name of that nested class as is. Most
    # subsequent canonicalizers erroneously replace and thus destroy that name,
    # requiring this canonicalizer be performed first.
    #
    # This canonicalizer disambiguates between two competing uses of the "."
    # delimiter in forward references:
    # * The "." delimiting nested child types from the parent types nesting
    #   those child types in relative forward references (e.g., the "." in the
    #   relative forward reference "OuterType.InnerType").
    # * The "." delimiting nested child attributes from the (sub)packages and
    #   (sub)modules nesting those child attributes in absolute forward
    #   references (e.g., the "." in the absolute forward reference
    #   "package.submodule.Type").
    #
    # This canonicalizer must thus be performed *BEFORE* the
    # _canonicalize_ref_absolute() canonicalizer, which assumes the "."
    # delimiter in the passed reference to imply that reference to be absolute.
    _find_ref_relative_on_cls_stack,

    # Canonicalize an absolute forward reference with low-level string munging
    # splitting this reference into its constituent module and type names,
    # ignoring high-level concerns like the type stack or callable annotated by
    # this reference. If this canonicalizer succeeds, this reference was in fact
    # an absolute rather than relative forward reference. This canonicalizer
    # disambiguates between these two distinct kinds of references and is thus
    # typically performed earlier than other (but *NOT* all) canonicalizers.
    # Absolute forward references take precedence over relative forward
    # references, requiring this canonicalizer be performed *BEFORE* all
    # remaining canonicalizers that assume the passed reference to be relative.
    _canonicalize_ref_absolute,

    # Canonicalize a relative forward reference relative to the fully-qualified
    # name of the module defining the currently decorated possibly nested class.
    # Resolving a relative forward reference against the *TYPE* annotated by
    # that reference takes precedence over resolving a relative forward
    # reference against the *CALLABLE* annotated by that reference, requiring
    # this canonicalizer (which performs the former) be performed *BEFORE* the
    # _canonicalize_ref_relative_to_func_owner() canonicalizer (which performs
    # the latter). See also the "Caveats" section of the docstring of the
    # canonicalize_hint_pep484_ref() getter, which details why types are
    # preferable to callables when resolving relative forward references.
    _canonicalize_ref_relative_to_type_owner,

    # Canonicalize a relative forward reference relative to the fully-qualified
    # name of the module defining the currently decorated callable. Resolving a
    # relative forward reference against *ANY* owner object annotated by that
    # reference takes precedence over resolving a relative forward reference to
    # a builtin type against the standard "builtins" module, requiring this
    # canonicalizer (which performs the former) be performed *BEFORE* the
    # _canonicalize_ref_relative_to_builtins() canonicalizer (which performs the
    # latter).
    _canonicalize_ref_relative_to_func_owner,

    # Canonicalize a relative forward reference to a builtin type (e.g., "int")
    # relative to the fully-qualified name of the standard "builtins" module.
    # This is a last-ditch desperate fallback and thus performed dead last.
    _canonicalize_ref_relative_to_builtins,
)
'''
Tuple of all **canonicalizers** (i.e., callables in the
``_canonicalize_hint_pep484_ref_*()`` family of private getters called to
canonicalize :pep:`484`-compliant relative forward references), ordered in
descending order of importance to ensure that iteration internally performed by
the parent :func:`.canonicalize_hint_pep484_ref` getter iteratively calls
the most important of these canonicalizers first.
'''


_HINT_CANONICALIZER_INDEX_MAX = len(_HINT_CANONICALIZERS)
'''
0-based index of the last **canonicalizer** (i.e., callable in the
``_canonicalize_hint_pep484_ref_*()`` family of private getters called to
canonicalize :pep:`484`-compliant relative forward references).
'''
