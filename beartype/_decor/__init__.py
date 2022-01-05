#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2022 Beartype authors.
# See "LICENSE" for further details.

# ....................{ TODO                              }....................
#FIXME: [OPTIMIZATION] As a useful microoptimization, unroll *ALL* calls to
#the any() and all() builtins into equivalent "for" loops in our critical path.
#Since we typically pass these builtins generator comprehensions created and
#destroyed on-the-fly, we've profiled these builtins to incur substantially
#higher runtime costs than equivalent "for" loops. Thanks alot, CPython. *sigh*

#FIXME: [FEATURE] Plugin architecture. The NumPy type hints use case will come
#up again and again. So, let's get out ahead of that use case rather than
#continuing to reinvent the wheel. Let's begin by defining a trivial plugin API
#enabling users to define their own arbitrary type hint *REDUCTIONS.* Because
#it's capitalized, we know the term "REDUCTIONS" is critical here. We are *NOT*
#(at least, *NOT* initially) defining a full-blown plugin API. We're only
#enabling users to reduce arbitrary type hints:
#* From domain-specific objects they implement and annotate their code with...
#* Into PEP-compliant type hints @beartype already supports.
#Due to their versatility, the standard use case is reducing PEP-noncompliant
#type hints to PEP 593-compliant beartype validators. To do so, consider:
#* Defining a new public "beartype.plug" subpackage, defining:
#  * A private "_PLUGIN_NAME_TO_SIGN" dictionary mapping from each "name"
#    parameter passed to each prior call of the plug_beartype() function to the
#    "HintSign" object that function dynamically creates to represent
#    PEP-noncompliant type hints handled by that plugin. This dictionary
#    effectively maps from the thing our users care about but we don't (i.e.,
#    plugin names) to the thing our users don't care about but we do (i.e.,
#    hint signs).
#  * A public plug_beartype() function with signature resembling:
#       def plug_beartype(
#           # Mandatory parameters.
#           name: str,
#           hint_reduce: Callable[[object,], object],
#
#           # Optional parameters.
#           hint_detect_from_repr_prefix_args_1_or_more: Optional[str] = None,
#           hint_detect_from_type_name: Optional[str] = None,
#       ) -> None:
#    ...where:
#    * The "name" parameter is an arbitrary non-empty string (e.g., "Numpy").
#      This function will then synthesize a new hint sign suffixed by this
#      substring (e.g., f'HintSign{name}') and map this name to that sign in
#      the "_PLUGIN_NAME_TO_SIGN" dictionary.
#    * The "hint_detect_from_repr_prefix_args_1_or_more" parameter is an
#      arbitrary non-empty string typically corresponding to the
#      fully-qualified name of a subclass of "types.GenericAlias" serving as a
#      PEP 585-compliant type hint factory(e.g.,
#      "muh_package.MuhTypeHintFactory"), corresponding exactly to the items
#      of the "HINT_REPR_PREFIX_ARGS_1_OR_MORE_TO_SIGN" set.
#    * The "hint_detect_from_type_name" parameter is the fully-qualified name
#      of a caller-defined class (e.g., "muh_package.MuhTypeHintFactoryType"),
#      corresponding exactly to the items of the "HINT_TYPE_NAME_TO_SIGN" set.
#    * The "hint_reduce" parameter is an arbitrary caller-defined callable
#      reducing all type hints identified by one or more of the detection
#      schemes below to another arbitrary (but hopefully PEP-compliant and
#      beartype-supported) type hint. Again, that will typically be a
#      PEP 593-compliant beartype validator.
#  * A public unplug_beartype() function with signature resembling:
#       def unplug_beartype(name: str) -> None:
#    This function simply looks up the passed name in various internal data
#    structures (e.g.,"_PLUGIN_NAME_TO_SIGN") to undo the effects of the prior
#    plug_beartype() call passed that name.
#
#Given that, we should then entirely reimplement our current strategy for
#handling NumPy type hints into a single call to plug_beartype(): e.g.,
#    # Pretty boss, ain't it? Note we intentionally pass
#    # "hint_detect_from_repr_prefix_args_1_or_more" here, despite the fact
#    # that the unsubscripted "numpy.typing.NDArray" factory is a valid type
#    # hint. Yes, this actually works. Why? Because that factory implicitly
#    # subscripts itself when unsubscripted. In other words, there is *NO* such
#    # thing as an unsubscripted typed NumPy array. O_o
#    def plug_beartype(
#        name='NumpyArray',
#        hint_reduce=reduce_hint_numpy_ndarray,
#        hint_detect_from_repr_prefix_args_1_or_more='numpy.ndarray',
#    )
#
#Yes, this would then permit us to break backward compatibility by bundling
#that logic into a new external "beartype_numpy" plugin for @beartype -- but we
#absolutely should *NOT* do that, both because it would severely break backward
#compatibility *AND* because everyone (including us) wants NumPy support
#out-of-the-box. We're all data scientists here. Do the right thing.

#FIXME: [FEATURE] Define the following supplementary decorators:
#* @beartype.beartype_O1(), identical to the current @beartype.beartype()
#  decorator but provided for disambiguity. This decorator only type-checks
#  exactly one item from each container for each call rather than all items.
#* @beartype.beartype_Ologn(), type-checking log(n) random items from each
#  container of "n" items for each call.
#* @beartype.beartype_On(), type-checking all items from each container for
#  each call. We have various ideas littered about GitHub on how to optimize
#  this for various conditions, but this is never going to be ideal and should
#  thus never be the default.
#
#To differentiate between these three strategies, consider:
#* Declare an enumeration in "beartype._decor._call" resembling:
#    from enum import Enum
#    BeartypeStrategyKind = Enum('BeartypeStrategyKind ('O1', 'Ologn', 'On',))
#* Define a new "BeartypeCall.strategy_kind" instance variable.
#* Set this variable to the corresponding "BeartypeStrategyKind" enumeration
#  member based on which of the three decorators listed above was called.
#* Explicitly pass the value of the "BeartypeCall.strategy_kind" instance
#  variable to the beartype._decor._code._pep._pephint.pep_code_check_hint()
#  function as a new memoized "strategy_kind" parameter.
#* Conditionally generate type-checking code throughout that function depending
#  on the value of that parameter.

#FIXME: Emit one non-fatal warning for each annotated type that is either:
#
#* "beartype.cave.UnavailableType".
#* "beartype.cave.UnavailableTypes".
#
#Both cases imply user-side misconfiguration, but not sufficiently awful enough
#to warrant fatal exceptions. Moreover, emitting warnings rather than
#exceptions enables end users to unconditionally disable all unwanted warnings,
#whereas no such facilities exist for unwanted exceptions.
#FIXME: Validate all tuple annotations to be non-empty *EXCLUDING*
#"beartype.cave.UnavailableTypes", which is intentionally empty.
#FIXME: Unit test the above edge case.

#FIXME: Add support for all possible kinds of parameters. @beartype currently
#supports most but *NOT* all types. Specifically:
#
#* Type-check variadic keyword arguments. Currently, only variadic positional
#  arguments are type-checked. When doing so, remove the
#  "Parameter.VAR_KEYWORD" type from the "_PARAM_KIND_IGNORABLE" set.
#* Type-check positional-only arguments under Python >= 3.8. Note that, since
#  C-based callables have *ALWAYS* supported positional-only arguments, the
#  "Parameter.POSITIONAL_ONLY" type is defined for *ALL* Python versions
#  despite only being usable in actual Python from Python >= 3.8. In other
#  words, support for type-checking positional-only arguments should be added
#  unconditionally without reference to Python version -- we suspect, anyway.
#  When doing so, remove the "Parameter.POSITIONAL_ONLY" type from the
#  "_PARAM_KIND_IGNORABLE" set.
#* Remove the "_PARAM_KIND_IGNORABLE" set entirely.

