import math

fac = math.factorial

def f(n):
    return (((70.0 / 100.0) ** n) * ((30.0 / 100.0) ** (8 - n))) / float(fac(n) * fac(8 - n))

sum = 0

for n in range(8, -1, -1):
    p = f(n)
    print "N=" + str(n) + ":", p
    sum += p

print "Sum:", sum
alpha = 1 / sum

print "alpha:", alpha

print "When normalized:"

sum = 0

for n in range(8, -1, -1):
    p = f(n) * alpha
    print "N=" + str(n) + ":", p
    sum += p

print "Sum:", sum

extreme = f(8) * alpha
advanced = (f(7) + f(6) + f(5) + f(4)) * alpha
great = (f(3) + f(2) + f(1)) * alpha

print "extreme:", extreme
print "advanced:", advanced
print "great:", great
print "n=0:", (f(0) * alpha)

print "revenue in 1000 CPUs"
print "extreme:", (extreme * 1000 * 1000)
print "advanced:", (advanced * 1000 * 100)
print "great:", (great * 1000 * 50)
