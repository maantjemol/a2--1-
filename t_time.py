import typing
import unittest
import numpy as np
import random
from divconq_shit import IntelDevice
from timeit import default_timer as timer
import matplotlib.pyplot as plt

def generate_grid(m, n):
    random.seed(9001)
    x = 0
    grid = [[0 for j in range(n)] for i in range(m)]
    for i in range(m):
        for j in range(n):
            grid[i][j] = x
            x += 1 + random.randint(0, 1)
    return grid


def test_big_grid(size):
    a = np.array(
        generate_grid(size, size)
    )
    c_shift = 2


    raw_locations = [f"l{i}" for i in range(len(a) * len(a[0]))]
    raw_codes = [str(x) for x in a.reshape(-1)]


    enc_locations = []
    for i in raw_locations:
        bit_string = ""
        for letter in i:
            bit_string += '{0:b} '.format(ord(letter) + c_shift)
        enc_locations.append(bit_string[:-1])


    enc_codes = []
    for i in raw_codes:
        bit_string = ""
        for letter in i:
            bit_string += '{0:b} '.format(ord(letter) + c_shift)
        enc_codes.append(bit_string[:-1])


    ob = IntelDevice(len(a[0]), len(a), enc_locations, enc_codes, c_shift)
    ob.fill_coordinate_to_loc()
    ob.fill_loc_grid()

    start = timer()
    for vid, v in enumerate(a.reshape(-1)):
        result, cells = ob.start_search(v)
    end = timer()
    print(end - start)

    fast_time = cells

    start = timer()
    for vid, v in enumerate(a.reshape(-1)):
        result, cells = ob.start_shit_search(v)
    end = timer()
    print(end - start)

    slow_time = cells

    return fast_time, slow_time

f = 1
results = {"divconq":[], "forloop": []}
for i in range(1,40):
    divconq, forloop = test_big_grid(i*f)
    results["divconq"].append(divconq)
    results["forloop"].append(forloop)

print(results)

data = results

x = [ x * f for x in range(len(data['divconq']))  ]

fig, ax = plt.subplots()
ax.bar(x, data['divconq'], color='b', width=0.35, label='Divide and Conquer')
ax.bar(x, data['forloop'], color='r', width=0.35, bottom=data['divconq'], label='For Loop')

ax.set_ylabel('Time (s)')
ax.set_xlabel('Input Size')
ax.set_title('Comparison of Divide and Conquer vs. For Loop')
ax.legend()
ax.set_yscale('log')

# manually set the positions of the y-axis ticks to powers of 10
ax.set_yticks([10**i for i in range(0, 7)])
plt.show()


