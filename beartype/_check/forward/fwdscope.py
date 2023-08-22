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

# ....................{ IMPORTS                            }....................
from beartype.roar import BeartypeDecorHintForwardRefException
from beartype.typing import Type
from beartype._data.hint.datahinttyping import LexicalScope
from beartype._check.forward._fwdref import (
    make_forwardref_indexable_subtype,
    _BeartypeForwardRefIndexableABC,
)
from beartype._util.text.utiltextident import die_unless_identifier
# from sys import modules as sys_modules

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
    _is_scope_module : bool
        :data:`True` only if the name of this scope is that of a previously
        imported module, implying this to be a forward module scope.
    _scope_name : str
        Fully-qualified name of this forward scope.
    _scope_attrs : LexicalScope
        **Lexical scope** (i.e., dictionary mapping from the relative
        unqualified name to value of each previously declared attribute)
        underlying this forward scope.
    '''

    # ..................{ INITIALIZERS                       }..................
    #FIXME: Implement us up, please.
    def __init__(
        self,
        scope_name: str,
        scope_attrs: LexicalScope,
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
        scope_attrs : LexicalScope
            **Lexical scope** (i.e., dictionary mapping from the relative
            unqualified name to value of each previously declared attribute)
            underlying this forward scope.

        Raises
        ----------
        BeartypeDecorHintForwardRefException
            If this scope name is *not* a valid Python attribute name.
        '''
        assert isinstance(scope_attrs, dict), (
            f'{repr(scope_attrs)} not dictionary.')

        # Initialize our superclass with this lexical scope, efficiently
        # pre-populating this dictionary with all previously declared attributes
        # underlying this forward scope.
        super().__init__(scope_attrs)

        # If this scope name is syntactically invalid, raise an exception.
        die_unless_identifier(
            text=scope_name,
            exception_cls=BeartypeDecorHintForwardRefException,
            exception_prefix='Forward scope name ',
        )
        # Else, this scope name is syntactically valid.

        # Classify all passed parameters.
        self._scope_attrs = scope_attrs
        self._scope_name = scope_name

        #FIXME: Consider excising, please.
        # True only if the name of this scope is that of a previously imported
        # module, implying this to be a module scope.
        # self._is_scope_module = scope_name in sys_modules

    # ..................{ DUNDERS                            }..................
    def __missing__(self, hint_name: str) -> Type[
        _BeartypeForwardRefIndexableABC]:
        '''
        Dunder method explicitly called by the superclass
        :meth:`dict.__getitem__` method implicitly called on each ``[``- and
        ``]``-delimited attempt to access an **unresolved type hint** (i.e.,
        *not* currently defined in this scope) with the passed name.

        This method transparently replaces this unresolved type hint with a
        **forward reference proxy** (i.e., concrete subclass of the private
        :class:`beartype._check.forward._fwdref._BeartypeForwardRefABC` abstract
        base class (ABC), which resolves this type hint on the first call to the
        :func:`isinstance` builtin whose second argument is that subclass).

        This method assumes that:

        * This scope is only partially initialized.
        * This type hint has yet to be declared in this scope.
        * This type hint will be declared in this scope by the later time that
          this method is called.

        Parameters
        ----------
        hint_name : str
            Relative (i.e., unqualified) or absolute (i.e., fully-qualified)
            name of this unresolved type hint.

        Returns
        ----------
        _BeartypeForwardRefIndexableABC
            Forward reference proxy deferring the resolution of this unresolved
            type hint.

        Raises
        ----------
        BeartypeDecorHintForwardRefException
            If this type hint name is *not* a valid Python attribute name.
        '''

        # If this type hint name is syntactically invalid, raise an exception.
        die_unless_identifier(
            text=hint_name,
            exception_cls=BeartypeDecorHintForwardRefException,
            exception_prefix='Forward reference ',
        )
        # Else, this type hint name is syntactically valid.

        # If this type hint name contains *NO* "." delimiters and is thus
        # relative to this scope...
        if '.' not in hint_name:
            # Canonicalize this relative type hint name into an absolute type
            # hint name relative to the name of this scope.
            hint_name = f'{self._scope_name}.{hint_name}'
        # Else, this type hint name contains one or more "." delimiters and is
        # thus absolute (i.e., fully-qualified). In this case, preserve this
        # name as is.

        # Forward reference proxy to be returned.
        forwardref_subtype = make_forwardref_indexable_subtype(hint_name)

        # Return this proxy. The superclass dict.__getitem__() dunder method
        # then implicitly maps the passed unresolved type hint name to this
        # proxy by effectively assigning this name to this proxy: e.g.,
        #     self[hint_name] = forwardref_subtype
        return forwardref_subtype
