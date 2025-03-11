#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype **dataclass decorators** (i.e., low-level decorators decorating
pure-Python types decorated by the :pep:`557`-compliant
:obj:`dataclasses.dataclass` decorator).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.roar import BeartypeDecorHintParamDefaultViolation
from beartype._conf.confcls import BeartypeConf
from beartype._util.cls.utilclsset import set_type_attr
from beartype._util.func.utilfuncget import get_func_annotations
from beartype._util.utilobject import (
    SENTINEL,
    get_object_type_name,
)

# ....................{ DECORATORS                         }....................
#FIXME: As a mandatory prerequisite *BEFORE* integrating this into the @beartype
#codebase, we first need to:
#* Generalize both is_bearable() and die_if_unbearable() to support quoted
#  relative forward references. As always, the algorithm should iteratively
#  search up the callstack for the first stack frame residing *OUTSIDE*
#  @beartype. Actually... that doesn't suffice. We probably really do need to
#  iteratively search up the entire call stack before raising an exception. It's
#  fine. Just do it. The alternative is broken badness.
#FIXME: Unit test against all possible dataclass edge cases, including:
#* "frozen=True".
#* "slots=True".
#* "frozen=True, slots=True".
#* "ClassVar[...]".
#* "InitVar[...]".
#* PEP 563.
#* Quoted relative forward references (e.g., "list['MuhUndefinedType']").
#* "typing.Self". We're *NOT* passing "cls_stack" to either the is_bearable() or
#  die_if_unbearable() functions, because those functions currently fail to
#  accept an optional "cls_stack" parameter. We should probably generalize both
#  of those functions to accept that parameter, huh? *sigh*

def beartype_pep557_dataclass(
    # Note that dataclasses do *NOT* have a more specific superclass than merely
    # the root "type" superclass of *ALL* types, sadly:
    #     >>> from dataclasses import dataclass
    #     >>> @dataclass
    #     ... class MuhDataclass(object): muh_int: int
    #     >>> MuhDataclass.__mro__
    #     (<class '__main__.MuhDataclass'>, <class 'object'>)  # <--- yikes
    #
    # From a typing perspective, "type" is the best that can be done. Yikes!
    datacls: type,
    conf: BeartypeConf,
) -> None:
    '''
    Decorate the passed **dataclass** (i.e., pure-Python types decorated by the
    :pep:`557`-compliant :obj:`dataclasses.dataclass` decorator) with
    dynamically generated type-checking of.

    This decorator safely monkey-patches type-checking into this same dataclass
    *without* creating or returning a new object. This type-checking *only*
    applies to **dataclass fields.** By :pep:`557`, a "dataclass field" is *any*
    class attribute of this dataclass annotated by *any* type hint other than
    either:

    * A :pep:`557`-compliant ``dataclasses.ClassVar[...]`` type hint.
    * A :pep:`557`-compliant ``dataclasses.InitVar[...]`` type hint.

    This decorator safely monkey-patches the ``__setattr__()`` dunder method of
    this dataclass. If this dataclass does *not* directly define
    ``__setattr__()``, this decorator adds a new ``__setattr__()`` to this
    dataclass; else, this decorator wraps the existing ``__setattr__()`` already
    directly defined on this dataclass by a new ``__setattr__()`` internally
    deferring to that existing ``__setattr__()``. In either case, this new
    ``__setattr__()`` type-checks each dataclass field on both:

    * **Dataclass object initialization** (i.e., at early ``__init__()`` time).
    * **Dataclass field assignment** (i.e., when each field is subsequently
      assigned to with an assignment statement).

    Parameters
    ----------
    datacls : BeartypeableT
        Dataclass to be decorated by :func:`beartype.beartype`.
    conf : BeartypeConf
        Beartype configuration configuring :func:`beartype.beartype` uniquely
        specific to this dataclass.

    Returns
    -------
    BeartypeableT
        This same dataclass monkey-patched in-place with type-checking.
    '''
    assert isinstance(datacls, type), f'{repr(datacls)} not dataclass.'
    assert isinstance(conf, BeartypeConf), (
        f'{repr(conf)} not beartype configuration.')

    # ..................{ IMPORTS                            }..................
    # Defer heavyweight imports prohibited at global scope.
    from beartype.door import (
        die_if_unbearable,
        is_bearable,
    )

    # ..................{ LOCALS                             }..................
    #FIXME: Inappropriate. Obviously, "dataclass" is an uncallable type rather
    #than a callable. Instead:
    #* Define a new "Annotationsable" type hint in the
    #  "beartype._data.hint.datahinttyping" submodule resembling:
    #      Annotationsable = Union[type, Callable]
    #      '''
    #      PEP-compliant type hint matching an **annotations-able** (i.e.,
    #      object capable of being annotated by two or more type hints via an
    #      ``__annotations__`` dunder dictionary defined on that object).
    #      '''
    #* Generalize the existing get_func_annotations() getter into a new
    #  get_object_annotations() getter with signature resembling:
    #      from beartype._data.hint.datahinttyping import (
    #          Annotations,
    #          Annotationsable,
    #      )
    #      def get_object_annotations(obj: Annotationsable) -> Annotations:
    #* Call that getter here.
    #FIXME: Copy this dictionary via dict.copy() for safety. Directly modifying
    #"__annotations__" dunder dictionaries is probably unsafe in Python >= 3.14.
    #Since this is becoming a common operation, perhaps simply add a new
    #optional "is_copy: bool = False" parameter to this get_object_annotations()
    #getter. If "is_copy" is true, then that getter performs the copy for us.

    # Dictionary mapping from the name of each field of this dataclass to the
    # type hint annotating that parameter *AFTER* resolving all PEP
    # 563-postponed type hints above.
    field_name_to_hint = get_func_annotations(datacls)

    # dict.get() method bound to this dictionary as a negligible optimization.
    field_name_to_hint_get = field_name_to_hint.get

    #FIXME: Insufficient. We also need to immediately sanify *ALL* of these
    #hints right here *OUTSIDE* of the closure defined below. Yet again, issues
    #arise. Why? Because the sanify_hint_root_func() function is inappropriate
    #here. Instead:
    #* Define a new sanify_hint_root_type() getter. This could prove
    #  non-trivial. sanify_hint_root_func() accepts a "decor_meta" parameter,
    #  which currently only applies to decorated *CALLABLES* rather than
    #  *TYPES*. We probably want to generalize "decor_meta" to support both...
    #  maybe? Maybe not? To do this properly, we probably first want to:
    #  * Create a new "decor_meta" type hierarchy resembling:
    #        class BeartypeDecorMetaABC(metaclass=ABCMeta): ...
    #        class BeartypeDecorMetaFunc(BeartypeDecorMetaABC): ...
    #        class BeartypeDecorMetaType(BeartypeDecorMetaABC): ...
    #  * Refactor references to "BeartypeDecorMeta" to either
    #    "BeartypeDecorMetaABC" *OR* ""BeartypeDecorMetaFunc" depending on
    #    context. Most probably require the latter. Any that don't should simply
    #    reference "BeartypeDecorMetaABC" for generality.
    #  * Remove all references to "BeartypeDecorMeta".
    #* Iterate over the items of the "field_name_to_hint" dictionary here.
    #* For each such key-value pair:
    #  * *BEFORE* sanifying this hint:
    #    * If this hint is either a "dataclasses.ClassVar[...]" *OR*
    #      "dataclasses.InitVar[...]" hint (as detectable via
    #      get_hint_pep_sign_or_none()), remove this hint from this dictionary
    #      entirely. The corresponding dataclass attribute is *NOT* actually a
    #      field and is thus ignorable for type-checking purposes. Although
    #      attempting to detect hint types *BEFORE* sanification is almost
    #      always a bad idea, this might be the one and only case where doing so
    #      is not only reasonable but desirable. Why? PEP 557. The standard
    #      pretty explicitly states that both "dataclasses.ClassVar[...]" *AND*
    #      "dataclasses.InitVar[...]" hints are only valid as root type hints.
    #      Why? Because the @dataclasses.dataclass decorator itself explicitly
    #      detects these root type hints with a crude detection scheme that only
    #      works because these hints are required to be root. Since PEP
    #      563-postponed stringified type hints are guaranteed to be resolved by
    #      the "FIXME:" below at an earlier decoration-time phase, these hints
    #      are guaranteed to be both non-stringified and root type hints. W00t!
    #  * Sanify this hint.
    #  * If doing so reduced this hint to "Any", remove this hint from this
    #    dictionary entirely. Doing so speeds up closure logic below.
    #  * Actually... this could be a problematic approach. Why? "hint_or_sane",
    #    of course. is_bearable() and die_if_unbearable() only accept actual
    #    type hints. But "hint_or_sane" could be a @beartype-specific type hint
    #    dataclass! So... that doesn't quite work. I suppose what we could do
    #    is an optimization resembling:
    #    * If sanifying this hint produced a different type hint than the
    #      original type hint *AND* this new type hint is *NOT* simply a
    #      "HintSanifiedData" object, replace this old hint with this new hint
    #      in the "field_name_to_hint" dictionary.
    #    * Else, preserve this existing hint in this dictionary as is. If a
    #      "HintSanifiedData" object was produced, we'll just have to throw that
    #      away for the moment. Alternately, we could *TRY* to generalize
    #      is_bearable() and die_if_unbearable() to accept these objects. But...
    #      probably not worth it for the moment. It is what it is.
    #FIXME: Note that an edge case could arise here under Python >= 3.12 due to
    #the intersection of PEP 563 and 695:
    #    from __future__ import annotations  # <-- PEP 563
    #    from dataclasses import dataclass
    #
    #    type ohnoes[T] = T | int  # <-- PEP 695
    #
    #    @dataclass
    #    class Ugh(object):
    #        guh: ohnoes[str]
    #
    #To efficiently resolve this, we *PROBABLY* want to generalize our existing
    #beartype.peps.resolve_pep563() resolver to additionally support types in
    #addition to its existing support for classes. Naturally, this gets ugly
    #fast. For example:
    #* The existing resolve_pep563() function accepts a "func" parameter.
    #  Consider deprecating this parameter and instead requesting that callers
    #  pass only a generic "obj" parameter.
    #* Generalize this function to accept an "obj" parameter resembling:
    #      obj: Annotationsable

    # Existing __setattr__() dunder method directly defined on this dataclass if
    # any *OR* "None" otherwise (i.e., if this dataclass fails to directly
    # define that method).
    datacls_setattr = datacls.__dict__.get('__setattr__')

    # *HORRIBLE HACK*. For unknown reasons, the super() function called below
    # requires the "__class__" attribute to be defined as a cell (i.e., closure)
    # variable. If this is *NOT* the case, then that call raises the unreadable
    # low-level exception:
    #     RuntimeError: super(): __class__ cell not found
    __class__ = datacls

    # ..................{ CLOSURES                           }..................
    def check_pep557_dataclass_field(
        self, attr_name: str, attr_value: object) -> None:
        # Type hint annotating this dataclass attribute if this attribute is
        # annotated and thus (probably) a dataclass field *OR* "None" otherwise
        # (i.e., if this attribute is unannotated).
        #
        # Note that:
        # * There exists a (mostly) one-to-one correlation between fields and
        #   type hints. PEP 557 literally defines a dataclass field as an
        #   annotated dataclass attribute:
        #      A field is defined as any variable identified in __annotations__.
        #      That is, a variable that has a type annotation.
        # * There exist alternate means of introspecting dataclass fields (e.g.,
        #   the public dataclasses.fields() global function). Without exception,
        #   these alternates are all less efficient *AND* more cumbersome than
        #   simply directly introspecting dataclass field type hints. Moreover,
        #   these alternates are unlikely to play nicely with unquoted forward
        #   references under Python >= 3.14.
        attr_hint = field_name_to_hint_get(attr_name, SENTINEL)

        # If this dataclass attribute is annotated and thus a field...
        if attr_hint is not SENTINEL:
            # If the new value of this field violates this hint...
            #
            # Note that this is a non-negligible optimization. Technically, this
            # preliminary test is superfluous: only the call to the
            # die_if_unbearable() raiser below is required. Pragmatically, this
            # preliminary test avoids various needlessly expensive operations in
            # the common case that this value satisfies this hint.
            if not is_bearable(obj=attr_value, hint=attr_hint, conf=conf):
                # Machine-readable representation of this dataclass instance.
                self_repr: str = ''

                # Attempt to introspect this representation of this instance.
                # There exist two common cases here:
                # * This instance has already been fully initialized (i.e., the
                #   __init__() dunder method has already successfully returned),
                #   implying that all dataclass fields have already been set to
                #   valid values on this instance. In this case, this
                #   "repr(self)" call *SHOULD* succeed -- unless this dataclass
                #   subclass has erroneously redefined the __repr__() dunder
                #   method in a fragile manner raising unexpected exceptions.
                # * This instance has *NOT* yet been fully initialized (i.e.,
                #   the __init__() dunder method has *NOT* yet successfully
                #   returned), implying that one or more dataclass fields have
                #   *NOT* yet been set to valid values on this instance. In this
                #   case, this "repr(self)" call *SHOULD* fail with an
                #   "AttributeError" resembling:
                #       AttributeError: '{class_name}' object has no attribute '{attr_name}'
                try:
                    self_repr = repr(self)
                # If introspecting this representation fails for any reason
                # whatsoever, fallback to just the fully-qualified name of this
                # dataclass subclass, which should *ALWAYS* be introspectable.
                except Exception:
                    self_repr = repr(get_object_type_name(datacls))

                # Human-readable substring prefixing the exception raised below.
                exception_prefix = (
                    f'Dataclass {self_repr} '
                    f'attribute {repr(attr_name)} new value {repr(attr_value)} '
                )

                #FIXME: *UGLY LOGIC.* Sure. Technically, this works. But we
                #repeat the *EXACT* same logic in our currently unused
                #_die_if_arg_default_unbearable() validator, which we will
                #almost certainly re-enable at some point. Instead:
                #* Just add a new optional "exception_cls" parameter to the
                #  die_if_unbearable() validator called below. If necessary, the
                #  initial implementation of this parameter could just do what
                #  we currently do here. Not great, but at least that logic
                #  would be centralized away from prying eyes in the same API.

                # Modifiable keyword dictionary encapsulating this beartype
                # configuration.
                conf_kwargs = conf.kwargs.copy()

                #FIXME: This should probably be configurable as well. For now,
                #this is fine. We shrug noncommittally. We shrug, everyone!
                #FIXME: "BeartypeDecorHintParamDefaultViolation" obviously isn't
                #right. Define a new "BeartypeDecorHintDataclassFieldViolation"
                #exception subclass, please.

                # Set the type of violation exception raised by the subsequent
                # call to the die_if_unbearable() function to the expected type.
                conf_kwargs['violation_door_type'] = (
                    BeartypeDecorHintParamDefaultViolation)

                # New beartype configuration initialized by this dictionary.
                conf_new = BeartypeConf(**conf_kwargs)

                # Raise this type of violation exception.
                die_if_unbearable(
                    obj=attr_value,
                    hint=attr_hint,
                    conf=conf_new,
                    exception_prefix=exception_prefix,
                )
            # Else, the new value of this field satisfies this hint. In this
            # case, silently reduce to a noop.
        # Else, this dataclass attribute is unannotated and thus *NOT* a field.
        # In this case, this attribute is ignorable.

        # Existing __setattr__() dunder method defined on this dataclass,
        # defined as either...
        datacls_superclass_setattr = (
            # If this dataclass directly defines this method, this method;
            datacls_setattr or
            # Else, this dataclass does *NOT* directly define this method. In
            # this case, fallback to the superclass __setattr__() dunder method
            # *GUARANTEED* to be defined on at least one superclass of this
            # dataclass. Why? Because the root superclass object.__setattr__()
            # dunder method is *GUARANTEED* to exist on all objects.
            super().__setattr__  # type: ignore[misc]
        )

        # Defer to the superclass __setattr__() implementation.
        datacls_superclass_setattr(attr_name, attr_value)

    # ..................{ DECORATORS                         }..................
    # Safely replace this undecorated __setattr__() implementation with this
    # decorated __setattr__() implementation.
    set_type_attr(datacls, '__setattr__', check_pep557_dataclass_field)
