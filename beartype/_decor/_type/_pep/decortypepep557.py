#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype **dataclass decorators** (i.e., low-level decorators decorating
pure-Python types decorated by the :pep:`557`-compliant
:obj:`dataclasses.dataclass` decorator).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ TODO                               }....................
#FIXME: Unit test against all possible dataclass edge cases, including:
#* "typing.Self". We're *NOT* passing "cls_stack" to either the is_bearable() or
#  die_if_unbearable() functions, because those functions currently fail to
#  accept an optional "cls_stack" parameter. We should probably generalize both
#  of those functions to accept that parameter, huh? Both already accept
#  optional undocumented "exception_prefix" parameters, for example. Yet another
#  optional undocumented parameter mostly only of interest to @beartype is no
#  significant hardship. That said:
#  * Each additional optional parameter accepted by a callable probably *DOES*
#    slow that callable down. Test this. If performance degrades as the number
#    of optional parameters increases, we should instead:
#    * Define a new "beartype._check.checktest" submodule. In this submodule:
#      * Define a new pair of lower-level is_obj_satisfies_hint() and
#        die_unless_obj_satisfies_hint() functions, initially just copy-pasted
#        from the existing is_bearable() and die_if_unbearable() functions.
#      * Grep the codebase for everywhere we currently pass that optional
#        "exception_prefix" parameter to either is_bearable() or
#        die_if_unbearable().
#      * Refactor each such call to instead call is_obj_satisfies_hint() or
#        die_unless_obj_satisfies_hint().
#      * Remove that optional "exception_prefix" parameter from both
#        is_bearable() and die_if_unbearable(). *NOTE THAT THIS IS SOMEWHAT
#        NON-TRIVIAL*. The exact details elude me at the moment, but we'll
#        basically need to do something resembling:
#        * Rename the existing make_func_checker() factory in the existing
#          "beartype._check.checkmake" submodule to make_func_checker_bearable()
#          for disambiguity.
#        * Define a new make_func_checker_satisfies() factory in that submodule,
#          initially just copy-pasted from make_func_checker_bearable().
#        * Remove *ALL* reference to "exception_prefix" from
#          make_func_checker_bearable() (while of course preserving those same
#          references in make_func_checker_satisfies()).
#        * Restore DRY by refactoring both make_func_checker_bearable() and
#          make_func_checker_satisfies() to defer to a new lower-level private
#          _make_func_checker() factory (or something something).
#        * At this point, the "checkmake" submodule has almost certainly
#          exploded into 10,000,000 lines of madness. Consequently:
#          * Define a new "beartype._check.make" subpackage.
#          * Rename "beartype._check.checkmake" to
#            "beartype._check.make.checkmakefunc".
#          * Split up "beartype._check.make.checkmakefunc" into appropriate new
#            submodules. *shrugs nonchalantly*
#      * Add a new optional "cls_stack" parameter to both
#        is_obj_satisfies_hint() and die_unless_obj_satisfies_hint().
#
#  *INDEED*. Performance almost certainly degrades as the number of optional
#  parameters increases, based on the implementation of our
#  "beartype._check.checkmake.make_func_checker() factory alone. Why? Because
#  the tuple size of "CACHE_KEY" increases. Ergo, we should have *ALREADY* done
#  this. So much sighing can be distantly heard.
#
#  *WAIT*. Does any of the above actually apply? Probably not. @beartype
#  resolves "typing.Self" at decoration time. So... uh. This should already just
#  work out-of-the-box. Test us up, yo! *lolface*
#* Dataclass subclasses. Does each dataclass subclass in a hierarchy have its
#  own unique "__annotations__" dunder dictionary *OR* does each such subclass
#  composite the "__annotations__" of both itself and its superclasses? Probably
#  the former, huh? Yikes. This implies that our trivial attempt to directly use
#  "__annotations__" fails to suffice. We'll actually have to iteratively crawl
#  up "datacls.__mro__" and composite the full "__annotations__" from the
#  "__annotations__" of all dataclass superclasses.
#
#  Note, however, that there exists a critical optimization here: we
#  *ABSOLUTELY* need to stop iterating up "datacls.__mro__" when we visit the
#  first superclass that is *NOT* also a dataclass. Is that even possible? No
#  idea. If it is, we halt iteration at that first non-dataclass. This is
#  essential, as the class attributes of that first non-dataclass (and all
#  superclasses of that non-dataclass) *CANNOT* by definition by fields.
#
#  *WAIT.* Halting iteration doesn't work, because "datacls.__mro__" doesn't
#  exactly correspond to superclass relations. Consider diamond inheritance, for
#  example. Ergo, we'll instead have to inefficiently *IGNORE* all superclasses
#  in "datacls.__mro__" that are *NOT* themselves dataclasses. Fine. No worries.
#  We can certainly do that. Nonetheless, we sigh. *sigh*
#
#  Oh -- and note that we'll need to iteratively resolve PEP 563-postponed
#  stringified type hints against each such superclass "__annotations__" as
#  well. Jeez. This sure got ugly fast, huh? So much sighing! *sigh sigh*

#FIXME: [SPEED] One possible blocker remains to globally enabling
#"is_pep557_fields=True": efficiency. Profile whether enabling
#"is_pep557_fields=True" reduces efficiency when setting arbitrary dataclass
#fields and, if so, by how much. A negligible amount of degradation is, of
#course, acceptable. It's negligible, after all! If the degradation is
#meaningfully measurable, however, then our current approach is a no-go. We
#almost don't need to profile this, do we? It's almost certainly a speed drag.
#
#The obvious solution (which is also the non-trivial solution) is to replace our
#currently unoptimized one-size-fits-all check_pep557_dataclass_field() closure
#defined below with *A DYNAMICALLY GENERATED __SETATTR__ FUNCTION SPECIFIC TO
#THE CURRENTLY DECORATED DATACLASS AND THE TYPE HINTS ANNOTATING THE FIELDS OF
#THAT DATACLASS.* I'm shouting in all caps because it's important. It's also
#nigh impossible, probably. To be sure, it would be a veritable ton of work. To
#be sure, that work would also be fun. And fun is entirely why we are here.

# ....................{ IMPORTS                            }....................
from beartype.roar import BeartypeCallHintPep557FieldViolation
from beartype._check.convert._reduce.redmain import reduce_hint
from beartype._conf.confmain import BeartypeConf
from beartype._data.typing.datatypingport import (
    DictStrToHint,
    Hint,
)
from beartype._data.hint.sign.datahintsignset import (
    HINT_SIGNS_PEP557_DATACLASS_NONFIELDS)
from beartype._data.kind.datakindiota import SENTINEL
from beartype._util.cls.pep.clspep557 import (
    die_unless_type_pep557_dataclass,
    is_pep557_dataclass_frozen,
)
from beartype._util.cls.utilclsset import set_type_attr
from beartype._util.hint.pep.proposal.pep749.pep649749annotate import (
    get_hintable_pep649749_annotations)
from beartype._util.hint.pep.utilpepsign import get_hint_pep_sign_or_none
from beartype._util.utilobjget import get_object_type_name

# ....................{ DECORATORS                         }....................
def beartype_pep557_dataclass(
    # Mandatory parameters.
    #
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

    # Optional parameters.
    exception_prefix: str = '',
) -> None:
    '''
    Decorate the passed **dataclass** (i.e., pure-Python class decorated by the
    :pep:`557`-compliant :obj:`dataclasses.dataclass` decorator) with
    dynamically generated type-checking of all **dataclass fields** (i.e., class
    attributes annotated by *any* type hints other than :pep:`526`-compliant
    ``dataclasses.ClassVar[...]`` or :pep:`557`-compliant
    ``dataclasses.InitVar[...]`` type hints) on both **dataclass object
    initialization** (i.e., at ``__init__()`` time) *and* **dataclass field
    assignment** (i.e., when each field is subsequently assigned to by an
    assignment statement).

    This decorator *only* type-checks **dataclass fields.** By :pep:`557`, a
    "dataclass field" is *any* class attribute of this dataclass annotated by
    *any* type hint other than either:

    * A :pep:`526`-compliant ``dataclasses.ClassVar[...]`` type hint.
    * A :pep:`557`-compliant ``dataclasses.InitVar[...]`` type hint.

    Unlike most :mod:`beartype` decorators, this decorator safely monkey-patches
    this dataclass in-place. (Equivalently, this decorator safely monkey-patches
    type-checking into this same dataclass *without* creating or returning a new
    dataclass.) Specifically, this decorator monkey-patches the
    ``__setattr__()`` dunder method of this dataclass. If this dataclass does
    *not* directly define ``__setattr__()``, this decorator adds a new
    ``__setattr__()`` to this dataclass; else, this decorator wraps the existing
    ``__setattr__()`` already directly defined on this dataclass with a new
    ``__setattr__()`` internally deferring to that existing ``__setattr__()``.
    In either case, this new ``__setattr__()`` type-checks that each dataclass
    field satisfies the type hint annotating that field on both:

    * **Dataclass object initialization** (i.e., at early ``__init__()`` time).
    * **Dataclass field assignment** (i.e., when each field is subsequently
      assigned to by an assignment statement).

    Parameters
    ----------
    datacls : BeartypeableT
        Dataclass to be decorated by :func:`beartype.beartype`.
    conf : BeartypeConf
        Beartype configuration configuring :func:`beartype.beartype` uniquely
        specific to this dataclass.
    exception_prefix : str, default: ''
        Human-readable substring prefixing raised exceptions messages. Defaults
        to the empty string.

    Returns
    -------
    BeartypeableT
        This same dataclass monkey-patched in-place with type-checking.
    '''
    assert isinstance(conf, BeartypeConf), (
        f'{repr(conf)} not beartype configuration.')

    # ..................{ PREAMBLE                           }..................
    # If this dataclass is *NOT* actually a dataclass, raise an exception.
    die_unless_type_pep557_dataclass(
        cls=datacls, exception_prefix=exception_prefix)
    # Else, this dataclass is actually a dataclass.

    # ..................{ IMPORTS                            }..................
    # Defer heavyweight imports prohibited at global scope.
    from beartype.door import (
        die_if_unbearable,
        is_bearable,
    )

    # ..................{ LOCALS                             }..................
    # *HORRIBLE HACK*. For unknown reasons, the super() function called below
    # requires the "__class__" attribute to be defined as a cell (i.e., closure)
    # variable. If this is *NOT* the case, then that call raises the unreadable
    # low-level exception:
    #     RuntimeError: super(): __class__ cell not found
    __class__ = datacls

    # __setattr__() dunder method directly defined on this dataclass if any *OR*
    # "None" (i.e., if this dataclass does *NOT* directly define this method).
    datacls_setattr = datacls.__dict__.get('__setattr__')

    # ..................{ SANIFICATION                       }..................
    # Sanify (i.e., sanitize) this dictionary of type hints.

    #FIXME: Copy this dictionary via dict.copy() for safety. Directly modifying
    #"__annotations__" dunder dictionaries is probably unsafe in Python >= 3.14.
    #Since this is becoming a common operation, perhaps simply add a new
    #optional "is_copy: bool = False" parameter to this get_object_annotations()
    #getter. If "is_copy" is true, then that getter performs the copy for us.

    # Unsanified (i.e., original) dictionary mapping from the name of each
    # possible field of this dataclass to the possibly insane type hint
    # annotating that field *AFTER* resolving all PEP 563-postponed type hints.
    attr_name_to_hint_insane = get_hintable_pep649749_annotations(datacls)

    # Sanified (i.e., sanitized) dictionary mapping from the name of each
    # guaranteable field of this dataclass to the ostensibly sane type hint
    # annotating that field, initialized to the empty dictionary.
    field_name_to_hint: DictStrToHint = {}

    # dict.get() method bound to this dictionary as a negligible optimization.
    field_name_to_hint_get = field_name_to_hint.get

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
    #beartype.peps.resolve_pep563() resolver to additionally support type
    #aliases in addition to its existing support for classes. Naturally, this
    #gets ugly fast. For example:
    #* The existing resolve_pep563() function accepts a "func" parameter.
    #  Consider deprecating this parameter and instead requesting that callers
    #  pass only a generic "obj" parameter.
    #* Generalize this function to accept an "obj" parameter resembling:
    #      obj: Annotationsable
    #FIXME: Actually, the above should just work now without any additional
    #improvements. Test that up though, please.

    # For the name and unsanified hint of each class attribute of this
    # dataclass...
    for field_name, field_hint in attr_name_to_hint_insane.items():
        # Sign uniquely identifying this unsanified hint.
        field_hint_sign = get_hint_pep_sign_or_none(field_hint)

        # If this sign signifies this class attribute to *NOT* be a dataclass
        # field, remove this attribute from consideration by ignoring this
        # attribute rather than adding this attribute back to this dictionary.
        #
        # Note that attempting to identify unsanified hints is often a bad idea.
        # Only sanified hints are safely identifiable, usually. This might be
        # the one and only edge case where identifying an unsanified hint is not
        # only reasonable but desirable. Why? PEP 557, which explicitly states
        # that both PEP 526-compliant "type.ClassVar[...]" *AND* PEP
        # 557-compliant "dataclasses.InitVar[...]" hints are only valid as root
        # hints directly annotating class variables of dataclasses. Why? Because
        # the PEP 557-compliant @dataclasses.dataclass decorator itself
        # explicitly detects these root hints with a crude detection scheme that
        # only works because these hints are required to be root. Since PEP
        # 563-postponed stringified type hints are guaranteed to have already
        # been resolved above, these hints are guaranteed to be both
        # non-stringified and root hints. W00t!
        if field_hint_sign in HINT_SIGNS_PEP557_DATACLASS_NONFIELDS:
            continue
        # Else, this sign signifies this class attribute to actually be a field.

        #FIXME: Insufficient. We also need to immediately sanify *ALL* of these
        #hints right here *OUTSIDE* of the closure defined below. Yet again,
        #issues arise. Why? Because the sanify_hint_root_func() function is
        #inappropriate here. Instead:
        #* Define a new sanify_hint_root_type() getter. This could prove
        #  non-trivial. sanify_hint_root_func() accepts a "decor_curr"
        #  parameter, which currently only applies to decorated *CALLABLES*
        #  rather than *TYPES*. We probably want to generalize "decor_curr" to
        #  support both... maybe? Maybe not? To do this properly, we probably
        #  first want to:
        #  * Create a new "decor_curr" type hierarchy resembling:
        #        class BeartypeDecorMetaABC(metaclass=ABCMeta): ...
        #        class BeartypeDecorMetaFunc(BeartypeDecorMetaABC): ...
        #        class BeartypeDecorMetaType(BeartypeDecorMetaABC): ...
        #  * Refactor references to "BeartypeCallDecorData" to either
        #    "BeartypeDecorMetaABC" *OR* ""BeartypeDecorMetaFunc" depending on
        #    context. Most probably require the latter. Any that don't should
        #    simply reference "BeartypeDecorMetaABC" for generality.
        #  * Remove all references to "BeartypeCallDecorData".
        #FIXME: If sanifying this hint so reduced this hint to
        #"HINT_SANE_IGNORABLE", remove this hint from this dictionary entirely.
        #Doing so speeds up closure logic below, which is critical. Obviously,
        #we'll also need to:
        #* Actually test this reduction by defining a new dataclass field in our
        #  test suite annotated by an ignorable type hint (e.g., "object").
        #FIXME: Actually... this could be a problematic approach. Why?
        #"hint_or_sane", of course. is_bearable() and die_if_unbearable() only
        #accept actual type hints. But "hint_or_sane" could be a
        #@beartype-specific "HintSane" dataclass object! So... that doesn't
        #quite work. I suppose what we could do is an optimization resembling:
        #* If sanifying this hint produced a different type hint than the
        #  original type hint *AND* this new type hint is *NOT* simply a
        #  "HintSane" object, replace this old hint with this new hint
        #  in the "field_name_to_hint" dictionary.
        #* Else, preserve this existing hint in this dictionary as is. If a
        #  "HintSane" object was produced, we'll just have to throw
        #  that away for the moment. Alternately, we could *TRY* to generalize
        #  is_bearable() and die_if_unbearable() to accept these objects.
        #  But... probably not worth it for the moment. It is what it is.
        #FIXME: Actually... we can do something even better! There's no
        #particular reason we have to call the public-facing is_bearable() and
        #die_if_unbearable() functions. Instead:
        #* Define new private-facing variants of those functions transparently
        #  accepting a "hint: HintSane" parameter. Call them:
        #  * is_hint_sane_bearable().
        #  * die_if_hint_sane_unbearable().
        #  In theory, this shouldn't be *TOO* hard.
        #* Call these private- rather than public-facing variants below.
        #  Voila! Problem transparently resolved.
        #
        #Right. Obviously. We suggested is_obj_satisfies_hint() and
        #die_unless_obj_satisfies_hint() functions above. Ergo, these should
        #instead be called is_obj_satisfies_hint_sane() and
        #die_unless_obj_satisfies_hint_sane(). Indeed, the "HintSane" dataclass
        #itself could just define a pair of new is_satisfied() and
        #die_unless_satisfied() methods. Probably the best idea. *shrug*
        #FIXME: *WAAAAAAAAAAAAAAAAAAAIT!* Oh, boy. Should've realized this
        #sooner. "HintSane" objects *PROBABLY* aren't an issue when we're
        #dealing with root type hints, which we are. Probably. Just strip the
        #"hint" instance variable out and ignore all of their other metadata.
        #FIXME: Calling reduce_hint() here almost certainly suffices. That said,
        #the larger issue now is that this beartype_pep557_dataclass() basically
        #accepts *NONE* of the parameters it needs to pass on to reduce_hint().
        #Should be a trivial refactoring. Sadly, we're outta time tonight. Ugh!
        #FIXME: *OH, HO*. Indeed, the core issue *NOW* is that we have no
        #type-centric concrete subclass implementing the "BeartypeCallDataABC"
        #ABC. Consequently, we'll sadly need to:
        #* In the existing "calldatadecorabc" submodule:
        #  * *DO NOT GLOBALLY* but instead *CAREFULLY MANUALLY* rename the
        #    "func_annotations" instance variable to "hintable_annotations",
        #    which will now need to generically apply to both callables *AND*
        #    types. I sigh. This requires some care. We'll need to grep the
        #    codebase for "func_annotations" and manually modify all hits that
        #    apply to "hintable_annotations". Probably most of those will be
        #    forward reference-specific, we assume. We also sigh. *sighing*
        #  * Apply a similar careful manual renaming of "func" to "hintable".
        #    For obvious reasons, this one should be even more careful. With any
        #    luck, tests will pick up any residual badness here. Ugh! Ugh! The
        #    safest way to do this would probably be to grep for:
        #    * '\bcall_curr\.func\b'.
        #    * '\bdecor_curr\.func\b'.
        #    Most other '\.func\b' matches *SHOULD* be ignorable here. Should.
        #* In the existing "calldatadecormin" submodule:
        #  * *GLOBALLY* rename the "func_scope_forward" instance variable to
        #    "hintable_scope_forward", which will now need to generically apply
        #    to both callables *AND* types. Unlike the prior rename, it is
        #    probably safe to do this globally. We still sigh. *sighing*
        #* Rename the "calldatadecor" submodule to
        #  "calldatadecorfunc". In that submodule:
        #  * Rename the "BeartypeCallDecorData" class to
        #    "BeartypeCallDecorFuncData".
        #* Define a new "calldatadecortype" submodule, probably copy-pasted from
        #  the existing "calldatadecorfunc" submodule. In this new submodule:
        #  * Define a new "BeartypeCallDecorTypeData" subclass, also subclassing
        #    the existing "BeartypeCallDecorMinimalData" subclass. The
        #    implementation should probably just define the trivial __init__()
        #    method accepting a mandatory "cls" parameter and whatever else
        #    (e.g., "cls_stack"). That should be it for now. Probably. Ugh!
        #* The big issue here is generalizing our currently callable-specific
        #  resolve_hint_pep484_ref_str_decor_curr() reducer to support both
        #  callables *AND* types. That's gonna be a bit non-trivial, folks.
        #  Specifically, we'll need to:
        #  * In the existing "beartype._util.cls.utilclstest" submodule:
        #    * Define a new is_cls_nested() tester, whose implementation
        #      should resemble:
        #          #FIXME: *DEFINITELY UNIT TEST THIS IMMEDIATELY.* Should be
        #          #trivial. Just make sure we test nested classes, obviously!
        #          @callable_cached
        #          def is_cls_nested(cls: type) -> bool:
        #              assert isinstance(cls, type), f'{repr(cls)} not class.'
        #              return '.' in cls.__qualname__
        #  * In the existing "beartype._util.utilobjtest" submodule:
        #    * Define a new is_obj_nested() tester, whose implementation
        #      should resemble:
        #          def is_obj_nested(obj: object) -> bool:
        #              # Avoid circular import dependencies.
        #              from beartype._util.cls.utilclstest import is_cls_nested
        #              from beartype._util.func.utilfunctest import is_func_nested
        #
        #              return (
        #                  is_cls_nested(obj)
        #                  if isinstance(obj, type) else
        #                  is_func_nested(obj)
        #                  if callable(obj) else
        #                  False
        #              )
        #* In the existing "fwdresolve" submodule:
        #  * Refactor resolve_hint_pep484_ref_str_decor_curr() to internally:
        #    * Refactor the call to is_func_nested() to instead call
        #      is_obj_nested() as follows:
        #          is_hintable_nested = bool(cls_stack) or is_obj_nested(hintable)
        #    * Locally rename "func_module_name" to "hintable_module_name".
        #    * Patch up everything else still referring to "func*". Ugh! Ugh!
        #* In the existing "fwdscopemake" submodule:
        #  * Refactor make_scope_forward_decor_curr() to internally:
        #    * Rename the "func_is_nested" parameter to "is_hintable_nested".
        #    * *SO MUCH BRUTALITY HERE*. This is the huge pain point. All of the
        #      introspection here assumes callables. Generalizing to also
        #      support types is definitely doable... and *MUST* be done. But
        #      it's also super non-trivial to the max. Guess we have no
        #      alternative except to slowly generalize each section piecemeal.
        #* Instantiate a new "decor_curr" local variable like so below:
        #      decor_curr = BeartypeCallDecorTypeData(
        #          cls=datacls,
        #          #FIXME: This beartype_pep557_dataclass() decorator will need
        #          #to be generalized to accept this new mandatory parameter!
        #          cls_stack=cls_stack,
        #          conf=conf,
        #      )
        #* Pass that to the sanify_hint_any() call below like so. Note that we've
        #  inspected the reduce_hint() API and are confident that this is all
        #  that's needed:
        #      from beartype._util.error.utilerrraise import reraise_exception_placeholder
        #
        #      # Attempt to...
        #      try:
        #          # With a context manager "catching" *ALL* non-fatal warnings issued
        #          # during this logic for subsequent "playback" below...
        #          with catch_warnings(record=True) as warnings_issued:
        #              # Metadata encapsulating the sanification of this hint.
        #              hint_sane = sanify_hint_any(
        #                  call_meta=decor_curr,
        #                  hint=hint,
        #                  conf=conf,
        #                  exception_prefix=EXCEPTION_PLACEHOLDER,
        #              )
        #
        #          # If one or more warnings were issued, reissue these warnings with
        #          # each placeholder substring (i.e., "EXCEPTION_PLACEHOLDER"
        #          # instance) replaced by a human-readable description of this
        #          # callable and annotated parameter.
        #          if warnings_issued:
        #              # print(f'warnings_issued: {warnings_issued}')
        #              reissue_warnings_placeholder(
        #                  warnings=warnings_issued,
        #                  #FIXME: Obviously not right. *shrug*
        #                  target_str=prefix_decor_curr_callable_arg_name(
        #                      decor_curr=decor_curr, arg_name=arg_name),
        #              )
        #          # Else, *NO* warnings were issued.
        #      # If any exception was raised, reraise this exception with each
        #      # placeholder substring (i.e., "EXCEPTION_PLACEHOLDER" instance)
        #      # replaced by a human-readable description of this callable and
        #      # annotated parameter.
        #      except Exception as exception:
        #          reraise_exception_placeholder(
        #              exception=exception,
        #              #FIXME: Obviously not right. *shrug*
        #              target_str=prefix_decor_curr_callable_arg_name(
        #                  decor_curr=decor_curr, arg_name=arg_name),
        #          )
        #
        #      # Sanified hint encapsulated by this metadata.
        #      field_hint = hint_sane.hint
        #* Add a unit test (or improve an existing one) to test that a dataclass
        #  nested inside another class can define a field annotated by a
        #  relative stringified forward reference to that outermost class. Ugh!

        # reduce_hint()  <-- UGH WHAT PARAMETERS YO

        # Add this field back to this sanified dictionary.
        field_name_to_hint[field_name] = field_hint

    # ..................{ CLOSURES                           }..................
    #FIXME: Docstring up this closure, please. *sigh*
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
        attr_hint: Hint = field_name_to_hint_get(attr_name, SENTINEL)  # type: ignore[arg-type]

        # If this dataclass attribute is annotated and thus a field...
        if attr_hint is not SENTINEL:
            # If the new value of this field violates this hint...
            #
            # Note that this is a non-negligible optimization. Technically, this
            # preliminary test is superfluous: only the call to the
            # die_if_unbearable() raiser below is required. Pragmatically, this
            # preliminary test avoids various needlessly expensive operations in
            # the common case that this value satisfies this hint.
            if not is_bearable(obj=attr_value, hint=attr_hint, conf=conf):  # pyright: ignore
                #FIXME: *UGLY LOGIC.* Sure. Technically, this works. But we
                #repeat the *EXACT* same logic in our currently unused
                #_die_if_arg_default_unbearable() validator, which we will
                #almost certainly re-enable at some point. Instead:
                #* Just add a new optional "exception_cls" parameter to the
                #  die_unless_obj_satisfies_hint() raiser called below. If
                #  necessary, the initial implementation of this parameter could
                #  just do what we currently do here. Not great, but at least
                #  that logic would be centralized away from prying eyes in the
                #  same API.

                # Modifiable keyword dictionary encapsulating this beartype
                # configuration.
                conf_kwargs = conf.kwargs.copy()

                #FIXME: This should probably be configurable as well. For now,
                #this is fine. We shrug noncommittally. We shrug, everyone!
                # Set the type of violation exception raised by the subsequent
                # call to the die_if_unbearable() function to the expected type.
                conf_kwargs['violation_door_type'] = (
                    BeartypeCallHintPep557FieldViolation)

                # New beartype configuration initialized by this dictionary.
                conf_new = BeartypeConf(**conf_kwargs)

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
                #
                # Note that the die_if_unbearable() raiser implicitly suffixes
                # this prefix by the substring "value". On the one hand, it
                # probably shouldn't be doing that. On the other hand, it
                # currently is doing that. On the gripping hand, we're too tired
                # to do anything about it doing that. This is why bugs exist.
                exception_prefix = (
                    f'Dataclass {self_repr} '
                    f'attribute {repr(attr_name)} new '
                )

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

        # If this dataclass does *NOT* directly override the superclass
        # __setattr__() dunder method with a non-default dataclass-specific
        # __setattr__() dunder method, fallback to the former. The superclass
        # __setattr__() dunder method is guaranteed to be defined on at least
        # one superclass of this dataclass. Why? Because the root superclass
        # type.__setattr__() dunder method is guaranteed to exist on all types.
        #
        # Note that:
        # * This is the common case and thus tested first.
        # * Unlike the below case, this method method is accessed via the
        #   super() builtin and is thus a true method bound to this dataclass.
        #   Ergo, the "self" parameter must *NOT* be explicitly passed.
        if datacls_setattr is None:
            super().__setattr__(attr_name, attr_value)  # type: ignore[misc]
        # Else, this dataclass directly defines a non-default dataclass-specific
        # implementation of this method overriding the superclass __setattr__()
        # dunder method. In this case, defer to this override.
        #
        # Note that, unlike the above case, this method was accessed via the
        # "__dict__" dunder dictionary and is thus an unbound function *NOT*
        # bound to this dataclass. Ergo, the "self" parameter *MUST* be
        # explicitly passed.
        else:
            datacls_setattr(self, attr_name, attr_value)

    # ..................{ DECORATORS                         }..................
    # setattr()-like callable to be called to set this attribute on this
    # dataclass, defined as either...
    setattr_func = (
        # If this dataclass is frozen, the standard setattr() builtin does *NOT*
        # suffice. Why? Because frozen dataclasses guarantee immutability by
        # overriding the __setattr__() dunder method (implicitly called by the
        # setattr() builtin) to unconditionally raise an exception. While
        # understandable, this behaviour prevents the set_type_attr() function
        # called below from monkey-patching type-checking into this dataclass;
        # attempting to do so would ironically invoke that same __setattr__()
        # dunder method, which would then raises an exception. This behaviour
        # can be circumvented by passing the type.__setattr__() dunder method as
        # this parameter, which then applies the desired monkey-patch *WITHOUT*
        # raising an exception. In short, stupid kludges is always the answer.
        type.__setattr__
        if is_pep557_dataclass_frozen(datacls) else
        # Else, this dataclass is *NOT* frozen. In this case, the standard
        # setattr() builtin, which internally defers to the __setattr__() dunder
        # method guaranteed to be defined by all dataclasses (due to the
        # existence of the type.__setattr__() dunder method).
        setattr
    )

    # Safely replace this undecorated __setattr__() implementation with this
    # decorated __setattr__() implementation.
    set_type_attr(
        cls=datacls,
        attr_name='__setattr__',
        attr_value=check_pep557_dataclass_field,
        setattr_func=setattr_func,  # pyright: ignore
    )
