from __future__ import absolute_import
from __future__ import unicode_literals

import io
import re

import pytest

from tokenize_rt import _re_partition
from tokenize_rt import ESCAPED_NL
from tokenize_rt import main
from tokenize_rt import reversed_enumerate
from tokenize_rt import src_to_tokens
from tokenize_rt import Token
from tokenize_rt import tokens_to_src
from tokenize_rt import UNIMPORTANT_WS


def test_re_partition_no_match():
    ret = _re_partition(re.compile('z'), 'abc')
    assert ret == ('abc', '', '')


def test_re_partition_match():
    ret = _re_partition(re.compile('b'), 'abc')
    assert ret == ('a', 'b', 'c')


def test_src_to_tokens_simple():
    src = 'x = 5\n'
    ret = src_to_tokens(src)
    assert ret == [
        Token('NAME', 'x', line=1, utf8_byte_offset=0),
        Token(UNIMPORTANT_WS, ' ', line=None, utf8_byte_offset=None),
        Token('OP', '=', line=1, utf8_byte_offset=2),
        Token(UNIMPORTANT_WS, ' ', line=None, utf8_byte_offset=None),
        Token('NUMBER', '5', line=1, utf8_byte_offset=4),
        Token('NEWLINE', '\n', line=1, utf8_byte_offset=5),
        Token('ENDMARKER', '', line=2, utf8_byte_offset=0),
    ]


def test_src_to_tokens_escaped_nl():
    src = (
        'x = \\\n'
        '    5'
    )
    ret = src_to_tokens(src)
    assert ret == [
        Token('NAME', 'x', line=1, utf8_byte_offset=0),
        Token(UNIMPORTANT_WS, ' ', line=None, utf8_byte_offset=None),
        Token('OP', '=', line=1, utf8_byte_offset=2),
        Token(UNIMPORTANT_WS, ' ', line=None, utf8_byte_offset=None),
        Token(ESCAPED_NL, '\\\n', line=None, utf8_byte_offset=None),
        Token(UNIMPORTANT_WS, '    ', line=None, utf8_byte_offset=None),
        Token('NUMBER', '5', line=2, utf8_byte_offset=4),
        Token('ENDMARKER', '', line=3, utf8_byte_offset=0),
    ]


def test_src_to_tokens_escaped_nl_no_left_ws():
    src = (
        'x =\\\n'
        '    5'
    )
    ret = src_to_tokens(src)
    assert ret == [
        Token('NAME', 'x', line=1, utf8_byte_offset=0),
        Token(UNIMPORTANT_WS, ' ', line=None, utf8_byte_offset=None),
        Token('OP', '=', line=1, utf8_byte_offset=2),
        Token(ESCAPED_NL, '\\\n', line=None, utf8_byte_offset=None),
        Token(UNIMPORTANT_WS, '    ', line=None, utf8_byte_offset=None),
        Token('NUMBER', '5', line=2, utf8_byte_offset=4),
        Token('ENDMARKER', '', line=3, utf8_byte_offset=0),
    ]


def test_src_to_tokens_escaped_nl_windows():
    src = (
        'x = \\\r\n'
        '    5'
    )
    ret = src_to_tokens(src)
    assert ret == [
        Token('NAME', 'x', line=1, utf8_byte_offset=0),
        Token(UNIMPORTANT_WS, ' ', line=None, utf8_byte_offset=None),
        Token('OP', '=', line=1, utf8_byte_offset=2),
        Token(UNIMPORTANT_WS, ' ', line=None, utf8_byte_offset=None),
        Token(ESCAPED_NL, '\\\r\n', line=None, utf8_byte_offset=None),
        Token(UNIMPORTANT_WS, '    ', line=None, utf8_byte_offset=None),
        Token('NUMBER', '5', line=2, utf8_byte_offset=4),
        Token('ENDMARKER', '', line=3, utf8_byte_offset=0),
    ]


@pytest.mark.parametrize(
    'filename',
    (
        'testing/resources/empty.py',
        'testing/resources/unicode_snowman.py',
        'testing/resources/backslash_continuation.py',
    ),
)
def test_roundtrip_tokenize(filename):
    with io.open(filename) as f:
        contents = f.read()
    ret = tokens_to_src(src_to_tokens(contents))
    assert ret == contents


def test_reversed_enumerate():
    tokens = src_to_tokens('x = 5')
    ret = reversed_enumerate(tokens)
    assert next(ret) == (5, Token('ENDMARKER', '', line=2, utf8_byte_offset=0))

    rest = list(ret)
    assert rest == [
        (4, Token('NUMBER', '5', line=1, utf8_byte_offset=4)),
        (3, Token(UNIMPORTANT_WS, ' ')),
        (2, Token('OP', '=', line=1, utf8_byte_offset=2)),
        (1, Token(UNIMPORTANT_WS, ' ')),
        (0, Token('NAME', 'x', line=1, utf8_byte_offset=0)),
    ]


def test_main(capsys):
    main(('testing/resources/simple.py',))
    out, _ = capsys.readouterr()
    assert out == (
        "1:0 NAME 'x'\n"
        "?:? UNIMPORTANT_WS ' '\n"
        "1:2 OP '='\n"
        "?:? UNIMPORTANT_WS ' '\n"
        "1:4 NUMBER '5'\n"
        "1:5 NEWLINE '\\n'\n"
        "2:0 ENDMARKER ''\n"
    )
