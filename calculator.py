#!/usr/bin/python

import sys

all_tokens = dict([
    ["_", -1],
    ["!", 0], ["~", 0], ["^", 1], ["&", 1], ["|", 1],
    ["**", 2], ["*", 3], ["/", 3], ["%", 3], ["+", 4], ["-", 4],
    ["&&", 6], ["||", 6], ["==", 7], ["!=", 7], ["<", 7], [">", 7], ["<=", 7], [">=", 7],
    ["=", 8], ["(", 99], [")", 99]])
unary = set(["!", "~", "_"])

class Token:
    OPERATOR=0
    NUMERIC=1
    VARIABLE=2
    def __init__(self, kind, token):
        self.kind = kind
        self.token = token
    def __repr__(self):
        return str(self.token)

def make_token(s):
    if s in all_tokens: return Token(Token.OPERATOR, s)
    elif s.isdigit(): return Token(Token.NUMERIC, int(s))
    elif s.isalpha(): return Token(Token.VARIABLE, s)
    else: raise Exception("Error: invalid token: '{}'".format(token))

def tokenize(s):
    tokens = []
    e = b = 0
    while e < len(s):
        if s[e] == ' ' or s[e] in all_tokens or s[e:e+2] in all_tokens:
            if b < e: tokens.append(make_token(s[b:e]))
            b = e + 1
        if s[e:e+2] in all_tokens:
            tokens.append(make_token(s[e:e+2]))
            e, b = e + 1, e + 2
        elif s[e] in all_tokens: tokens.append(make_token(s[e]))
        e += 1
    if b < len(s): tokens.append(make_token(s[b:]))
    return tokens

def parse(tokens):
    result = []
    stack = []
    expectExpr = True
    for t in tokens:
        if t.kind == Token.NUMERIC or t.kind == Token.VARIABLE:
            result.append(t)
            expectExpr = False
        else:
            if t.token == "(":
                if not expectExpr: raise Exception("Error: expected a binary operator, but got '('")
                stack.append(t)
            elif t.token == ")":
                if expectExpr: raise Exception("Error: expected an expression, but got ')'")
                while len(stack) > 0 and stack[-1].token != "(": result.append(stack.pop())
                if len(stack) == 0 or stack[-1].token != "(": raise Exception("Error: unmatched ')'")
                stack.pop()
                expectExpr = False
            elif t.token in unary:
                if not expectExpr: raise Exception("Error: expected a binary operator, but got unary operator '{}'". format(t.token))
                stack.append(t)
            elif expectExpr and t.token == "-":
                stack.append(Token(Token.OPERATOR, "_"))
            else:
                if expectExpr: raise Exception("Error: expected an expression, but got binary operator '{}'". format(t.token))
                while len(stack) > 0 and all_tokens[stack[-1].token] < all_tokens[t.token]: result.append(stack.pop())
                stack.append(t)
                expectExpr = True
    while len(stack) > 0 and stack[-1].token != "(": result.append(stack.pop())
    if len(stack) > 0: raise Exception("Error: unmatched '('")
    return result

class Calculator:
    def __init__(self):
        self.variables = {}
    def value(self, token):
        if token.kind == Token.VARIABLE:
            if token.token not in self.variables:
                raise Exception("Error: variable '{}' is referenced before assignment".format(token.token))
            else: return self.variables[token.token]
        else: return token.token
    def execute(self, tokens):
        stack = []
        tmp = {}
        def append(val):
            stack.append(Token(Token.NUMERIC, val))
        for t in tokens:
            if t.kind == Token.OPERATOR:
                if t.token == "=":
                    val = self.value(stack.pop())
                    v = stack.pop()
                    if v.kind != Token.VARIABLE:
                        raise Exception("Error: left hand of the assignment is not an l-value")
                    tmp[v.token] = val
                    append(val)
                elif t.token in unary:
                    val = self.value(stack.pop())
                    if t.token == "!": append(0 if val != 0 else 1)
                    elif t.token == "~": append(~val)
                    elif t.token == "_": append(-val)
                    else: raise Exception("Uknown operator '{}'".format(t.token))
                else:
                    rhs = self.value(stack.pop())
                    lhs = self.value(stack.pop())
                    if t.token == "+": append(lhs + rhs)
                    elif t.token == "-": append(lhs - rhs)
                    elif t.token == "*": append(lhs * rhs)
                    elif t.token == "/": append(lhs / rhs)
                    elif t.token == "%": append(lhs % rhs)
                    elif t.token == "&": append(lhs & rhs)
                    elif t.token == "|": append(lhs | rhs)
                    elif t.token == "^": append(lhs ^ rhs)
                    elif t.token == "**": append(int(lhs ** rhs))
                    elif t.token == "&&": append(1 if (lhs != 0 and rhs != 0) else 0)
                    elif t.token == "||": append(0 if (lhs == 0 and rhs == 0) else 1)
                    elif t.token == "==": append(1 if lhs == rhs else 0)
                    elif t.token == "!=": append(0 if lhs == rhs else 1)
                    elif t.token == ">": append(1 if lhs > rhs else 0)
                    elif t.token == "<": append(1 if lhs < rhs else 0)
                    elif t.token == ">=": append(1 if lhs >= rhs else 0)
                    elif t.token == "<=": append(1 if lhs <= rhs else 0)
                    else: raise Exception("Uknown operator '{}'".format(t.token))
            else: stack.append(t)
        if len(stack) > 2: raise Exception("Unfinished expression")
        self.variables.update(tmp)
        return self.value(stack[0]) if len(stack) == 1 else 0

if __name__ == "__main__":
    c = Calculator()
    while True:
        try:
            line = raw_input("> ")
            tokens = tokenize(line)
            if len(tokens) > 0:
                parsed = parse(tokens)
                result = c.execute(parsed)
                print result
        except EOFError: print; break
        except Exception as e: print e
