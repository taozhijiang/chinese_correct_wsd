#!/usr/bin/python3
# -*- encoding: utf-8 -*-

#
# a script to preprocess chinese HTML pages to be used as raw corpus for
# character based tagging, like CRF and maxent

# the output would be a list of sentence, each sentence is composed of tokens.
# Token is either Chinese character, English word, or punctuation.

#
# this script will
# !1. remove all HTML tags in the input file
# !2. remove all JS and CSS
# 3. replace all spaces with newline
# 4. replace a line full of alphanumber with a newline
# 5. replace successive punctuations (including full-width puncts) with the leading one
# 6. put a newline after each punctuation of it
# 7. replace successive newlines with one newline

import sys
import codecs
from hanzi_util import is_terminator, is_punct, is_zh

def split_into_sentences_j(line):
    tokens = []
    en_token = []

    def close_token(token):
        if token:
            tokens.append(''.join(token))
            del(token[:])

    for c in line:
        if is_terminator(c):
            # close current token
            if not tokens: continue
            close_token(en_token)
            #tokens.append(c)
            yield tokens
            tokens = []
        elif is_punct(c):
            close_token(en_token)
            #tokens.append(c)
        elif is_zh(c):
            close_token(en_token)
            tokens.append(c)
        elif c == u' ' or c == u'\t':
            close_token(en_token)
        else:
            #en_token.append(c)
            pass
    if tokens:
        yield tokens

def split_into_sentences_e(line):
    tokens = []
    en_token = []

    def close_token(token):
        if token:
            tokens.append(''.join(token))
            del(token[:])

    for c in line:
        if is_terminator(c):
            # close current token
            if not tokens: continue
            close_token(en_token)
            #tokens.append(c)
            yield tokens
            tokens = []
        elif is_punct(c):
            close_token(en_token)
            #tokens.append(c)
        elif is_zh(c):
            close_token(en_token)
            tokens.append(c)
        elif c == u' ' or c == u'\t':
            close_token(en_token)
        else:
            #en_token.append(c)
            pass
    if tokens:
        yield tokens

def split_into_sentences(line):
    tokens = []
    en_token = []

    def close_token(token):
        if token:
            tokens.append(''.join(token))
            del(token[:])

    for c in line:
        if is_terminator(c):
            # close current token
            if not tokens: continue
            close_token(en_token)
            tokens.append(c)
            yield tokens
            tokens = []
        elif is_punct(c):
            close_token(en_token)
            tokens.append(c)
        elif is_zh(c):
            close_token(en_token)
            tokens.append(c)
        elif c == u' ' or c == u'\t':
            close_token(en_token)
        else:
            en_token.append(c)
    if tokens:
        yield tokens

def process(input):
    for line in input:
        for sentence in split_into_sentences(line.strip()):
            yield sentence

def print_sentence(sentence):
    s = u' '.join(sentence)
    print (s)

if __name__ == "__main__":
    for fn in sys.argv[1:]:
        with codecs.open(fn, 'r', 'utf-8') as f:
            for sentence in process(f):
                print_sentence(sentence)
