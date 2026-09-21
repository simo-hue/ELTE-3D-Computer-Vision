import numpy as np

l = [i for i in range(1, 31, 1)]

print(l)

z = np.array(l)
z = np.reshape(z, (6, 5))

print("")
print(z)
print("")

xy = np.zeros(z.shape, np.uint8)

xy[z % 2 == 0] = 1

#print(xy.astype(np.uint8))
print(xy)
print("")
