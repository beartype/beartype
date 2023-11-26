#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`695`-compliant **type alias** (i.e., objects created via the
``type`` statement under Python >= 3.12) utilities.

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ TODO                               }....................
#FIXME: PEP 695 is fundamentally broken for forward references. To sanely handle
#forward references in a way that preserves working behaviour for both trivial
#recursive type aliases *AND* non-trivial recursive type aliases, a significant
#rethink is required. This is that rethink.
#
#Basically, Python itself needs to recursively compose larger type aliases from
#smaller type aliases that it synthetically instantiates on-demand. Since Python
#currently fails to do that, @beartype must do that. Thankfully, this is
#feasible -- albeit non-trivial, as always.
#
#Specifically, the "beartype.claw" API should statically and unconditionally
#transform *EVERY* single type alias as follows:
#    # "beartype.claw" should transform this...
#    type alias = UndeclaredClass | UndeclaredType
#
#    # ...into this.
#    type alias = UndeclaredClass | UndeclaredType
#    while True:
#        try:
#            alias.__value__
#            break
#        except NameError as exception:
#            undeclared_attr_name = get_nameerror_attr_name(exception)
#            exec(f'type {undeclared_attr_name} = {undeclared_attr_name}')
#            type alias = UndeclaredClass | UndeclaredType
#
#The above approach transparently supports non-trivial recursive type aliases
#resembling:
#    type circular_foo = list[circular_bar]
#    type circular_bar = int | circular_foo
#
#Given the above transformation, supporting forward references embedded within
#PEP 695-style "type" aliases is now trivial. How? Simply:
#* Define a new "HintSignPep695TypeAlias" sign. Note that there already exists a
#  deprecated "typing.TypeAlias" type. Ergo, disambiguation is required for both
#  sanity and maintainability here.
#* Detect PEP 695-style "type" aliases via this new "HintSignPep695TypeAlias"
#  sign. This is trivial, as these aliases are detectable as an instance of
#  "types.TypeAliasType". I think... or something? *sigh*
#* Define a new PEP 695-specific reduce_pep695() reducer resembling:
#      from beartype._cave._cavefast import Pep695TypeAlias
#
#      def reduce_pep695(hint: Pep695TypeAlias) -> object:
#
#          # De-aliased type hint to be returned.
#          hint_aliased = None
#
#          # Attempt to reduce this PEP 695-compliant type alias to the type hint it
#          # lazily encapsulates. If this type alias is *NOT* itself a forward
#          # reference to an undeclared attribute, this reduction is guaranteed to
#          # succeed.
#          try:
#              hint_aliased = hint.__value__
#          # If this reduction raises a "NameError", this type alias is a forward
#          # reference to an undeclared attribute. In this case, reduce this type alias
#          # to a stringified type hint referring to that attribute.
#          except NameError:
#              hint_aliased = repr(hint)
#              assert is_identifier(hint_aliased), (
#                  f'PEP 695 type alias forward reference {repr(hint_aliased)} '
#                  f'not identifier.'
#              )
#
#          # Return this de-aliased type hint.
#          return hint_aliased
