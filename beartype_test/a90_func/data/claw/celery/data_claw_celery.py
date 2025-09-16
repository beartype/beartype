#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype **import hookable Celery integration submodule** (i.e., data module
defining Celery-specific Runnables decorated by the third-party
decorator-hostile :func:`celery_core.runnables.chain` decorator which the
:mod:`beartype.beartype` decorator will then be injected *after* rather than
*before* as the earliest decorator, mimicking real-world usage of
:func:`beartype.claw` import hooks from external callers).

See Also
--------
https://github.com/beartype/beartype/issues/500
    StackOverflow issue exercised by this submodule.
'''

# ....................{ IMPORTS                            }....................
# from beartype.roar import BeartypeCallHintParamViolation
from celery import Celery
# from pytest import raises

# ....................{ GLOBALS                            }....................
celery_server = Celery(broker='memory://')
'''
Arbitrary in-memory Celery server leveraging the in-memory broker.

Note that Celery provides *no* equivalent in-memory backend, for the obvious
reason that Celery principally leverages the multiprocessing forking model.
Clearly, forks do *not* share memory. Unfortunately, because Celery provides
*no* equivalent in-memory backend, there exists *no* trivial means of extracting
the data asynchronously returned from a Celery task. The Celery task defined
below thus intentionally returns *no* data; instead, that task simply validates
the contents of the passed input.
'''

# ....................{ FUNCTIONS                          }....................
@celery_server.task(name="Amaz'd and full of fear; like anxious men")
def amazed_and_full_of_fear(like_anxious_men: dict[str, str]) -> None:
    '''
    Arbitrary function trivially satisfying Celery's task protocol by
    accepting an arbitrary dictionary of mock input data.

    The :obj:`Celery.task` decorator method wraps this function in a
    Celery-specific ``Task`` object defining an ``apply_async()`` method, which
    we then indirectly call below via the higher-level ``delay()`` method to
    validate this wrapping.

    Note that this Celery task intentionally returns *no* output. Doing so would
    require the non-trivial installation, configuration, and registration of a
    non-trivial third-party package above as this Celery server's backend.
    '''

    # Value associated with this key of this caller-defined mock input.
    gather_in_panting_troops = like_anxious_men['gather in panting troops']

    # Assert this value to be the expected mock input.
    assert gather_in_panting_troops == 'like anxious men'

# ....................{ PASS                               }....................
# Implicitly assert that the import hook registered by the caller respected the
# decorator-hostile @task decorator decorating the function defined above by
# injecting the @beartype decorator as the last decorator on that function.
#
# If this call raises an unexpected exception, then that import hook failed to
# respect that the decorator-hostile @task decorator by instead injecting the
# @beartype decorator as the first decorator on that function. Since @task is
# decorator-hostile and thus hostile to @beartype as well, @task prohibits
# *ANY* decorator from being applied after itself.
#
# Note that this result is extremely unsafe and thus largely useless. Since this
# Celery server lacks a backend, Celery tasks queued against this server can
# only be invoked. They *CANNOT* be queried after invocation -- even as to their
# failure state. Attempting to call *ANY* method of this result causes Celery to
# raise an unreadable exception resembling:
#     NotImplementedError: No result backend is configured.
#     Please see the documentation for more information.
#
# In other words, Celery is fundamentally hostile to testing by unrelated
# third-party packages like @beartype that could honestly care less about
# Celery. Seriously, Celery. What were you thinking?
amazed_and_full_of_fear_result = amazed_and_full_of_fear.delay(
    {'gather in panting troops': 'like anxious men'})

#FIXME: Preserved for posterity, but unlikely we'll ever be able to resurrect
#this. Doing so raises the "NotImplementedError" exception detailed above.
# # Value returned by that call.
# when_earthquakes_jar = amazed_and_full_of_fear_result.get()
#
# # Explicitly assert that call returned the expected output.
# print(f'when_earthquakes_jar: {when_earthquakes_jar}')
# assert when_earthquakes_jar == 'Who on wide plains like anxious men'

# ....................{ FAIL                               }....................
#FIXME: *LOLBRO.* We have no idea how to even test whether a Celery task raises
#an exception or not without attaching a valid third-party Celery backend to the
#Celery server defined above, which we *CLEARLY* are not going to do. *sigh*
# # Assert this Runnable when passed an invalid parameter raises the expected
# # @beartype-specific type-checking violation.
# with raises(BeartypeCallHintParamViolation):
#     amazed_and_full_of_fear.delay(
#         {len('When earthquakes jar'): len('their battlements and towers.')})
