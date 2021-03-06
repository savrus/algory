#!/usr/bin/python3
#
# Copyright (c) 2013-2014, savrus
#

class SplayTreeBase:
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

class RBTreeBase:
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

class SplayTree(SplayTreeBase):
    def slide(self, n, side):
        while n.c[side]: n = n.c[side]
        self.splay(n)
        return n.k
    def smthessor(self, k, side):
        n = self.access(k)
        if (n.k < k, n.k > k)[side]: return n.k
        if not n.c[side]: return None
        n = n.c[side]
        r = n.k if n.k != k else None
        while n.c[1-side if n.k != k else side]:
            n = n.c[1-side if n.k != k else side]
            if n.k != k: r = n.k
        self.splay(n)
        return r

    def max(self):
        return self.slide(self.root, 1) if self.root else None
    def min(self):
        return self.slide(self.root, 0) if self.root else None
    def successor(self, k):
        return self.smthessor(k, 1) if self.root else None
    def predecessor(self, k):
        return self.smthessor(k, 0) if self.root else None
    def __iter__(self):
        def r(n):
            if n == None: raise StopIteration
            for x in r(n.c[0]): yield x
            yield n
            for x in r(n.c[1]): yield x
        for x in r(self.root): yield x

class RBTree(RBTreeBase):
    def slide(self, n, side):
        while n.c[side]: n = n.c[side]
        return n.k
    def smthessor(self, k, side):
        n = self.access(k)
        if (n.k < k, n.k > k)[side]: return n.k
        m, r = n.c[side], None
        while m:
            if m.k != k: r = m.k
            m = m.c[1-side if m.k != k else side]
        if r != None: return r
        while n.p and n == n.p.c[side]: n = n.p
        return n.p.k if n.p else None

    def max(self):
        return self.slide(self.root, 1) if self.root else None
    def min(self):
        return self.slide(self.root, 0) if self.root else None
    def successor(self, k):
        return self.smthessor(k, 1) if self.root else None
    def predecessor(self, k):
        return self.smthessor(k, 0) if self.root else None
    def __iter__(self):
        def r(n):
            if n == None: raise StopIteration
            for x in r(n.c[0]): yield x
            yield n
            for x in r(n.c[1]): yield x
        for x in r(self.root): yield x

class _vanEmdeBoarsNode:
    def __init__(self, l):
        self._u = 1 << l
        self._l = l
        self._m = [None,None]
        self._s = None
        self._cluster = dict()
    def _check(self, x): assert 0 <= x < self._u
    def _high(self, x): return x >> (self._l//2)
    def _low(self, x): return x & ((1 << (self._l//2))-1)
    def _index(self, x, y): return (x << (self._l//2)) + y
    def _c(self,x): return self._cluster.get(self._high(x), None)
    def _smthecessor(self, x, side):
        self._check(x)
        if self._u == 2: return side if x == 1-side and self._m[side] == side else None
        elif self.min() != None and (x < self._m[0] if side else x > self._m[1]): return self._m[1-side]
        else:
            m = self._c(x)._m[side] if self._c(x) else None
            if m != None and (self._low(x) < m if side else self._low(x) > m):
                return self._index(self._high(x), self._c(x)._smthecessor(self._low(x), side))
            else:
                sc = self._s._smthecessor(self._high(x), side) if self._s else None
                if sc == None:
                    if side == 0 and self.min() != None and x > self.min(): return self.min()
                    return None
                return self._index(sc, self._cluster[sc]._m[1-side])

    def min(self): return self._m[0]
    def max(self): return self._m[1]
    def __contains__(self,x):
        self._check(x)
        if x in self._m: return True
        if self._u == 2: return False
        return self._low(x) in self._c(x) if self._c(x) else False
    def successor(self, x): return self._smthecessor(x, 1)
    def predecessor(self, x): return self._smthecessor(x, 0)
    def add(self,x):
        self._check(x)
        if x in self._m: raise KeyError
        if self.min() == None: self._m[0] = self._m[1] = x
        else:
            if x < self.min(): self._m[0], x = x, self._m[0]
            if self._u > 2:
                if not self._c(x): self._cluster[self._high(x)] = _vanEmdeBoarsNode(self._l//2)
                if not self._s: self._s = _vanEmdeBoarsNode(self._l - self._l//2)
                if self._c(x).min() == None: self._s.add(self._high(x))
                self._c(x).add(self._low(x))
            if x > self.max(): self._m[1] = x
    def remove(self, x):
        self._check(x)
        if self._m[0] == self._m[1]:
            if x != self._m[0]: raise KeyError
            self._m[0] = self._m[1] = None
        elif self._u == 2:
            if x not in self._m: raise KeyError
            self._m[0] = self._m[1] = 1 if x == 0 else 0
        else:
            if x == self.min():
                sc = self._s.min()
                x = self._index(sc, self._cluster[sc].min())
                self._m[0] = x
            self._c(x).remove(self._low(x))
            if self._c(x).min() == None:
                self._cluster.pop(self._high(x))
                self._s.remove(self._high(x))
                if x == self.max():
                    sm = self._s.max()
                    if sm == None:
                        self._m[1] = self._m[0]
                        self._s = None
                    else: self._m[1] = self._index(m, self._cluster[sm].max())
            elif x == self.max():
                self._m[1] = self._index(self._high(x), self._c(x).max())
    def __str__(self):
        return "u:%s l:%s m:%s s:(%s) c:[%s]" % (self._u, self._l, self._m, self._s, ",\n".join([str(n) for n in self.c]) if self.c else None)

class vanEmdeBoarsTree(_vanEmdeBoarsNode):
    def __init__(self,universe):
        super().__init__(1 if universe <= 1 else 1 + (lambda a:lambda v,l:a(a,v,l))(lambda s,x,l: 0 if not l else l+s(s,x>>l,l) if x>>l else s(s,x,l>>1))(universe,(lambda a:lambda v,l:a(a,v,l))(lambda s,x,l: l if (x >> (l<<1)) == 0 else s(s,x,l<<1))(universe,1)))


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
        print("Test Tree-as-Set for %s passed" % t.__class__.__name__);
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
    def test_PredSucc(t):
        s = set()
        for i in range(10000):
            x = randint(1,100000)
            assert (x in t) == (x in s)
            t.add(x)
            s.add(x)
        assert t.max() == max(s)
        assert t.min() == min(s)
        for i in range(100000):
            x = randint(0,100001)
            assert (t.successor(x) == None and x >= max(s)) or (t.successor(x) == min((y for y in s if y > x)))
            assert (t.predecessor(x) == None and x <= min(s)) or (t.predecessor(x) == max((y for y in s if y < x)))
        print("Test PredSucc for %s passed" % t.__class__.__name__)
    def test_vanEmdeBoarsTree():
        def step(t,N):
            rb = RBTree()
            for i in range(N//2):
                x = randint(1,N-1)
                assert (x in t) == (x in rb)
                if x not in t:
                    t.add(x)
                    rb.add(x)
                assert x in t
            assert t.max() == rb.max() and t.min() == rb.min()
            for x in range(N):
                assert t.successor(x) == rb.successor(x)
                assert t.predecessor(x) == rb.predecessor(x)
            for x in range(N):
                if x in t:
                    t.remove(x)
                    assert x not in t
        N = 100000
        t = vanEmdeBoarsTree(N)
        step(t,N)
        assert not t._s and len(t._cluster) == 0
        step(t,N)
        print("Test vanEmdeBoarsTree passed")
    def test_Iteration(t):
        l = []
        for i in range(10000):
            x = randint(1,100000)
            t.add(x)
            l.append(x)
        ll = [x.k for x in t]
        assert ll == sorted(l)
        print("Test Iteration for %s passed" % t.__class__.__name__)
    test_TreeAsSet(SplayTree())
    test_TreeAsSet(RBTree())
    test_RBTree()
    test_TreeAsMultiset()
    test_Iteration(RBTree())
    test_Iteration(SplayTree())
    test_PredSucc(RBTree())
    test_PredSucc(SplayTree())
    test_vanEmdeBoarsTree()

if __name__ == "__main__": tree_test()
