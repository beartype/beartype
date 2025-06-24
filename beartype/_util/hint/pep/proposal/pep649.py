#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`649`-compliant **annotations** (i.e., ``__annotation__``
dunder dictionaries dynamically created by ``__annotate__()`` dunder methods,
mapping from the names of annotated child objects of parent hintables to the
type hints annotating those child objects).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ TODO                               }....................
#FIXME: [USABILITY] Our get_pep649_hintable_annotations() dictionary currently
#assumes that *ALL* formats except "Format.FORWARDREF" are useless. That was a
#profound API mistake. Our is_subhint() implementation for PEP 589-compliant
#"TypedDict" subclasses *ABSOLUTELY* requires an API that allows callers to
#explicitly pass this format to other members. Refactor as follows, please:
#    def get_pep649_hintable_annotations_or_none(
#        # Mandatory parameters.
#        hintable: Pep649Hintable,
#
#        # Optional keyword-only parameters.
#        *,
#        annotate_format: Format = Format.FORWARDREF,
#    ) -> Pep649HintableAnnotations:
#
#Significant (but not insurmountable) issues with that include:
#* Our Python <= 3.13 implementation has *NO* access to the
#  "annotationlib.Format.FORWARDREF" member. While we could fabricate some sort
#  of absurd fake placeholder for both this and the "annotationlib.Format"
#  enumeration, doing so would probably be overkill. Instead, just declare the
#  Python <= 3.13-version of get_pep649_hintable_annotations_or_none() as:
#      def get_pep649_hintable_annotations_or_none(
#          # Mandatory parameters.
#          hintable: Pep649Hintable,
#
#          # Optional parameters.
#          **kwarg
#      ) -> Pep649HintableAnnotations:
#  The "annotate_format" parameter has no meaning or relevance under Python <=
#  3.13. Thus, we just silently ignore it. *shrug*
#* get_pep649_hintable_annotations_or_none() should *FIRST* test whether
#  "annotate_format is Format.VALUE". If so, this getter should *IMMEDIATELY*
#  just trivially return the unmemoized value returned by get_annotations().
#  Why? Because *ALL* hintables already implicitly cache the
#  "Format.VALUE"-style value of their "__annotations__" dictionaries. Ergo, no
#  additional memoization is required. Consider this:
#      def get_pep649_hintable_annotations_or_none(
#          # Mandatory parameters.
#          hintable: Pep649Hintable,
#
#          # Optional parameters.
#          annotate_format: Format = Format.FORWARDREF,
#      ) -> Pep649HintableAnnotations:
#          # Note that we *ALWAYS* explicitly pass the desired format to the
#          # lower-level get_annotations() getter, even when this format
#          # corresponds to the current default value for this parameter. Why?
#          # Because there is *NO* guarantee that this default value will
#          # continue to be "Format.VALUE". Indeed, we strongly suspect that
#          # some subsequent CPython version will break backward compatibility
#          # by changing this default value to "Format.FORWARDREF". In other
#          # words, we profoundly lack trust in typing-centric CPython APIs.
#          # Given the prior history, this mistrust is well-founded.
#          if annotate_format is Format.VALUE:
#              return get_annotations(hintable, format=Format.VALUE)
#
#          ...
#* That still leaves two remaining formats: "Format.FORWARDREF" and
#  "Format.STRING". Our current memoization strategy assumes the former. So,
#  we'll need to generalize our memoizing data structures to account for an
#  explicit format. In other words:
#      # Instead of this and this...
#      _MODULE_NAME_TO_ANNOTATIONS: (
#          Dict[str, Optional[Pep649HintableAnnotations]]) = {}.
#      _MODULE_NAME_TO_HINTABLE_BASENAME_TO_ANNOTATIONS: (
#          Dict[str, Dict[str, Optional[Pep649HintableAnnotations]]]) = {}
#
#      # ...we want this and this.
#      _MODULE_NAME_TO_FORMAT_TO_ANNOTATIONS: (
#          Dict[str, Dict[Format, Optional[Pep649HintableAnnotations]]]) = {}
#      _MODULE_NAME_TO_HINTABLE_BASENAME_TO_FORMAT_TO_ANNOTATIONS: (
#          Dict[str,
#              Dict[str,
#                  Dict[Format,
#                      Optional[Pep649HintableAnnotations]
#                  ]
#              ]
#          ]
#      ) = {}
#* get_pep649_hintable_annotations_or_none() will then need to be refactored to
#  accommodate those significant improvements.
#* We'll also need to refactor the private
#  _get_pep649_hintable_annotations_or_none_uncached() getter accordingly.

#FIXME: [SAFETY] It's no longer safe to return mutable dictionaries from either
#get_pep649_hintable_annotations() or get_pep649_hintable_annotations_or_none().
#These getters are both memoized. Even if they weren't, PEP 649 renders
#"__annotations__" unsafe for mutation. For safety, these getters should now
#return "FrozenDict" objects. See to it, please. *sigh*

#FIXME: Also, don't neglect to *IMMEDIATELY* excise the
#@method_cached_arg_by_id decorator. Quite a facepalm there, folks.

# ....................{ IMPORTS                            }....................
from beartype.roar._roarexc import BeartypeDecorHintPep649Exception
from beartype.typing import (
    Optional,
)
from beartype._data.hint.datahinttyping import (
    Pep649Hintable,
    Pep649HintableAnnotations,
    TypeException,
)
from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_14
from beartype._util.text.utiltextlabel import label_beartypeable_kind

# ....................{ GETTERS                            }....................
#FIXME: Unit test us up, please.
def get_pep649_hintable_annotations(
    # Mandatory parameters.
    hintable: Pep649Hintable,

    # Optional parameters.
    exception_cls: TypeException = BeartypeDecorHintPep649Exception,
    exception_prefix: str = '',
) -> Pep649HintableAnnotations:
    '''
    **Annotations** (i.e., possibly empty ``__annotations__`` dunder dictionary
    mapping from the name of each annotated child object of the passed hintable
    to the type hint annotating that child object) annotating the passed
    **hintable** (i.e., ideally pure-Python object defining the
    ``__annotations__`` dunder attribute as well as the :pep:`649`-compliant
    ``__annotate__`` dunder method if the active Python interpreter targets
    Python >= 3.14) if this hintable defines the ``__annotations__`` dunder
    dictionary *or* raise an exception otherwise (i.e., if this hintable fails
    to define the ``__annotations__`` dunder dictionary).

    Parameters
    ----------
    hintable : Pep649Hintable
        Hintable to be inspected.
    exception_cls : TypeException, default: BeartypeDecorHintPep649Exception
        Type of exception to be raised in the event of a fatal error. Defaults
        to :exc:`.BeartypeDecorHintPep649Exception`.
    exception_prefix : str, default: ''
        Human-readable substring prefixing raised exception messages. Defaults
        to the empty string.

    Returns
    -------
    Pep649HintableAnnotations
        ``__annotations__`` dunder dictionary set on this hintable.

    Raises
    ------
    exception_cls
         If this hintable fails to define the ``__annotations__`` dunder
         dictionary. Since *all* pure-Python hintables (including unannotated
         hintables) define this dictionary, this getter raises an exception only
         if the passed hintable is either:

         * *Not* actually a hintable.
         * A **pseudo-callable object** (i.e., otherwise uncallable object whose
           class renders all instances of that class callable by defining the
           ``__call__()`` dunder method).
    '''

    # "__annotations__" dictionary dictionary defined by this hintable if this
    # hintable is actually a hintable *OR* "None" otherwise.
    hint_annotations = get_pep649_hintable_annotations_or_none(hintable)

    # If this hintable is *NOT* actually a hintable, raise an exception.
    if hint_annotations is None:
        assert isinstance(exception_cls, type), (
            f'{repr(exception_cls)} not class.')
        assert issubclass(exception_cls, Exception), (
            f'{repr(exception_cls)} not exception subclass.')
        assert isinstance(exception_prefix, str), (
            f'{repr(exception_prefix)} not string.')

        # Raise a human-readable exception.
        raise exception_cls(
            f'{exception_prefix}'
            f'{label_beartypeable_kind(hintable)} {repr(hintable)} '  # type: ignore[type-var]
            f'not annotatable by type hints '
            f'(i.e., PEP 649 "__annotate__" and "__annotations__" '
            f'dunder attributes undefined).'
        )
    # Else, that hintable is a hintable.

    # Return this dictionary.
    return hint_annotations

# ....................{ VERSIONS                           }....................
# If the active Python interpreter targets Python >= 3.14...
if IS_PYTHON_AT_LEAST_3_14:
    # ....................{ IMPORTS                        }....................
    # Defer version-specific imports.
    from annotationlib import (  # type: ignore[import-not-found]
        Format,
        get_annotations,
    )
    from beartype.typing import Dict
    from beartype._cave._cavefast import (
        CallableOrClassTypes,
        ModuleType,
    )
    from beartype._data.kind.datakindiota import SENTINEL
    from beartype._util.module.utilmodget import (
        get_module_name,
        get_object_module_name_or_none,
    )
    from beartype._util.utilobject import get_object_basename_scoped

    # ....................{ CLEARERS                       }....................
    #FIXME: Unit test us up, please.
    def clear_pep649_caches() -> None:

        # Clear all dictionary globals declared below.
        _MODULE_NAME_TO_ANNOTATIONS.clear()
        _MODULE_NAME_TO_HINTABLE_BASENAME_TO_ANNOTATIONS.clear()

    # ....................{ GETTERS                        }....................
    #FIXME: Unit test us up, please.
    # Note that this getter is memoized *ONLY* under Python >= 3.14. Why?
    # Because the lower-level annotationlib.get_annotations() getter underlying
    # this higher-level getter *ONLY* memoizes the annotations dictionary it
    # creates and returns when passed the "format=Format.VALUE" keyword
    # parameter. When passed *ANY* other "format" value,
    # annotationlib.get_annotations() avoids avoids caching its return value.
    # Creating this return value is algorithmically non-trivial and expensive.
    # Sadly, we are effectively required to memoize this return value here.
    def get_pep649_hintable_annotations_or_none(
        hintable: Pep649Hintable) -> Optional[Pep649HintableAnnotations]:

        # If this hintable is either a callable *OR* class...
        #
        # Note that almost all hintables of interest are either callables or
        # classes. This common case is intentionally detected first for speed.
        if isinstance(hintable, CallableOrClassTypes):
            # Fully-qualified name of the module defining this hintable if any
            # *OR* "None" otherwise (e.g., if this hintable is defined in-memory
            # outside a module namespace).
            module_name = get_object_module_name_or_none(hintable)

            # If a module defines this hintable...
            if module_name:
                # Dictionary mapping from the lexically scoped name of each
                # hintable defined by this module previously memoized by a prior
                # call to this getter if any *OR* the sentinel otherwise (i.e.,
                # if this getter has yet to be passed such a hintable).
                hintable_basename_to_annotations = (
                    _MODULE_NAME_TO_HINTABLE_BASENAME_TO_ANNOTATIONS.get(
                        module_name, SENTINEL))

                # If such a dictionary was *NOT* memoized...
                if hintable_basename_to_annotations is SENTINEL:
                    # Default this dictionary to a new empty dictionary,
                    # additionally memoized into this global cache for speed.
                    hintable_basename_to_annotations = (
                        _MODULE_NAME_TO_HINTABLE_BASENAME_TO_ANNOTATIONS[
                            module_name]) = {}
                # Else, this dictionary was memoized.
                #
                # In either case, this dictionary now exists.

                # Lexically scoped name of this hintable excluding the
                # fully-qualified name of the module defining this hintable.
                hintable_basename = get_object_basename_scoped(hintable)

                # "__annotations__" dunder dictionary for this module previously
                # memoized by a prior call to this getter if any *OR* the
                # sentinel otherwise (i.e., if this getter has yet to be passed
                # this module).
                hintable_annotations = hintable_basename_to_annotations.get(  # type: ignore[union-attr]
                    hintable_basename, SENTINEL)

                # If such a dictionary was memoized, return this dictionary.
                if hintable_annotations is not SENTINEL:
                    return hintable_annotations  # type: ignore[return-value]
                # Else, *NO* such dictionary was memoized.

                # "__annotations__" dunder dictionary for this hintable.
                hintable_annotations = (
                    _get_pep649_hintable_annotations_or_none_uncached(hintable))

                # Cache this dictionary under this hintable's basename.
                hintable_basename_to_annotations[hintable_basename] = (  # type: ignore[index]
                    hintable_annotations)

                # Return this dictionary.
                return hintable_annotations
            # Else, *NO* module defines this hintable. In this case, fallback to
            # unmemoized behaviour. Although non-ideal, a hintable residing
            # outside a module arguably constitutes an erroneous edge case that
            # should generally *NEVER* occur. Optimizing this is *NOT* worth it.
        # Else, this hintable is neither a callable *NOR* class.
        #
        # If this hintable is a module...
        elif isinstance(hintable, ModuleType):
            # Fully-qualified name of this module.
            module_name = get_module_name(hintable)

            #FIXME: [SPEED] Globalize this getter for efficiency, please. *sigh*
            # "__annotations__" dunder dictionary for this module previously
            # memoized by a prior call to this getter if any *OR* the sentinel
            # otherwise (i.e., if this getter has yet to be passed this module).
            module_annotations = _MODULE_NAME_TO_ANNOTATIONS.get(
                module_name, SENTINEL)

            # If such a dictionary was memoized, return this dictionary.
            if module_annotations is not SENTINEL:
                return module_annotations  # type: ignore[return-value]
            # Else, *NO* such dictionary was memoized.

            # "__annotations__" dunder dictionary for this module.
            module_annotations = (
                _get_pep649_hintable_annotations_or_none_uncached(hintable))

            # Cache this dictionary under this module's fully-qualified name.
            _MODULE_NAME_TO_ANNOTATIONS[module_name] = module_annotations

            # Return this dictionary.
            return module_annotations
        # Else, this hintable is an unknown type of object.

        # Fallback to the unmemoized getter underlying this memoized getter.
        # Although non-ideal, the only general-purpose alternative would be to
        # memoize a reference to this object, preventing this object from *EVER*
        # being garbage-collected, inviting memory leaks. In other words, there
        # exist *NO* safe means of memoizing arbitrary user-defined objects.
        return _get_pep649_hintable_annotations_or_none_uncached(hintable)

    # ....................{ SETTERS                        }....................
    #FIXME: Unit test us up, please.
    def set_pep649_hintable_annotations(
        # Mandatory parameters.
        hintable: Pep649Hintable,
        annotations: Pep649HintableAnnotations,

        # Optional parameters.
        exception_cls: TypeException = BeartypeDecorHintPep649Exception,
        exception_prefix: str = '',
    ) -> None:
        assert isinstance(annotations, dict), (
            f'{repr(annotations)} not dictionary.')
        assert all(
            isinstance(annotations_key, str) for annotations_key in annotations
        ), f'{repr(annotations)} not dictionary mapping names to type hints.'

        # If this hintable is *NOT* actually a hintable, raise an exception.
        # Amusingly, the simplest means of implementing this validation is to
        # simply retrieve the prior "__annotations__" dunder dictionary
        # currently set on this hintable.
        get_pep649_hintable_annotations(
            hintable=hintable,
            exception_cls=exception_cls,
            exception_prefix=exception_prefix,
        )
        # Else, this hintable is actually a hintable defining the requisite pair
        # of PEP 649- and 749-compliant dunder attributes:
        # * __annotate__().
        # * "__annotations__"

        # Existing __annotate__() dunder method set on this hintable if any *OR*
        # "None" otherwise (e.g., if an external caller has already explicitly
        # set the "__annotations__" dunder attribute on this hintable, which
        # implicitly sets the __annotate__() dunder method to "None").
        original_hintable_annotate = getattr(hintable, '__annotate__', None)

        def beartype_hintable_annotate(
            self, annotate_format: Format) -> Pep649HintableAnnotations:
            f'''
            Hintable {repr(hintable)} :pep:`649`- and :pep:`749`-compliant
            ``__annotate__()`` dunder method, modifying the user-defined
            ``__annotations__`` dunder dictionary for this hintable with
            :mod:`beartype`-specific improvements.

            These improvements include:

            * **Memoization** (i.e., caching) across root type hints, reducing
              space consumption.
            * :pep:`563`-compliant conversion of unquoted forward references
              under the ``from __future__ import annotations`` pragma into
              equivalent :mod:`beartype`-specific **forward reference proxies**
              (i.e., objects transparently proxying undefined types).

            Parameters
            ----------
            annotate_format : Format
                Kind of annotation format to be returned. See also :pep:`649`
                and :pep:`749` for further details.

            Returns
            -------
            Pep649HintableAnnotations
                New ``__annotations__`` dunder dictionary set on this hintable.
            '''

            #FIXME: [SPEED] Globalize access to frequently accessed "Format"
            #members and reference those globals instead below. This method
            #*COULD* be frequently called enough to warrant micro-optimization.

            #FIXME: *NO*. Sadly, it turns out that the "Format.VALUE" format has
            #demonstrable real-world value. See our is_subhint() implementation
            #for PEP 589-compliant "TypedDict" subclasses, which *ABSOLUTELY*
            #requires this format. Succinctly, the "Format.VALUE" format enables
            #callers to detect whether an annotations dictionary contains one or
            #more unquoted forward references, which then enables callers to
            #conditionally modify runtime behaviour accordingly.
            #
            #In other words:
            #* Excise the "_ANNOTATE_FORMATS_VALUELIKE" set global, which no
            #  longer has any demonstrable value. (Get it, "value"? Ugh.)
            #* Refactor this implementation to resemble:
            #      if annotate_format is Format.FORWARDREF:
            #          return annotations
            #      elif original_hintable_annotate is not None:
            #          return original_hintable_annotate(annotate_format)
            #
            #      raise NotImplementedError()
            #
            #Surprisingly trivial, actually. That's a bit simpler but more
            #broadly useful and specific than the current heavy-handed tactic.

            # If the caller requested a value-like format, trivially return the
            # "__annotations__" dunder dictionary passed to the parent
            # set_pep649_hintable_annotations() setter of this closure.
            #
            # If this dictionary contains:
            # * *NO* unquoted forward references, this dictionary already
            #   complies with the "Format.VALUE" format.
            # * One or more unquoted forward references, this dictionary
            #   already complies with the "Format.FORWARDREF" format. Why? A
            #   complex and non-obvious chain of casuistry. Bear with us. If
            #   this dictionary did *NOT* already comply with the
            #   "Format.FORWARDREF" format, then (by process of elimination)
            #   this dictionary *MUST* at least comply with the "Format.VALUE"
            #   format. However, since this dictionary contains unquoted forward
            #   references, the annotationlib.get_annotations() getter would
            #   have raised a "NameError" exception when attempting to return
            #   this dictionary under the "Format.VALUE" format, in which case
            #   this dictionary could *NOT* possibly exist. Clearly, however,
            #   this dictionary exists. Since this is an obvious contradiction,
            #   this dictionary *MUST* necessarily already comply with the
            #   "Format.FORWARDREF" format.
            #
            # There now exist four possible cases:
            # * The caller passed "Format.VALUE" and this dictionary already
            #   complies with the "Format.VALUE" format. *WONDERFUL!*
            # * The caller passed "Format.FORWARDREF" and this dictionary
            #   complies with the "Format.FORWARDREF" format. *WONDERFUL!*
            # * The caller passed "Format.FORWARDREF" and this dictionary only
            #   complies with the "Format.VALUE" format, which implies this
            #   dictionary contains *NO* unquoted forward references. Since the
            #   "Format.FORWARDREF" format simply reduces to "Format.VALUE" if a
            #   dictionary contains *NO* unquoted forward references, this case
            #   is still *WONDERFUL!*
            # * The caller passed "Format.VALUE" and this dictionary actually
            #   complies with the "Format.FORWARDREF" format instead.
            #   Unsurprisingly, this case is awkward. If the caller passed
            #   "Format.VALUE", they presumably expect this __annotate__()
            #   function to raise a "NameError" exception if this dictionary
            #   contains unquoted forward references. This dictionary actually
            #   complies with the "Format.FORWARDREF" format and thus actually
            #   contains unquoted forward references. Sadly, there is *NO*
            #   efficient means of differentiating this case from the case in
            #   which this dictionary contains *NO* unquoted forward references.
            #   Even if an efficient means did exist, there would still exist
            #   *NO* reason to do so. The "Format.VALUE" format has little to
            #   *NO* intrinsic value in and of itself. The only reason that
            #   "Format.VALUE" exists is to inform the high-level
            #   call_annotate_function() and get_annotations() functions defined
            #   by the standard "annotationslib" module that this dictionary
            #   contains unquoted forward references, which then respond by
            #   wrapping unquoted forward references in "ForwardRef" proxies to
            #   comply with the "Format.FORWARDREF" format. But this dictionary
            #   already complies with this format! In this case, no further work
            #   is required or desired. This __annotate__() monkey-patch thus
            #   intentionally conflates the largely useless "Format.VALUE"
            #   format with the largely useful "Format.FORWARDREF" format.
            #   Although not exactly wonderful, this approach is the best that
            #   we can reasonably do without rendering this API insane.
            if annotate_format in _ANNOTATE_FORMATS_VALUELIKE:
                return annotations
            # Else, the caller did *NOT* request a value-like format.
            #
            # If...
            elif (
                # The caller requested the documentation-oriented string
                # format *AND*...
                annotate_format is Format.STRING and
                # An existing __annotate__() dunder method is set on this
                # hintable...
                original_hintable_annotate is not None
            ):
                # Then defer to the existing __annotate__() dunder method set on
                # this hintable. While this beartype-specific monkey-patch of
                # that method *COULD* attempt to manually redefine this format
                # without simply deferring to that method, doing so would be
                # both non-trivial and undesirable. Callers requesting
                # documentation are ultimately requesting human-readable string
                # representations of the *ORIGINAL* type hints annotating this
                # hintable. Those type hints are what the third-party packages
                # defining those hintables intended those hintables to be
                # annotated as. Those type hints embody those intentions, thus
                # constituting the most readable description of those hintables.
                return original_hintable_annotate(annotate_format)
            # Else, the caller either requested an unknown format *OR* no
            # existing __annotate__() dunder method is set on this hintable.
            #
            # In the latter case, this beartype-specific implementation of that
            # method *MUST* either:
            # * Attempt to manually redefine this format. Although feasible,
            #   doing so would be both non-trivial and undesirable. See above
            #   for further discussion.
            # * Raise the builtin "NotImplementedError" exception. The caller is
            #   then expected to manually implement this format. Thankfully, the
            #   high-level call_annotate_function() and get_annotations()
            #   functions defined by the standard "annotationslib" module do
            #   just that; they explicitly catch this exception and respond by
            #   manually implementing the "Format.STRING" format in the expected
            #   way. This is the only sane solution.
            #
            # Unsurprisingly, we opt for the latter approach by simply falling
            # through to the fallback defined below.

            # Notify the caller that this __annotate__() implementation fails to
            # support this format by raising a "NotImplementedError" exception.
            #
            # Note that:
            # * PEP 649 itself encourages user-defined __annotate__()
            #   implementations to raise bare "NotImplementedError" exceptions
            #   lacking messages. Indeed, the call_annotate_function() and
            #   get_annotations() functions trivially catch these exceptions and
            #   ignore associated messages.
            # * PEP 749 explicitly instructs user-defined __annotate__()
            #   implementations to raise "NotImplementedError" exceptions when
            #   passed the private "Format.VALUE_WITH_FAKE_GLOBALS" format:
            #       Users who manually write annotate functions should raise
            #       NotImplementedError if the VALUE_WITH_FAKE_GLOBALS format is
            #       requested, so the standard library will not call the
            #       manually written annotate function with “fake globals”,
            #       which could have unpredictable results.
            raise NotImplementedError()

        # Attempt to silently replace this hintable's existing __annotate__()
        # dunder method with this new beartype-specific monkey-patch.
        try:
            hintable.__annotate__ = beartype_hintable_annotate  # type: ignore[union-attr]
        # If doing so fails with an exception resembling the following, this
        # hintable is *NOT* pure-Python. The canonical example are C-based
        # decorator objects (e.g., class, property, or static method
        # descriptors), whose exception message reads:
        #     AttributeError: 'method' object has no attribute '__annotate__'
        #     and no __dict__ for setting new attributes. Did you mean:
        #     '__getstate__'?
        #
        # C-based decorator objects only define:
        # * A read-only __annotate__() dunder method that proxies an original
        #   writeable __annotate__() dunder method of the pure-Python callables
        #   they originally decorated.
        # * A read-only "__annotations__" dunder attribute that proxies an
        #   original writeable "__annotations__" dunder attribute of the
        #   pure-Python callables they originally decorated.
        #
        # Detecting this edge case is non-trivial and most easily deferred to
        # this late time. While non-ideal, simplicity >>>> idealism here.
        except AttributeError as exception:
            # Lower-level presumably pure-Python callable wrapped by this
            # higher-level presumably C-based decorator object if this decorator
            # object wraps such a callable *OR* "None" otherwise (i.e., if this
            # object does *NOT* wrap such a callable).
            #
            # Note that this callable is intentionally accessed as the
            # "__func__" dunder attribute on this decorator object, as the
            # following standard decorator objects *ALL* wrap their decorated
            # callables with this attribute:
            # * Bound instance method descriptors.
            # * @classmethod-decorated class method descriptors.
            # * @staticmethod-decorated static method descriptors.
            #
            # See also the "beartype._util.func.utilfuncwrap" submodule.
            hintable_func = getattr(hintable, '__func__', None)

            #FIXME: File an upstream CPython issue about this, please. *sigh*
            #FIXME: Remove this edge case *AFTER* some future Python version
            #fully satisfies PEP 749 by implementing this paragraph:
            #    The constructors for classmethod() and staticmethod() currently
            #    copy the __annotations__ attribute from the wrapped object to
            #    the wrapper. They will instead have writable attributes for
            #    __annotate__ and __annotations__. Reading these attributes will
            #    retrieve the corresponding attribute from the underlying
            #    callable and cache it in the wrapper’s __dict__. Writing to
            #    these attributes will directly update the __dict__, without
            #    affecting the wrapped callable.
            #
            #Currently, Python does *NOT* do that. Neither the __annotate__()
            #nor "__annotate__" dunder attributes are settable on @classmethod
            #or @staticmethod descriptors:
            #    class Yum(object):
            #        @classmethod
            #        def guh(cls) -> None: pass
            #
            #    def ugh_annotate(): return {}
            #
            #    yim = Yum()
            #    print(Yum.guh.__annotate__)          # <-- reading this works
            #    Yum.guh.__annotate__ = ugh_annotate  # <-- writing this fails
            #
            #The above example currently raises:
            #    AttributeError: 'method' object has no attribute '__annotate__'
            #    and no __dict__ for setting new attributes. Did you mean:
            #    '__getstate__'?
            #
            #Presumably, Python will start doing that at some point. Once Python
            #does, this issue becomes a non-issue. For the moment, efficiency is
            #irrelevant. We just need this to work for a temporary span of time.

            # If...
            if (
                # This higher-level presumably C-based decorator object wraps a
                # lower-level presumably pure-Python callable *AND*...
                hintable_func is not None and
                # This decorator object does *NOT* wrap itself...
                #
                # Note that:
                # * This edge case should never occur. Indeed, if this
                #   decorator object is one of the standard decorator objects
                #   listed above, this edge case is guaranteed to *NOT* occur.
                # * This identity test is a Poor Man's Recursion Guard. Clearly,
                #   this identity test does *NOT* actually constitute a
                #   recursion guard. Implementing a "true" recursion guard would
                #   require tracking a set of all previously seen hintables
                #   across recursive calls. Since it's unclear whether this edge
                #   case will even arise in practice, it's unclear whether the
                #   effort is worth investing in a "true" recursion guard. For
                #   the moment, the Poor Man's Recursion Guard suffices...
                hintable_func is not hintable
            ):
                # Then attempt to set this annotations dictionary on this
                # lower-level presumably pure-Python callable instead.
                return set_pep649_hintable_annotations(
                    hintable=hintable_func,
                    annotations=annotations,
                    exception_cls=exception_cls,
                    exception_prefix=exception_prefix,
                )
            # Else, either this higher-level presumably C-based decorator object
            # does not wrap a lower-level presumably pure-Python callable *OR*
            # this decorator object wraps itself. In either case, unwrapping
            # this decorator object would be harmful. Avoid doing so.

            # If the "__annotations__" dunder attribute of this hintable is
            # *NOT* a dictionary, this dunder attribute has *PROBABLY* been
            # nullified to "None", *PROBABLY* due to another decorator having
            # previously set the __annotate__() dunder method of the presumably
            # pure-Python callable underlying this C-based decorator object.
            # Yes, there are a lot of assumptions *PROBABLY* happening here.
            # The only remaining means of setting the passed annotations
            # dictionary on this hintable would be to set the "__annotations__"
            # dunder attribute to this dictionary. However, attempting to set
            # the __annotate__() dunder method raised an "AttributeError"!
            # Ergo, attempting to set the "__annotations__" dunder dictionary
            # would almost certainly raise the same exception. Since there exist
            # *NO* remaining means of setting the passed annotations dictionary
            # on this hintable, we have *NO* recourse but to notify the caller
            # of this modern tragedy by raising an exception.
            if not isinstance(hintable.__annotations__, dict):
                raise exception_cls(
                    f'{exception_prefix}'
                    f'{label_beartypeable_kind(hintable)} {repr(hintable)} '  # type: ignore[type-var]
                    f'type hints not settable to '
                    f'annotations dictionary {repr(annotations)} '
                    f'(i.e., PEP 649 "__annotate__" and "__annotations__" '
                    f'dunder attributes not settable, but "__annotations__" '
                    f'dunder attribute already set to '
                    f'non-dictionary value {repr(hintable.__annotations__)}).'
                ) from exception
            # Else, the "__annotations__" dunder attribute of this hintable is a
            # dictionary.

            # For the name of each annotated attribute of this hintable and the
            # new hint which which to annotate this attribute, overwrite the
            # prior hint originally annotating this attribute with this new
            # hint.
            #
            # Note that:
            # * The above assignment is an efficient O(1) operation and thus
            #   intentionally performed first.
            # * This iteration-based assignment is an inefficient O(n) operation
            #   (where "n" is the number of annotated attributes of this
            #   hintable) and thus intentionally performed last here.
            for attr_name, attr_hint in annotations.items():
                hintable.__annotations__[attr_name] = attr_hint

    # ....................{ PRIVATE ~ globals              }....................
    _ANNOTATE_FORMATS_VALUELIKE = frozenset((Format.FORWARDREF, Format.VALUE,))
    '''
    Frozen set of all :class:`.Format` enumeration members that are
    **value-like** (i.e., which cause ``__annotate__()`` dunder methods passed
    these members to return standard ``__annotations__`` dunder dictionaries
    mapping from the names of hintable attributes to the type hints annotating
    those attributes).
    '''

    # ....................{ PRIVATE ~ globals : dict       }....................
    _MODULE_NAME_TO_ANNOTATIONS: (
        Dict[str, Optional[Pep649HintableAnnotations]]) = {}
    '''
    Dictionary mapping from the fully-qualified name of each module defining one
    or more global variables annotated by type hints to that module's **memoized
    annotations dictionary** (i.e., dictionary from the name of each such global
    variable to the type hint annotating that global variable as returned by the
    :func:`.get_pep649_hintable_annotations_or_none` getter when passed that
    module).
    '''


    _MODULE_NAME_TO_HINTABLE_BASENAME_TO_ANNOTATIONS: (
        Dict[str, Dict[str, Optional[Pep649HintableAnnotations]]]) = {}
    '''
    Dictionary mapping from the fully-qualified name of each module to a nested
    dictionary mapping from the unqualified basename of each:

    * Callable in that module accepting one or more parameters annotated by type
      hints and/or returning a value annotated by a type hint to that callable's
      **memoized annotations dictionary** (i.e., dictionary from the name of
      each such parameter or return to the type hint annotating that parameter
      or return as returned by the
      :func:`.get_pep649_hintable_annotations_or_none` getter when passed that
      callable).
    * Class in that module defining one or more class variables annotated by
      type hints to that class' **memoized annotations dictionary** (i.e.,
      dictionary from the name of each such class variable to the type hint
      annotating that class variable as returned by the
      :func:`.get_pep649_hintable_annotations_or_none` getter when passed that
      class).
    '''

    # ....................{ PRIVATE ~ getters              }....................
    def _get_pep649_hintable_annotations_or_none_uncached(
        hintable: Pep649Hintable) -> Optional[Pep649HintableAnnotations]:
        '''
        **Unmemoized annotations** (i.e., possibly empty ``__annotations__``
        dunder dictionary mapping from the name of each annotated child object
        of the passed hintable to the type hint annotating that child object)
        annotating the passed **hintable** (i.e., ideally pure-Python object
        defining the ``__annotations__`` dunder attribute as well as the
        :pep:`649`-compliant ``__annotate__`` dunder method if the active Python
        interpreter targets Python >= 3.14) if this hintable defines the
        ``__annotations__`` dunder dictionary *or* :data:`None` otherwise (i.e.,
        if this hintable fails to define the ``__annotations__`` dunder
        dictionary).

        This getter exhibits non-amortized worst-case :math:`O(n)` linear time
        complexity for :math:`n` the total number of unquoted forward references
        across all type hints annotating this hintable.

        Parameters
        ----------
        hintable : Pep649Hintable
            Hintable to be inspected.

        Returns
        -------
        Optional[Pep649HintableAnnotations]
            Either:

            * If this hintable is actually a hintable, the ``__annotations__``
              dunder dictionary set on this hintable.
            * Else, :data:`None`.
        '''

        #FIXME: *NO*. The current implementation is unsafe. Instead, we *MUST*
        #always defer to get_annotations() as follows:
        #    return (
        #        get_annotations(hintable, format=Format.FORWARDREF)
        #        if (
        #            getattr(hintable, '__annotate__', None) is not None or
        #            getattr(hintable, '__annotations__', None) is not None or
        #        ) else
        #        None
        #    )
        #
        #Refactor the current implementation to resemble the above while
        #preserving existing deep commentary, please. *sigh*

        # If the passed hintable defines the PEP 649-compliant __annotate__()
        # dunder method to be anything *OTHER* than "None", this hintable is
        # expected to be annotated by one or more type hints.
        #
        # Note that:
        # * The __annotate__() dunder method is guaranteed to exist *ONLY* for
        #   standard pure-Python hintables. Various other hintables of interest
        #   (e.g., functions exported by the standard "operator" module) do
        #   *NOT* necessarily declare this method. Since this getter is commonly
        #   called in general-purpose contexts where this guarantee does
        #   *NOT* necessarily hold, we intentionally access this attribute
        #   safely albeit somewhat more slowly via getattr().
        # * PEP 649 explicitly supports external nullification of this method
        #   (i.e., setting this attribute to "None"). Indeed, PEP 649 explicitly
        #   requires nullification as a means of efficiently declaring a
        #   hintable to be unannotated:
        #       If an object has no annotations, __annotate__ should be
        #       initialized to None, rather than to a function that returns
        #       an empty dict.
        # * The __annotate__() dunder method and "__annotations__" dunder
        #   dictionary invalidate one another. Setting one nullifies the other:
        #       * Setting o.__annotate__ to a callable invalidates the cached
        #         annotations dict.
        #       * Setting o.__annotations__ to a legal value automatically sets
        #         o.__annotate__ to None.
        #   Thus, the __annotate__() dunder method being "None" does *NOT* imply
        #   this hintable to be unannotated. The "__annotations__" dunder
        #   attribute may be a non-"None" non-empty dictionary, in which case
        #   this hintable would be annotated. Where annotations are concerned,
        #   there are now multiple sources of objective truth. This is awful.
        # * The get_annotations() getter called below safely accepts the
        #   "Format.FORWARDREF" format *ONLY* when this hintable defines the
        #   __annotate__() dunder method. If this hintable does *NOT* define
        #   __annotate__() and get_annotations() is passed "Format.FORWARDREF",
        #   then get_annotations() raises either:
        #   * If this hintable at least defines the "__annotations__" dunder
        #     dictionary but this dictionary contains one or more unquoted
        #     forward references, a "NameError" exception.
        #   * Else, a "TypeError" exception.
        #   However, this higher-level getter is designed exactly to avoid
        #   raising these sorts of exceptions! Ergo, get_annotations() is safely
        #   callable only when the __annotate__() dunder method exists.
        if getattr(hintable, '__annotate__', None) is not None:
            # Defer to the PEP 649-compliant high-level
            # annotationlib.get_annotations() getter internally deferring to the
            # PEP 649-compliant low-level __annotate__() dunder callable rather
            # than the PEP 484-compliant "__annotations__" dunder attribute.
            # Why? Because the latter reduces to calling
            # "get_annotations(hintable, format=Format.VALUE)", which raises a
            # "NameError" exception if the passed hintable is annotated by one
            # or more unquoted forward references. This is unacceptable API
            # design. Yet, this is Python >= 3.14.
            #
            # Note that:
            # * get_annotations() is guaranteed to *NEVER* return "None". If
            #   the __annotate__() dunder method and "__annotations__" dunder
            #   attribute are both "None", then get_annotations() raises a
            #   "TypeError" exception. However, get_annotations() is the
            #   canonical means of retrieving annotations under Python >= 3.14.
            #   Thus, we infer that at most one of but *NOT* both of
            #   __annotate__() and "__annotations__" may be "None".
            # * get_annotations() is guaranteed to *ALWAYS* return a dictionary.
            #   In fact:
            #   * If the "__annotations__" dunder attribute contains one or more
            #     unquoted forward references, the returned dictionary is
            #     guaranteed to be a new dictionary.
            #   * Else, the returned dictionary is guaranteed to be the same
            #     value as that of "__annotations__".
            return get_annotations(hintable, format=Format.FORWARDREF)
        # Else, this hintable does *NOT* define __annotate__().

        # Return either the PEP 484-compliant "__annotations__" dunder attribute
        # if this hintable defines this attribute *OR* "None" otherwise
        # (i.e., if this hintable fails to define this attribute).
        #
        # Note that:
        # * The "__annotations__" dunder attribute is guaranteed to exist *ONLY*
        #   for standard pure-Python hintables. See above for further details.
        # * The "__annotations__" dunder attribute is expected to either:
        #   * If this hintable actually is a hintable, be non-"None". Why?
        #     Because the __annotate__() dunder method was "None". By the logic
        #     given above, it should *NEVER* be the case that both
        #     __annotate__() and "__annotations__" are "None". However,
        #     __annotate__() was "None". It follows that "__annotations__"
        #     should now be non-"None" (and thus a valid dictionary).
        #   * Else, *NOT* exist. Ideally, unhintable objects should *NEVER*
        #     define the "__annotations__" dunder attribute.
        #   Ergo, it follows that this getter returns "None" *ONLY* when this
        #   hintable is not actually a hintable. Phew! Sanity is preserved.
        # * The "__annotations__" dunder attribute is *NOT* safely accessible
        #   under Python >= 3.14 in the worst case. If this dictionary contains
        #   one or more type hints subscripted by one or more unquoted forward
        #   references, then directly accessing this attribute is guaranteed to
        #   raise a non-human-readable "NameError" exception. Consequently, we
        #   perform this unsafe fallback *ONLY* when the __annotate__() dunder
        #   method does *NOT* exist. Although non-ideal, PEP 649 explicitly
        #   permits callers to set this attribute -- presumably as an unsafe
        #   means of preserving backward compatibility. That would be fine,
        #   except that setting this attribute nullifies and thus destroys any
        #   previously set __annotate__() dunder method! Again:
        #       * Setting o.__annotations__ to a legal value automatically sets
        #         o.__annotate__ to None.
        # * The "__annotations__" dunder attribute and __annotate__() dunder
        #   method are strongly coupled. If one is defined, the other should
        #   be defined. If one is undefined, the other should be undefined.
        #   Ergo, it should *NEVER* be the case that the __annotate__() dunder
        #   method is undefined but the "__annotations__" dunder attribute is.
        #   Ergo, this edge case should *NEVER* arise. Naturally, this edge case
        #   will often arise. Why? Because nothing prevents third-party packages
        #   from manually defining "__annotations__" dunder attributes on
        #   arbitrary objects. Although CPython *COULD* prohibit that (e.g., by
        #   defining the "object.__annotations__" descriptor to do just that),
        #   CPython currently does *NOT* prohibit that. In fact, no
        #   "object.__annotations__" descriptor currently exists to even do so.
        return getattr(hintable, '__annotations__', None)
# Else, the active Python interpreter targets Python <= 3.13. In this case,
# trivially defer to the PEP 484-compliant "__annotations__" dunder attribute.
else:
    # ....................{ CLEARERS                       }....................
    def clear_pep649_caches() -> None:
        pass

    # ....................{ GETTERS                        }....................
    def get_pep649_hintable_annotations_or_none(
        hintable: Pep649Hintable) -> Optional[Pep649HintableAnnotations]:

        # Return either the PEP 484-compliant "__annotations__" dunder attribute
        # if the passed hintable defines this attribute *OR* "None" otherwise
        # (i.e., if this hintable fails to define this attribute).
        #
        # Note that the "__annotations__" dunder attribute is guaranteed to
        # exist *ONLY* for standard pure-Python hintables. Various other
        # hintables of interest (e.g., functions exported by the standard
        # "operator" module) do *NOT* necessarily declare this attribute. Since
        # this getter is commonly called in general-purpose contexts where this
        # guarantee does *NOT* necessarily hold, we intentionally access this
        # attribute safely albeit somewhat more slowly via getattr().
        return getattr(hintable, '__annotations__', None)

    # ....................{ SETTERS                        }....................
    def set_pep649_hintable_annotations(
        # Mandatory parameters.
        hintable: Pep649Hintable,
        annotations: Pep649HintableAnnotations,

        # Optional parameters.
        exception_cls: TypeException = BeartypeDecorHintPep649Exception,
        exception_prefix: str = '',
    ) -> None:
        assert isinstance(annotations, dict), (
            f'{repr(annotations)} not dictionary.')
        assert all(
            isinstance(annotations_key, str) for annotations_key in annotations
        ), f'{repr(annotations)} not dictionary mapping names to type hints.'

        # If this hintable is *NOT* actually a hintable, raise an exception.
        # Amusingly, the simplest means of implementing this validation is to
        # simply retrieve the prior "__annotations__" dunder dictionary
        # currently set on this hintable.
        get_pep649_hintable_annotations(
            hintable=hintable,
            exception_cls=exception_cls,
            exception_prefix=exception_prefix,
        )
        # Else, this hintable is actually a hintable.

        # Attempt to...
        try:
            # Atomically (i.e., all-at-once) replace this hintable's existing
            # "__annotations__" dunder dictionary with these new annotations. Do
            # so atomically for both safety and efficiency.
            hintable.__annotations__ = annotations
        # If doing so fails with an exception resembling the following, this
        # hintable is *NOT* pure-Python. The canonical example are C-based
        # decorator objects (e.g., class, property, or static method
        # descriptors), whose exception message reads:
        #     AttributeError: 'method' object has no attribute '__annotations__'
        #
        # C-based decorator objects define a read-only "__annotations__" dunder
        # attribute that proxies an original writeable "__annotations__" dunder
        # attribute of the pure-Python callables they originally decorated.
        # Detecting this edge case is non-trivial and most easily deferred to
        # this late time. While non-ideal, simplicity >>>> idealism here.
        except AttributeError:
            # For the name of each annotated attribute of this hintable and the
            # new hint which which to annotate this attribute, overwrite the
            # prior hint originally annotating this attribute with this new
            # hint.
            #
            # Note that:
            # * The above assignment is an efficient O(1) operation and thus
            #   intentionally performed first.
            # * This iteration-based assignment is an inefficient O(n) operation
            #   (where "n" is the number of annotated attributes of this
            #   hintable) and thus intentionally performed last here.
            for attr_name, attr_hint in annotations.items():
                hintable.__annotations__[attr_name] = attr_hint

# ....................{ VERSIONS ~ docs                    }....................
clear_pep649_caches.__doc__ = (
    '''
    Clear (i.e., empty) *all* internal :pep:`649`-specific caches specifically
    leveraged by this submodule, enabling callers to reset this submodule to its
    initial state.
    '''
)
get_pep649_hintable_annotations_or_none.__doc__ = (
    '''
    **Memoized annotations** (i.e., possibly empty ``__annotations__`` dunder
    dictionary mapping from the name of each annotated child object of the
    passed hintable to the type hint annotating that child object) annotating
    the passed **hintable** (i.e., ideally pure-Python object defining the
    ``__annotations__`` dunder attribute as well as the :pep:`649`-compliant
    ``__annotate__`` dunder method if the active Python interpreter targets
    Python >= 3.14) if this hintable defines the ``__annotations__`` dunder
    dictionary *or* :data:`None` otherwise (i.e., if this hintable fails to
    define the ``__annotations__`` dunder dictionary).

    This getter is memoized for efficiency, guaranteeing amortized worst-case
    :math:`O(1)` constant time complexity. The first call to this getter passed
    a new hintable annotated by one or more type hints containing :math:`n`
    unquoted forward references exhibits non-amortized worst-case :math:`O(n)`
    linear time complexity, justifying the memoization of this getter.

    Parameters
    ----------
    hintable : Pep649Hintable
        Hintable to be inspected.

    Returns
    -------
    Optional[Pep649HintableAnnotations]
        Either:

        * If this hintable is actually a hintable, the ``__annotations__``
          dunder dictionary set on this hintable.
        * Else, :data:`None`.
    '''
)
set_pep649_hintable_annotations.__doc__ = (
    '''
    Set the **annotations** (i.e., ``__annotations__`` dunder dictionary mapping
    from the name of each annotated child object of the passed hintable to the
    type hint annotating that child object) annotating the passed **hintable**
    (i.e., ideally pure-Python object defining the ``__annotations__`` dunder
    attribute as well as the :pep:`649`-compliant ``__annotate__`` dunder method
    if the active Python interpreter targets Python >= 3.14) to the passed
    dictionary.

    Parameters
    ----------
    hintable : Pep649Hintable
        Hintable to be inspected.
    annotations : Pep649HintableAnnotations
        ``__annotations__`` dunder dictionary to set on this hintable.
    exception_cls : TypeException, default: BeartypeDecorHintPep649Exception
        Type of exception to be raised in the event of a fatal error. Defaults
        to :exc:`.BeartypeDecorHintPep649Exception`.
    exception_prefix : str, default: ''
        Human-readable substring prefixing raised exception messages. Defaults
        to the empty string.

    Raises
    ------
    exception_cls
         If this hintable fails to define the ``__annotations__`` dunder
         dictionary. Since *all* pure-Python hintables (including unannotated
         hintables) define this dictionary, this getter raises an exception only
         if the passed hintable is either:

         * *Not* actually a hintable.
         * A **pseudo-callable object** (i.e., otherwise uncallable object whose
           class renders all instances of that class callable by defining the
           ``__call__()`` dunder method).
    '''
)
