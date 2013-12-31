#!/usr/bin/python3
#
# Copyright (c) 2013, savrus
#

import sys
import random

def Euclid(a,b):
    # returns gcd(a,b)
    if b == 0: return abs(a)
    while a % b != 0:
        a,b = b, a % b
    return abs(b)

def gcd(a,b):
    return abs(a) if b == 0 else gcd(b, a%b)

def ExtendedEuclid(a,b):
    # returns gcd(a,b) and (u,v) such that a*u+b*v = gcd(a,b)
    assert a > 0 and b > 0
    p,q,s,t = 1,0,0,1
    while a % b != 0:
        p,q,s,t = s,t,p-int(a/b)*s,q-int(a/b)*t
        a,b = b, a % b
    return b,s,t

def TestExtendedEuclid():
    # unit test for ExtendedEuclid
    while True:
        a = random.randint(1,(1<<32))
        b = random.randint(1,(1<<32))
        d,u,v = ExtendedEuclid(a,b)
        if d != u*a+v*b:
            print("Error: %s != %s * %s + %s * %s" % (d,u,a,v,b))

def DemoExtendedEuclid():
    print("Enter two numbers to calculate greated common divisor: ")
    a,b = [int(x) for x in sys.stdin.readline().split()]
    u,v,d = euclid(a,b)
    print("%s * %s + %s * %s = %s" % (u,a,v,b,d))

def ModuloPower(a,p,n):
    # return a^p (mod n)
    assert a > 0 and p >= 0 and n > 0
    r = 1
    while p:
        if p & 1 == 1: r = (r * a) % n
        a = (a * a) % n
        p >>= 1
    return r

def Jacobi(a,n):
    # returns Jacobi symbol [a/n] (a generalization of Legendre symbol)
    assert a > 0 and n > 0 and n % 2 == 1
    r = 1
    while a > 1:
        if a >= n: a = a % n
        if a % 2 == 0:
            r *= (abs(4 - (n % 8)) - 2)
            a //= 2
        elif a < n:
            if ((a-1)*(n-1)//4) % 2 == 1: r *= -1
            a,n = n,a
    return r

def IsPrime1(n):
    # If n is prime returns True. If returned False, n is not a prime
    assert n > 0
    if n == 1: return True
    if n % 2 == 0: return False
    a = random.randint(1, n-1)
    if Euclid(a,n) != 1: return False
    j = Jacobi(a,n)
    p = ModuloPower(a, (n-1)//2, n)
    if (j - p) % n == 0: return True
    return False

def DemoIsPrime1():
    print("Enter number for primarity testing ")
    n = int(sys.stdin.readline())
    print("%s is %s" % (n, "probably prime" if IsPrime1(n) else "composite"))

def Log2(n):
    # return integer log_2(n)
    l, p = 1, 2
    while p < n: l, p = l+1, p*2
    return l

def Root(n, p):
    # return floor of p-th power root of n
    q = 2
    while (q*2)**p <= n: q *= 2
    u,l = q*2, q
    while u - l > 1:
        m = (u+l)//2
        if m**p > n: u = m
        else: l = m
    return l

def ExactPower(n):
    # return (True,y,z) if n is y**z for some y,z. (False,0,0) otherwize.
    assert n > 0
    for z in range(Log2(n), 1, -1):
        y = Root(n, z)
        if y**z == n: return True, y, z
    return False, 0, 0

def TestExactPower():
    while True:
        a = random.randint(1,(1<<16))
        b = random.randint(2,(1<<10))
        print("test for %s**%s" % (a,b))
        n = a**b
        p,y,z = ExactPower(n)
        if p == False:
            print("Error: returned False for %s ** %s" % (a,b))
        elif y ** z != n:
            print("Error: returned %s ** %s != %s ** %s" % (y,z,a,b))
        n = random.randint(1,(1<<32))
        p,y,z = ExactPower(n)
        if p == True and y ** z != n:
            print("Error: returned true but %s ** %s != %s" % (y,z,n))

def IsExactPower(n):
    # returns True if n is y**z for some y,z. False otherwize.
    r,l,p = ExactPower(n)
    return r

def DemoExactPower():
    print("Enter number for exact power testing ")
    n = int(sys.stdin.readline())
    r,l,p = ExactPower(n)
    if r: print("%s = %s ** %s" % (n, l, p))
    else: print("%s is not an exact power" % n)

def IsPrime2(n, t):
    # returns True if n is prime, False otherwise. Error probability 1/2**t
    assert n > 0 and t > 0
    if IsExactPower(n): return False
    b = [random.randint(1, n-1) for i in range(0,t)]
    for bb in b:
        if Euclid(n, bb) != 1: return False
    r = [ModuloPower(bb, (n-1)//2, n) for bb in b]
    for rr in r:
        if (rr - 1) % n != 0 and (rr + 1) % n != 0: return False
    if len([1 for rr in r if (rr - 1) % n == 0]) == t: return False
    return True

def DemoIsPrime2():
    print("Enter number for primarity testing and probability")
    n,t = [int(x) for x in sys.stdin.readline().split()]
    print("%s is probably %s" % (n, "prime" if IsPrime2(n,t) else "composite"))


def IsPrime3(n):
    # If n is prime returns True. If returned False, n is not a prime
    assert n > 0
    if n == 1: return True
    r, R = 0, n-1
    while R & 1 == 0: r, R = r + 1, R >> 1
    a = random.randint(1, n -1)
    b = [ModuloPower(a, (2**i)*R, n) for i in range(0,r+1)]
    if b[r] != 1: return False
    if b[0] == 1: return True
    while b[r] == 1: r -= 1
    if (b[r] + 1) % n == 0: return True
    return False

def DemoIsPrime3():
    print("Enter number for primarity testing ")
    n = int(sys.stdin.readline())
    print("%s is %s" % (n, "probably prime" if IsPrime3(n) else "composite"))

def IsPrimeMillerRabin(n,t):
    for j in range(0, t):
        if not IsPrime3(n): return False
    return True

def DemoIsPrimeMillerRabin():
    print("Enter number for primarity testing and probability")
    n,t = [int(x) for x in sys.stdin.readline().split()]
    print("%s is %s" % (n, "probably prime" if IsPrimeMillerRabin(n,t) else "composite"))

def PollardRho(n):
    # returns a nontrivial divisor of n if one found
    assert n > 0
    x = random.randint(0, n-1)
    y, k, i = x, 2, 1
    while True:
        i += 1
        x = (x*x - 1) % n
        d = Euclid(y - x, n)
        if d != 1 and d != n: return d
        if i == k: y, k = x, k*2

def PollardRhoModified(n):
    # returns a nontrivial divisor of n if one found
    assert n > 0
    l = Root(n,2)
    while True:
        x = random.randint(0, n-1)
        y, k, i = x, 2, 1
        while i <= l:
            i += 1
            x = (x*x - 1) % n
            d = Euclid(y - x, n)
            if d != 1 and d != n: return d
            if i == k: y, k = x, k*2

def Factorize(n):
    # try to factor n
    factors = dict()
    p = 0
    while n % 2 == 0: p, n = p + 1, n // 2
    if p > 0: factors[2] = p
    if n == 1: return factors
    stack = [n]
    while len(stack) > 0:
        n = stack.pop()
        if IsPrimeMillerRabin(n, Log2(n)):
            if n not in factors: factors[n] = 1
            else: factors[n] += 1
        else:
            d = PollardRhoModified(n)
            stack.append(d)
            stack.append(n//d)
    return factors

def DemoFactorize():
    print("Enter number for factoring ")
    n = int(sys.stdin.readline())
    f = Factorize(n)
    s = "*".join(["(%s**%s)" % (k,f[k]) if f[k] != 1 else "%s" % k for k in sorted(f.keys())])
    print("%s = %s" % (n, s))

def TestFactorize():
    while True:
        n = random.randint(1,(1<<64))
        #print("Trying to factirize %s" % n)
        f = Factorize(n)
        s = "*".join(["(%s**%s)" % (k,f[k]) if f[k] != 1 else "%s" % k for k in sorted(f.keys())])
        m = 1
        for k in f.keys(): m *= k**f[k]
        if n != m: print("Error: %s != %s" % (n, s))
        else: print("%s = %s" % (n, s))

def Test2Factorize():
    def RandomPrime(a,b):
        while True:
            n = random.randint(a,b)
            if IsPrimeMillerRabin(n, Log2(b)): return n
    while True:
        a = RandomPrime(1<<39,1<<40)
        b = RandomPrime(1<<39,1<<40)
        n = a*b
        print("Trying to factorize: %s " % n, end="")
        sys.stdout.flush()
        f = Factorize(n)
        s = "*".join(["(%s**%s)" % (k,f[k]) if f[k] != 1 else "%s" % k for k in sorted(f.keys())])
        m = 1
        for k in f.keys(): m *= k**f[k]
        if n != m: print("!= %s (ERROR)" % (s))
        else: print("= %s" % (s))

if __name__ == "__main__":
    Test2Factorize()

