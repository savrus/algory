#!/usr/bin/python3
#
# Copyright (c) 2013-2014, savrus
#

def ZFunction(s):
    z = [len(s)] if len(s) > 0 else []
    last = 0
    lasti = 0
    for i in range(1, len(s)):
        t = 0
        if i < last: t = min(z[i-lasti], last - i)
        if i+t >= last:
            lasti = i
            while i+t < len(s) and s[i+t] == s[t]: t += 1
            last = i + t
        z.append(t)
    return z

def PrefixFunction(s):
    p = [0] if len(s) > 0 else []
    for i in range(1,len(s)):
        t = p[i-1]
        while t > 0 and s[t] != s[i]: t = p[t-1]
        if s[t] == s[i]: t += 1
        else: assert(t == 0)
        p.append(t)
    return(p)

def ZFunction2PrefixFunction(z):
    p = [0] if len(z) > 0 else []
    last = 1
    for i in range(1, len(z)):
        for j in range(last, i+z[i]): p.append(j-i+1)
        last = max(last,i+z[i])
    if last == len(z)-1: p.append(0)
    return p    

def PrefixFunction2ZFunction(p):
    z = [len(p)] if len(p) > 0 else []
    last = 0
    lasti = 0
    for i in range(1, len(p)):
        t = 0
        if i < last: t = min(z[i-lasti], last - i)
        if i+t >= last:
            lasti = i
            while i+t < len(p) and p[i+t] == t+1: t += 1
            last = i + t
        z.append(t)
    return z

class SuffixTree:
    # Nodes are of class Node. Node.out is a dict which contains outgoing edges. Keys are first characters.
    # Edges are lists of 3 element: [start, end, target node].
    # If target node is a leaf, it is None and so is the end.
    # Tree is traversed by Position. If Position.edge is None, we are at a node Position.node.
    # Oherwise we are at edge Position.edge skipping Position.skip characters.
    # After Position.way() and Position.link() we are either at a node or in the middle of edge.
    # After split() we are at the end of the edge (skip equals edge length), but we don't go there
    # because our link is at the beginning of the edge and we are going to use it right after split()
    class Node:
        def __init__(self):
            self.out = {}
            self.link = None
        def way(self, c):
            return self.out.get(c, None)
    class Position:
        def __init__(self, s, node):
            self.s = s
            self.node = node
            self.edge = None
            self.skip = None
        # Try to extend position by character 'c'. Returns True on success, False otherwise
        def way(self, c):
            if self.edge == None:
                self.edge = self.node.way(c)
                if self.edge == None: return False
                self.skip = 1
            else:
                if c == self.s[self.edge[0]+self.skip]: self.skip += 1
                else: return False
            if self.edge[0] + self.skip == self.edge[1]:
                self.node = self.edge[2]
                self.edge = None
            return True
        # Go by link. Return True on success, False otherwise (= we are already at root)
        def link(self):
            if self.edge == None:
                if self.node.link == None: return False
                self.node = self.node.link
            else:
                k = self.edge[0]
                if self.node.link == None:
                    k += 1
                    self.skip -= 1
                else:
                    self.node = self.node.link
                edge = None
                while self.skip > 0 and edge == None:
                    edge = self.node.out[self.s[k]]
                    if edge[1] != None and edge[1]-edge[0] <= self.skip:
                        #assert(self.s[edge[0]:edge[1]] == self.s[k:k+edge[1]-edge[0]])
                        self.skip -= edge[1]-edge[0]
                        k += edge[1]-edge[0]
                        self.node = edge[2]
                        edge = None
                self.edge = edge
            return True
    # Append new leaf to the node
    def addleaf(self, node, i):
        assert(node.way(self.s[i]) == None)
        node.out[self.s[i]] = [i, None, None]
    # Split edge at current position. We stay at old node
    def split(self, p):
        assert(p.skip > 0 and (p.edge[1] == None or p.edge[0] + p.skip < p.edge[1]))
        node = self.Node()
        node.out[self.s[p.edge[0]+p.skip]] = [p.edge[0]+p.skip, p.edge[1], p.edge[2]]
        p.edge[1:3] = [p.edge[0] + p.skip, node]
    # Construct Suffix Tree
    def __init__(self, s):
        self.endsymbol = chr(0)
        self.s = s + self.endsymbol
        self.root = self.Node()
        p = self.Position(self.s, self.root)
        for i in range(len(self.s)):
            prev = None
            while not p.way(self.s[i]):
                n = p.node
                if p.edge != None:
                    self.split(p)
                    n = p.edge[2]
                if prev:
                    assert(prev.link == None or prev.link == n)
                    prev.link = n
                prev = n
                self.addleaf(n,i)
                if not p.link():
                    assert(p.node == self.root)
                    break
                # if We are at edge, next time we will split it and create a node for link
                # but if we are already at a node, there is no guarantee that the loop will continue
                if p.edge == None:
                    assert(prev.link == None or prev.link == p.node)
                    prev.link = p.node
    # Search string in the tree. Succes if we finish matching at a leaf.
    def __contains__(self, string):
        string += self.endsymbol
        i = 0
        n = self.root
        e = None
        while i < len(string):
            if string[i] not in n.out.keys(): return False
            e = n.out[string[i]]
            eend = e[1] if e[1] != None else len(self.s)
            #if string[i:i + eend-e[0]] != self.s[e[0]:eend]: return False
            if not self.s.startswith(string[i:i + eend-e[0]], e[0], eend): return False
            i += eend-e[0]
            n = e[2]
        return e == None or e[1] == None
    # Iterate over all strings in the tree
    def __iter__(self):
        stack = [ (self.root, iter(sorted(self.root.out.items())), 0) ]
        ss = ""
        while len(stack) > 0:
            node, it, plen = stack[-1]
            try: k, edge = next(it)
            except StopIteration:
                stack.pop()
                ss = ss[:-plen]
                continue
            if edge[2] == None: yield ss + self.s[edge[0]:-len(self.endsymbol)]
            else:
                stack.append((edge[2], iter(sorted(edge[2].out.items())), edge[1]-edge[0]))
                ss += self.s[edge[0]:edge[1]]
    # Return Suffix Array
    def SA(self):
        stack = [ (self.root, iter(sorted(self.root.out.items())), 0) ]
        l = 0
        sa = []
        while len(stack) > 0:
            node, it, plen = stack[-1]
            try: k, edge = next(it)
            except StopIteration:
                stack.pop()
                l -= plen
                continue
            if edge[2] == None:
                ll = l + len(self.s) - edge[0]
                if ll > 1: sa.append(len(self.s)-ll)
            else:
                stack.append((edge[2], iter(sorted(edge[2].out.items())), edge[1]-edge[0]))
                l += edge[1] - edge[0]
        return sa
    # Represent the entire Suffix Tree as a string (for debugging)
    def string(self, i):
        stack = [(self.root, 0)]
        n = 1
        s = ""
        while len(stack) > 0:
            node, node_id = stack.pop()
            s += "%s:" % node_id
            for k, e in node.out.items():
                if e[2] != None:
                    s += " (%s)\'%s\'[%s:%s]->%s" % (k, self.s[e[0]:e[1]],e[0],e[1], n)
                    stack.append((e[2], n))
                    n += 1
                else:
                    s += " (%s)\'%s\'[%s:%s]->leaf" % (k, self.s[e[0]:i],e[0],i)
            s += "\n"
        return s
    def __str__(self): return self.string(None)

def _string_test():
    import random
    A = "abcdefghijklmnopqrstuvwxyz"
    def StringGenerator(length, alphabet):
        s = [0]*length
        while 1:
            yield "".join([alphabet[x] for x in s])
            p = length - 1
            while p >= 0 and s[p] == len(alphabet) - 1:
                s[p] = 0
                p -= 1
            if p == -1: return
            s[p] += 1
    def ZFunctionSlow(s):
        z = []
        for i in range(0,len(s)):
            l = 0
            while i+l < len(s) and s[l] == s[i+l]: l += 1
            z.append(l)
        return z
    def PrefixFunctionSlow(s):
        p = [0] if len(s) > 0 else []
        for i in range(1, len(s)):
            l = 0
            for t in range(0,i):
                if s[0:t+1] == s[i-t:i+1]: l = t+1
            p.append(l)
        return p
    def test_ZFunction_PrefixFunction():
        for l in range(0,7):
            for s in StringGenerator(l, A[0:l]):
                assert(PrefixFunctionSlow(s) == PrefixFunction(s))
                assert(ZFunctionSlow(s) == ZFunction(s))
                assert(ZFunction2PrefixFunction(ZFunction(s)) == PrefixFunction(s))
                assert(ZFunction(s) == PrefixFunction2ZFunction(PrefixFunction(s)))
        print("Test ZFunction_PrefixFunction Passed")
    def SuffixArraySlow(s):
        suff = []
        for i in range(len(s)):
            suff.append(s[i:])
        sa = []
        for i in sorted(suff):
            sa.append(len(s) - len(i))
        return sa
    def test_SuffixTree():
        assert "aba" not in SuffixTree("aabba")
        line =  "".join([A[random.randrange(len(A))] for i in range(100000)])
        t = SuffixTree(line)
        for i in range(len(line)): assert line[i:] in t
        for s in t: assert line.endswith(s)
        print("Test Suffix Tree Passed")
    def test_SuffixArray():
        line =  "".join([A[random.randrange(len(A))] for i in range(100000)])
        assert(SuffixArraySlow(line) == SuffixTree(line).SA())
        print("Test Suffix Array Passed")
    test_ZFunction_PrefixFunction()
    test_SuffixTree()
    test_SuffixArray()

if __name__ == "__main__": _string_test()
