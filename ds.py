#!/usr/bin/python3
#
# Copyright (c) 2013, savrus
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
    def __str__(self):
        return "{self:%s next:%s prev:%s data:%s}" % (repr(self), repr(self.next), repr(self.prev), repr(self.data))
    
class glist(list):
    # expanding list
    def __setitem__(self, index, value):
        if index >= len(self): self.extend([None]*(index+1-len(self)))
        list.__setitem__(self,index,value)
    def __getitem__(self, index):
        if index >= len(self): return None
        return list.__getitem__(self,index)

class FibHeap:
    class Node():
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
            self.child = child.bros.next
            if child.nobros(): self.child = None
            else: child.bros.detach()
    def consolidate(self):
        last = 0
        def auxput(x):
            nonlocal last
            last = max(last, x.deg)
            if self.aux[x.deg] == None: self.aux[x.deg] = x
            else:
                y, self.aux[x.deg] = self.aux[x.deg], None
                if y.key < x.key: x,y = y,x
                x.adopt(y)
                auxput(x)
        for n in self.root.bros:
            n.data.parent = None
            auxput(n.data)
        for i in range(last+1):
            if self.aux[i] != None:
                if self.aux[i].key < self.root.key: self.root = self.aux[i]
                self.aux[i] = None
    def cascade(self, n):
        while True:
            p = n.parent
            p.abandon(n)
            self.root.bros.join(n.bros)
            n.mark = False
            n = p
            if not n.mark: break
        if n.parent: n.mark = True
    def goodnode(self, n):
        return n.parent or not n.nobros() or n == self.root

    def union(self, fibheap):
        if self.root and fibheap.root:
            self.root.bros.join(fibheap.root.bros)
            if fibheap.root.key < self.root.key: self.root = fibheap.root
        elif fibheap.root: self.root = fibheap.root
        fibheap.root = None
    def decrease_key(self, n, key):
        assert(self.goodnode(n) and key <= n.key)
        n.key = key
        if n.parent and n.key < n.parent.key: self.cascade(n)
        if n.key < self.root.key: self.root = n
    def delete(self, n):
        assert(self.goodnode(n))
        if n.parent: self.cascade(n)
        if n.child != None: n.bros.join(n.child.bros)
        if n.nobros(): self.root = None
        else:
            if self.root == n: self.root = n.bros.next.data
            n.bros.detach()
            self.consolidate()
    def extract_min(self):
        self.delete(self.root)
    def empty(self):
        return self.root == None
    def minkey(self):
        return self.root.key
    def insert(self, key):
        n = self.Node(key)
        if self.root: self.root.bros.join(n.bros)
        if self.root == None or key < self.root.key: self.root = n
        return n
    def __init__(self):
        self.root = None
        self.aux = glist()




if __name__ == "__main__":
    l = [i for i in range(10)]
    import random
    random.shuffle(l)
    print(l)
    f = FibHeap()
    k = None
    for i in l: k = f.insert(i)
    #k = f.insert(-2)
    f.extract_min()
    f.insert(-2)
    f.decrease_key(k, -1)
    l = []
    while not f.empty():
        l.append(f.minkey())
        f.extract_min()
    print(l)
