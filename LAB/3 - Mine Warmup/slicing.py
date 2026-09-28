import numpy as np

l = [i for i in range(1, 31, 1)]

print(l)

z = np.array(l)
z = np.reshape(z, (6, 5))

print("")
print(z)
print("")

print(z[:, ::2])
print("")

print(z[:, ::-1])
print("")
