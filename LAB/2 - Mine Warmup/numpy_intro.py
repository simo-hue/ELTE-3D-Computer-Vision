import numpy as np
import random

a = np.array([1, 2, 3])
b = np.array([1, 2, 3])

res = a*b

print(f"{a} * {b} = {res}")

print(f"SIZE: {res.size}")
print(f"SHAPE: {res.shape}")
print(f"NUMBER OF DIMENSION: {res.ndim}")

print("")

# matA = np.array([[1,2 , 3], [4, 5, 6], [7, 8, 9]])
matA = np.random.randint(100, size=(3, 3))
matB = np.random.randint(100, size=(3, 3))

print("")

print(f"MATRIX A: \n {matA}")
print(f"MATRIX B: \n {matB}")

print("")

z = np.zeros((3, 3))

print(f"ZERO MATRIX: \n {z}")
print("")

z = np.abs((matA - matB))

print(f"ABSOLUTE DIFFERENCE MATRIX: \n {z}")
print("")


