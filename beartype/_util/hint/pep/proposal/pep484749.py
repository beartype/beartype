#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`484`- and :pep:`749`-compliant **forward reference type hint
utilities** (i.e., low-level callables introspecting forward references in a
general-purpose manner without regard for the types of those references).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.roar import (
    BeartypeCallHintPep749ForwardRefObjectException,
    BeartypeDecorHintForwardRefException,
)
from beartype._cave._cavefast import (
    HintPep484749RefObjectType,
    HintPep484749RefTypes,
)
from beartype._data.typing.datatyping import (
    HintPep484749Ref,
    TupleStrOrNoneAndStr,
    TypeException,
)
from beartype._data.typing.datatypingport import Hint
from beartype._util.module.utilmodget import get_object_module_name_or_none
from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_14
from beartype._util.text.utiltextlabel import label_exception_traceback
from typing import Optional

# ....................{ RAISERS                            }....................
#FIXME: Validate that this forward reference string is *NOT* the empty string.
#FIXME: Validate that this forward reference string is a syntactically valid
#"."-delimited concatenation of Python identifiers. We already have logic
#performing that validation somewhere, so let's reuse that here, please.
#Right. So, we already have an is_identifier() tester; now, we just need to
#define a new die_unless_identifier() validator.
def die_unless_hint_pep484749_ref(
    # Mandatory parameters.
    hint: HintPep484749Ref,

    # Optional parameters.
    exception_cls: TypeException = BeartypeDecorHintForwardRefException,
    exception_prefix: str = '',
) -> None:
    '''
    Raise an exception unless the passed object is a :pep:`484`-compliant
    **forward reference hint** (i.e., object referring to a user-defined type
    that typically has yet to be defined).

    Equivalently, this validator raises an exception if this object is neither:

    * A string whose value is the syntactically valid name of a class.
    * An instance of the :class:`typing.ForwardRef` class. The :mod:`typing`
      module implicitly replaces all strings subscripting :mod:`typing` objects
      (e.g., the ``MuhType`` in ``List['MuhType']``) with
      :class:`typing.ForwardRef` instances containing those strings as instance
      variables, for nebulous reasons that make little justifiable sense but
      what you gonna do 'cause this is 2020. *Fight me.*

    Parameters
    ----------
    hint : HintPep484749Ref
        Object to be validated.
    exception_cls : Type[Exception], default: BeartypeDecorHintForwardRefException
        Type of exception to be raised in the event of a fatal error. Defaults
        to :exc:`.BeartypeDecorHintForwardRefException`.
    exception_prefix : str, default: ''
        Human-readable substring prefixing raised exception messages. Defaults
        to the empty string.

    Raises
    ------
    exception_cls
        If this object is *not* a forward reference type hint.
    '''

    # If this object is *NOT* a forward reference type hint, raise an exception.
    if not isinstance(hint, HintPep484749RefTypes):
        assert isinstance(exception_cls, type), (
            f'{repr(exception_cls)} not exception subclass.')
        assert isinstance(exception_prefix, str), (
            f'{repr(exception_prefix)} not string.')

        raise exception_cls(
            f'{exception_prefix}type hint {repr(hint)} not forward reference '
            f'(i.e., neither string nor "typing.ForwardRef" object).'
        )
    # Else, this object is a forward reference type hint.

# ....................{ TESTERS                            }....................
#FIXME: Unit test us up, please!
def is_hint_pep484749_ref_object_resolvable(
    hint: HintPep484749RefObjectType) -> bool:
    '''
    :data:`True` only if the passed :pep:`749`-compliant **object-oriented
    forward reference type hint** (i.e., :class:`annotationlib.ForwardRef`
    object encapsulating all metadata required to dynamically resolve at runtime
    a reference to a referent target type hint that typically has yet to be
    defined in the current lexical scope) is dynamically resolvable at runtime
    (i.e., actually does encapsulate all such requisite metadata).

    This reference may be safely passed to the corresponding
    :func:`.resolve_hint_pep484749_ref_object` resolver *if and only if* this
    tester returns :data:`True`. Callers should thus gate calls to that resolver
    in ``if`` conditionals first calling this tester. Why? Because only a subset
    of object-oriented forward references are safely resolvable at runtime.
    Almost all parameters (and thus requisite metadata) accepted by the
    :meth:`annotationlib.ForwardRef.__init__` and
    :meth:`typing.ForwardRef.__init__` constructors are optional. Moreover,
    those parameters default to unhelpful default values (e.g., :data:`None`).
    Object-oriented forward reference type hints are thus *not* guaranteed to be
    dynamically resolvable at runtime to their referent target type hints.

    This tester returns :data:`True` for the proper subset of
    :class:`annotationlib.ForwardRef` objects whose
    :meth:`annotationlib.ForwardRef.evaluate` methods raise *no* unexpected
    exceptions. All other :class:`annotationlib.ForwardRef` objects are unusable
    for runtime resolution purposes. What constitutes "the proper subset of
    :class:`annotationlib.ForwardRef` objects whose
    :meth:`annotationlib.ForwardRef.evaluate` methods raise *no* unexpected
    exceptions" can be reverse-engineered by inspection from the body of that
    method. Specifically, if the passed reference defines *all* of the following
    dunder attributes to be non-empty strings, this reference can be safely
    resolved by calling its :meth:`annotationlib.ForwardRef.evaluate`:

    * The private :attr:`annotationlib.ForwardRef.__owner__`` dunder attribute.
      Although technically private, this dunder is nonetheless stable across at
      least Python 3.14 and 3.15. More importantly, this dunder suffices to
      resolve resolve references to referents externally defined as either:

      * **Globals** if that owner is either a callable or type.
      * **Locals** or **type parameters** if that owner is a type.

      For simplicity, this tester currently assumes any non-:data:`None` owner
      to be either a callable or type and thus suffice to resolve references to
      referents externally defined as at least globals (i.e., the common case).

    Equivalently, this tester returns :data:`True` for *all*
    :class:`annotationlib.ForwardRef` objects implicitly generated by
    :pep:`749`-compliant ``__annotate__()`` dunder methods defined on both
    pure-Python callables and types under Python >= 3.14. Under at least Python
    3.14 and 3.15, this implicit generation is currently backed by an override
    of the private :meth:`annotationlib._StringifierDict.__missing__` dictionary
    method. By trivial inspection, that method's implementation passes the
    optional ``owner`` but *not* ``module`` parameter.

    Luckily, the standard :mod:`annotationlib` module itself implicitly passes a
    non-:data:`None` value as the ``owner`` parameter for the common case of the
    public :func:`annotationlib.get_annotations` getter. That high-level public
    getter internally calls the low-level private
    :func:`annotationlib._get_and_call_annotate` getter, which passes the same
    **annotatable object** (i.e., module, type, or callable defining the
    ``__annotate__`` dunder method) as the ``owner`` parameter.

    Unluckily, the standard :mod:`annotationlib` module does *not* implicitly
    pass a similar default for the ``owner`` parameter under any other use case.
    Instead, callers must do so by manually passing the optional ``owner``
    parameter to all other public callables exported by that module, including:

    * The :func:`annotationlib.ForwardRef.__init__` constructor.
    * The :func:`annotationlib.ForwardRef.evaluate` method.
    * The global :func:`annotationlib.call_annotate_function` function.
    * The global :func:`annotationlib.call_evaluate_function` function.

    Ergo, :mod:`beartype` itself *must* manually pass a non-:data:`None` value
    as the optional ``owner`` parameter when manually calling one of the above
    callables outside of the context of the
    :func:`annotationlib.get_annotations` getter.

    Parameters
    ----------
    hint : HintPep484749RefObjectType
        Object-oriented forward reference type hint to be inspected.

    Returns
    -------
    bool
        :data:`True` only if this reference is resolvable at runtime.
    '''
    assert isinstance(hint, HintPep484749RefObjectType), (
        f'{repr(hint)} not "annotationlib.ForwardRef" object.')

    # Return true only if...
    return (
        # The active Python interpreter targets Python >= 3.14 *AND*...
        #
        # Note that this implies this reference to actually be a full-blown
        # "annotationlib.ForwardRef" object (which necessarily defines the
        # dunder attribute tested below) rather than a thin "typing.ForwardRef"
        # wrapper (which doesn't). Under Python >= 3.14, the latter is simply a
        # deprecated alias of the former.
        IS_PYTHON_AT_LEAST_3_14 and
        # This private dunder variable is a non-empty string.
        bool(hint.__owner__)  # type: ignore[attr-defined]
    )

# ....................{ GETTERS                            }....................
#FIXME: Unit test us up, please.
def get_hint_pep484749_ref_names(
    # Mandatory parameters.
    hint: HintPep484749Ref,

    # Optional parameters.
    exception_cls: TypeException = BeartypeDecorHintForwardRefException,
    exception_prefix: str = '',
) -> TupleStrOrNoneAndStr:
    '''
    Possibly undefined fully-qualified module name and possibly qualified
    classname referred to by the passed :pep:`484`-compliant **forward reference
    type hint** (i.e., object indirectly referring to a type hint that typically
    has yet to be defined).

    This getter is intentionally *not* memoized (e.g., by the
    ``callable_cached`` decorator), as the implementation mostly reduces to an
    efficient one-liner.

    Parameters
    ----------
    hint : HintPep484749Ref
        Forward reference to be introspected.
    exception_cls : Type[Exception], default: BeartypeDecorHintForwardRefException
        Type of exception to be raised in the event of a fatal error. Defaults
        to :exc:`.BeartypeDecorHintForwardRefException`.
    exception_prefix : str, default: ''
        Human-readable substring prefixing raised exception messages. Defaults
        to the empty string.

    Returns
    -------
    tuple[Optional[str], str]
        2-tuple ``(hint_module_name, hint_type_name)`` where:

        * ``hint_module_name`` is the possibly undefined fully-qualified module
          name referred to by this forward reference, defined as either:

          * If this forward reference is a :class:`annotationlib.ForwardRef`
            object passed a module name at instantiation time via the ``module``
            parameter, this module name.
          * Else, :data:`None`.

        * ``hint_type_name`` is the possibly qualified classname referred to by this
          forward reference.

    Raises
    ------
    exception_cls
        If either:

        * This forward reference is *not* actually a forward reference.
        * This forward reference is **relative** (i.e., contains *no* ``.``
          delimiters) and either:

          * Neither the passed callable nor class define the ``__module__``
            dunder attribute.
          * The passed callable and/or class define the ``__module__``
            dunder attribute, but the values of those attributes all refer to
            unimportable modules that do *not* appear to physically exist.
    '''

    # If this is *NOT* a forward reference, raise an exception.
    die_unless_hint_pep484749_ref(
        hint=hint,
        exception_cls=exception_cls,
        exception_prefix=exception_prefix,
    )
    # Else, this is a forward reference.

    # Possibly unqualified basename of the class to which reference refers.
    hint_name: str = None  # type: ignore[assignment]

    # Fully-qualified name of the module to which this reference is relative if
    # this reference is relative to an importable module *OR* "None" otherwise
    # (i.e., if this reference is either absolute and thus not relative to a
    # module *OR* relative to an unimportable module).
    #
    # Note that, although *ALL* callables and classes should define the
    # "__module__" instance variable underlying the call to this getter, *SOME*
    # callables and classes do not. For this reason, we intentionally:
    # * Call the get_object_module_name_or_none() getter rather than
    #   get_object_module_name().
    # * Explicitly detect "None".
    # * Raise a human-readable exception.
    #
    # Doing so produces significantly more readable exceptions than merely
    # calling get_object_module_name(). Problematic objects include:
    # * Objects defined in Sphinx-specific "conf.py" configuration files. In all
    #   likelihood, Sphinx is running these files in some sort of arcane and
    #   non-standard manner (over which beartype has *NO* control).
    hint_module_name: Optional[str] = None

    # If this reference is a string, the classname of this reference is this
    # reference itself.
    if isinstance(hint, str):
        hint_name = hint
    # Else, this reference is *NOT* a string. By process of elimination, this
    # reference *MUST* be an "annotationlib.ForwardRef" *OR* "typing.ForwardRef"
    # object. In this case...
    else:
        # Forward reference classname referred to by this reference.
        hint_name = hint.__forward_arg__

        # Fully-qualified name of the module to which this presumably relative
        # forward reference is relative to if any *OR* "None" otherwise (i.e.,
        # if *NO* such name was passed at forward reference instantiation time).
        hint_module_name = get_hint_pep484749_ref_object_module_name_or_none(
            hint)

    # Return metadata describing this forward reference relative to this module.
    return hint_module_name, hint_name

# ....................{ GETTERS                            }....................
def get_hint_pep484749_ref_object_module_name_or_none(
    hint: HintPep484749RefObjectType) -> Optional[str]:
    '''
    Fully-qualified name of the module to which the passed :pep:`749`-compliant
    **object-oriented forward reference type hint** (i.e.,
    :class:`annotationlib.ForwardRef` object encapsulating all metadata required
    to dynamically resolve at runtime a reference to a referent target type hint
    that typically has yet to be defined in the current lexical scope) is
    relative to if any *or* :data:`None` otherwise (i.e., if *no* such name was
    passed at the time this object was instantiated).

    This getter is guaranteed to return a non-empty string *only* if this hint
    originates from :mod:`beartype` itself. This includes any of the following:

    * The low-level :func:`annotationlib.get_annotations` getter underlying the
      higher-level
      :func:`beartype._util.hint.pep.proposal.pep649749.get_pep649749_hintable_annotations_or_none`
      getter.
    * The higher-level
      :func:`beartype._util.hint.pep.proposal.pep749.get_hint_pep749_evaluator_mandatory`
      getter.
    * The higher-level
      :func:`beartype._util.hint.pep.proposal.pep749.get_hint_pep749_evaluator_optional`
      getter.

    Parameters
    ----------
    hint : HintPep484749RefObjectType
        Object-oriented forward reference type hint to be inspected.

    Returns
    -------
    Optional[str]
        Either:

        * If this :class:`annotationlib.ForwardRef` object was passed a module
          name at instantiation time via the ``module`` parameter, this module
          name.
        * Else, :data:`None`.
    '''
    assert isinstance(hint, HintPep484749RefObjectType), (
        f'{repr(hint)} not "annotationlib.ForwardRef" object.')

    # Fully-qualified name of the module to which this presumably relative
    # forward reference is relative to if any *OR* "None" otherwise (i.e.,
    # if *NO* such name was passed at forward reference instantiation time).
    #
    # Since the active Python interpreter targets >= Python 3.10, this
    # "typing.ForwardRef" object defines an optional "__forward_module__:
    # Optional[str] = None" dunder attribute whose value is either:
    # * If Python passed the "module" parameter when instantiating this
    #   "typing.ForwardRef" object, the value of that parameter -- which is
    #   presumably the fully-qualified name of the module to which this
    #   presumably relative forward reference is relative to.
    # * Else, "None".
    #
    # Note that:
    # * This requires violating privacy encapsulation by accessing dunder
    #   attributes unique to "typing.ForwardRef" objects. Sad, yet true.
    # * This object defines a significant number of other "__forward_"-prefixed
    #   dunder instance variables, which exist *ONLY* to enable the blatantly
    #   useless typing.get_type_hints() function to avoid repeatedly (and thus
    #   inefficiently) reevaluating the same forward reference. *sigh*
    # * Technically, this dunder attribute has been defined since at least
    #   Python >= 3.9.18. Sadly, one or more unknown earlier patch releases of
    #   the Python 3.9 development cycle do *NOT* support this. This is
    #   currently only safely usable under Python >= 3.10 -- all patch releases
    #   of which are known to define this dunder attribute.
    hint_module_name = hint.__forward_module__

    # If...
    if (
        # This reference was not instantiated with a module name *BUT*...
        not hint_module_name and (
            # The active Python interpreter targets Python >= 3.14 *AND*...
            #
            # Note that this implies this reference to be an
            # "annotationlib.ForwardRef" object defining the private "__owner__"
            # instance variable introspected below.
            IS_PYTHON_AT_LEAST_3_14 and
            # This reference was instantiated with an owner (typically either an
            # arbitrary callable *OR* type)...
            hint.__owner__ is not None  # type: ignore[attr-defined]
        )
    ):
        # Fully-qualified name of the module defining that owner if any *OR*
        # "None" otherwise (e.g., if neither a callable *NOR* type).
        hint_module_name = get_object_module_name_or_none(hint.__owner__)  # type: ignore[attr-defined]
    # Else, this reference was instantiated with either:
    # * A module name. In this case, preserve that module name as is.
    # * Neither a module *NOR* owner name. Default to *NO* module name.

    # Return this module name.
    return hint_module_name

# ....................{ RESOLVERS                          }....................
#FIXME: Unit test us up, please.
def resolve_hint_pep484749_ref_object(
    # Mandatory parameters.
    hint: HintPep484749RefObjectType,

    # Optional parameters.
    exception_cls: TypeException = (
        BeartypeCallHintPep749ForwardRefObjectException),
    exception_prefix: str = '',
) -> Hint:
    '''
    Resolve the passed :pep:`749`-compliant **object-oriented forward reference
    type hint** (i.e., :class:`annotationlib.ForwardRef` object encapsulating
    all metadata required to dynamically resolve at runtime a reference to a
    referent target type hint that typically has yet to be defined in the
    current lexical scope) to that referent target type hint.

    This resolver is intentionally *not* memoized (e.g., by the
    ``@callable_cached`` decorator). Resolving both absolute *and* relative
    forward references assumes contextual context (e.g., the fully-qualified
    name of the object to which relative forward references are relative to)
    that *cannot* be safely and context-freely memoized away.

    Caveats
    -------
    **Callers should gate calls to this resolver in** ``if`` **conditionals
    first calling the** :func:`.is_hint_pep484749_ref_object_resolvable`
    **tester.** Doing so substantially reduces the likelihood of unexpected
    exceptions. Why? Because only a subset of object-oriented forward references
    are safely resolvable at runtime. See that tester for further commentary.

    Parameters
    ----------
    hint : HintPep484749RefObjectType
        Object-oriented forward reference type hint to be resolved.
    exception_cls : Type[Exception], default: BeartypeCallHintPep749ForwardRefObjectException
        Type of exception to be raised in the event of a fatal error. Defaults
        to :exc:`.BeartypeCallHintPep749ForwardRefObjectException`.
    exception_prefix : str, default: ''
        Human-readable substring prefixing raised exception messages. Defaults
        to the empty string.

    Returns
    -------
    Hint
        Non-string type hint to which this reference refers.

    Raises
    ------
    exception_cls
        If attempting to dynamically evaluate this reference raises an
        exception, typically due to this reference being syntactically invalid
        as Python.
    '''
    assert isinstance(hint, HintPep484749RefObjectType), (
        f'{repr(hint)} not "annotationlib.ForwardRef" object.')

    # Attempt to resolve this source forward reference to its target referent.
    try:
        hint_resolved = hint.evaluate()  # type: ignore[attr-defined]
        # print(f'Resolved object-oriented type hint {repr(hint)} to {repr(hint_resolved)}...')
    # If doing so fails for *ANY* reason whatsoever...
    except Exception as exception:
        assert isinstance(exception_cls, type), (
            f'{repr(exception_cls)} not exception class.')
        assert isinstance(exception_prefix, str), (
            f'{repr(exception_prefix)} not string.')

        # Possibly undefined fully-qualified module name and possibly
        # unqualified classname referred to by this forward reference.
        hint_module_name, hint_type_name = get_hint_pep484749_ref_names(
            hint=hint, exception_prefix=exception_prefix)

        # Human-readable traceback formatted from this exception, indented to
        # improve readability when embedded below.
        exception_traceback = label_exception_traceback(exception)

        # Human-readable message to be raised.
        exception_message = (
            f'{exception_prefix}'
            f'PEP 649 unquoted forward reference type hint "{hint_type_name}" '
        )

        # If this forward reference originates from a known module, append that.
        if hint_module_name:
            exception_message += f'in module "{hint_module_name}" '
        # Else, this forward reference originates from *NO* known module.

        # Finalize this message.
        exception_message += (
            f'wrapped by PEP 749 resolver {repr(hint)} '
            f'unresolvable to its target referent:\n'
            f'{exception_traceback}'
        )

        # Raise a human-readable exception wrapping the typically
        # non-human-readable exception raised above.
        raise exception_cls(exception_message) from exception

    # Return this resolved hint.
    return hint_resolved
