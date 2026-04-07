#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

# ....................{ TODO                               }....................
#FIXME: Note that NumPy provides an efficient means of generating a large
#number of pseudo-random integers all-at-once. The core issue there, of
#course, is that we then need to optionally depend upon and detect NumPy,
#which then requires us to split our random integer generation logic into two
#parallel code paths that we'll then have to maintain -- and the two will be
#rather different. In any case, here's how one generates a NumPy array
#containing 100 pseudo-random integers in the range [0, 127]:
#    random_ints = numpy.random.randint(128, size=100)
#
#To leverage that sanely, we'd need to:
#* Globally cache that array somewhere.
#* Globally cache the current index into that array.
#* When NumPy is unimportable, fallback to generating a Python list containing
#  the same number of pseudo-random integers in the same range.
#* In either case, we'd probably want to wrap that logic in a globally
#  accessible infinite generator singleton that returns another pseudo-random
#  integer every time you iterate it. This assumes, of course, that iterating
#  generators is reasonably fast in Python. (If not, just make that a getter
#  method of a standard singleton object.)
#* Replace the code snippet below with something resembling:
#      '''
#      __beartype_random_int = next(__beartype_random_int_generator)
#      '''
#Note that thread concurrency issues are probable ignorably here, but that
#there's still a great deal of maintenance and refactoring that would need to
#happen to sanely support this. In other words, ain't happenin' anytime soon.
#FIXME: To support both NumPy and non-NumPy code paths transparently, design a
#novel private data structure named "_BeartypeRNJesus" whose __next__() dunder
#method transparently returns a new random integer. The implementation of that
#method then handles all of the low-level minutiae like:
#* Storing and iterating the 0-based index of the next index into an internally
#  cached NumPy array created by calling numpy.random.randint().
#* Creating a new cached NumPy array after exhausting the prior cached array.
