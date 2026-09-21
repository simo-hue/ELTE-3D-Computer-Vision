import numpy as np

scores = np.array([
  [[80, 90], [81, 91] ],  # Student 1's scores
  [[75, 85], [78, 5]],  # Student 2's scores
  [[95, 99], [100, 18]]    # Student 3's scores
])

print(scores)
print("")
print(np.max(scores))
print("")
print(np.max(scores, axis=0))
print("")
print(np.max(scores, axis=1))
print("")
print(np.max(scores, axis=2))
print("")
print(np.max(scores, axis=-1))
print("")