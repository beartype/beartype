#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype **forward scope classes** (i.e., dictionary subclasses deferring the
resolutions of local and global scopes of classes and callables decorated by the
:func:`beartype.beartype` decorator when dynamically evaluating stringified type
hints for those classes and callables).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ TODO                               }....................
#FIXME: Begin at least *DETECTING* recursive type hints. For the moment, simply:
#* Detect when a type hint recursively refers to itself. Note that this requires
#  generalizing our handling of relative forward references in the __missing__()
#  method below to:
#  * Detect when the attribute referred to by a relative forward reference is,
#    in fact, the root type hint containing the relative forward reference. This
#    is trivial, *ASSUMING THAT THE NAME OF THE ROOT TYPE HINT IS PASSED TO THE*
#    BeartypeForwardScope.__init__() method. In fact, that's pretty much
#    required, right? But... how can we actually get that name? The *ONLY* means
#    is by AST inspection via "beartype.claw", really. Given sufficient
#    intelligence, our "beartype.claw" AST node transformer could:
#    * Introspect whether each type hint annotating a callable is a (possibly
#      fully-qualified) Python identifier or not. Type hints that are:
#      * *NOT* Python identifiers are ignorable for these purposes.
#      * Python identifiers could possibly be recursive type hints. To enable
#        lower-level logic to decide this, our node transformer would then need
#        to dynamically construct a call to the @beartype decorator passing the
#        names of *ALL* root type hints annotating the current callable: e.g.,
#            from typing import List
#            RecursiveTypeHint = List['RecursiveTypeHint']
#            NonrecursiveTypeHint = list
#
#            @beartype(arg_to_type_hint_names={
#                'muh_first_arg': 'RecursiveTypeHint',
#                'muh_other_arg': 'NonrecursiveTypeHint',
#            })
#            def muh_func(
#                muh_first_arg: RecursiveTypeHint,
#                muh_other_arg: NonrecursiveTypeHint,
#                muh_final_arg: list[int],  # <-- *NOT A PYTHON IDENTIFIER*
#            ) -> None: ...
#        Feasible? Certainly. Non-trivial? Certainly. *shrug*
#  * Raise a human-readable exception when detecting a recursive type hint. This
#    is better than raising a non-human-readable exception, which we currently
#    do. Naturally, eventually, we should instead...
#  * Dynamically generate a new recursive type-checking tester function that
#    recursively calls itself indefinitely. If doing so generates a
#    "RecursionError", @beartype considers that the user's problem. *wink*
#
#Let's revisit this when we've at least finalized the initial implementation of
#"BeartypeForwardScope", please.

# ....................{ IMPORTS                            }....................
from beartype.typing import Dict
# from beartype._data.hint.datahinttyping import BeartypeableT

# ....................{ SUBCLASSES                         }....................
#FIXME: Implement us up, please.
#FIXME: Unit test us up, please.
class BeartypeForwardScope(dict):
    '''
    **Forward scope** (i.e., dictionary deferring the resolution of a local or
    global scope of an arbitrary class or callable when dynamically evaluating
    stringified type hints for that class or callable, including both forward
    references *and* :pep:`563`-postponed type hints).

    Attributes
    ----------
    _scope_name : str
        Fully-qualified name of this forward scope.
    '''

    # ..................{ INITIALIZERS                       }..................
    #FIXME: Implement us up, please.
    #FIXME: Docstring us up, please.
    def __init__(
        self,
        scope_name: str,
        scope_attrs: Dict[str, object],
    ) -> None:
        '''
        Initialize this forward scope.

        Attributes
        ----------
        scope_name : str
            Fully-qualified name of this forward scope. For example:

            * ``"some_package.some_module"`` for a module scope (e.g., to
              resolve a global class or callable against this scope).
            * ``"some_package.some_module.SomeClass"`` for a class scope (e.g.,
              to resolve a nested class or callable against this scope).
        '''

        # Initialize our superclass with this dictionary mapping from each
        # attribute name to value of the (possibly only partially initialized)
        # local or global scope of this beartypeable.
        super().__init__(scope_attrs)

        # Classify all passed parameters.
        self._scope_attrs = scope_attrs
        self._scope_name = scope_name

    # ..................{ DUNDERS                            }..................
    def __missing__(self, attr_name: str) -> object:
        '''
        Dunder method explicitly called by the superclass
        :meth:`dict.__getitem__` method implicitly called on caller attempts to
        access the passed missing key with ``[``- and ``]``-delimited syntax.

        This method treats this attempt to retrieve this missing key as an
        attempt to resolve an attribute of this (possibly only partially
        initialized) local or global scope that has yet to be defined in this
        scope -- but hopefully will be at some later time *after* this scope is
        fully initialized.

        Parameters
        ----------
        attr_name : str
            Name of the attribute to be resolved.

        Returns
        ----------
        object
            Attribute whose name is this missing key.

        Raises
        ----------
        BeartypeCallHintForwardRefException
            If the submodule declaring this scope contains *no* attribute with
            this name.
        '''

        #FIXME: Implement us up, please. Note that a variety of edge cases
        #exist, including:

        # If this name contains one or more "." delimiters, this name is
        # presumed to be fully-qualified (i.e., absolute) rather than relative
        # to this lexical scope. In this case...
        if '.' in attr_name:
            #FIXME: The appropriate decision for the moment is probably just to
            #preserve this name as is by returning this name as is. *shrug*
            return attr_name
        # Else, this name contains *NO* "." delimiters, implying this name to be
        # relative to this lexical scope. In this case...
        else:
            #FIXME: Ascertain whether this scope is global or non-global.
            #Ideally, this scope is global. Why? Because, if this scope is
            #global, then we simply:
            #* Canonicalize this relative forward reference into an absolute
            #  forward reference relative to "self._scope_name": e.g.,
            #      attr_name_absolute = f'{self._scope_name}.{attr_name}'
            #* Return "attr_name_absolute". That's it. Trivial and efficient!
            #
            #However, if this scope is non-global, then matters become
            #significantly less trivial and less efficient. The appropriate
            #decision for the moment is probably just to preserve this name as
            #is by returning this name as is. *shrug*
            #FIXME: The question then becomes: how do we detect whether this
            #scope is global or not? Possibly simple. Consider:

            #FIXME: Slightly inefficient. Shift this test into __init__() as:
            #    self._is_scope_global = scope_name in sys_modules
            from sys import modules as sys_modules
            # If this scope is global...
            if self._scope_name in sys_modules:
                # Canonicalize this relative forward reference into an absolute
                # forward reference relative to the fully-qualified name of this
                # forward scope.
                attr_name = f'{self._scope_name}.{attr_name}'

        #FIXME: The appropriate decision for the moment is probably just to
        #preserve this name as is by returning this name as is. *shrug*
        return attr_name

        # # Module attribute whose fully-qualified name is this forward
        # # reference, dynamically imported at callable call time.
        # hint_class: type = import_module_attr(
        #     module_attr_name=hint_classname,
        #     exception_cls=BeartypeCallHintForwardRefException,
        #     exception_prefix='Forward reference ',
        # )
        #
        # # Return this class. The superclass dict.__getitem__() dunder method
        # # then implicitly maps the passed missing key to this class by
        # # effectively assigning this name to this class: e.g.,
        # #     self[hint_classname] = hint_class
        # return hint_class  # type: ignore[return-value]
