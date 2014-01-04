#!/usr/bin/python3
#
# Copyright (c) 2013-2014, savrus
#

class dllist():
    # Circular doubly linked list.
    # Iterator supports removal of current node (e.g. for i in list: i.detach())
    def __init__(self, data = None):
        self.next = self
        self.prev = self
        self.data = data
    def join(self, n):
        self.next.prev, self.next, n.prev.next, n.prev = n.prev, n, self.next, self
    def detach(self):
        self.prev.next, self.next.prev, self.prev, self.next = self.next, self.prev, self, self
    def __iter__(self):
        n = self.next
        while n != self:
            n = n.next
            yield n.prev
        yield n
    
class glist(list):
    # expanding list
    def __setitem__(self, index, value):
        if index >= len(self): self.extend([None]*(index+1-len(self)))
        super().__setitem__(index,value)
    def __getitem__(self, index):
        if index >= len(self): return None
        return super().__getitem__(index)

class FibHeap:
    class _Node():
        def __init__(self, key):
            self.key = key 
            self.parent = None
            self.child = None
            self.bros = dllist(self)
            self.mark = False
            self.deg = 0
        def nobros(self):
            return self.bros.next == self.bros
        def adopt(self, child):
            self.deg += 1
            child.parent = self
            child.bros.detach()
            if self.child == None: self.child = child
            else: self.child.bros.join(child.bros)
        def abandon(self, child):
            self.deg -= 1
            child.parent = None
            self.child = child.bros.next.data
            if child.nobros(): self.child = None
            else: child.bros.detach()
    def _consolidate(self):
        for x in (l.data for l in self.root.bros):
            x.parent = None
            x.mark = False
            while x:
                if self.aux[x.deg] == None: self.aux[x.deg], x = x, None
                else:
                    y, self.aux[x.deg] = self.aux[x.deg], None
                    if y.key < x.key: x,y = y,x
                    self.root = x
                    x.adopt(y)
        for x in (l.data for l in self.root.bros):
            self.aux[x.deg] = None
            if x.key < self.root.key: self.root = x
    def _cascade(self, n):
        while True:
            p = n.parent
            p.abandon(n)
            self.root.bros.join(n.bros)
            n.mark = False
            n = p
            if not n.mark: break
        if n.parent: n.mark = True
    def _goodnode(self, n):
        return n.parent or not n.nobros() or n == self.root
    def __init__(self):
        self.root = None
        self.aux = glist()

    def union(self, fibheap):
        if self.root and fibheap.root:
            self.root.bros.join(fibheap.root.bros)
            if fibheap.root.key < self.root.key: self.root = fibheap.root
        elif fibheap.root: self.root = fibheap.root
        fibheap.root = None
    def decrease_key(self, n, key):
        assert(self._goodnode(n) and key <= n.key)
        n.key = key
        if n.parent and n.key < n.parent.key: self._cascade(n)
        if n.key < self.root.key: self.root = n
    def remove(self, n):
        assert(self._goodnode(n))
        if n.parent: self._cascade(n)
        if n.child != None: n.bros.join(n.child.bros)
        if n.nobros(): self.root = None
        else:
            if self.root == n: self.root = n.bros.next.data
            n.bros.detach()
            self._consolidate()
    def insert(self, key):
        n = self._Node(key)
        if self.root: self.root.bros.join(n.bros)
        if self.root == None or key < self.root.key: self.root = n
        return n
    def extract_min(self): self.remove(self.root)
    def empty(self): return self.root == None
    def minkey(self): return self.root.key


###############################################################################
# Testing
def ds_test():
    from random import randint
    def test_FibHeap():
        f = FibHeap()
        l = []
        N = 100000
        for i in range(N):
            k = randint(1,1000)
            l.append([k, None])
            l[-1][1] = f.insert(k)
        d = 0
        for x in range(N):
            i = randint(0,N-1)
            if l[i][0] == 0: continue
            l[i][0] = randint(0,l[i][0]-1)
            if l[i][0] == 0:
                f.remove(l[i][1])
                d += 1
            else: f.decrease_key(*reversed(l[i]))
        l = sorted([x[0] for x in l if x[0] > 0])
        h = []
        while not f.empty():
            h.append(f.minkey())
            f.extract_min()
        assert l == h
        print("Test FibHeap passed (%d removals)" %d)
    test_FibHeap()
    
if __name__ == "__main__": ds_test()
