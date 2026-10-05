#!/usr/bin/env python3
'''
Minimal :pep:`526` import-hook regression fixture for recursive aliases.
'''

from typing import TypeAlias


RecursiveAlias: TypeAlias = str | list['RecursiveAlias']


def check_local_recursive_alias() -> None:
    value: RecursiveAlias = ['a']


check_local_recursive_alias()
