#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype **thread-safe Decidedly Object-Oriented Runtime-checking (DOOR)
type-checking unit tests** (i.e., unit tests validating that
:mod:`beartype.door` functionality behaves thread-safely, especially under
free-threading GIL-free Python interpreters).
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS ~ raisers                    }....................
def test_door_threadsafe() -> None:
    '''
    Test that the :func:`beartype.door.is_bearable` tester function behaves
    thread-safely, especially under free-threading GIL-free Python interpreters.

    See Also
    --------
    https://github.com/beartype/beartype/issues/670
        Beartype issue validated by this unit test. Thanks so much to heroic
        astrophysics Pythonista @nstarman (Nathaniel Starkman) for effectively
        writing the entirety of this beastly test. You rock the cosmos!
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    import sys
    from beartype.door import is_bearable
    from beartype._data.typing.datatypingport import TupleHints
    from beartype._util.cls.utilclsmake import make_type
    from threading import (
        Barrier,
        Thread,
    )

    # ....................{ MAIN                           }....................
    # Current ideal thread duration (in floating-point seconds) for the active
    # Python interpreter, localized to permit its restoration below.
    switch_interval_old = sys.getswitchinterval()

    # Attempt to...
    try:
        # Increase this ideal thread duration to force frequent Global
        # Interpreter Lock (GIL) hand-offs in this interpreter. Crucially, this
        # includes while the beartype type-checker called below is dynamically
        # generating type-checking code. Doing so reliably reproduces any of a
        # number of horrifying race conditions present in obsolete versions of
        # this package. Those races also occur at the default ideal thread
        # duration of 5ms interval under real-world workloads, albeit less
        # frequently. See also:
        #     https://github.com/beartype/plum/issue#274
        sys.setswitchinterval(1e-6)

        # Magic number of threads to be concurrently run below. Don't ask.
        THREAD_COUNT = 24

        # For a magic number of iterations... We clearly said: "Don't ask."
        for iteration_index in range(300):
            # ....................{ HINTS                  }....................
            # Arbitrary types uniquely recreated each iteration, thus
            # guaranteeing that the beartype type-checker called below will
            # dynamically generate new unmemoized type-checking code each
            # iteration for each type hint subscripted by these types below.
            # Doing so increases the likelihood that competing threads will
            # dynamically generate type-checking code concurrently and thus
            # potentially trigger any lingering race conditions.
            SadSignOfRuin = make_type(
                type_name=f'SadSignOfRuin{iteration_index}')
            SuddenDismay = make_type(
                type_name=f'SuddenDismay{iteration_index}')

            # Non-empty tuple of arbitrary PEP 585-compliant type hints
            # subscripted by these types.
            type_hints = (
                list[SadSignOfRuin],
                dict[str, SuddenDismay],
                tuple[SadSignOfRuin, SuddenDismay],
            )

            # ....................{ WORKERS                }....................
            # Thread barrier temporarily pausing *ALL* running threads
            # instantiated below at the thread_barrier.wait() statement
            # performed below until these threads have all reached that barrier.
            # Doing so increases the likelihood of race conditions. Yikes!
            thread_barrier = Barrier(THREAD_COUNT)

            def thread_worker(
                thread_barrier: Barrier = thread_barrier,
                type_hints: TupleHints = type_hints,
            ) -> None:
                '''
                Closure run by each thread instantiated below, effectively
                accepting *no* parameters but passed "optional" parameters
                defaulting to local variables defined above as a crude means of
                injecting these variables into this thread.
                '''

                # Pause *ALL* running threads instantiated below until these
                # threads have all reached this barrier.
                thread_barrier.wait()

                # For each iteration-specific type hint, type-check this hint
                # against an arbitrary object.
                for type_hint in type_hints:
                    is_bearable(None, type_hint)

            # ....................{ THREADS                }....................
            # List of all threads running the worker closure defined above.
            threads = [
                Thread(target=thread_worker) for _ in range(THREAD_COUNT)]

            # Start these threads.
            for t in threads:
                t.start()

            # Block until either:
            # * These threads have *ALL* halted successfully.
            # * At least one of these threads has halted unsuccessfully by
            #   raising an exception, which then re-raises that exception.
            for t in threads:
                t.join()
    # Regardless of whether doing so raises an exception or not...
    finally:
        # Restore the prior ideal thread duration localized above.
        sys.setswitchinterval(switch_interval_old)
