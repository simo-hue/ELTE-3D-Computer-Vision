import numpy as np

l = [i for i in range(1, 31, 1)]

print(l)

z = np.array(l)
z = np.reshape(z, (6, 5))

print("")
print(z)
print("")

print(z[2:4, 0:2])
print("")

print(z[[0,1,2,3], [1,2,3,4]])
print("")