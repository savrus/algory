#!/usr/bin/python3
#
# Copyright (c) 2014, savrus
#

class CartesianTreeNode:
    def __init__(self, key, priority, data=None):
        self.key = key
        self.prio = priority
        self.data = data
        self.p = None
        self.c = [None, None]
    #construct Cartesian Tree from list l of Nodes
    @staticmethod
    def construct(l):
        def recursive(l):
            if len(l) == 0: return None
            n = l[0]
            for i in l:
                if i.prio < n.prio: n = i
            ll, lr = [], []
            for i in l:
                if i.key < n.key: ll.append(i)
                elif i is not n: lr.append(i)
            n.c[0], n.c[1] = recursive(ll), recursive(lr)
            #for right in (0,1):
            #    if n.c[right]: n.c[right].p = n
            return n
        return recursive(l)
    #construct Cartesian Tree from list l of Nodes sorted by key
    @staticmethod
    def constructSorted(l):
        if len(l) == 0: return None
        root = last = l[0]
        for i in l[1:]:
            while last is not None and last.prio > i.prio: last = last.p
            if last is None: i.c[0], root.p, root = root, i, i
            else:
                i.p, i.c[0], last.c[1] = last, last.c[1], i
                if i.c[0] != None: i.c[0].p = i
            last = i
        return root
    @staticmethod
    def query(n, x1, x2, k1, k2):
        def yieldsubtree(n):
            nonlocal x1, x2
            if n is None or n.prio > x2: raise StopIteration
            if n.prio >= x1: yield n
            for right in (0,1):
                for i in yieldsubtree(n.c[right]): yield i
        def traverse(n, right):
            nonlocal x1, x2, k1, k2
            while n is not None:
                if n.prio > x2: raise StopIteration
                if (n.key <= k2 if right else n.key >= k1):
                    if n.prio >= x1: yield n
                    for i in yieldsubtree(n.c[1-right]): yield i
                    n = n.c[right]
                else: n = n.c[1-right]
        while n != None and n.prio <= x2 and (n.key < k1 or n.key > k2):
            n = n.c[0] if n.key > k2 else n.c[1]
        if n == None or n.prio > x2: raise StopIteration
        if n.prio >= x1: yield n
        for right in (0,1):
            for i in traverse(n.c[right],right): yield i

class KDTree:
    class _Node:
        def __init__(self, pivot, children, point=None, data=None):
            self.pivot = pivot
            self.c = children
            self.point = point
            self.data = data
    def _u(self):
        self._unique += 1
        return self._unique
    # k is dimension, l is list of (point, data), point is list of coordinates
    def __init__(self, k, l):
        self._unique = 0
        self.k = k
        def recursive(s,i):
            pivot = s[i][(len(s[i])-1)//2][0][i]
            if len(s[i]) == 1: return self._Node(pivot, None, s[i][0][0], s[i][0][1])
            l = [[p for p in s[j] if p[0][i] <= pivot ] for j in range(k)]
            r = [[p for p in s[j] if p[0][i] >  pivot ] for j in range(k)]
            return self._Node(pivot, [recursive(l, (i+1) % k), recursive(r, (i+1) % k)])
        l = [([(x,self._u()) for x in p[0]], p[1]) for p in l]
        s = [sorted(list(l), key = lambda p: p[0][i]) for i in range(k)]
        self.low = [s[i][0][0][i][0] for i in range(k)]
        self.up = [s[i][-1][0][i][0] for i in range(k)]
        self.root = recursive(s, 0)
    # low, up are list of bounds per coordinates
    def query(self, low, up):
        def recursive(n,low,up,i):
            if n.c == None:
                if all((low[i] <= n.point[i] <= up[i] for i in range(self.k))): yield n.data
            else:
                if low[i] <= n.pivot:
                    for x in recursive(n.c[0],low,up, (i+1) % self.k): yield x
                if up[i] >= n.pivot:
                    for x in recursive(n.c[1],low,up, (i+1) % self.k): yield x
        low = [(low[i] if low[i] is not None else self.low[i],0) for i in range(self.k)]
        up = [(up[i] if up[i] is not None else self.up[i],self._unique) for i in range(self.k)]
        for x in recursive(self.root,low,up,0): yield x

###############################################################################
# Testing


def geometry_test():
    from random import randint
    def test_Cartesian1():
        N = 10000
        for ii in range(1000):
            l1 = []
            l2 = []
            for i in range(1000):
                x, y = randint(0,N), randint(0,N)
                l1.append(CartesianTreeNode(x,y))
                l2.append(CartesianTreeNode(x,y))
            p = CartesianTreeNode.constructSorted(sorted(l1, key = lambda x: x.key))
            r = CartesianTreeNode.construct(l2)
            for i in range(1000):
                x1 = randint(0, N-1)
                x2 = randint(x1, N)
                y1 = randint(0, N-1)
                y2 = randint(y1, N)
                res1 = [(i.prio, i.key) for i in CartesianTreeNode.query(r, x1, x2, y1, y2)]
                res2 = [(i.prio, i.key) for i in CartesianTreeNode.query(p, x1, x2, y1, y2)]
                res3 = [(i.prio, i.key) for i in l1 if x1 <= i.prio <= x2 and y1 <= i.key <= y2]
                if not  sorted(res1) == sorted(res2) == sorted(res3):
                    print("query %s %s %s %s\n res1: %s\n res2: %s\n res3: %s" % (x1,x2,y1,y2,sorted(res1),sorted(res2),sorted(res3)))
                assert sorted(res1) == sorted(res2) == sorted(res3)
        print("Test Cartesian1 passed")
    def test_KDTree():
        def S(a,b): return a if a is not None else b
        N = 10000
        k = 20
        l = [[randint(0,1000) for i in range(k)] for j in range(N)]
        kd = KDTree(k, [(p,p) for p in l])
        for jj in range(1000):
            low = [randint(0,999) for i in range(k)]
            up = [randint(low[i], 1000) for i in range(k)]
            low[0] = None
            up[-1] = None
            r1 = [x for x in l if all([S(low[i],-1) <= x[i] <= S(up[i],10000) for i in range(k)])]
            r2 = [x for x in kd.query(low, up)]
            assert sorted(r1) == sorted(r2)
    test_Cartesian1()
    test_KDTree()

if __name__ == "__main__": geometry_test()
