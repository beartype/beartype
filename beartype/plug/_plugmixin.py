#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype plugin mixin hierarchy** (i.e., public classes intended to be
subclassed as mixins by users extending :mod:`beartype` with third-party runtime
behaviours).

Most of the public attributes defined by this private submodule are explicitly
exported to external users in our top-level :mod:`beartype.plug.__init__`
submodule. This private submodule is *not* intended for direct importation by
downstream callers.
'''

# ....................{ IMPORTS                            }....................

# ....................{ MIXINS                             }....................
class BeartypeHintable(object):
    '''
    **Beartype hintable mixin** (i.e., class intended to be subclassed as a
    mixin by user-defined classes extending :mod:`beartype` with class-specific
    runtime type-checking via the :mod:`beartype`-specific
    :meth:`__beartype_hint__` method).

    Usage
    ----------
    **You are encouraged but not required to subclass this mixin.** Doing so
    publicly declares your intention to implement this abstract method and then
    raises a :exc:`NotImplementedError` exception when you fail to do so,
    improving the quality of your codebase with a simple contractual guarantee.
    This mixin does *not* require a custom metaclass and is thus safely
    subclassable by everything -- including your own classes.

    **Beartype internally ignores this mixin.** This mixin exists *only* to
    improve the quality of your codebase. Instead, beartype detects type hints
    defining :meth:`__beartype_hint__` methods via the :func:`getattr` builtin
    and then replaces those hints with the new type hints returned by those
    methods. In pseudo-code, this logic crudely resembles: e.g.,

    .. code-block::

       # "__beartype_hint__" attribute of this type hint if any *OR* "None".
       beartype_hinter = getattr(hint, '__beartype_hint__')

       # If this hint defines this attribute *AND* this attribute is callable,
       # replace this hint by the new type hint returned by this callable.
       if callable(beartype_hinter):
           hint = beartype_hinter()

    You care about this, because this means that:

    * You can trivially monkey-patch third-party classes *not* under your direct
      control with :meth:`__beartype_hint__` methods, constraining those classes
      with runtime type-checking implemented by you!
    * :mod:`beartype` accepts *any* arbitrary objects defining
      :meth:`__beartype_hint__` methods as valid type hints -- including objects
      that are neither classes nor PEP-compliant! Of course, doing so would
      render your code incompatible with static type-checkers and thus IDEs.
      That's a bad thing. Nonetheless, this API enables you to do bad things.
      With great plugin power comes great user responsibility.
    '''

    # ....................{ METHODS                        }....................
    @classmethod
    def __beartype_hint__(cls) -> object:
        '''
        **Beartype type hint transform** (i.e., :mod:`beartype`-specific dunder
        class method returning a new type hint, which typically constrains this
        class with additional runtime type-checking).
        '''

        raise NotImplementedError(  # pragma: no cover
            'Abstract class method '
            'BeartypeHintable.__beartype_hint__() undefined.'
        )
