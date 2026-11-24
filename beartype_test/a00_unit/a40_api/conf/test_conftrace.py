#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''Import tracing configuration tests.'''


def test_conf_trace_imports() -> None:
    from beartype import BeartypeConf
    from beartype.roar import BeartypeConfParamException
    from pytest import raises

    default = BeartypeConf()
    assert default.claw_is_trace_imports is False
    assert default is BeartypeConf(claw_is_trace_imports=False)
    assert 'claw_is_trace_imports' not in repr(default)
    traced = BeartypeConf(claw_is_trace_imports=True)
    assert traced is BeartypeConf(claw_is_trace_imports=True)
    assert traced.claw_is_trace_imports is True
    assert traced.kwargs['claw_is_trace_imports'] is True
    assert BeartypeConf(**traced.kwargs).claw_is_trace_imports is True
    assert 'claw_is_trace_imports=True' in repr(traced)
    with raises(AttributeError):
        traced.claw_is_trace_imports = False
    for invalid in (None, 0, 1, 'true', (), [], {}):
        with raises(BeartypeConfParamException):
            BeartypeConf(claw_is_trace_imports=invalid)
