#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype **import hookable FastMCP integration submodule** (i.e., data module
defining FastMCP-specific runnables decorated by the third-party
decorator-hostile :func:`fastmcp.FastMCP.tool` decorator which the
:mod:`beartype.beartype` decorator will then be injected *after* rather than
*before* as the earliest decorator, mimicking real-world usage of
:func:`beartype.claw` import hooks from external callers).

See Also
--------
https://github.com/beartype/beartype/issues/540
    StackOverflow issue exercised by this submodule.
https://gofastmcp.com/clients/client
    Official FastMCP documentation lightly inspiring this integration test.
'''

# ....................{ IMPORTS                            }....................
from fastmcp import (
    Client,
    FastMCP,
)

# ....................{ GLOBALS                            }....................
fastmcp_server = FastMCP('With stride colossal, on from hall to hall;')
'''
Arbitrary in-memory FastMCP server leveraging the default STDIO (i.e., standard
input and output) transport protocol.
'''


fastmcp_client = Client(fastmcp_server)
'''
Arbitrary in-memory FastMCP client connecting to this server of that protocol.
'''

# ....................{ FUNCTIONS                          }....................
@fastmcp_server.tool
def with_stride_colossal(on_from_hall_to_hall: str) -> int:
    '''
    Arbitrary function trivially satisfying FastMCP's runnable protocol by
    accepting an arbitrary string of mock input data and returning a byte string
    mocking the output text response of a model context protocol (MCP) passed
    that input.

    The :meth:`mcp.tool` decorator wraps this function in a FastMCP-specific
    runnable object defining a ``run()`` method, which we then call below to
    validate this wrapping.
    '''

    # Return the trivial length of this string. We initially attempted to coerce
    # this string into a byte string, but Pydantic promptly complained about
    # that. Lol. "Y U H8 byte string, M8?"
    return len(on_from_hall_to_hall)

# ....................{ MAIN                               }....................
async def data_claw_fastmcp_main() -> None:
    '''
    Asynchronous coroutine performing all FastMCP-specific integration tests.

    Note that:

    * FastMCP implicitly transforms *all* FastMCP-decorated synchronous
      callables into asynchronous callables. Client FastMCP operations, in
      particular, *must* then be called "using the ``async with`` context
      manager for proper connection lifecycle management."
    * The caller *must* manually run this coroutine within an ``asyncio`` loop
      explicitly managed by the caller.
    '''
    # print('[data_claw_fastmcp] with_stride_colossal:')
    # print(with_stride_colossal.__module__)
    # print(with_stride_colossal.__class__.__name__)

    # ....................{ FASTMCP                        }....................
    # Inside a FastMCP-specific asynchronous context manager encapsulating this
    # client-server connection...
    async with fastmcp_client:
        # Implicitly assert the server connected to this client to be awake by
        # trivially pinging the server from this client.
        await fastmcp_client.ping()

        # ....................{ PASS                       }....................
        # Valid input to be passed to the FastMCP tool defined above.
        TOOL_INPUT = 'While far within each aisle and deep recess,'

        # Synchronously call the asynchronous FastMCP server tool defined above
        # with valid input. Doing so implicitly asserts that the import hook
        # registered by the caller respected the decorator-hostile
        # @fastmcp_server.tool method decorating the function defined above by
        # injecting the @beartype decorator as the last decorator on that
        # function.
        #
        # If this call raises an unexpected exception, then that import hook
        # failed to respect that the decorator-hostile @fastmcp_server.tool
        # decorator by instead injecting the @beartype decorator as the first
        # decorator on that function. Since @fastmcp_server.tool is
        # decorator-hostile and thus hostile to @beartype as well,
        # @fastmcp_server.tool prohibits *ANY* decorator from being applied
        # after itself.
        #
        # Note that:
        # * The object returned by this asynchronous client invocation of a
        #   FastMCP tool is a FastMCP-specific "CallToolResult" object. Look. We
        #   don't know either. This API is hell to test. Sanity now! See also:
        #     https://gofastmcp.com/clients/tools#handling-results
        # * There's little point in attempting to validate that this tool raises
        #   @beartype-specific type-checking violations. Why? Because it
        #   doesn't. FastMCP validates input through Pydantic *BEFORE*
        #   @beartype-specific type-checking can get there. It is what it is.
        tool_output = await fastmcp_client.call_tool(
            'with_stride_colossal', {'on_from_hall_to_hall': TOOL_INPUT})

        # Explicitly assert that call returned the expected output.
        # print(f'tool_output: {tool_output}')
        assert tool_output.data == len(TOOL_INPUT)
