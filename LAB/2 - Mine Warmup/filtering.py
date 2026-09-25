import numpy as np

l = [i for i in range(1, 31, 1)]

print(l)

z = np.array(l)
z = np.reshape(z, (6, 5))

print("")
print(z)
print("")


even = (z[z % 2 == 0])


print("")
print(f"EVEN: {even}")
print("")

even = np.where(z % 2 == 0, z, -1) # I put -1 where the condition is false


print("")
print(f"EVEN PRESERVED: {even}")
print("")
