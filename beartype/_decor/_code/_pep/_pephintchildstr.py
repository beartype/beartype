#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2020 Cecil Curry.
# See "LICENSE" for further details.

'''
**Beartype decorator child hint type-checking substringifier** (i.e., class
generating placeholder substrings to be globally replaced by a Python code
snippet type-checking the current pith expression against the currently
iterated child hint of the currently visited parent hint) for PEP-compliant
type-checking graph-based code generation.

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                           }....................
from beartype._util.cache.pool.utilcachepool import KeyPool

# See the "beartype.__init__" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ CLASSES                           }....................
class _HintChildStringifier(object):
    '''
    **Child hint type-checking substringifier** (i.e., object generating
    placeholder substrings to be globally replaced by a Python code snippet
    type-checking the current pith expression against the currently iterated
    child hint of the currently visited parent hint).

    Attributes
    ----------
    _pep_hint_child_id : int
        Integer uniquely identifying the currently iterated child hint of the
        currently visited parent hint.
    '''

    # ..................{ INITIALIZERS                      }..................
    def __init__(self) -> None:
        '''
        Initialize this stringifier.
        '''

        # Make it so, ensign.
        self.reinit()


    def reinit(self) -> None:
        '''
        Reinitialize this stringifier, typically after retrieval of
        previously cached instance of this class.

        Specifically, this method resets the :attr:`_pep_hint_child_id`
        instance variable to its initial value.
        '''

        # Since the get_next_pep_hint_child_str() method increments *BEFORE*
        # stringifying this identifier, initializing this identifier to -1
        # ensures that method returns a string containing "0" rather than "-1".
        self._pep_hint_child_id = -1

    # ..................{ GETTERS                           }..................
    def get_next_pep_hint_child_str(self) -> str:
        '''
        Generate a **child hint type-checking substring** (i.e., placeholder
        to be globally replaced by a Python code snippet type-checking the
        current pith expression against the currently iterated child hint of
        the currently visited parent hint).

        This method should only be called exactly once on each hint, typically
        by the currently visited parent hint on iterating each child hint of
        that parent hint.
        '''

        # Increment the unique identifier of the currently iterated child hint.
        self._pep_hint_child_id += 1

        #FIXME: Refactor to leverage f-strings after dropping Python 3.5
        #support, which are the optimal means of performing string formatting.

        # Generate a unique source type-checking substring.
        return '@[' + str(self._pep_hint_child_id) + '}!'

# ....................{ SINGLETONS ~ private              }....................
_hintchildstr_pool = KeyPool(item_maker=_HintChildStringifier)
'''
Thread-safe **child hint type-checking substringifier pool** (i.e.,
:class:`KeyPool` singleton caching previously instantiated
:class:`_HintChildStringifier` instances).

Caveats
----------
**Avoid accessing this private singleton externally.** Instead, call the public
:func:`acquire_hint_child_stringifier` and
:func:`release_hint_child_stringifier` functions, which efficiently validate
both input *and* output to conform to sane expectations.
'''

# ....................{ FUNCTIONS                         }....................
def acquire_hint_child_stringifier() -> _HintChildStringifier:
    '''
    Acquire a reinitialized **child hint type-checking substringifier** (i.e.,
    object generating placeholder substrings to be globally replaced by a
    Python code snippet type-checking the current pith expression against the
    currently iterated child hint of the currently visited parent hint).

    For convenience, this function reinitializes this substringifier on behalf
    of the caller. Callers need *not* explicitly call the
    :meth:`_HintChildStringifier.reinit` method.

    Returns
    ----------
    _HintChildStringifier
        Reinitialized child hint type-checking substringifier.
    '''

    # Thread-safely acquire a child hint substringifier of this length.
    hintchildstr = _hintchildstr_pool.acquire()
    assert isinstance(hintchildstr, _HintChildStringifier), (
        '{!r} not a child hint substringifier.'.format(hintchildstr))

    # Reinitialize this substringifier.
    hintchildstr.reinit()

    # Return this substringifier.
    return hintchildstr


def release_hint_child_stringifier(
    hintchildstr: _HintChildStringifier) -> None:
    '''
    Release the passed child hint type-checking substringifier acquired by a
    prior call to the :func:`acquire_hint_child_stringifier` function.

    Caveats
    ----------
    **This object is not safely accessible after calling this function.**
    Callers should make *no* attempts to read, write, or otherwise access this
    object, but should instead nullify *all* variables referring to this object
    immediately after releasing this object (e.g., by setting these variables
    to the ``None`` singleton, by deleting these variables).

    Parameters
    ----------
    hintchildstr : _HintChildStringifier
        Child hint type-checking substringifier to be released.
    '''
    assert isinstance(hintchildstr, _HintChildStringifier), (
        '{!r} not a child hint substringifier.'.format(hintchildstr))

    # Thread-safely release this substringifier.
    _hintchildstr_pool.release(hintchildstr)
