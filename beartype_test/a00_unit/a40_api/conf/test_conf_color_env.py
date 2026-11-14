#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Standard colour environment variables and their configuration precedence.
'''


def test_conf_color_env_precedence(monkeypatch: 'pytest.MonkeyPatch') -> None:
    '''All environment combinations preserve priority, warnings and caching.'''
    from beartype import BeartypeConf
    from beartype.roar import BeartypeConfShellVarWarning
    from itertools import product
    from warnings import catch_warnings, simplefilter

    specific_values = {None: None, 'True': True, 'False': False, 'None': None}
    standard_values = (None, '', '1', '0', 'False', ' ')
    cached = {}

    for specific, no_color, force_color in product(
        specific_values, standard_values, standard_values):
        for name, value in (
            ('BEARTYPE_IS_COLOR', specific),
            ('NO_COLOR', no_color),
            ('FORCE_COLOR', force_color),
        ):
            if value is None:
                monkeypatch.delenv(name, raising=False)
            else:
                monkeypatch.setenv(name, value)

        if specific is not None:
            selected = 'BEARTYPE_IS_COLOR'
            override = specific_values[specific]
        elif no_color not in (None, ''):
            selected, override = 'NO_COLOR', False
        elif force_color not in (None, ''):
            selected, override = 'FORCE_COLOR', True
        else:
            selected, override = None, None

        for kwargs in ({}, {'is_color': True}, {'is_color': False}, {'is_color': None}):
            expected = override if selected else kwargs.get('is_color')
            with catch_warnings(record=True) as warnings:
                simplefilter('always')
                conf = BeartypeConf(**kwargs)

            assert conf.is_color is expected
            if expected in cached:
                assert conf is cached[expected]
            else:
                cached[expected] = conf

            conflict = (
                selected is not None and 'is_color' in kwargs and
                kwargs['is_color'] is not expected)
            assert len(warnings) == int(conflict)
            if conflict:
                assert warnings[0].category is BeartypeConfShellVarWarning
                assert f'${{{selected}}}' in str(warnings[0].message)


def test_conf_color_env_invalid(monkeypatch: 'pytest.MonkeyPatch') -> None:
    '''An invalid specific override never falls through to standard colours.'''
    from beartype import BeartypeConf
    from beartype.roar import BeartypeConfShellVarException
    from pytest import raises

    monkeypatch.setenv('NO_COLOR', '1')
    monkeypatch.setenv('FORCE_COLOR', '1')
    for value in ('', '0', 'false', 'True ', 'invalid'):
        monkeypatch.setenv('BEARTYPE_IS_COLOR', value)
        with raises(BeartypeConfShellVarException, match='BEARTYPE_IS_COLOR'):
            BeartypeConf()


def test_conf_color_env_snapshot(monkeypatch: 'pytest.MonkeyPatch') -> None:
    '''Environment changes affect new configurations, not existing ones.'''
    from beartype import BeartypeConf

    for name in ('BEARTYPE_IS_COLOR', 'NO_COLOR', 'FORCE_COLOR'):
        monkeypatch.delenv(name, raising=False)
    automatic = BeartypeConf()
    monkeypatch.setenv('NO_COLOR', '1')
    plain = BeartypeConf()
    monkeypatch.delenv('NO_COLOR')
    monkeypatch.setenv('FORCE_COLOR', '1')
    coloured = BeartypeConf()
    assert automatic.is_color is None
    assert plain.is_color is False
    assert coloured.is_color is True

    # Python's interpreter-specific setting is deliberately not inherited.
    monkeypatch.delenv('FORCE_COLOR')
    monkeypatch.setenv('PYTHON_COLORS', '1')
    assert BeartypeConf() is automatic


def test_conf_color_env_decorator(monkeypatch: 'pytest.MonkeyPatch') -> None:
    '''Real violations use the configured colours, not merely a stored flag.'''
    from beartype import beartype, BeartypeConf
    from beartype.roar import BeartypeCallHintParamViolation
    from pytest import raises

    for name in ('BEARTYPE_IS_COLOR', 'NO_COLOR', 'FORCE_COLOR'):
        monkeypatch.delenv(name, raising=False)

    for name, expected in (('NO_COLOR', False), ('FORCE_COLOR', True)):
        monkeypatch.setenv(name, '1')

        @beartype(conf=BeartypeConf())
        def identity(value: int) -> int:
            return value

        assert identity(1) == 1
        with raises(BeartypeCallHintParamViolation) as exception:
            identity('not an integer')
        assert ('\x1b[' in str(exception.value)) is expected
        monkeypatch.delenv(name)


def test_conf_color_env_fresh_process() -> None:
    '''Fresh default decorators honour environment settings before import.'''
    import os
    import subprocess
    import sys
    from textwrap import dedent

    source = dedent('''
        import os
        from beartype import beartype, BeartypeConf
        from beartype.roar import BeartypeCallHintParamViolation

        def is_coloured(func):
            try:
                func('not an integer')
            except BeartypeCallHintParamViolation as exception:
                return '\\x1b[' in str(exception)
            else:
                raise AssertionError('type violation not raised')

        @beartype
        def identity(value: int) -> int:
            return value

        initial_is_coloured = is_coloured(identity)
        print('coloured' if initial_is_coloured else 'plain')

        # Defaults are captured at import. Subsequent environment changes
        # affect new explicit configurations, not default or existing wrappers.
        for name in ('BEARTYPE_IS_COLOR', 'NO_COLOR', 'FORCE_COLOR'):
            os.environ.pop(name, None)
        os.environ['NO_COLOR' if initial_is_coloured else 'FORCE_COLOR'] = '1'

        @beartype
        def default_after_change(value: int) -> int:
            return value

        @beartype(conf=BeartypeConf())
        def explicit_after_change(value: int) -> int:
            return value

        assert is_coloured(identity) is initial_is_coloured
        assert is_coloured(default_after_change) is initial_is_coloured
        assert is_coloured(explicit_after_change) is not initial_is_coloured

        for name in ('NO_COLOR', 'FORCE_COLOR'):
            os.environ.pop(name, None)
        os.environ['FORCE_COLOR' if initial_is_coloured else 'NO_COLOR'] = '1'
        assert is_coloured(explicit_after_change) is not initial_is_coloured
    ''')
    clean_env = {
        key: value for key, value in os.environ.items()
        if key not in ('BEARTYPE_IS_COLOR', 'NO_COLOR', 'FORCE_COLOR')
    }
    for variables, expected in (
        ({}, 'plain'),
        ({'NO_COLOR': '', 'FORCE_COLOR': ''}, 'plain'),
        ({'NO_COLOR': '1'}, 'plain'),
        ({'FORCE_COLOR': '1'}, 'coloured'),
        ({'NO_COLOR': '1', 'FORCE_COLOR': '1'}, 'plain'),
        ({'NO_COLOR': '', 'FORCE_COLOR': '0'}, 'coloured'),
        ({'BEARTYPE_IS_COLOR': 'True', 'NO_COLOR': '1'}, 'coloured'),
        ({'BEARTYPE_IS_COLOR': 'False', 'FORCE_COLOR': '1'}, 'plain'),
        ({'BEARTYPE_IS_COLOR': 'None', 'FORCE_COLOR': '1'}, 'plain'),
    ):
        result = subprocess.run(
            [sys.executable, '-c', source],
            env={**clean_env, **variables},
            capture_output=True, text=True, timeout=30, check=True,
        )
        assert result.stdout.strip() == expected
