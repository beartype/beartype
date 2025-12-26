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

# ....................{ IMPORTS                            }....................
from beartype.roar import BeartypeDecorHintForwardRefException
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
from beartype._util.module.utilmodget import get_object_module_name_or_none
from beartype._util.module.utilmodtest import is_module
from beartype._util.text.utiltextlabel import label_callable
from collections.abc import (
    Callable,
    Sequence,
)
from typing import Optional

# ....................{ GETTERS                            }....................
#FIXME: Resolve *ALL* unit tests marked 'Currently broken.' *sigh*
def get_hint_pep484_ref_names_absolute(
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
          corresponding **type stack** (i.e., tuple of the one or more nested
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
        * ``hint_type_name`` is the unqualified classname referred to by this forward
          reference.

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
    #    >>> module_name is None or (
    #    ...     isinstance(module_name, str) and
    #    ...     len(module_name)
    #    ... )
    #    True
    #    >>> isinstance(hint_ref_name, str) and len(hint_ref_name)
    #    True
    hint_module_name, hint_type_name = get_hint_pep484_ref_names_relative(
        hint=hint,
        exception_cls=exception_cls,
        exception_prefix=exception_prefix,
    )

    #FIXME: Comment us up, please.
    hint_module_name_origin: object = None

    # True only if this classname contains one or more "." characters and is
    # thus already (...hopefully) fully-qualified.
    is_hint_type_name_qualified = '.' in hint_type_name

    # ....................{ HEURISTIC ~ nested class       }....................
    # If...
    if (
        # This reference was *NOT* instantiated with a module name (i.e., this
        # reference is relative to some module whose name has yet to be decided)
        # *AND*...
        not hint_module_name and
        # This reference annotates a method of a class...
        cls_stack
    # Then...
    #
    # Note that this ad-hoc heuristic preferentially canonicalizes relative
    # references via this efficient class-oriented approach for both
    # efficiency *AND* (more importantly) robustness. If the class currently
    # being decorated by @beartype is a nested class (e.g., a type declared
    # inside another type) *AND* this is a stringified relative forward
    # reference whose value is the partially qualified name of that nested
    # class *WITHOUT* reference to that module (e.g., "OuterType.InnerType"
    # for a nested class "InnerType" declared inside a global class
    # "OuterType"), this approach correctly preserves the partially
    # qualified name of that nested class as is. Most subsequent approaches
    # erroneously replace and thus destroy that name, necessitating that
    # this approach be performed first *BEFORE* those other approaches.
    ):
        # Possibly nested class currently being decorated by @beartype.
        cls = cls_stack[-1]

        # If this classname contains one or more "." characters...
        if is_hint_type_name_qualified:
            hint_type_names = hint_type_name.split('.')

            #FIXME: Comment us up, please. *sigh*
            if len(hint_type_names) == len(cls_stack):
                #FIXME: Inefficient, but who cares at the moment. Perform
                #manual iteration when we feel like optimizing this. *sigh*
                #FIXME: Comment us up, please. *sigh*
                type_nested_names = list(
                    type_nested.__name__ for type_nested in cls_stack)

                #FIXME: Comment us up, please. *sigh*
                if hint_type_names == type_nested_names:
                    # Fully-qualified name of the module defining this type.
                    hint_module_name = get_object_module_name_or_none(cls)

                    #FIXME: Comment us up, please. *sigh*
                    hint_module_name_origin = cls_stack
        #FIXME: Comment us up, please. *sigh*
        elif hint_type_name == cls.__name__:
            # Fully-qualified name of the module defining this class.
            hint_module_name = get_object_module_name_or_none(cls)

            #FIXME: Comment us up, please. *sigh*
            hint_module_name_origin = cls_stack
        #FIXME: Comment us up, please. *sigh*
    # Else, this reference was already instantiated with a module name *AND* ...
    #FIXME: Comment us up, please. *sigh*

    # ....................{ HEURISTIC ~ absolute reference }....................
    # If...
    if (
        # The fully-qualified name of the module defining the attribute to which
        # this reference refers still has yet to be decided *AND*...
        not hint_module_name and
        # This classname contains one or more "." characters and is thus already
        # (...hopefully) fully-qualified...
        is_hint_type_name_qualified
    ):
        # Possibly empty fully-qualified module name and unqualified
        # basename of the type referred to by this reference.
        hint_module_name, _, hint_type_name = hint_type_name.rpartition('.')
    # Else, either ... *OR* this classname contains *NO* "." characters.
    #FIXME: Comment us up, please. *sigh*

    # ....................{ HEURISTIC ~ relative reference }....................
    # If the fully-qualified name of the module defining the attribute to which
    # this reference refers still has yet to be decided...
    if not hint_module_name:
        #FIXME: Improve commentary, please. Notably, note why classes *MUST* be
        #prioritized over callables. See the docstring with respect to
        #"typing.NamedTuple". *sigh*
        if cls_stack:
            # Fully-qualified name of the module defining this class.
            hint_module_name = get_object_module_name_or_none(cls_stack[-1])

            #FIXME: Comment us up, please. *sigh*
            hint_module_name_origin = cls_stack
        #FIXME: Comment us up, please. *sigh*
        #
        # If this reference annotates a function...
        elif func:
            # Fully-qualified name of the module defining this function.
            hint_module_name = get_object_module_name_or_none(func)

            #FIXME: Comment us up, please. *sigh*
            hint_module_name_origin = func
        # Else, this reference does *NOT* annotate a function.
        #
        # If a builtin type with this classname exists, assume this reference
        # refers to this builtin type exposed by the standard "builtins" module.
        elif hint_type_name in TYPE_BUILTIN_NAME_TO_TYPE:
            # Fully-qualified name of the standard "builtins" module. Note that
            # this module is *ALWAYS* guaranteed to be importable.
            hint_module_name = BUILTINS_MODULE_NAME
        # Else, this reference does *NOT* refer to a builtin type. In this case,
        # there exists *NO* owner module against which to canonicalize this
        # relative reference. This edge case occurs when this getter is
        # transitively called by a high-level "beartype.door" runtime
        # type-checker (e.g., is_bearable(), die_if_unbearable()). In this case,
        # raise an exception.
        else:
            raise exception_cls(
                f'{exception_prefix}type hint relative forward reference '
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
    #FIXME: Comment us up, please. *sigh*

    # ....................{ HEURISTIC ~ malicious object   }....................
    #FIXME: Document why this rare edge case occurs. Notably, either:
    #* Malicious classes (whose __module__ attributes are either "None",
    #  the empty string, or an unimportable module).
    #* Malicious forward references (whose "."-delimited prefix is an
    #  unimportable module).

    # If it is still *NOT* the case that...
    #
    # Note that this edge case rarely arises. Efficiency is *NOT* a concern.
    if not (
        # The fully-qualified name of the module defining the attribute to which
        # this reference refers is known *AND*...
        hint_module_name and
        #FIXME: Comment us up, please. Basically, calling is_module() is
        #dangerous at this early decoration time. We only do so if we can do so
        #safely, which is when this module name ideally refers to the module
        #currently being imported. *sigh*
        #FIXME: Also, DRY violation between here and below. Probably best just
        #to inject a "!!! CAVEATS: Synchronize... !!!" banner here. *shrug*
        # That module is importable *AND*...
        (not hint_module_name_origin or is_module(hint_module_name))
    # Then fallback to...
    ):
        #FIXME: Improve commentary, please. Notably, note why classes *MUST* be
        #prioritized over callables. See the docstring with respect to
        #"typing.NamedTuple". *sigh*
        #FIXME: Duplicates logic above. Whatevahs!
        #FIXME: This is some pretty ad-hoc logic. Tests pass, but... *YIKES*.

        # If a builtin type with this classname exists, assume this reference
        # refers to this builtin type exposed by the standard "builtins" module.
        if hint_type_name in TYPE_BUILTIN_NAME_TO_TYPE:
            # Fully-qualified name of the standard "builtins" module. Note that
            # this module is *ALWAYS* guaranteed to be importable.
            hint_module_name = BUILTINS_MODULE_NAME
        elif cls_stack and hint_module_name_origin is not cls_stack:
            # Fully-qualified name of the module defining this class.
            hint_module_name = get_object_module_name_or_none(cls_stack[-1])
        # If this reference annotates a callable, then fallback to...
        elif func and hint_module_name_origin is not func:
            # Fully-qualified name of the module defining this callable.
            hint_module_name = get_object_module_name_or_none(func)
        # Else, this reference does *NOT* annotate a callable.

        # If it is still *NOT* the case that...
        if not (
            # The fully-qualified name of the module defining the attribute to
            # which this reference refers is known *AND*...
            hint_module_name and
            # That module is importable *AND*...
            (not hint_module_name_origin or is_module(hint_module_name))
        # There exists *NO* usable module from which to import the attribute to
        # which this reference refers. In this case, raise an exception.
        ):
            # Exception message to be raised.
            exception_message = (
                f'{exception_prefix}type hint relative forward reference '
                f'"{hint_type_name}" unresolvable relative to'
            )

            # If this reference annotates a method of a class...
            if cls_stack:
                # Fully-qualified name of the module defining that class.
                cls_module_name = get_object_module_name_or_none(cls)  # pyright: ignore

                # Append this message by...
                exception_message += (
                    # Substring describing this class *AND*...
                    f':\n* {repr(cls)} ' +  # pyright: ignore
                    (
                        # If that class defines a "__module__" dunder attribute,
                        # substring describing that module.
                        f'in unimportable module "{cls_module_name}".'
                        if cls_module_name else
                        # Else, that class defines *NO* such attribute. In this
                        # case, a substring describing that failure.
                        'with undefined "__module__" attribute.'
                    ) +
                    # Substring suffixing this item and prefixing the next item.
                    '\n* '
                )
            # Else, this reference annotates a global or local function. In this
            # case, append a substring prefixing the next item.
            else:
                exception_message += ' '

            # Append this message by an appropriate substring defined as the dynamic
            # concatenation of...
            exception_message += (
                # Substring describing this callable if callable is actually
                # callable or falling back to its representation otherwise *AND*...
                (
                    f'{label_callable(func)} '
                    if callable(func) else
                    f'{repr(func)} '
                ) +
                # Substring describing this module.
                (
                    f'in unimportable module "{hint_module_name}".'
                    if hint_module_name else
                    'with undefined "__module__" attribute.'
                )
            )

            # Raise this exception.
            raise exception_cls(exception_message)
    # Else, there exists a usable module from which to import the attribute to
    # which this reference refers.

    # Guarantee sanity for caller convenience.
    assert hint_module_name, f'Forward reference "{hint}" module unparseable.'
    assert hint_type_name, f'Forward reference "{hint}" attribute unparseable.'

    # Return metadata describing this forward reference relative to this module.
    return hint_module_name, hint_type_name

# ....................{ GETTERS                            }....................
#FIXME: Resolve *ALL* unit tests marked 'Currently broken.' *sigh*
#FIXME: Add additional unit tests to test all edge case implied by the new
#_get_hint_pep484_ref_names_absolute_type_nested() canonicalizer, please.
#FIXME: Rename to get_hint_pep484_ref_names_absolute() once working, please.
#FIXME: Consider shifting this into a new submodule, please. Perhaps a new
#structure resembling the following would be warranted:
#* A new "beartype._util.hint.pep.proposal.pep484.forward" subpackage defining:
#  * A new "pep484refrelative" submodule. All public functions *EXCEPT* this
#    public function should be shifted there.
#  * A new "pep484refabsolute" submodule. Only this public function and all
#    private attributes required thereby should be shifted there.
def get_hint_pep484_ref_names_absolute_new(
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
        * ``hint_type_name`` is the unqualified classname referred to by this forward
          reference.

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
    # hint_relative = get_hint_pep484_ref_names_relative(
    hint_module_name, hint_type_name = get_hint_pep484_ref_names_relative(
        hint=hint,
        exception_cls=exception_cls,
        exception_prefix=exception_prefix,
    )

    # 0-based index of the current canonicalizer (i.e., private getter in the
    # _get_hint_pep484_ref_names_absolute_*() family of private getters
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

        #FIXME: *GIATONS OF EDGE CASES HERE.* Are we actually unit-testing any
        #of this at the moment? Uhh. No idea, honestly. *lolz but sad*
        # If this index exceeds that of the last available canonicalizer, no
        # canonicalizer successfully canonicalized this relative forward
        # reference. In this case.
        if hint_canonicalizer_index >= _HINT_CANONICALIZER_INDEX_MAX:
            # If this reference annotates neither...
            if (
                # A method of a class *NOR*...
                not cls_stack and
                # A function...
                func is None
            ):
            # This reference does *NOT* annotate a callable. If this reference
            # had annotated a callable, it (almost certainly) would have been
            # canonicalizable against the "__module__" dunder attribute of that
            # callable, whose value is the fully-qualified name of the module
            # declaring that callable. This edge case occurs when this getter is
            # transitively called by a high-level "beartype.door" runtime
            # type-checker (e.g., is_bearable(), die_if_unbearable()). In this
            # case, raise a readable exception offering pertinent advice.
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
            # Else, this reference annotates a callable. This reference *SHOULD*
            # have been canonicalizable against the "__module__" dunder
            # attribute of that callable, whose value is the fully-qualified
            # name of the module declaring that callable. Since canonicalization
            # still failed, that value (almost certainly) refers to a
            # non-existent or otherwise unimportable module. This edge case
            # commonly arises when this callable is dynamically synthesized
            # in-memory rather than physically residing in an on-disk module. In
            # this case, raise a readable exception detailing this issue.
            else:
                # Exception message to be raised.
                exception_message = (
                    f'{exception_prefix}relative forward reference type hint '
                    f'"{hint_type_name}" unresolvable relative to'
                )

                # Lower-level exception submessages possibly defined below, to
                # be embedded in this higher-level exception messages.
                exception_submessage_type = ''
                exception_submessage_func = ''

                # If this reference annotates a method of a class...
                if cls_stack:
                    # Possibly nested class currently being decorated.
                    cls = cls_stack[-1]

                    # Fully-qualified name of the module defining this type if
                    # that module is importable *OR* "None" otherwise. See
                    # relevant commentary in the lower-level
                    # get_hint_pep484_ref_names_absolute_type_nested() getter.
                    hint_module_name_cls = get_object_module_name_or_none(
                        obj=cls, is_module_importable_or_none=True)

                    # Set this type-specific submessage to...
                    exception_submessage_type = (
                        # Substring describing this type *AND*...
                        f'{repr(cls)} ' +

                        #FIXME: DRY violation here between this and the
                        #subsequent "if" conditional. Ignorable stuff for now!
                        # Substring describing this type's module as either...
                        (
                            # If this type defines a "__module__" dunder
                            # attribute referring to an importable module,
                            # substring describing that module.
                            f'in unimportable module "{hint_module_name_cls}".'
                            if hint_module_name_cls else
                            # Else, this type defines *NO* such attribute. In
                            # this case, a substring describing that failure.
                            'with undefined or invalid "__module__" attribute.'
                        )
                    )
                # Else, this reference does *NOT* annotate a method.

                # If this reference annotates a function...
                if func:
                    # Fully-qualified name of the module defining this function
                    # if that module is importable *OR* "None" otherwise. See
                    # relevant commentary in the lower-level
                    # get_hint_pep484_ref_names_absolute_type_nested() getter.
                    hint_module_name_func = get_object_module_name_or_none(
                        obj=func, is_module_importable_or_none=True)

                    # Set this function-specific submessage to...
                    exception_submessage_func = (
                        # Substring describing this function if this function is
                        # actually function or falling back to its
                        # representation otherwise *AND*...
                        (
                            f'{label_callable(func)} '
                            if callable(func) else
                            f'{repr(func)} '
                        ) +
                        # Substring describing this function's module as
                        # either...
                        (
                            # If this function defines a "__module__" dunder
                            # attribute referring to an importable module,
                            # substring describing that module.
                            f'in unimportable module "{hint_module_name_func}".'
                            if hint_module_name_func else
                            # Else, this type defines *NO* such attribute. In
                            # this case, a substring describing that failure.
                            'with undefined or invalid "__module__" attribute.'
                        )
                    )

                # If both exception submessages were defined above, embed both
                # as ASCII list items prefixed by bullet points for readability.
                # Specifically...
                if exception_submessage_type and exception_submessage_func:
                    # Append this message by...
                    exception_message += (
                        ':'
                        f'\n* {exception_submessage_type}'
                        f'\n* {exception_submessage_func}'
                    )
                # Else, both exception submessages were *NOT* defined above.
                #
                # If only the type-specific submessage is defined, append that.
                elif exception_submessage_type:
                    exception_message += f' {exception_submessage_type}'
                # Else, the type-specific submessage is undefined.
                #
                # If only the function-specific submessage is defined, append
                # that.
                elif exception_submessage_func:
                    exception_message += f' {exception_submessage_func}'
                # Else, the function-specific submessage is undefined. Since
                # this implies *NO* exception submessage to be defined, append a
                # placeholder suffix that admits we have no idea anymore. Guh!
                else:
                    exception_message += ' unknown parent module.'

                # Raise this exception.
                raise exception_cls(exception_message)
        # Else, this index corresponds to that of an available canonicalizer.

        # Current canonicalizer.
        hint_canonicalizer = _HINT_CANONICALIZERS[hint_canonicalizer_index]

        # Either:
        # * If this canonicalizer successfully canonicalized this relative
        #   forward reference, the fully-qualified module name and qualified
        #   classname referred to by this reference.
        # * Else, the currently undefined module name and possibly unqualified
        #   classname preserved as is.
        hint_module_name, hint_type_name = hint_canonicalizer(
            hint_type_name=hint_type_name,
            is_hint_type_name_qualified=is_hint_type_name_qualified,
            cls_stack=cls_stack,
            func=func,
            exception_cls=exception_cls,
            exception_prefix=exception_prefix,
        )

    # Return the 2-tuple of these names.
    return hint_module_name, hint_type_name

# ....................{ GETTERS ~ cls_stack                }....................
#FIXME: Unit test us up, please. *sigh*
def get_hint_pep484_ref_names_absolute_type_nested(
    # Mandatory parameters.
    hint_type_name: str,
    cls_stack: TypeStack,

    # Optional parameters.
    is_hint_type_name_qualified: Optional[bool] = None,
    **kwargs
) -> TupleStrOrNoneAndStr:
    '''
    Possibly undefined fully-qualified module name and possibly unqualified
    classname referred to by the forward reference ``hint`` parameter passed to
    the parent :func:`.get_hint_pep484_ref_names_absolute` getter, canonicalized
    relative to the module declaring the passed type stack if this classname is
    the partially-qualified name of the currently decorated (i.e., most deeply
    nested) class on the type stack *or* preserved as is otherwise.

    Parameters
    ----------
    hint_type_name : str
        Possibly unqualified classname referred to by that forward reference.
    cls_stack : TypeStack
        Either:

        * If this forward reference annotates a method of a class, the
          corresponding **type stack** (i.e., tuple of the one or more nested
          :func:`beartype.beartype`-decorated classes lexically containing that
          method).
        * Else, :data:`None`.
    is_hint_type_name_qualified : Optional[bool], default: None
        :data:`True` only if this classname contains one or more ``"."``
        delimiters and is thus at least partially qualified already. Note that
        this parameter is an optimization to avoid repeated string searches.
        Defaults to :data:`None`, in which case this getter falls back to
        deciding this boolean in the trivial way.

    All remaining keyword arguments are silently ignored.

    Returns
    -------
    tuple[Optional[str], str]
        2-tuple ``(hint_module_name, hint_type_name)`` such that:

        * If this classname is the partially-qualified name of the currently
          decorated (i.e., most deeply nested) class on the type stack, then:

          * ``hint_module_name`` is the fully-qualified name of the module
            declaring that class.
          * ``hint_type_name`` is the partially qualified name of that class.

        * Else, ``(None, hint_type_name)`` where ``hint_type_name`` is the
          passed parameter of the same name.
    '''
    assert isinstance(is_hint_type_name_qualified, NoneTypeOr[bool]), (
        f'{repr(is_hint_type_name_qualified)} neither boolean nor "None".')
    assert isinstance(cls_stack, NoneTypeOr[Sequence]), (
        f'{repr(cls_stack)} neither sequence nor "None".')

    # Possibly undefined fully-qualified name of the module referred to be this
    # relative forward reference.
    hint_module_name: Optional[str] = None

    # If this reference annotates a method of a type...
    if cls_stack:
        # Number of possibly nested classes currently being decorated by the
        # @beartype decorator.
        cls_stack_len = len(cls_stack)

        # True only if at least two nested classes are currently being decorated
        # by the @beartype decorator.
        is_cls_stack_nested = cls_stack_len >= 2

        # True only if this reference refers to the currently decorated (i.e.,
        # most deeply nested) type currently being decorated by @beartype,
        # defaulting to false for safety.
        is_hint_self = False

        # If the caller failed to pass this boolean, default this boolean to a
        # string test in the trivial manner.
        if is_hint_type_name_qualified is None:
            is_hint_type_name_qualified = '.' in hint_type_name
        # Else, the caller passed this boolean. Preserve this boolean as is.

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
            # is the number of nested classes currently being decorated by the
            # @beartype decorator, this classname *COULD* be that of the
            # currently decorated (i.e., most deeply nested) such type. In this
            # case...
            #
            # Note that this test is an optimization gating the *MUCH* slower
            # iterative test performed below.
            if len(hint_type_names) == cls_stack_len:
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
                # refers to this type. Note this fact.
                else:
                    is_hint_self = True
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
            is_hint_self = True
        # Else, either this reference is qualified, two or more nested classes
        # are currently being decorated by the @beartype decorator, *OR* this
        # this unqualified reference does *NOT* refer to the currently decorated
        # type. Regardless, this canonicalizer *CANNOT* canonicalize this
        # reference.

        # If this reference refers to the currently decorated type...
        if is_hint_self:
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
                obj=cls_stack[-1], is_module_importable_or_none=True)
        # Else, this reference does *NOT* refer to the currently decorated type.
    # Else, this reference does *NOT* annotate a method of a type. In this
    # case, preserve this module and classname as is.

    # Return this possibly canonicalized module and classname.
    return hint_module_name, hint_type_name

# ....................{ PRIVATE ~ getters                  }....................
def _get_hint_pep484_ref_names_absolute_str(
    hint_type_name: str, **kwargs) -> TupleStrOrNoneAndStr:
    '''
    Possibly undefined fully-qualified module name and possibly unqualified
    classname referred to by the forward reference ``hint`` parameter passed to
    the parent :func:`.get_hint_pep484_ref_names_absolute` getter, trivially
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
        Possibly unqualified classname referred to by that forward reference.

    All remaining keyword arguments are silently ignored.

    Returns
    -------
    tuple[Optional[str], str]
        2-tuple ``(hint_module_name, hint_type_name)`` as detailed above.
    '''

    # Possibly empty fully-qualified module name and unqualified basename of the
    # type referred to by this reference.
    hint_module_name, _, hint_type_name = hint_type_name.rpartition('.')

    # Return the 2-tuple of these names.
    return hint_module_name, hint_type_name


def _get_hint_pep484_ref_names_absolute_type_current(
    hint_type_name: str,
    cls_stack: TypeStack,
    **kwargs
) -> TupleStrOrNoneAndStr:
    '''
    Possibly undefined fully-qualified module name and possibly unqualified
    classname referred to by the forward reference ``hint`` parameter passed to
    the parent :func:`.get_hint_pep484_ref_names_absolute` getter, canonicalized
    relative to the module declaring the currently decorated (i.e., most deeply
    nested) class on the type stack *or* preserved as is otherwise.

    Parameters
    ----------
    hint_type_name : str
        Possibly unqualified classname referred to by that forward reference.
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
    tuple[Optional[str], str]
        2-tuple ``(hint_module_name, hint_type_name)`` where:

        * ``hint_module_name`` is either:

          * If ``cls_stack`` is not :data:`None`, the module declaring the
            currently decorated (i.e., most deeply nested) class on this stack.
          * Else, :data:`None`.

        * ``hint_type_name`` is the passed parameter of the same name as is.
    '''
    assert isinstance(cls_stack, NoneTypeOr[Sequence]), (
        f'{repr(cls_stack)} neither sequence nor "None".')

    # Possibly undefined fully-qualified name of the module to be returned.
    hint_module_name: Optional[str] = None

    # If this reference annotates a method of a type...
    if cls_stack:
        # Fully-qualified name of the module defining the currently decorated
        # class, accessible as the most deeply nested type on the type stack.
        hint_module_name = get_object_module_name_or_none(cls_stack[-1])
    # Else, this reference does *NOT* annotate a method of a type. In this
    # case, preserve this module and classname as is.

    # Return this possibly canonicalized module and classname.
    return hint_module_name, hint_type_name

# ....................{ PRIVATE ~ hints                    }....................
_HintCanonicalizer = Callable[..., TupleStrOrNoneAndStr]
'''
:pep:`585`-compliant type hint matching a **canonicalizer** (i.e., callable in
the ``_get_hint_pep484_ref_names_absolute_*()`` family of private getters called
to canonicalize :pep:`484`-compliant relative forward references).
'''

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
    # necessitating that this canonicalizer be performed first.
    get_hint_pep484_ref_names_absolute_type_nested,

    # Canonicalize an absolute forward reference with low-level string munging
    # splitting this reference into its constituent module and type names,
    # ignoring high-level concerns like the type stack or callable annotated by
    # this reference. If this canonicalizer succeeds, this reference was in fact
    # an absolute rather than relative forward reference. This canonicalizer
    # disambiguates between these two distinct kinds of references and is thus
    # typically performed earlier than other (but *NOT* all) canonicalizers.
    # Absolute forward references take precedence over relative forward
    # references, necessitating that this canonicalizer be performed *BEFORE*
    # all remaining canonicalizers unique to relative forward references.
    _get_hint_pep484_ref_names_absolute_str,

    # Canonicalize a relative forward reference relative to the fully-qualified
    # name of the module defining the currently decorated possibly nested class.
    _get_hint_pep484_ref_names_absolute_type_current,
)
'''
Tuple of all **canonicalizers** (i.e., callables in the
``_get_hint_pep484_ref_names_absolute_*()`` family of private getters called to
canonicalize :pep:`484`-compliant relative forward references), ordered in
descending order of importance to ensure that iteration internally performed by
the parent :func:`.get_hint_pep484_ref_names_absolute` getter iteratively calls
the most important of these canonicalizers first.
'''


_HINT_CANONICALIZER_INDEX_MAX = len(_HINT_CANONICALIZERS)
'''
0-based index of the last **canonicalizer** (i.e., callable in the
``_get_hint_pep484_ref_names_absolute_*()`` family of private getters called to
canonicalize :pep:`484`-compliant relative forward references).
'''
