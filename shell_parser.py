#!/usr/bin/env python3
"""Shell command parser (pipes, redirects, quotes) — zero-dep."""
import re

def tokenize(cmd):
    tokens=[]; i=0; n=len(cmd)
    while i<n:
        if cmd[i] in " \t": i+=1; continue
        if cmd[i]=="|": tokens.append(("PIPE","|")); i+=1
        elif cmd[i:i+2]==">>": tokens.append(("APPEND",">>")); i+=2
        elif cmd[i]==">": tokens.append(("REDIR_OUT",">")); i+=1
        elif cmd[i]=="<": tokens.append(("REDIR_IN","<")); i+=1
        elif cmd[i] in "'\"":
            q=cmd[i]; j=i+1
            while j<n and cmd[j]!=q: j+=1
            tokens.append(("WORD",cmd[i+1:j])); i=j+1
        else:
            j=i
            while j<n and cmd[j] not in " \t|><": j+=1
            tokens.append(("WORD",cmd[i:j])); i=j
    return tokens

def parse(cmd):
    tokens=tokenize(cmd); commands=[]; current={"args":[],"stdin":None,"stdout":None,"append":False}
    i=0
    while i<len(tokens):
        typ,val=tokens[i]
        if typ=="PIPE":
            commands.append(current); current={"args":[],"stdin":None,"stdout":None,"append":False}
        elif typ=="REDIR_OUT" and i+1<len(tokens):
            i+=1; current["stdout"]=tokens[i][1]
        elif typ=="APPEND" and i+1<len(tokens):
            i+=1; current["stdout"]=tokens[i][1]; current["append"]=True
        elif typ=="REDIR_IN" and i+1<len(tokens):
            i+=1; current["stdin"]=tokens[i][1]
        elif typ=="WORD": current["args"].append(val)
        i+=1
    if current["args"]: commands.append(current)
    return commands

if __name__=="__main__":
    tests=["ls -la","cat file.txt | grep error | wc -l",
           "echo 'hello world' > out.txt","sort < input.txt >> output.txt",
           'grep "hello world" file.txt | sort -u']
    for cmd in tests:
        parsed=parse(cmd)
        print(f"$ {cmd}")
        for i,c in enumerate(parsed):
            parts=f"  cmd[{i}]: {c['args']}"
            if c["stdin"]: parts+=f" <{c['stdin']}"
            if c["stdout"]: parts+=f" {'>>'+c['stdout'] if c['append'] else '>'+c['stdout']}"
            print(parts)
