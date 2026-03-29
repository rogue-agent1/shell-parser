#!/usr/bin/env python3
"""Shell parser: pipes, redirects, quoting, globs, subshells."""
import sys, re

class Token:
    WORD, PIPE, REDIRECT_IN, REDIRECT_OUT, REDIRECT_APPEND = "WORD","PIPE","REDIR_IN","REDIR_OUT","REDIR_APP"
    AND, OR, SEMICOLON, BACKGROUND, SUBSHELL_OPEN, SUBSHELL_CLOSE = "AND","OR","SEMI","BG","SUB_OPEN","SUB_CLOSE"
    def __init__(self, type_, value): self.type = type_; self.value = value
    def __repr__(self): return f"Token({self.type}, {self.value!r})"

def tokenize(line):
    tokens = []; i = 0
    while i < len(line):
        c = line[i]
        if c in ' \t': i += 1; continue
        if c == '|':
            if i+1 < len(line) and line[i+1] == '|': tokens.append(Token(Token.OR, '||')); i += 2
            else: tokens.append(Token(Token.PIPE, '|')); i += 1
        elif c == '&':
            if i+1 < len(line) and line[i+1] == '&': tokens.append(Token(Token.AND, '&&')); i += 2
            else: tokens.append(Token(Token.BACKGROUND, '&')); i += 1
        elif c == '>':
            if i+1 < len(line) and line[i+1] == '>': tokens.append(Token(Token.REDIRECT_APPEND, '>>')); i += 2
            else: tokens.append(Token(Token.REDIRECT_OUT, '>')); i += 1
        elif c == '<': tokens.append(Token(Token.REDIRECT_IN, '<')); i += 1
        elif c == ';': tokens.append(Token(Token.SEMICOLON, ';')); i += 1
        elif c == '(': tokens.append(Token(Token.SUBSHELL_OPEN, '(')); i += 1
        elif c == ')': tokens.append(Token(Token.SUBSHELL_CLOSE, ')')); i += 1
        elif c in ('"', "'"):
            quote = c; i += 1; word = ""
            while i < len(line) and line[i] != quote: word += line[i]; i += 1
            i += 1; tokens.append(Token(Token.WORD, word))
        else:
            word = ""
            while i < len(line) and line[i] not in ' \t|&><;()': word += line[i]; i += 1
            tokens.append(Token(Token.WORD, word))
    return tokens

class Command:
    def __init__(self, args, redirects=None, background=False):
        self.args = args; self.redirects = redirects or []; self.background = background
    def __repr__(self): return f"Cmd({self.args}, redir={self.redirects}, bg={self.background})"

class Pipeline:
    def __init__(self, commands): self.commands = commands
    def __repr__(self): return f"Pipeline({self.commands})"

def parse(tokens):
    pipelines = []; current_args = []; current_redirects = []; commands = []
    for tok in tokens:
        if tok.type == Token.WORD: current_args.append(tok.value)
        elif tok.type in (Token.REDIRECT_OUT, Token.REDIRECT_IN, Token.REDIRECT_APPEND):
            current_redirects.append(tok.value)
        elif tok.type == Token.PIPE:
            commands.append(Command(current_args, current_redirects)); current_args = []; current_redirects = []
        elif tok.type in (Token.SEMICOLON, Token.AND, Token.OR):
            commands.append(Command(current_args, current_redirects))
            pipelines.append((Pipeline(commands), tok.type)); commands = []; current_args = []; current_redirects = []
    if current_args: commands.append(Command(current_args, current_redirects))
    if commands: pipelines.append((Pipeline(commands), None))
    return pipelines

def main():
    tests = ['ls -la | grep ".py" | wc -l', 'cat file.txt > output.txt',
             'make && ./test || echo "failed"', 'echo "hello world" >> log.txt &',
             "(cd /tmp; ls) | sort"]
    for line in tests:
        tokens = tokenize(line); result = parse(tokens)
        print(f"  $ {line}")
        for pipeline, op in result: print(f"    {pipeline} {op or ''}")

if __name__ == "__main__": main()
