#!/usr/bin/python3
#
# Copyright (c) 2013, savrus
#

class SplayTree:
    class Node:
        def __init__(self, key):
            self.p = None
            self.c = [None, None]
            self.k = key
    def zig(self, n):
        p = n.p
        if p.p: p.p.c[p == p.p.c[1]] = n
        right = n == p.c[1]
        p.p, n.p, p.c[right], n.c[1-right] = n, p.p, n.c[1-right], p
        if p.c[right] != None: p.c[right].p = p
    def zigzig(self, n):
        self.zig(n.p)
        self.zig(n)
    def zigzag(self, n):
        self.zig(n)
        self.zig(n)
    def splay(self, n):
        while n.p:
            if n.p.p == None: self.zig(n)
            else:
                if (n == n.p.c[1]) == (n.p == n.p.p.c[1]): self.zigzig(n)
                else: self.zigzag(n)
        self.root = n
    def access(self, key):
        n = self.root
        if n == None: return n
        while n.k != key and n.c[n.k < key]: n = n.c[n.k < key]
        self.splay(n)
        return n
    def split(self, key):
        n = self.access(key)
        if n == None: return None, None
        right = n.k < key
        t, n.c[right] = n.c[right], None
        if right: return n, t
        else: return t, n
    def join(self, l, r):
        if l == None:
            self.root = r
            return
        self.root = l
        if r:
            while l.c[1]: l = l.c[1]
            self.splay(l)
            l.c[1] = r
            r.p = l

    def add(self, key):
        n = self.Node(key)
        n.c[0], n.c[1] = self.split(key)
        for i in range(2):
            if n.c[i] != None: n.c[i].p = n
        self.root = n
    def remove(self, key):
        n = self.access(key)
        if n and n.k == key:
            for i in range(2):
                if n.c[i]: n.c[i].p = None
            self.join(n.c[0], n.c[1])
        else: raise KeyError
    def __contains__(self, key):
        n = self.access(key)
        return n and n.k == key
    def __init__(self):
        self.root = None

class RBTree:
    class Node:
        def __init__(self, key, black = True):
            self.p = None
            self.c = [None, None]
            self.k = key
            self.b = black
    def rotate(self, n):
        p = n.p
        if p.p: p.p.c[p == p.p.c[1]] = n
        else: self.root = n
        right = n == n.p.c[1]
        p.p, n.p, p.c[right], n.c[1-right] = n, p.p, n.c[1-right], p
        if p.c[right]: p.c[right].p = p
    def access(self, key):
        n = self.root
        if n == None: return None
        while n.k != key and n.c[n.k < key]: n = n.c[n.k < key]
        return n
    def sibling(self, n):
        return n.p.c[n != n.p.c[1]]
    
    def add(self, key):
        p = self.root
        if p == None: self.root = self.Node(key)
        else:
            while p.c[p.k < key]: p = p.c[p.k < key]
            n = self.Node(key, False)
            p.c[p.k < n.k], n.p = n, p
            while n.p and not n.p.b:
                p = n.p
                pright = p == p.p.c[1]
                y = p.p.c[1-pright]
                if y and not y.b: p.b, y.b, p.p.b, n = True, True, False, p.p
                else:
                    if n != p.c[pright]:
                        self.rotate(n)
                        n, p = p, n
                    p.b, p.p.b = True, False
                    self.rotate(p)
            if not n.p: n.b = True
    def remove(self, key):
        n = self.access(key)
        if not n or n.k != key: raise KeyError
        if n.c[0] and n.c[1]:
            m = n.c[1]
            while m.c[0]: m = m.c[0]
            n.k, n = m.k, m
        if n.c[0] or n.c[1]: n.k, n.c[n.c[1] != None] = n.c[n.c[1] != None].k, None
        elif not n.p: self.root = None
        else:
            d = n
            while n.b and n.p:
                w = self.sibling(n)
                if not w.b:
                    self.rotate(w)
                    w.b, n.p.b, w = True, False, self.sibling(n)
                if all([not w.c[i] or w.c[i].b for i in [0,1]]): w.b, n = False, n.p
                else:
                    right = n == n.p.c[1]
                    if w.c[right] and not w.c[right].b:
                        w.b, w.c[right].b, w = False, True, w.c[right]
                        self.rotate(w)
                    self.rotate(w)
                    w.b, n.p.b, w.c[1-right].b = n.p.b, True, True
                    n = self.root
            n.b = True
            d.p.c[d == d.p.c[1]] = None
    def __contains__(self, key):
        n = self.access(key)
        return n and n.k == key
    def __init__(self):
        self.root = None


###############################################################################
# Testing
def tree_test():
    from random import randint
    def rbcheck(self):
        assert(not self.root or self.root.b)
        def sub(n):
            if not n: return 0
            if not n.b: assert(all([not n.c[i] or n.c[i].b for i in [0,1]]))
            l, r = sub(n.c[0]), sub(n.c[1])
            assert(l==r)
            return l + n.b
        sub(self.root)
    def test_TreeAsSet(t):
        s = set()
        for i in range(100000):
            x = randint(1,10000)
            assert (x in t) == (x in s)
            if x in t:
                t.remove(x)
                s.remove(x)
            else:
                t.add(x)
                s.add(x)
        print("Test Tree-as-Set passed");
    def test_RBTree():
        t = RBTree()
        for i in range(10000):
            x = randint(1,1000)
            if x in t:
                t.remove(x)
                rbcheck(t)
            else:
                t.add(x)
                rbcheck(t)
        print("Test RBTree passed");
    def test_TreeAsMultiset():
        t = RBTree()
        s = SplayTree()
        for i in range(10000):
            x = randint(1,100)
            assert (x in t) == (x in s)
            if x in t and randint(0,10) > 6:
                t.remove(x)
                s.remove(x)
            else:
                t.add(x)
                s.add(x)
            rbcheck(t)
        print("Test Tree-as-MultySet passed");
    test_TreeAsSet(SplayTree())
    test_TreeAsSet(RBTree())
    test_RBTree()
    test_TreeAsMultiset()

if __name__ == "__main__": tree_test()
