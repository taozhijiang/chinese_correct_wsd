#!/usr/bin/python3
# -*- encoding: utf-8 -*-

from curses import ascii

def is_zhs(str):
    for i in str:
        if not is_zh(i):
            return False
    return True

def is_zh(ch):
    """return True if ch is Chinese character.
    full-width puncts/latins are not counted in.
    """
    x = ord(ch)
    # CJK Radicals Supplement and Kangxi radicals
    if 0x2e80 <= x <= 0x2fef:
        return True
    # CJK Unified Ideographs Extension A
    elif 0x3400 <= x <= 0x4dbf:
        return True
    # CJK Unified Ideographs
    elif 0x4e00 <= x <= 0x9fbb:
        return True
    # CJK Compatibility Ideographs
    elif 0xf900 <= x <= 0xfad9:
        return True
    # CJK Unified Ideographs Extension B
    elif 0x20000 <= x <= 0x2a6df:
        return True
    else:
        return False

def is_punct(ch):
    x = ord(ch)
    # in no-formal literals, space is used as punctuation sometimes.
    if x < 127 and ascii.ispunct(x):
        return True
    # General Punctuation
    elif 0x2000 <= x <= 0x206f:
        return True
    # CJK Symbols and Punctuation
    elif 0x3000 <= x <= 0x303f:
        return True
    # Halfwidth and Fullwidth Forms
    elif 0xff00 <= x <= 0xffef:
        return True
    # CJK Compatibility Forms
    elif 0xfe30 <= x <= 0xfe4f:
        return True
    else:
        return False

def is_terminator(ch):
    return ch in (u'!', u'?', u',', u';', u'.', u'！', u'？', u'，', u'。', u'…')

chinese_number = (u'十', u'百', u'千', u'万', u'亿', u'一', u'二', u'三', u'四', u'五', u'六', u'七', u'八', u'九', u'零', u'几')
def is_zh_number(ch):
    return ch in chinese_number

if __name__ == "__main__":
    print(is_zhs('市长'))
    print(is_zhs('23市'))
    print(is_zhs('大'))
    print(is_zhs('我有24'))
