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
#            @beartype(_arg_to_type_hint_names={
#                'muh_first_arg': 'RecursiveTypeHint',
#                'muh_other_arg': 'NonrecursiveTypeHint',
#            })
#            def muh_func(
#                muh_first_arg: RecursiveTypeHint,
#                muh_other_arg: NonrecursiveTypeHint,
#                muh_final_arg: list[int],  # <-- *NOT A PYTHON IDENTIFIER*
#            ) -> None: ...
#
#        Note that our prospective "_arg_to_type_hint_names" parameter is
#        intentionally privatized.
#
#        Feasible? Certainly. Non-trivial? Certainly. *shrug*
#  * Additionally, note that even the above doesn't suffice. Yes, it *DOES*
#    suffice for the trivial case of a recursive type hint passed as a root type
#    hint. But what about the non-trivial case of a recursive type hint embedded
#    in a parent type hint (e.g., "set[RecursiveTypeHint]")? To properly handle
#    this, we would need to... do what exactly? We have *NO* idea. Is this even
#    worth doing if we can't reasonably detect embedded recursive type hints?
#    *sigh*
#  * It might make more sense to attempt to:
#    * Detect attribute assignments that appear to be defining recursive type
#      hints. Ugh. The issue here is that we could conceivably do so for the
#      current submodule but *NOT* across module boundaries (without caching an
#      insane amount of on-disk metadata, anyway).
#    * Pass a tuple of the names of all such attributes to @beartype.
#    Okay. So, we're agreed we are *NOT* doing that. NO ON-DISK CACHING... yet.
#  * Perhaps we can, indeed, detect embedded recursive type hints by:
#    * Parsing apart something like "set[RecursiveTypeHint]" into the frozen set
#      of all Python identifiers referenced by that type hint. In this case,
#      that would be "frozenset(('set', 'RecursiveTypeHint'))". Of course, we
#      could further optimize this by excluding builtin names (e.g., "set").
#      Seems reasonable... maybe? Presumably, this requires recursively visiting
#      each root type hint AST node to iteratively construct this frozen set.
#  * *OH. OH, BOY.* I sorta figured out how to detect embedded recursive type
#    hints -- but it's insane. Just passing frozen sets or whatever doesn't
#    work, because that approach invites obvious false positives in various edge
#    cases. The *ONLY* approach that is robust, deterministic, and failure-proof
#    against all edge cases is to pass *THE AST NODE ENCAPSULATING EACH TYPE
#    HINT* to @beartype. We pass AST nodes; not the names of type hints: e.g.,
#            from typing import List
#            RecursiveTypeHint = List['RecursiveTypeHint']
#            NonrecursiveTypeHint = list
#
#            @beartype(_arg_to_type_hint_node={
#                'muh_first_arg': AstNode(name='set[RecursiveTypeHint]'),  # <-- fake AST node, obviously
#                'muh_other_arg': AstNode(name='NonrecursiveTypeHint'),    # <-- more faking just for show
#            })
#            def muh_func(
#                muh_first_arg: set[RecursiveTypeHint],
#                muh_other_arg: NonrecursiveTypeHint,
#            ) -> None: ...
#
#    Fairly convinced that would work. The idea here is that our code generation
#    algorithm would iteratively visit each child AST node in parallel to the
#    actual child type hint that it is currently visiting. Doing so enables
#    @beartype to then decide whether a type hint is recursive or not... in
#    theory, anyway. Note, however, that this is still *EXTREMELY* non-trivial.
#    Like, our code generation algorithm would probably need to maintain an
#    internal stack of the names of all parent type hints on the current path to
#    the currently visited child type hint. lolwut?
#  * Raise a human-readable exception when detecting a recursive type hint. This
#    is better than raising a non-human-readable exception, which we currently
#    do. Naturally, eventually, we should instead...
#  * Dynamically generate a new recursive type-checking
#    BeartypeForwardRef_{attr_name}.is_instance() tester method that recursively
#    calls itself indefinitely. If doing so generates a "RecursionError",
#    @beartype considers that the user's problem. *wink*
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
